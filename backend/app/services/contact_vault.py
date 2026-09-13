import sqlite3
import json
import time
import uuid
import re
import difflib
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from pydantic import BaseModel, Field
from backend.app.config import settings

logger = logging.getLogger("SmartGlasses.ContactVault")

class VaultContact(BaseModel):
    id: str
    user_id: str = "default_user"
    name: str
    aliases: List[str] = Field(default_factory=list)
    phone_numbers: List[str] = Field(default_factory=list)
    email_addresses: List[str] = Field(default_factory=list)
    company: Optional[str] = None
    notes: Optional[str] = None
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)

class ContactResolutionResult(BaseModel):
    status: str  # "RESOLVED", "AMBIGUOUS", "NOT_FOUND"
    contact: Optional[VaultContact] = None
    candidates: List[VaultContact] = Field(default_factory=list)
    confidence: float = 0.0
    clarification_prompt: Optional[str] = None

class PersonalContactVault:
    """
    User-controlled Personal Contact & Account Registry.
    Provides explicit phone/email account linking, alias mapping, fuzzy search,
    and ambiguity disambiguation.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = settings.DATABASE_URL.replace("sqlite:///", "").lstrip("./")
        self.db_path = Path(db_path).resolve()
        self._init_db()
        self._seed_default_contacts()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS personal_contacts (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    aliases TEXT NOT NULL,
                    phone_numbers TEXT NOT NULL,
                    email_addresses TEXT NOT NULL,
                    company TEXT,
                    notes TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            conn.commit()

    def _seed_default_contacts(self):
        default_seed = [
            {
                "id": "c_rahul_sharma",
                "name": "Rahul Sharma",
                "aliases": ["Rahul", "Sharmaji", "Colleague"],
                "phone_numbers": ["+919876543210"],
                "email_addresses": ["rahul.sharma@techcorp.com", "tyachi6@gmail.com"],
                "company": "TechCorp",
                "notes": "Engineering lead"
            },
            {
                "id": "c_rahul_verma",
                "name": "Rahul Verma",
                "aliases": ["Junior Rahul", "Classmate"],
                "phone_numbers": ["+919876543219"],
                "email_addresses": ["rahul.verma@college.edu"],
                "company": "University",
                "notes": "College batchmate"
            },
            {
                "id": "c_sneha_patil",
                "name": "Sneha Patil",
                "aliases": ["Sneha", "Teammate"],
                "phone_numbers": ["+919876543211"],
                "email_addresses": ["sneha.patil@techcorp.com"],
                "company": "TechCorp",
                "notes": "Product designer"
            },
            {
                "id": "c_amit_joshi",
                "name": "Amit Joshi",
                "aliases": ["Amit", "Friend"],
                "phone_numbers": ["+919876543212"],
                "email_addresses": ["amit.joshi@gmail.com"],
                "company": "FinTech",
                "notes": "Friend"
            },
            {
                "id": "c_priya_rao",
                "name": "Priya Rao",
                "aliases": ["Priya", "Mentor"],
                "phone_numbers": ["+919876543213"],
                "email_addresses": ["priya.rao@iit.ac.in"],
                "company": "IIT",
                "notes": "Academic advisor"
            }
        ]
        with self._get_conn() as conn:
            for c in default_seed:
                row = conn.execute("SELECT id FROM personal_contacts WHERE id = ?", (c["id"],)).fetchone()
                if not row:
                    conn.execute("""
                        INSERT INTO personal_contacts (
                            id, user_id, name, aliases, phone_numbers, email_addresses, company, notes, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        c["id"], "default_user", c["name"],
                        json.dumps(c["aliases"]),
                        json.dumps(c["phone_numbers"]),
                        json.dumps(c["email_addresses"]),
                        c["company"], c["notes"],
                        time.time(), time.time()
                    ))
            conn.commit()

    def add_contact(
        self,
        user_id: str,
        name: str,
        phone_numbers: Optional[List[str]] = None,
        email_addresses: Optional[List[str]] = None,
        aliases: Optional[List[str]] = None,
        company: Optional[str] = None,
        notes: Optional[str] = None
    ) -> VaultContact:
        cid = f"c_{uuid.uuid4().hex[:10]}"
        now = time.time()
        phones = phone_numbers or []
        emails = email_addresses or []
        alias_list = aliases or []

        contact = VaultContact(
            id=cid,
            user_id=user_id,
            name=name.strip(),
            aliases=alias_list,
            phone_numbers=phones,
            email_addresses=emails,
            company=company,
            notes=notes,
            created_at=now,
            updated_at=now
        )
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO personal_contacts (
                    id, user_id, name, aliases, phone_numbers, email_addresses, company, notes, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                contact.id, contact.user_id, contact.name,
                json.dumps(contact.aliases),
                json.dumps(contact.phone_numbers),
                json.dumps(contact.email_addresses),
                contact.company, contact.notes,
                now, now
            ))
            conn.commit()
        return contact

    def list_contacts(self, user_id: str = "default_user") -> List[VaultContact]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM personal_contacts WHERE user_id = ? ORDER BY name ASC", (user_id,)).fetchall()
            return [
                VaultContact(
                    id=r["id"],
                    user_id=r["user_id"],
                    name=r["name"],
                    aliases=json.loads(r["aliases"]),
                    phone_numbers=json.loads(r["phone_numbers"]),
                    email_addresses=json.loads(r["email_addresses"]),
                    company=r["company"],
                    notes=r["notes"],
                    created_at=r["created_at"],
                    updated_at=r["updated_at"]
                )
                for r in rows
            ]

    def delete_contact(self, contact_id: str, user_id: str = "default_user") -> bool:
        with self._get_conn() as conn:
            cur = conn.execute("DELETE FROM personal_contacts WHERE id = ? AND user_id = ?", (contact_id, user_id))
            conn.commit()
            return cur.rowcount > 0

    def resolve_contact(self, query: str, user_id: str = "default_user") -> ContactResolutionResult:
        """
        Resolves a name query against personal contact registry.
        Employs exact matching, alias matching, substring inclusion, and fuzzy similarity.
        """
        if not query:
            return ContactResolutionResult(status="NOT_FOUND")

        raw_q = query.strip().lower()
        # Clean honorifics
        clean_q = re.sub(r"\b(?:bhai|ji|sir|mam|didi|bro|mr|mrs|to|for|with)\b", "", raw_q).strip()
        all_contacts = self.list_contacts(user_id)

        # 1. Exact Full Name, First Name, or Alias Match
        exact_matches = []
        for c in all_contacts:
            c_name_lower = c.name.lower()
            first_name = c_name_lower.split()[0] if c_name_lower else ""
            if c_name_lower == clean_q or c_name_lower == raw_q or first_name == clean_q or first_name == raw_q:
                exact_matches.append(c)
            elif any(a.lower() == clean_q or a.lower() == raw_q for a in c.aliases):
                exact_matches.append(c)

        if len(exact_matches) == 1:
            return ContactResolutionResult(status="RESOLVED", contact=exact_matches[0], confidence=1.0)
        elif len(exact_matches) > 1:
            names = " and ".join(c.name for c in exact_matches)
            return ContactResolutionResult(
                status="AMBIGUOUS",
                candidates=exact_matches,
                confidence=0.9,
                clarification_prompt=f"I found multiple contacts matching '{query}': {names}. Which one did you mean?"
            )

        # 2. Substring Name / Alias Match
        sub_matches = []
        for c in all_contacts:
            if clean_q in c.name.lower() or any(clean_q in a.lower() for a in c.aliases):
                sub_matches.append(c)

        if len(sub_matches) == 1:
            return ContactResolutionResult(status="RESOLVED", contact=sub_matches[0], confidence=0.88)
        elif len(sub_matches) > 1:
            names = " and ".join(c.name for c in sub_matches)
            return ContactResolutionResult(
                status="AMBIGUOUS",
                candidates=sub_matches,
                confidence=0.85,
                clarification_prompt=f"I found multiple contacts matching '{query}': {names}. Which one did you mean?"
            )

        # 3. Fuzzy Similarity Match
        best_score = 0.0
        best_contact = None
        for c in all_contacts:
            name_score = difflib.SequenceMatcher(None, clean_q, c.name.lower()).ratio()
            alias_scores = [difflib.SequenceMatcher(None, clean_q, a.lower()).ratio() for a in c.aliases]
            max_alias = max(alias_scores) if alias_scores else 0.0
            score = max(name_score, max_alias)
            if score > best_score:
                best_score = score
                best_contact = c

        if best_score >= 0.75 and best_contact:
            return ContactResolutionResult(status="RESOLVED", contact=best_contact, confidence=best_score)

        return ContactResolutionResult(status="NOT_FOUND", confidence=0.0)

    def find_by_phone(self, phone: str, user_id: str = "default_user") -> Optional[VaultContact]:
        clean_phone = re.sub(r"[^\d+]", "", phone)
        for c in self.list_contacts(user_id):
            for p in c.phone_numbers:
                if re.sub(r"[^\d+]", "", p) == clean_phone or p.endswith(clean_phone[-10:]) if len(clean_phone) >= 10 else False:
                    return c
        return None

    def find_by_email(self, email: str, user_id: str = "default_user") -> Optional[VaultContact]:
        clean_email = email.strip().lower()
        for c in self.list_contacts(user_id):
            for e in c.email_addresses:
                if e.strip().lower() == clean_email:
                    return c
        return None

contact_vault = PersonalContactVault()

