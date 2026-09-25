"""
Device Transport Abstract Interface:
Defines the unified transport contract for all hardware communications
(telemetry, status, events, commands, and shadow state).
"""

from abc import ABC, abstractmethod
from typing import Callable, Dict, Any, Optional, List
from backend.app.models.aws_schemas import (
    TelemetryPayload,
    DeviceStatusPayload,
    DeviceEventPayload,
    DeviceCommandPayload,
    DeviceShadowState
)


class DeviceTransport(ABC):
    """
    Abstract communication contract.
    Implementations handle underlying networking (Local Loopback / Local MQTT / AWS IoT Core).
    """

    @abstractmethod
    async def connect(self) -> bool:
        """Establish transport connection with broker / cloud endpoint."""
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """Gracefully disconnect from transport."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Returns current connection status."""
        pass

    @abstractmethod
    async def publish_telemetry(self, telemetry: TelemetryPayload) -> bool:
        """Publish device telemetry."""
        pass

    @abstractmethod
    async def publish_event(self, event: DeviceEventPayload) -> bool:
        """Publish a discrete device event."""
        pass

    @abstractmethod
    async def publish_status(self, status: DeviceStatusPayload) -> bool:
        """Publish device status."""
        pass

    @abstractmethod
    async def send_command(self, command: DeviceCommandPayload) -> bool:
        """Send a downlink command to target device."""
        pass

    @abstractmethod
    async def update_shadow(self, shadow: DeviceShadowState) -> bool:
        """Update desired/reported state in Device Shadow."""
        pass

    @abstractmethod
    async def get_shadow(self, device_id: str) -> Optional[DeviceShadowState]:
        """Fetch current Device Shadow state."""
        pass

    @abstractmethod
    def subscribe(self, topic: str, handler: Callable[[str, Dict[str, Any]], None]) -> bool:
        """Subscribe to a specific topic or pattern with callback handler."""
        pass
