from typing import Dict, Any, Optional
from backend.app.services.providers.messaging_provider import get_messaging_provider
from backend.app.services.entity_resolver import entity_resolver, ResolutionStatus

def sms_read_recent(limit: int = 5) -> Dict[str, Any]:
    """
    Retrieve recent SMS messages received on the user's phone.
    """
    provider = get_messaging_provider()
    return provider.get_recent_messages(limit=min(limit, 5))

def sms_search(query: Optional[str] = None, sender: Optional[str] = None) -> Dict[str, Any]:
    """
    Search SMS messages by sender contact name or message text content.
    """
    provider = get_messaging_provider()
    return provider.search_messages(query=query, sender=sender)

def sms_send_message(recipient: str, text: str) -> Dict[str, Any]:
    """
    Send an SMS message to a recipient.
    HIGH-RISK OPERATION: Requires explicit 2-step user confirmation before execution.
    """
    # 1. Resolve contact
    res = entity_resolver.resolve_contact(recipient)
    if res.status == ResolutionStatus.AMBIGUOUS:
        return {
            "status": "ambiguous",
            "message": res.clarification_prompt,
            "clarification_prompt": res.clarification_prompt
        }
    elif res.status == ResolutionStatus.NOT_FOUND:
        target_recipient = recipient
    else:
        target_recipient = res.contact.phone if res.contact else recipient

    # 2. Execute via messaging provider
    provider = get_messaging_provider()
    return provider.send_message(recipient=target_recipient, text=text)
