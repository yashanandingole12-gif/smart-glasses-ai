from typing import List, Dict, Any, Optional
from backend.app.services.providers.email_provider import get_email_provider
from backend.app.services.entity_resolver import entity_resolver, ResolutionStatus

def gmail_search(query: Optional[str] = None, user_id: str = "default_user") -> Dict[str, Any]:
    """
    Search emails in inbox using configured Email Provider (Real Gmail or Laptop Simulator).
    """
    provider = get_email_provider(user_id=user_id)
    return provider.search(query)

def gmail_read(message_id: Optional[str] = None, index: Optional[int] = None, user_id: str = "default_user") -> Dict[str, Any]:
    """
    Read full content of a specific email by id or index (Stage 2 fetch).
    """
    provider = get_email_provider(user_id=user_id)
    return provider.read(message_id=message_id, index=index)

def gmail_send_message(recipient: str, subject: str, body: str, user_id: str = "default_user") -> Dict[str, Any]:
    """
    Send an email message via Gmail.
    HIGH-RISK WRITE OPERATION: Requires explicit 2-step user confirmation before execution.
    """
    # 1. Resolve contact email if name given
    target_email = recipient
    if "@" not in recipient:
        res = entity_resolver.resolve_contact(recipient)
        if res.status == ResolutionStatus.RESOLVED and res.contact and res.contact.email:
            target_email = res.contact.email
        elif res.status == ResolutionStatus.AMBIGUOUS:
            return {
                "status": "ambiguous",
                "message": res.clarification_prompt,
                "clarification_prompt": res.clarification_prompt
            }

    provider = get_email_provider(user_id=user_id)
    return provider.send_message(recipient=target_email, subject=subject, body=body)

def gmail_reply_message(message_id: str, body: str, user_id: str = "default_user") -> Dict[str, Any]:
    """
    Reply to an existing email thread via Gmail.
    HIGH-RISK WRITE OPERATION: Requires explicit 2-step user confirmation before execution.
    """
    provider = get_email_provider(user_id=user_id)
    return provider.reply_message(message_id=message_id, body=body)
