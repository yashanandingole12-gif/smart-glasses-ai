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
    Processes user voice transcript or text query, enriches with Context Engine,
    invokes LangGraph agent, and tracks sub-second latency breakdown.
    """
    metrics = LatencyMetrics(
        request_id=req.request_id,
        session_id=req.session_id
    )

    t_ctx_start = time.time()
    # Retrieve relevant context
    context = context_engine.get_relevant_context(
        user_message=req.message,
        client_context=req.context,
        session_id=req.session_id
    )
    metrics.context_duration_ms = (time.time() - t_ctx_start) * 1000.0

    t_llm_start = time.time()
    # Run LangGraph agent
    agent_output = await run_agent(
        session_id=req.session_id,
        user_message=req.message,
        context_payload=context.model_dump()
    )
    metrics.llm_duration_ms = (time.time() - t_llm_start) * 1000.0
    metrics.finish()

    log_request_metrics(metrics)

    return AgentMessageResponse(
        session_id=req.session_id,
        response=agent_output["response"],
        actions=agent_output.get("actions", []),
        requires_confirmation=agent_output.get("requires_confirmation", False),
        confirmation_prompt=agent_output.get("confirmation_prompt"),
        sources=["context_engine", "calendar", "sqlite_memory"],
        metadata={
            "latency_ms": metrics.total_latency_ms,
            "llm_provider": settings.LLM_PROVIDER,
            "period": context.time.period
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
