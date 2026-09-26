"""
EVA Contradiction & Evolution Engine:
Handles evolving preferences, life changes, and belief updates without deleting historical truth.
Implements:
- Generalized Multi-Category Contradiction Detection against active memories
- Shift & Evolution Status Tracking ('CURRENT' -> 'EVOLVED' / 'HISTORICAL')
- Memory Graph Linking (relation='supersedes')
- Confidence Scoring Adjustment (repeated vs single emotional claims)
"""
import time
import logging
import uuid
import re
import json
from typing import Dict, Any, List, Optional, Tuple
from backend.app.services.memory.eva_memory_store import eva_memory_store, MemoryItem, EvaMemoryStore

logger = logging.getLogger("SmartGlasses.ContradictionEngine")

# Common negation & transition indicator patterns
NEGATION_PATTERNS = [
    r"don't like\s+([a-zA-Z0-9_\s]+)",
    r"no longer\s+([a-zA-Z0-9_\s]+)",
    r"stopped\s+([a-zA-Z0-9_\s]+)",
    r"quit\s+([a-zA-Z0-9_\s]+)",
    r"not interested in\s+([a-zA-Z0-9_\s]+)",
    r"hate\s+([a-zA-Z0-9_\s]+)",
    r"switched from\s+([a-zA-Z0-9_\s]+)\s+to\s+([a-zA-Z0-9_\s]+)",
    r"moved from\s+([a-zA-Z0-9_\s]+)\s+to\s+([a-zA-Z0-9_\s]+)",
    r"not doing\s+([a-zA-Z0-9_\s]+)\s+anymore",
    r"changed my mind about\s+([a-zA-Z0-9_\s]+)",
    r"prefer\s+([a-zA-Z0-9_\s]+)\s+over\s+([a-zA-Z0-9_\s]+)"
]

EVOLUTION_CATEGORY_MAP = {
    "career": "CAREER_SHIFT",
    "preference": "PREFERENCE_SHIFT",
    "project": "PROJECT_PIVOT",
    "relationship": "RELATIONSHIP_UPDATE",
    "habits": "HABIT_EVOLUTION",
    "health": "HEALTH_UPDATE"
}


class ContradictionResult:
    def __init__(
        self,
        has_conflict: bool,
        conflicting_memory: Optional[Dict[str, Any]] = None,
        evolution_type: str = "NONE",  # NONE, PREFERENCE_SHIFT, CAREER_SHIFT, LIFE_EVENT, UNCERTAIN
        reason: str = ""
    ):
        self.has_conflict = has_conflict
        self.conflicting_memory = conflicting_memory
        self.evolution_type = evolution_type
        self.reason = reason


class ContradictionEngine:
    """
    Evaluates new user statements against established memories to preserve continuity.
    Understands: 'User changed their mind/direction' rather than 'one memory must be deleted'.
    """

    def __init__(self, memory_store: Optional[EvaMemoryStore] = None):
        self.memory_store = memory_store or eva_memory_store

    def evaluate_statement(self, statement: str, category: str = "preference") -> ContradictionResult:
        """
        Scans existing memories in category or across categories for potential contradictions,
        preference shifts, career evolutions, and lifestyle transitions.
        """
        st_lower = statement.strip().lower()
        tokens = [t for t in re.sub(r'[^a-zA-Z0-9\s]', ' ', st_lower).split() if len(t) > 2]
        if not tokens:
            return ContradictionResult(has_conflict=False)

        # Fetch active candidate memories in the target category (or cross-category)
        with self.memory_store._get_connection() as conn:
            cursor = conn.cursor()
            if category and category not in ("general", "CORE_IDENTITY"):
                cursor.execute("""
                    SELECT * FROM memories
                    WHERE (category = ? OR category LIKE ?) AND status IN ('current', 'CURRENT', 'uncertain', 'UNCERTAIN')
                    ORDER BY date_created DESC LIMIT 30
                """, (category, f"%{category}%"))
            else:
                cursor.execute("""
                    SELECT * FROM memories
                    WHERE status IN ('current', 'CURRENT', 'uncertain', 'UNCERTAIN')
                    ORDER BY date_created DESC LIMIT 30
                """)
            candidates = [dict(r) for r in cursor.fetchall()]

        # 1. Regex-driven Negation & Shift Detection
        for pattern in NEGATION_PATTERNS:
            match = re.search(pattern, st_lower)
            if match:
                negated_target = match.group(1).strip()
                negated_words = [w for w in negated_target.split() if len(w) > 2]
                
                for cand in candidates:
                    cand_content = cand.get("content", "").lower()
                    triggers = cand.get("triggers", [])
                    if isinstance(triggers, str):
                        try:
                            triggers = json.loads(triggers)
                        except Exception:
                            triggers = []
                    triggers_lower = [str(tr).lower() for tr in triggers]
                    
                    # Check if candidate mentions the negated target
                    matches_target = any(nw in cand_content for nw in negated_words) or any(nw in tr for tr in triggers_lower for nw in negated_words)
                    if matches_target:
                        ev_type = EVOLUTION_CATEGORY_MAP.get(category.lower(), "PREFERENCE_SHIFT")
                        return ContradictionResult(
                            has_conflict=True,
                            conflicting_memory=cand,
                            evolution_type=ev_type,
                            reason=f"User stated shift regarding '{negated_target}' ('{statement}')."
                        )

        # 2. Category-Specific Semantic Transition Rules
        for cand in candidates:
            cand_content = cand.get("content", "").lower()

            # Career / Aspiration shift (e.g. mechanical -> AI / robotics / software)
            if category in ("career", "CA.001", "aspiration") or any(w in st_lower for w in ["want to become", "career", "switched to", "focusing on"]):
                if any(w in st_lower for w in ["ai", "robotics", "autonomy", "software", "embedded"]) and any(w in cand_content for w in ["traditional", "mechanical", "tooling", "fabrication", "lathe", "manufacturing"]):
                    return ContradictionResult(
                        has_conflict=True,
                        conflicting_memory=cand,
                        evolution_type="CAREER_SHIFT",
                        reason="Career focus transitioned towards AI, robotics, and autonomy."
                    )

            # Location / Relocation shift
            if any(w in st_lower for w in ["moved to", "living in", "relocated to", "staying in"]):
                if any(w in cand_content for w in ["lives in", "based in", "staying in", "located at"]):
                    overlap_tokens = set(tokens) & set(cand_content.split())
                    if not any(city in cand_content for city in tokens):
                        return ContradictionResult(
                            has_conflict=True,
                            conflicting_memory=cand,
                            evolution_type="LOCATION_SHIFT",
                            reason=f"User indicated relocation or location change: '{statement}'."
                        )

            # Direct Antonym / Explicit Preference Inversion
            triggers = cand.get("triggers", [])
            if isinstance(triggers, str):
                try:
                    triggers = json.loads(triggers)
                except Exception:
                    triggers = []
            for trigger in triggers:
                tr_str = str(trigger).lower()
                if tr_str in st_lower and any(neg in st_lower for neg in ["don't", "not", "no longer", "never", "dislike", "stopped"]):
                    return ContradictionResult(
                        has_conflict=True,
                        conflicting_memory=cand,
                        evolution_type="PREFERENCE_SHIFT",
                        reason=f"Direct inversion of preference regarding '{trigger}'."
                    )

        return ContradictionResult(has_conflict=False)

    def process_and_evolve_memory(
        self,
        new_content: str,
        category: str,
        confidence: float = 0.85,
        importance: int = 3,
        sensitivity: str = "S1",
        triggers: Optional[List[str]] = None
    ) -> Tuple[str, Optional[str]]:
        """
        Inserts new memory, evolving conflicting previous memory if detected.
        Returns (new_memory_id, evolved_old_memory_id).
        """
        check = self.evaluate_statement(new_content, category)

        new_mem_id = f"MEM.{uuid.uuid4().hex[:8].upper()}"
        new_item = MemoryItem(
            memory_id=new_mem_id,
            category=category,
            content=new_content,
            confidence=confidence,
            importance=importance,
            sensitivity=sensitivity,
            kind="said",
            status="current",
            triggers=triggers or []
        )

        if check.has_conflict and check.conflicting_memory:
            old_id = check.conflicting_memory["memory_id"]
            evolved_id = self.memory_store.evolve_memory(
                old_memory_id=old_id,
                new_item=new_item,
                transition_context=check.reason
            )
            logger.info(f"Evolved memory {old_id} -> {evolved_id}: {check.reason}")
            return (evolved_id, old_id)

        # Standard insertion
        saved_id = self.memory_store.insert_memory(new_item)
        return (saved_id, None)


# Global Singleton
contradiction_engine = ContradictionEngine()
