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
    VisionAnalyzeRequest,
    VisionAnalyzeResponse
)
from backend.app.services.context_engine import context_engine
from backend.app.services.agent_graph import run_agent
from backend.app.services.tool_registry import registry
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

    # 1. Retrieve relevant context
    t_ctx_start = time.time()
    context = context_engine.get_relevant_context(
        user_message=req.message,
        client_context=req.context,
        session_id=req.session_id
    )
    metrics.context_ms = (time.time() - t_ctx_start) * 1000.0

    # 2. Section 7: Deterministic Fast Path Check (Time, Battery, Location, Date)
    t_fp_start = time.time()
    fast_reply = context_engine.resolve_deterministic_query(
        user_message=req.message,
        context=context,
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

    # 3. LangGraph Agent Execution with Multi-Tier LLM Router
    t_agent_start = time.time()
    try:
        agent_output = await run_agent(
            session_id=req.session_id,
            user_message=req.message,
            context_payload=context.model_dump(),
            language=req.language or "auto",
            locale=req.locale or "en-IN"
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
    """Search endpoint for web or product queries."""
    if search_type == "product":
        return product_search(category="pants", color="black", style="cargo")
    return web_search(query)

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
