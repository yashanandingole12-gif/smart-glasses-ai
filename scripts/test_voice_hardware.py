import asyncio
import time
import sys
from pathlib import Path

# Set console encoding to UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from simulator.microphone import SimulatorSpeechToText
from simulator.speaker import SimulatorTextToSpeech

async def main():
    print("=" * 60)
    print("Smart Glasses AI - Real Laptop Voice Hardware Diagnostic")
    print("=" * 60)

    print("\n1. Testing Text-to-Speech (Laptop Speakers)...")
    speaker = SimulatorTextToSpeech(engine_type="sapi5")
    test_phrase = "Smart Glasses voice pipeline initialized. Testing microphone next."
    tts_ms = await speaker.speak(test_phrase)
    print(f"   [OK] TTS Spoken: '{test_phrase}'")
    print(f"   [OK] Measured TTS Latency: {tts_ms:.1f}ms")

    print("\n2. Testing Speech-to-Text (Laptop Microphone)...")
    print("   [*] Recording 3 seconds from default microphone... Please speak now!")
    mic = SimulatorSpeechToText(engine_type="faster_whisper")
    transcript, stt_ms = await mic.transcribe_from_microphone(duration_sec=3.0)
    print(f"   [OK] Captured & Transcribed: '{transcript}'")
    print(f"   [OK] Measured STT Latency: {stt_ms:.1f}ms")

    print("\n3. Testing Voice Pipeline Echo...")
    reply_phrase = f"I heard you say: {transcript}"
    print(f"   [*] Speaking: '{reply_phrase}'")
    echo_tts_ms = await speaker.speak(reply_phrase)

    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY:")
    print(f"   - STT Latency: {stt_ms:.1f}ms")
    print(f"   - TTS Latency: {tts_ms:.1f}ms")
    print("   - Voice Hardware Status: OPERATIONAL")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
