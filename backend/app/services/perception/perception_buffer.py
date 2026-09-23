"""
Ambient Perception Buffer (Sub-Second, Discardable Ring Buffer).
High-frequency sensor ingest (Frames, Audio RMS, IMU, Gaze) that processes at edge
and discards raw pixel data, emitting only lightweight semantic events.
"""
from typing import Dict, Any, List, Optional, Deque
from collections import deque
import time
import uuid
from pydantic import BaseModel, Field


class RawSensorSnapshot(BaseModel):
    """Sub-second raw sensor telemetry packet."""
    timestamp: float = Field(default_factory=time.time)
    has_image_frame: bool = False
    frame_width: int = 0
    frame_height: int = 0
    audio_rms_energy: float = 0.0
    audio_vad_active: bool = False
    imu_angular_velocity: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])  # pitch, roll, yaw
    imu_acceleration: List[float] = Field(default_factory=lambda: [0.0, 0.0, 1.0])       # ax, ay, az
    gaze_vector: List[float] = Field(default_factory=lambda: [0.0, 0.0, 1.0])            # gx, gy, gz
    ambient_lux: float = 250.0


class PerceptionEvent(BaseModel):
    """Discrete semantic event emitted by the local perception encoder."""
    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:8]}")
    timestamp: float = Field(default_factory=time.time)
    event_type: str  # e.g., "PERSON_APPROACHING", "GAZE_LOCKED_TEXT", "SPEAKER_FACING_WEARER", "RAPID_HEAD_TURN"
    confidence: float = 0.9
    source_modalities: List[str] = Field(default_factory=list)  # ["vision", "audio", "imu"]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    salience_score: Optional[float] = None


class PerceptionBuffer:
    """
    Rolling, sub-second discardable circular buffer for high-frequency smart glasses telemetry.
    Zero-pixel retention: pixels are analyzed by local tiny models and immediately released.
    """

    def __init__(self, max_buffer_size: int = 60, ttl_seconds: float = 1.0):
        self.max_buffer_size = max_buffer_size
        self.ttl_seconds = ttl_seconds
        self.buffer: Deque[RawSensorSnapshot] = deque(maxlen=max_buffer_size)
        self.discarded_frames_count: int = 0
        self.emitted_events_count: int = 0

    def push_snapshot(self, snapshot: RawSensorSnapshot) -> None:
        """Appends a high-frequency snapshot and discards stale entries beyond TTL."""
        now = time.time()
        self.buffer.append(snapshot)
        
        # Purge items older than TTL (zero long-term storage of raw telemetry)
        while self.buffer and (now - self.buffer[0].timestamp > self.ttl_seconds):
            discarded = self.buffer.popleft()
            if discarded.has_image_frame:
                self.discarded_frames_count += 1

    def get_recent_window(self, window_seconds: float = 1.0) -> List[RawSensorSnapshot]:
        """Returns valid active snapshots within the ephemeral window."""
        now = time.time()
        return [s for s in self.buffer if (now - s.timestamp) <= window_seconds]

    def clear(self) -> None:
        """Purges the buffer immediately."""
        self.buffer.clear()

    def get_telemetry_stats(self) -> Dict[str, Any]:
        """Returns operational metrics demonstrating ambient-first discard efficiency."""
        return {
            "current_buffer_length": len(self.buffer),
            "max_buffer_capacity": self.max_buffer_size,
            "ttl_seconds": self.ttl_seconds,
            "discarded_raw_frames": self.discarded_frames_count,
            "emitted_events": self.emitted_events_count,
            "privacy_mode": "ZERO_PIXEL_PERSISTENCE"
        }
