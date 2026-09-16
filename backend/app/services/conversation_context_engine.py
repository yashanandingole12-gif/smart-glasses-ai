import time
import threading
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger("SmartGlasses.ConversationContextEngine")

DEFAULT_CONTEXT_TTL_SECONDS = 900.0  # 15 minutes TTL for short-term conversation context

class ActiveSessionContext:
    def __init__(self, session_id: str):
        self.session_id: str = session_id
        self.active_subject: Optional[str] = None
        self.active_entity: Dict[str, Any] = {}
        self.active_email: Dict[str, Any] = {
            "messages": [],
            "selected": None,
            "thread_id": None,
            "query": None
        }
        self.active_calendar: Dict[str, Any] = {
            "events": [],
            "selected": None,
            "date_str": None
        }
        self.active_sms: Dict[str, Any] = {
            "contact": None,
            "phone": None,
            "messages": [],
            "selected": None
        }
        self.active_contact: Optional[Dict[str, Any]] = None
        self.active_contact_disambiguation: Optional[Dict[str, Any]] = None
        self.active_search: Dict[str, Any] = {
            "query": None,
            "results": [],
            "selected": None
        }
        self.active_document: Optional[Dict[str, Any]] = None
        self.active_calculation: Optional[Dict[str, Any]] = None
        self.active_vision: Optional[Dict[str, Any]] = None
        self.previous_intent: Optional[str] = None
        self.previous_response: Optional[str] = None
        self.previous_tool_result: Optional[Any] = None
        self.updated_at: float = time.time()

    def touch(self):
        self.updated_at = time.time()

    def is_expired(self, ttl_seconds: float = DEFAULT_CONTEXT_TTL_SECONDS) -> bool:
        return (time.time() - self.updated_at) > ttl_seconds

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "active_subject": self.active_subject,
            "active_entity": self.active_entity,
            "active_email": self.active_email,
            "active_calendar": self.active_calendar,
            "active_sms": self.active_sms,
            "active_contact": self.active_contact,
            "active_contact_disambiguation": self.active_contact_disambiguation,
            "active_search": self.active_search,
            "active_document": self.active_document,
            "active_calculation": self.active_calculation,
            "active_vision": self.active_vision,
            "previous_intent": self.previous_intent,
            "previous_response": self.previous_response,
            "previous_tool_result": self.previous_tool_result,
            "updated_at": self.updated_at
        }


class ConversationContextEngine:
    """
    Thread-safe, TTL-bounded Multi-Turn Conversation Context Engine.
    Maintains active subjects, referents, ordinal selections, and cross-tool state
    strictly separated from long-term user profile data.
    """

    def __init__(self, ttl_seconds: float = DEFAULT_CONTEXT_TTL_SECONDS):
        self._sessions: Dict[str, ActiveSessionContext] = {}
        self._lock = threading.RLock()
        self.ttl_seconds = ttl_seconds

    def _cleanup_expired(self):
        now = time.time()
        expired_keys = [
            sid for sid, ctx in self._sessions.items()
            if (now - ctx.updated_at) > self.ttl_seconds
        ]
        for sid in expired_keys:
            self._sessions.pop(sid, None)

    def get_session(self, session_id: str) -> ActiveSessionContext:
        with self._lock:
            self._cleanup_expired()
            if session_id not in self._sessions:
                self._sessions[session_id] = ActiveSessionContext(session_id)
            ctx = self._sessions[session_id]
            ctx.touch()
            return ctx

    def get_context(self, session_id: str) -> ActiveSessionContext:
        """Alias for get_session for consistent API access."""
        return self.get_session(session_id)

    def clear_context(self, session_id: str):
        """Alias for clear for consistent API access."""
        self.clear(session_id)

    def update_subject(self, session_id: str, subject: str, entity_data: Optional[Dict[str, Any]] = None):
        with self._lock:
            ctx = self.get_session(session_id)
            if subject:
                ctx.active_subject = subject.strip()
            if entity_data:
                ctx.active_entity.update(entity_data)
            ctx.touch()

    def update_email(
        self,
        session_id: str,
        messages: Optional[List[Dict[str, Any]]] = None,
        selected: Optional[Dict[str, Any]] = None,
        query: Optional[str] = None
    ):
        with self._lock:
            ctx = self.get_session(session_id)
            if messages is not None:
                ctx.active_email["messages"] = list(messages)
            if selected is not None:
                ctx.active_email["selected"] = dict(selected)
                ctx.active_email["thread_id"] = selected.get("thread_id") or selected.get("id")
            if query is not None:
                ctx.active_email["query"] = query
            ctx.touch()

    def update_calendar(
        self,
        session_id: str,
        events: Optional[List[Dict[str, Any]]] = None,
        selected: Optional[Dict[str, Any]] = None,
        date_str: Optional[str] = None
    ):
        with self._lock:
            ctx = self.get_session(session_id)
            if events is not None:
                ctx.active_calendar["events"] = list(events)
            if selected is not None:
                ctx.active_calendar["selected"] = dict(selected)
            if date_str is not None:
                ctx.active_calendar["date_str"] = date_str
            ctx.touch()

    def update_sms(
        self,
        session_id: str,
        contact: Optional[str] = None,
        phone: Optional[str] = None,
        messages: Optional[List[Dict[str, Any]]] = None,
        selected: Optional[Dict[str, Any]] = None
    ):
        with self._lock:
            ctx = self.get_session(session_id)
            if contact is not None:
                ctx.active_sms["contact"] = contact
            if phone is not None:
                ctx.active_sms["phone"] = phone
            if messages is not None:
                ctx.active_sms["messages"] = list(messages)
            if selected is not None:
                ctx.active_sms["selected"] = dict(selected)
            ctx.touch()

    def update_contact(self, session_id: str, contact_data: Dict[str, Any]):
        with self._lock:
            ctx = self.get_session(session_id)
            ctx.active_contact = dict(contact_data)
            ctx.touch()

    def update_contact_disambiguation(
        self,
        session_id: str,
        candidates: List[Dict[str, Any]],
        action: str = "call",
        message_body: Optional[str] = None,
        query: Optional[str] = None,
        target_query: Optional[str] = None,
        body: Optional[str] = None
    ):
        with self._lock:
            ctx = self.get_session(session_id)
            ctx.active_contact_disambiguation = {
                "candidates": list(candidates),
                "action": action,
                "message_body": message_body or body,
                "body": message_body or body,
                "query": query or target_query,
                "target_query": query or target_query,
                "timestamp": time.time()
            }
            ctx.touch()

    def get_active_contact_disambiguation(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            ctx = self.get_session(session_id)
            if ctx.active_contact_disambiguation:
                if (time.time() - ctx.active_contact_disambiguation.get("timestamp", 0)) > self.ttl_seconds:
                    ctx.active_contact_disambiguation = None
                    return None
                return ctx.active_contact_disambiguation
            return None

    def clear_contact_disambiguation(self, session_id: str):
        with self._lock:
            ctx = self.get_session(session_id)
            ctx.active_contact_disambiguation = None
            ctx.touch()

    def update_search(self, session_id: str, query: str, results: List[Dict[str, Any]]):
        with self._lock:
            ctx = self.get_session(session_id)
            ctx.active_search["query"] = query
            ctx.active_search["results"] = list(results)
            ctx.touch()

    def update_document(self, session_id: str, file_id: str, filename: str, text: str):
        with self._lock:
            ctx = self.get_session(session_id)
            ctx.active_document = {
                "file_id": file_id,
                "filename": filename,
                "text": text[:1000] if text else ""
            }
            ctx.touch()

    def update_calculation(
        self,
        session_id: str,
        expression: str,
        result: Any,
        variable: Optional[str] = None,
        approx_result: Optional[Any] = None,
        steps: Optional[List[str]] = None,
        solution_display: Optional[str] = None,
        text_response: Optional[str] = None,
        raw_query: Optional[str] = None
    ):
        with self._lock:
            ctx = self.get_session(session_id)
            ctx.active_calculation = {
                "expression": expression,
                "result": result,
                "variable": variable,
                "approx_result": approx_result,
                "steps": list(steps) if steps else [],
                "solution_display": solution_display or str(result),
                "text_response": text_response or f"Result is {result}",
                "raw_query": raw_query
            }
            ctx.touch()

    def update_vision_context(
        self,
        session_id: str,
        capture_id: str,
        metadata: Dict[str, Any],
        result: Dict[str, Any],
        description: str,
        objects: Optional[List[str]] = None,
        text_detected: Optional[List[str]] = None,
        raw_query: Optional[str] = None
    ):
        with self._lock:
            ctx = self.get_session(session_id)
            ctx.active_vision = {
                "capture_id": capture_id,
                "timestamp": metadata.get("timestamp", time.time()),
                "device_id": metadata.get("device_id", "SmartGlasses-S3"),
                "width": metadata.get("width", 640),
                "height": metadata.get("height", 480),
                "mime_type": metadata.get("mime_type", "image/jpeg"),
                "byte_size": metadata.get("byte_size", 0),
                "checksum": metadata.get("checksum", ""),
                "description": description,
                "objects": list(objects) if objects else [],
                "text_detected": list(text_detected) if text_detected else [],
                "structured_attributes": result.get("structured_attributes", {}),
                "category": result.get("category"),
                "color": result.get("color"),
                "style": result.get("style"),
                "raw_query": raw_query,
                "provider": result.get("provider", "gemini-flash"),
                "latency_ms": result.get("latency_ms", 0.0)
            }
            ctx.touch()

    def update_turn(
        self,
        session_id: str,
        intent: Optional[str] = None,
        response: Optional[str] = None,
        tool_result: Optional[Any] = None
    ):
        with self._lock:
            ctx = self.get_session(session_id)
            if intent:
                ctx.previous_intent = intent
            if response:
                ctx.previous_response = response
            if tool_result is not None:
                ctx.previous_tool_result = tool_result
            ctx.touch()

    def clear(self, session_id: str):
        with self._lock:
            self._sessions.pop(session_id, None)


conversation_context_engine = ConversationContextEngine()
