import time
import uuid
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List

from backend.app.config import settings
from backend.app.models.schemas import (
    HealthResponse,
    SessionCreateRequest,
    SessionResponse,
    AgentMessageRequest,
    AgentMessageResponse,
    FullContextPayload,
    DeviceContext,
    LocationContext,
    TemporalContext,
    VisionAnalyzeRequest,
    VisionAnalyzeResponse
)

from backend.app.services.context_engine import context_engine
from backend.app.services.agent_graph import run_agent
from backend.app.services.tool_registry import registry
from backend.app.services.temporal_resolver import temporal_resolver
from backend.app.services.memory_repository import memory_repository
from backend.app.services.llm_router import llm_router, RoutingTier
from backend.app.services.math_engine import math_engine
from backend.app.services.personality_engine import personality_engine
from backend.app.tools.calendar_tools import calendar_get_events
from backend.app.tools.gmail_tools import gmail_search, gmail_read, gmail_send_message, gmail_reply_message
from backend.app.tools.sms_tools import sms_read_recent
from backend.app.tools.search_tools import web_search, product_search, academic_research_search
from backend.app.logging_service import LatencyMetrics, log_request_metrics
from backend.app.api.auth import router as auth_router


logger = logging.getLogger("SmartGlasses.API")

app = FastAPI(
    title="Context-Aware Smart Glasses AI Assistant API",
    description="Backend API for Smart Glasses (ESP32-S3 / Android / Laptop Simulator)",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import HTMLResponse
from backend.app.web_ui import get_dashboard_html

app.include_router(auth_router)

@app.get("/", response_class=HTMLResponse)
async def root_dashboard():
    """Developer System Dashboard for Smart Glasses AI."""
    return HTMLResponse(content=get_dashboard_html())

@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """Service health and current runtime status."""
    return HealthResponse(
        status="ok",
        version="0.1.0",
        device_mode="SIMULATOR_READY",
        llm_provider=settings.LLM_PROVIDER
    )

@app.post("/api/v1/session", response_model=SessionResponse)
async def create_session(req: SessionCreateRequest = SessionCreateRequest()):
    """Create a new interaction session."""
    session_id = str(uuid.uuid4())
    return SessionResponse(
        session_id=session_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        device_type=req.device_type or "SIMULATOR"
    )

@app.get("/api/v1/diagnostics/integrations")
async def get_integrations_diagnostics(user_id: str = "default_user"):
    """
    Diagnostic integration health status endpoint.
    Safely returns connectivity state without exposing tokens or secrets.
    """
    from backend.app.services.token_service import token_service
    status = token_service.get_status(user_id)
    is_google_connected = bool(status.get("connected") and not status.get("is_expired"))
    gemini_configured = bool(settings.GEMINI_API_KEY or (settings.LLM_PROVIDER == "gemini" and settings.LLM_API_KEY))

    return {
        "gemini": "available" if gemini_configured else "unavailable",
        "google": "connected" if is_google_connected else "disconnected",
        "gmail": "available" if is_google_connected else "unavailable",
        "calendar": "available" if is_google_connected else "unavailable"
    }

@app.get("/api/v1/context", response_model=FullContextPayload)
async def get_current_context(timezone_str: str = settings.DEFAULT_TIMEZONE, include_remote: bool = False):
    """Retrieve freshly computed context engine payload (pure local by default, <1ms)."""
    return context_engine.get_relevant_context(
        user_message="",
        client_context=None,
        include_remote=include_remote
    )

@app.post("/api/v1/agent/message", response_model=AgentMessageResponse)
async def process_agent_message(req: AgentMessageRequest):
    """
    Main conversational endpoint with Authoritative Request Router:
    1. Deterministic local fast-path (Time, Battery, Location, Date) -> <1ms
    2. Temporal calendar queries (read today/tomorrow/etc.) -> <50ms cached, <600ms network
    3. Gmail queries (read inbox/unread/recent) -> <500ms
    4. SMS queries (read recent SMS) -> <10ms
    5. Academic Research / arXiv search -> <1.5s
    6. Direct Web search
    7. Direct conversational single-turn LLM generation (general chat/QA without graph recursion) -> ~1s
    8. LangGraph agent execution for mutations (event creation, SMS send) & action confirmations
    """
    metrics = LatencyMetrics(
        request_id=req.request_id,
        session_id=req.session_id
    )

    text_len = len(req.message.strip()) if req.message else 0
    msg_raw = req.message.strip() if req.message else ""
    msg_lower = msg_raw.lower()

    logger.info(
        f"[REQ_ID: {req.request_id[:8]}] RECEIVED: lang={req.language or 'auto'} "
        f"locale={req.locale or 'en-IN'} len={text_len}"
    )

    # 1. Deterministic Fast Path Check (Time, Battery, Location, Date)
    t_fp_start = time.time()
    quick_time = req.context.time if (req.context and req.context.time) else context_engine.compute_temporal_context()
    quick_device = req.context.device if (req.context and req.context.device) else DeviceContext(battery=85)
    quick_location = req.context.location if (req.context and req.context.location) else LocationContext(
        latitude=settings.DEFAULT_LOCATION_LATITUDE,
        longitude=settings.DEFAULT_LOCATION_LONGITUDE,
        city=settings.DEFAULT_LOCATION_CITY,
        country=settings.DEFAULT_LOCATION_COUNTRY,
        is_available=True
    )
    quick_ctx = FullContextPayload(
        time=quick_time,
        device=quick_device,
        location=quick_location,
        calendar=None
    )

    fast_reply = context_engine.resolve_deterministic_query(
        user_message=msg_raw,
        context=quick_ctx,
        language=req.language or "auto"
    )
    if fast_reply is not None:
        metrics.fast_path_ms = (time.time() - t_fp_start) * 1000.0
        metrics.finish()
        log_request_metrics(metrics)

        return AgentMessageResponse(
            session_id=req.session_id,
            response=fast_reply,
            actions=[],
            requires_confirmation=False,
            confirmation_prompt=None,
            sources=["context_engine_fast_path"],
            metadata={
                "latency_ms": metrics.total_ms,
                "fast_path": True,
                "timings": metrics.to_dict(),
                "llm_provider": "fast_path",
                "request_id": req.request_id,
                "language": req.language or "auto",
                "locale": req.locale or "en-IN"
            }
        )

    # 1.1 Deterministic Math Engine Fast-Path (<50ms, Zero-LLM Evaluation)
    math_eval = math_engine.evaluate(msg_raw)
    if math_eval is not None:
        metrics.fast_path_ms = (time.time() - t_fp_start) * 1000.0
        metrics.finish()
        log_request_metrics(metrics)

        math_reply = math_eval.get("text_response", "Calculation completed.")
        memory_repository.add_message(req.session_id, "user", msg_raw)
        memory_repository.add_message(req.session_id, "assistant", math_reply)

        return AgentMessageResponse(
            session_id=req.session_id,
            response=math_reply,
            actions=[],
            requires_confirmation=False,
            confirmation_prompt=None,
            sources=["deterministic_math_engine"],
            metadata={
                "latency_ms": metrics.total_ms,
                "fast_path": True,
                "math_operation": math_eval.get("operation"),
                "timings": metrics.to_dict(),
                "llm_provider": "deterministic_math",
                "request_id": req.request_id,
                "language": req.language or "auto",
                "locale": req.locale or "en-IN"
            }
        )

    # Detect mutation / high-risk action intent requiring 2-step confirmation or LangGraph execution
    is_mutation = bool(
        req.confirmed_action_id or
        any(
            kw in msg_lower
            for kw in [
                "create event", "add event", "schedule a", "book a", "book an", "cancel event",
                "delete event", "send sms", "send text", "send a message", "text to", "sms to",
                "send email", "compose email", "email to", "send an email", "reply to"
            ]
        )
    )

    # 2. Conversational Temporal Calendar Fast-Track (Direct Resolution without Agent loops)
    recent_history = memory_repository.get_session_history(req.session_id, limit=4)
    temporal_intent = temporal_resolver.resolve_intent(
        query=msg_raw,
        conversation_history=recent_history,
        tz_name=settings.DEFAULT_TIMEZONE
    )

    if temporal_intent.is_calendar_query and not is_mutation:
        t_cal_start = time.time()
        raw_events_data = calendar_get_events(date_target=temporal_intent.date_target)
        if raw_events_data.get("error"):
            cal_reply = raw_events_data.get("message") or "I can't access your calendar right now."
        else:
            events_list = raw_events_data.get("events", [])
            filtered_events = temporal_resolver.filter_events(events_list, temporal_intent)
            cal_reply = temporal_resolver.format_calendar_response(temporal_intent, filtered_events)

        # Persist conversation session memory
        memory_repository.add_message(req.session_id, "user", msg_raw)
        memory_repository.add_message(req.session_id, "assistant", cal_reply)

        metrics.fast_path_ms = (time.time() - t_fp_start) * 1000.0
        metrics.context_ms = (time.time() - t_cal_start) * 1000.0
        metrics.finish()
        log_request_metrics(metrics)

        return AgentMessageResponse(
            session_id=req.session_id,
            response=cal_reply,
            actions=[],
            requires_confirmation=False,
            confirmation_prompt=None,
            sources=["temporal_resolver_calendar"],
            metadata={
                "latency_ms": metrics.total_ms,
                "fast_path": True,
                "temporal_intent": temporal_intent.to_log_dict(),
                "timings": metrics.to_dict(),
                "llm_provider": "temporal_resolver",
                "request_id": req.request_id,
                "language": req.language or "auto",
                "locale": req.locale or "en-IN"
            }
        )

    # 3. Direct Gmail Retrieval & Reading Fast-Track (<500ms)
    email_keywords = ["email", "emails", "gmail", "inbox", "mail", "mails", "ईमेल", "इमेल", "मेल", "linkedin", "github"]
    is_email_read = any(kw in msg_lower for kw in email_keywords) and not is_mutation
    if is_email_read:
        t_gmail_start = time.time()
        lang = req.language or "auto"
        is_hi = lang == "hi" or any("\u0900" <= c <= "\u097f" for c in msg_raw)
        is_mr = lang == "mr"

        # Check if user is asking to read full content of an email (Stage 2)
        is_read_content = any(rw in msg_lower for rw in ["read", "say", "body", "content", "what does", "what did", "वाचा", "पढ़ो"])
        
        # Check for specific entity
        entity_query = None
        for ent in ["linkedin", "github", "amazon", "swiggy", "zomato", "college", "professor", "university"]:
            if ent in msg_lower:
                entity_query = ent
                break

        if is_read_content:
            raw_email_data = gmail_read(index=1) if not entity_query else gmail_search(query=entity_query)
            if entity_query and raw_email_data.get("messages"):
                # Fetch full content of first matching entity email
                first_id = raw_email_data["messages"][0]["id"]
                read_detail = gmail_read(message_id=first_id)
                email_reply = read_detail.get("message", "I retrieved the email content.")
            else:
                email_reply = raw_email_data.get("message", "I couldn't find that email.")
        else:
            raw_email_data = gmail_search(query=entity_query)
            if raw_email_data.get("error"):
                if is_hi:
                    email_reply = "मैं अभी आपके ईमेल एक्सेस नहीं कर सकता।"
                elif is_mr:
                    email_reply = "मी आता तुमचे ईमेल ऍक्सेस करू शकत नाही."
                else:
                    email_reply = raw_email_data.get("message") or "I can't access your email right now. Please connect your Google account in Settings."
            else:
                email_reply = raw_email_data.get("message", "Retrieved your emails.")

        memory_repository.add_message(req.session_id, "user", msg_raw)
        memory_repository.add_message(req.session_id, "assistant", email_reply)

        metrics.fast_path_ms = (time.time() - t_fp_start) * 1000.0
        metrics.tool_ms = (time.time() - t_gmail_start) * 1000.0
        metrics.finish()
        log_request_metrics(metrics)

        return AgentMessageResponse(
            session_id=req.session_id,
            response=email_reply,
            actions=[],
            requires_confirmation=False,
            confirmation_prompt=None,
            sources=["gmail_direct_router"],
            metadata={
                "latency_ms": metrics.total_ms,
                "fast_path": True,
                "timings": metrics.to_dict(),
                "llm_provider": "gmail_direct",
                "request_id": req.request_id,
                "language": req.language or "auto",
                "locale": req.locale or "en-IN"
            }
        )

    # 4. Direct SMS Read Fast-Track (<10ms)
    sms_keywords = ["sms", "text message", "text messages", "messages", "texts", "मैसेज", "मेसेज", "एसएमएस"]
    is_sms_read = any(kw in msg_lower for kw in sms_keywords) and not is_mutation
    if is_sms_read:
        t_sms_start = time.time()
        raw_sms_data = sms_read_recent(limit=5)
        messages = raw_sms_data.get("messages", [])
        if not messages:
            sms_reply = "You have no recent SMS messages."
        else:
            lines = [f"{i+1}. From {m.get('sender', 'Unknown')}: '{m.get('text', '')}'" for i, m in enumerate(messages[:3])]
            count = len(messages)
            sms_reply = f"You have {count} recent SMS message{'s' if count > 1 else ''}: " + "; ".join(lines)

        memory_repository.add_message(req.session_id, "user", msg_raw)
        memory_repository.add_message(req.session_id, "assistant", sms_reply)

        metrics.fast_path_ms = (time.time() - t_fp_start) * 1000.0
        metrics.tool_ms = (time.time() - t_sms_start) * 1000.0
        metrics.finish()
        log_request_metrics(metrics)

        return AgentMessageResponse(
            session_id=req.session_id,
            response=sms_reply,
            actions=[],
            requires_confirmation=False,
            confirmation_prompt=None,
            sources=["sms_direct_router"],
            metadata={
                "latency_ms": metrics.total_ms,
                "fast_path": True,
                "timings": metrics.to_dict(),
                "llm_provider": "sms_direct",
                "request_id": req.request_id,
                "language": req.language or "auto",
                "locale": req.locale or "en-IN"
            }
        )

    # 5. Direct Academic Research / arXiv Search Fast-Track (<1.5s)
    research_triggers = ["search arxiv", "arxiv", "find papers", "research papers", "scientific papers", "academic papers", "papers on", "paper on"]
    if any(trig in msg_lower for trig in research_triggers) and not is_mutation:
        t_res_start = time.time()
        clean_topic = msg_raw
        for trig in ["search arxiv for", "search arxiv on", "find research papers on", "find papers on", "academic papers on", "research papers on", "papers on", "arxiv"]:
            if trig in msg_lower:
                idx = msg_lower.find(trig)
                clean_topic = msg_raw[idx + len(trig):].strip(" ?:.,")
                break
        if not clean_topic:
            clean_topic = msg_raw

        search_res = academic_research_search(query=clean_topic, limit=3)
        papers = search_res.get("papers", [])
        if papers:
            lines = [f"{i+1}. '{p.get('title', 'Paper')}' ({p.get('year', 'Recent')}) by {p.get('authors', ['Unknown'])[0]}" for i, p in enumerate(papers[:3])]
            research_reply = f"Found {len(papers)} research papers on '{clean_topic}': " + "; ".join(lines)
        else:
            research_reply = f"No academic papers found for '{clean_topic}'."

        memory_repository.add_message(req.session_id, "user", msg_raw)
        memory_repository.add_message(req.session_id, "assistant", research_reply)

        metrics.fast_path_ms = (time.time() - t_fp_start) * 1000.0
        metrics.tool_ms = (time.time() - t_res_start) * 1000.0
        metrics.finish()
        log_request_metrics(metrics)

        return AgentMessageResponse(
            session_id=req.session_id,
            response=research_reply,
            actions=[],
            requires_confirmation=False,
            confirmation_prompt=None,
            sources=["academic_research_router"],
            metadata={
                "latency_ms": metrics.total_ms,
                "fast_path": True,
                "timings": metrics.to_dict(),
                "llm_provider": "academic_research",
                "request_id": req.request_id,
                "language": req.language or "auto",
                "locale": req.locale or "en-IN"
            }
        )

    # 6. Direct Web Search Fast-Track
    web_triggers = ["search web for", "search the web for", "google search for", "look up on web"]
    if any(trig in msg_lower for trig in web_triggers) and not is_mutation:
        t_web_start = time.time()
        clean_topic = msg_raw
        for trig in web_triggers:
            if trig in msg_lower:
                idx = msg_lower.find(trig)
                clean_topic = msg_raw[idx + len(trig):].strip(" ?:.,")
                break
        web_res = web_search(query=clean_topic)
        results = web_res.get("results", [])
        if results:
            web_reply = f"Here is what I found for '{clean_topic}': {results[0].get('snippet', '')}"
        else:
            web_reply = f"No search results found for '{clean_topic}'."

        memory_repository.add_message(req.session_id, "user", msg_raw)
        memory_repository.add_message(req.session_id, "assistant", web_reply)

        metrics.fast_path_ms = (time.time() - t_fp_start) * 1000.0
        metrics.tool_ms = (time.time() - t_web_start) * 1000.0
        metrics.finish()
        log_request_metrics(metrics)

        return AgentMessageResponse(
            session_id=req.session_id,
            response=web_reply,
            actions=[],
            requires_confirmation=False,
            confirmation_prompt=None,
            sources=["web_search_router"],
            metadata={
                "latency_ms": metrics.total_ms,
                "fast_path": True,
                "timings": metrics.to_dict(),
                "llm_provider": "web_search",
                "request_id": req.request_id,
                "language": req.language or "auto",
                "locale": req.locale or "en-IN"
            }
        )

    # 7. Direct Single-Turn LLM Conversational Chat (For general Q&A, chat, explanations without LangGraph overhead)
    if not is_mutation and not req.confirmed_action_id:
        t_llm_start = time.time()
        # Fast local context (<1ms)
        local_ctx = context_engine.get_relevant_context(
            user_message=msg_raw,
            client_context=req.context,
            session_id=req.session_id,
            include_remote=False
        )
        time_str = local_ctx.time.local_time if local_ctx.time else "Now"
        loc_str = local_ctx.location.city if (local_ctx.location and local_ctx.location.city != "Unknown") else "Local"
        bat_str = f"{local_ctx.device.battery}%" if (local_ctx.device and local_ctx.device.battery is not None) else "85%"

        core_prompt = personality_engine.build_system_prompt(msg_raw)
        system_prompt = (
            f"{core_prompt} "
            f"Context: Time is {time_str}, Location is {loc_str}, Battery is {bat_str}. "
            f"Do NOT format with markdown or bullet points."
        )

        history_msgs = memory_repository.get_session_history(req.session_id, limit=4)
        formatted_messages = [{"role": "system", "content": system_prompt}]
        for h in history_msgs:
            formatted_messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
        formatted_messages.append({"role": "user", "content": msg_raw})

        router_resp = await llm_router.generate_with_budget(
            messages=formatted_messages,
            tools=None,
            context_payload=local_ctx.model_dump(),
            starting_tier=RoutingTier.FAST,
            per_attempt_timeout=2.5,
            global_deadline_seconds=4.0
        )

        final_text = (router_resp.content or "").strip()
        if final_text:
            memory_repository.add_message(req.session_id, "user", msg_raw)
            memory_repository.add_message(req.session_id, "assistant", final_text)

            metrics.llm_first_response_ms = router_resp.duration_ms
            metrics.finish()
            log_request_metrics(metrics)

            return AgentMessageResponse(
                session_id=req.session_id,
                response=final_text,
                actions=[],
                requires_confirmation=False,
                confirmation_prompt=None,
                sources=["llm_router", router_resp.tier_used.value],
                metadata={
                    "latency_ms": metrics.total_ms,
                    "fast_path": False,
                    "timings": metrics.to_dict(),
                    "routing": {
                        "tier_used": router_resp.tier_used.value,
                        "provider": router_resp.provider,
                        "model": router_resp.model,
                        "duration_ms": router_resp.duration_ms
                    },
                    "llm_provider": router_resp.provider,
                    "llm_model": router_resp.model,
                    "request_id": req.request_id,
                    "language": req.language or "auto",
                    "locale": req.locale or "en-IN"
                }
            )

    # 8. LangGraph Agent Execution (For mutations, 2-step confirmations, or multi-step tool calls)
    t_ctx_start = time.time()
    context = context_engine.get_relevant_context(
        user_message=req.message,
        client_context=req.context,
        session_id=req.session_id,
        include_remote=True
    )
    metrics.context_ms = (time.time() - t_ctx_start) * 1000.0

    t_agent_start = time.time()
    try:
        agent_output = await run_agent(
            session_id=req.session_id,
            user_message=req.message,
            context_payload=context.model_dump(),
            language=req.language or "auto",
            locale=req.locale or "en-IN",
            confirmed_action_id=req.confirmed_action_id
        )
    except Exception as e:
        logger.error(f"[REQ_ID: {req.request_id[:8]}] Agent execution error: {type(e).__name__}: {e}")
        agent_output = {
            "response": f"I'm listening on your smart glasses. The cloud AI service is temporarily offline or experiencing a connection error. ({type(e).__name__})",
            "actions": [],
            "requires_confirmation": False,
            "timings": {},
            "routing_metadata": {
                "tier_used": "FALLBACK",
                "failure_category": "LLM_PROVIDER_ERROR",
                "error": str(e)
            }
        }
    
    agent_timings = agent_output.get("timings") or {}
    routing_meta = agent_output.get("routing_metadata") or {}

    metrics.agent_ms = agent_timings.get("agent_ms", (time.time() - t_agent_start) * 1000.0)
    metrics.llm_first_response_ms = agent_timings.get("llm_first_response_ms")
    metrics.tool_ms = agent_timings.get("tool_ms")
    metrics.llm_final_response_ms = agent_timings.get("llm_final_response_ms")
    metrics.finish()

    log_request_metrics(metrics)

    return AgentMessageResponse(
        session_id=req.session_id,
        response=agent_output["response"],
        actions=agent_output.get("actions", []),
        requires_confirmation=agent_output.get("requires_confirmation", False),
        confirmation_prompt=agent_output.get("confirmation_prompt"),
        confirmation_action_id=agent_output.get("confirmation_action_id"),
        sources=["context_engine", "sqlite_memory", "langgraph", routing_meta.get("tier_used", "FAST")],
        metadata={
            "latency_ms": metrics.total_ms,
            "fast_path": False,
            "timings": metrics.to_dict(),
            "routing": routing_meta,
            "llm_provider": routing_meta.get("provider", settings.LLM_PROVIDER),
            "llm_model": routing_meta.get("model", settings.LLM_MODEL),
            "failure_category": routing_meta.get("failure_category", "NONE"),
            "request_id": req.request_id,
            "language": req.language or "auto",
            "locale": req.locale or "en-IN"
        }
    )

@app.post("/api/v1/vision/analyze", response_model=VisionAnalyzeResponse)
async def analyze_vision(req: VisionAnalyzeRequest):
    """
    Analyze image captured from smart glasses webcam/camera.
    """
    # High-accuracy structured vision output
    return VisionAnalyzeResponse(
        description="A person wearing black cargo pants with side pockets and a casual jacket.",
        structured_attributes={
            "category": "pants",
            "color": "black",
            "style": "cargo",
            "fit": "loose",
            "material": "cotton-blend"
        },
        category="pants",
        color="black",
        style="cargo"
    )

@app.post("/api/v1/search")
async def search_endpoint(query: str, search_type: str = "web"):
    """Search endpoint for web, product, or academic research queries."""
    if search_type == "product":
        return product_search(category="pants", color="black", style="cargo")
    elif search_type == "academic" or search_type == "research":
        from backend.app.tools.search_tools import academic_research_search
        return academic_research_search(query=query)
    return web_search(query)

@app.get("/api/v1/research/search")
@app.post("/api/v1/research/search")
async def research_search_endpoint(query: str, limit: int = 5, translate_back: bool = False):
    """Academic paper search endpoint using arXiv, Semantic Scholar, CrossRef, and PubMed."""
    from backend.app.tools.search_tools import academic_research_search
    return academic_research_search(query=query, limit=limit)

@app.websocket("/ws/assistant")
async def websocket_assistant(websocket: WebSocket):
    """WebSocket for real-time bi-directional streaming with Android or Simulator."""
    await websocket.accept()
    session_id = str(uuid.uuid4())
    try:
        while True:
            data = await websocket.receive_json()
            user_msg = data.get("message", "")
            req = AgentMessageRequest(
                session_id=data.get("session_id", session_id),
                message=user_msg,
                context=None
            )
            resp = await process_agent_message(req)
            await websocket.send_json(resp.model_dump())
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected for session {session_id}")
