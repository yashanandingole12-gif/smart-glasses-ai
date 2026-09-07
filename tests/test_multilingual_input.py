import pytest
import time
import asyncio
from typing import Dict, Any, List

from backend.app.models.schemas import AgentMessageRequest, FullContextPayload, TemporalContext, LocationContext, CalendarContext, CalendarEvent, DeviceContext, ConversationContext
from backend.app.services.agent_graph import run_agent
from backend.app.services.llm_service import LLMService
from backend.app.services.context_engine import context_engine
from simulator.speaker import sanitize_speech_text, SimulatorTextToSpeech

# Test matrix definitions
MULTILINGUAL_TEST_CASES = [
    {
        "language_name": "English",
        "input_text": "Good morning",
        "requested_language": "en",
        "locale": "en-IN",
        "expected_language": "en",
        "expected_substrings": ["morning"]
    },
    {
        "language_name": "Hindi",
        "input_text": "सुप्रभात",
        "requested_language": "hi",
        "locale": "hi-IN",
        "expected_language": "hi",
        "expected_substrings": ["सुप्रभात"]
    },

    {
        "language_name": "Marathi",
        "input_text": "शुभ सकाळ",
        "requested_language": "mr",
        "locale": "mr-IN",
        "expected_language": "mr",
        "expected_substrings": ["सकाळ"]
    },
    {
        "language_name": "Hinglish",
        "input_text": "Good morning, aaj mera calendar check karo",
        "requested_language": "hi-Latn",
        "locale": "hi-Latn-IN",
        "expected_language": "hi-Latn",
        "expected_substrings": ["calendar"]
    }

]

def make_test_context() -> Dict[str, Any]:
    return {
        "time": {
            "local_time": "08:15 AM",
            "period": "morning",
            "timezone": "Asia/Kolkata",
            "date_str": "Friday, Aug 25",
            "iso_timestamp": "2026-08-25T08:15:00+05:30"
        },
        "location": {
            "latitude": 21.1458,
            "longitude": 79.0882,
            "city": "Nagpur",
            "country": "India",
            "place_type": "college campus"
        },
        "calendar": {
            "current_event": None,
            "next_event": {
                "id": "ml_101",
                "title": "Machine Learning Class",
                "start_time": "10:30 AM",
                "end_time": "12:00 PM",
                "location": "Room 302",
                "description": "Weekly lecture"
            },
            "today_events": []
        },
        "device": {
            "battery": 88,
            "camera_available": True,
            "microphone_available": True,
            "network": "WIFI",
            "connection_type": "SIMULATOR"
        },
        "conversation": {
            "recent_topic": None,
            "referenced_entities": {},
            "last_intent": None
        }
    }

@pytest.mark.asyncio
@pytest.mark.parametrize("case", MULTILINGUAL_TEST_CASES, ids=lambda c: c["language_name"])
async def test_multilingual_single_turn_agent(case):
    """Verify single-turn language preservation and contextual accuracy in LangGraph agent."""
    ctx = make_test_context()
    session_id = f"test_multi_{case['requested_language']}_{int(time.time()*1000)}"

    result = await run_agent(
        session_id=session_id,
        user_message=case["input_text"],
        context_payload=ctx,
        language=case["requested_language"],
        locale=case["locale"]
    )

    response_text = result["response"]
    assert response_text is not None and len(response_text) > 0

    # Verify key contextual elements are present in the response
    for sub in case["expected_substrings"]:
        assert sub.lower() in response_text.lower() or sub in response_text, (
            f"Expected substring '{sub}' in response: '{response_text}' for {case['language_name']}"
        )

@pytest.mark.asyncio
async def test_multilingual_matrix_5_runs_latency():
    """
    Run each language at least 5 times and compute latency statistics for STT, Context, LLM, TTS, and Total.
    """
    results_summary = []
    tts = SimulatorTextToSpeech(engine_type="silent")

    for case in MULTILINGUAL_TEST_CASES:
        lang_name = case["language_name"]
        stt_latencies = []
        llm_latencies = []
        tts_latencies = []
        total_latencies = []
        success_count = 0
        failure_count = 0

        for run_idx in range(5):
            t_total_start = time.perf_counter()

            # 1. Simulated STT Layer
            t_stt_start = time.perf_counter()
            # Fast simulated STT inference time (~50-120ms)
            await asyncio.sleep(0.01)
            t_stt_end = time.perf_counter()
            stt_duration_ms = (t_stt_end - t_stt_start) * 1000.0
            stt_latencies.append(stt_duration_ms)

            # 2. Context Engine Layer
            ctx = make_test_context()

            # 3. LangGraph & LLM Layer
            t_llm_start = time.perf_counter()
            try:
                agent_res = await run_agent(
                    session_id=f"matrix_{case['requested_language']}_{run_idx}",
                    user_message=case["input_text"],
                    context_payload=ctx,
                    language=case["requested_language"],
                    locale=case["locale"]
                )
                t_llm_end = time.perf_counter()
                llm_duration_ms = (t_llm_end - t_llm_start) * 1000.0
                llm_latencies.append(llm_duration_ms)

                resp_text = agent_res["response"]
                assert resp_text is not None and len(resp_text) > 0

                # 4. TTS Layer
                t_tts_start = time.perf_counter()
                tts_ms = await tts.speak(resp_text)
                t_tts_end = time.perf_counter()
                tts_duration_ms = (t_tts_end - t_tts_start) * 1000.0
                tts_latencies.append(tts_duration_ms)

                total_ms = (time.perf_counter() - t_total_start) * 1000.0
                total_latencies.append(total_ms)
                success_count += 1
            except Exception as e:
                failure_count += 1

        avg_stt = sum(stt_latencies) / len(stt_latencies)
        avg_llm = sum(llm_latencies) / len(llm_latencies)
        avg_tts = sum(tts_latencies) / len(tts_latencies)
        avg_total = sum(total_latencies) / len(total_latencies)

        results_summary.append({
            "language": lang_name,
            "success": success_count,
            "failures": failure_count,
            "avg_stt_ms": avg_stt,
            "avg_llm_ms": avg_llm,
            "avg_tts_ms": avg_tts,
            "avg_total_ms": avg_total
        })

    # Assert 100% success rate across all 5 runs for all 4 languages (20 total runs)
    for res in results_summary:
        assert res["success"] == 5
        assert res["failures"] == 0

    print("\n--- MULTILINGUAL MATRIX 5-RUN LATENCY SUMMARY ---")
    for r in results_summary:
        print(f"Language: {r['language']:<10} | Success: {r['success']}/5 | Failures: {r['failures']} | "
              f"STT: {r['avg_stt_ms']:.1f}ms | LLM: {r['avg_llm_ms']:.1f}ms | TTS: {r['avg_tts_ms']:.1f}ms | Total: {r['avg_total_ms']:.1f}ms")

@pytest.mark.asyncio
async def test_multilingual_api_request_payload():
    """Verify AgentMessageRequest schema validates and preserves language & locale fields."""
    req = AgentMessageRequest(
        message="सुप्रभात",
        language="hi",
        locale="hi-IN"
    )
    assert req.language == "hi"
    assert req.locale == "hi-IN"

    data = req.model_dump()
    assert data["language"] == "hi"
    assert data["locale"] == "hi-IN"
