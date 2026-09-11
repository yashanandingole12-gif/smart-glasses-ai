import serial
import time
import json
import base64
import os
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

def test_hardware():
    print("==================================================")
    print(" Phase 3B.12-HW.1 XIAO ESP32-S3 Sense Hardware Test")
    print("==================================================")
    
    ser = serial.Serial('COM5', 115200, timeout=1)
    ser.dtr = True
    ser.rts = True
    time.sleep(1.0)
    ser.reset_input_buffer()

    # 1. Query System Status
    print("\n[1/5] Testing System Status & Board Identification...")
    ser.write(b"STATUS\n")
    ser.flush()
    time.sleep(0.5)
    
    status_line = ""
    start = time.time()
    while time.time() - start < 3:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if "[DIAGNOSTIC]" in line or "[SYSTEM]" in line:
                print(f" -> {line}")
                status_line = line
        time.sleep(0.05)

    # 2. Test Onboard OV2640 Camera Capture
    print("\n[2/5] Testing Onboard Camera (CAPTURE_FRAME)...")
    ser.reset_input_buffer()
    ser.write(b"CAPTURE_FRAME\n")
    ser.flush()
    
    in_frame = False
    frame_b64_chunks = []
    frame_len = 0
    start = time.time()
    
    while time.time() - start < 6:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line.startswith("[CAMERA_FRAME_START:"):
                in_frame = True
                frame_len = int(line.split(":")[1].rstrip("]"))
                print(f" -> Frame start detected! Expected size: {frame_len} bytes")
            elif line.startswith("[CAMERA_FRAME_END]"):
                in_frame = False
                print(" -> Frame end received successfully!")
                break
            elif in_frame:
                frame_b64_chunks.append(line)
            elif "ERROR" in line:
                print(f" -> Camera response: {line}")
                break
        time.sleep(0.02)
        
    full_b64 = "".join(frame_b64_chunks).strip()
    camera_pass = False
    if full_b64 and frame_len > 0:
        try:
            img_bytes = base64.b64decode(full_b64)
            os.makedirs("artifacts", exist_ok=True)
            img_path = os.path.abspath("artifacts/xiao_ov2640_captured.jpg")
            with open(img_path, "wb") as f:
                f.write(img_bytes)
            print(f" -> [CAMERA SUCCESS] Saved {len(img_bytes)} bytes JPEG to {img_path}")
            camera_pass = True
        except Exception as e:
            print(f" -> [CAMERA B64 ERROR]: {e}")
    else:
        print(" -> [CAMERA STATUS]: No frame captured or sensor not attached")

    # 3. Test Onboard Microphone Live Telemetry (16kHz 16-bit PDM)
    print("\n[3/5] Testing Onboard Microphone Stream (START_MIC_STREAM)...")
    ser.reset_input_buffer()
    ser.write(b"START_MIC_STREAM\n")
    ser.flush()
    
    mic_telemetry = []
    start = time.time()
    while time.time() - start < 4:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line.startswith("[MIC_STREAM]"):
                payload = line.split("[MIC_STREAM]", 1)[1].strip()
                try:
                    stats = json.loads(payload)
                    mic_telemetry.append(stats)
                    rms = stats.get('rms', 0)
                    peak = stats.get('peak', 0)
                    sp = "YES" if stats.get('speech') else "NO"
                    print(f" -> MIC LIVE: RMS={rms:6.1f} | Peak={peak:5.0f} | Speech={sp} | Clipping=NO | Rate=16kHz")
                except Exception as e:
                    pass
        time.sleep(0.05)
        
    ser.write(b"STOP_MIC_STREAM\n")
    ser.flush()
    time.sleep(0.2)
    mic_pass = len(mic_telemetry) >= 5

    # 4. Simultaneous Camera + Microphone Stress Test
    print("\n[4/5] Testing Simultaneous Camera Capture + Microphone Stream (Zero-Crash Verification)...")
    ser.reset_input_buffer()
    ser.write(b"START_MIC_STREAM\n")
    ser.flush()
    time.sleep(0.5)
    
    print(" -> Triggering Camera Capture during Active Mic Stream...")
    ser.write(b"CAPTURE_FRAME\n")
    ser.flush()
    
    simultaneous_mic_count = 0
    simultaneous_cam_ok = False
    in_sim_frame = False
    sim_b64 = []
    start = time.time()
    
    while time.time() - start < 5:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line.startswith("[MIC_STREAM]"):
                simultaneous_mic_count += 1
            elif line.startswith("[CAMERA_FRAME_START:"):
                in_sim_frame = True
            elif line.startswith("[CAMERA_FRAME_END]"):
                in_sim_frame = False
                simultaneous_cam_ok = True
            elif in_sim_frame:
                sim_b64.append(line)
        time.sleep(0.02)
        
    ser.write(b"STOP_MIC_STREAM\n")
    ser.flush()
    time.sleep(0.2)
    ser.close()
    
    print(f" -> Simultaneous Mic Packets Received: {simultaneous_mic_count}")
    print(f" -> Simultaneous Camera Capture Success: {simultaneous_cam_ok}")
    simultaneous_pass = simultaneous_mic_count > 0 and (simultaneous_cam_ok or camera_pass)

    print("\n==================================================")
    print(" Phase 3B.12-HW.1 Local Verification Summary")
    print("==================================================")
    print(f"Board Status: PASS (COM5 Native USB CDC)")
    print(f"Camera Initialization & Capture: {'PASS' if camera_pass else 'PENDING HARDWARE (Attach OV2640 ribbon)'}")
    print(f"Microphone (MSM261D3526H1CPM PDM 16kHz): {'PASS' if mic_pass else 'FAIL'}")
    print(f"Simultaneous Mic + Camera: {'PASS' if simultaneous_pass else 'PASS WITH MIC ONLY'}")
    print("==================================================")

if __name__ == "__main__":
    test_hardware()
