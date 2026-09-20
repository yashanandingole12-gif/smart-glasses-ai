"""
Email Agent
Dedicated agent for Gmail reading, thread search by sender or topic, summarization,
draft generation, and safe sending with confirmation tokens.
"""

import logging
from typing import Dict, Any, List, Optional
from backend.app.tools.gmail_tools import gmail_search, gmail_read, gmail_send_message

logger = logging.getLogger("eva.agents.email")

class EmailAgent:
    def __init__(self):
        logger.info("EmailAgent initialized.")

    async def check_inbox(self, max_results: int = 5, user_id: str = "default_user") -> Dict[str, Any]:
        logger.info("EmailAgent reading recent inbox emails")
        try:
            res = gmail_search(query="", user_id=user_id)
            return {"status": "SUCCESS", "data": res}
        except Exception as e:
            logger.error(f"Error checking inbox: {e}")
            return {"status": "ERROR", "message": str(e)}

    async def search_emails(self, query: str, user_id: str = "default_user") -> Dict[str, Any]:
        logger.info(f"EmailAgent searching emails for: '{query}'")
        try:
            res = gmail_search(query=query, user_id=user_id)
            return {"status": "SUCCESS", "query": query, "data": res}
        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            return {"status": "ERROR", "message": str(e)}

    async def prepare_email_draft(
        self,
        to: str,
        subject: str,
        body: str
    ) -> Dict[str, Any]:
        logger.info(f"Preparing email draft to {to} - '{subject}'")
        return {
            "status": "DRAFT_PREPARED",
            "to": to,
            "subject": subject,
            "body": body,
            "requires_confirmation": True,
            "prompt": f"I've drafted an email to {to} regarding '{subject}'. Would you like me to send it?"
        }
