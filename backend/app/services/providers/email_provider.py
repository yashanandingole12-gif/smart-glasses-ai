import base64
import logging
import httpx
import asyncio
import threading
import time
import re
import concurrent.futures
from email.mime.text import MIMEText
from datetime import datetime
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger("SmartGlasses.EmailProvider")

def resolve_email_search_query(raw_query: Optional[str]) -> str:
    """
    Intelligently maps natural language email queries and entity mentions
    to optimized Gmail search queries.
    """
    if not raw_query or not raw_query.strip():
        return "is:unread"

    q = raw_query.strip().lower()

    # If it's already an explicit Gmail query, keep it
    if any(prefix in q for prefix in ["from:", "to:", "subject:", "is:", "label:", "has:", "after:", "before:"]):
        return raw_query.strip()

    # Clean conversational filler
    q_clean = re.sub(r"^(?:check|find|read|search|show|get|see)\s+(?:my\s+)?(?:latest\s+|new\s+|recent\s+)?", "", q)
    q_clean = re.sub(r"\s*(?:email|emails|mail|mails|message|messages)$", "", q_clean).strip()

    # Common entity mappings
    entity_domains = {
        "linkedin": "(linkedin.com OR linkedin)",
        "github": "(github.com OR github)",
        "amazon": "(amazon.com OR amazon)",
        "google": "(google.com OR google)",
        "twitter": "(twitter.com OR x.com)",
        "facebook": "(facebook.com OR meta.com)",
        "netflix": "(netflix.com)",
        "apple": "(apple.com)",
        "microsoft": "(microsoft.com)",
        "uber": "(uber.com)",
        "swiggy": "(swiggy.in OR swiggy)",
        "zomato": "(zomato.com OR zomato)",
        "college": "(college OR university OR .edu OR admin)",
        "university": "(university OR .edu OR college)",
        "professor": "(professor OR prof OR sir OR dept)",
    }

    for entity_key, domain_query in entity_domains.items():
        if entity_key in q_clean or entity_key in q:
            return f"from:{domain_query} OR subject:{entity_key}"

    if not q_clean or q_clean in ["unread", "latest", "new", "inbox"]:
        return "is:unread"

    # Default to sender or subject search
    return f"from:({q_clean}) OR subject:({q_clean}) OR {q_clean}"


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

    @abstractmethod
    def check_write_permission(self) -> Tuple[bool, str]:
        """Check if the current OAuth authorization includes email sending permissions."""
        pass

    @abstractmethod
    def send_message(self, recipient: str, subject: str, body: str) -> Dict[str, Any]:
        """Send a new email message to a recipient."""
        pass

    @abstractmethod
    def reply_message(self, message_id: str, body: str) -> Dict[str, Any]:
        """Reply to an existing email thread."""
        pass


class LaptopEmailProvider(EmailProvider):
    """Deterministic development email provider for laptop simulation."""

    def __init__(self):
        self._mock_emails = [
            {
                "id": "msg_001",
                "thread_id": "thread_001",
                "sender": "college.admin@university.edu",
                "subject": "Class Schedule Update: Room Change for ML Lecture",
                "snippet": "Please note today's Machine Learning lecture will be held in Room 302.",
                "body": "Dear Students, please note that today's Machine Learning lecture will be held in Room 302 at 10:30 AM instead of Lab 4.",
                "timestamp": "07:45 AM",
                "read": False
            },
            {
                "id": "msg_002",
                "thread_id": "thread_002",
                "sender": "rahul.sharma@techcorp.com",
                "subject": "Review of Smart Glasses Prototype Architecture",
                "snippet": "Hey, reviewed the ESP32 and BLE specs. Looks great, let's sync at 3 PM.",
                "body": "Hey team, I reviewed the ESP32 firmware and BLE transmission specs. Everything looks clean and latency is within budget. Let's sync at 3 PM.",
                "timestamp": "Yesterday",
                "read": True
            },
            {
                "id": "msg_003",
                "thread_id": "thread_003",
                "sender": "notifications@linkedin.com",
                "subject": "You have 3 new job recommendations and 2 connection requests",
                "snippet": "Check out new roles matching your profile: Senior Embedded AI Engineer.",
                "body": "Hi Yash, we found 3 new job recommendations matching your profile for Senior Embedded AI Engineer at top tech firms in India.",
                "timestamp": "Aug 20",
                "read": False
            }
        ]

    def search(self, query: Optional[str] = None) -> Dict[str, Any]:
        results = self._mock_emails
        if query:
            q = query.lower()
            if "linkedin" in q:
                results = [m for m in results if "linkedin" in m["sender"].lower() or "linkedin" in m["subject"].lower()]
            elif "college" in q or "admin" in q:
                results = [m for m in results if "college" in m["sender"].lower() or "admin" in m["sender"].lower()]
            elif "rahul" in q:
                results = [m for m in results if "rahul" in m["sender"].lower() or "rahul" in m["subject"].lower()]
            else:
                results = [
                    m for m in results
                    if q in m["subject"].lower() or q in m["sender"].lower() or q in m["snippet"].lower()
                ]

        entity_label = "matching" if query else "inbox"
        msg = f"Retrieved {len(results)} {entity_label} emails." if results else f"I couldn't find any emails matching '{query or 'your inbox'}'."

        return {
            "count": len(results),
            "unread_count": sum(1 for m in results if not m.get("read", True)),
            "messages": results,
            "message": msg
        }

    def read(self, message_id: Optional[str] = None, index: Optional[int] = None) -> Dict[str, Any]:
        if index is not None and 1 <= index <= len(self._mock_emails):
            target = self._mock_emails[index - 1]
            return {"status": "found", "email": target, "message": f"Email from {target['sender']}: {target['body']}"}
        if message_id:
            for m in self._mock_emails:
                if m["id"] == message_id:
                    return {"status": "found", "email": m, "message": f"Email from {m['sender']}: {m['body']}"}
        return {"status": "not_found", "message": "Email not found."}

    def get_unread_count(self) -> int:
        return sum(1 for m in self._mock_emails if not m.get("read", True))

    def check_write_permission(self) -> Tuple[bool, str]:
        return (True, "Mock email write access active.")

    def send_message(self, recipient: str, subject: str, body: str) -> Dict[str, Any]:
        new_msg = {
            "id": f"msg_{len(self._mock_emails) + 1:03d}",
            "thread_id": f"thread_{len(self._mock_emails) + 1:03d}",
            "sender": "me@smartglasses.ai",
            "recipient": recipient,
            "subject": subject,
            "snippet": body[:80],
            "body": body,
            "timestamp": "Just now",
            "read": True
        }
        self._mock_emails.insert(0, new_msg)
        return {
            "status": "sent",
            "message_id": new_msg["id"],
            "recipient": recipient,
            "subject": subject,
            "message": f"Email successfully sent to {recipient}."
        }

    def reply_message(self, message_id: str, body: str) -> Dict[str, Any]:
        target = next((m for m in self._mock_emails if m["id"] == message_id), self._mock_emails[0])
        new_msg = {
            "id": f"msg_{len(self._mock_emails) + 1:03d}",
            "thread_id": target.get("thread_id", "thread_default"),
            "sender": "me@smartglasses.ai",
            "recipient": target["sender"],
            "subject": f"Re: {target['subject']}",
            "snippet": body[:80],
            "body": body,
            "timestamp": "Just now",
            "read": True
        }
        self._mock_emails.insert(0, new_msg)
        return {
            "status": "sent",
            "message_id": new_msg["id"],
            "recipient": target["sender"],
            "subject": new_msg["subject"],
            "message": f"Reply successfully sent to {target['sender']}."
        }


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

    def check_write_permission(self) -> Tuple[bool, str]:
        from backend.app.services.token_service import token_service
        status = token_service.get_status(self.user_id)
        if not status.get("connected") or status.get("is_expired"):
            return (False, "Gmail is not connected. Please connect your Google account in settings.")

        scopes = status.get("scopes", [])
        write_scopes = [
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/gmail.modify",
            "https://mail.google.com/"
        ]
        has_write = any(s in scopes for s in write_scopes)
        if not has_write:
            return (
                False,
                "Your Gmail connection is read-only. I need permission to send email. "
                "Please re-authorize with sending permissions via http://localhost:8001/api/v1/auth/google."
            )
        return (True, "Write permissions granted.")

    def search(self, query: Optional[str] = None) -> Dict[str, Any]:
        t_start = datetime.now()
        resolved_q = resolve_email_search_query(query)
        cache_key = f"{self.user_id}:{resolved_q}"

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
                logger.info("gmail_request account=<redacted> provider=google status=unauthenticated")
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
                resp = _gmail_client.get(list_url, headers=headers, params={"q": resolved_q, "maxResults": 5})
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
                        "Action required: Enable 'Gmail API' in Google Cloud Console and re-authorize."
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
                    search_term = query or "inbox"
                    res = {
                        "count": 0,
                        "unread_count": 0,
                        "messages": [],
                        "status": "inbox_zero",
                        "message": f"I couldn't find any emails matching '{search_term}'." if query else "You have no unread emails."
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
                                "thread_id": m_data.get("threadId", mid),
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
                
                first_sender = parsed_messages[0]["sender"] if parsed_messages else "Unknown"
                first_sender_name = first_sender.split("<")[0].strip() if "<" in first_sender else first_sender
                
                if query and "linkedin" in query.lower():
                    speech_msg = f"You have {len(parsed_messages)} emails from LinkedIn. The latest says: {parsed_messages[0]['snippet']}"
                elif len(parsed_messages) == 1:
                    speech_msg = f"You have 1 email from {first_sender_name} with subject '{parsed_messages[0]['subject']}'."
                else:
                    speech_msg = f"You have {len(parsed_messages)} emails. Latest from {first_sender_name}: '{parsed_messages[0]['subject']}'."

                res = {
                    "count": len(parsed_messages),
                    "unread_count": unread_cnt if unread_cnt > 0 else len(parsed_messages),
                    "messages": parsed_messages,
                    "message": speech_msg
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
        """Stage 2: Fetch and decode full message body."""
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
                m_resp = client.get(msg_url, headers=headers, params={"format": "full"})
                if m_resp.status_code == 200:
                    m_data = m_resp.json()
                    headers_dict = {h["name"]: h["value"] for h in m_data.get("payload", {}).get("headers", [])}
                    
                    # Extract plain text body parts
                    body_text = self._extract_body(m_data.get("payload", {}))
                    if not body_text:
                        body_text = m_data.get("snippet", "")

                    # Sanitize for wearable speech output (max 300 chars)
                    clean_body = re.sub(r"https?://\S+", "", body_text)
                    clean_body = re.sub(r"\s+", " ", clean_body).strip()
                    if len(clean_body) > 280:
                        clean_body = clean_body[:280] + "..."

                    sender = headers_dict.get("From", "Unknown")
                    sender_name = sender.split("<")[0].strip() if "<" in sender else sender
                    subject = headers_dict.get("Subject", "No Subject")

                    speech_text = f"Email from {sender_name}: '{subject}'. {clean_body}"

                    return {
                        "status": "found",
                        "email": {
                            "id": target_id,
                            "thread_id": m_data.get("threadId", target_id),
                            "sender": sender,
                            "subject": subject,
                            "snippet": m_data.get("snippet", ""),
                            "body": clean_body,
                            "timestamp": headers_dict.get("Date", "")
                        },
                        "message": speech_text
                    }
            return {"status": "not_found", "message": "Email not found."}
        except Exception as e:
            logger.error("Error reading email from Gmail API: %s", e)
            return {"status": "error", "error": str(e), "message": "I can't access your email right now."}

    def _extract_body(self, payload: Dict[str, Any]) -> str:
        """Recursively decode text/plain body from Gmail payload parts."""
        mime_type = payload.get("mimeType", "")
        body_data = payload.get("body", {}).get("data", "")

        if mime_type == "text/plain" and body_data:
            try:
                return base64.urlsafe_b64decode(body_data).decode("utf-8", errors="ignore")
            except Exception:
                pass

        parts = payload.get("parts", [])
        for part in parts:
            extracted = self._extract_body(part)
            if extracted:
                return extracted

        # Fallback to HTML if text/plain not found
        if body_data:
            try:
                raw_html = base64.urlsafe_b64decode(body_data).decode("utf-8", errors="ignore")
                return re.sub(r"<[^>]+>", " ", raw_html)
            except Exception:
                pass
        return ""

    def get_unread_count(self) -> int:
        res = self.search("is:unread")
        return res.get("unread_count", 0)

    def send_message(self, recipient: str, subject: str, body: str) -> Dict[str, Any]:
        """Send a real email using Gmail API (Requires gmail.send or gmail.modify scope)."""
        has_perm, perm_msg = self.check_write_permission()
        if not has_perm:
            return {"status": "permission_denied", "error": perm_msg, "message": perm_msg}

        token = self._get_valid_token_sync()
        if not token:
            return {"status": "unauthenticated", "error": "Gmail is not connected.", "message": "I can't send email right now."}

        # Build RFC 2822 MIME message
        mime_msg = MIMEText(body, "plain", "utf-8")
        mime_msg["to"] = recipient
        mime_msg["subject"] = subject

        raw_b64 = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode("utf-8")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
                resp = client.post(url, headers=headers, json={"raw": raw_b64})
                if resp.status_code in [200, 201]:
                    data = resp.json()
                    gmail_cache.invalidate(self.user_id)
                    logger.info("Successfully sent email to %s (id=%s)", recipient, data.get("id"))
                    return {
                        "status": "sent",
                        "message_id": data.get("id"),
                        "thread_id": data.get("threadId"),
                        "recipient": recipient,
                        "subject": subject,
                        "message": f"Email successfully sent to {recipient}."
                    }
                elif resp.status_code == 403:
                    return {
                        "status": "permission_denied",
                        "error": "Google returned 403 Forbidden. The granted scopes do not permit sending email.",
                        "message": "Your Gmail connection is read-only. I need permission to send email. Please authorize email sending in settings."
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"Failed to send email (HTTP {resp.status_code}): {resp.text}",
                        "message": "Could not send email via Gmail."
                    }
        except Exception as e:
            logger.error("Exception during Gmail send: %s", e)
            return {"status": "error", "error": str(e), "message": "Could not send email right now."}

    def reply_message(self, message_id: str, body: str) -> Dict[str, Any]:
        """Reply to an existing message thread in Gmail."""
        has_perm, perm_msg = self.check_write_permission()
        if not has_perm:
            return {"status": "permission_denied", "error": perm_msg, "message": perm_msg}

        token = self._get_valid_token_sync()
        if not token:
            return {"status": "unauthenticated", "error": "Gmail is not connected.", "message": "I can't send email right now."}

        headers = {"Authorization": f"Bearer {token}"}

        # 1. Fetch original message headers
        try:
            with httpx.Client(timeout=10.0) as client:
                get_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}"
                m_resp = client.get(get_url, headers=headers, params={"format": "metadata", "metadataHeaders": ["From", "Subject", "Message-ID"]})
                if m_resp.status_code != 200:
                    return {"status": "not_found", "message": "Original email thread not found."}

                m_data = m_resp.json()
                thread_id = m_data.get("threadId", message_id)
                headers_dict = {h["name"]: h["value"] for h in m_data.get("payload", {}).get("headers", [])}
                original_from = headers_dict.get("From", "")
                original_subject = headers_dict.get("Subject", "Message")
                orig_msg_id = headers_dict.get("Message-ID", "")

                reply_subject = original_subject if original_subject.startswith("Re:") else f"Re: {original_subject}"

                # 2. Build MIME reply
                mime_msg = MIMEText(body, "plain", "utf-8")
                mime_msg["to"] = original_from
                mime_msg["subject"] = reply_subject
                if orig_msg_id:
                    mime_msg["In-Reply-To"] = orig_msg_id
                    mime_msg["References"] = orig_msg_id

                raw_b64 = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode("utf-8")

                send_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
                send_resp = client.post(send_url, headers=headers, json={"raw": raw_b64, "threadId": thread_id})
                if send_resp.status_code in [200, 201]:
                    data = send_resp.json()
                    gmail_cache.invalidate(self.user_id)
                    return {
                        "status": "sent",
                        "message_id": data.get("id"),
                        "thread_id": data.get("threadId"),
                        "recipient": original_from,
                        "subject": reply_subject,
                        "message": f"Reply successfully sent to {original_from}."
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"Failed to send reply (HTTP {send_resp.status_code})",
                        "message": "Could not send reply via Gmail."
                    }
        except Exception as e:
            logger.error("Exception during Gmail reply: %s", e)
            return {"status": "error", "error": str(e), "message": "Could not send reply right now."}


def get_email_provider(user_id: str = "default_user") -> EmailProvider:
    """Factory: Returns authoritative GoogleGmailProvider."""
    return GoogleGmailProvider(user_id=user_id)

email_provider = get_email_provider()
