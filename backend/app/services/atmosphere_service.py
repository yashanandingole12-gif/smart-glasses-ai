"""
EVA Color Atmosphere System & Tone Shifting Engine
Provides a unified semantic atmosphere model across Web, Android, and Smart Glasses.

Principle: Color Existing Inside Darkness.
Supported Atmospheres:
  1. GROUNDED   (#0C0C08, #6D6333, #B49E45) - calm / grounded / stable
  2. FOCUSED    (#161411, #484428, #D3A95B) - clarity / concentration / precision
  3. CREATIVE   (#190903, #510A16, #B57B88) - creative / intimate / expressive
  4. CURIOUS    (#0C0805, #703912, #D3A95B) - discovery / exploration / curiosity
  5. REFLECTIVE (#161411, #7F582D, #ECDBA1) - quiet / contemplative / deep
  6. ENERGETIC  (#301306, #B1650E, #ECDBA1) - momentum / action / vitality
  7. NIGHT      (#0C0805, #190903, #D3A95B) - mysterious / quiet / expansive
  8. CUSTOM     - adaptive user-defined tone shifting
"""

import logging
from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field

logger = logging.getLogger("eva.atmosphere")

class AtmosphereMode(str, Enum):
    GROUNDED = "GROUNDED"
    FOCUSED = "FOCUSED"
    CREATIVE = "CREATIVE"
    CURIOUS = "CURIOUS"
    REFLECTIVE = "REFLECTIVE"
    ENERGETIC = "ENERGETIC"
    NIGHT = "NIGHT"
    CUSTOM = "CUSTOM"

class AtmospherePreset(BaseModel):
    id: AtmosphereMode
    name: str
    emotion: str
    foundation: str
    night_base: str
    accent: str
    highlight: str
    surface_tint: str
    border_illumination: str
    glow_opacity: float = Field(default=0.25, ge=0.05, le=0.80)
    particle_density: int = Field(default=24, ge=8, le=64)
    motion_scale: float = Field(default=1.0, ge=0.4, le=1.8)
    transition_ms: int = Field(default=1400, ge=800, le=2500)

ATMOSPHERE_PRESETS: Dict[AtmosphereMode, AtmospherePreset] = {
    AtmosphereMode.GROUNDED: AtmospherePreset(
        id=AtmosphereMode.GROUNDED,
        name="Grounded",
        emotion="calm / grounded / stable",
        foundation="#0C0C08",
        night_base="#161411",
        accent="#6D6333",
        highlight="#B49E45",
        surface_tint="rgba(22, 20, 15, 0.72)",
        border_illumination="rgba(109, 99, 51, 0.35)",
        glow_opacity=0.22,
        particle_density=20,
        motion_scale=0.85,
        transition_ms=1400
    ),
    AtmosphereMode.FOCUSED: AtmospherePreset(
        id=AtmosphereMode.FOCUSED,
        name="Focused",
        emotion="clarity / concentration / precision",
        foundation="#161411",
        night_base="#190903",
        accent="#484428",
        highlight="#D3A95B",
        surface_tint="rgba(28, 25, 21, 0.75)",
        border_illumination="rgba(211, 169, 91, 0.30)",
        glow_opacity=0.25,
        particle_density=18,
        motion_scale=0.80,
        transition_ms=1200
    ),
    AtmosphereMode.CREATIVE: AtmospherePreset(
        id=AtmosphereMode.CREATIVE,
        name="Creative",
        emotion="creative / intimate / expressive",
        foundation="#190903",
        night_base="#2B221E",
        accent="#510A16",
        highlight="#B57B88",
        surface_tint="rgba(33, 16, 20, 0.75)",
        border_illumination="rgba(181, 123, 136, 0.35)",
        glow_opacity=0.32,
        particle_density=28,
        motion_scale=1.15,
        transition_ms=1600
    ),
    AtmosphereMode.CURIOUS: AtmospherePreset(
        id=AtmosphereMode.CURIOUS,
        name="Curious",
        emotion="discovery / exploration / curiosity",
        foundation="#0C0805",
        night_base="#161411",
        accent="#703912",
        highlight="#D3A95B",
        surface_tint="rgba(26, 17, 12, 0.75)",
        border_illumination="rgba(211, 169, 91, 0.35)",
        glow_opacity=0.28,
        particle_density=24,
        motion_scale=1.00,
        transition_ms=1400
    ),
    AtmosphereMode.REFLECTIVE: AtmospherePreset(
        id=AtmosphereMode.REFLECTIVE,
        name="Reflective",
        emotion="quiet / contemplative / deep",
        foundation="#161411",
        night_base="#0C0805",
        accent="#7F582D",
        highlight="#ECDBA1",
        surface_tint="rgba(27, 23, 19, 0.72)",
        border_illumination="rgba(236, 219, 161, 0.28)",
        glow_opacity=0.20,
        particle_density=16,
        motion_scale=0.75,
        transition_ms=1800
    ),
    AtmosphereMode.ENERGETIC: AtmospherePreset(
        id=AtmosphereMode.ENERGETIC,
        name="Energetic",
        emotion="momentum / action / vitality",
        foundation="#301306",
        night_base="#190903",
        accent="#B1650E",
        highlight="#ECDBA1",
        surface_tint="rgba(48, 22, 10, 0.78)",
        border_illumination="rgba(236, 219, 161, 0.45)",
        glow_opacity=0.38,
        particle_density=32,
        motion_scale=1.35,
        transition_ms=1100
    ),
    AtmosphereMode.NIGHT: AtmospherePreset(
        id=AtmosphereMode.NIGHT,
        name="Night",
        emotion="mysterious / quiet / expansive",
        foundation="#0C0805",
        night_base="#161411",
        accent="#190903",
        highlight="#D3A95B",
        surface_tint="rgba(19, 15, 12, 0.80)",
        border_illumination="rgba(211, 169, 91, 0.22)",
        glow_opacity=0.18,
        particle_density=14,
        motion_scale=0.65,
        transition_ms=1800
    ),
    AtmosphereMode.CUSTOM: AtmospherePreset(
        id=AtmosphereMode.CUSTOM,
        name="Custom",
        emotion="adaptive / personal resonance",
        foundation="#0C0805",
        night_base="#161411",
        accent="#703912",
        highlight="#D3A95B",
        surface_tint="rgba(24, 18, 14, 0.75)",
        border_illumination="rgba(211, 169, 91, 0.30)",
        glow_opacity=0.25,
        particle_density=22,
        motion_scale=1.00,
        transition_ms=1400
    )
}

class AtmosphereService:
    def __init__(self):
        self._current_mode: AtmosphereMode = AtmosphereMode.GROUNDED
        self._custom_override: Optional[AtmospherePreset] = None
        logger.info(f"AtmosphereService initialized (Default: {self._current_mode.value})")

    def get_current_atmosphere(self) -> AtmospherePreset:
        if self._current_mode == AtmosphereMode.CUSTOM and self._custom_override:
            return self._custom_override
        return ATMOSPHERE_PRESETS.get(self._current_mode, ATMOSPHERE_PRESETS[AtmosphereMode.GROUNDED])

    def get_current_mode(self) -> str:
        return self._current_mode.value

    def set_atmosphere(self, mode: AtmosphereMode) -> AtmospherePreset:
        if mode in ATMOSPHERE_PRESETS:
            self._current_mode = mode
            logger.info(f"[ATMOSPHERE] Tone shifted to {mode.value} ({ATMOSPHERE_PRESETS[mode].emotion})")
        return self.get_current_atmosphere()

    def set_custom_atmosphere(
        self,
        foundation: str,
        accent: str,
        highlight: str,
        emotion: str = "custom adaptive",
        glow_opacity: float = 0.25,
        motion_scale: float = 1.0
    ) -> AtmospherePreset:
        self._custom_override = AtmospherePreset(
            id=AtmosphereMode.CUSTOM,
            name="Custom",
            emotion=emotion,
            foundation=foundation,
            night_base="#161411",
            accent=accent,
            highlight=highlight,
            surface_tint=f"{accent}22",
            border_illumination=f"{highlight}40",
            glow_opacity=glow_opacity,
            particle_density=22,
            motion_scale=motion_scale,
            transition_ms=1400
        )
        self._current_mode = AtmosphereMode.CUSTOM
        logger.info(f"[ATMOSPHERE] Configured and applied CUSTOM atmosphere ({foundation}, {accent}, {highlight})")
        return self._custom_override

    def get_all_presets(self) -> List[Dict[str, Any]]:
        return [p.model_dump() for p in ATMOSPHERE_PRESETS.values()]

    def get_wearable_state(self) -> Dict[str, Any]:
        """Returns compact lightweight state for Smart Glasses BLE transmission."""
        atm = self.get_current_atmosphere()
        return {
            "atmosphere": atm.id.value,
            "accent": atm.accent,
            "highlight": atm.highlight,
            "foundation": atm.foundation
        }

atmosphere_service = AtmosphereService()
