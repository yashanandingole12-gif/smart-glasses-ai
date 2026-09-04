import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from backend.app.services.entity_resolver import entity_resolver, ResolutionStatus

logger = logging.getLogger("SmartGlasses.MessagingProvider")

class MessagingProvider(ABC):
    """Abstract provider interface for messaging services (Android SMS, simulation, etc.)."""

    @abstractmethod
    def get_recent_messages(self, limit: int = 5) -> Dict[str, Any]:
        """Retrieve recent SMS messages (bounded by limit)."""
        pass

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
        """Send an SMS message to a recipient phone number."""
        pass


class MockMessagingProvider(MessagingProvider):
    """Deterministic development messaging provider for laptop simulation and CI."""

    def __init__(self, custom_messages: Optional[List[Dict[str, Any]]] = None):
        if custom_messages is not None:
            self._mock_messages = custom_messages
        else:
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
                },
                {
                    "id": "sms_003",
                    "sender": "Amit",
                    "phone": "+919876543212",
                    "text": "Are you joining the smart glasses demo session?",
                    "timestamp": "Aug 28",
                    "read": False
                }
            ]

    def get_recent_messages(self, limit: int = 5) -> Dict[str, Any]:
        msgs = self._mock_messages[:limit]
        return {
            "count": len(msgs),
            "messages": msgs,
            "message": "Messages retrieved successfully." if msgs else "No messages found."
        }

    def search_messages(self, query: Optional[str] = None, sender: Optional[str] = None) -> Dict[str, Any]:
        results = list(self._mock_messages)
        if sender:
            # Check for direct exact match first
            direct_matches = [
                m for m in results
                if m.get("sender", "").lower() == sender.lower() or sender.lower() in m.get("sender", "").lower()
            ]
            if direct_matches:
                results = direct_matches
            else:
                # Fuzzy match contact name if no direct sender name matched
                res = entity_resolver.resolve_contact(sender)
                if res.status == ResolutionStatus.AMBIGUOUS:
                    return {
                        "count": 0,
                        "messages": [],
                        "ambiguous": True,
                        "clarification_prompt": res.clarification_prompt,
                        "message": res.clarification_prompt
                    }
                elif res.status == ResolutionStatus.RESOLVED and res.contact:
                    target_phone = res.contact.phone
                    target_name = res.contact.name.lower()
                    results = [
                        m for m in results
                        if m.get("phone") == target_phone or sender.lower() in m.get("sender", "").lower() or target_name in m.get("sender", "").lower()
                    ]
                else:
                    results = [m for m in results if sender.lower() in m.get("sender", "").lower()]


        if query:
            q = query.lower()
            results = [m for m in results if q in m.get("text", "").lower()]

        return {
            "count": len(results),
            "messages": results[:5],
            "message": "Messages retrieved successfully." if results else "No matching messages found."
        }

    def read_message(self, message_id: Optional[str] = None, index: Optional[int] = None) -> Dict[str, Any]:
        if index is not None and 1 <= index <= len(self._mock_messages):
            return {"status": "found", "message": self._mock_messages[index - 1]}
        if message_id:
            for m in self._mock_messages:
                if m["id"] == message_id:
                    return {"status": "found", "message": m}
        return {"status": "not_found", "message": "Message not found."}

    def send_message(self, recipient: str, text: str, idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        # Sensitive data redaction for logging
        logger.info(f"Executing SMS send to recipient '{recipient}' (len={len(text)})")
        new_msg = {
            "id": f"sms_{len(self._mock_messages) + 1:03d}",
            "sender": "Me",
            "recipient": recipient,
            "text": text[:160],  # Bounded SMS length
            "timestamp": "Just now",
            "read": True
        }
        self._mock_messages.insert(0, new_msg)
        return {
            "status": "sent",
            "message_id": new_msg["id"],
            "recipient": recipient,
            "text": text[:160]
        }


def get_messaging_provider() -> MessagingProvider:
    return MockMessagingProvider()

messaging_provider = get_messaging_provider()
