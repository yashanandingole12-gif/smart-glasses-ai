import serial
import time
import json
import base64
import os

def test_esp32_hw():
    print("=== XIAO ESP32-S3 Sense Hardware Verification ===")
    ser = serial.Serial('COM5', 115200, timeout=2)
    ser.dtr = True
    ser.rts = True
    time.sleep(1.5)
    
    # Read initial boot logs
    print("\n--- Reading Boot & Status Logs ---")
    end_time = time.time() + 3
    boot_lines = []
    while time.time() < end_time:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='replace').strip()
            if line:
                boot_lines.append(line)
                print(f"[BOOT LOG]: {line}")
        time.sleep(0.05)

    # 1. Test Camera Capture
    print("\n--- Testing Onboard Camera (CAPTURE_FRAME) ---")
    ser.write(b"CAPTURE_FRAME\n")
    ser.flush()
    time.sleep(0.5)
    
    cam_data = None
    cam_start = time.time()
    while time.time() - cam_start < 5:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='replace').strip()
            if line.startswith("CAM_FRAME:"):
                payload = line.split("CAM_FRAME:", 1)[1].strip()
                try:
                    cam_data = json.loads(payload)
                    print(f"[CAMERA SUCCESS]: Frame received! Size: {cam_data.get('size')} bytes, Format: {cam_data.get('format')}, Resolution: {cam_data.get('width')}x{cam_data.get('height')}")
                    # Save image artifact
                    b64_str = cam_data.get('base64', '')
                    if b64_str:
                        img_bytes = base64.b64decode(b64_str)
                        os.makedirs("artifacts", exist_ok=True)
                        with open("artifacts/real_xiao_camera_frame.jpg", "wb") as f:
                            f.write(img_bytes)
                        print(f"[CAMERA SAVED]: Saved image to artifacts/real_xiao_camera_frame.jpg ({len(img_bytes)} bytes)")
                except Exception as e:
                    print(f"[CAMERA ERROR parsing JSON]: {e}")
                break
            elif line.startswith("CAM_ERR"):
                print(f"[CAMERA ERROR]: {line}")
                break
        time.sleep(0.05)
    
    # 2. Test Onboard Microphone Telemetry
    print("\n--- Testing Onboard Microphone (MIC_TEST 5 seconds) ---")
    ser.write(b"MIC_TEST\n")
    ser.flush()
    
    mic_samples = []
    mic_start = time.time()
    while time.time() - mic_start < 6:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='replace').strip()
            if line.startswith("MIC_STATS:"):
                payload = line.split("MIC_STATS:", 1)[1].strip()
                try:
                    stats = json.loads(payload)
                    mic_samples.append(stats)
                    print(f"[MIC LIVE]: RMS={stats.get('rms', 0):6.1f} | Peak={stats.get('peak', 0):5d} | Speech={stats.get('speech_detected')} | Clip={stats.get('clipping')}")
                except Exception as e:
                    print(f"[MIC PARSE ERR]: {e}")
            elif line:
                print(f"[MIC LOG]: {line}")
        time.sleep(0.05)
        
    ser.close()
    print("\n=== Verification Completed ===")
    return {
        "boot_lines": boot_lines,
        "camera_success": cam_data is not None,
        "mic_samples_count": len(mic_samples)
    }

if __name__ == "__main__":
    test_esp32_hw()
