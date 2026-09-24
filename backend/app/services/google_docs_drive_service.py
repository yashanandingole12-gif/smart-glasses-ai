"""
Google Docs, Google Drive, and Cloud File Sharing Service:
Dedicated service for creating Google Docs, searching Drive PDFs and files,
generating all-accessible public sharing links, and 1-click sharing with Google Contacts.
"""

import logging
import httpx
import os
from typing import Dict, Any, List, Optional

try:
    from backend.app.config import settings
    from backend.app.services.token_service import token_service
    from backend.app.services.storage_service import storage_service
    from backend.app.services.contact_vault import contact_vault
except ImportError:
    from app.config import settings
    from app.services.token_service import token_service
    from app.services.storage_service import storage_service
    from app.services.contact_vault import contact_vault

logger = logging.getLogger("SmartGlasses.GoogleDocsDriveService")

DRIVE_API_BASE = "https://www.googleapis.com/drive/v3"
DOCS_API_BASE = "https://docs.googleapis.com/v1"

class GoogleDocsDriveService:
    """
    Handles Google Docs creation, Drive file search, public link generation,
    and contact document sharing.
    """

    async def _get_auth_headers(self, user_id: str = "default_user") -> Optional[Dict[str, str]]:
        access_token = await token_service.get_valid_token(user_id)
        if not access_token:
            return None
        return {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    async def create_google_doc(
        self,
        title: str,
        content: str = "",
        share_accessible: bool = True,
        user_id: str = "default_user"
    ) -> Dict[str, Any]:
        """Create a new Google Document in user's Drive with optional initial text and accessible sharing."""
        headers = await self._get_auth_headers(user_id)
        if not headers:
            # Fallback to local storage document creation if Google account not connected
            local_res = storage_service.save_file(
                file_bytes=content.encode("utf-8"),
                filename=f"{title.replace(' ', '_')}.txt",
                content_type="text/plain",
                source="eva_docs_creator"
            )
            share_url = f"http://{settings.HOST}:{settings.PORT}/api/v1/files/{local_res['file_id']}/download"
            return {
                "success": True,
                "status": "CREATED_LOCAL",
                "document_id": local_res["file_id"],
                "title": title,
                "shareable_url": share_url,
                "message": f"Created document '{title}' in EVA Local Storage. (Google Account not connected)."
            }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # 1. Create empty document
                doc_payload = {"title": title}
                create_resp = await client.post(
                    f"{DOCS_API_BASE}/documents",
                    headers=headers,
                    json=doc_payload
                )

                if create_resp.status_code not in [200, 201]:
                    logger.warning(f"Google Docs API create error ({create_resp.status_code}): {create_resp.text}")
                    # Fallback to Drive files creation
                    drive_file_payload = {
                        "name": title,
                        "mimeType": "application/vnd.google-apps.document"
                    }
                    create_resp = await client.post(
                        f"{DRIVE_API_BASE}/files",
                        headers=headers,
                        json=drive_file_payload
                    )

                if create_resp.status_code in [200, 201]:
                    doc_data = create_resp.json()
                    doc_id = doc_data.get("documentId") or doc_data.get("id")
                    
                    # 2. Insert text content if provided
                    if content and doc_id:
                        insert_payload = {
                            "requests": [
                                {
                                    "insertText": {
                                        "location": {"index": 1},
                                        "text": content
                                    }
                                }
                            ]
                        }
                        await client.post(
                            f"{DOCS_API_BASE}/documents/{doc_id}:batchUpdate",
                            headers=headers,
                            json=insert_payload
                        )

                    # 3. Grant Accessible Link Permission (Anyone with link can view/edit)
                    shareable_url = f"https://docs.google.com/document/d/{doc_id}/edit"
                    if share_accessible and doc_id:
                        perm_res = await self.share_file(
                            file_id=doc_id,
                            role="reader",
                            make_public=True,
                            user_id=user_id
                        )
                        if perm_res.get("webViewLink"):
                            shareable_url = perm_res["webViewLink"]

                    return {
                        "success": True,
                        "status": "CREATED_GOOGLE_DOC",
                        "document_id": doc_id,
                        "title": title,
                        "shareable_url": shareable_url,
                        "message": f"Successfully created Google Doc '{title}' with accessible sharing permissions."
                    }
        except Exception as e:
            logger.error(f"Error creating Google Doc: {e}")

        # Local fallback
        local_res = storage_service.save_file(
            file_bytes=content.encode("utf-8"),
            filename=f"{title.replace(' ', '_')}.txt",
            content_type="text/plain",
            source="eva_docs_creator"
        )
        return {
            "success": True,
            "status": "CREATED_LOCAL_FALLBACK",
            "document_id": local_res["file_id"],
            "title": title,
            "shareable_url": f"http://{settings.HOST}:{settings.PORT}/api/v1/files/{local_res['file_id']}/download",
            "message": f"Created '{title}' in Local Cloud Storage."
        }

    async def search_files(
        self,
        query: str = "",
        mime_type: Optional[str] = None,
        limit: int = 10,
        user_id: str = "default_user"
    ) -> Dict[str, Any]:
        """Search Google Drive and Local Storage for Docs, PDFs, Spreadsheets, and files."""
        headers = await self._get_auth_headers(user_id)
        results = []

        # 1. Search Google Drive if connected
        if headers:
            try:
                q_parts = ["trashed = false"]
                if query:
                    clean_q = query.replace("'", "\\'")
                    q_parts.append(f"(name contains '{clean_q}' or fullText contains '{clean_q}')")
                if mime_type:
                    q_parts.append(f"mimeType = '{mime_type}'")

                params = {
                    "q": " and ".join(q_parts),
                    "pageSize": limit,
                    "fields": "files(id, name, mimeType, webViewLink, webContentLink, iconLink, modifiedTime, size, shared)"
                }
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.get(f"{DRIVE_API_BASE}/files", headers=headers, params=params)
                    if resp.status_code == 200:
                        files = resp.json().get("files", [])
                        for f in files:
                            results.append({
                                "source": "google_drive",
                                "file_id": f.get("id"),
                                "name": f.get("name"),
                                "mime_type": f.get("mimeType"),
                                "shareable_url": f.get("webViewLink") or f"https://drive.google.com/file/d/{f.get('id')}/view",
                                "modified_at": f.get("modifiedTime"),
                                "size_bytes": f.get("size", 0),
                                "shared": f.get("shared", False)
                            })
            except Exception as e:
                logger.warning(f"Google Drive search notice: {e}")

        # 2. Search local storage files (PDFs, docs, images uploaded in EVA)
        local_files = storage_service.list_files(limit=limit)
        for lf in local_files:
            fname = lf.get("filename", "")
            if not query or query.lower() in fname.lower():
                results.append({
                    "source": "local_eva_cloud",
                    "file_id": lf.get("file_id"),
                    "name": fname,
                    "mime_type": lf.get("content_type", "application/octet-stream"),
                    "shareable_url": f"http://{settings.HOST}:{settings.PORT}/api/v1/files/{lf.get('file_id')}/download",
                    "modified_at": lf.get("created_at"),
                    "size_bytes": lf.get("file_size", 0),
                    "shared": True
                })

        return {
            "success": True,
            "query": query,
            "count": len(results),
            "files": results
        }

    async def share_file(
        self,
        file_id: str,
        role: str = "reader",
        make_public: bool = True,
        recipient_email: Optional[str] = None,
        recipient_name: Optional[str] = None,
        user_id: str = "default_user"
    ) -> Dict[str, Any]:
        """
        Grants all-accessible permissions to a Google Drive file / Doc,
        or shares directly with a contact's email address.
        """
        # Resolve recipient name to email from contact vault if email not given
        if recipient_name and not recipient_email:
            matched_contact = contact_vault.get_contact_by_name(recipient_name, user_id=user_id)
            if matched_contact and matched_contact.email_addresses:
                recipient_email = matched_contact.email_addresses[0]

        headers = await self._get_auth_headers(user_id)
        if not headers:
            # Check if it's a local file
            local_meta = storage_service.get_file(file_id)
            if local_meta:
                share_url = f"http://{settings.HOST}:{settings.PORT}/api/v1/files/{file_id}/download"
                return {
                    "success": True,
                    "status": "SHARED_LOCAL",
                    "file_id": file_id,
                    "filename": local_meta.get("filename"),
                    "shareable_url": share_url,
                    "recipient_email": recipient_email,
                    "role": role,
                    "message": f"Generated all-accessible link for '{local_meta.get('filename')}': {share_url}"
                }
            return {
                "success": False,
                "status": "NOT_CONNECTED",
                "message": "Google Drive is not connected. Connect Google Account in Settings."
            }

        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                perm_payload: Dict[str, Any] = {}
                if recipient_email:
                    perm_payload = {
                        "role": role,
                        "type": "user",
                        "emailAddress": recipient_email
                    }
                elif make_public:
                    perm_payload = {
                        "role": role,
                        "type": "anyone"
                    }

                # 1. Create permission on Drive file
                perm_resp = await client.post(
                    f"{DRIVE_API_BASE}/files/{file_id}/permissions",
                    headers=headers,
                    json=perm_payload
                )

                # 2. Get shareable webViewLink
                file_resp = await client.get(
                    f"{DRIVE_API_BASE}/files/{file_id}?fields=id,name,mimeType,webViewLink,webContentLink",
                    headers=headers
                )
                file_meta = file_resp.json() if file_resp.status_code == 200 else {}
                shareable_url = file_meta.get("webViewLink") or f"https://drive.google.com/file/d/{file_id}/view"

                target_desc = f"with {recipient_email}" if recipient_email else "with Anyone with the link (All-accessible)"
                return {
                    "success": True,
                    "status": "SHARED_GOOGLE_DRIVE",
                    "file_id": file_id,
                    "filename": file_meta.get("name", "Document"),
                    "shareable_url": shareable_url,
                    "recipient_email": recipient_email,
                    "role": role,
                    "message": f"Successfully shared '{file_meta.get('name', 'File')}' {target_desc}. Link: {shareable_url}"
                }
        except Exception as e:
            logger.error(f"Error sharing file: {e}")
            return {
                "success": False,
                "status": "ERROR",
                "message": str(e)
            }

google_docs_drive_service = GoogleDocsDriveService()
