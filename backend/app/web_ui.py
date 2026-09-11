def get_dashboard_html() -> str:
    """Returns the luxury personal assistant dashboard for the Smart Glasses AI with full storage, Google OAuth write, and audio capabilities."""
    return r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LARA Smart Glasses AI — Executive Console & Storage Hub</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #FBF9F5;
            --surface: #FFFFFF;
            --surface-subtle: #F6F3ED;
            --border: #EBE6DD;
            --border-focus: #C5A880;
            --gold: #C5A880;
            --gold-light: #F4ECE1;
            --gold-hover: #B5966B;
            --espresso: #2E2522;
            --charcoal: #1A1A1A;
            --text-muted: #6B6661;
            --text-light: #8E8883;
            --sage: #4A6B56;
            --sage-bg: #EDF3EF;
            --terracotta: #9E4A44;
            --terracotta-bg: #F9EFEF;
            --shadow: 0 4px 20px rgba(44, 42, 41, 0.04);
            --shadow-card: 0 8px 30px rgba(44, 42, 41, 0.06);
            --radius-lg: 16px;
            --radius-md: 12px;
            --radius-sm: 8px;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg);
            color: var(--charcoal);
            min-height: 100vh;
            padding: 32px 20px 48px;
            display: flex;
            justify-content: center;
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
        }

        .container {
            width: 100%;
            max-width: 900px;
            display: flex;
            flex-direction: column;
            gap: 24px;
        }

        /* Header */
        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border);
        }

        .brand-title {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 24px;
            font-weight: 600;
            letter-spacing: 1.5px;
            color: var(--espresso);
            text-transform: uppercase;
        }

        .brand-subtitle {
            font-size: 12px;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: var(--gold);
            font-weight: 500;
            margin-top: 2px;
        }

        .header-actions {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .btn-gold {
            background: var(--surface);
            color: var(--espresso);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 9px 16px;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.8px;
            text-transform: uppercase;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .btn-gold:hover {
            border-color: var(--gold);
            background: var(--gold-light);
            color: var(--espresso);
        }

        .btn-speaker-toggle {
            background: var(--surface);
            color: var(--espresso);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 9px 14px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .btn-speaker-toggle.active {
            background: var(--sage-bg);
            border-color: var(--sage);
            color: var(--sage);
        }

        /* Luxury Cards */
        .card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 24px;
            box-shadow: var(--shadow);
            transition: box-shadow 0.2s ease;
        }

        .card:hover {
            box-shadow: var(--shadow-card);
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 18px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--surface-subtle);
        }

        .card-title {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 18px;
            font-weight: 600;
            letter-spacing: 0.5px;
            color: var(--espresso);
        }

        .card-subtitle {
            font-size: 12px;
            color: var(--text-light);
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }

        /* Context Sub-Bar */
        .context-bar {
            display: flex;
            align-items: center;
            gap: 16px;
            font-size: 13px;
            color: var(--text-muted);
            margin-bottom: 18px;
            padding: 10px 16px;
            background: var(--surface-subtle);
            border-radius: var(--radius-sm);
            flex-wrap: wrap;
        }

        .context-item {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .context-sep {
            color: var(--border);
        }

        /* Dropzone / Upload Box */
        .upload-zone {
            border: 2px dashed var(--border-focus);
            border-radius: var(--radius-md);
            padding: 20px;
            text-align: center;
            background: var(--surface-subtle);
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
        }

        .upload-zone:hover {
            background: var(--gold-light);
            border-color: var(--gold);
        }

        .file-badge {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 10px 14px;
            font-size: 13px;
            margin-top: 10px;
        }

        /* Chat / Conversation Feed */
        .conversation-feed {
            display: flex;
            flex-direction: column;
            gap: 12px;
            max-height: 320px;
            overflow-y: auto;
            padding: 16px;
            background: var(--surface-subtle);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            margin-bottom: 16px;
        }

        .msg-bubble {
            display: flex;
            flex-direction: column;
            gap: 4px;
            padding: 12px 16px;
            border-radius: var(--radius-md);
            font-size: 14px;
            line-height: 1.5;
            max-width: 90%;
            position: relative;
        }

        .msg-user {
            background: var(--gold-light);
            color: var(--espresso);
            align-self: flex-end;
            border: 1px solid rgba(197, 168, 128, 0.3);
        }

        .msg-assistant {
            background: var(--surface);
            color: var(--charcoal);
            align-self: flex-start;
            border: 1px solid var(--border);
            box-shadow: 0 2px 8px rgba(44, 42, 41, 0.02);
        }

        .msg-sender {
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: var(--gold-hover);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .msg-user .msg-sender {
            color: var(--espresso);
        }

        .btn-replay-audio {
            background: none;
            border: none;
            color: var(--gold-hover);
            cursor: pointer;
            font-size: 13px;
            padding: 2px 6px;
            border-radius: 4px;
            transition: all 0.2s;
        }

        .btn-replay-audio:hover {
            background: var(--gold-light);
            color: var(--espresso);
        }

        .msg-time {
            font-size: 10px;
            color: var(--text-light);
            margin-top: 4px;
            align-self: flex-end;
        }

        /* Quick Voice Queries Bar */
        .quick-actions-bar {
            display: flex;
            gap: 8px;
            overflow-x: auto;
            padding-bottom: 12px;
            margin-bottom: 12px;
            scrollbar-width: thin;
        }

        .btn-quick-chip {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 6px 12px;
            font-size: 12px;
            color: var(--espresso);
            white-space: nowrap;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .btn-quick-chip:hover {
            border-color: var(--gold);
            background: var(--gold-light);
        }

        /* Inputs & Controls */
        .control-row {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .input-luxury {
            flex: 1;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 12px 16px;
            color: var(--charcoal);
            font-family: inherit;
            font-size: 14px;
            outline: none;
            transition: all 0.2s ease;
        }

        .input-luxury:focus {
            border-color: var(--border-focus);
            box-shadow: 0 0 0 3px rgba(197, 168, 128, 0.15);
        }

        .btn-primary {
            background: var(--espresso);
            color: var(--surface);
            border: none;
            border-radius: var(--radius-sm);
            padding: 12px 20px;
            font-size: 13px;
            font-weight: 600;
            letter-spacing: 0.5px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .btn-primary:hover {
            background: var(--charcoal);
            box-shadow: 0 4px 12px rgba(46, 37, 34, 0.2);
        }

        .btn-talk {
            background: var(--gold);
            color: var(--surface);
            border: none;
            border-radius: var(--radius-sm);
            padding: 12px 18px;
            font-size: 13px;
            font-weight: 600;
            letter-spacing: 0.5px;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .btn-talk:hover {
            background: var(--gold-hover);
            box-shadow: 0 4px 12px rgba(197, 168, 128, 0.3);
        }

        .btn-talk.recording {
            background: var(--terracotta);
            animation: pulse-mic 1.2s infinite;
        }

        @keyframes pulse-mic {
            0% { box-shadow: 0 0 0 0 rgba(158, 74, 68, 0.6); }
            70% { box-shadow: 0 0 0 10px rgba(158, 74, 68, 0); }
            100% { box-shadow: 0 0 0 0 rgba(158, 74, 68, 0); }
        }

        /* 2-Column Grid */
        .grid-2col {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
        }

        @media (max-width: 700px) {
            .grid-2col { grid-template-columns: 1fr; }
            .header { flex-direction: column; align-items: flex-start; gap: 14px; }
        }

        /* Tables & Badges */
        .status-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }

        .status-table td {
            padding: 8px 0;
            border-bottom: 1px solid var(--surface-subtle);
        }

        .status-table tr:last-child td {
            border-bottom: none;
        }

        .status-table td:last-child {
            text-align: right;
        }

        .badge-status {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }

        .badge-connected {
            background: var(--sage-bg);
            color: var(--sage);
        }

        .badge-disconnected {
            background: var(--terracotta-bg);
            color: var(--terracotta);
        }

        .badge-connected::before,
        .badge-disconnected::before {
            content: "";
            display: inline-block;
            width: 6px;
            height: 6px;
            border-radius: 50%;
        }

        .badge-connected::before { background-color: var(--sage); }
        .badge-disconnected::before { background-color: var(--terracotta); }

        /* Developer Diagnostics */
        .diagnostics-details {
            margin-top: 8px;
        }

        .diagnostics-summary {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-light);
            cursor: pointer;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        .diagnostics-content {
            margin-top: 10px;
            padding: 14px;
            background: var(--surface-subtle);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            font-size: 12px;
            color: var(--text-muted);
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        /* Upload Zone & File Management */
        .upload-zone {
            border: 2px dashed var(--border);
            border-radius: var(--radius-md);
            padding: 24px 16px;
            text-align: center;
            background: var(--surface-subtle);
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 6px;
            margin-bottom: 16px;
        }

        .upload-zone:hover {
            border-color: var(--gold);
            background: var(--gold-light);
        }

        .file-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .file-badge {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 14px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            font-size: 13px;
            transition: all 0.2s ease;
        }

        .file-badge:hover {
            border-color: var(--gold);
            box-shadow: var(--shadow);
        }

        .btn-replay-audio {
            background: transparent;
            border: none;
            cursor: pointer;
            font-size: 14px;
            padding: 2px 6px;
            border-radius: 4px;
            transition: background 0.2s;
        }

        .btn-replay-audio:hover {
            background: var(--gold-light);
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="header">
            <div>
                <div class="brand-title">LARA Smart Glasses</div>
                <div class="brand-subtitle">Executive AI Companion & Unified Storage Hub</div>
            </div>
            <div class="header-actions">
                <button class="btn-speaker-toggle active" id="btn-speaker" onclick="toggleSpeaker()">
                    🔊 Laptop Speaker: ON
                </button>
                <a href="/api/v1/auth/google" target="_blank" class="btn-gold" id="btn-oauth">
                    Connect Google Account
                </a>
            </div>
        </header>

        <!-- Assistant Main Voice & Interaction Card -->
        <div class="card">
            <div class="card-header">
                <div>
                    <h2 class="card-title">Assistant Voice & Console</h2>
                    <div class="card-subtitle" id="greeting-txt">Good afternoon. How may I assist?</div>
                </div>
                <span class="badge-status badge-connected" id="badge-ai-mode">Cloud AI</span>
            </div>

            <!-- Current Context Sub-Bar -->
            <div class="context-bar">
                <div class="context-item">
                    <span>Time:</span> <strong id="ctx-time">--:--</strong>
                </div>
                <span class="context-sep">·</span>
                <div class="context-item">
                    <span>Location:</span> <strong id="ctx-location">Nagpur, India</strong>
                </div>
                <span class="context-sep">·</span>
                <div class="context-item">
                    <span>Google Account:</span> <strong id="ctx-google-user">Connected</strong>
                </div>
                <span class="context-sep">·</span>
                <div class="context-item">
                    <span>Battery:</span> <strong>85%</strong>
                </div>
            </div>

            <!-- Conversation Feed -->
            <div class="conversation-feed" id="chat-box">
                <div class="msg-bubble msg-assistant">
                    <div class="msg-sender">
                        <span>LARA Assistant</span>
                        <button class="btn-replay-audio" onclick="speakText('I am ready. You can speak or type your request below.')" title="Listen on Laptop Speaker">🔊</button>
                    </div>
                    <div>I am ready. Ask a question, check your email, inspect your schedule, or upload a document below.</div>
                </div>
            </div>

            <!-- Quick Capability Test Suite (5 Core Wearable Benchmarks + Document Summarization) -->
            <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: var(--gold-hover); margin-bottom: 6px;">
                ⚡ Wearable Benchmark Suite:
            </div>
            <div class="quick-actions-bar">
                <button class="btn-quick-chip" style="background:var(--gold-light); font-weight:600;" onclick="runFullCapabilitySuite()">▶️ Run Core 5 Suite</button>
                <button class="btn-quick-chip" onclick="sendQuickMessage('Check my unread emails')">✉️ 1. Check Email</button>
                <button class="btn-quick-chip" onclick="sendQuickMessage('Read my latest email')">📖 2. Read Email</button>
                <button class="btn-quick-chip" onclick="sendQuickMessage('What is 125 plus 375?')">🧮 3. Calculation (125+375)</button>
                <button class="btn-quick-chip" onclick="sendQuickMessage('What is on my calendar today?')">📅 4. Calendar Events</button>
                <button class="btn-quick-chip" onclick="sendQuickMessage('What are the key benefits of smart glasses with AI?')">🤖 5. AI Q&A</button>
                <button class="btn-quick-chip" onclick="sendQuickMessage('Summarize my uploaded document')">📄 Summarize Document</button>
                <button class="btn-quick-chip" onclick="sendQuickMessage('शुभ सकाळ, माझं आजचं कॅलेंडर दाखव')">🇮🇳 Marathi</button>
                <button class="btn-quick-chip" onclick="sendQuickMessage('सुप्रभात, आज मेरा क्या शेड्यूल है?')">🇮🇳 Hindi</button>
            </div>

            <!-- Input & Controls -->
            <div class="control-row">
                <input type="text" id="user-input" class="input-luxury" placeholder="Ask LARA anything or click 🎙️ to talk..." onkeydown="if(event.key==='Enter') sendMessage()">
                <button class="btn-talk" id="btn-mic" onclick="toggleMicrophone()" title="Push to Talk with Microphone">🎙️ Talk</button>
                <button class="btn-primary" onclick="sendMessage()">Send</button>
            </div>
        </div>

        <!-- Unified Storage & Document Hub -->
        <div class="card" id="storage-card">
            <div class="card-header">
                <div>
                    <h2 class="card-title">Unified File & Document Storage</h2>
                    <div class="card-subtitle">PDF, DOCX, TXT, and Image Processing Pipeline</div>
                </div>
                <span class="badge-status badge-connected" id="badge-storage-status">STORAGE READY</span>
            </div>

            <div class="upload-zone" onclick="document.getElementById('file-upload-input').click()">
                <input type="file" id="file-upload-input" style="display:none" onchange="handleFileUpload(event)" accept=".pdf,.docx,.txt,.csv,.jpg,.jpeg,.png,.webp">
                <div style="font-size:24px;">📁</div>
                <div style="font-weight:600; color:var(--espresso);">Click to Upload Document or Image</div>
                <div style="font-size:12px; color:var(--text-muted);">Supports PDF, DOCX, TXT, CSV, and JPG/PNG (Max 20MB)</div>
            </div>

            <div id="file-list-container">
                <!-- Uploaded file items populated here -->
            </div>
        </div>

        <!-- 2-Column Grid: Services & Device -->
        <div class="grid-2col">
            <!-- Connected Services -->
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Connected Services</h2>
                </div>
                <table class="status-table">
                    <tr>
                        <td>Google Account</td>
                        <td><span class="badge-status badge-disconnected" id="badge-google">Disconnected</span></td>
                    </tr>
                    <tr>
                        <td>Gmail API (Read + Send)</td>
                        <td><span class="badge-status badge-disconnected" id="badge-gmail">Disconnected</span></td>
                    </tr>
                    <tr>
                        <td>Google Calendar</td>
                        <td><span class="badge-status badge-disconnected" id="badge-cal">Disconnected</span></td>
                    </tr>
                    <tr>
                        <td>Document Storage Engine</td>
                        <td><span class="badge-status badge-connected" id="badge-storage">Active (Local SQLite)</span></td>
                    </tr>
                    <tr>
                        <td>Backend Gateway</td>
                        <td><span class="badge-status badge-connected" id="badge-backend">Connected</span></td>
                    </tr>
                </table>
            </div>

            <!-- Device Status -->
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Hardware Telemetry</h2>
                </div>
                <table class="status-table">
                    <tr>
                        <td>Peripheral Status</td>
                        <td><strong style="color:var(--espresso);">Software Baseline (ESP32 Ready)</strong></td>
                    </tr>
                    <tr>
                        <td>Laptop Microphone (STT)</td>
                        <td><span class="badge-status badge-connected" id="badge-stt">Web Speech Active</span></td>
                    </tr>
                    <tr>
                        <td>Laptop Speaker (TTS)</td>
                        <td><span class="badge-status badge-connected" id="badge-tts">Speaker Ready</span></td>
                    </tr>
                    <tr>
                        <td>Google OAuth Scopes</td>
                        <td><strong style="font-size:11px; color:var(--sage);">Read + Send + Calendar</strong></td>
                    </tr>
                </table>
            </div>
        </div>

        <!-- Developer Diagnostics -->
        <details class="diagnostics-details">
            <summary class="diagnostics-summary">Developer Diagnostics & Latency Breakdown</summary>
            <div class="diagnostics-content">
                <div>Backend Engine: <strong>FastAPI · Port 8001</strong></div>
                <div>LLM Provider: <strong id="diag-llm">Gemini Flash</strong></div>
                <div>Session ID: <span id="diag-session" style="font-family:monospace;">--</span></div>
            </div>
        </details>
    </div>

    <script>
        const sessionId = "web_user_" + Math.random().toString(36).substring(2, 9);
        document.getElementById('diag-session').textContent = sessionId;

        let speakerEnabled = true;
        let recognition = null;
        let isRecording = false;

        // 1. Web Speech Synthesis (Speaker Relay)
        function sanitizeSpeechText(text) {
            if (!text) return "";
            return text
                .replace(/[*_#`~]/g, '')
                .replace(/https?:\/\/\S+/g, 'link')
                .replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1')
                .replace(/•/g, ', ')
                .replace(/\s+/g, ' ')
                .trim();
        }

        function speakText(text) {
            if (!speakerEnabled || !('speechSynthesis' in window)) return;
            
            window.speechSynthesis.cancel();
            const clean = sanitizeSpeechText(text);
            if (!clean) return;

            const utterance = new SpeechSynthesisUtterance(clean);
            utterance.rate = 1.05;
            utterance.pitch = 1.0;

            const hasDevanagari = /[\u0900-\u097F]/.test(clean);
            const voices = window.speechSynthesis.getVoices();

            if (hasDevanagari) {
                const hiVoice = voices.find(v => v.lang.includes('hi') || v.lang.includes('mr'));
                if (hiVoice) utterance.voice = hiVoice;
                utterance.lang = hiVoice ? hiVoice.lang : 'hi-IN';
            } else {
                const enVoice = voices.find(v => v.lang.includes('en-IN') || v.lang.includes('en-US') || v.lang.includes('en-GB'));
                if (enVoice) utterance.voice = enVoice;
            }

            window.speechSynthesis.speak(utterance);
        }

        function toggleSpeaker() {
            speakerEnabled = !speakerEnabled;
            const btn = document.getElementById('btn-speaker');
            if (speakerEnabled) {
                btn.className = "btn-speaker-toggle active";
                btn.textContent = "🔊 Laptop Speaker: ON";
                speakText("Laptop speaker audio enabled.");
            } else {
                btn.className = "btn-speaker-toggle";
                btn.textContent = "🔈 Laptop Speaker: OFF";
                window.speechSynthesis.cancel();
            }
        }

        // 2. File Upload & Document Management
        async function handleFileUpload(event) {
            const file = event.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append("file", file);
            formData.append("source", "web");

            const zone = document.querySelector('.upload-zone');
            zone.innerHTML = '<div style="font-weight:600; color:var(--gold-hover);">⏳ Uploading and processing ' + escapeHtml(file.name) + '...</div>';

            try {
                const isImg = file.type.startsWith('image/');
                const endpoint = isImg ? '/api/v1/images/upload' : '/api/v1/files/upload';
                const resp = await fetch(endpoint, {
                    method: 'POST',
                    body: formData
                });

                if (resp.ok) {
                    const data = await resp.json();
                    zone.innerHTML = '<div style="font-size:24px;">✅</div>' +
                        '<div style="font-weight:600; color:var(--sage);">Successfully Uploaded ' + escapeHtml(data.filename) + '</div>' +
                        '<div style="font-size:12px; color:var(--text-muted);">' + (data.has_extracted_text ? 'Indexed text successfully. LARA can now answer questions about it.' : 'Image saved.') + '</div>';
                    
                    fetchRecentFiles();
                } else {
                    const err = await resp.json();
                    zone.innerHTML = '<div style="font-weight:600; color:var(--terracotta);">❌ Upload failed: ' + escapeHtml(err.message || 'Error') + '</div>';
                }
            } catch (err) {
                zone.innerHTML = '<div style="font-weight:600; color:var(--terracotta);">❌ Upload failed: ' + escapeHtml(err.message) + '</div>';
            }
        }

        async function fetchRecentFiles() {
            try {
                const resp = await fetch('/api/v1/files?limit=5');
                if (resp.ok) {
                    const data = await resp.json();
                    const container = document.getElementById('file-list-container');
                    if (data.files && data.files.length > 0) {
                        let html = '';
                        data.files.forEach(f => {
                            html += '<div class="file-badge">' +
                                '<div><strong>📄 ' + escapeHtml(f.filename) + '</strong> <span style="font-size:11px; color:var(--text-light);">(' + (f.size_bytes/1024).toFixed(1) + ' KB)</span></div>' +
                                '<div style="display:flex; gap:6px;">' +
                                '<button class="btn-quick-chip" onclick="sendQuickMessage(\'Summarize ' + escapeHtml(f.filename) + '\')">Summarize</button>' +
                                '<button class="btn-quick-chip" style="color:var(--terracotta);" onclick="deleteFile(\'' + f.file_id + '\')">🗑️</button>' +
                                '</div>' +
                                '</div>';
                        });
                        container.innerHTML = html;
                    }
                }
            } catch (err) {
                console.warn("Could not fetch file list:", err);
            }
        }

        async function deleteFile(fileId) {
            try {
                const resp = await fetch('/api/v1/files/' + fileId, { method: 'DELETE' });
                if (resp.ok) {
                    fetchRecentFiles();
                }
            } catch (err) {
                console.warn("Delete error:", err);
            }
        }

        // 3. Speech Recognition & Voice Testing
        function initSpeechRecognition() {
            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRec) {
                console.warn("Web Speech Recognition not supported in this browser.");
                return;
            }

            recognition = new SpeechRec();
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'en-IN';

            recognition.onstart = function() {
                isRecording = true;
                const btn = document.getElementById('btn-mic');
                btn.className = "btn-talk recording";
                btn.textContent = "🔴 Listening...";
                document.getElementById('user-input').placeholder = "Listening to your voice...";
            };

            recognition.onresult = function(event) {
                let interimTranscript = '';
                let finalTranscript = '';
                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    } else {
                        interimTranscript += event.results[i][0].transcript;
                    }
                }
                const currentText = finalTranscript || interimTranscript;
                if (currentText) {
                    document.getElementById('user-input').value = currentText;
                }
            };

            recognition.onerror = function(event) {
                console.warn("Speech recognition error:", event.error);
                stopMicrophone();
            };

            recognition.onend = function() {
                stopMicrophone();
                const text = document.getElementById('user-input').value.trim();
                if (text) {
                    sendMessage();
                }
            };
        }

        function toggleMicrophone() {
            if (!recognition) {
                initSpeechRecognition();
            }
            if (!recognition) {
                alert("Your browser does not support Web Speech Recognition. Please use Google Chrome or Edge.");
                return;
            }

            if (isRecording) {
                recognition.stop();
                stopMicrophone();
            } else {
                window.speechSynthesis.cancel();
                document.getElementById('user-input').value = '';
                recognition.start();
            }
        }

        function stopMicrophone() {
            isRecording = false;
            const btn = document.getElementById('btn-mic');
            btn.className = "btn-talk";
            btn.textContent = "🎙️ Talk";
            document.getElementById('user-input').placeholder = "Ask LARA anything or click 🎙️ to talk...";
        }

        if ('speechSynthesis' in window) {
            window.speechSynthesis.onvoiceschanged = function() {
                window.speechSynthesis.getVoices();
            };
        }

        // 4. Status & Integration Polling
        async function updateStatus() {
            try {
                const hResp = await fetch('/api/v1/health');
                if (hResp.ok) {
                    const hData = await hResp.json();
                    const bBackend = document.getElementById('badge-backend');
                    if (bBackend) {
                        bBackend.className = "badge-status badge-connected";
                        bBackend.textContent = "Connected";
                    }
                    const dLLM = document.getElementById('diag-llm');
                    if (dLLM) dLLM.textContent = hData.llm_provider || "Gemini Flash";
                }
            } catch (err) {
                console.warn("Health check error:", err);
            }

            try {
                const dResp = await fetch('/api/v1/diagnostics/integrations');
                if (dResp.ok) {
                    const diagData = await dResp.json();
                    const isGoogle = diagData.google === 'connected';
                    const isGemini = diagData.gemini === 'available';

                    const badgeAi = document.getElementById('badge-ai-mode');
                    if (badgeAi) {
                        if (isGemini) {
                            badgeAi.className = "badge-status badge-connected";
                            badgeAi.textContent = "Cloud AI (Gemini)";
                        } else {
                            badgeAi.className = "badge-status badge-disconnected";
                            badgeAi.textContent = "Offline / Local";
                        }
                    }

                    const bGoogle = document.getElementById('badge-google');
                    const bGmail = document.getElementById('badge-gmail');
                    const bCal = document.getElementById('badge-cal');
                    const btnOauth = document.getElementById('btn-oauth');
                    const ctxGoogle = document.getElementById('ctx-google-user');

                    if (isGoogle) {
                        if (bGoogle) { bGoogle.className = "badge-status badge-connected"; bGoogle.textContent = "Connected"; }
                        if (bGmail) { bGmail.className = "badge-status badge-connected"; bGmail.textContent = "Active (Read + Send)"; }
                        if (bCal) { bCal.className = "badge-status badge-connected"; bCal.textContent = "Active"; }
                        if (ctxGoogle) ctxGoogle.textContent = "Connected (Write Enabled)";
                        if (btnOauth) {
                            btnOauth.textContent = "Google Connected";
                            btnOauth.style.borderColor = "var(--sage)";
                        }
                    } else {
                        if (bGoogle) { bGoogle.className = "badge-status badge-disconnected"; bGoogle.textContent = "Disconnected"; }
                        if (bGmail) { bGmail.className = "badge-status badge-disconnected"; bGmail.textContent = "Disconnected"; }
                        if (bCal) { bCal.className = "badge-status badge-disconnected"; bCal.textContent = "Disconnected"; }
                        if (ctxGoogle) ctxGoogle.textContent = "Disconnected";
                        if (btnOauth) {
                            btnOauth.textContent = "Connect Google Account";
                            btnOauth.style.borderColor = "var(--border)";
                        }
                    }
                }
            } catch (err) {
                console.warn("Diagnostics check error:", err);
            }

            try {
                const cResp = await fetch('/api/v1/context');
                if (cResp.ok) {
                    const cData = await cResp.json();
                    if (cData.time) {
                        const ctxTime = document.getElementById('ctx-time');
                        if (ctxTime) ctxTime.textContent = cData.time.local_time || "--";
                        const period = cData.time.period || "afternoon";
                        const greet = document.getElementById('greeting-txt');
                        if (greet) greet.textContent = "Good " + period + ". How may I assist?";
                    }
                    if (cData.location) {
                        const ctxLoc = document.getElementById('ctx-location');
                        if (ctxLoc) ctxLoc.textContent = cData.location.city + ", " + cData.location.country;
                    }
                }
            } catch (err) {
                console.warn("Context fetch error:", err);
            }
        }

        // 5. Send Message & Speak Reply
        async function sendMessage() {
            const input = document.getElementById('user-input');
            const msg = input.value.trim();
            if (!msg) return;
            input.value = '';
            await postMessage(msg);
        }

        async function sendQuickMessage(msg) {
            await postMessage(msg);
        }

        async function runFullCapabilitySuite() {
            const suite = [
                "Check my unread emails",
                "Read my latest email",
                "What is 125 plus 375?",
                "What is on my calendar today?",
                "What are the key benefits of smart glasses with AI?"
            ];
            for (let i = 0; i < suite.length; i++) {
                await postMessage(suite[i]);
                await new Promise(resolve => setTimeout(resolve, 2500));
            }
        }

        async function postMessage(messageText) {
            const chatBox = document.getElementById('chat-box');
            
            const userDiv = document.createElement('div');
            userDiv.className = 'msg-bubble msg-user';
            userDiv.innerHTML = '<span class="msg-sender">Transcript</span><div>' + escapeHtml(messageText) + '</div>';
            chatBox.appendChild(userDiv);
            chatBox.scrollTop = chatBox.scrollHeight;

            const astDiv = document.createElement('div');
            astDiv.className = 'msg-bubble msg-assistant';
            astDiv.innerHTML = '<span class="msg-sender">LARA Assistant</span><div>Thinking...</div>';
            chatBox.appendChild(astDiv);
            chatBox.scrollTop = chatBox.scrollHeight;

            const tStart = performance.now();

            try {
                const resp = await fetch('/api/v1/agent/message', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: sessionId,
                        message: messageText,
                        language: "auto",
                        locale: "en-IN",
                        context: null
                    })
                });

                const tDuration = (performance.now() - tStart).toFixed(0);

                if (resp.ok) {
                    const data = await resp.json();
                    const replyText = data.response || "No response received.";
                    const lat = data.metadata && data.metadata.latency_ms ? data.metadata.latency_ms.toFixed(0) : tDuration;
                    
                    astDiv.innerHTML = '<div class="msg-sender">' +
                        '<span>LARA Response</span>' +
                        '<button class="btn-replay-audio" onclick="speakText(this.getAttribute(\'data-text\'))" data-text="' + escapeHtml(replyText).replace(/"/g, '&quot;') + '" title="Replay on Laptop Speaker">🔊</button>' +
                        '</div>' +
                        '<div>' + escapeHtml(replyText) + '</div>' +
                        '<div class="msg-time">Latency: ' + lat + ' ms</div>';
                    
                    speakText(replyText);
                } else {
                    const errJson = await resp.json().catch(() => ({}));
                    astDiv.innerHTML = '<span class="msg-sender" style="color:var(--terracotta);">Error</span><div>' + escapeHtml(errJson.message || ('HTTP ' + resp.status)) + '</div>';
                }
            } catch (err) {
                astDiv.innerHTML = '<span class="msg-sender" style="color:var(--terracotta);">Error</span><div>Unable to reach assistant: ' + escapeHtml(err.message) + '</div>';
            }

            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function escapeHtml(text) {
            if (!text) return "";
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        initSpeechRecognition();
        updateStatus();
        fetchRecentFiles();
        setInterval(updateStatus, 5000);
    </script>
</body>
</html>
"""
