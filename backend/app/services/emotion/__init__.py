"""
Emotion and affect subsystem package.
"""
from backend.app.services.emotion.affect_engine import AffectEngine, AffectVector
from backend.app.services.emotion.social_affect_separator import SocialAffectSeparator, SurroundingIndividualAffect
from backend.app.services.emotion.attenuation_policy import AttenuationPolicyEngine, HUDRenderState
from backend.app.services.emotion.ethical_guard import EmotionEthicalGuard, EthicalRefusalError

__all__ = [
    "AffectEngine",
    "AffectVector",
    "SocialAffectSeparator",
    "SurroundingIndividualAffect",
    "AttenuationPolicyEngine",
    "HUDRenderState",
    "EmotionEthicalGuard",
    "EthicalRefusalError"
]
