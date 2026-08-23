from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class MessagingProvider(ABC):
    """Abstract provider interface for messaging services (Android SMS, WhatsApp, Telegram, etc.)."""

    @abstractmethod
    def search_messages(self, query: Optional[str] = None, sender: Optional[str] = None) -> Dict[str, Any]:
        """Search messages by text query or sender contact."""
        pass

    @abstractmethod
    def read_message(self, message_id: Optional[str] = None, index: Optional[int] = None) -> Dict[str, Any]:
        """Read a specific message content."""
        pass

    @abstractmethod
    def send_message(self, recipient: str, text: str, idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        """Send a message to a recipient contact/phone."""
        pass


class MockMessagingProvider(MessagingProvider):
    """Deterministic development messaging provider for laptop simulation."""

    def __init__(self):
        self._mock_messages = [
            {
                "id": "sms_001",
                "sender": "Rahul",
                "phone": "+919876543210",
                "text": "Hey, let's meet at 5 PM at the lab.",
                "timestamp": "08:00 AM",
                "read": True
            },
            {
                "id": "sms_002",
                "sender": "Sneha",
                "phone": "+919876543211",
                "text": "Sent the presentation slides for today's review.",
                "timestamp": "Yesterday",
                "read": True
            }
        ]

    def search_messages(self, query: Optional[str] = None, sender: Optional[str] = None) -> Dict[str, Any]:
        results = self._mock_messages
        if sender:
            results = [m for m in results if sender.lower() in m["sender"].lower()]
        if query:
            results = [m for m in results if query.lower() in m["text"].lower()]
        return {
            "count": len(results),
            "messages": results
        }

    def read_message(self, message_id: Optional[str] = None, index: Optional[int] = None) -> Dict[str, Any]:
        if index is not None and 1 <= index <= len(self._mock_messages):
            return {"status": "found", "message": self._mock_messages[index - 1]}
        if message_id:
            for m in self._mock_messages:
                if m["id"] == message_id:
                    return {"status": "found", "message": m}
        return {"status": "not_found", "message": "Message not found"}

    def send_message(self, recipient: str, text: str, idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        new_msg = {
            "id": f"sms_{len(self._mock_messages) + 1:03d}",
            "sender": "Me",
            "recipient": recipient,
            "text": text,
            "timestamp": "Just now",
            "read": True
        }
        self._mock_messages.append(new_msg)
        return {
            "status": "sent",
            "message_id": new_msg["id"],
            "recipient": recipient,
            "text": text
        }
