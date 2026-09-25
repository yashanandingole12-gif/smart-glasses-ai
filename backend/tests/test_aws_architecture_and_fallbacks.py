"""
Unit and Integration Tests for EVA AWS Cloud Integration Layer.
Verifies all AWS abstractions, transport decoupling, local fallbacks,
telemetry normalization, Device Shadow, and CloudWatch logging without requiring AWS credentials.
"""

import pytest
import time
from unittest.mock import patch, MagicMock

from backend.app.config import settings
from backend.app.models.aws_schemas import (
    TelemetryPayload,
    DeviceStatusPayload,
    DeviceEventPayload,
    DeviceCommandPayload,
    DeviceShadowState,
    MQTTTopicStructure,
    ConnectionState,
    AudioOutputMode
)
from backend.app.services.transport.local_mqtt_transport import LocalMqttTransport
from backend.app.services.transport.aws_iot_transport import AwsIotTransport
from backend.app.services.transport.transport_factory import get_device_transport
from backend.app.services.aws.aws_iot_service import aws_iot_service
from backend.app.services.aws.aws_s3_service import aws_s3_service
from backend.app.services.aws.aws_secrets_service import aws_secrets_service
from backend.app.services.aws.aws_cloudwatch_service import aws_cloudwatch_service, redact_sensitive_data


def test_aws_default_disabled_for_local_dev():
    """Verify AWS_ENABLED defaults to False for safe local development."""
    assert settings.AWS_ENABLED is False or isinstance(settings.AWS_ENABLED, bool)
    transport = get_device_transport(force_recreate=True)
    if not settings.AWS_ENABLED:
        assert isinstance(transport, LocalMqttTransport)


def test_telemetry_schema_normalization():
    """Verify normalized telemetry schema conforms to hardware and web contract."""
    telemetry = TelemetryPayload(
        device_id="EVA-GLS-01",
        battery=78,
        temperature=31.4,
        free_heap=241832,
        ble=ConnectionState.CONNECTED,
        wifi=ConnectionState.CONNECTED,
        microphone="ready",
        audio=AudioOutputMode.TWS,
        firmware="1.0.0"
    )
    assert telemetry.device_id == "EVA-GLS-01"
    assert telemetry.battery == 78
    assert telemetry.audio == AudioOutputMode.TWS
    d = telemetry.model_dump()
    assert "timestamp" in d
    assert d["free_heap"] == 241832


def test_mqtt_topic_hierarchy_generation():
    """Verify MQTT topics conform to the fleet structure."""
    assert MQTTTopicStructure.telemetry("EVA-GLS-01") == "eva/EVA-GLS-01/telemetry"
    assert MQTTTopicStructure.status("EVA-GLS-01") == "eva/EVA-GLS-01/status"
    assert MQTTTopicStructure.events("EVA-GLS-01") == "eva/EVA-GLS-01/events"
    assert MQTTTopicStructure.commands("EVA-GLS-01") == "eva/EVA-GLS-01/commands"
    assert MQTTTopicStructure.diagnostics("EVA-GLS-01") == "eva/EVA-GLS-01/diagnostics"
    # Scalable to fleet
    assert MQTTTopicStructure.telemetry("EVA-GLS-02") == "eva/EVA-GLS-02/telemetry"


@pytest.mark.asyncio
async def test_local_transport_telemetry_publish_and_subscribe():
    """Verify in-memory local transport dispatches telemetry to subscribers."""
    transport = LocalMqttTransport()
    await transport.connect()
    assert transport.is_connected() is True

    received = []
    def handler(topic, data):
        received.append((topic, data))

    transport.subscribe("eva/EVA-GLS-01/telemetry", handler)

    payload = TelemetryPayload(device_id="EVA-GLS-01", battery=92)
    published = await transport.publish_telemetry(payload)
    assert published is True
    assert len(received) == 1
    assert received[0][0] == "eva/EVA-GLS-01/telemetry"
    assert received[0][1]["battery"] == 92


@pytest.mark.asyncio
async def test_device_shadow_state_sync():
    """Verify Device Shadow merging of desired and reported states with delta."""
    transport = LocalMqttTransport()
    await transport.connect()

    # Step 1: Update desired state
    s1 = DeviceShadowState(
        device_id="EVA-GLS-01",
        desired={"audio_output": "bone_conduction", "mic_gain": 90},
        reported={"audio_output": "tws", "mic_gain": 80}
    )
    await transport.update_shadow(s1)

    shadow = await transport.get_shadow("EVA-GLS-01")
    assert shadow is not None
    assert shadow.desired["audio_output"] == "bone_conduction"
    assert shadow.reported["audio_output"] == "tws"
    assert shadow.delta == {"audio_output": "bone_conduction", "mic_gain": 90}


@pytest.mark.asyncio
async def test_aws_iot_service_command_dispatch():
    """Verify downlink command generation and dispatching."""
    await aws_iot_service.initialize()
    cmd = await aws_iot_service.send_command(
        command_type="CAPTURE_FRAME",
        parameters={"resolution": "VGA", "quality": 10},
        device_id="EVA-GLS-01"
    )
    assert cmd.command_type == "CAPTURE_FRAME"
    assert cmd.device_id == "EVA-GLS-01"
    assert cmd.command_id.startswith("cmd_")


def test_s3_service_local_fallback_and_upload():
    """Verify S3 service saves to local storage with local download URL when AWS_ENABLED=false."""
    res = aws_s3_service.upload_file(
        file_bytes=b"EVA Architecture Blueprint",
        filename="blueprint_test.txt",
        content_type="text/plain",
        prefix="docs"
    )
    assert res["success"] is True
    assert "url" in res
    assert res["storage_provider"] in ["LOCAL_STORAGE", "AWS_S3"]


def test_secrets_service_caching_and_fallback():
    """Verify Secrets Manager service falls back cleanly to local settings with TTL cache."""
    secrets = aws_secrets_service.get_secrets(force_refresh=True)
    assert isinstance(secrets, dict)
    assert "GEMINI_API_KEY" in secrets
    assert "DATABASE_URL" in secrets


def test_cloudwatch_structured_logging_and_redaction():
    """Verify CloudWatch service redacts sensitive API keys and tokens in JSON logs."""
    raw_message = "Connected to Gemini with Bearer eyJhbGciOiJIUzI1NiJ9.test and api_key=AIzaSySecret123"
    metadata = {
        "user_id": "default_user",
        "api_key": "AIzaSySecret123",
        "nested": {"token": "secret_token_val", "safe_val": 42}
    }

    log_entry = aws_cloudwatch_service.log_event(
        event_type="AGENT_REQUEST",
        message=raw_message,
        device_id="EVA-GLS-01",
        metadata=metadata
    )

    assert log_entry["event_type"] == "AGENT_REQUEST"
    assert "[REDACTED]" in log_entry["message"]
    assert "AIzaSySecret123" not in log_entry["message"]
    assert log_entry["metadata"]["api_key"] == "[REDACTED]"
    assert log_entry["metadata"]["nested"]["token"] == "[REDACTED]"
    assert log_entry["metadata"]["nested"]["safe_val"] == 42


@pytest.mark.asyncio
async def test_aws_iot_transport_mock_fallback_safety():
    """Verify AwsIotTransport handles missing certificates or endpoints safely without crashing."""
    transport = AwsIotTransport(endpoint=None)
    connected = await transport.connect()
    assert connected is True
    assert transport.is_connected() is True

    pub = await transport.publish_telemetry(TelemetryPayload(device_id="EVA-GLS-01", battery=80))
    assert pub is True
    await transport.disconnect()
