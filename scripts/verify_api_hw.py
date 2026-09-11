import requests
import json
import time

def verify_all_endpoints():
    base_url = "http://127.0.0.1:8001"
    print("=== Testing FastAPI Hardware & Voice Endpoints ===")

    # 1. Health
    r = requests.get(f"{base_url}/api/v1/health")
    print(f"[1] Health Check: {r.status_code} -> {r.json()}")

    # 2. Camera Capture
    t0 = time.time()
    r = requests.get(f"{base_url}/api/v1/hardware/camera/capture")
    lat_cam = (time.time() - t0) * 1000
    if r.status_code == 200:
        d = r.json()
        print(f"[2] Camera Capture Endpoint: {r.status_code} -> Size: {d.get('size_bytes')} bytes, Res: {d.get('resolution')}, Driver: {d.get('format')} (HTTP Latency: {lat_cam:.1f}ms)")
    else:
        print(f"[2] Camera Capture Endpoint: {r.status_code} -> {r.text}")

    # 3. Mic Telemetry
    t0 = time.time()
    r = requests.get(f"{base_url}/api/v1/hardware/mic/telemetry")
    lat_mic = (time.time() - t0) * 1000
    if r.status_code == 200:
        d = r.json()
        print(f"[3] Microphone Telemetry Endpoint: {r.status_code} -> RMS: {d.get('rms')}, Peak: {d.get('peak')}, Speech: {d.get('speech_detected')}, Format: {d.get('format')} (HTTP Latency: {lat_mic:.1f}ms)")
    else:
        print(f"[3] Microphone Telemetry Endpoint: {r.status_code} -> {r.text}")

    # 4. End-to-End LARA Agent Message
    t0 = time.time()
    payload = {
        "session_id": "test_hw_verification",
        "message": "What is 125 plus 375?",
        "language": "auto",
        "locale": "en-IN"
    }
    r = requests.post(f"{base_url}/api/v1/agent/message", json=payload)
    lat_msg = (time.time() - t0) * 1000
    if r.status_code == 200:
        d = r.json()
        print(f"[4] LARA Voice Query: {r.status_code} -> Response: '{d.get('response')}' (Total Latency: {lat_msg:.1f}ms, Server: {d.get('metadata', {}).get('latency_ms')}ms)")
    else:
        print(f"[4] LARA Voice Query: {r.status_code} -> {r.text}")

    # 5. Calendar Query
    t0 = time.time()
    payload = {
        "session_id": "test_hw_verification",
        "message": "What is on my calendar today?",
        "language": "auto",
        "locale": "en-IN"
    }
    r = requests.post(f"{base_url}/api/v1/agent/message", json=payload)
    lat_cal = (time.time() - t0) * 1000
    if r.status_code == 200:
        d = r.json()
        print(f"[5] Calendar Query: {r.status_code} -> Response: '{d.get('response')}' (Total Latency: {lat_cal:.1f}ms)")

    # 6. Email Query
    t0 = time.time()
    payload = {
        "session_id": "test_hw_verification",
        "message": "Check my unread emails",
        "language": "auto",
        "locale": "en-IN"
    }
    r = requests.post(f"{base_url}/api/v1/agent/message", json=payload)
    lat_em = (time.time() - t0) * 1000
    if r.status_code == 200:
        d = r.json()
        print(f"[6] Email Query: {r.status_code} -> Response: '{d.get('response')}' (Total Latency: {lat_em:.1f}ms)")

if __name__ == "__main__":
    verify_all_endpoints()
