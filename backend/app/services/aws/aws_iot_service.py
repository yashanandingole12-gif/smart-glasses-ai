"""
AWS IoT Service:
High-level service coordinating device telemetry, event dispatch,
downlink commands, and Device Shadow state synchronization.
"""

import time
import uuid
import logging
from typing import Dict, Any, Optional, Callable, List

from backend.app.config import settings
from backend.app.models.aws_schemas import (
    TelemetryPayload,
    DeviceStatusPayload,
    DeviceEventPayload,
    DeviceCommandPayload,
    DeviceShadowState,
    MQTTTopicStructure
)
from backend.app.services.transport.transport_factory import get_device_transport

logger = logging.getLogger("SmartGlasses.AwsIotService")


class AwsIotService:
    """
    Orchestrates IoT device communication across the EVA backend.
    Decoupled from underlying networking through the DeviceTransport abstraction.
    """

    def __init__(self):
        self._latest_telemetry: Dict[str, TelemetryPayload] = {}
        self._device_status: Dict[str, DeviceStatusPayload] = {}
        self._command_callbacks: Dict[str, List[Callable[[DeviceCommandPayload], None]]] = {}

    @property
    def transport(self):
        return get_device_transport()

    async def initialize(self) -> bool:
        """Connects transport and sets up fleet topic subscriptions."""
        transport = self.transport
        connected = await transport.connect()
        if connected:
            # Subscribe to fleet wildcard topics
            transport.subscribe("eva/+/telemetry", self._handle_incoming_telemetry)
            transport.subscribe("eva/+/events", self._handle_incoming_event)
            transport.subscribe("eva/+/status", self._handle_incoming_status)
            transport.subscribe("eva/+/commands", self._handle_incoming_command)
            logger.info("AwsIotService initialized and subscribed to fleet topics.")
        return connected

    async def ingest_telemetry(self, telemetry: TelemetryPayload) -> bool:
        """Publishes and caches normalized device telemetry."""
        self._latest_telemetry[telemetry.device_id] = telemetry
        # Update device status last_seen
        self._device_status[telemetry.device_id] = DeviceStatusPayload(
            device_id=telemetry.device_id,
            is_online=True,
            last_seen=time.time(),
            transport_type="AWS_IOT" if settings.AWS_ENABLED else "LOCAL_TRANSPORT"
        )
        return await self.transport.publish_telemetry(telemetry)

    async def dispatch_event(
        self,
        event_type: str,
        details: Optional[Dict[str, Any]] = None,
        level: str = "INFO",
        device_id: str = "EVA-GLS-01"
    ) -> bool:
        """Publishes a discrete hardware or agent event."""
        evt = DeviceEventPayload(
            device_id=device_id,
            event_type=event_type,
            level=level,
            timestamp=time.time(),
            details=details or {}
        )
        return await self.transport.publish_event(evt)

    async def send_command(
        self,
        command_type: str,
        parameters: Optional[Dict[str, Any]] = None,
        device_id: str = "EVA-GLS-01",
        timeout_seconds: float = 30.0
    ) -> DeviceCommandPayload:
        """Dispatches an authoritative command to the smart glasses."""
        cmd = DeviceCommandPayload(
            command_id=f"cmd_{uuid.uuid4().hex[:10]}",
            device_id=device_id,
            command_type=command_type,
            parameters=parameters or {},
            timestamp=time.time(),
            expires_at=time.time() + timeout_seconds
        )
        await self.transport.send_command(cmd)
        return cmd

    async def sync_shadow_desired(self, desired_state: Dict[str, Any], device_id: str = "EVA-GLS-01") -> bool:
        """Updates desired config in AWS IoT Device Shadow."""
        shadow = DeviceShadowState(
            device_id=device_id,
            desired=desired_state,
            reported={}
        )
        return await self.transport.update_shadow(shadow)

    async def sync_shadow_reported(self, reported_state: Dict[str, Any], device_id: str = "EVA-GLS-01") -> bool:
        """Updates reported state in AWS IoT Device Shadow."""
        shadow = DeviceShadowState(
            device_id=device_id,
            desired={},
            reported=reported_state
        )
        return await self.transport.update_shadow(shadow)

    async def get_shadow_state(self, device_id: str = "EVA-GLS-01") -> Optional[DeviceShadowState]:
        """Fetches current Device Shadow state."""
        return await self.transport.get_shadow(device_id)

    def get_latest_telemetry(self, device_id: str = "EVA-GLS-01") -> Optional[TelemetryPayload]:
        """Retrieves cached telemetry for Web Console and health checks."""
        return self._latest_telemetry.get(device_id) or TelemetryPayload(device_id=device_id)

    def get_device_status(self, device_id: str = "EVA-GLS-01") -> DeviceStatusPayload:
        """Retrieves device online and connectivity status."""
        return self._device_status.get(device_id) or DeviceStatusPayload(
            device_id=device_id,
            is_online=True,
            transport_type="AWS_IOT" if settings.AWS_ENABLED else "LOCAL_TRANSPORT"
        )

    # -------------------------------------------------------------------------
    # Internal Handlers
    # -------------------------------------------------------------------------
    def _handle_incoming_telemetry(self, topic: str, data: Dict[str, Any]):
        try:
            telemetry = TelemetryPayload(**data)
            self._latest_telemetry[telemetry.device_id] = telemetry
            self._device_status[telemetry.device_id] = DeviceStatusPayload(
                device_id=telemetry.device_id,
                is_online=True,
                last_seen=time.time()
            )
        except Exception as e:
            logger.warning(f"Failed to parse telemetry on {topic}: {e}")

    def _handle_incoming_event(self, topic: str, data: Dict[str, Any]):
        logger.info(f"Incoming event on {topic}: {data.get('event_type')}")

    def _handle_incoming_status(self, topic: str, data: Dict[str, Any]):
        dev_id = data.get("device_id", "EVA-GLS-01")
        self._device_status[dev_id] = DeviceStatusPayload(**data)

    def _handle_incoming_command(self, topic: str, data: Dict[str, Any]):
        logger.info(f"Incoming command dispatched on {topic}: {data.get('command_type')}")


aws_iot_service = AwsIotService()
