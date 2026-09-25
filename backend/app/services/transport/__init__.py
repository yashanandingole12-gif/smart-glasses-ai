"""
Device Transport Layer for EVA Smart Glasses AI Ecosystem.
Provides seamless switching between Local MQTT/WebSocket transport and AWS IoT Core.
"""

from .device_transport import DeviceTransport
from .local_mqtt_transport import LocalMqttTransport
from .aws_iot_transport import AwsIotTransport
from .transport_factory import get_device_transport

__all__ = [
    "DeviceTransport",
    "LocalMqttTransport",
    "AwsIotTransport",
    "get_device_transport"
]
