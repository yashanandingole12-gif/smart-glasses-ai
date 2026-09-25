"""
Local MQTT / In-Memory Transport Implementation:
Used when AWS_ENABLED=false. Provides full local loopback, event subscription,
command routing, and mock Device Shadow synchronization.
"""

import time
import logging
from typing import Callable, Dict, Any, Optional, List
from collections import defaultdict

from backend.app.models.aws_schemas import (
    TelemetryPayload,
    DeviceStatusPayload,
    DeviceEventPayload,
    DeviceCommandPayload,
    DeviceShadowState,
    MQTTTopicStructure
)
from backend.app.services.transport.device_transport import DeviceTransport

logger = logging.getLogger("SmartGlasses.LocalMqttTransport")


class LocalMqttTransport(DeviceTransport):
    """
    Local in-memory / local broker transport.
    Zero external cloud dependencies for 100% offline operation.
    """

    def __init__(self):
        self._connected = False
        self._subscribers: Dict[str, List[Callable[[str, Dict[str, Any]], None]]] = defaultdict(list)
        self._last_telemetry: Dict[str, TelemetryPayload] = {}
        self._last_status: Dict[str, DeviceStatusPayload] = {}
        self._shadow_store: Dict[str, DeviceShadowState] = {}
        self._event_history: List[DeviceEventPayload] = []
        self._command_history: List[DeviceCommandPayload] = []

    async def connect(self) -> bool:
        self._connected = True
        logger.info("LocalMqttTransport connected (mode: LOCAL_OFFLINE)")
        return True

    async def disconnect(self) -> bool:
        self._connected = False
        logger.info("LocalMqttTransport disconnected")
        return True

    def is_connected(self) -> bool:
        return self._connected

    async def publish_telemetry(self, telemetry: TelemetryPayload) -> bool:
        self._last_telemetry[telemetry.device_id] = telemetry
        topic = MQTTTopicStructure.telemetry(telemetry.device_id)
        self._notify_subscribers(topic, telemetry.model_dump())
        logger.debug(f"[LocalTransport] Telemetry published to {topic}: batt={telemetry.battery}%, temp={telemetry.temperature}C")
        return True

    async def publish_event(self, event: DeviceEventPayload) -> bool:
        self._event_history.append(event)
        if len(self._event_history) > 100:
            self._event_history.pop(0)
        topic = MQTTTopicStructure.events(event.device_id)
        self._notify_subscribers(topic, event.model_dump())
        logger.info(f"[LocalTransport] Event published to {topic}: {event.event_type} ({event.level})")
        return True

    async def publish_status(self, status: DeviceStatusPayload) -> bool:
        self._last_status[status.device_id] = status
        topic = MQTTTopicStructure.status(status.device_id)
        self._notify_subscribers(topic, status.model_dump())
        logger.debug(f"[LocalTransport] Status published to {topic}: online={status.is_online}")
        return True

    async def send_command(self, command: DeviceCommandPayload) -> bool:
        self._command_history.append(command)
        topic = MQTTTopicStructure.commands(command.device_id)
        self._notify_subscribers(topic, command.model_dump())
        logger.info(f"[LocalTransport] Command sent to {topic}: {command.command_type} (id={command.command_id})")
        return True

    async def update_shadow(self, shadow: DeviceShadowState) -> bool:
        existing = self._shadow_store.get(shadow.device_id)
        if existing:
            # Merge desired and reported states
            merged_desired = {**existing.desired, **shadow.desired}
            merged_reported = {**existing.reported, **shadow.reported}
            # Calculate delta
            delta = {k: v for k, v in merged_desired.items() if merged_reported.get(k) != v}
            updated = DeviceShadowState(
                device_id=shadow.device_id,
                desired=merged_desired,
                reported=merged_reported,
                delta=delta if delta else None,
                version=existing.version + 1,
                timestamp=time.time()
            )
            self._shadow_store[shadow.device_id] = updated
        else:
            delta = {k: v for k, v in shadow.desired.items() if shadow.reported.get(k) != v}
            self._shadow_store[shadow.device_id] = DeviceShadowState(
                device_id=shadow.device_id,
                desired=shadow.desired,
                reported=shadow.reported,
                delta=delta if delta else shadow.delta,
                version=shadow.version,
                timestamp=shadow.timestamp
            )

        topic = MQTTTopicStructure.shadow_update(shadow.device_id)
        self._notify_subscribers(topic, self._shadow_store[shadow.device_id].model_dump())
        logger.info(f"[LocalTransport] Device shadow updated for {shadow.device_id} (version={self._shadow_store[shadow.device_id].version})")
        return True

    async def get_shadow(self, device_id: str) -> Optional[DeviceShadowState]:
        if device_id not in self._shadow_store:
            # Create default initial shadow
            self._shadow_store[device_id] = DeviceShadowState(device_id=device_id)
        return self._shadow_store.get(device_id)

    def subscribe(self, topic: str, handler: Callable[[str, Dict[str, Any]], None]) -> bool:
        self._subscribers[topic].append(handler)
        logger.debug(f"[LocalTransport] Subscribed to topic: {topic}")
        return True

    def _notify_subscribers(self, topic: str, payload: Dict[str, Any]):
        # Direct exact match
        for handler in self._subscribers.get(topic, []):
            try:
                handler(topic, payload)
            except Exception as e:
                logger.error(f"Error in subscriber handler for {topic}: {e}")
        
        # Wildcard match (e.g., eva/+/telemetry or eva/#)
        for pattern, handlers in self._subscribers.items():
            if "#" in pattern or "+" in pattern:
                if self._topic_matches(pattern, topic):
                    for h in handlers:
                        try:
                            h(topic, payload)
                        except Exception as e:
                            logger.error(f"Error in wildcard subscriber handler for {pattern}: {e}")

    @staticmethod
    def _topic_matches(pattern: str, topic: str) -> bool:
        pat_parts = pattern.split("/")
        top_parts = topic.split("/")
        i = 0
        for i, p in enumerate(pat_parts):
            if p == "#":
                return True
            if i >= len(top_parts):
                return False
            if p != "+" and p != top_parts[i]:
                return False
        return i == len(top_parts) - 1
