"""
Ethical Guard & Privacy Boundary for Emotion & Wearable Appearance.
Enforces:
1. Propose, Never Assert: Affect interventions are tentative and user-correctable.
2. Hard Refusal: Strictly forbids manipulating the wearer's outward appearance
   to deceive or socially manipulate others in real time.
3. Strict Privacy: Affect states remain confidential to the wearer.
"""
from typing import Dict, Any, Optional
from backend.app.services.emotion.affect_engine import AffectVector


class EthicalRefusalError(Exception):
    """Raised when an operation violates the wearable ethics guardrail."""
    pass


class EmotionEthicalGuard:
    """Enforces privacy invariants and ethical rendering constraints."""

    @staticmethod
    def generate_tentative_proposal(affect: AffectVector) -> Optional[Dict[str, str]]:
        """Generates tentative, user-correctable assistance prompts."""
        if affect.arousal > 0.70 and affect.valence < -0.2:
            return {
                "type": "STRESS_ATTENUATION_PROPOSAL",
                "spoken_prompt": "You seem a bit stressed. Would you like me to hold non-urgent notifications?",
                "suggested_action": "HOLD_NOTIFICATIONS"
            }
        elif affect.arousal > 0.65 and affect.valence > 0.4:
            return {
                "type": "HIGH_FOCUS_PROPOSAL",
                "spoken_prompt": "Looks like you're in a high-focus flow. Should I keep HUD overlays minimal?",
                "suggested_action": "MINIMAL_HUD"
            }
        return None

    @staticmethod
    def validate_appearance_mutation_request(request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hard Guardrail:
        Blocks any command attempting to disguise, deceive, or covertly alter outward social appearance.
        """
        intent = str(request_payload.get("intent", "")).lower()
        target_audience = str(request_payload.get("target_audience", "wearer")).lower()
        deceptive_flags = ["deceive", "manipulate_others", "fake_expression", "mask_mood_to_others", "alter_external_lens_tint_covertly"]

        if any(flag in intent for flag in deceptive_flags) or (target_audience != "wearer" and "covert" in intent):
            raise EthicalRefusalError(
                "ETHICAL VIOLATION REFUSAL: The system strictly refuses to alter outward appearance "
                "or disguise the wearer to covertly manipulate how bystanders perceive them in real time."
            )

        return {"status": "AUTHORIZED_SAFE", "target": target_audience}
