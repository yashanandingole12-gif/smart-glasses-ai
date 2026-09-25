"""
Transport Factory:
Determines whether to instantiate LocalMqttTransport or AwsIotTransport
based on the AWS_ENABLED configuration setting.
"""

import logging
from backend.app.config import settings
from backend.app.services.transport.device_transport import DeviceTransport
from backend.app.services.transport.local_mqtt_transport import LocalMqttTransport
from backend.app.services.transport.aws_iot_transport import AwsIotTransport

logger = logging.getLogger("SmartGlasses.TransportFactory")

_global_transport: DeviceTransport = None


def get_device_transport(force_recreate: bool = False) -> DeviceTransport:
    """
    Returns the active DeviceTransport singleton.
    Defaults to LocalMqttTransport when AWS_ENABLED=false.
    """
    global _global_transport
    if _global_transport is None or force_recreate:
        if settings.AWS_ENABLED:
            logger.info("Initializing AWS IoT Core Device Transport (AWS_ENABLED=true)")
            _global_transport = AwsIotTransport(
                endpoint=settings.AWS_IOT_ENDPOINT,
                client_id=settings.AWS_IOT_CLIENT_ID,
                cert_path=settings.AWS_IOT_CERT_PATH,
                key_path=settings.AWS_IOT_KEY_PATH,
                root_ca_path=settings.AWS_IOT_ROOT_CA_PATH
            )
        else:
            logger.info("Initializing Local MQTT / Loopback Device Transport (AWS_ENABLED=false)")
            _global_transport = LocalMqttTransport()
    return _global_transport
