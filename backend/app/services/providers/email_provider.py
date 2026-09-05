import logging
import httpx
import asyncio
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


class GoogleGmailProvider(EmailProvider):
    """
    Real Google Gmail API provider connecting via backend OAuth 2.0 token.
    Uses read-only scope (https://www.googleapis.com/auth/gmail.readonly).
    Never exposes raw tokens to client or LLM.
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
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(asyncio.run, token_service.get_valid_token(self.user_id)).result()
            return asyncio.run(token_service.get_valid_token(self.user_id))
        except Exception:
            return None

    def search(self, query: Optional[str] = None) -> Dict[str, Any]:
        t_start = datetime.now()
        token = self._get_valid_token_sync()
        if not token:
            logger.info(f"gmail_request account=<redacted> provider=google status=unauthenticated")
            return {
                "count": 0,
                "unread_count": 0,
                "messages": [],
                "error": "Gmail is not connected.",
                "message": "I can't access your email right now."
            }

        q_param = query if query else "is:unread"
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            with httpx.Client(timeout=10.0) as client:
                # 1. List messages
                list_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
                resp = client.get(list_url, headers=headers, params={"q": q_param, "maxResults": 5})
                if resp.status_code == 401:
                    logger.warning("Gmail API returned 401 Unauthorized; disconnecting expired token.")
                    try:
                        from backend.app.services.token_service import token_service
                        try:
                            loop = asyncio.get_running_loop()
                        except RuntimeError:
                            loop = None
                        if loop and loop.is_running():
                            import concurrent.futures
                            with concurrent.futures.ThreadPoolExecutor() as pool:
                                pool.submit(asyncio.run, token_service.disconnect(self.user_id)).result()
                        else:
                            asyncio.run(token_service.disconnect(self.user_id))
                    except Exception:
                        pass
                    return {
                        "count": 0,
                        "unread_count": 0,
                        "messages": [],
                        "error": "Gmail authentication expired.",
                        "message": "I can't access your email right now."
                    }
                elif resp.status_code != 200:
                    logger.warning("Gmail API list returned %d: %s", resp.status_code, resp.text)
                    return {
                        "count": 0,
                        "unread_count": 0,
                        "messages": [],
                        "error": f"Gmail API error (HTTP {resp.status_code})",
                        "message": "I can't access your email right now."
                    }

                data = resp.json()
                msg_ids = [m["id"] for m in data.get("messages", [])]
                if not msg_ids:
                    lat_ms = (datetime.now() - t_start).total_seconds() * 1000.0
                    logger.info(f"gmail_request account=<redacted> provider=google result_count=0 latency_ms={lat_ms:.1f}")
                    return {
                        "count": 0,
                        "unread_count": 0,
                        "messages": [],
                        "status": "inbox_zero",
                        "message": "You have no unread emails."
                    }

                # 2. Fetch metadata for each message
                parsed_messages = []
                for mid in msg_ids:
                    msg_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{mid}"
                    m_resp = client.get(
                        msg_url,
                        headers=headers,
                        params={"format": "metadata", "metadataHeaders": ["From", "Subject", "Date"]}
                    )
                    if m_resp.status_code == 200:
                        m_data = m_resp.json()
                        headers_dict = {h["name"]: h["value"] for h in m_data.get("payload", {}).get("headers", [])}
                        parsed_messages.append({
                            "id": mid,
                            "sender": headers_dict.get("From", "Unknown Sender"),
                            "subject": headers_dict.get("Subject", "No Subject"),
                            "snippet": m_data.get("snippet", ""),
                            "timestamp": headers_dict.get("Date", "Recent"),
                            "read": "UNREAD" not in m_data.get("labelIds", [])
                        })

                unread_cnt = sum(1 for m in parsed_messages if not m.get("read", True))
                lat_ms = (datetime.now() - t_start).total_seconds() * 1000.0
                logger.info(f"gmail_request account=<redacted> provider=google result_count={len(parsed_messages)} latency_ms={lat_ms:.1f}")
                return {
                    "count": len(parsed_messages),
                    "unread_count": unread_cnt if unread_cnt > 0 else len(parsed_messages),
                    "messages": parsed_messages,
                    "message": f"Retrieved {len(parsed_messages)} emails from Gmail."
                }
        except Exception as e:
            lat_ms = (datetime.now() - t_start).total_seconds() * 1000.0
            logger.error(f"gmail_request account=<redacted> provider=google error={e} latency_ms={lat_ms:.1f}")
            return {
                "count": 0,
                "unread_count": 0,
                "messages": [],
                "error": str(e),
                "message": "I can't access your email right now."
            }

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

