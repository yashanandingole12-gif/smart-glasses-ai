"""
Smart Glasses AI - Speaker & Message Audio Tester
Tests receiving AI response audio, tones, message chimes, and PCM streaming on the ESP32-S3 speaker.
"""

import sys
import time
import base64
import struct
import math

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("[ERROR] 'pyserial' not installed. Install with: pip install pyserial")
    sys.exit(1)


def find_esp32_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        desc = (p.description or "").lower()
        hwid = (p.hwid or "").lower()
        if "ch340" in desc or "cp210" in desc or "usb" in desc or "xiao" in desc or "esp32" in desc or "303a" in hwid:
            return p.device
    if ports:
        return ports[0].device
    return None


def generate_wav_sine_tone(freq_hz=440, duration_sec=1.0, sample_rate=16000, volume=0.7):
    """Generates an in-memory 16-bit Mono RIFF WAV byte array."""
    num_samples = int(sample_rate * duration_sec)
    pcm_data = bytearray()
    
    for i in range(num_samples):
        # Apply 5ms attack/decay envelope
        env = 1.0
        if i < 80:
            env = i / 80.0
        elif num_samples - i < 80:
            env = (num_samples - i) / 80.0
            
        sample = int(math.sin(2.0 * math.pi * freq_hz * (i / sample_rate)) * 32767.0 * volume * env)
        sample = max(-32768, min(32767, sample))
        pcm_data.extend(struct.pack('<h', sample))
    
    # 44-byte standard RIFF WAV Header
    header = bytearray()
    header.extend(b'RIFF')
    header.extend(struct.pack('<I', 36 + len(pcm_data)))
    header.extend(b'WAVE')
    header.extend(b'fmt ')
    header.extend(struct.pack('<I', 16))          # Subchunk1Size (16 for PCM)
    header.extend(struct.pack('<H', 1))           # AudioFormat (1 for PCM)
    header.extend(struct.pack('<H', 1))           # NumChannels (1 = Mono)
    header.extend(struct.pack('<I', sample_rate)) # SampleRate
    header.extend(struct.pack('<I', sample_rate * 2)) # ByteRate
    header.extend(struct.pack('<H', 2))           # BlockAlign
    header.extend(struct.pack('<H', 16))          # BitsPerSample
    header.extend(b'data')
    header.extend(struct.pack('<I', len(pcm_data)))
    
    return header + pcm_data


def run_interactive_tester(port=None, baud=115200):
    if not port:
        port = find_esp32_port()
    if not port:
        print("[ERROR] No serial port detected. Please plug in Seeed XIAO ESP32-S3.")
        return

    print("=" * 60)
    print(f"  Smart Glasses ESP32 Speaker Audio Test Client")
    print(f"  Target Port: {port} @ {baud} baud")
    print("=" * 60)

    try:
        ser = serial.Serial(port, baud, timeout=1.0)
        time.sleep(1.5) # Allow ESP32 boot
    except Exception as e:
        print(f"[ERROR] Failed to open {port}: {e}")
        print("Note: If a device monitor or another terminal is holding COM5, close it first.")
        return

    print("\n[CONNECTED] Serial stream active. Select an action:")
    print(" 1 -> Play Incoming Message Notification Alert")
    print(" 2 -> Play AI Response Ready Chime (4-note arpeggio)")
    print(" 3 -> Play Wake-up Prompt Chime")
    print(" 4 -> Play Incoming Call Ringtone")
    print(" 5 -> Play Success Tone")
    print(" 6 -> Play Error Alert")
    print(" 7 -> Run ESP32 Physical Speaker Hardware Diagnostic")
    print(" 8 -> Send 880Hz Test Tone (300ms)")
    print(" 9 -> Stream Base64 Synthesized WAV Audio (440Hz A4 note)")
    print(" 10 -> Set Volume (10% - 100%)")
    print(" q -> Quit\n")

    while True:
        try:
            choice = input("Enter choice (1-10, q): ").strip()
            if choice == 'q' or choice == 'exit':
                break
            elif choice == '1':
                ser.write(b"PLAY_MESSAGE_ALERT\n")
                print(">> Sent: PLAY_MESSAGE_ALERT")
            elif choice == '2':
                ser.write(b"PLAY_AI_RESPONSE\n")
                print(">> Sent: PLAY_AI_RESPONSE")
            elif choice == '3':
                ser.write(b"PLAY_WAKE\n")
                print(">> Sent: PLAY_WAKE")
            elif choice == '4':
                ser.write(b"PLAY_CALL\n")
                print(">> Sent: PLAY_CALL")
            elif choice == '5':
                ser.write(b"PLAY_SUCCESS\n")
                print(">> Sent: PLAY_SUCCESS")
            elif choice == '6':
                ser.write(b"PLAY_ERROR\n")
                print(">> Sent: PLAY_ERROR")
            elif choice == '7':
                ser.write(b"SPK_TEST\n")
                print(">> Sent: SPK_TEST (Full Speaker Diagnostic)")
            elif choice == '8':
                ser.write(b"PLAY_TONE 880 300\n")
                print(">> Sent: PLAY_TONE 880 300")
            elif choice == '9':
                print("[AUDIO] Generating 440Hz 1.0s WAV audio payload...")
                wav_bytes = generate_wav_sine_tone(440, 1.0, 16000, 0.8)
                b64_str = base64.b64encode(wav_bytes).decode('ascii')
                cmd = f"PLAY_AUDIO_BASE64 {b64_str}\n"
                ser.write(cmd.encode('ascii'))
                print(f">> Streamed Base64 Audio ({len(wav_bytes)} bytes) to ESP32 speaker!")
            elif choice == '10':
                vol_str = input("Enter volume percentage (0 - 100): ").strip()
                ser.write(f"SET_VOLUME {vol_str}\n".encode('ascii'))
                print(f">> Sent: SET_VOLUME {vol_str}")
            else:
                print("Invalid option. Choose 1-10 or 'q'.")

            time.sleep(0.3)
            # Print any incoming responses from ESP32
            while ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"  [ESP32] {line}")

        except KeyboardInterrupt:
            break

    ser.close()
    print("\n[DISCONNECTED] Test session closed.")


if __name__ == "__main__":
    port_arg = sys.argv[1] if len(sys.argv) > 1 else None
    run_interactive_tester(port_arg)
