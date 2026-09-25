"""
AWS & IoT Standardized Schemas for EVA Smart Glasses AI Ecosystem.
Shared normalized schemas for ESP32-S3, Local MQTT, AWS IoT Core, FastAPI, and Web Console.
"""

import time
from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class AudioOutputMode(str, Enum):
    TWS = "tws"
    BONE_CONDUCTION = "bone_conduction"
    SPEAKER = "speaker"
    PHONE = "phone"
    SILENT = "silent"


class ConnectionState(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    STANDBY = "standby"
    ERROR = "error"


class TelemetryPayload(BaseModel):
    """
    Normalized telemetry schema across ESP32, Local MQTT, AWS IoT, and Web Console.
    """
    device_id: str = Field(default="EVA-GLS-01", description="Scalable device identity (e.g., EVA-GLS-01, EVA-GLS-02)")
    timestamp: float = Field(default_factory=time.time, description="Unix epoch timestamp in seconds")
    battery: int = Field(default=85, ge=0, le=100, description="Battery percentage (0-100)")
    temperature: float = Field(default=31.4, description="Onboard ESP32 sensor temperature in Celsius")
    free_heap: int = Field(default=241832, description="Available internal SRAM/PSRAM in bytes")
    ble: ConnectionState = Field(default=ConnectionState.CONNECTED, description="BLE connection status")
    wifi: ConnectionState = Field(default=ConnectionState.CONNECTED, description="Wi-Fi connection status")
    microphone: str = Field(default="ready", description="Microphone state: ready, recording, muted")
    audio: AudioOutputMode = Field(default=AudioOutputMode.TWS, description="Current audio routing target")
    firmware: str = Field(default="1.0.0", description="Installed firmware semantic version")
    uptime_seconds: Optional[int] = Field(default=0, description="Device uptime since boot")
    rssi: Optional[int] = Field(default=-62, description="Wi-Fi / BLE signal strength in dBm")


class DeviceStatusPayload(BaseModel):
    """
    High-level device connectivity and operational health.
    """
    device_id: str = "EVA-GLS-01"
    is_online: bool = True
    last_seen: float = Field(default_factory=time.time)
    transport_type: str = "LOCAL_MOCK"  # "LOCAL_MQTT", "AWS_IOT_CORE", "BLE", "SIMULATOR"
    active_session_id: Optional[str] = None
    diagnostics: Dict[str, Any] = Field(default_factory=dict)


class DeviceEventPayload(BaseModel):
    """
    Structured discrete hardware or agent events.
    """
    device_id: str = "EVA-GLS-01"
    event_type: str  # e.g., "BUTTON_SHORT_PRESS", "WAKEWORD_DETECTED", "CAMERA_FRAME_CAPTURED", "BATTERY_LOW"
    level: str = "INFO"  # "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
    timestamp: float = Field(default_factory=time.time)
    details: Dict[str, Any] = Field(default_factory=dict)


class DeviceCommandPayload(BaseModel):
    """
    Downlink command sent from Backend / Agent to Smart Glasses.
    """
    command_id: str
    device_id: str = "EVA-GLS-01"
    command_type: str  # e.g., "CAPTURE_FRAME", "SET_AUDIO_OUTPUT", "TRIGGER_HAPTIC", "REBOOT", "OTA_UPDATE"
    parameters: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)
    expires_at: Optional[float] = None


class DeviceShadowState(BaseModel):
    """
    AWS IoT Device Shadow state representation for synchronizing persistent config.
    """
    device_id: str = "EVA-GLS-01"
    desired: Dict[str, Any] = Field(default_factory=lambda: {"audio_output": "tws", "mic_gain": 80})
    reported: Dict[str, Any] = Field(default_factory=lambda: {"audio_output": "tws", "battery": 85, "firmware": "1.0.0"})
    delta: Optional[Dict[str, Any]] = None
    version: int = 1
    timestamp: float = Field(default_factory=time.time)


class MQTTTopicStructure:
    """
    Deterministic hierarchical MQTT topic generator for EVA device fleets.
    """
    @staticmethod
    def telemetry(device_id: str = "EVA-GLS-01") -> str:
        return f"eva/{device_id}/telemetry"

    @staticmethod
    def status(device_id: str = "EVA-GLS-01") -> str:
        return f"eva/{device_id}/status"

    @staticmethod
    def events(device_id: str = "EVA-GLS-01") -> str:
        return f"eva/{device_id}/events"

    @staticmethod
    def commands(device_id: str = "EVA-GLS-01") -> str:
        return f"eva/{device_id}/commands"

    @staticmethod
    def diagnostics(device_id: str = "EVA-GLS-01") -> str:
        return f"eva/{device_id}/diagnostics"

    @staticmethod
    def shadow_update(device_id: str = "EVA-GLS-01") -> str:
        return f"$aws/things/{device_id}/shadow/update"

    @staticmethod
    def shadow_get(device_id: str = "EVA-GLS-01") -> str:
        return f"$aws/things/{device_id}/shadow/get"
