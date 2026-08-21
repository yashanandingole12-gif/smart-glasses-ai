from typing import List, Dict, Any, Optional

_MOCK_EMAILS = [
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

def gmail_search(query: Optional[str] = None) -> Dict[str, Any]:
    """
    Search emails in inbox.
    """
    results = _MOCK_EMAILS
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

def gmail_read(message_id: Optional[str] = None, index: Optional[int] = None) -> Dict[str, Any]:
    """
    Read full content of a specific email by id or index.
    """
    if index is not None and 1 <= index <= len(_MOCK_EMAILS):
        return {"status": "found", "email": _MOCK_EMAILS[index - 1]}
    if message_id:
        for m in _MOCK_EMAILS:
            if m["id"] == message_id:
                return {"status": "found", "email": m}
    return {"status": "not_found", "message": "Email not found"}
