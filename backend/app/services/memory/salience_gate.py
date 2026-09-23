"""
Salience Gate for Ambient-First Context Engine.
Filters high-frequency perception events based on novelty, task relevance,
and emotional marking to gate promotion into Working Memory.
"""
from typing import Dict, Any, Optional, Set
import time
from backend.app.services.perception.perception_buffer import PerceptionEvent


class SalienceGate:
    """
    Evaluates events using a multi-factor salience score:
      S = w_novelty * N + w_task * T + w_emotion * E
    Only events passing the threshold θ are admitted to Working Memory.
    """

    def __init__(
        self,
        salience_threshold: float = 0.55,
        weight_novelty: float = 0.40,
        weight_task_relevance: float = 0.35,
        weight_emotion: float = 0.25
    ):
        self.salience_threshold = salience_threshold
        self.weight_novelty = weight_novelty
        self.weight_task_relevance = weight_task_relevance
        self.weight_emotion = weight_emotion
        self.seen_signatures: Set[str] = set()
        self.signature_timestamps: Dict[str, float] = {}

    def compute_salience(
        self,
        event: PerceptionEvent,
        active_task_context: Optional[str] = None,
        wearer_arousal: float = 0.2
    ) -> float:
        """Calculates normalized salience score in range [0.0, 1.0]."""
        # 1. Novelty Scoring (N)
        sig = f"{event.event_type}_{event.metadata.get('name', '')}_{event.metadata.get('text_preview', '')}"
        now = time.time()
        
        last_seen = self.signature_timestamps.get(sig, 0.0)
        time_delta = now - last_seen
        
        if sig not in self.seen_signatures:
            novelty = 1.0
        elif time_delta > 120.0:
            novelty = min(1.0, 0.4 + (time_delta / 300.0))
        else:
            novelty = max(0.1, time_delta / 120.0)

        # 2. Task Relevance Scoring (T)
        task_relevance = 0.2  # Default ambient baseline
        if active_task_context:
            ctx_lower = active_task_context.lower()
            if "navigate" in ctx_lower and "SIGN" in event.event_type:
                task_relevance = 0.95
            elif "conversation" in ctx_lower and "PERSON" in event.event_type:
                task_relevance = 0.90
            elif "read" in ctx_lower and "DOCUMENT" in event.event_type:
                task_relevance = 0.88
            elif "meeting" in ctx_lower and "SPEAKER" in event.event_type:
                task_relevance = 0.92

        # 3. Emotional Marking (E)
        # High arousal boosts salience because urgent/stressful events require attention
        emotion_mark = min(1.0, 0.2 + (wearer_arousal * 0.8))

        # Combined Salience Score
        salience = (
            self.weight_novelty * novelty +
            self.weight_task_relevance * task_relevance +
            self.weight_emotion * emotion_mark
        )
        
        event.salience_score = round(salience, 3)
        return event.salience_score

    def should_promote(
        self,
        event: PerceptionEvent,
        active_task_context: Optional[str] = None,
        wearer_arousal: float = 0.2
    ) -> bool:
        """Determines if the event should breach the salience gate into Working Memory."""
        score = self.compute_salience(event, active_task_context, wearer_arousal)
        promoted = score >= self.salience_threshold

        if promoted:
            sig = f"{event.event_type}_{event.metadata.get('name', '')}_{event.metadata.get('text_preview', '')}"
            self.seen_signatures.add(sig)
            self.signature_timestamps[sig] = time.time()

        return promoted
