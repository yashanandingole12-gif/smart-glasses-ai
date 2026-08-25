from typing import List, Dict, Any, Optional
from backend.app.services.providers.email_provider import get_email_provider

def gmail_search(query: Optional[str] = None) -> Dict[str, Any]:
    """
    Search emails in inbox using configured Email Provider (Real Gmail or Laptop Simulator).
    """
    provider = get_email_provider()
    return provider.search(query)

def gmail_read(message_id: Optional[str] = None, index: Optional[int] = None) -> Dict[str, Any]:
    """
    Read full content of a specific email by id or index.
    """
    provider = get_email_provider()
    return provider.read(message_id=message_id, index=index)
