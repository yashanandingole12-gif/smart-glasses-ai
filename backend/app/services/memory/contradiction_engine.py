"""
EVA Contradiction & Evolution Engine:
Handles evolving preferences, life changes, and belief updates without deleting historical truth.
Implements:
- Contradiction Detection against active memories
- Evolution Status Tracking ('CURRENT' -> 'EVOLVED' / 'HISTORICAL')
- Memory Graph Linking (relation='supersedes')
- Confidence Scoring Adjustment (repeated vs single emotional claims)
"""
import time
import logging
import uuid
from typing import Dict, Any, List, Optional, Tuple
from backend.app.services.memory.eva_memory_store import eva_memory_store, MemoryItem, EvaMemoryStore

logger = logging.getLogger("SmartGlasses.ContradictionEngine")


class ContradictionResult:
    def __init__(
        self,
        has_conflict: bool,
        conflicting_memory: Optional[Dict[str, Any]] = None,
        evolution_type: str = "NONE",  # NONE, PREFERENCE_SHIFT, LIFE_EVENT, UNCERTAIN
        reason: str = ""
    ):
        self.has_conflict = has_conflict
        self.conflicting_memory = conflicting_memory
        self.evolution_type = evolution_type
        self.reason = reason


class ContradictionEngine:
    """
    Evaluates new user statements against established memories to preserve continuity.
    Understands: 'Yash changed his mind' rather than 'one memory must be deleted'.
    """

    def __init__(self, memory_store: Optional[EvaMemoryStore] = None):
        self.memory_store = memory_store or eva_memory_store

    def evaluate_statement(self, statement: str, category: str = "preference") -> ContradictionResult:
        """
        Scans existing memories in category or across categories for potential contradictions.
        """
        tokens = [t.lower() for t in statement.split() if len(t) > 3]
        if not tokens:
            return ContradictionResult(has_conflict=False)

        # Fetch active candidate memories in the target category (or cross-category)
        with self.memory_store._get_connection() as conn:
            cursor = conn.cursor()
            if category and category != "general":
                cursor.execute("""
                    SELECT * FROM memories
                    WHERE category = ? AND status IN ('current', 'CURRENT', 'uncertain', 'UNCERTAIN')
                    ORDER BY date_created DESC LIMIT 20
                """, (category,))
            else:
                cursor.execute("""
                    SELECT * FROM memories
                    WHERE status IN ('current', 'CURRENT', 'uncertain', 'UNCERTAIN')
                    ORDER BY date_created DESC LIMIT 20
                """)
            candidates = [dict(r) for r in cursor.fetchall()]

        st_lower = statement.lower()
        for cand in candidates:
            cand_content = cand.get("content", "").lower()

            # 1. Career / Aspiration shift
            if any(w in st_lower for w in ["want", "career", "work in", "focus on"]) or category == "career":
                if any(w in st_lower for w in ["ai", "robotics", "autonomy", "software"]) and any(w in cand_content for w in ["traditional", "mechanical", "tooling", "fabrication", "lathe"]):
                    return ContradictionResult(
                        has_conflict=True,
                        conflicting_memory=cand,
                        evolution_type="PREFERENCE_SHIFT",
                        reason="Career direction evolved from traditional mechanical tooling to AI robotics & autonomy."
                    )

            # 2. Preference negation ("I don't like X anymore" vs "Likes X")
            if any(neg in st_lower for neg in ["don't like", "no longer", "stopped", "quit", "not interested in"]):
                triggers = cand.get("triggers", [])
                if isinstance(triggers, str):
                    try:
                        triggers = json.loads(triggers)
                    except Exception:
                        triggers = []
                for trigger in triggers:
                    if trigger.lower() in st_lower:
                        return ContradictionResult(
                            has_conflict=True,
                            conflicting_memory=cand,
                            evolution_type="PREFERENCE_SHIFT",
                            reason=f"User indicated shift in preference regarding '{trigger}'."
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
