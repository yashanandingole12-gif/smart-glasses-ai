"""
EVA Smart Glasses - Live Interactive Command-Line Audio & Voice Tester
Connects to ESP32-S3 on COM7, streams microphone telemetry, visualizes live voice levels,
captures speech, queries EVA AI backend, and speaks responses aloud through TWS/PC speakers.
"""

import sys
import time
import json
import serial
import pyttsx3
import requests
import threading

PORT = "COM7"
BAUD = 115200
BACKEND_URL = "http://127.0.0.1:8001"

# Initialize local TTS engine for immediate audio feedback
try:
    tts_engine = pyttsx3.init()
    tts_engine.setProperty('rate', 175)
except Exception:
    tts_engine = None

def speak_audio(text: str):
    print(f"\n🔊 [EVA SPEAKING]: {text}\n")
    if tts_engine:
        try:
            tts_engine.say(text)
            tts_engine.runAndWait()
        except Exception:
            pass

def print_header():
    print("=" * 65)
    print("  🎙️  EVA SMART GLASSES - LIVE HARDWARE & VOICE TEST CONSOLE  🎙️")
    print("=" * 65)
    print(f" Port: {PORT} @ {BAUD} baud | Backend: {BACKEND_URL}")
    print("-----------------------------------------------------------------")
    print(" Instructions:")
    print("   1. Speak directly into the ESP32-S3 microphone.")
    print("   2. Watch the live ASCII audio VU-meter react to your voice.")
    print("   3. Type 'w' + Enter to simulate Voice Wake / Button PTT.")
    print("   4. Type 'q' + Enter to query EVA AI manually.")
    print("   5. Type 's' + Enter to check full hardware status.")
    print("   6. Press Ctrl+C to exit.")
    print("=" * 65)
    print()

def main():
    print_header()

    try:
        ser = serial.Serial(PORT, BAUD, timeout=0.5)
        time.sleep(1.0)
        print(f"✅ Connected to ESP32-S3 on {PORT}!\n")
    except Exception as e:
        print(f"❌ Could not open {PORT}: {e}")
        print("Please verify the board is plugged in or check Device Manager for the COM port.")
        sys.exit(1)

    running = True

    def serial_listener():
        while running:
            try:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if not line:
                    continue

                if "VOICE WAKE" in line or "TALK_START" in line:
                    print(f"\n🚨 [WAKE DETECTED]: {line}")
                    print("🎤 >> ESP32 Microphone is actively recording your voice...")

                elif "MIC_STREAM" in line:
                    # Parse JSON or display meter
                    try:
                        data_str = line.split("MIC_STREAM", 1)[1].strip()
                        data = json.loads(data_str)
                        rms = data.get("rms", 0.0)
                        bars = min(30, int(rms / 100.0))
                        meter = "█" * bars + "░" * (30 - bars)
                        speech_tag = "🗣️ VOICE DETECTED" if data.get("speech") else "   ambient"
                        print(f"\r[MIC LEVEL] [{meter}] RMS: {rms:6.1f} | {speech_tag}", end="", flush=True)
                    except Exception:
                        print(f"\n{line}")

                elif "HEARTBEAT" in line:
                    # Clean periodic telemetry
                    pass
                else:
                    print(f"\n[ESP32]: {line}")

            except Exception as ex:
                if running:
                    print(f"\n[SERIAL NOTICE]: {ex}")
                    time.sleep(0.5)

    listener_thread = threading.Thread(target=serial_listener, daemon=True)
    listener_thread.start()

    # Interactive Command Loop
    while True:
        try:
            cmd = input().strip()
            if not cmd:
                continue

            if cmd.lower() in ['exit', 'quit', 'x']:
                break
            elif cmd.lower() in ['w', 'wake', 'talk']:
                print("\n>> Triggering Voice Wake on ESP32...")
                ser.write(b"WAKE\n")
            elif cmd.lower() in ['s', 'status', 'ping']:
                ser.write(b"STATUS\n")
            elif cmd.lower() in ['1', 'chime']:
                ser.write(b"1\n")
            elif cmd.lower().startswith('q ') or cmd.lower() == 'q':
                query = cmd[2:].strip() if cmd.lower().startswith('q ') else input("Enter question for EVA: ").strip()
                if query:
                    print(f"\n>> Sending query to EVA: '{query}'...")
                    try:
                        resp = requests.post(
                            f"{BACKEND_URL}/api/v1/agent/message",
                            json={"session_id": "test_session", "message": query},
                            timeout=8.0
                        )
                        if resp.status_code == 200:
                            ans = resp.json().get("response", "No response.")
                            speak_audio(ans)
                        else:
                            print(f"❌ Backend Error ({resp.status_code}): {resp.text}")
                    except Exception as err:
                        print(f"❌ Backend Connection Error: {err}")
            else:
                ser.write(f"{cmd}\n".encode('utf-8'))

        except KeyboardInterrupt:
            print("\nExiting...")
            break

    running = False
    ser.close()
    print("Console closed.")

if __name__ == "__main__":
    main()
