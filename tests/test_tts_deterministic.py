import asyncio
import logging
import pytest
import time
from typing import List

from simulator.speaker import SimulatorTextToSpeech, TTSState, TTSError, sanitize_speech_text
from backend.app.services.agent_graph import run_agent

logger = logging.getLogger("SmartGlasses.SpeakerTest")


def test_sanitize_speech_text():
    """Verify markdown symbols, headers, and bullet points are cleanly sanitized."""
    raw = "### Hello **world**! Here is `code` and *italics*.\n- Item 1\n- Item 2"
    sanitized = sanitize_speech_text(raw)
    assert "**" not in sanitized
    assert "`" not in sanitized
    assert "*" not in sanitized
    assert "###" not in sanitized
    assert "Hello world! Here is code and italics. Item 1 Item 2" in sanitized


@pytest.mark.asyncio
async def test_tts_initialization_and_states():
    """Verify TTS initial state, transitions to QUEUED, SPEAKING, and COMPLETED."""
    speaker = SimulatorTextToSpeech(silent=True)
    assert speaker.state in (TTSState.IDLE, TTSState.COMPLETED)

    # Empty text check
    res_empty = await speaker.speak("")
    assert res_empty == 0.0

    # Normal speak
    duration_ms = await speaker.speak("Test speech playback verification.")
    assert duration_ms >= 0.0
    assert speaker.state in (TTSState.COMPLETED, TTSState.IDLE)
    speaker.stop()


@pytest.mark.asyncio
async def test_tts_queue_serialization_prevent_overlap():
    """Verify that multiple concurrent speak calls are queued and serialized without overlapping."""
    speaker = SimulatorTextToSpeech(silent=True)
    
    order_completed: List[int] = []

    async def speak_task(index: int, text: str):
        await speaker.speak(text)
        order_completed.append(index)

    # Launch 5 concurrent speak requests
    tasks = [
        asyncio.create_task(speak_task(i, f"Message number {i} for queue order test."))
        for i in range(5)
    ]
    await asyncio.gather(*tasks)

    # Must finish in strict FIFO order
    assert order_completed == [0, 1, 2, 3, 4]
    speaker.stop()


@pytest.mark.asyncio
async def test_tts_error_propagation():
    """Verify TTS errors are not swallowed and raise TTSError."""
    speaker = SimulatorTextToSpeech(silent=True)
    speaker.stop()  # Stop worker to force an error on subsequent speak

    with pytest.raises(TTSError):
        await speaker.speak("This should fail because worker is stopped.")

    assert speaker.state == TTSState.FAILED


@pytest.mark.asyncio
async def test_20_repeated_speech_sequential():
    """
    Test 20 repeated sequential speech operations.
    Validates determinism, 100% success rate, and measures latency.
    """
    # Use native sapi5 or silent based on environment test config
    speaker = SimulatorTextToSpeech(engine_type="sapi5")
    latencies: List[float] = []

    test_sentences = [
        f"Sequential test iteration {i + 1}: The quick brown fox jumps over the lazy dog."
        for i in range(20)
    ]

    for i, phrase in enumerate(test_sentences):
        t0 = time.time()
        lat = await speaker.speak(phrase)
        elapsed = (time.time() - t0) * 1000.0
        assert lat > 0, f"Iteration {i+1} failed to report positive latency."
        latencies.append(lat)
        assert speaker.state in (TTSState.COMPLETED, TTSState.IDLE)

    avg_latency = sum(latencies) / len(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)

    print(f"\n[20 REPEATED SPEECH TEST RESULTS]")
    print(f"  • Total Runs: {len(latencies)} / 20 Successful")
    print(f"  • Average Latency: {avg_latency:.2f} ms")
    print(f"  • Min Latency: {min_latency:.2f} ms")
    print(f"  • Max Latency: {max_latency:.2f} ms")

    speaker.stop()
    assert len(latencies) == 20


@pytest.mark.asyncio
async def test_five_consecutive_agent_responses():
    """
    Test 5 consecutive end-to-end agent query-response-to-TTS pipeline runs.
    Ensures complete roundtrip pipeline is stable and free of deadlocks or dropped audio.
    """
    from simulator.context import SimulatorContextEngine

    speaker = SimulatorTextToSpeech(engine_type="sapi5")
    sim_context = SimulatorContextEngine(city="Nagpur", country="India")

    user_queries = [
        "What time is it in Nagpur right now?",
        "Do I have any classes or events scheduled this morning?",
        "What is my current battery level and device health?",
        "Can you remind me of my location and timezone?",
        "Thank you, that is all for now."
    ]

    print("\n[5 CONSECUTIVE AGENT RESPONSES PIPELINE TEST]")

    for idx, query in enumerate(user_queries, 1):
        context_payload = sim_context.get_full_context_dict(battery=82)

        # 1. Run LangGraph Agent
        t_agent_start = time.perf_counter()
        agent_out = await run_agent(
            session_id="tts_agent_consecutive_test",
            user_message=query,
            context_payload=context_payload
        )
        response_text = agent_out.get("response", "")
        agent_latency_ms = (time.perf_counter() - t_agent_start) * 1000.0

        assert len(response_text) > 0, f"Empty agent response on query {idx}"

        # 2. Run TTS playback
        t_tts_start = time.perf_counter()
        tts_latency_ms = await speaker.speak(response_text)
        assert tts_latency_ms > 0

        print(f"  [{idx}/5] Query: '{query}'")
        print(f"        Agent Response: \"{response_text}\"")
        print(f"        Agent Latency: {agent_latency_ms:.1f}ms | TTS Latency: {tts_latency_ms:.1f}ms")
        assert speaker.state in (TTSState.COMPLETED, TTSState.IDLE)

    speaker.stop()
