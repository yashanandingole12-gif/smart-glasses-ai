import logging
import httpx
import re
from typing import Dict, Any, List, Optional
from backend.app.config import settings
from backend.app.services.token_service import token_service
from backend.app.services.contact_vault import contact_vault, VaultContact

logger = logging.getLogger("SmartGlasses.GoogleContactsService")

PEOPLE_API_CONNECTIONS_URL = "https://people.googleapis.com/v1/people/me/connections"

class GoogleContactsService:
    """
    Google Contacts (People API) Integration Service.
    
    Security & Architecture Guarantees:
    - Uses minimal read-only scope ('https://www.googleapis.com/auth/contacts.readonly').
    - Tokens are managed securely in SQLite and never exposed to client, LLM, or logs.
    - Contacts are normalized (name, aliases, phone numbers, email addresses, organization)
      and synced into the user-controlled Contact Vault.
    - Employs safe deduplication without merging distinct contacts sharing common first names.
    """

    async def fetch_and_sync_contacts(self, user_id: str = "default_user") -> Dict[str, Any]:
        """Fetch contacts from Google People API and synchronize into Contact Vault."""
        access_token = await token_service.get_valid_access_token(user_id)
        if not access_token:
            logger.warning(f"Google Contacts sync skipped: No active Google OAuth token for user '{user_id}'")
            return {
                "success": False,
                "status": "NOT_CONNECTED",
                "message": "Google Account is not connected. Please connect Google Account first.",
                "synced_count": 0,
                "contacts": []
            }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        params = {
            "personFields": "names,emailAddresses,phoneNumbers,organizations,nicknames",
            "pageSize": 100
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(PEOPLE_API_CONNECTIONS_URL, headers=headers, params=params)

                if resp.status_code == 403:
                    logger.warning("Google People API 403 Forbidden - Check contacts.readonly scope.")
                    return {
                        "success": False,
                        "status": "INSUFFICIENT_SCOPES",
                        "message": "Google Contacts permission not granted. Please re-authorize Google Account with Contacts scope.",
                        "synced_count": 0,
                        "contacts": []
                    }

                if resp.status_code != 200:
                    logger.error(f"Google People API error HTTP {resp.status_code}: {resp.text[:100]}")
                    return {
                        "success": False,
                        "status": "ERROR",
                        "message": f"Google People API error HTTP {resp.status_code}",
                        "synced_count": 0,
                        "contacts": []
                    }

                data = resp.json()
                connections = data.get("connections", [])
                normalized = self._normalize_connections(connections)

                # Sync into Contact Vault
                synced_contacts = contact_vault.sync_google_contacts(normalized, user_id=user_id)
                logger.info(f"Successfully synced {len(synced_contacts)} Google Contacts for user '{user_id}'")

                return {
                    "success": True,
                    "status": "SYNCED",
                    "synced_count": len(synced_contacts),
                    "total_found": len(connections),
                    "contacts": [c.model_dump() for c in synced_contacts]
                }

        except Exception as e:
            logger.error(f"Exception during Google Contacts sync: {e}")
            return {
                "success": False,
                "status": "EXCEPTION",
                "message": str(e),
                "synced_count": 0,
                "contacts": []
            }

    def normalize_person_data(self, person: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize a single raw Google People API person object into a structured dictionary."""
        # 1. Name & Aliases
        names = person.get("names", [])
        primary_name = None
        given_name = None
        family_name = None
        if names:
            primary = next((n for n in names if n.get("metadata", {}).get("primary")), names[0])
            primary_name = primary.get("displayName")
            given_name = primary.get("givenName")
            family_name = primary.get("familyName")

        if not primary_name:
            return None

        aliases = []
        # Nicknames
        for nick in person.get("nicknames", []):
            val = nick.get("value")
            if val and val not in aliases and val.lower() != primary_name.lower():
                aliases.append(val)

        # First name alias if multi-word name
        if given_name and given_name.lower() != primary_name.lower() and given_name not in aliases:
            aliases.append(given_name)

        # 2. Phone Numbers
        phones = []
        for p in person.get("phoneNumbers", []):
            raw_phone = p.get("canonicalForm") or p.get("value")
            if raw_phone:
                clean_phone = re.sub(r"[^\d+]", "", raw_phone)
                if clean_phone and clean_phone not in phones:
                    phones.append(clean_phone)

        # 3. Email Addresses
        emails = []
        for e in person.get("emailAddresses", []):
            val = e.get("value")
            if val:
                clean_email = val.strip().lower()
                if clean_email and clean_email not in emails:
                    emails.append(clean_email)

        # 4. Organization & Job Title
        company = None
        job_title = None
        orgs = person.get("organizations", [])
        if orgs:
            primary_org = next((o for o in orgs if o.get("metadata", {}).get("primary")), orgs[0])
            company = primary_org.get("name")
            job_title = primary_org.get("title")

        notes = f"{job_title} at {company}" if (company and job_title) else (company or job_title)

        return {
            "name": primary_name.strip(),
            "aliases": aliases,
            "phone_numbers": phones,
            "email_addresses": emails,
            "organization": company,
            "job_title": job_title,
            "company": company,
            "notes": notes
        }

    def _normalize_connections(self, connections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize raw People API connection items into structured contact records."""
        results = []
        for person in connections:
            norm = self.normalize_person_data(person)
            if norm:
                results.append(norm)
        return results

google_contacts_service = GoogleContactsService()
