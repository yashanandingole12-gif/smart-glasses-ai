# Context-Aware Smart Glasses AI Assistant

A complete, production-ready, context-aware smart glasses ecosystem featuring:
- **ESP32-S3 Firmware**: Custom BLE GATT service, push-to-talk interrupt handler, I2S audio & camera HAL.
- **Laptop Smart-Glasses Simulator**: Hardware-equivalent terminal emulator with microphone STT, webcam vision, speaker TTS, and keyboard push-to-talk.
- **FastAPI & Context Engine**: Dynamic temporal, spatial, calendar, and device context enrichment.
- **Single-Agent LangGraph**: Stateful LLM orchestration with checkpointing, tool-calling registry, and risk confirmation rules.
- **Android Mobile Hub**: Kotlin + Jetpack Compose companion app supporting both real BLE ESP32 and simulated glasses.

---

## Quick Start (Phase 1: Laptop Simulator Mode)

### 1. Prerequisites
- Python 3.11+ (Python 3.13 supported)
- Microphone, speakers, and webcam (optional)

### 2. Setup Environment
Run the automated PowerShell setup script:
```powershell
.\scripts\setup_env.ps1
```
Or manually install dependencies:
```bash
pip install -r backend/requirements.txt
pip install -r simulator/requirements.txt
```

### 3. Run Backend
```powershell
.\scripts\run_backend.ps1
```
Or:
```bash
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Run Simulator
In another terminal:
```powershell
.\scripts\run_simulator.ps1
```
Or:
```bash
python simulator/main.py
```

### 5. Interaction
- Press **ENTER** (or **SPACE**) in the simulator to simulate the physical glasses button.
- Speak into your laptop microphone: `"Good morning."`
- The system captures your voice, determines time and location, fetches calendar context, generates a contextual AI response, and speaks it out via your laptop speaker!

---

## Directory Overview
- `backend/`: FastAPI application, LangGraph agent, Context Engine, LLM service, and tool registry.
- `simulator/`: Laptop smart-glasses hardware simulator (audio, camera, terminal UI).
- `firmware/esp32-s3/`: Real PlatformIO C++ firmware for ESP32-S3 smart glasses.
- `android/`: Android companion application (Kotlin / Compose / BLE).
- `docs/`: System architecture, API documentation, BLE protocol specification, setup guide.
- `tests/`: Automated test suite.
