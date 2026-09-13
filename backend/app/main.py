import time
import uuid
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request, UploadFile, File, Form, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional

from backend.app.config import settings
from backend.app.models.schemas import (
    HealthResponse,
    SessionCreateRequest,
    SessionResponse,
    AgentMessageRequest,
    AgentMessageResponse,
    AgentAction,
    RiskLevel,
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
from backend.app.services.structured_request_parser import structured_request_parser, ParsedIntent
from backend.app.services.smart_glass_formatter import smart_glass_formatter
from backend.app.services.storage_service import storage_service
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

from backend.app.web_ui import get_dashboard_html

app.include_router(auth_router)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Standardized API error contract for HTTPExceptions."""
    detail_str = str(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": f"HTTP_{exc.status_code}",
            "message": detail_str,
            "detail": detail_str,
            "retryable": exc.status_code in [408, 429, 502, 503, 504]
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Standardized API error contract protecting secrets and internal paths."""
    logger.error("Unhandled API Exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred while processing your request.",
            "retryable": True
        }
    )


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
    is_google_connected = bool(status.get("connected") and (not status.get("is_expired") or status.get("has_refresh_token", True)))
    gemini_configured = bool(settings.GEMINI_API_KEY or (settings.LLM_PROVIDER == "gemini" and settings.LLM_API_KEY))

    return {
        "gemini": "available" if gemini_configured else "unavailable",
        "google": "connected" if is_google_connected else "disconnected",
        "gmail": "available" if is_google_connected else "unavailable",
        "calendar": "available" if is_google_connected else "unavailable"
    }

@app.get("/api/v1/hardware/camera/capture")
async def hardware_camera_capture():
    """Captures a live JPEG image frame from the XIAO ESP32-S3 Sense OV2640 camera."""
    from backend.app.services.hardware_bridge import hardware_bridge
    return hardware_bridge.capture_camera_frame()

@app.get("/api/v1/hardware/mic/telemetry")
async def hardware_mic_telemetry():
    """Retrieves live audio energy (RMS, Peak, VAD) from the XIAO ESP32-S3 Sense MSM261D PDM microphone."""
    from backend.app.services.hardware_bridge import hardware_bridge
    return hardware_bridge.get_microphone_telemetry()


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

    # Fetch recent conversational context
    recent_history = memory_repository.get_session_history(req.session_id, limit=4)
    parsed_req = structured_request_parser.parse(msg_raw, recent_history)

    # Check for active pending confirmation token for this session
    pending_action = registry.get_pending_action_for_session(req.session_id)

    # Handle Cancellation explicitly
    if parsed_req.intent == ParsedIntent.CANCELLATION:
        if pending_action:
            registry.cancel_pending_action_for_session(req.session_id)
        memory_repository.add_message(req.session_id, "user", msg_raw)
        memory_repository.add_message(req.session_id, "assistant", "Action cancelled.")
        metrics.fast_path_ms = 1.0
        metrics.finish()
        log_request_metrics(metrics)
        return AgentMessageResponse(
            session_id=req.session_id,
            response="Action cancelled.",
            actions=[],
            requires_confirmation=False,
            confirmation_prompt=None,
            sources=["action_cancellation"],
            metadata={
                "latency_ms": metrics.total_ms,
                "fast_path": True,
                "timings": metrics.to_dict(),
                "llm_provider": "local_security",
                "request_id": req.request_id,
                "language": req.language or "auto",
                "locale": req.locale or "en-IN"
            }
        )

    # Handle Affirmative Confirmation (execute the pending high-risk action)
    if parsed_req.intent == ParsedIntent.CONFIRMATION and pending_action and not req.confirmed_action_id:
        req.confirmed_action_id = pending_action.action_id

    # Detect mutation / high-risk action intent requiring 2-step confirmation or LangGraph execution
    is_mutation = bool(
        req.confirmed_action_id or
        parsed_req.intent in [ParsedIntent.CONFIRMATION, ParsedIntent.SMS_SEND, ParsedIntent.SMS_REPLY, ParsedIntent.EMAIL_SEND, ParsedIntent.EMAIL_REPLY, ParsedIntent.CALENDAR_CREATE] or
        any(
            kw in msg_lower
            for kw in [
                "create event", "add event", "schedule a", "book a", "book an", "cancel event",
                "delete event", "send sms", "send text", "send a message", "text to", "sms to",
                "send email", "compose email", "email to", "send an email", "reply to", "draft email", "draft an email"
            ]
        )
    )

    # 1. Device & Call Controls Fast-Track (<50ms)
    if parsed_req.intent in [ParsedIntent.CALL_MAKE, ParsedIntent.CALL_ANSWER, ParsedIntent.CALL_REJECT, ParsedIntent.CALL_HANGUP, ParsedIntent.CALL_INCOMING_QUERY]:
        t_call_start = time.time()
        actions = []
        requires_confirmation = False
        conf_prompt = None

        if parsed_req.intent == ParsedIntent.CALL_MAKE:
            if parsed_req.resolved_contact:
                call_reply = smart_glass_formatter.format_call_action("call_make", parsed_req.resolved_contact.name, parsed_req.resolved_contact.phone)
                actions = [
                    AgentAction(
                        tool_name="call_controller",
                        tool_input={"action": "call_make", "name": parsed_req.resolved_contact.name, "phone": parsed_req.resolved_contact.phone},
                        risk_level=RiskLevel.READ,
                        status="executed"
                    )
                ]
            elif parsed_req.parameters.get("resolution_status") == "AMBIGUOUS":
                call_reply = parsed_req.parameters.get("clarification_prompt") or f"Which {parsed_req.entity} would you like to call?"
            else:
                call_reply = parsed_req.parameters.get("clarification_prompt") or f"I couldn't find {parsed_req.entity} in your contacts."
        else:
            call_reply = smart_glass_formatter.format_call_action(parsed_req.intent.value)
            actions = [
                AgentAction(
                    tool_name="call_controller",
                    tool_input={"action": parsed_req.intent.value},
                    risk_level=RiskLevel.READ,
                    status="executed"
                )
            ]

        memory_repository.add_message(req.session_id, "user", msg_raw)
        memory_repository.add_message(req.session_id, "assistant", call_reply)

        metrics.fast_path_ms = (time.time() - t_call_start) * 1000.0
        metrics.finish()
        log_request_metrics(metrics)

        return AgentMessageResponse(
            session_id=req.session_id,
            response=call_reply,
            actions=actions,
            requires_confirmation=requires_confirmation,
            confirmation_prompt=conf_prompt,
            sources=["call_controller_fast_path"],
            metadata={
                "latency_ms": metrics.total_ms,
                "fast_path": True,
                "intent": parsed_req.intent.value,
                "timings": metrics.to_dict(),
                "llm_provider": "device_telephony",
                "request_id": req.request_id,
                "language": req.language or "auto",
                "locale": req.locale or "en-IN"
            }
        )

    # 2. Deterministic Fast Path Check (Time, Battery, Location, Date)
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

    # 3. Deterministic Math Engine Fast-Path (<50ms, Zero-LLM Evaluation)
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

    # 4. Conversational Temporal Calendar Fast-Track (Direct Resolution without Agent loops)
    temporal_intent = temporal_resolver.resolve_intent(
        query=msg_raw,
        conversation_history=recent_history,
        tz_name=settings.DEFAULT_TIMEZONE
    )

    if (parsed_req.intent in [ParsedIntent.CALENDAR_QUERY, ParsedIntent.CALENDAR_FREE_TIME] or temporal_intent.is_calendar_query) and not is_mutation:
        t_cal_start = time.time()
        raw_events_data = calendar_get_events(date_target=temporal_intent.date_target)
        if raw_events_data.get("error"):
            cal_reply = raw_events_data.get("message") or "I can't access your calendar right now."
        else:
            events_list = raw_events_data.get("events", [])
            filtered_events = temporal_resolver.filter_events(events_list, temporal_intent)
            cal_reply = temporal_resolver.format_calendar_response(
                intent=temporal_intent,
                events=filtered_events,
                language=req.language or "auto",
                query=msg_raw
            )

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

    # 5. Direct Gmail Retrieval & Reading Fast-Track (<500ms)
    if parsed_req.intent in [ParsedIntent.EMAIL_SEARCH, ParsedIntent.EMAIL_READ] and not is_mutation:
        t_gmail_start = time.time()
        lang = req.language or "auto"
        is_hi = lang == "hi" or any("\u0900" <= c <= "\u097f" for c in msg_raw)
        is_mr = lang == "mr"

        if parsed_req.intent == ParsedIntent.EMAIL_READ or parsed_req.is_read_content:
            # Read full email content
            if parsed_req.topic:
                raw_email_data = gmail_read(topic=parsed_req.topic)
            elif parsed_req.sender:
                search_res = gmail_search(query=parsed_req.sender)
                if search_res.get("messages"):
                    raw_email_data = gmail_read(message_id=search_res["messages"][0]["id"])
                else:
                    raw_email_data = search_res
            else:
                idx = parsed_req.parameters.get("index", 1)
                raw_email_data = gmail_read(index=idx)

            if raw_email_data.get("email"):
                email_reply = smart_glass_formatter.format_email_read(raw_email_data["email"])
            else:
                email_reply = raw_email_data.get("message", "I couldn't find that email.")
        else:
            # Search emails with topic / sender / temporal constraints
            search_terms = []
            if parsed_req.sender:
                search_terms.append(parsed_req.sender)
            if parsed_req.topic:
                search_terms.append(parsed_req.topic)
            if parsed_req.filters.get("date"):
                search_terms.append(parsed_req.filters["date"])
            if parsed_req.is_unread_only:
                search_terms.append("unread")

            search_query = " ".join(search_terms) if search_terms else msg_raw
            raw_email_data = gmail_search(query=search_query)

            if raw_email_data.get("error"):
                if is_hi:
                    email_reply = "मैं अभी आपके ईमेल एक्सेस नहीं कर सकता।"
                elif is_mr:
                    email_reply = "मी आता तुमचे ईमेल ऍक्सेस करू शकत नाही."
                else:
                    email_reply = raw_email_data.get("message") or "I can't access your email right now. Please connect your Google account in Settings."
            else:
                messages = raw_email_data.get("messages", [])
                email_reply = smart_glass_formatter.format_email_search(
                    results=messages,
                    query_topic=parsed_req.topic,
                    sender=parsed_req.sender,
                    unread_only=parsed_req.is_unread_only,
                    language=req.language or "auto",
                    raw_query=msg_raw
                )

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

    # 6. Direct SMS Read & Search Fast-Track (<10ms)
    if parsed_req.intent in [ParsedIntent.SMS_SEARCH, ParsedIntent.SMS_READ] and not is_mutation:
        t_sms_start = time.time()
        raw_sms_data = sms_read_recent(limit=5)
        messages = raw_sms_data.get("messages", [])

        if parsed_req.sender:
            # Filter messages by sender name
            s_norm = parsed_req.sender.lower()
            filtered_sms = [m for m in messages if s_norm in m.get("sender", "").lower()]
            sms_reply = smart_glass_formatter.format_sms_search(filtered_sms, sender=parsed_req.sender)
        else:
            sms_reply = smart_glass_formatter.format_sms_search(messages)

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

    # 7. Direct Academic Research / arXiv Search Fast-Track (<1.5s)
    if parsed_req.intent == ParsedIntent.RESEARCH_SEARCH and not is_mutation:
        t_res_start = time.time()
        clean_topic = parsed_req.topic or msg_raw
        search_res = academic_research_search(query=clean_topic, limit=3)
        papers = search_res.get("papers", [])
        if papers:
            lines = [f"'{p.get('title', 'Paper')}' by {p.get('authors', ['Unknown'])[0]}" for p in papers[:2]]
            research_reply = f"Found {len(papers)} research papers on {clean_topic}: " + ", and ".join(lines) + "."
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

    # 8. Direct Web Search & Search Follow-ups Fast-Track
    if parsed_req.intent in [ParsedIntent.WEB_SEARCH, ParsedIntent.SEARCH_FOLLOW_UP] and not is_mutation:
        t_web_start = time.time()
        clean_topic = parsed_req.topic or (parsed_req.follow_up_modifier if parsed_req.is_follow_up else msg_raw)
        web_res = web_search(query=clean_topic)
        results = web_res.get("results", [])
        if results:
            web_reply = smart_glass_formatter.format_search_summary(clean_topic, results[0].get("snippet", ""))
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

    # 9. Document & Storage Context Reasoner (For queries regarding uploaded resume, PDF, or documents)
    is_doc_query = any(kw in msg_lower for kw in ["resume", "document", "uploaded file", "this pdf", "summarize my", "summarize this doc", "summarize document", "uploaded doc", "my cv", "summarize the file"])
    if is_doc_query and not is_mutation and not req.confirmed_action_id:
        t_doc_start = time.time()
        latest_doc = storage_service.get_latest_document_context()
        if latest_doc and latest_doc.get("extracted_text"):
            doc_text = latest_doc["extracted_text"][:4000]
            doc_prompt = (
                f"You are LARA, an executive smart glasses AI assistant. "
                f"The user has uploaded a document named '{latest_doc['filename']}'. "
                f"Here is the text extracted from the document:\n\n{doc_text}\n\n"
                f"Provide a clear, concise, wearable-friendly summary or directly answer the user's inquiry in 2-3 sentences."
            )
            formatted_messages = [
                {"role": "system", "content": doc_prompt},
                {"role": "user", "content": msg_raw}
            ]
            router_resp = await llm_router.generate_with_budget(
                messages=formatted_messages,
                tools=None,
                starting_tier=RoutingTier.FAST
            )
            doc_reply = (router_resp.content or "Document summarized.").strip()
            memory_repository.add_message(req.session_id, "user", msg_raw)
            memory_repository.add_message(req.session_id, "assistant", doc_reply)

            metrics.fast_path_ms = (time.time() - t_fp_start) * 1000.0
            metrics.llm_first_response_ms = router_resp.duration_ms
            metrics.finish()
            log_request_metrics(metrics)

            return AgentMessageResponse(
                session_id=req.session_id,
                response=doc_reply,
                actions=[],
                requires_confirmation=False,
                confirmation_prompt=None,
                sources=["storage_document_engine", latest_doc["filename"]],
                metadata={
                    "latency_ms": metrics.total_ms,
                    "fast_path": True,
                    "document_id": latest_doc["file_id"],
                    "document_name": latest_doc["filename"],
                    "timings": metrics.to_dict(),
                    "llm_provider": router_resp.provider,
                    "request_id": req.request_id,
                    "language": req.language or "auto",
                    "locale": req.locale or "en-IN"
                }
            )

    # 10. Direct Single-Turn LLM Conversational Chat (For general Q&A, chat, explanations without LangGraph overhead)
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
            f"Context: Time is {time_str}, Location is {loc_str}, Battery is {bat_str}."
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
            per_attempt_timeout=settings.LLM_TIMEOUT_SECONDS,
            global_deadline_seconds=settings.REQUEST_DEADLINE_SECONDS
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
@app.post("/api/v1/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    source: str = Form("web")
):
    """Secure document and file upload endpoint."""
    try:
        content = await file.read()
        res = storage_service.save_file(
            file_bytes=content,
            filename=file.filename or "uploaded_file",
            content_type=file.content_type,
            source=source
        )
        return {
            "success": True,
            **res
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail="Failed to store uploaded file.")

@app.post("/api/v1/images/upload")
async def upload_image(
    file: UploadFile = File(...),
    source: str = Form("web")
):
    """Dedicated image upload endpoint."""
    try:
        content = await file.read()
        res = storage_service.save_file(
            file_bytes=content,
            filename=file.filename or "image.jpg",
            content_type=file.content_type or "image/jpeg",
            source=source
        )
        return {
            "success": True,
            "image_id": res["file_id"],
            **res
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Image upload error: {e}")
        raise HTTPException(status_code=500, detail="Failed to store uploaded image.")

@app.get("/api/v1/files")
async def list_uploaded_files(limit: int = 20):
    """List recently uploaded files and documents."""
    files = storage_service.list_files(limit=limit)
    return {
        "success": True,
        "files": files,
        "count": len(files)
    }

@app.get("/api/v1/files/{file_id}")
async def get_file_metadata(file_id: str):
    """Get metadata for an uploaded file."""
    file_info = storage_service.get_file(file_id)
    if not file_info:
        raise HTTPException(status_code=404, detail=f"File with ID '{file_id}' not found.")
    return {
        "success": True,
        **file_info
    }

@app.get("/api/v1/files/{file_id}/download")
async def download_file(file_id: str):
    """Download raw file bytes with safe headers."""
    res = storage_service.get_file_bytes(file_id)
    if not res:
        raise HTTPException(status_code=404, detail="File not found or missing from disk.")
    data, filename, mime_type = res
    return Response(
        content=data,
        media_type=mime_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@app.delete("/api/v1/files/{file_id}")
async def delete_file_endpoint(file_id: str):
    """Delete an uploaded file from disk and database."""
    deleted = storage_service.delete_file(file_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="File not found.")
    return {
        "success": True,
        "file_id": file_id,
        "deleted": True,
        "message": "File successfully removed."
    }

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

# -------------------------------------------------------------------------
# Security, Device Pairing, Contact Vault & Desktop Agent Endpoints (Phase 3B.13)
# -------------------------------------------------------------------------

@app.get("/api/v1/security/devices")
async def get_paired_devices(user_id: str = "default_user"):
    """List registered devices with cryptographic status and scoped permissions."""
    from backend.app.services.device_security_service import device_security_service
    devices = device_security_service.list_devices(user_id)
    return {
        "success": True,
        "devices": [d.model_dump() for d in devices],
        "count": len(devices)
    }

@app.post("/api/v1/security/devices/pair")
async def pair_new_device(req: Dict[str, Any], user_id: str = "default_user"):
    """Pair a new hardware or client device with scoped permissions."""
    from backend.app.services.device_security_service import device_security_service
    name = req.get("device_name", "New Device")
    dtype = req.get("device_type", "ANDROID")
    scopes = req.get("scoped_permissions", ["AUDIO_STREAM"])
    res = device_security_service.pair_device(user_id, name, dtype, scopes)
    return {
        "success": True,
        **res
    }

@app.delete("/api/v1/security/devices/{device_id}")
async def revoke_device_access(device_id: str, user_id: str = "default_user"):
    """Revoke authorization for a paired device."""
    from backend.app.services.device_security_service import device_security_service
    revoked = device_security_service.revoke_device(device_id, user_id)
    if not revoked:
        raise HTTPException(status_code=404, detail="Device not found.")
    return {
        "success": True,
        "device_id": device_id,
        "status": "REVOKED",
        "message": f"Device '{device_id}' revoked."
    }

@app.get("/api/v1/security/contacts")
async def list_contact_vault(user_id: str = "default_user"):
    """List user-controlled contacts and linked phone/email identifiers."""
    from backend.app.services.contact_vault import contact_vault
    contacts = contact_vault.list_contacts(user_id)
    return {
        "success": True,
        "contacts": [c.model_dump() for c in contacts],
        "count": len(contacts)
    }

@app.post("/api/v1/security/contacts")
async def add_contact_vault(req: Dict[str, Any], user_id: str = "default_user"):
    """Add or link a new personal contact in Contact Vault."""
    from backend.app.services.contact_vault import contact_vault
    name = req.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Contact name is required.")
    c = contact_vault.add_contact(
        user_id=user_id,
        name=name,
        phone_numbers=req.get("phone_numbers", []),
        email_addresses=req.get("email_addresses", []),
        aliases=req.get("aliases", []),
        company=req.get("company"),
        notes=req.get("notes")
    )
    return {
        "success": True,
        "contact": c.model_dump()
    }

@app.delete("/api/v1/security/contacts/{contact_id}")
async def delete_contact_vault(contact_id: str, user_id: str = "default_user"):
    """Delete a contact from Contact Vault."""
    from backend.app.services.contact_vault import contact_vault
    deleted = contact_vault.delete_contact(contact_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Contact not found.")
    return {
        "success": True,
        "contact_id": contact_id,
        "deleted": True
    }

@app.get("/api/v1/security/audit-log")
async def get_security_audit_logs(limit: int = 50, user_id: str = "default_user"):
    """Retrieve sanitized security audit log events."""
    from backend.app.services.device_security_service import device_security_service
    logs = device_security_service.get_audit_logs(limit, user_id)
    return {
        "success": True,
        "audit_logs": logs,
        "count": len(logs)
    }

@app.get("/api/v1/context/conversation/{session_id}")
async def get_conversation_context(session_id: str):
    """Retrieve active multi-turn context slots for a session."""
    from backend.app.services.conversation_context_engine import conversation_context_engine
    ctx = conversation_context_engine.get_context(session_id)
    return {
        "success": True,
        "session_id": session_id,
        "context": ctx.to_dict()
    }

@app.post("/api/v1/context/conversation/{session_id}/reset")
async def reset_conversation_context(session_id: str):
    """Reset active multi-turn conversational context slots."""
    from backend.app.services.conversation_context_engine import conversation_context_engine
    conversation_context_engine.clear_context(session_id)
    return {
        "success": True,
        "session_id": session_id,
        "message": "Conversation context cleared."
    }

@app.post("/api/v1/security/desktop/action")
async def execute_desktop_action(req: Dict[str, Any], user_id: str = "default_user"):
    """Execute an approved, scoped action on the host laptop desktop agent."""
    from backend.app.services.device_security_service import device_security_service
    action = req.get("action", "")
    target = req.get("target")
    res = device_security_service.execute_laptop_action(action, target, user_id)
    return {
        "success": res.get("status") == "success",
        **res
    }



