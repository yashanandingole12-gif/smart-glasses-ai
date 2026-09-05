import logging
import httpx
import asyncio
import threading
import time
import concurrent.futures
from datetime import datetime
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

logger = logging.getLogger("SmartGlasses.EmailProvider")

class EmailProvider(ABC):
    """Abstract provider interface for email services (Laptop Mock / Google Gmail API)."""

    @abstractmethod
    def search(self, query: Optional[str] = None) -> Dict[str, Any]:
        """Search emails matching query or retrieve inbox overview."""
        pass

    @abstractmethod
    def read(self, message_id: Optional[str] = None, index: Optional[int] = None) -> Dict[str, Any]:
        """Read full content of an email by ID or 1-based index."""
        pass

    @abstractmethod
    def get_unread_count(self) -> int:
        """Get number of unread emails."""
        pass


class LaptopEmailProvider(EmailProvider):
    """Deterministic development email provider for laptop simulation."""

    def __init__(self):
        self._mock_emails = [
            {
                "id": "msg_001",
                "sender": "college.admin@university.edu",
                "subject": "Class Schedule Update: Room Change for ML Lecture",
                "snippet": "Please note today's Machine Learning lecture will be held in Room 302.",
                "timestamp": "07:45 AM",
                "read": False
            },
            {
                "id": "msg_002",
                "sender": "rahul.sharma@techcorp.com",
                "subject": "Review of Smart Glasses Prototype Architecture",
                "snippet": "Hey, reviewed the ESP32 and BLE specs. Looks great, let's sync at 3 PM.",
                "timestamp": "Yesterday",
                "read": True
            },
            {
                "id": "msg_003",
                "sender": "newsletter@dailytech.io",
                "subject": "Edge AI in Wearables 2026",
                "snippet": "New developments in on-device speech recognition and ultra-low power LLMs.",
                "timestamp": "Aug 20",
                "read": True
            }
        ]

    def search(self, query: Optional[str] = None) -> Dict[str, Any]:
        results = self._mock_emails
        if query:
            q = query.lower()
            results = [
                m for m in results
                if q in m["subject"].lower() or q in m["sender"].lower() or q in m["snippet"].lower()
            ]
        return {
            "count": len(results),
            "unread_count": sum(1 for m in results if not m.get("read", True)),
            "messages": results
        }

    def read(self, message_id: Optional[str] = None, index: Optional[int] = None) -> Dict[str, Any]:
        if index is not None and 1 <= index <= len(self._mock_emails):
            return {"status": "found", "email": self._mock_emails[index - 1]}
        if message_id:
            for m in self._mock_emails:
                if m["id"] == message_id:
                    return {"status": "found", "email": m}
        return {"status": "not_found", "message": "Email not found"}

    def get_unread_count(self) -> int:
        return sum(1 for m in self._mock_emails if not m.get("read", True))


class GmailCache:
    """Thread-safe 45-second cache for Gmail overview and unread metadata with single-flight protection."""
    def __init__(self, ttl_seconds: float = 45.0):
        self.ttl = ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._timestamps: Dict[str, float] = {}
        self._lock = threading.Lock()
        self._in_flight: Dict[str, threading.Event] = {}
        self._in_flight_results: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            if key in self._cache:
                if time.time() - self._timestamps.get(key, 0) < self.ttl:
                    return self._cache[key]
                else:
                    self._cache.pop(key, None)
                    self._timestamps.pop(key, None)
        return None

    def set(self, key: str, value: Dict[str, Any]) -> None:
        with self._lock:
            is_error = bool(value.get("error"))
            self._cache[key] = value
            self._timestamps[key] = time.time() if not is_error else (time.time() - self.ttl + 10.0)

    def invalidate(self, user_id: Optional[str] = None) -> None:
        with self._lock:
            if user_id:
                keys_to_del = [k for k in self._cache if k.startswith(f"{user_id}:")]
                for k in keys_to_del:
                    self._cache.pop(k, None)
                    self._timestamps.pop(k, None)
            else:
                self._cache.clear()
                self._timestamps.clear()

gmail_cache = GmailCache(ttl_seconds=45.0)
_gmail_client = httpx.Client(timeout=4.0, limits=httpx.Limits(max_keepalive_connections=5, max_connections=10))

class GoogleGmailProvider(EmailProvider):
    """
    Authoritative production Google Gmail provider using OAuth 2.0.
    Fetches real emails via the Gmail v1 API.
    Zero mock data fallbacks in production.
    """

    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id

    def _get_valid_token_sync(self) -> Optional[str]:
        from backend.app.services.token_service import token_service
        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(asyncio.run, token_service.get_valid_token(self.user_id)).result()
            return asyncio.run(token_service.get_valid_token(self.user_id))
        except Exception:
            return None

    def search(self, query: Optional[str] = None) -> Dict[str, Any]:
        t_start = datetime.now()
        q_param = query if query else "is:unread"
        cache_key = f"{self.user_id}:{q_param}"

        cached = gmail_cache.get(cache_key)
        if cached is not None:
            logger.debug(f"gmail_cache_hit user={self.user_id} key={cache_key}")
            return cached

        # Single-flight check
        event = None
        is_fetcher = False
        with gmail_cache._lock:
            if cache_key in gmail_cache._in_flight:
                event = gmail_cache._in_flight[cache_key]
            else:
                event = threading.Event()
                gmail_cache._in_flight[cache_key] = event
                is_fetcher = True

        if not is_fetcher and event is not None:
            event.wait(timeout=4.5)
            with gmail_cache._lock:
                res = gmail_cache._in_flight_results.get(cache_key)
            if res:
                return res
            return gmail_cache.get(cache_key) or {
                "count": 0,
                "unread_count": 0,
                "messages": [],
                "message": "I can't access your email right now."
            }

        try:
            token = self._get_valid_token_sync()
            if not token:
                logger.info(f"gmail_request account=<redacted> provider=google status=unauthenticated")
                res = {
                    "count": 0,
                    "unread_count": 0,
                    "messages": [],
                    "error": "Gmail is not connected.",
                    "message": "I can't access your email right now."
                }
                gmail_cache.set(cache_key, res)
                return res

            headers = {"Authorization": f"Bearer {token}"}

            try:
                # 1. List messages
                list_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
                resp = _gmail_client.get(list_url, headers=headers, params={"q": q_param, "maxResults": 5})
                if resp.status_code == 401:
                    logger.warning("Gmail API returned 401 Unauthorized; disconnecting expired token.")
                    try:
                        from backend.app.services.token_service import token_service
                        try:
                            loop = asyncio.get_running_loop()
                        except RuntimeError:
                            loop = None
                        if loop and loop.is_running():
                            with concurrent.futures.ThreadPoolExecutor() as pool:
                                pool.submit(asyncio.run, token_service.disconnect(self.user_id)).result()
                        else:
                            asyncio.run(token_service.disconnect(self.user_id))
                    except Exception:
                        pass
                    res = {
                        "count": 0,
                        "unread_count": 0,
                        "messages": [],
                        "error": "Gmail authentication expired.",
                        "message": "I can't access your email right now."
                    }
                    gmail_cache.set(cache_key, res)
                    return res
                elif resp.status_code == 403:
                    error_detail = ""
                    try:
                        err_json = resp.json().get("error", {})
                        error_detail = err_json.get("message", resp.text)
                    except Exception:
                        error_detail = resp.text
                    logger.error(
                        f"Gmail API returned 403 Forbidden: {error_detail}. "
                        "Action required: (1) Enable 'Gmail API' in Google Cloud Console: "
                        "https://console.cloud.google.com/apis/library/gmail.googleapis.com "
                        "(2) Re-authorize via http://localhost:8001/api/v1/auth/google to grant email permissions."
                    )
                    res = {
                        "count": 0,
                        "unread_count": 0,
                        "messages": [],
                        "error": f"Gmail API 403: {error_detail}",
                        "message": "I can't access your email right now."
                    }
                    gmail_cache.set(cache_key, res)
                    return res
                elif resp.status_code != 200:
                    logger.warning("Gmail API list returned %d: %s", resp.status_code, resp.text)
                    res = {
                        "count": 0,
                        "unread_count": 0,
                        "messages": [],
                        "error": f"Gmail API error (HTTP {resp.status_code})",
                        "message": "I can't access your email right now."
                    }
                    gmail_cache.set(cache_key, res)
                    return res

                data = resp.json()
                msg_ids = [m["id"] for m in data.get("messages", [])]
                if not msg_ids:
                    lat_ms = (datetime.now() - t_start).total_seconds() * 1000.0
                    logger.info(f"gmail_request account=<redacted> provider=google result_count=0 latency_ms={lat_ms:.1f}")
                    res = {
                        "count": 0,
                        "unread_count": 0,
                        "messages": [],
                        "status": "inbox_zero",
                        "message": "You have no unread emails."
                    }
                    gmail_cache.set(cache_key, res)
                    return res

                # 2. Concurrently fetch metadata for each message (Max concurrency 3)
                def _fetch_single_metadata(mid: str) -> Optional[Dict[str, Any]]:
                    msg_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{mid}"
                    try:
                        m_resp = _gmail_client.get(
                            msg_url,
                            headers=headers,
                            params={"format": "metadata", "metadataHeaders": ["From", "Subject", "Date"]}
                        )
                        if m_resp.status_code == 200:
                            m_data = m_resp.json()
                            headers_dict = {h["name"]: h["value"] for h in m_data.get("payload", {}).get("headers", [])}
                            return {
                                "id": mid,
                                "sender": headers_dict.get("From", "Unknown Sender"),
                                "subject": headers_dict.get("Subject", "No Subject"),
                                "snippet": m_data.get("snippet", ""),
                                "timestamp": headers_dict.get("Date", "Recent"),
                                "read": "UNREAD" not in m_data.get("labelIds", [])
                            }
                    except Exception:
                        pass
                    return None

                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
                    raw_parsed = pool.map(_fetch_single_metadata, msg_ids[:5])
                    parsed_messages = [m for m in raw_parsed if m is not None]

                unread_cnt = sum(1 for m in parsed_messages if not m.get("read", True))
                lat_ms = (datetime.now() - t_start).total_seconds() * 1000.0
                res = {
                    "count": len(parsed_messages),
                    "unread_count": unread_cnt if unread_cnt > 0 else len(parsed_messages),
                    "messages": parsed_messages,
                    "message": f"Retrieved {len(parsed_messages)} emails from Gmail."
                }
                gmail_cache.set(cache_key, res)
                return res

            except Exception as e:
                lat_ms = (datetime.now() - t_start).total_seconds() * 1000.0
                logger.error(f"gmail_request account=<redacted> provider=google error={e} latency_ms={lat_ms:.1f}")
                res = {
                    "count": 0,
                    "unread_count": 0,
                    "messages": [],
                    "error": str(e),
                    "message": "I can't access your email right now."
                }
                gmail_cache.set(cache_key, res)
                return res
        finally:
            with gmail_cache._lock:
                if is_fetcher:
                    gmail_cache._in_flight_results[cache_key] = res if 'res' in locals() else {}
                    event.set()
                    gmail_cache._in_flight.pop(cache_key, None)

    def read(self, message_id: Optional[str] = None, index: Optional[int] = None) -> Dict[str, Any]:
        token = self._get_valid_token_sync()
        if not token:
            return {"status": "not_found", "error": "Gmail is not connected.", "message": "I can't access your email right now."}

        headers = {"Authorization": f"Bearer {token}"}
        try:
            target_id = message_id
            if index is not None and not target_id:
                overview = self.search()
                msgs = overview.get("messages", [])
                if 1 <= index <= len(msgs):
                    target_id = msgs[index - 1]["id"]

            if not target_id:
                return {"status": "not_found", "message": "Email not found."}

            with httpx.Client(timeout=10.0) as client:
                msg_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{target_id}"
                m_resp = client.get(msg_url, headers=headers)
                if m_resp.status_code == 200:
                    m_data = m_resp.json()
                    headers_dict = {h["name"]: h["value"] for h in m_data.get("payload", {}).get("headers", [])}
                    return {
                        "status": "found",
                        "email": {
                            "id": target_id,
                            "sender": headers_dict.get("From", "Unknown"),
                            "subject": headers_dict.get("Subject", "No Subject"),
                            "snippet": m_data.get("snippet", ""),
                            "timestamp": headers_dict.get("Date", "")
                        }
                    }
            return {"status": "not_found", "message": "Email not found."}
        except Exception as e:
            logger.error("Error reading email from Gmail API: %s", e)
            return {"status": "error", "error": str(e), "message": "I can't access your email right now."}

    def get_unread_count(self) -> int:
        res = self.search("is:unread")
        return res.get("unread_count", 0)


def get_email_provider(user_id: str = "default_user") -> EmailProvider:
    """Factory: Returns authoritative GoogleGmailProvider."""
    return GoogleGmailProvider(user_id=user_id)

