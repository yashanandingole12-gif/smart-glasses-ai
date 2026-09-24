"""
Google Workspace Agent
Authoritative ecosystem coordinator for Gmail, Google Calendar, Google Docs, Google Drive,
and Google Contacts. Supports all-accessible file sharing, PDF search, and contact management.
"""

import logging
from typing import Dict, Any, List, Optional

try:
    from backend.app.tools.calendar_tools import calendar_get_events, calendar_find_free_time, calendar_create_event
    from backend.app.tools.gmail_tools import gmail_search, gmail_read
    from backend.app.services.contact_vault import contact_vault
    from backend.app.services.google_contacts_service import google_contacts_service
    from backend.app.services.google_docs_drive_service import google_docs_drive_service
except ImportError:
    from app.tools.calendar_tools import calendar_get_events, calendar_find_free_time, calendar_create_event
    from app.tools.gmail_tools import gmail_search, gmail_read
    from app.services.contact_vault import contact_vault
    from app.services.google_contacts_service import google_contacts_service
    from app.services.google_docs_drive_service import google_docs_drive_service

logger = logging.getLogger("eva.agents.workspace")

class WorkspaceAgent:
    def __init__(self):
        logger.info("WorkspaceAgent initialized with full Google Docs, Drive, and Contacts handlers.")

    async def get_overview(self, user_id: str = "default_user") -> Dict[str, Any]:
        """
        Produce a unified overview across Calendar, Gmail, Drive Docs, and Contacts.
        """
        logger.info("WorkspaceAgent generating unified workspace overview")
        calendar_events = []
        try:
            cal_res = calendar_get_events(time_min="today", user_id=user_id)
            if isinstance(cal_res, dict) and "events" in cal_res:
                calendar_events = cal_res["events"]
            elif isinstance(cal_res, list):
                calendar_events = cal_res
        except Exception as e:
            logger.warning(f"Calendar query notice: {e}")

        emails = []
        try:
            mail_res = gmail_search(query="", user_id=user_id)
            if isinstance(mail_res, dict) and "messages" in mail_res:
                emails = mail_res["messages"]
            elif isinstance(mail_res, list):
                emails = mail_res
        except Exception as e:
            logger.warning(f"Gmail query notice: {e}")

        contacts = contact_vault.list_contacts(user_id=user_id)
        drive_res = await google_docs_drive_service.search_files(limit=5, user_id=user_id)

        return {
            "status": "SUCCESS",
            "calendar_events_count": len(calendar_events),
            "upcoming_events": calendar_events[:3],
            "recent_emails_count": len(emails),
            "recent_emails": emails[:3],
            "total_contacts": len(contacts),
            "total_drive_files": drive_res.get("count", 0),
            "recent_files": drive_res.get("files", [])[:3]
        }

    async def get_schedule_for_date(self, target_date: str = "today", user_id: str = "default_user") -> Dict[str, Any]:
        logger.info(f"Fetching schedule for: {target_date}")
        try:
            events = calendar_get_events(time_min=target_date, user_id=user_id)
            return {"status": "SUCCESS", "target_date": target_date, "events": events}
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}

    async def search_drive_documents(self, query: str = "", mime_type: Optional[str] = None, user_id: str = "default_user") -> Dict[str, Any]:
        """Search Google Drive and Local Cloud for Docs, PDFs, and files."""
        logger.info(f"Searching Drive documents for: '{query}'")
        res = await google_docs_drive_service.search_files(query=query, mime_type=mime_type, user_id=user_id)
        return {
            "status": "SUCCESS",
            "query": query,
            "count": res.get("count", 0),
            "documents": res.get("files", [])
        }

    async def create_google_doc(self, title: str, content: str = "", share_accessible: bool = True, user_id: str = "default_user") -> Dict[str, Any]:
        """Create a Google Doc with text content and all-accessible sharing."""
        logger.info(f"Creating Google Doc '{title}' (accessible={share_accessible})")
        return await google_docs_drive_service.create_google_doc(
            title=title,
            content=content,
            share_accessible=share_accessible,
            user_id=user_id
        )

    async def share_file_or_doc(
        self,
        file_id: str,
        role: str = "reader",
        make_public: bool = True,
        recipient_email: Optional[str] = None,
        recipient_name: Optional[str] = None,
        user_id: str = "default_user"
    ) -> Dict[str, Any]:
        """Share any file/doc with all-accessible link or directly with a contact."""
        logger.info(f"Sharing file '{file_id}' (recipient={recipient_email or recipient_name}, public={make_public})")
        return await google_docs_drive_service.share_file(
            file_id=file_id,
            role=role,
            make_public=make_public,
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            user_id=user_id
        )

    async def sync_contacts(self, user_id: str = "default_user") -> Dict[str, Any]:
        """Fetch and sync Google Contacts into local vault."""
        return await google_contacts_service.fetch_and_sync_contacts(user_id=user_id)

    async def search_contacts(self, query: str = "", user_id: str = "default_user") -> Dict[str, Any]:
        """Search contacts by name, alias, or email."""
        contacts = contact_vault.search_contacts(query=query, user_id=user_id)
        return {
            "status": "SUCCESS",
            "query": query,
            "count": len(contacts),
            "contacts": [c.model_dump() for c in contacts]
        }

workspace_agent = WorkspaceAgent()
