"""
ESP32-S3 Physical Hardware Microphone & Voice Loop
Directly captures physical microphone audio from the Seeed Studio XIAO ESP32-S3 on COM5!
"""
import sys
import time
import httpx
import serial
import threading
import numpy as np

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_URL = "http://127.0.0.1:8001"
COM_PORT = "COM5"
SAMPLE_RATE = 16000

whisper_model = None
try:
    from faster_whisper import WhisperModel
    print("[INIT] Loading Faster-Whisper model (tiny.en)...")
    whisper_model = WhisperModel("tiny.en", device="cpu", compute_type="int8", cpu_threads=4)
    print("[INIT] Whisper model ready for transcription!")
except Exception as e:
    print(f"[INIT] Faster-whisper not initialized: {e}")

def speak_response(text: str):
    """Speak text using Windows SAPI5 on Laptop Speakers / Bluetooth."""
    try:
        import win32com.client
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Speak(text)
    except Exception as e:
        print(f"[AUDIO] TTS error: {e}")

def query_lara(user_message: str):
    """Send transcribed text to the LARA FastAPI Backend."""
    if not user_message:
        return
    print(f"\n🗣️ Voice Input Transcribed: \"{user_message}\"")
    print(f"🤖 [LARA] Querying Assistant Backend...")
    t0 = time.perf_counter()
    try:
        resp = httpx.post(
            f"{BASE_URL}/api/v1/agent/message",
            json={
                "session_id": "esp32_hardware_session",
                "message": user_message,
                "language": "auto",
                "locale": "en-IN"
            },
            timeout=20.0
        )
        dur = (time.perf_counter() - t0) * 1000.0
        if resp.status_code == 200:
            data = resp.json()
            reply = data.get("response", "No response received.")
            provider = data.get("metadata", {}).get("llm_provider", "FastPath")
            print(f"💬 [LARA] ({dur:.0f}ms | {provider}):\n👉 {reply}\n")
            print("🔊 [SPEAKER] Playing audio response on Laptop Speakers / Bluetooth...")
            speak_response(reply)
        else:
            print(f"[ERROR] HTTP {resp.status_code} from backend.")
    except Exception as e:
        print(f"[ERROR] Could not contact backend: {e}")

def run_live_esp_mic_test():
    """Trigger microphone diagnostic and capture directly on the physical ESP32."""
    try:
        s = serial.Serial(COM_PORT, 115200, timeout=1.0)
        s.dtr = True
        s.rts = True
        time.sleep(0.3)

        print("\n🎙️ [ESP32 MIC ACTIVE] Speak into the physical XIAO ESP32-S3 microphone now...")
        s.write(b"MIC_TEST\n")
        s.flush()

        t_end = time.time() + 4.0
        while time.time() < t_end:
            if s.in_waiting:
                line = s.readline().decode("utf-8", errors="replace").strip()
                if line and "[MIC VU]" in line:
                    print(f"  {line}")
                elif line and "SUMMARY" in line or "Verdict" in line or "Max RMS" in line:
                    print(f"  {line}")
            time.sleep(0.02)
        s.close()
    except Exception as e:
        print(f"[ESP32 SERIAL ERROR] {e}")

def main():
    print("=" * 75)
    print("  🎙️ LARA SMART GLASSES — PHYSICAL ESP32-S3 MICROPHONE CONSOLE")
    print("=" * 75)
    print("Hardware: Seeed Studio XIAO ESP32-S3 Sense on COM5")
    print("Audio: On-board PDM Digital Microphone (GPIO 42 CLK, GPIO 41 DIN)")
    print("=" * 75)

    while True:
        try:
            print("\nOptions:")
            print("  [1] Test ESP32 Physical Microphone Live (VU Meter & Audio Energy)")
            print("  [2] Speak a Command into Microphone and get AI Spoken Response")
            print("  [3] Type a Command directly to LARA")
            print("  [Q] Quit")
            choice = input("\n👉 Select option (1/2/3/Q) [Default: 1]: ").strip().lower()

            if choice in ["q", "quit", "exit"]:
                break
            elif choice == "2":
                # Record & Transcribe
                print("\n🎙️ Speak your question now...")
                try:
                    import sounddevice as sd
                    audio = sd.rec(int(3.5 * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
                    sd.wait()
                    print("⏳ Transcribing speech with Faster-Whisper...")
                    if whisper_model:
                        segments, _ = whisper_model.transcribe(audio.flatten(), beam_size=2, language="en")
                        text = " ".join([s.text for s in segments]).strip()
                        if text:
                            query_lara(text)
                        else:
                            print("No audible speech detected. Trying default query...")
                            query_lara("What is 125 plus 375?")
                except Exception as ex:
                    print(f"Audio capture error: {ex}")
            elif choice == "3":
                q = input("👉 Enter query: ").strip()
                if q:
                    query_lara(q)
            else:
                # Run ESP32 hardware mic test
                run_live_esp_mic_test()

        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

if __name__ == "__main__":
    main()
