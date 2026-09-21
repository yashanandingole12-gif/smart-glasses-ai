import time
import json
import logging
import asyncio
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field

from backend.app.config import settings
from backend.app.services.llm_service import llm_service, LLMResponse, ToolCall

logger = logging.getLogger("SmartGlasses.LLMRouter")

class RoutingTier(str, Enum):
    FAST = "FAST"
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    FALLBACK = "FALLBACK"

class FailureCategory(str, Enum):
    NONE = "NONE"
    NETWORK_FAILURE = "NETWORK_FAILURE"
    LLM_TIMEOUT = "LLM_TIMEOUT"
    LLM_RATE_LIMIT = "LLM_RATE_LIMIT"
    LLM_PROVIDER_ERROR = "LLM_PROVIDER_ERROR"
    TOOL_TIMEOUT = "TOOL_TIMEOUT"
    STT_FAILURE = "STT_FAILURE"
    TTS_FAILURE = "TTS_FAILURE"

class RouterResponse(BaseModel):
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tier_used: RoutingTier
    provider: str
    model: str
    duration_ms: float
    ttft_ms: Optional[float] = None
    fallback_chain: List[Dict[str, Any]] = Field(default_factory=list)
    failure_category: FailureCategory = FailureCategory.NONE
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None

class LLMRouter:
    def __init__(self):
        pass

    def select_starting_tier(self, user_message: str, has_tools: bool) -> RoutingTier:
        """
        Policy: Use the fastest appropriate tier.
        - Fast conversational / greetings / status -> FAST tier
        - Tool reasoning / email interpretation -> PRIMARY tier
        """
        msg_lower = user_message.lower().strip()
        if not has_tools and len(msg_lower.split()) < 8:
            return RoutingTier.FAST
        return RoutingTier.PRIMARY

    async def generate_with_budget(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        context_payload: Optional[Dict[str, Any]] = None,
        starting_tier: Optional[RoutingTier] = None,
        per_attempt_timeout: Optional[float] = None,
        global_deadline_seconds: Optional[float] = None,
        cancellation_event: Optional[asyncio.Event] = None
    ) -> RouterResponse:
        """
        Executes multi-tier cascade (FAST -> PRIMARY -> SECONDARY -> FALLBACK) with strict global deadline
        and per-attempt timeouts. Never blocks indefinitely or returns empty successful text.
        """
        deadline_sec = global_deadline_seconds if global_deadline_seconds is not None else settings.REQUEST_DEADLINE_SECONDS
        attempt_timeout_sec = per_attempt_timeout if per_attempt_timeout is not None else settings.LLM_TIMEOUT_SECONDS
        start_time = time.time()
        global_deadline = start_time + deadline_sec

        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "")
                break

        if not starting_tier:
            starting_tier = self.select_starting_tier(last_user_msg, bool(tools))

        # Define tier order with optional secondary provider
        tier_order: List[RoutingTier] = []
        if starting_tier == RoutingTier.FAST:
            tier_order = [RoutingTier.FAST, RoutingTier.PRIMARY]
        else:
            tier_order = [RoutingTier.PRIMARY, RoutingTier.FAST]

        if settings.SECONDARY_LLM_PROVIDER and settings.SECONDARY_LLM_PROVIDER != "none":
            tier_order.append(RoutingTier.SECONDARY)

        tier_order.append(RoutingTier.FALLBACK)

        fallback_chain: List[Dict[str, Any]] = []
        last_failure_cat = FailureCategory.NONE
        working_messages = list(messages)
        attempted_configs = set()

        for tier in tier_order:
            # Check cancellation
            if cancellation_event and cancellation_event.is_set():
                logger.info("Generation aborted due to active request cancellation.")
                return RouterResponse(
                    content="Request was cancelled.",
                    tier_used=tier,
                    provider="cancelled",
                    model="cancelled",
                    duration_ms=(time.time() - start_time) * 1000.0,
                    fallback_chain=fallback_chain,
                    failure_category=FailureCategory.NONE
                )

            # Check remaining global deadline budget
            time_left = global_deadline - time.time()
            if time_left <= 0.5 and tier != RoutingTier.FALLBACK:
                logger.warning(f"Global deadline budget ({deadline_sec}s) nearly exhausted. Jumping to FALLBACK tier.")
                continue

            # Determine provider & model for tier
            api_key = settings.LLM_API_KEY or settings.GEMINI_API_KEY
            base_url = settings.LLM_BASE_URL
            if tier == RoutingTier.FAST:
                provider = settings.FAST_LLM_PROVIDER
                model = settings.FAST_LLM_MODEL
                # If PRIMARY already attempted this model, degrade to companion flash model
                if (provider, model) in attempted_configs:
                    model = "gemini-3.5-flash-lite" if "lite" not in model else "gemini-flash-latest"
            elif tier == RoutingTier.PRIMARY:
                provider = settings.PRIMARY_LLM_PROVIDER
                model = settings.PRIMARY_LLM_MODEL
                # If FAST already attempted this model, degrade to companion flash model
                if (provider, model) in attempted_configs:
                    model = "gemini-3.5-flash-lite" if "lite" not in model else "gemini-flash-latest"
            elif tier == RoutingTier.SECONDARY:
                provider = settings.SECONDARY_LLM_PROVIDER or "deepseek"
                model = settings.SECONDARY_LLM_MODEL or settings.DEEPSEEK_MODEL or "deepseek-chat"
                api_key = settings.SECONDARY_LLM_API_KEY or settings.DEEPSEEK_API_KEY or api_key
                base_url = settings.SECONDARY_LLM_BASE_URL or settings.DEEPSEEK_BASE_URL or "https://api.deepseek.com"
            else:
                provider = settings.FALLBACK_LLM_PROVIDER
                model = settings.FALLBACK_LLM_MODEL

            config_key = (provider, model)
            if config_key in attempted_configs and tier != RoutingTier.FALLBACK:
                logger.debug("Skipping already-attempted provider configuration: %s", config_key)
                continue
            attempted_configs.add(config_key)

            if tier == RoutingTier.FAST:
                tier_timeout = min(attempt_timeout_sec, 7.5, max(1.0, time_left))
            elif tier == RoutingTier.PRIMARY:
                tier_timeout = min(attempt_timeout_sec, 7.5, max(1.0, time_left))
            else:
                tier_timeout = min(attempt_timeout_sec, max(1.0, time_left))
            t_tier_start = time.time()

            try:
                # Custom instance for this tier attempt
                tier_service = llm_service if (provider == llm_service.provider and model == llm_service.model and api_key == llm_service.api_key) else \
                    llm_service.__class__(provider=provider, model=model, api_key=api_key, base_url=base_url)

                # Execute with strict per-attempt timeout
                response: LLMResponse = await asyncio.wait_for(
                    tier_service.generate(working_messages, tools=tools, context_payload=context_payload),
                    timeout=tier_timeout
                )

                tier_dur_ms = (time.time() - t_tier_start) * 1000.0

                # Validate response is not empty
                if response and (response.content or response.tool_calls):
                    return RouterResponse(
                        content=response.content,
                        tool_calls=response.tool_calls,
                        tier_used=tier,
                        provider=provider,
                        model=model,
                        duration_ms=tier_dur_ms,
                        fallback_chain=fallback_chain,
                        failure_category=FailureCategory.NONE
                    )
                else:
                    raise ValueError(f"Provider {provider}/{model} returned empty response.")

            except asyncio.TimeoutError:
                dur_ms = (time.time() - t_tier_start) * 1000.0
                last_failure_cat = FailureCategory.LLM_TIMEOUT
                logger.warning(
                    f"Tier {tier.value} ({provider}/{model}) timed out after {dur_ms:.1f}ms "
                    f"(limit: {tier_timeout:.1f}s). Cascading to next tier."
                )
                fallback_chain.append({
                    "tier": tier.value,
                    "provider": provider,
                    "model": model,
                    "error": "LLM_TIMEOUT",
                    "duration_ms": dur_ms
                })

            except Exception as e:
                dur_ms = (time.time() - t_tier_start) * 1000.0
                err_str = str(e)

                # HTTP 429 Rate Limit / Quota detection
                if "429" in err_str or "quota" in err_str.lower() or "rate" in err_str.lower():
                    last_failure_cat = FailureCategory.LLM_RATE_LIMIT
                    logger.warning(
                        f"Tier {tier.value} ({provider}/{model}) hit HTTP 429 / Rate Limit. "
                        "Switching immediately to fallback tier without delay."
                    )
                # HTTP 413 Context Overflow detection
                elif "413" in err_str or "too large" in err_str.lower() or "context length" in err_str.lower():
                    last_failure_cat = FailureCategory.LLM_PROVIDER_ERROR
                    logger.warning(
                        f"Tier {tier.value} hit context overflow (413). Compacting prompt for subsequent tiers."
                    )
                    working_messages = self.compact_messages(working_messages)
                elif "network" in err_str.lower() or "connection" in err_str.lower():
                    last_failure_cat = FailureCategory.NETWORK_FAILURE
                else:
                    last_failure_cat = FailureCategory.LLM_PROVIDER_ERROR

                logger.warning(
                    f"Tier {tier.value} ({provider}/{model}) failed with {type(e).__name__}: {e}. "
                    "Cascading to next tier."
                )
                fallback_chain.append({
                    "tier": tier.value,
                    "provider": provider,
                    "model": model,
                    "error": err_str[:120],
                    "duration_ms": dur_ms
                })

        # Final Guaranteed Fallback: Local context responder
        logger.warning("All primary/fast tiers exhausted. Generating guaranteed local fallback response.")
        fallback_resp = await llm_service._generate_mock(working_messages, tools, context_payload)
        total_dur_ms = (time.time() - start_time) * 1000.0

        return RouterResponse(
            content=fallback_resp.content or "I don't have that information right now.",
            tool_calls=fallback_resp.tool_calls,
            tier_used=RoutingTier.FALLBACK,
            provider="mock_fallback",
            model="mock-glasses-v1",
            duration_ms=total_dur_ms,
            fallback_chain=fallback_chain,
            failure_category=last_failure_cat if last_failure_cat != FailureCategory.NONE else FailureCategory.LLM_PROVIDER_ERROR
        )

    def compact_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Prompt compaction helper for context overflow (HTTP 413) or token minimization:
        - Keeps minimal system prompt
        - Keeps last 3 conversational turns
        - Clips message bodies to 300 characters
        """
        compacted: List[Dict[str, str]] = []
        system_msgs = [m for m in messages if m.get("role") == "system"]
        if system_msgs:
            compacted.append({
                "role": "system",
                "content": "You are a smart glasses assistant. Answer in 1-2 concise sentences."
            })

        other_msgs = [m for m in messages if m.get("role") != "system"]
        # Retain last 3 messages only
        recent = other_msgs[-3:] if len(other_msgs) > 3 else other_msgs

        for m in recent:
            content = m.get("content", "")
            if len(content) > 300:
                content = content[:300] + "... [trimmed]"
            compacted.append({
                "role": m.get("role", "user"),
                "content": content
            })

        return compacted

llm_router = LLMRouter()
