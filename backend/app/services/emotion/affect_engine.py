"""
Continuous Affect & Emotion Dynamics Engine.
Maintains a 2D Valence-Arousal state vector with a slow decay time constant (tau ~ 240s),
filtering momentary micro-expressions into sustained baseline emotional shifts.
"""
from typing import Dict, Any, List, Optional
import time
import math
from pydantic import BaseModel, Field


class AffectVector(BaseModel):
    """2D Valence-Arousal emotion representation."""
    valence: float = Field(default=0.0, ge=-1.0, le=1.0, description="Negative (-1.0) to Positive (+1.0)")
    arousal: float = Field(default=0.2, ge=0.0, le=1.0, description="Calm (0.0) to Stressed/Excited (1.0)")
    confidence: float = 0.8
    last_updated: float = Field(default_factory=time.time)
    baseline_drift: float = 0.0


class AffectEngine:
    """
    Tracks running affect over slow time constants.
    Filters micro-expression noise: a single smile or furrowed brow is noise;
    only multi-turn acoustic/prosodic/biometric trends shift the baseline.
    """

    def __init__(self, decay_tau_seconds: float = 240.0, micro_expression_weight: float = 0.15):
        self.decay_tau_seconds = decay_tau_seconds
        self.micro_expression_weight = micro_expression_weight
        self.current_affect = AffectVector()
        self.baseline_affect = AffectVector(valence=0.1, arousal=0.2)
        self.observation_history: List[Dict[str, Any]] = []

    def update_from_telemetry(
        self,
        instantaneous_valence: float,
        instantaneous_arousal: float,
        modality_weights: Optional[Dict[str, float]] = None,
        source: str = "voice_prosody"
    ) -> AffectVector:
        """
        Applies exponential decay toward baseline and integrates new observations.
        v(t) = baseline + (v_prev - baseline) * exp(-dt/tau) + w * delta
        """
        now = time.time()
        dt = max(0.0, now - self.current_affect.last_updated)
        decay_factor = math.exp(-dt / self.decay_tau_seconds)

        # Decay towards baseline
        decayed_v = self.baseline_affect.valence + (self.current_affect.valence - self.baseline_affect.valence) * decay_factor
        decayed_a = self.baseline_affect.arousal + (self.current_affect.arousal - self.baseline_affect.arousal) * decay_factor

        # Attenuate the impact of momentary micro-expressions
        weight = self.micro_expression_weight
        if modality_weights and source in modality_weights:
            weight *= modality_weights[source]

        # Update running vector with dampening
        new_v = decayed_v + weight * (instantaneous_valence - decayed_v)
        new_a = decayed_a + weight * (instantaneous_arousal - decayed_a)

        # Clamp bounds
        self.current_affect.valence = max(-1.0, min(1.0, round(new_v, 3)))
        self.current_affect.arousal = max(0.0, min(1.0, round(new_a, 3)))
        self.current_affect.last_updated = now

        self.observation_history.append({
            "timestamp": now,
            "source": source,
            "instant_v": instantaneous_valence,
            "instant_a": instantaneous_arousal,
            "running_v": self.current_affect.valence,
            "running_a": self.current_affect.arousal
        })

        if len(self.observation_history) > 50:
            self.observation_history.pop(0)

        return self.current_affect

    def apply_user_correction(self, corrected_valence: float, corrected_arousal: float) -> AffectVector:
        """Allows wearer to directly correct inferred affect state."""
        self.current_affect.valence = max(-1.0, min(1.0, corrected_valence))
        self.current_affect.arousal = max(0.0, min(1.0, corrected_arousal))
        self.current_affect.last_updated = time.time()
        # Adapt personal baseline slightly towards user feedback
        self.baseline_affect.valence = 0.8 * self.baseline_affect.valence + 0.2 * self.current_affect.valence
        self.baseline_affect.arousal = 0.8 * self.baseline_affect.arousal + 0.2 * self.current_affect.arousal
        return self.current_affect

    def get_affect_summary(self) -> str:
        """Returns qualitative natural language summary of current affect state."""
        v = self.current_affect.valence
        a = self.current_affect.arousal

        if a > 0.65:
            state = "Stressed / High Arousal" if v < 0.0 else "Excited / Highly Engaged"
        elif a < 0.30:
            state = "Relaxed / Calm" if v >= 0.0 else "Subdued / Fatigued"
        else:
            state = "Focused / Neutral Baseline"

        return f"{state} (Valence={v:.2f}, Arousal={a:.2f})"
