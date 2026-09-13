import pytest
import io
import struct
import base64
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.math_engine import math_engine
from backend.app.services.vision_service import vision_service
from backend.app.services.hardware_bridge import hardware_bridge

client = TestClient(app)

# ==============================================================================
# 1. DETERMINISTIC QUADRATIC EQUATION SOLVER TESTS
# ==============================================================================

def test_quadratic_two_real_roots():
    # x^2 + 5x + 6 = 0 -> roots: -3, -2
    res = math_engine.evaluate("x^2 + 5x + 6 = 0")
    assert res is not None
    assert res["operation"] == "quadratic_equation"
    assert res["root_type"] == "two_real"
    assert -3.0 in res["roots"]
    assert -2.0 in res["roots"]
    assert "x equals -3" in res["text_response"]
    assert "x equals -2" in res["text_response"]
    # Verify zero LaTeX
    assert "$" not in res["text_response"]
    assert "\\" not in res["text_response"]


def test_quadratic_with_coefficients():
    # 2x^2 - 4x - 6 = 0 -> 2(x^2 - 2x - 3) = 0 -> (x-3)(x+1) = 0 -> roots: -1, 3
    res = math_engine.evaluate("2x^2 - 4x - 6 = 0")
    assert res is not None
    assert res["operation"] == "quadratic_equation"
    assert res["root_type"] == "two_real"
    assert -1.0 in res["roots"]
    assert 3.0 in res["roots"]
    assert len(res["steps"]) >= 4


def test_quadratic_single_repeated_root():
    # x^2 - 4x + 4 = 0 -> (x-2)^2 = 0 -> root: 2
    res = math_engine.evaluate("x^2 - 4x + 4 = 0")
    assert res is not None
    assert res["operation"] == "quadratic_equation"
    assert res["root_type"] == "repeated_real"
    assert res["roots"] == [2.0]
    assert "x equals 2" in res["text_response"]


def test_quadratic_complex_roots():
    # x^2 + 4 = 0 -> x = +- 2i
    res = math_engine.evaluate("x^2 + 4 = 0")
    assert res is not None
    assert res["operation"] == "quadratic_equation"
    assert res["root_type"] == "complex"
    assert "complex solutions" in res["text_response"]
    assert "2 i" in res["text_response"]


def test_quadratic_spoken_normalization():
    # Spoken: "solve 3x squared plus 6x minus 9 equals 0"
    res = math_engine.evaluate("solve 3x squared plus 6x minus 9 equals 0")
    assert res is not None
    assert res["operation"] == "quadratic_equation"
    # 3x^2 + 6x - 9 = 0 -> x^2 + 2x - 3 = 0 -> (x+3)(x-1) = 0 -> roots: -3, 1
    assert -3.0 in res["roots"]
    assert 1.0 in res["roots"]


def test_quadratic_non_zero_rhs():
    # x^2 + 3x = 10 -> x^2 + 3x - 10 = 0 -> (x+5)(x-2) = 0 -> roots: -5, 2
    res = math_engine.evaluate("x^2 + 3x = 10")
    assert res is not None
    assert res["operation"] == "quadratic_equation"
    assert -5.0 in res["roots"]
    assert 2.0 in res["roots"]


# ==============================================================================
# 2. ESP32 DIGITAL MIC WAV RECORDING & AUDIO HEADER TESTS
# ==============================================================================

def test_esp32_audio_recording_wav_structure():
    audio_res = hardware_bridge.record_esp32_audio(duration_ms=1000)
    assert audio_res["status"] == "success"
    assert audio_res["format"] == "audio/wav"
    assert audio_res["sample_rate"] == 16000
    assert audio_res["channels"] == 1
    
    raw_bytes = base64.b64decode(audio_res["base64_data"])
    assert len(raw_bytes) >= 44
    assert raw_bytes[:4] == b"RIFF"
    assert raw_bytes[8:12] == b"WAVE"
    assert raw_bytes[12:16] == b"fmt "


def test_esp32_audio_transcription_service():
    # Test audio transcription with valid WAV bytes
    silence_wav = hardware_bridge._generate_fallback_wav(1000)
    trans_res = vision_service.transcribe_audio_from_esp32(silence_wav)
    assert trans_res["status"] == "success"
    assert "transcript" in trans_res


# ==============================================================================
# 3. VISION SERVICE: QR SCANNING, OCR, AND LANGUAGE TRANSCRIPTION
# ==============================================================================

def test_vision_qr_scan():
    dummy_img = b"\xff\xd8\xff\xe0" + b"\x00" * 100
    qr_res = vision_service.scan_qr_code(dummy_img)
    assert qr_res["status"] == "success"
    assert "speech_response" in qr_res
    assert "$" not in qr_res["speech_response"]


def test_vision_equation_extraction():
    dummy_img = b"\xff\xd8\xff\xe0" + b"\x00" * 100
    eq_res = vision_service.extract_equation_from_image(dummy_img)
    assert eq_res["status"] == "success"
    assert "equation" in eq_res


def test_vision_language_transcription():
    dummy_img = b"\xff\xd8\xff\xe0" + b"\x00" * 100
    trans_res = vision_service.transcribe_language_from_image(dummy_img)
    assert trans_res["status"] == "success"
    assert "spoken_summary" in trans_res


# ==============================================================================
# 4. FASTAPI HARDWARE & MULTIMODAL API ENDPOINTS
# ==============================================================================

def test_api_hardware_multimodal_capture():
    resp = client.post("/api/v1/hardware/multimodal/capture", params={"duration_ms": 1000, "override_query": "solve this equation"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["mode"] == "quadratic_math_solver"
    assert "speech_response" in data
    assert "extracted_equation" in data


def test_api_vision_qr_scan():
    resp = client.post("/api/v1/vision/qr/scan")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "speech_response" in data


def test_api_vision_equation_solve():
    resp = client.post("/api/v1/vision/equation/solve", params={"equation_override": "2x^2 - 8 = 0"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["math_solution"]["operation"] == "quadratic_equation"
    assert -2.0 in data["math_solution"]["roots"]
    assert 2.0 in data["math_solution"]["roots"]


def test_api_hardware_mic_record():
    resp = client.post("/api/v1/hardware/mic/record", params={"duration_ms": 1000})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["format"] == "audio/wav"
    assert data["sample_rate"] == 16000
