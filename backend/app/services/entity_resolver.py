import re
import difflib
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field

class ResolutionStatus(str, Enum):
    RESOLVED = "RESOLVED"
    AMBIGUOUS = "AMBIGUOUS"
    NOT_FOUND = "NOT_FOUND"

class Contact(BaseModel):
    name: str
    phone: str
    relationship: Optional[str] = None
    email: Optional[str] = None

class EntityResolutionResult(BaseModel):
    status: ResolutionStatus
    contact: Optional[Contact] = None
    candidates: List[Contact] = Field(default_factory=list)
    confidence: float = 0.0
    clarification_prompt: Optional[str] = None

# Default test contacts repository
DEFAULT_CONTACTS: List[Contact] = [
    Contact(name="Rahul Sharma", phone="+919876543210", relationship="colleague", email="rahul.sharma@techcorp.com"),
    Contact(name="Rahul Verma", phone="+919876543219", relationship="classmate", email="rahul.verma@college.edu"),
    Contact(name="Sneha Patil", phone="+919876543211", relationship="teammate", email="sneha.patil@techcorp.com"),
    Contact(name="Amit Joshi", phone="+919876543212", relationship="friend", email="amit.joshi@gmail.com"),
    Contact(name="Priya Rao", phone="+919876543213", relationship="mentor", email="priya.rao@iit.ac.in")
]

COMPANY_DOMAINS: Dict[str, str] = {
    "linkedin": "linkedin.com",
    "github": "github.com",
    "amazon": "amazon.in",
    "google": "google.com",
    "swiggy": "swiggy.in",
    "zomato": "zomato.com",
    "internshala": "internshala.com",
    "angel one": "angelone.in",
    "college": "edu",
    "university": "edu",
    "iit": "iit",
    "apple": "apple.com",
    "microsoft": "microsoft.com",
    "uber": "uber.com",
    "twitter": "x.com"
}

class EntityResolver:
    """
    Deterministic entity resolution layer for contacts, companies, and parameters.
    Implements normalization, fuzzy string matching, confidence scoring,
    and ambiguity detection.
    """

    def __init__(self, contacts: Optional[List[Contact]] = None):
        self.contacts = contacts if contacts is not None else DEFAULT_CONTACTS
        self.company_domains = COMPANY_DOMAINS

    def resolve_domain(self, query: str) -> Optional[str]:
        """Resolves company name to canonical domain query."""
        if not query:
            return None
        q = query.lower().strip()
        for k, v in self.company_domains.items():
            if k in q:
                return v
        return None

    def normalize_name(self, text: str) -> str:
        """Strip honorifics, titles, and non-alphanumeric noise."""
        if not text:
            return ""
        norm = text.lower().strip()
        # Remove common Indian honorifics / colloquial suffixes
        honorifics = ["bhai", "ji", "sir", "mam", "didi", "bro", "dr", "mr", "mrs", "miss"]
        for h in honorifics:
            norm = re.sub(rf"\b{h}\b", "", norm).strip()
        norm = re.sub(r"[^\w\s]", "", norm)
        return re.sub(r"\s+", " ", norm).strip()

    def resolve_contact(
        self,
        query: str,
        high_threshold: float = 0.85,
        ambiguity_gap: float = 0.15
    ) -> EntityResolutionResult:
        """
        Resolves a name query against contact database with confidence scoring:
        - High confidence & unique -> RESOLVED
        - Multiple close matches -> AMBIGUOUS (prompts clarification)
        - Low confidence -> NOT_FOUND
        """
        norm_query = self.normalize_name(query)
        if not norm_query:
            return EntityResolutionResult(
                status=ResolutionStatus.NOT_FOUND,
                confidence=0.0,
                clarification_prompt="Please specify a recipient name."
            )

        scored_candidates = []

        for c in self.contacts:
            c_norm = self.normalize_name(c.name)
            first_name = c_norm.split()[0] if c_norm else ""

            # Exact match on full name, first name, or relationship
            if norm_query == c_norm or norm_query == first_name:
                score = 1.0
            elif c.relationship and norm_query in [c.relationship.lower(), f"my {c.relationship.lower()}"]:
                score = 1.0
            else:
                # Fuzzy ratio matching
                score_full = difflib.SequenceMatcher(None, norm_query, c_norm).ratio()
                score_first = difflib.SequenceMatcher(None, norm_query, first_name).ratio() if first_name else 0.0
                score_rel = difflib.SequenceMatcher(None, norm_query, c.relationship.lower()).ratio() if c.relationship else 0.0
                score = max(score_full, score_first, score_rel)


            scored_candidates.append((score, c))

        # Sort by highest score descending
        scored_candidates.sort(key=lambda x: x[0], reverse=True)

        top_matches = [c for s, c in scored_candidates if s >= 0.50]
        if not top_matches:
            return EntityResolutionResult(
                status=ResolutionStatus.NOT_FOUND,
                confidence=scored_candidates[0][0] if scored_candidates else 0.0,
                clarification_prompt=f"I couldn't find any contact matching '{query}'."
            )

        top_score, top_contact = scored_candidates[0]

        # Check for ambiguity: multiple matches with score >= 0.70 or close gap
        high_matches = [(s, c) for s, c in scored_candidates if s >= 0.70]
        if len(high_matches) > 1:
            second_score, second_contact = scored_candidates[1]
            if (top_score - second_score) < ambiguity_gap or (top_score == second_score):
                names_str = " and ".join(f"{c.name} ({c.phone})" for _, c in high_matches[:3])
                return EntityResolutionResult(
                    status=ResolutionStatus.AMBIGUOUS,
                    candidates=[c for _, c in high_matches],
                    confidence=top_score,
                    clarification_prompt=f"I found multiple contacts for '{query}': {names_str}. Which one do you mean?"
                )

        # High confidence unique match
        if top_score >= high_threshold or (top_score >= 0.70 and len(top_matches) == 1):
            return EntityResolutionResult(
                status=ResolutionStatus.RESOLVED,
                contact=top_contact,
                candidates=[top_contact],
                confidence=top_score
            )

        # Ambiguous if below high threshold but above 0.50
        names_str = " or ".join(f"{c.name}" for c in top_matches[:2])
        return EntityResolutionResult(
            status=ResolutionStatus.AMBIGUOUS,
            candidates=top_matches,
            confidence=top_score,
            clarification_prompt=f"Did you mean {names_str}?"
        )

entity_resolver = EntityResolver()
