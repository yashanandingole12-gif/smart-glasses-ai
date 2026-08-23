from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

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
