# Smart Glasses AI Assistant - System Architecture

## Overview
The Context-Aware Smart Glasses AI Assistant is designed as a hybrid edge-cloud wearable intelligence system. It seamlessly supports two deployment modes:
1. **Laptop Simulator Mode (Hardware-in-the-Loop Development)**: Uses the laptop microphone, speaker, webcam, and keyboard button to test the complete AI pipeline without physical glasses hardware.
2. **Physical Wearable Mode**: Uses ESP32-S3 glasses firmware communicating over BLE to an Android mobile hub, which proxies requests to the FastAPI backend.

```
                    PHYSICAL MODE                         LAPTOP SIMULATOR MODE
                    +-------------+                       +---------------------+
                    |  ESP32-S3   |                       |  Laptop Simulator   |
                    | (PTT Button |                       | (Keyboard, Mic,     |
                    |  I2S Mic/Spk|                       |  Webcam, Speaker)   |
                    +------+------+                       +----------+----------+
                           | BLE GATT                                | HTTPS
                           v                                         |
                    +-------------+                                  |
                    |Android Phone|                                  |
                    | (Mobile Hub)|                                  |
                    +------+------+                                  |
                           | HTTPS                                   |
                           +--------------------+--------------------+
                                                |
                                                v
                                   +-------------------------+
                                   |     FastAPI Backend     |
                                   |  (/api/v1/agent/message)|
                                   +------------+------------+
                                                |
                                                v
                                   +-------------------------+
                                   |     Context Engine      |
                                   | (Time, Loc, Cal, Device)|
                                   +------------+------------+
                                                |
                                                v
                                   +-------------------------+
                                   |     LangGraph Agent     |
                                   |  (StateGraph + Memory)  |
                                   +------------+------------+
                                                |
                        +-----------------------+-----------------------+
                        |                       |                       |
                        v                       v                       v
               +-----------------+     +-----------------+     +-----------------+
               |   LLMService    |     |  Tool Registry  |     |  Memory Store   |
               | (Gemini/OpenAI/ |     | (Calendar, Mail,|     | (SQLite Session |
               |  Claude/Ollama) |     |  Search, Place) |     |  & Long-Term)   |
               +-----------------+     +-----------------+     +-----------------+
```

---

## Key Subsystems
1. **Context Engine**: Gathers multi-dimensional telemetry (local time, diurnal period, geographic coordinates, upcoming calendar events, battery health) and enriches every user prompt.
2. **LangGraph Agent**: Single-agent state graph with tool execution loops, entity resolution across dialogue turns, and risk-based action confirmation.
3. **Hardware Abstraction Layer (`GlassesDevice`)**: Ensures the FastAPI backend and Android companion application work identically with the laptop simulator and the physical ESP32-S3 glasses.
4. **Structured Latency Pipeline**: Tracks sub-second execution intervals across speech transcription, context lookup, LLM inference, tool execution, and speech synthesis.
