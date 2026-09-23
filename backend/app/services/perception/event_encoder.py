"""
Tiny Local Edge Event Encoder.
Translates high-frequency sensor snapshots (audio, gaze, IMU, scene) into
compact, semantic event tokens, filtering out 99.9% of raw uncompressed data.
"""
from typing import List, Optional, Dict, Any
import math
from backend.app.services.perception.perception_buffer import RawSensorSnapshot, PerceptionEvent


class TinyEventEncoder:
    """
    Lightweight local classifier simulating on-device micro-NPU edge models.
    Converts raw sensory streams to structured semantic events.
    """

    def __init__(
        self,
        voice_rms_threshold: float = 0.25,
        rapid_head_turn_dps: float = 80.0,
        gaze_stability_threshold: float = 0.85
    ):
        self.voice_rms_threshold = voice_rms_threshold
        self.rapid_head_turn_dps = rapid_head_turn_dps
        self.gaze_stability_threshold = gaze_stability_threshold

    def encode_events(
        self,
        snapshots: List[RawSensorSnapshot],
        detected_visual_entities: Optional[List[Dict[str, Any]]] = None
    ) -> List[PerceptionEvent]:
        """Analyzes recent snapshots and emits high-level semantic events."""
        if not snapshots:
            return []

        events: List[PerceptionEvent] = []
        latest = snapshots[-1]

        # 1. Acoustic & Speech Direction Detection
        if latest.audio_vad_active and latest.audio_rms_energy >= self.voice_rms_threshold:
            # Differentiate wearer voice from external speaker
            is_wearer = latest.audio_rms_energy > 0.65
            events.append(PerceptionEvent(
                event_type="SPEAKER_DIRECTED_AT_WEARER" if not is_wearer else "WEARER_SPEAKING",
                confidence=0.92,
                source_modalities=["audio"],
                metadata={
                    "rms_energy": latest.audio_rms_energy,
                    "vad_active": True,
                    "estimated_source": "wearer" if is_wearer else "interlocutor"
                }
            ))

        # 2. IMU & Head Dynamics Detection
        rot_speed = math.sqrt(
            latest.imu_angular_velocity[0] ** 2 +
            latest.imu_angular_velocity[1] ** 2 +
            latest.imu_angular_velocity[2] ** 2
        )
        if rot_speed > self.rapid_head_turn_dps:
            events.append(PerceptionEvent(
                event_type="RAPID_HEAD_TURN",
                confidence=0.88,
                source_modalities=["imu"],
                metadata={"angular_speed_dps": round(rot_speed, 1)}
            ))

        # 3. Gaze & Visual Fixation Detection
        gaze_mag = math.sqrt(
            latest.gaze_vector[0] ** 2 +
            latest.gaze_vector[1] ** 2 +
            latest.gaze_vector[2] ** 2
        )
        if gaze_mag > 0 and (latest.gaze_vector[2] / (gaze_mag + 1e-6)) > self.gaze_stability_threshold:
            events.append(PerceptionEvent(
                event_type="GAZE_STABLE_FOCUS",
                confidence=0.85,
                source_modalities=["gaze"],
                metadata={"focus_depth_axis": round(latest.gaze_vector[2], 2)}
            ))

        # 4. Semantic Vision Token Conversion (e.g. from local YOLO-nano / micro-ISP)
        if detected_visual_entities:
            for entity in detected_visual_entities:
                label = entity.get("label", "object").upper()
                dist = entity.get("distance_m", 1.5)
                
                if label in ["PERSON", "HUMAN", "FACE"]:
                    events.append(PerceptionEvent(
                        event_type="PERSON_APPROACHING" if dist < 2.0 else "PERSON_IN_PROXIMITY",
                        confidence=entity.get("confidence", 0.9),
                        source_modalities=["vision"],
                        metadata={"name": entity.get("name"), "distance_m": dist}
                    ))
                elif label in ["TEXT", "MENU", "DOCUMENT", "SIGNBOARD"]:
                    events.append(PerceptionEvent(
                        event_type="USER_LOOKING_AT_DOCUMENT" if label in ["MENU", "DOCUMENT"] else "USER_READING_SIGN",
                        confidence=entity.get("confidence", 0.9),
                        source_modalities=["vision", "gaze"],
                        metadata={"text_preview": entity.get("text", "")}
                    ))

        return events
