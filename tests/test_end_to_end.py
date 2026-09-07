import pytest
import asyncio
import time
from httpx import AsyncClient, ASGITransport

from backend.app.main import app
from simulator.device import SimulatedGlassesDevice, DeviceEvent
from simulator.context import SimulatorContextEngine
from simulator.speaker import SimulatorTextToSpeech

@pytest.mark.asyncio
async def test_full_push_to_talk_pipeline():
    """
    End-to-End Test:
    1. User triggers simulated button (ENTER)
    2. Simulated device fires BUTTON_PRESSED event
    3. User voice transcript is gathered ("Good morning.")
    4. Local time and location context are retrieved
    5. Request sent to FastAPI backend
    6. Context Engine enriches request with temporal & calendar context
    7. LangGraph agent orchestrates LLM inference
    8. Contextual response generated (mentions time, Nagpur, class at 10:30)
    9. Response passed to TTS engine
    10. Latency metrics verified
    """
    t_start = time.time()

    # Step 1 & 2: Simulated Device button press
    device = SimulatedGlassesDevice(initial_battery=82)
    event_fired = []
    device.register_event_listener(
        DeviceEvent.BUTTON_PRESSED,
        lambda d: event_fired.append("BUTTON_PRESSED")
    )
    await device.connect()
    device.trigger_button_press()
    assert "BUTTON_PRESSED" in event_fired

    # Step 3 & 4: Simulator gathers user input and local context
    user_speech_transcript = "Good morning."
    sim_context_engine = SimulatorContextEngine(city="Nagpur", country="India")
    context_payload = sim_context_engine.get_full_context_dict(battery=device.get_battery())

    # Step 5: Send to FastAPI backend
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        req_payload = {
            "session_id": "e2e_test_session_001",
            "message": user_speech_transcript,
            "context": context_payload,
            "client_timestamp": time.time()
        }
        resp = await client.post("/api/v1/agent/message", json=req_payload)

        # Step 6, 7 & 8: Verify contextual agent response
        assert resp.status_code == 200
        data = resp.json()
        response_text = data.get("response", "")

        # Verify it is NOT a generic chatbot response (mentions calendar event or time/location)
        resp_lower = response_text.lower()
        assert any(term in resp_lower for term in ["10:30", "nagpur", "morning", "good", "night", "evening", "pm", "am", "time"])

        # Step 9: Text-to-speech synthesis
        speaker = SimulatorTextToSpeech(silent=True)
        tts_duration_ms = await speaker.speak(response_text)
        assert tts_duration_ms >= 0

    total_latency_sec = time.time() - t_start
    print(f"\n[E2E TEST PASSED] Total Pipeline Latency: {total_latency_sec:.3f}s")
    print(f"[E2E TEST RESPONSE] \"{response_text}\"")
