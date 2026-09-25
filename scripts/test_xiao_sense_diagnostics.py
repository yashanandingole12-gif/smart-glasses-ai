"""
XIAO ESP32-S3 Sense Hardware Diagnostics CLI Test Runner
Safely queries hardware diagnostics endpoints for OV2640 camera and MSM261D PDM mic without interfering with main EVA assistant flow.
"""

import sys
import time
import requests
import json

BASE_URL = "http://localhost:8001"

def test_hardware_diagnostics():
    print("=" * 60)
    print("🔍 Testing XIAO ESP32-S3 Sense Hardware Diagnostics")
    print("=" * 60)

    # 1. Test Overall Diagnostic Status
    print("\n1. Testing ESP32 Diagnostic Status Endpoint...")
    try:
        res = requests.get(f"{BASE_URL}/api/v1/hardware/esp32/diagnostic", timeout=5)
        if res.status_code == 200:
            data = res.json()
            print("   ✅ Hardware Diagnostic Endpoint Passed:")
            print(json.dumps(data, indent=6))
        else:
            print(f"   ⚠️ Diagnostic endpoint returned status {res.status_code}")
    except Exception as e:
        print(f"   ❌ Error reaching diagnostic endpoint: {e}")

    # 2. Test Camera Frame Endpoint
    print("\n2. Testing OV2640 Camera Capture Endpoint...")
    try:
        res = requests.get(f"{BASE_URL}/api/v1/hardware/camera/capture", timeout=5)
        if res.status_code == 200:
            data = res.json()
            print(f"   ✅ Camera Capture: Status={data.get('status')}, Sensor={data.get('sensor')}, Res={data.get('resolution')}")
        else:
            print(f"   ⚠️ Camera endpoint returned status {res.status_code}")
    except Exception as e:
        print(f"   ❌ Error reaching camera endpoint: {e}")

    # 3. Test Microphone Telemetry Endpoint
    print("\n3. Testing MSM261D PDM Microphone Telemetry...")
    try:
        res = requests.get(f"{BASE_URL}/api/v1/hardware/mic/telemetry", timeout=5)
        if res.status_code == 200:
            data = res.json()
            print(f"   ✅ Mic Telemetry: Status={data.get('status')}, RMS={data.get('rms_energy')}, VAD={data.get('vad_active')}")
        else:
            print(f"   ⚠️ Mic endpoint returned status {res.status_code}")
    except Exception as e:
        print(f"   ❌ Error reaching mic telemetry endpoint: {e}")

    # 4. Test Deterministic Math Endpoint
    print("\n4. Testing Deterministic Math Endpoint (45.2x + 1916029.9888 = 0)...")
    try:
        res = requests.post(f"{BASE_URL}/api/v1/math/evaluate", json={"query": "45.2x + 1916029.9888 = 0"}, timeout=5)
        if res.status_code == 200:
            data = res.json()
            math_data = data.get("data", {})
            print(f"   ✅ Math Result: {math_data.get('solution_display')} (Spoken: '{math_data.get('text_response')}')")
            print("   Steps:")
            for s in math_data.get("steps", []):
                print(f"     - {s}")
        else:
            print(f"   ⚠️ Math endpoint returned status {res.status_code}")
    except Exception as e:
        print(f"   ❌ Error reaching math evaluate endpoint: {e}")

    print("\n" + "=" * 60)
    print("🎯 Hardware & Math Diagnostics Suite Completed")
    print("=" * 60)

if __name__ == "__main__":
    test_hardware_diagnostics()
