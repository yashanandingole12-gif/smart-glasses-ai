"""
Ambient Working Memory Engine with Fresh Turn Context Assembly.
Maintains a rolling, attended set of facts (location, active company, visual focus, last turns)
and builds lightweight, task-specific prompt contexts dynamically (MemGPT-style salience paging).
"""
from typing import Dict, Any, List, Optional
import time
from pydantic import BaseModel, Field
from backend.app.services.perception.perception_buffer import PerceptionEvent


class AttendedFact(BaseModel):
    """An active fact in working memory."""
    fact_id: str
    category: str  # "LOCATION", "INTERLOCUTOR", "VISUAL_FOCUS", "CONVERSATION_TURN", "AFFECT_STATE"
    content: str
    confidence: float = 1.0
    timestamp: float = Field(default_factory=time.time)
    expires_at: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkingMemoryEngine:
    """
    Working Memory (minutes to hours).
    Provides rolling attended context and fresh prompt construction.
    """

    def __init__(self, fact_ttl_seconds: float = 3600.0):
        self.fact_ttl_seconds = fact_ttl_seconds
        self.facts: Dict[str, AttendedFact] = {}
        self.current_location: str = "Unknown"
        self.active_interlocutors: List[str] = []
        self.active_visual_target: Optional[str] = None
        self.recent_turns: List[Dict[str, str]] = []

    def add_or_update_fact(
        self,
        fact_id: str,
        category: str,
        content: str,
        ttl_seconds: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AttendedFact:
        """Adds or updates an attended fact with dynamic expiration."""
        now = time.time()
        ttl = ttl_seconds if ttl_seconds is not None else self.fact_ttl_seconds
        fact = AttendedFact(
            fact_id=fact_id,
            category=category,
            content=content,
            timestamp=now,
            expires_at=now + ttl,
            metadata=metadata or {}
        )
        self.facts[fact_id] = fact
        return fact

    def ingest_salient_event(self, event: PerceptionEvent) -> Optional[AttendedFact]:
        """Promotes a salient perception event into a structured working memory fact."""
        event_type = event.event_type
        now = time.time()

        if "PERSON" in event_type:
            name = event.metadata.get("name", "Unknown Person")
            if name not in self.active_interlocutors and name != "Unknown Person":
                self.active_interlocutors.append(name)
            return self.add_or_update_fact(
                fact_id=f"person_{name.lower().replace(' ', '_')}",
                category="INTERLOCUTOR",
                content=f"In proximity with {name} (distance ~{event.metadata.get('distance_m', 1.5)}m)",
                ttl_seconds=1800.0,
                metadata={"name": name, "confidence": event.confidence}
            )

        elif "DOCUMENT" in event_type or "SIGN" in event_type:
            text = event.metadata.get("text_preview", "Unspecified text")
            self.active_visual_target = text
            return self.add_or_update_fact(
                fact_id=f"visual_focus_{int(now)}",
                category="VISUAL_FOCUS",
                content=f"Gaze locked on: {text}",
                ttl_seconds=300.0,
                metadata={"text": text}
            )

        elif "RAPID_HEAD_TURN" in event_type:
            return self.add_or_update_fact(
                fact_id="last_head_turn",
                category="PHYSICAL_DYNAMICS",
                content=f"Wearer abruptly shifted head attention ({event.metadata.get('angular_speed_dps')} dps)",
                ttl_seconds=60.0
            )

        return None

    def record_dialogue_turn(self, role: str, message: str, max_turns: int = 4) -> None:
        """Records a dialogue turn and maintains a compact rolling window."""
        self.recent_turns.append({"role": role, "message": message, "timestamp": str(time.time())})
        if len(self.recent_turns) > max_turns:
            self.recent_turns = self.recent_turns[-max_turns:]

    def assemble_fresh_turn_context(
        self,
        query: str,
        relevant_long_term_facts: Optional[List[str]] = None,
        wearer_affect_summary: Optional[str] = None
    ) -> str:
        """
        Assembles fresh, compact turn context from active working memory + relevant LTM.
        Zero context bloating: never holds the whole day in the context window.
        """
        self._purge_expired_facts()
        sections: List[str] = []

        # 1. Location & Environmental State
        if self.current_location and self.current_location != "Unknown":
            sections.append(f"📍 Location: {self.current_location}")

        # 2. People in Attention
        if self.active_interlocutors:
            sections.append(f"👥 Present: {', '.join(self.active_interlocutors)}")

        # 3. Active Visual Focus / Screen
        if self.active_visual_target:
            sections.append(f"👁️ Visual Focus: {self.active_visual_target}")

        # 4. Affect State (Wearer Mood Baseline)
        if wearer_affect_summary:
            sections.append(f"🧠 Affect Context: {wearer_affect_summary}")

        # 5. Long-term memory temporal recall
        if relevant_long_term_facts:
            facts_text = " | ".join(relevant_long_term_facts[:3])
            sections.append(f"🏛️ Temporal LTM: {facts_text}")

        # 6. Immediate Dialogue Context
        if self.recent_turns:
            turns_str = "\n".join([f"{t['role'].upper()}: {t['message']}" for t in self.recent_turns[-3:]])
            sections.append(f"💬 Recent Turns:\n{turns_str}")

        return "\n".join(sections)

    def _purge_expired_facts(self) -> None:
        """Removes expired facts."""
        now = time.time()
        expired = [fid for fid, fact in self.facts.items() if fact.expires_at and fact.expires_at < now]
        for fid in expired:
            del self.facts[fid]

    def get_state(self) -> Dict[str, Any]:
        """Returns the current state of working memory."""
        self._purge_expired_facts()
        return {
            "active_facts_count": len(self.facts),
            "location": self.current_location,
            "interlocutors": self.active_interlocutors,
            "visual_target": self.active_visual_target,
            "recent_turns_count": len(self.recent_turns),
            "facts": [f.model_dump() for f in self.facts.values()]
        }
