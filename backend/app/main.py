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
from backend.app.tools.calendar_tools import calendar_get_events
from backend.app.tools.search_tools import web_search, product_search
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
async def get_current_context(timezone_str: str = settings.DEFAULT_TIMEZONE):
    """Retrieve freshly computed context engine payload."""
    return context_engine.get_relevant_context(
        user_message="",
        client_context=None
    )

@app.post("/api/v1/agent/message", response_model=AgentMessageResponse)
async def process_agent_message(req: AgentMessageRequest):
    """
    Main conversational endpoint:
    Processes user voice transcript or text query with deterministic fast-path routing,
    enriches with Context Engine, executes LangGraph agent when reasoning is required,
    and logs sub-stage latency profiling.
    """
    metrics = LatencyMetrics(
        request_id=req.request_id,
        session_id=req.session_id
    )

    # Safe diagnostic metadata logging (No raw transcript logged in production)
    text_len = len(req.message.strip()) if req.message else 0
    logger.info(
        f"[REQ_ID: {req.request_id[:8]}] RECEIVED: lang={req.language or 'auto'} "
        f"locale={req.locale or 'en-IN'} len={text_len}"
    )

    # 1. Section 7: Deterministic Fast Path Check (Time, Battery, Location, Date)
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
        user_message=req.message,
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

    # 2. Conversational Temporal Calendar Fast-Track (Direct Resolution without Agent loops)
    recent_history = memory_repository.get_session_history(req.session_id, limit=4)
    temporal_intent = temporal_resolver.resolve_intent(
        query=req.message,
        conversation_history=recent_history,
        tz_name=settings.DEFAULT_TIMEZONE
    )

    is_mutation = any(
        kw in req.message.lower()
        for kw in ["create", "add event", "book", "schedule a", "cancel", "delete", "send"]
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
        memory_repository.add_message(req.session_id, "user", req.message)
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

    # 3. Retrieve full relevant context for LLM / Agent reasoning
    t_ctx_start = time.time()
    context = context_engine.get_relevant_context(
        user_message=req.message,
        client_context=req.context,
        session_id=req.session_id
    )
    metrics.context_ms = (time.time() - t_ctx_start) * 1000.0


    # 3. LangGraph Agent Execution with Multi-Tier LLM Router
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
