# EVA Master Architecture Specification

## 1. System Philosophy & Single Authority
EVA is designed as **one continuous, latency-resilient AI companion**.

### Authority Model:
* **Android Phone**: The primary local control, connectivity, audio-routing, permission, and session authority.
* **Smart Glasses (ESP32-S3)**: An optional sensory extension (Microphone input, BLE command link, 2.4GHz Wi-Fi). Camera remains strictly **ON HOLD**.
* **Cloud / Backend**: Intelligence, LLM orchestration, Google Workspace, GitHub, LinkedIn, and Academic Research layer.
* **Audio Flow**:
  * **INPUT**: ESP32 Digital PDM Microphone (MSM261D3526H1CPM) or Phone Mic.
  * **PROCESSOR / GATEWAY**: Android Background Companion Service.
  * **OUTPUT**: TWS Bluetooth Earbuds / Speaker (with automatic fallback to Phone Speaker).

```
[ ESP32-S3 Mic ] ──(Framed BLE/Wi-Fi Transport)──► [ Android Background Core ]
                                                              │
                    ┌─────────────────────────────────────────┴─────────────────────────────────────────┐
                    ▼                                         ▼                                         ▼
         [ Rule-Based Engine ]                      [ Generative Engine ]                     [ Agentic Engine ]
         (Offline Deterministic)                   (Multi-Tier LLM Router)                   (Composable Agents)
          - Time, Date, Battery                     - Python/C/C++ Code                       - Research Agent
          - Call / SMS Controls                     - Drafting & Composition                  - Opportunity Matcher
          - Definitional Dict                       - Summarization                           - Google Workspace
          - Arithmetic Engine                       - Explanations                            - GitHub / LinkedIn
                    │                                         │                                         │
                    └─────────────────────────────────────────┼─────────────────────────────────────────┘
                                                              ▼
                                                   [ Android Text-To-Speech ]
                                                              │
                                                              ▼
                                                   [ AudioOutputRouter ]
                                                              │
                                                              ▼
                                                   [ 🎧 Connected TWS ]
```

---

## 2. Core Architectural Pillars

### Pillar 1: Glasses-Optional Resilience
* The system never makes the glasses a single point of failure.
* If glasses are disconnected $\rightarrow$ EVA operates using Phone Microphone and Screen/TWS.
* If glasses are connected $\rightarrow$ ESP32 mic captures speech and streams framed packets to Android.

### Pillar 2: Offline Deterministic Fast-Path (<10ms)
* Queries for time, date, battery, definitions, arithmetic, telephony, and notifications are resolved locally by `LocalDeterministicResolver` (Android) and `DeterministicRuleEngine` (Backend).
* Zero cloud/LLM calls are made for deterministic queries.

### Pillar 3: Dynamic Audio Routing with TWS Priority
* `AudioOutputRouter` monitors device changes via Android `AudioDeviceCallback`.
* If TWS is connected $\rightarrow$ Audio routes to TWS in HD speech mode.
* If TWS disconnects $\rightarrow$ Output immediately falls back to Phone Speaker.
* When TWS reconnects $\rightarrow$ Output automatically restores to TWS.

### Pillar 4: Composable Multi-Agent Ecosystem
* **LinkedIn Agent**: Professional opportunity search and application preparation.
* **Email / Gmail Agent**: Search, read, draft, and send emails via existing Google OAuth 2.0.
* **Google Workspace Agent**: Integrated coordination across Gmail, Calendar, Drive, and Contacts.
* **GitHub Agent**: Code search, repository inspection, issues, and PR management.
* **Research Agent**: Real academic literature discovery across arXiv, OpenAlex, Semantic Scholar, and Crossref.
* **Opportunity Matcher**: Scores jobs against structured `UserProfile` with explicit criteria and mandatory human confirmation.
* **Resume / Profile Agent**: Structured user profile storage.
* **Web Research Agent**: Pluggable real-time web search.
