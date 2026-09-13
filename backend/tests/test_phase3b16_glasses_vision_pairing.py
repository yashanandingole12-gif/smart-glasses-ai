import io
import time
import base64
import hashlib
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.vision_service import vision_service
from backend.app.services.conversation_context_engine import conversation_context_engine
from backend.app.services.smart_glass_formatter import smart_glass_formatter
from backend.app.services.follow_up_resolver import follow_up_resolver
from backend.app.services.hardware_bridge import hardware_bridge
from backend.app.services.agent_graph import run_agent

client = TestClient(app)

def _create_test_jpeg(width: int = 640, height: int = 480, color: tuple = (70, 130, 180)) -> bytes:
    """Generates a valid test JPEG image buffer."""
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def test_vision_jpeg_validation_and_identity():
    """Verify that JPEG validation extracts dimensions, mime type, and sha256 checksum."""
    jpeg_bytes = _create_test_jpeg(640, 480)
    val_res = vision_service.validate_image(jpeg_bytes)

    assert val_res["valid"] is True
    assert val_res["width"] == 640
    assert val_res["height"] == 480
    assert val_res["format"] == "JPEG"
    assert val_res["mime_type"] == "image/jpeg"
    assert val_res["byte_size"] == len(jpeg_bytes)
    assert val_res["checksum"] == hashlib.sha256(jpeg_bytes).hexdigest()
    assert val_res["state"] == "IMAGE_VALIDATED"

def test_vision_corrupted_image_failure_diagnostics():
    """Verify that corrupted or empty image buffers fail gracefully with diagnostic state."""
    corrupt_bytes = b"NOT_A_VALID_JPEG_IMAGE_HEADER"
    val_res = vision_service.validate_image(corrupt_bytes)
    assert val_res["valid"] is False
    assert val_res["state"] == "INVALID_IMAGE"

    analyze_res = vision_service.analyze_image(corrupt_bytes, user_query="What do you see?")
    assert analyze_res["status"] == "error"
    assert analyze_res["pipeline_state"] == "INVALID_IMAGE"

def test_vision_analyze_structured_response_and_identity():
    """Verify analyze_image returns structured fields, preserved capture_id, and metadata."""
    jpeg_bytes = _create_test_jpeg(640, 480)
    session_id = f"test_vision_sess_{int(time.time())}"
    custom_capture_id = "cap_test_12345"

    res = vision_service.analyze_image(
        image_bytes=jpeg_bytes,
        user_query="What is in front of me?",
        session_id=session_id,
        device_id="SmartGlasses-S3",
        capture_id=custom_capture_id
    )

    assert res["status"] == "success"
    assert res["capture_id"] == custom_capture_id
    assert res["description"] != ""
    assert isinstance(res["objects"], list)
    assert isinstance(res["text_detected"], list)
    assert res["pipeline_state"] == "COMPLETE"
    assert res["metadata"]["checksum"] == hashlib.sha256(jpeg_bytes).hexdigest()

def test_smart_glass_formatter_speech_safety():
    """Verify that spoken responses contain zero markdown, zero LaTeX, zero JSON, and max 3 sentences."""
    raw_desc = "I see **a silver laptop** on the `desk`.\n\nThere is also a phone with $\\alpha=5$ and https://example.com URL.\nExtra sentence four that should be clipped."
    speech = smart_glass_formatter.format_vision_description(
        description=raw_desc,
        objects=["laptop", "phone"],
        requested_aspect="What do you see?"
    )

    assert "**" not in speech
    assert "`" not in speech
    assert "https://" not in speech
    assert "\\alpha" not in speech
    # 1 to 3 sentences
    sentences = [s for s in speech.split(".") if s.strip()]
    assert len(sentences) <= 3

def test_active_vision_context_and_follow_up_questions():
    """Verify active vision context is stored and enables multi-turn follow-ups."""
    session_id = f"test_vision_followup_{int(time.time())}"
    jpeg_bytes = _create_test_jpeg(640, 480, color=(0, 0, 0))

    # 1. First visual request
    res = vision_service.analyze_image(
        image_bytes=jpeg_bytes,
        user_query="Look at this",
        session_id=session_id,
        device_id="SmartGlasses-S3",
        capture_id="cap_followup_999"
    )
    assert res["status"] == "success"

    # Context must now hold active_vision
    ctx = conversation_context_engine.get_session(session_id)
    assert ctx.active_vision is not None
    assert ctx.active_vision["capture_id"] == "cap_followup_999"

    # 2. Follow-up: "What color is it?"
    followup1 = follow_up_resolver.resolve(session_id, "What color is it?")
    assert followup1.is_follow_up is True
    assert followup1.target_capability == "vision"
    assert followup1.direct_answer is not None

    # 3. Follow-up: "Is it a phone?"
    followup2 = follow_up_resolver.resolve(session_id, "Is it a phone?")
    assert followup2.is_follow_up is True
    assert followup2.target_capability == "vision"
    assert followup2.direct_answer is not None

    # 4. Follow-up: "Tell me more"
    followup3 = follow_up_resolver.resolve(session_id, "Tell me more")
    assert followup3.is_follow_up is True
    assert followup3.target_capability == "vision"
    assert "image" in followup3.direct_answer.lower() or "see" in followup3.direct_answer.lower()

def test_api_vision_analyze_endpoint():
    """Verify POST /api/v1/vision/analyze accepts base64 and returns VisionAnalyzeResponse."""
    jpeg_bytes = _create_test_jpeg(320, 240)
    b64_img = base64.b64encode(jpeg_bytes).decode('utf-8')
    session_id = f"api_test_vision_{int(time.time())}"

    payload = {
        "session_id": session_id,
        "image_base64": b64_img,
        "prompt": "What do you see in front of me?",
        "device_id": "SmartGlasses-S3"
    }

    resp = client.post("/api/v1/vision/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == "success"
    assert data["capture_id"] is not None
    assert data["description"] != ""
    assert isinstance(data["objects"], list)
    assert data["provider"] in ["gemini-flash", "local_fallback", "gemini-2.5-flash"]

def test_api_hardware_status_phase3b16_telemetry():
    """Verify GET /api/v1/hardware/status returns Phase 3B.16 wearable metrics."""
    resp = client.get("/api/v1/hardware/status")
    assert resp.status_code == 200
    data = resp.json()

    assert "esp32_connected" in data
    assert "ble_state" in data
    assert "camera_available" in data
    assert "microphone_available" in data
    assert "vision_ready" in data
    assert "last_capture_timestamp" in data
    assert "last_vision_status" in data
    assert data["camera_available"] is True
    assert data["microphone_available"] is True
    assert data["vision_ready"] is True

@pytest.mark.asyncio
async def test_agent_graph_voice_vision_intent():
    """Verify voice vision commands ('what do you see') trigger the vision pipeline directly."""
    session_id = f"test_graph_vision_{int(time.time())}"
    jpeg_bytes = _create_test_jpeg(640, 480)
    b64_img = base64.b64encode(jpeg_bytes).decode('utf-8')

    res = await run_agent(
        session_id=session_id,
        user_message="What do you see?",
        context_payload={"image_base64": b64_img}
    )

    assert res["response"] != ""
    assert len(res["actions"]) == 1
    assert res["actions"][0].tool_name == "vision_analyze"
    assert res["routing_metadata"]["tier_used"] == "FAST"
    assert "capture_id" in res["routing_metadata"]
