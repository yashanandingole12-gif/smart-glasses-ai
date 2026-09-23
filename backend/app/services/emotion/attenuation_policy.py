"""
HUD Appearance & Attenuation Render Policy.
Translates cognitive memory and wearer affect into dynamic HUD display rules:
High arousal/stress -> Attenuate notifications, soften contrast, suppress non-urgent overlays.
Calm/relaxed -> Allow ambient informative layers.
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel
from backend.app.services.emotion.affect_engine import AffectVector


class HUDRenderState(BaseModel):
    """Configuration for smart glasses visual HUD rendering."""
    contrast_level: float  # 0.1 (ultra-soft) to 1.0 (high)
    max_active_cards: int
    allow_non_urgent_notifications: bool
    glyph_mode: str  # "MINIMAL_BREATH", "EXPANDED_ORBIT", "SILENT_DOT"
    active_overlay_layer: str  # "TURN_BY_TURN", "CONVERSATION_ASSIST", "READING_HINT", "AMBIENT_OVERVIEW"
    color_temperature: str  # "SOFT_INDIGO", "PEACOCK_TEAL", "WARM_AMBER"
    attenuation_level_pct: int


class AttenuationPolicyEngine:
    """
    Renders glasses display state according to the principle:
    'Appearance is a view into the context engine, never a separate feature. One state, many renderings.'
    """

    def compute_render_policy(
        self,
        affect: AffectVector,
        active_activity: str = "IDLE",
        is_in_conversation: bool = False
    ) -> HUDRenderState:
        """Determines HUD visual density and contrast based on arousal and task context."""
        arousal = affect.arousal
        valence = affect.valence

        # Calculate base attenuation from arousal (0.0 to 1.0)
        # Higher arousal -> higher attenuation (getting out of the way)
        attenuation_pct = int(min(100, max(0, arousal * 100)))

        # 1. Attenuation by Arousal / Stress Level
        if arousal > 0.70:
            # High stress/arousal: emergency/critical information only, softened contrast
            contrast = 0.35
            max_cards = 1
            allow_non_urgent = False
            glyph_mode = "SILENT_DOT"
            color_temp = "SOFT_INDIGO"
        elif arousal > 0.45:
            # Moderate arousal: streamlined focus
            contrast = 0.65
            max_cards = 2
            allow_non_urgent = False
            glyph_mode = "MINIMAL_BREATH"
            color_temp = "PEACOCK_TEAL"
        else:
            # Calm / baseline: ambient richness allowed
            contrast = 0.90
            max_cards = 4
            allow_non_urgent = True
            glyph_mode = "EXPANDED_ORBIT"
            color_temp = "WARM_AMBER" if valence > 0.3 else "PEACOCK_TEAL"

        # 2. Context-Driven Overlay Layer
        act = active_activity.upper()
        if "WALK" in act or "NAVIGAT" in act:
            layer = "TURN_BY_TURN"
        elif is_in_conversation or "CONVERSATION" in act:
            layer = "CONVERSATION_ASSIST"
        elif "READ" in act or "DOCUMENT" in act:
            layer = "READING_HINT"
        else:
            layer = "AMBIENT_OVERVIEW"

        return HUDRenderState(
            contrast_level=contrast,
            max_active_cards=max_cards,
            allow_non_urgent_notifications=allow_non_urgent,
            glyph_mode=glyph_mode,
            active_overlay_layer=layer,
            color_temperature=color_temp,
            attenuation_level_pct=attenuation_pct
        )
