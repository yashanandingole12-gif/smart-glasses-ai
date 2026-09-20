def get_dashboard_html() -> str:
    """Returns the LARA Real-Time Operations Console & Live Intelligence Dashboard (Clean Luxury, Zero Emojis)."""
    return r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LARA Smart Glasses — Private Intelligence & Control</title>
    <style>
        :root {
            --bg-base: #0c0d10;
            --bg-surface: #14161d;
            --bg-card: #1b1e27;
            --bg-input: #222632;
            --border: #2c3140;
            --border-active: #d96b27;
            --accent: #d96b27;
            --accent-glow: rgba(217, 107, 39, 0.25);
            --accent-hover: #eb7c36;
            --emerald: #10b981;
            --emerald-bg: rgba(16, 185, 129, 0.15);
            --blue: #3b82f6;
            --blue-bg: rgba(59, 130, 246, 0.15);
            --purple: #8b5cf6;
            --purple-bg: rgba(139, 92, 246, 0.15);
            --amber: #f59e0b;
            --amber-bg: rgba(245, 158, 11, 0.15);
            --red: #ef4444;
            --red-bg: rgba(239, 68, 68, 0.15);
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --text-muted: #6b7280;
            --font-mono: "JetBrains Mono", "Courier New", monospace;
            --radius-sm: 6px;
            --radius-md: 10px;
            --radius-lg: 14px;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-base);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }

        /* Top Header Navigation */
        .top-header {
            background-color: var(--bg-surface);
            border-bottom: 1px solid var(--border);
            padding: 12px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .brand-section {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .brand-badge {
            background: linear-gradient(135deg, #d96b27, #f59e0b);
            color: #fff;
            font-weight: 800;
            font-size: 13px;
            padding: 4px 10px;
            border-radius: var(--radius-sm);
            letter-spacing: 1.5px;
        }

        .brand-title {
            font-size: 18px;
            font-weight: 700;
            letter-spacing: 0.5px;
        }

        .brand-subtitle {
            font-size: 12px;
            color: var(--text-secondary);
        }

        .system-status-pills {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.5px;
            border: 1px solid var(--border);
            background: var(--bg-card);
        }

        .pill-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
        }

        .pill-live .pill-dot { background-color: var(--emerald); box-shadow: 0 0 8px var(--emerald); }
        .pill-live { color: var(--emerald); border-color: rgba(16, 185, 129, 0.3); background: var(--emerald-bg); }

        .pill-cloud .pill-dot { background-color: var(--blue); }
        .pill-cloud { color: var(--blue); }

        .pill-hw .pill-dot { background-color: var(--amber); }
        .pill-hw { color: var(--amber); }

        /* Navigation Tabs */
        .tabs-nav {
            background-color: var(--bg-surface);
            border-bottom: 1px solid var(--border);
            display: flex;
            gap: 8px;
            padding: 0 24px;
            overflow-x: auto;
        }

        .tab-button {
            background: none;
            border: none;
            color: var(--text-secondary);
            font-size: 13px;
            font-weight: 600;
            padding: 12px 18px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.15s ease;
            display: flex;
            align-items: center;
            gap: 8px;
            white-space: nowrap;
        }

        .tab-button:hover {
            color: var(--text-primary);
        }

        .tab-button.active {
            color: var(--accent);
            border-bottom-color: var(--accent);
        }

        .tab-badge {
            background: var(--bg-base);
            padding: 2px 7px;
            border-radius: 10px;
            font-size: 10px;
            border: 1px solid var(--border);
        }

        /* Main Workspace Container */
        .main-container {
            flex: 1;
            padding: 24px;
            max-width: 1440px;
            margin: 0 auto;
            width: 100%;
        }

        .tab-panel {
            display: none;
        }

        .tab-panel.active {
            display: grid;
            gap: 20px;
        }

        /* 2-Column Grid Layouts */
        .grid-2col {
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 20px;
        }

        @media (max-width: 1024px) {
            .grid-2col {
                grid-template-columns: 1fr;
            }
        }

        /* Card Component */
        .card {
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--border);
            padding-bottom: 12px;
        }

        .card-title {
            font-size: 14px;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* Live Activity Stream Styling */
        .stream-controls {
            display: flex;
            gap: 8px;
        }

        .btn-sm {
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-secondary);
            padding: 4px 10px;
            border-radius: var(--radius-sm);
            font-size: 11px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.15s;
        }

        .btn-sm:hover {
            color: var(--text-primary);
            border-color: var(--border-active);
        }

        .live-stream-box {
            background: var(--bg-base);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            height: 520px;
            overflow-y: auto;
            padding: 12px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            font-family: var(--font-mono);
            font-size: 12px;
        }

        .stream-entry {
            background: var(--bg-card);
            border-left: 3px solid var(--border);
            border-radius: 4px;
            padding: 10px 12px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            animation: fadeIn 0.2s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-4px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .entry-USER_QUERY { border-left-color: var(--blue); }
        .entry-ASSISTANT_RESPONSE { border-left-color: var(--emerald); }
        .entry-CAMERA_CAPTURE { border-left-color: var(--purple); }
        .entry-VISION_ANALYZE { border-left-color: var(--amber); }
        .entry-RESEARCH_SEARCH { border-left-color: #ec4899; }
        .entry-SYSTEM_CONNECTED { border-left-color: var(--emerald); }

        .entry-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 11px;
        }

        .entry-type {
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 3px;
        }

        .type-USER_QUERY { background: var(--blue-bg); color: var(--blue); }
        .type-ASSISTANT_RESPONSE { background: var(--emerald-bg); color: var(--emerald); }
        .type-CAMERA_CAPTURE { background: var(--purple-bg); color: var(--purple); }
        .type-VISION_ANALYZE { background: var(--amber-bg); color: var(--amber); }
        .type-RESEARCH_SEARCH { background: rgba(236, 72, 153, 0.15); color: #ec4899; }
        .type-SYSTEM_CONNECTED { background: var(--emerald-bg); color: var(--emerald); }

        .entry-time {
            color: var(--text-muted);
        }

        .entry-body {
            color: var(--text-primary);
            line-height: 1.4;
            word-break: break-word;
        }

        .entry-meta {
            color: var(--text-secondary);
            font-size: 10px;
            display: flex;
            gap: 12px;
        }

        /* Quick Prompt Buttons */
        .quick-prompts-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }

        .prompt-chip {
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-secondary);
            padding: 8px 12px;
            border-radius: var(--radius-sm);
            font-size: 12px;
            text-align: left;
            cursor: pointer;
            transition: all 0.15s;
            display: flex;
            flex-direction: column;
            gap: 2px;
        }

        .prompt-chip strong {
            color: var(--text-primary);
            font-size: 12px;
        }

        .prompt-chip span {
            font-size: 10px;
            color: var(--text-muted);
        }

        .prompt-chip:hover {
            border-color: var(--accent);
            background: var(--bg-input);
            color: var(--accent);
        }

        /* Interactive Query Box */
        .query-input-group {
            display: flex;
            gap: 8px;
        }

        .input-text {
            flex: 1;
            background: var(--bg-input);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            color: var(--text-primary);
            padding: 10px 14px;
            font-size: 13px;
            outline: none;
            transition: border-color 0.15s;
        }

        .input-text:focus {
            border-color: var(--border-active);
        }

        .btn-primary {
            background: var(--accent);
            color: #fff;
            border: none;
            border-radius: var(--radius-sm);
            padding: 10px 18px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.15s;
        }

        .btn-primary:hover {
            background: var(--accent-hover);
        }

        /* Smart Glass OLED Simulator */
        .oled-display-box {
            background: #000;
            border: 3px solid #333;
            border-radius: 8px;
            padding: 12px;
            width: 100%;
            height: 120px;
            font-family: var(--font-mono);
            color: #00ffcc;
            text-shadow: 0 0 5px rgba(0, 255, 204, 0.6);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            overflow: hidden;
            box-shadow: inset 0 0 10px rgba(0, 255, 204, 0.2);
        }

        .oled-header {
            font-size: 10px;
            display: flex;
            justify-content: space-between;
            border-bottom: 1px dashed rgba(0, 255, 204, 0.3);
            padding-bottom: 2px;
        }

        .oled-content {
            font-size: 12px;
            line-height: 1.3;
            flex: 1;
            padding-top: 4px;
            overflow: hidden;
        }

        /* Research Hub Styling */
        .research-search-bar {
            display: flex;
            gap: 10px;
        }

        .papers-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
            max-height: 600px;
            overflow-y: auto;
        }

        .paper-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 14px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            transition: border-color 0.15s;
        }

        .paper-card:hover {
            border-color: var(--accent);
        }

        .paper-title {
            font-size: 14px;
            font-weight: 700;
            color: var(--text-primary);
        }

        .paper-title a {
            color: var(--text-primary);
            text-decoration: none;
        }

        .paper-title a:hover {
            color: var(--accent);
            text-decoration: underline;
        }

        .paper-meta {
            font-size: 11px;
            color: var(--text-secondary);
            display: flex;
            gap: 14px;
            flex-wrap: wrap;
        }

        .paper-abstract {
            font-size: 12px;
            color: var(--text-secondary);
            line-height: 1.5;
        }

        .paper-actions {
            display: flex;
            gap: 8px;
            margin-top: 4px;
        }

        /* Camera & Vision Hub */
        .cam-preview-box {
            background: #000;
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            height: 260px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            position: relative;
        }

        .cam-preview-img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }

        .cam-overlay-status {
            position: absolute;
            bottom: 8px;
            left: 8px;
            background: rgba(0, 0, 0, 0.7);
            color: #fff;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 10px;
            font-family: var(--font-mono);
        }

        /* Telemetry Meters */
        .metric-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            padding: 6px 0;
            border-bottom: 1px solid var(--border);
        }

        .metric-label {
            color: var(--text-secondary);
        }

        .metric-value {
            font-family: var(--font-mono);
            font-weight: 600;
            color: var(--text-primary);
        }
    </style>
</head>
<body>

    <!-- Top Executive Header Bar -->
    <header class="top-header">
        <div class="brand-section">
            <div class="brand-badge">EVA</div>
            <div>
                <div class="brand-title">EVA Smart Glasses — Private Intelligence & Control</div>
                <div class="brand-subtitle">ESP32 Smart Glasses & Android Hub</div>
            </div>
        </div>
        <div class="system-status-pills">
            <div class="pill pill-live" id="sse-status-pill">
                <span class="pill-dot"></span>
                <span id="sse-status-text">SSE Stream Active</span>
            </div>
            <div class="pill pill-cloud">
                <span class="pill-dot"></span>
                <span>Gemini 2.5 Flash</span>
            </div>
            <div class="pill pill-hw">
                <span class="pill-dot"></span>
                <span>ESP32-S3 Sense (COM5)</span>
            </div>
        </div>
    </header>

    <!-- Navigation Tabs -->
    <nav class="tabs-nav">
        <button class="tab-button active" onclick="switchTab('live-stream')">
            Live Activity Stream
            <span class="tab-badge" id="event-counter-badge">0</span>
        </button>
        <button class="tab-button" onclick="switchTab('ai-playground')">
            Intent Inspector & Playground
        </button>
        <button class="tab-button" onclick="switchTab('research-hub')">
            EVA Research Engine
        </button>
        <button class="tab-button" onclick="switchTab('desk-analysis')">
            Desk & Data Analysis
        </button>
        <button class="tab-button" onclick="switchTab('camera-vision')">
            Camera & Vision Hub
        </button>
        <button class="tab-button" onclick="switchTab('workspace')">
            Workspace & Environment
        </button>
        <button class="tab-button" onclick="switchTab('automations-hub')">
            Automations Center & Smart Notifications
        </button>
        <button class="tab-button" onclick="switchTab('system-diagnostics')">
            Device Health & Telemetry
        </button>
    </nav>

    <!-- Main Content Workspace -->
    <main class="main-container">

        <!-- TAB 1: LIVE ACTIVITY STREAM -->
        <section id="tab-live-stream" class="tab-panel active">
            <div class="grid-2col">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            <span>Real-Time Global Event Stream</span>
                        </div>
                        <div class="stream-controls">
                            <button class="btn-sm" onclick="clearLiveEvents()">Clear Feed</button>
                            <button class="btn-sm" id="autoscroll-toggle-btn" onclick="toggleAutoScroll()">Auto-scroll: ON</button>
                        </div>
                    </div>
                    <div class="live-stream-box" id="live-stream-feed">
                        <div class="stream-entry entry-SYSTEM_CONNECTED">
                            <div class="entry-header">
                                <span class="entry-type type-SYSTEM_CONNECTED">SYSTEM</span>
                                <span class="entry-time">Initialising</span>
                            </div>
                            <div class="entry-body">Subscribing to real-time telemetry from glasses, mobile companion, and AI kernel...</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            <span>Glasses Live HUD & Audio Sim</span>
                        </div>
                    </div>
                    
                    <div>
                        <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 6px;">0.42" OLED (SSD1306) Optical Preview:</div>
                        <div class="oled-display-box" id="oled-preview">
                            <div class="oled-header">
                                <span>LARA v2.0</span>
                                <span id="oled-clock">10:45 AM</span>
                                <span>BAT 85%</span>
                            </div>
                            <div class="oled-content" id="oled-text">
                                Ready for voice or touch commands.
                            </div>
                        </div>
                    </div>

                    <div style="margin-top: 10px;">
                        <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 6px;">Latest Spoken Voice Output:</div>
                        <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 12px; font-size: 13px; line-height: 1.4;" id="voice-preview-text">
                            No spoken output generated yet.
                        </div>
                    </div>

                    <div style="margin-top: 10px;">
                        <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 6px;">Quick Test Triggers:</div>
                        <div class="quick-prompts-grid">
                            <button class="prompt-chip" onclick="sendQuickPrompt('Nagpur mein best pet shop kahan hai')">
                                <strong>Nagpur Pet Shops</strong>
                                <span>Local search grounding</span>
                            </button>
                            <button class="prompt-chip" onclick="sendQuickPrompt('Write a simple calculator in Python')">
                                <strong>Python Calculator</strong>
                                <span>Code generation test</span>
                            </button>
                            <button class="prompt-chip" onclick="sendQuickPrompt('Plan a 3-day trip to Goa with itinerary')">
                                <strong>Goa Trip Plan</strong>
                                <span>Multi-step reasoning</span>
                            </button>
                            <button class="prompt-chip" onclick="triggerCameraCapture()">
                                <strong>Capture Photo</strong>
                                <span>ESP32 camera frame</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- TAB 2: AI VOICE & LOGIC PLAYGROUND / INTENT INSPECTOR -->
        <section id="tab-ai-playground" class="tab-panel">
            <div class="grid-2col">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            <span>Intent Inspector & AI Tester</span>
                        </div>
                    </div>

                    <div class="quick-prompts-grid" style="grid-template-columns: 1fr 1fr;">
                        <button class="prompt-chip" onclick="sendQuickPrompt('Nagpur mai best pet shop kaha hai')">
                            <strong>Nagpur Best Pet Shop</strong>
                            <span>Hindi/Hinglish query</span>
                        </button>
                        <button class="prompt-chip" onclick="sendQuickPrompt('write a simple calclator python')">
                            <strong>Simple Calculator Code</strong>
                            <span>Python script generation</span>
                        </button>
                        <button class="prompt-chip" onclick="sendQuickPrompt('plan a trip to Manali for 4 days')">
                            <strong>Manali 4-Day Trip</strong>
                            <span>Itinerary planning</span>
                        </button>
                        <button class="prompt-chip" onclick="sendQuickPrompt('Search research papers on ergonomic smart wearable')">
                            <strong>Ergonomic Wearables</strong>
                            <span>Academic arXiv retrieval</span>
                        </button>
                    </div>

                    <div class="query-input-group">
                        <input type="text" id="playground-query-input" class="input-text" placeholder="Type or speak a command for LARA..." onkeydown="if(event.key==='Enter') executePlaygroundQuery()">
                        <button class="btn-primary" onclick="executePlaygroundQuery()" id="playground-send-btn">Send Query</button>
                    </div>

                    <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 14px; min-height: 180px; display: flex; flex-direction: column; gap: 8px;">
                        <div style="font-size: 11px; font-weight: 700; color: var(--accent); text-transform: uppercase;">Assistant Response:</div>
                        <div id="playground-response-area" style="font-size: 13px; line-height: 1.5; color: var(--text-primary); white-space: pre-wrap;">
                            Click one of the prompt buttons above or type any query to test the full AI pipeline.
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            <span>Execution Telemetry & Latency</span>
                        </div>
                    </div>

                    <div class="metric-row">
                        <span class="metric-label">Parsed Intent:</span>
                        <span class="metric-value" id="meta-intent">STANDBY</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Routing Provider:</span>
                        <span class="metric-value" id="meta-provider">gemini-2.5-flash</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Fast-Path Latency:</span>
                        <span class="metric-value" id="meta-fastpath">-</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Total Pipeline Latency:</span>
                        <span class="metric-value" id="meta-latency">-</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Knowledge Sources:</span>
                        <span class="metric-value" id="meta-sources">-</span>
                    </div>

                    <div style="margin-top: 10px;">
                        <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 6px;">Raw JSON Inspection:</div>
                        <pre id="raw-json-inspector" style="background: var(--bg-base); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 10px; font-family: var(--font-mono); font-size: 11px; height: 180px; overflow-y: auto; color: var(--text-secondary);">{}</pre>
                    </div>
                </div>
            </div>
        </section>

        <!-- TAB 3: LARA RESEARCH ENGINE -->
        <section id="tab-research-hub" class="tab-panel">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">
                        <span>Academic & Scientific Literature Search</span>
                    </div>
                </div>

                <div class="research-search-bar">
                    <input type="text" id="research-query-input" class="input-text" value="ergonomic smart wearable" placeholder="Search arXiv, Semantic Scholar, CrossRef, PubMed..." onkeydown="if(event.key==='Enter') executeResearchSearch()">
                    <button class="btn-primary" onclick="executeResearchSearch()" id="research-search-btn">Search Papers</button>
                </div>

                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <button class="btn-sm" onclick="setResearchQuery('ergonomic smart wearable')">Ergonomic Smart Wearable</button>
                    <button class="btn-sm" onclick="setResearchQuery('edge AI on microcontroller')">Edge AI ESP32</button>
                    <button class="btn-sm" onclick="setResearchQuery('augmented reality optical waveguide')">AR Optical Waveguide</button>
                    <button class="btn-sm" onclick="setResearchQuery('deep learning audio noise suppression')">Audio Noise Suppression</button>
                </div>

                <div class="papers-list" id="research-results-container">
                    <div style="text-align: center; color: var(--text-secondary); padding: 40px;">
                        Enter a research query above to fetch peer-reviewed publications.
                    </div>
                </div>
            </div>
        </section>

        <!-- TAB 4: DESK & DATA ANALYSIS -->
        <section id="tab-desk-analysis" class="tab-panel">
            <div class="grid-2col">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            <span>Desk & Data Analysis</span>
                        </div>
                    </div>
                    <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.5;">
                        Query uploaded spreadsheets, staff datasets, and financial documents with zero hallucination.
                    </div>
                    <div class="query-input-group">
                        <input type="text" id="desk-query-input" class="input-text" placeholder="e.g. summarize dataset uploaded by staff..." onkeydown="if(event.key==='Enter') queryDeskData()">
                        <button class="btn-primary" onclick="queryDeskData()">Analyze</button>
                    </div>
                    <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 14px; min-height: 120px;" id="desk-results-area">
                        Dataset ready for natural language analysis.
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            <span>Incoming SMS Broadcast Sim</span>
                        </div>
                    </div>
                    <div style="font-size: 13px; color: var(--text-secondary);">
                        Simulate incoming SMS delivered by Android Companion Service:
                    </div>
                    <button class="btn-primary" onclick="simulateIncomingSmsPrompt()">Simulate Incoming SMS</button>
                    <button class="btn-sm" onclick="triggerMultimodalCapture()">Trigger Multimodal Capture</button>
                </div>
            </div>
        </section>

        <!-- TAB 5: CAMERA & VISION HUB -->
        <section id="tab-camera-vision" class="tab-panel">
            <div class="grid-2col">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            <span>Live Hardware Camera Capture</span>
                        </div>
                        <button class="btn-primary" onclick="triggerCameraCapture()" id="cam-capture-btn">Snap Frame</button>
                    </div>

                    <div class="cam-preview-box" id="cam-box">
                        <img id="cam-image" class="cam-preview-img" src="" style="display:none;" alt="Camera Frame">
                        <div id="cam-placeholder" style="color: var(--text-muted); font-size: 13px;">No frame captured yet. Click "Snap Frame".</div>
                        <div class="cam-overlay-status" id="cam-overlay-info">SENSOR: OV2640 | QVGA</div>
                    </div>

                    <div style="display: flex; gap: 8px;">
                        <button class="btn-primary" style="flex:1;" onclick="analyzeCurrentFrame()">Explain Picture (Vision AI)</button>
                        <button class="btn-sm" onclick="scanQRFromCurrentFrame()">Scan QR</button>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            <span>Multimodal Vision Analysis</span>
                        </div>
                    </div>

                    <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 14px; min-height: 180px;">
                        <div style="font-size: 11px; font-weight: 700; color: var(--accent); margin-bottom: 6px;">Vision Scene Breakdown:</div>
                        <div id="vision-description-text" style="font-size: 13px; line-height: 1.5; color: var(--text-primary);">
                            Capture a frame on the left and click "Explain Picture" to run Multimodal Vision.
                        </div>
                    </div>

                    <div style="margin-top: 10px;">
                        <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 6px;">Detected Objects:</div>
                        <div id="detected-objects-tags" style="display: flex; gap: 6px; flex-wrap: wrap;">
                            <span style="font-size: 11px; color: var(--text-muted);">None</span>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- TAB 6: AUTOMATIONS & NOTIFICATIONS -->
        <section id="tab-automations-hub" class="tab-panel">
            <div class="grid-2col">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            <span>Automations Center</span>
                        </div>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Scheduled Automations:</span>
                        <span class="metric-value">Active (2 tasks registered)</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Execution Mode:</span>
                        <span class="metric-value">Background Async Queue</span>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            <span>Smart Notifications</span>
                        </div>
                    </div>
                    <div style="font-size: 13px; color: var(--text-secondary);">
                        Proactive glasses notifications: Calendar warnings, high-priority emails, SMS summaries.
                    </div>
                </div>
            </div>
        </section>

        <!-- TAB 7: TELEMETRY & DEVICE HEALTH -->
        <section id="tab-system-diagnostics" class="tab-panel">
            <div class="grid-2col">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            <span>System Hardware Telemetry</span>
                        </div>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Microcontroller Board:</span>
                        <span class="metric-value">Seeed Studio XIAO ESP32-S3 Sense</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Microphone Subsystem:</span>
                        <span class="metric-value">MSM261D PDM (16 kHz, 16-bit DC Filtered)</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Audio DAC Amplifier:</span>
                        <span class="metric-value">MAX98357A I2S (Pins D8, D9, D10)</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Mini OLED Display:</span>
                        <span class="metric-value">0.42" SSD1306 I2C (Pins D4 SDA, D5 SCL)</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Camera Sensor:</span>
                        <span class="metric-value">OV2640 / OV3660 2MP Sense Header</span>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            <span>Cloud & Local Intelligence Status</span>
                        </div>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Primary LLM Provider:</span>
                        <span class="metric-value">Google Gemini (gemini-2.5-flash)</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Local Request Router:</span>
                        <span class="metric-value">Authoritative Multi-turn Synthesizer</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Academic Research Engine:</span>
                        <span class="metric-value">arXiv API + CrossRef + PubMed</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Web Search Grounding:</span>
                        <span class="metric-value">DuckDuckGo Real-Time Search</span>
                    </div>
                </div>
            </div>
        </section>

        <!-- TAB: WORKSPACE & ENVIRONMENT -->
        <section id="tab-workspace" class="tab-panel">
            <div id="view-workspace" class="grid-2col">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Workspace & Environment</div>
                    </div>
                    <div id="workspace-content" style="padding: 12px; font-size: 13px; color: var(--text-secondary);">
                        <div>Active Workspace: <strong>EVA Intelligent Edge Hub</strong></div>
                        <div style="margin-top: 8px;">Unified orchestration active across Gmail, Calendar, Contacts, and Local Device Storage.</div>
                        <button class="btn-sm" style="margin-top: 12px;" onclick="loadWorkspaceEnvironment()">Refresh Workspace</button>
                    </div>
                </div>
                <div class="card side-telemetry-panel">
                    <div class="card-header">
                        <div class="card-title">Environment Telemetry</div>
                    </div>
                    <div id="environment-telemetry" style="padding: 12px; font-size: 13px; color: var(--text-secondary);">
                        <div>Real-Time Insights & Context Freshness Monitoring Active.</div>
                    </div>
                </div>
            </div>
        </section>

    </main>

    <script>
        async function loadWorkspaceEnvironment() {
            try {
                const res = await fetch('/api/v1/workspace/environment');
                const data = await res.json();
                console.log('Workspace loaded:', data);
            } catch (err) {
                console.error('Workspace load error:', err);
            }
        }

        // State & Variables
        let eventCount = 0;
        let autoScroll = true;
        let lastCapturedImageBase64 = "";

        // Tab Switching
        function switchTab(tabId) {
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));

            const targetBtn = Array.from(document.querySelectorAll('.tab-button')).find(b => b.getAttribute('onclick').includes(tabId));
            if (targetBtn) targetBtn.classList.add('active');

            const targetPanel = document.getElementById('tab-' + tabId);
            if (targetPanel) targetPanel.classList.add('active');
        }

        // Auto-Scroll Toggle
        function toggleAutoScroll() {
            autoScroll = !autoScroll;
            document.getElementById('autoscroll-toggle-btn').innerText = 'Auto-scroll: ' + (autoScroll ? 'ON' : 'OFF');
        }

        // Clear Live Events
        function clearLiveEvents() {
            document.getElementById('live-stream-feed').innerHTML = '';
            eventCount = 0;
            document.getElementById('event-counter-badge').innerText = '0';
        }

        // Append Event to Live Stream UI
        function appendLiveEvent(evt) {
            eventCount++;
            document.getElementById('event-counter-badge').innerText = eventCount;

            const feed = document.getElementById('live-stream-feed');
            const entry = document.createElement('div');
            entry.className = `stream-entry entry-${evt.type || 'SYSTEM'}`;

            const timeStr = evt.timestamp ? new Date(evt.timestamp).toLocaleTimeString() : new Date().toLocaleTimeString();
            let summaryText = "";
            let metaHtml = "";

            if (evt.type === 'USER_QUERY') {
                summaryText = `User: "${evt.data?.message || ''}"`;
                metaHtml = `<span>Intent: ${evt.data?.intent || 'GENERAL'}</span> <span>ReqID: ${(evt.data?.request_id || '').substring(0,8)}</span>`;
                // Update OLED preview with user query
                updateOledDisplay(`Query: ${evt.data?.message || ''}`);
            } else if (evt.type === 'ASSISTANT_RESPONSE') {
                summaryText = `LARA: "${evt.data?.response || ''}"`;
                metaHtml = `<span>Latency: ${evt.data?.latency_ms || 0}ms</span> <span>Provider: ${evt.data?.llm_provider || 'local'}</span>`;
                // Update HUD
                updateOledDisplay(evt.data?.response || '');
                document.getElementById('voice-preview-text').innerText = evt.data?.response || '';
            } else if (evt.type === 'RESEARCH_SEARCH') {
                summaryText = `Academic Research Search: "${evt.data?.query || ''}" (${evt.data?.results_count || 0} papers found)`;
            } else if (evt.type === 'CAMERA_CAPTURE') {
                summaryText = `Camera frame captured (${evt.data?.resolution || 'QVGA'}) - Status: ${evt.data?.status || 'OK'}`;
            } else if (evt.type === 'VISION_ANALYZE') {
                summaryText = `Vision Analysis: "${evt.data?.description || ''}" (${evt.data?.latency_ms || 0}ms)`;
            } else {
                summaryText = JSON.stringify(evt.data || evt);
            }

            entry.innerHTML = `
                <div class="entry-header">
                    <span class="entry-type type-${evt.type || 'SYSTEM'}">${evt.type || 'EVENT'}</span>
                    <span class="entry-time">${timeStr}</span>
                </div>
                <div class="entry-body">${escapeHtml(summaryText)}</div>
                ${metaHtml ? `<div class="entry-meta">${metaHtml}</div>` : ''}
            `;

            feed.appendChild(entry);
            if (autoScroll) {
                feed.scrollTop = feed.scrollHeight;
            }
        }

        function escapeHtml(text) {
            if (!text) return '';
            return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
        }

        function updateOledDisplay(text) {
            const el = document.getElementById('oled-text');
            if (el) {
                el.innerText = text.substring(0, 80) + (text.length > 80 ? '...' : '');
            }
            const clockEl = document.getElementById('oled-clock');
            if (clockEl) {
                clockEl.innerText = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            }
        }

        // Hardware Status Updater
        async function updateHardwareStatus() {
            try {
                const res = await fetch('/api/v1/hardware/status');
                const data = await res.json();
                return data;
            } catch (e) {
                return null;
            }
        }

        // Simulators
        async function simulateIncomingSmsPrompt() {
            try {
                await fetch('/api/v1/sms/receive', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        sender: "Rahul Sharma",
                        phone: "+91 98765 43210",
                        body: "Hey, are you free for the project review meeting at 4 PM today?"
                    })
                });
                alert("Incoming SMS simulated.");
            } catch (e) {
                console.error(e);
            }
        }

        async function triggerMultimodalCapture() {
            try {
                await fetch('/api/v1/hardware/multimodal/capture', { method: 'POST' });
            } catch (e) {
                console.error(e);
            }
        }

        async function queryDeskData() {
            const input = document.getElementById('desk-query-input');
            const q = input.value.trim();
            if (!q) return;
            sendQuickPrompt(q);
        }

        // SSE Real-Time Connection
        function initSSEStream() {
            const sseStatusPill = document.getElementById('sse-status-pill');
            const sseStatusText = document.getElementById('sse-status-text');

            const evtSource = new EventSource('/api/v1/events/stream');

            evtSource.onopen = function() {
                sseStatusPill.className = "pill pill-live";
                sseStatusText.innerText = "SSE Stream Active";
            };

            evtSource.onmessage = function(e) {
                try {
                    const eventData = JSON.parse(e.data);
                    appendLiveEvent(eventData);
                } catch (err) {
                    console.error("SSE parse error", err);
                }
            };

            evtSource.onerror = function() {
                sseStatusPill.className = "pill pill-hw";
                sseStatusText.innerText = "Reconnecting SSE...";
            };
        }

        // Initial Recent Events Hydration
        async function loadRecentEvents() {
            try {
                const res = await fetch('/api/v1/events/recent');
                const data = await res.json();
                if (data && data.events) {
                    data.events.forEach(evt => appendLiveEvent(evt));
                }
            } catch (e) {
                console.warn("Could not load recent events", e);
            }
        }

        // Quick Prompt Trigger
        async function sendQuickPrompt(promptText) {
            document.getElementById('playground-query-input').value = promptText;
            switchTab('ai-playground');
            await executePlaygroundQuery();
        }

        // Execute AI Playground Query
        async function executePlaygroundQuery() {
            const input = document.getElementById('playground-query-input');
            const query = input.value.trim();
            if (!query) return;

            const sendBtn = document.getElementById('playground-send-btn');
            const responseArea = document.getElementById('playground-response-area');
            sendBtn.disabled = true;
            sendBtn.innerText = "Processing...";
            responseArea.innerText = "Thinking & routing query...";

            try {
                const t0 = performance.now();
                const res = await fetch('/api/v1/agent/message', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: query,
                        session_id: 'web_console_session',
                        device_id: 'WebDashboard',
                        language: 'auto'
                    })
                });

                const data = await res.json();
                const tTotal = Math.round(performance.now() - t0);

                responseArea.innerText = data.response || "No response received.";
                document.getElementById('voice-preview-text').innerText = data.response || "";
                updateOledDisplay(data.response || "");

                // Update Telemetry Panel
                const meta = data.metadata || {};
                document.getElementById('meta-intent').innerText = meta.intent || (data.sources ? data.sources[0] : 'GENERAL');
                document.getElementById('meta-provider').innerText = meta.llm_provider || 'gemini-2.5-flash';
                document.getElementById('meta-fastpath').innerText = meta.fast_path ? 'YES' : 'NO';
                document.getElementById('meta-latency').innerText = `${meta.latency_ms || tTotal} ms`;
                document.getElementById('meta-sources').innerText = (data.sources || []).join(', ') || 'LLM';

                document.getElementById('raw-json-inspector').innerText = JSON.stringify(data, null, 2);

            } catch (err) {
                responseArea.innerText = "Error calling agent: " + err.message;
            } finally {
                sendBtn.disabled = false;
                sendBtn.innerText = "Send Query";
            }
        }

        // Academic Research Search
        function setResearchQuery(q) {
            document.getElementById('research-query-input').value = q;
            executeResearchSearch();
        }

        async function executeResearchSearch() {
            const query = document.getElementById('research-query-input').value.trim();
            if (!query) return;

            const btn = document.getElementById('research-search-btn');
            const container = document.getElementById('research-results-container');
            btn.disabled = true;
            btn.innerText = "Searching...";
            container.innerHTML = '<div style="text-align:center; padding:30px; color:var(--text-secondary);">Querying arXiv and scientific paper index...</div>';

            try {
                const res = await fetch(`/api/v1/research/search?query=${encodeURIComponent(query)}&limit=6`);
                const data = await res.json();
                const papers = data.papers || [];

                if (papers.length === 0) {
                    container.innerHTML = `<div style="text-align:center; padding:30px; color:var(--text-secondary);">No papers found for "${escapeHtml(query)}".</div>`;
                    return;
                }

                let html = "";
                papers.forEach(p => {
                    const authors = (p.authors || ['Unknown']).join(', ');
                    html += `
                        <div class="paper-card">
                            <div class="paper-title">
                                <a href="${p.pdf_url || p.url || '#'}" target="_blank">${escapeHtml(p.title || 'Research Paper')}</a>
                            </div>
                            <div class="paper-meta">
                                <span>Authors: ${escapeHtml(authors)}</span>
                                <span>Published: ${p.published || 'Recent'}</span>
                                <span>Source: ${p.source || 'arXiv'}</span>
                            </div>
                            <div class="paper-abstract">${escapeHtml(p.summary || p.abstract || 'No abstract available.')}</div>
                            <div class="paper-actions">
                                <a href="${p.pdf_url || p.url || '#'}" target="_blank" class="btn-sm" style="text-decoration:none;">View Paper PDF</a>
                                <button class="btn-sm" onclick="sendQuickPrompt('Explain paper: ${escapeHtml(p.title)}')">Ask LARA to Explain</button>
                            </div>
                        </div>
                    `;
                });

                container.innerHTML = html;
            } catch (err) {
                container.innerHTML = `<div style="color:var(--red); padding:20px;">Error fetching papers: ${err.message}</div>`;
            } finally {
                btn.disabled = false;
                btn.innerText = "Search Papers";
            }
        }

        // Camera Frame Capture
        async function triggerCameraCapture() {
            const btn = document.getElementById('cam-capture-btn');
            btn.disabled = true;
            btn.innerText = "Capturing...";

            try {
                const res = await fetch('/api/v1/hardware/camera/capture');
                const data = await res.json();

                if (data.base64_data) {
                    lastCapturedImageBase64 = data.base64_data;
                    const img = document.getElementById('cam-image');
                    img.src = "data:image/jpeg;base64," + data.base64_data;
                    img.style.display = "block";
                    document.getElementById('cam-placeholder').style.display = "none";
                    document.getElementById('cam-overlay-info').innerText = `SENSOR: OV2640 | ${data.resolution || 'QVGA'} | ${data.fps || 15} FPS`;
                }
            } catch (e) {
                console.error("Camera capture failed", e);
            } finally {
                btn.disabled = false;
                btn.innerText = "Snap Frame";
            }
        }

        // Analyze Picture with Vision AI
        async function analyzeCurrentFrame() {
            if (!lastCapturedImageBase64) {
                await triggerCameraCapture();
            }

            const descEl = document.getElementById('vision-description-text');
            const tagsEl = document.getElementById('detected-objects-tags');
            descEl.innerText = "Analyzing frame with Gemini Multimodal Vision...";

            try {
                const res = await fetch('/api/v1/vision/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image_base64: lastCapturedImageBase64,
                        prompt: "Explain what you see in this photo captured by smart glasses."
                    })
                });

                const data = await res.json();
                descEl.innerText = data.description || "Scene analysis completed.";

                if (data.objects && data.objects.length > 0) {
                    tagsEl.innerHTML = data.objects.map(obj => `<span class="pill pill-cloud">${escapeHtml(obj)}</span>`).join(' ');
                } else {
                    tagsEl.innerHTML = '<span style="font-size: 11px; color: var(--text-muted);">None detected</span>';
                }

                updateOledDisplay(data.description || "Vision analysis done.");
                document.getElementById('voice-preview-text').innerText = data.description || "";
            } catch (err) {
                descEl.innerText = "Vision analysis error: " + err.message;
            }
        }

        // Scan QR from Current Frame
        async function scanQRFromCurrentFrame() {
            const descEl = document.getElementById('vision-description-text');
            descEl.innerText = "Scanning frame for QR code...";

            try {
                const res = await fetch('/api/v1/vision/qr/scan', { method: 'POST' });
                const data = await res.json();
                if (data.success && data.data) {
                    descEl.innerText = `Decoded QR Code: ${data.data}`;
                    updateOledDisplay(`QR: ${data.data}`);
                } else {
                    descEl.innerText = "No QR code detected in the current camera frame.";
                }
            } catch (err) {
                descEl.innerText = "QR scan error: " + err.message;
            }
        }

        // Initialize on page load
        window.addEventListener('DOMContentLoaded', () => {
            initSSEStream();
            loadRecentEvents();
        });
    </script>
</body>
</html>
"""
