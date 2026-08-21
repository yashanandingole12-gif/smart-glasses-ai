import json
import logging
import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from backend.app.config import settings

logger = logging.getLogger("SmartGlasses.LLMService")

class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]

class LLMResponse(BaseModel):
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    provider: str
    model: str

class LLMService:
    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.provider = (provider or settings.LLM_PROVIDER).lower()
        self.model = model or settings.LLM_MODEL
        self.api_key = api_key or settings.LLM_API_KEY
        self.base_url = base_url or settings.LLM_BASE_URL

    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        context_payload: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        """
        Model-agnostic generation routing to appropriate provider.
        """
        if self.provider == "mock":
            return await self._generate_mock(messages, tools, context_payload)
        elif self.provider in ["openai", "gemini", "anthropic"]:
            if not self.api_key or self.api_key.strip() == "":
                err_msg = f"LLM_PROVIDER is set to '{self.provider}' but LLM_API_KEY is missing. Please set your API key in .env or switch LLM_PROVIDER to 'mock'."
                logger.error(err_msg)
                return LLMResponse(
                    content=err_msg,
                    provider=self.provider,
                    model=self.model
                )
            if self.provider == "openai":
                return await self._generate_openai(messages, tools)
            elif self.provider == "gemini":
                return await self._generate_gemini(messages, tools)
            elif self.provider == "anthropic":
                return await self._generate_anthropic(messages, tools)
        elif self.provider == "ollama":
            return await self._generate_ollama(messages, tools)
        else:
            logger.warning(f"Unknown provider '{self.provider}', falling back to mock provider.")
            return await self._generate_mock(messages, tools, context_payload)

    async def _generate_mock(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        context_payload: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        """
        Intelligent context-aware fallback provider that accurately demonstrates smart-glasses responses.
        """
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "").strip()
                break

        msg_lower = last_user_msg.lower()

        # Check for tool responses in conversation
        tool_results = [m for m in messages if m.get("role") == "tool" or m.get("role") == "function"]

        if tool_results:
            last_tool_res = tool_results[-1].get("content", "")
            try:
                data = json.loads(last_tool_res)
            except Exception:
                data = last_tool_res

            # Format tool response
            if "unread_count" in str(data):
                unread = data.get("unread_count", 1) if isinstance(data, dict) else 1
                return LLMResponse(
                    content=f"You have {unread} unread emails. The latest is from {data['messages'][0]['sender'] if isinstance(data, dict) and data.get('messages') else 'college admin'}.",
                    provider="mock",
                    model=self.model
                )
            elif "free_slots" in str(data):
                return LLMResponse(
                    content="You are free between 12:00 PM and 3:00 PM today, and after 7:30 PM.",
                    provider="mock",
                    model=self.model
                )
            elif "events" in str(data):
                next_ev = data.get("next_event", {}) if isinstance(data, dict) else {}
                title = next_ev.get("title", "Class")
                t = next_ev.get("start_time", "10:30 AM")
                return LLMResponse(
                    content=f"Your next event is {title} at {t}.",
                    provider="mock",
                    model=self.model
                )

        # Context-aware greetings
        if any(g in msg_lower for g in ["good morning", "morning", "good afternoon", "good evening", "good night", "hello", "hi"]):
            time_str = "8:15 AM"
            city = "Nagpur"
            next_ev_str = "class at 10:30"
            period = "morning"

            if context_payload:
                t_info = context_payload.get("time", {})
                time_str = t_info.get("local_time", time_str)
                period = t_info.get("period", period)
                if hasattr(period, "value"):
                    period = period.value
                period = str(period).lower().replace("timeperiod.", "")
                loc_info = context_payload.get("location", {})
                city = loc_info.get("city", city)
                cal_info = context_payload.get("calendar", {})
                if cal_info.get("next_event"):
                    ev = cal_info["next_event"]
                    next_ev_str = f"{ev.get('title', 'event').lower()} at {ev.get('start_time', '10:30')}"

            greeting = f"Good {period}" if period != "night" else "Good evening"
            content = f"{greeting}. It's {time_str} and you're in {city}. You have {next_ev_str}. How can I help?"
            return LLMResponse(content=content, provider="mock", model=self.model)

        has_email_context = any("email" in m.get("content", "").lower() or "mail" in m.get("content", "").lower() for m in messages)
        has_cal_context = any("calendar" in m.get("content", "").lower() or "event" in m.get("content", "").lower() or "class" in m.get("content", "").lower() for m in messages)

        # Tool triggering heuristics for mock mode
        if "email" in msg_lower or "mail" in msg_lower or (has_email_context and "read" in msg_lower):
            if "read" in msg_lower or "first" in msg_lower or "second" in msg_lower or "third" in msg_lower:
                idx = 1
                if "second" in msg_lower or "2" in msg_lower:
                    idx = 2
                elif "third" in msg_lower or "3" in msg_lower:
                    idx = 3
                return LLMResponse(
                    tool_calls=[ToolCall(name="gmail_read", arguments={"index": idx})],
                    provider="mock",
                    model=self.model
                )
            return LLMResponse(
                tool_calls=[ToolCall(name="gmail_search", arguments={"query": "is:unread"})],
                provider="mock",
                model=self.model
            )

        if "calendar" in msg_lower or "class" in msg_lower or "next" in msg_lower or "schedule" in msg_lower or "event" in msg_lower or (has_cal_context and "when" in msg_lower):
            if "free" in msg_lower:
                return LLMResponse(
                    tool_calls=[ToolCall(name="calendar_find_free_time", arguments={})],
                    provider="mock",
                    model=self.model
                )
            return LLMResponse(
                tool_calls=[ToolCall(name="calendar_get_events", arguments={})],
                provider="mock",
                model=self.model
            )

        if "search" in msg_lower or "pants" in msg_lower or "wearing" in msg_lower:
            if "pants" in msg_lower or "cloth" in msg_lower or "wearing" in msg_lower:
                return LLMResponse(
                    tool_calls=[ToolCall(name="product_search", arguments={"category": "cargo pants", "color": "black", "style": "loose"})],
                    provider="mock",
                    model=self.model
                )
            return LLMResponse(
                tool_calls=[ToolCall(name="web_search", arguments={"query": last_user_msg})],
                provider="mock",
                model=self.model
            )

        if "where am i" in msg_lower or "location" in msg_lower:
            return LLMResponse(
                tool_calls=[ToolCall(name="get_location", arguments={})],
                provider="mock",
                model=self.model
            )

        if "time" in msg_lower:
            return LLMResponse(
                tool_calls=[ToolCall(name="get_time", arguments={})],
                provider="mock",
                model=self.model
            )

        # Default conversational response
        return LLMResponse(
            content=f"I'm listening on your smart glasses. (Echo: {last_user_msg})",
            provider="mock",
            model=self.model
        )

    async def _generate_openai(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> LLMResponse:
        url = (self.base_url or "https://api.openai.com/v1") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages
        }
        if tools:
            payload["tools"] = [{"type": "function", "function": t} for t in tools]

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            choice = data["choices"][0]["message"]
            content = choice.get("content")
            tool_calls = None
            if choice.get("tool_calls"):
                tool_calls = [
                    ToolCall(
                        name=tc["function"]["name"],
                        arguments=json.loads(tc["function"]["arguments"])
                    )
                    for tc in choice["tool_calls"]
                ]
            return LLMResponse(content=content, tool_calls=tool_calls, provider="openai", model=self.model)

    async def _generate_gemini(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> LLMResponse:
        # Standard Gemini REST endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        # Convert messages to Gemini format
        contents = []
        for m in messages:
            role = "user" if m.get("role") in ["user", "system"] else "model"
            contents.append({"role": role, "parts": [{"text": m.get("content", "")}]})

        payload: Dict[str, Any] = {"contents": contents}
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            cand = data["candidates"][0]["content"]
            text = "".join(p.get("text", "") for p in cand.get("parts", []))
            return LLMResponse(content=text, provider="gemini", model=self.model)

    async def _generate_anthropic(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> LLMResponse:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        # Format messages for Anthropic
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        conv_msgs = [m for m in messages if m["role"] in ["user", "assistant"]]
        payload = {
            "model": self.model,
            "system": system_msg,
            "messages": conv_msgs,
            "max_tokens": 1024
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            text = "".join(b["text"] for b in data.get("content", []) if b.get("type") == "text")
            return LLMResponse(content=text, provider="anthropic", model=self.model)

    async def _generate_ollama(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> LLMResponse:
        url = (self.base_url or "http://localhost:11434") + "/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return LLMResponse(content=data.get("message", {}).get("content"), provider="ollama", model=self.model)

llm_service = LLMService()
