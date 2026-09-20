# EVA System Reliability & Failure Recovery Guide

## 1. Failure Taxonomy & Recovery Strategies

EVA is engineered to gracefully degrade and automatically recover across all connectivity, hardware, and network failure modes without crashing or terminating user sessions.

| Failure Scenario | Immediate Impact | Automatic Recovery Strategy | Graceful Degradation State |
| :--- | :--- | :--- | :--- |
| **BLE Interruption** | Command / Audio packet loss | Automatic background reconnection with exponential backoff; switches transport to Wi-Fi if available. | EVA operates in Standalone Mobile Mode. |
| **Wi-Fi Interruption** | Cloud API latency / failure | Audio transport falls back to BLE; deterministic queries route to local rule engine. | Local offline functionality remains 100% active. |
| **Backend Cloud Outage** | LLM / Agent tools unavailable | `AIResponseRouter` automatically catches network exception and delegates to `LocalDeterministicResolver` and on-device NLP. | Offline time, date, battery, calls, and definitional answers continue sub-10ms. |
| **TWS Disconnect** | Audio output path broken | `AudioOutputRouter` catches `onAudioDevicesRemoved` broadcast and immediately redirects active speech to Phone Speaker. | Voice output continues uninterrupted on phone speaker. |
| **TWS Reconnect** | TWS becomes available again | `AudioOutputRouter` catches `onAudioDevicesAdded` broadcast and smoothly restores output route to TWS. | Next utterance routes to TWS. |
| **ESP32 Reboot / Brownout** | Hardware reset | Android background service detects disconnect, maintains active conversation session, and auto-pairs on reboot. | Session state is preserved. |
| **Android Service Restart** | Background memory reclaim | `BootReceiver` and `GlassesBackgroundService` restart with `START_STICKY` and reload persistent context from `smart_glasses.db`. | Companion restarts seamlessly. |
| **Stale / Duplicate Audio** | Out-of-order packets | `AudioTransport` jitter buffer compares monotonic `sequence_number` against `lastEmittedSequence` and drops stale frames. | Audio stream remains in sync. |

---

## 2. Bounded Buffers & Anti-Crash Invariants

1. **Zero Unbounded Queues**: All audio, event, and telemetry queues have strict upper capacity bounds (e.g. 32 frames). Oldest items are dropped during burst overruns.
2. **Deterministic Timeouts**: All external HTTP/gRPC requests enforce strict deadlines (8.0s timeout with circuit breakers).
3. **Idempotent Mutations**: Actions that modify calendar, send emails, or send SMS require unique `request_id` idempotency keys to prevent duplicate execution during network retries.
