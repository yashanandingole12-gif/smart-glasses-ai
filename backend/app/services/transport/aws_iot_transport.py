"""
AWS IoT Core Transport Implementation:
Used when AWS_ENABLED=true. Handles MQTT/TLS connections using X.509 client certificates,
subscribes to device fleet topics, manages Device Shadows, and publishes telemetry.
"""

import json
import time
import logging
import ssl
from typing import Callable, Dict, Any, Optional, List
from collections import defaultdict

from backend.app.config import settings
from backend.app.models.aws_schemas import (
    TelemetryPayload,
    DeviceStatusPayload,
    DeviceEventPayload,
    DeviceCommandPayload,
    DeviceShadowState,
    MQTTTopicStructure
)
from backend.app.services.transport.device_transport import DeviceTransport

logger = logging.getLogger("SmartGlasses.AwsIotTransport")


class AwsIotTransport(DeviceTransport):
    """
    Production-ready AWS IoT Core transport over MQTT/TLS (Port 8883).
    Supports X.509 device certificates without hardcoding AWS access keys.
    """

    def __init__(
        self,
        endpoint: Optional[str] = None,
        client_id: Optional[str] = None,
        cert_path: Optional[str] = None,
        key_path: Optional[str] = None,
        root_ca_path: Optional[str] = None
    ):
        self.endpoint = endpoint or settings.AWS_IOT_ENDPOINT
        self.client_id = client_id or settings.AWS_IOT_CLIENT_ID
        self.cert_path = cert_path or settings.AWS_IOT_CERT_PATH
        self.key_path = key_path or settings.AWS_IOT_KEY_PATH
        self.root_ca_path = root_ca_path or settings.AWS_IOT_ROOT_CA_PATH

        self._connected = False
        self._mqtt_client = None
        self._subscribers: Dict[str, List[Callable[[str, Dict[str, Any]], None]]] = defaultdict(list)
        self._shadow_cache: Dict[str, DeviceShadowState] = {}

    async def connect(self) -> bool:
        """
        Initializes MQTT client and establishes TLS connection with AWS IoT Core.
        If endpoint or certs are not configured, logs diagnostic notice without crashing.
        """
        if not self.endpoint:
            logger.info("AWS IoT endpoint not configured. Operating in simulated AWS IoT mode.")
            self._connected = True
            return True

        try:
            # Check for paho-mqtt or AWSIoTPythonSDK
            try:
                import paho.mqtt.client as mqtt
                self._mqtt_client = mqtt.Client(client_id=self.client_id, protocol=mqtt.MQTTv311)
                
                if self.cert_path and self.key_path and self.root_ca_path:
                    self._mqtt_client.tls_set(
                        ca_certs=self.root_ca_path,
                        certfile=self.cert_path,
                        keyfile=self.key_path,
                        cert_reqs=ssl.CERT_REQUIRED,
                        tls_version=ssl.PROTOCOL_TLSv1_2
                    )

                self._mqtt_client.on_connect = self._on_connect
                self._mqtt_client.on_message = self._on_message
                self._mqtt_client.connect(self.endpoint, port=8883, keepalive=60)
                self._mqtt_client.loop_start()
                self._connected = True
                logger.info(f"AwsIotTransport connected to AWS IoT Core endpoint: {self.endpoint}")
                return True
            except ImportError:
                logger.info("paho-mqtt not installed; operating in mock AWS IoT mode.")
                self._connected = True
                return True
        except Exception as e:
            logger.error(f"Failed to connect to AWS IoT Core: {e}")
            self._connected = False
            return False

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Successfully connected to AWS IoT Core broker.")
            # Resubscribe to all active topics
            for topic in self._subscribers.keys():
                client.subscribe(topic)
        else:
            logger.error(f"AWS IoT Core connection refused with code: {rc}")

    def _on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload_str = msg.payload.decode("utf-8")
            payload_data = json.loads(payload_str)
            for handler in self._subscribers.get(topic, []):
                handler(topic, payload_data)
        except Exception as e:
            logger.error(f"Error processing AWS IoT message on {msg.topic}: {e}")

    async def disconnect(self) -> bool:
        if self._mqtt_client:
            try:
                self._mqtt_client.loop_stop()
                self._mqtt_client.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting AWS IoT client: {e}")
        self._connected = False
        logger.info("AwsIotTransport disconnected.")
        return True

    def is_connected(self) -> bool:
        return self._connected

    async def publish_telemetry(self, telemetry: TelemetryPayload) -> bool:
        topic = MQTTTopicStructure.telemetry(telemetry.device_id)
        payload = telemetry.model_dump()
        return self._publish(topic, payload)

    async def publish_event(self, event: DeviceEventPayload) -> bool:
        topic = MQTTTopicStructure.events(event.device_id)
        payload = event.model_dump()
        return self._publish(topic, payload)

    async def publish_status(self, status: DeviceStatusPayload) -> bool:
        topic = MQTTTopicStructure.status(status.device_id)
        payload = status.model_dump()
        return self._publish(topic, payload)

    async def send_command(self, command: DeviceCommandPayload) -> bool:
        topic = MQTTTopicStructure.commands(command.device_id)
        payload = command.model_dump()
        return self._publish(topic, payload)

    async def update_shadow(self, shadow: DeviceShadowState) -> bool:
        topic = MQTTTopicStructure.shadow_update(shadow.device_id)
        shadow_doc = {
            "state": {
                "desired": shadow.desired,
                "reported": shadow.reported
            }
        }
        self._shadow_cache[shadow.device_id] = shadow
        return self._publish(topic, shadow_doc)

    async def get_shadow(self, device_id: str) -> Optional[DeviceShadowState]:
        if device_id in self._shadow_cache:
            return self._shadow_cache[device_id]
        topic = MQTTTopicStructure.shadow_get(device_id)
        self._publish(topic, {})
        return self._shadow_cache.get(device_id) or DeviceShadowState(device_id=device_id)

    def subscribe(self, topic: str, handler: Callable[[str, Dict[str, Any]], None]) -> bool:
        self._subscribers[topic].append(handler)
        if self._mqtt_client and self._connected:
            self._mqtt_client.subscribe(topic)
        logger.debug(f"[AwsIotTransport] Subscribed to {topic}")
        return True

    def _publish(self, topic: str, data: Dict[str, Any]) -> bool:
        if self._mqtt_client and self._connected:
            try:
                self._mqtt_client.publish(topic, json.dumps(data), qos=1)
                logger.debug(f"[AwsIotTransport] Published to {topic}")
                return True
            except Exception as e:
                logger.error(f"[AwsIotTransport] Publish error: {e}")
                return False
        else:
            logger.debug(f"[AwsIotTransport Mock] Published to {topic}: {list(data.keys())}")
            # Notify local subscribers for test/mock compatibility
            for handler in self._subscribers.get(topic, []):
                handler(topic, data)
            return True
