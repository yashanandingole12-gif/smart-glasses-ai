"""
Social Affect Separator.
Strictly separates the wearer's internal affective state from the affect
of surrounding individuals / ambient social group.
"""
from typing import Dict, Any, List
import time
from pydantic import BaseModel, Field
from backend.app.services.emotion.affect_engine import AffectVector


class SurroundingIndividualAffect(BaseModel):
    """Estimated affect of a bystander or interlocutor."""
    person_id: str
    name: str = "Unknown"
    estimated_valence: float = 0.0
    estimated_arousal: float = 0.2
    confidence: float = 0.65
    last_observed: float = Field(default_factory=time.time)


class SocialAffectSeparator:
    """
    Manages dual affective contexts:
    1. Wearer internal state (grounded, high privacy, controls HUD attenuation)
    2. Surrounding social dynamics (contextual awareness for conversation assistance)
    """

    def __init__(self):
        self.surrounding_people: Dict[str, SurroundingIndividualAffect] = {}
        self.ambient_room_energy: float = 0.2

    def record_surrounding_observation(
        self,
        person_id: str,
        name: str,
        valence: float,
        arousal: float,
        confidence: float = 0.7
    ) -> SurroundingIndividualAffect:
        """Records an external person's affective cues."""
        ind = SurroundingIndividualAffect(
            person_id=person_id,
            name=name,
            estimated_valence=max(-1.0, min(1.0, valence)),
            estimated_arousal=max(0.0, min(1.0, arousal)),
            confidence=confidence,
            last_observed=time.time()
        )
        self.surrounding_people[person_id] = ind
        self._update_room_energy()
        return ind

    def _update_room_energy(self) -> None:
        """Computes aggregate room mood/energy."""
        if not self.surrounding_people:
            self.ambient_room_energy = 0.2
            return
        arousals = [p.estimated_arousal for p in self.surrounding_people.values()]
        self.ambient_room_energy = round(sum(arousals) / len(arousals), 2)

    def get_social_context_summary(self, wearer_affect: AffectVector) -> Dict[str, Any]:
        """Provides decoupled summary ensuring wearer state is clearly delineated."""
        return {
            "wearer_internal": {
                "valence": wearer_affect.valence,
                "arousal": wearer_affect.arousal,
                "is_private": True
            },
            "surrounding_environment": {
                "ambient_room_energy": self.ambient_room_energy,
                "observed_individuals_count": len(self.surrounding_people),
                "individuals": [
                    {
                        "name": p.name,
                        "valence": p.estimated_valence,
                        "arousal": p.estimated_arousal
                    }
                    for p in self.surrounding_people.values()
                ]
            }
        }
