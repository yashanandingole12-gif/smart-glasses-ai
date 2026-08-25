def get_dashboard_html() -> str:
    """Returns the lightweight, responsive development dashboard for the Smart Glasses AI."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Glasses AI - Developer Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0A0E14;
            --surface: #151B23;
            --border: #30363D;
            --cyan: #00E5FF;
            --emerald: #00E676;
            --red: #FF5252;
            --text: #F0F6FC;
            --text-sec: #8B949E;
            --card-bg: rgba(21, 27, 35, 0.85);
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Outfit', -apple-system, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            min-height: 100vh;
            padding: 24px;
            display: flex;
            justify-content: center;
        }
        .container {
            width: 100%;
            max-width: 860px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--border);
            padding-bottom: 16px;
        }
        .title-group h1 {
            font-size: 24px;
            font-weight: 700;
            letter-spacing: 0.5px;
            color: var(--cyan);
        }
        .title-group p {
            font-size: 13px;
            color: var(--text-sec);
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 10px;
        }
        .status-pill {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 10px 14px;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .pill-label {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: var(--text-sec);
        }
        .pill-value {
            font-size: 13px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
        }
        .dot-green { background: var(--emerald); box-shadow: 0 0 8px rgba(0, 230, 118, 0.6); }
        .dot-red { background: var(--red); box-shadow: 0 0 8px rgba(255, 82, 82, 0.6); }
        
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 20px;
            backdrop-filter: blur(10px);
        }
        .card h2 {
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--cyan);
            margin-bottom: 14px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .context-row {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
            font-size: 14px;
        }
        .context-item {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        .context-item span:first-child {
            font-size: 11px;
            color: var(--text-sec);
            text-transform: uppercase;
        }
        .context-item span:last-child {
            font-weight: 600;
            color: var(--text);
        }
        
        /* Chat UI */
        .chat-box {
            display: flex;
            flex-direction: column;
            gap: 12px;
            max-height: 280px;
            overflow-y: auto;
            padding: 12px;
            background: rgba(10, 14, 20, 0.6);
            border: 1px solid var(--border);
            border-radius: 10px;
            margin-bottom: 16px;
            font-family: 'Outfit', sans-serif;
        }
        .message {
            display: flex;
            flex-direction: column;
            gap: 4px;
            padding: 10px 14px;
            border-radius: 8px;
            font-size: 14px;
            line-height: 1.5;
        }
        .msg-user {
            background: rgba(0, 229, 255, 0.1);
            border-left: 3px solid var(--cyan);
            align-self: flex-start;
            max-width: 90%;
        }
        .msg-assistant {
            background: rgba(0, 230, 118, 0.08);
            border-left: 3px solid var(--emerald);
            align-self: flex-start;
            max-width: 95%;
        }
        .msg-header {
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.5px;
        }
        .msg-user .msg-header { color: var(--cyan); }
        .msg-assistant .msg-header { color: var(--emerald); }
        .msg-latency {
            font-size: 10px;
            color: var(--text-sec);
            margin-top: 4px;
            font-family: 'JetBrains Mono', monospace;
        }
        
        .input-row {
            display: flex;
            gap: 10px;
        }
        .input-text {
            flex: 1;
            background: #0A0E14;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px 16px;
            color: #fff;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }
        .input-text:focus {
            border-color: var(--cyan);
        }
        .btn {
            background: var(--cyan);
            color: #0A0E14;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 700;
            font-size: 13px;
            letter-spacing: 0.5px;
            cursor: pointer;
            transition: opacity 0.2s, transform 0.1s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            text-decoration: none;
        }
        .btn:hover { opacity: 0.9; }
        .btn:active { transform: scale(0.98); }
        .btn-secondary {
            background: #21262D;
            color: var(--text);
            border: 1px solid var(--border);
        }
        .btn-secondary:hover {
            border-color: var(--cyan);
            color: var(--cyan);
        }
        .btn-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 14px;
        }
        
        .system-row {
            display: flex;
            gap: 20px;
            font-size: 13px;
            color: var(--text-sec);
        }
        .sys-item {
            display: flex;
            align-items: center;
            gap: 6px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="title-group">
                <h1>CONTEXT-AWARE SMART GLASSES AI</h1>
                <p>Developer System Dashboard & Mobile Gateway</p>
            </div>
            <a href="/api/v1/auth/google" target="_blank" class="btn" id="btn-oauth">
                CONNECT GOOGLE
            </a>
        </header>

        <!-- Live Status Badges -->
        <div class="status-grid">
            <div class="status-pill">
                <span class="pill-label">Backend</span>
                <span class="pill-value"><span class="dot dot-green" id="dot-backend"></span><span id="txt-backend">Connected</span></span>
            </div>
            <div class="status-pill">
                <span class="pill-label">Agent</span>
                <span class="pill-value"><span class="dot dot-green" id="dot-agent"></span><span id="txt-agent">Ready</span></span>
            </div>
            <div class="status-pill">
                <span class="pill-label">LLM</span>
                <span class="pill-value"><span class="dot dot-green" id="dot-llm"></span><span id="txt-llm">Connected</span></span>
            </div>
            <div class="status-pill">
                <span class="pill-label">TTS</span>
                <span class="pill-value"><span class="dot dot-green" id="dot-tts"></span><span id="txt-tts">Ready</span></span>
            </div>
            <div class="status-pill">
                <span class="pill-label">STT</span>
                <span class="pill-value"><span class="dot dot-green" id="dot-stt"></span><span id="txt-stt">Ready</span></span>
            </div>
            <div class="status-pill">
                <span class="pill-label">Google</span>
                <span class="pill-value"><span class="dot dot-red" id="dot-google"></span><span id="txt-google">Checking...</span></span>
            </div>
            <div class="status-pill">
                <span class="pill-label">Gmail</span>
                <span class="pill-value"><span class="dot dot-red" id="dot-gmail"></span><span id="txt-gmail">Checking...</span></span>
            </div>
        </div>

        <!-- Current Context -->
        <div class="card">
            <h2>Current Context</h2>
            <div class="context-row">
                <div class="context-item">
                    <span>Time</span>
                    <span id="ctx-time">--:--</span>
                </div>
                <div class="context-item">
                    <span>Period</span>
                    <span id="ctx-period">--</span>
                </div>
                <div class="context-item">
                    <span>Location</span>
                    <span id="ctx-location">Nagpur, India</span>
                </div>
                <div class="context-item">
                    <span>Timezone</span>
                    <span id="ctx-tz">Asia/Kolkata</span>
                </div>
            </div>
        </div>

        <!-- Assistant Interactive Area -->
        <div class="card">
            <h2>Assistant Testing Hub</h2>
            <div class="chat-box" id="chat-box">
                <div class="message msg-assistant">
                    <span class="msg-header">ASSISTANT</span>
                    <div>Ready on your smart glasses. Try typing a query or clicking a quick test button below.</div>
                </div>
            </div>
            
            <div class="input-row">
                <input type="text" id="user-input" class="input-text" placeholder="Type a message (e.g. 'Good morning' or 'What time is it?')" onkeydown="if(event.key==='Enter') sendMessage()">
                <button class="btn" id="btn-ask" onclick="sendMessage()">ASK</button>
            </div>

            <div class="btn-group">
                <button class="btn btn-secondary" onclick="sendQuickMessage('Good morning.')">🌅 Test Assistant</button>
                <button class="btn btn-secondary" onclick="sendQuickMessage('Check my email.')">✉️ Check Gmail</button>
                <button class="btn btn-secondary" onclick="sendQuickMessage('Where am I and what time is it?')">📍 Check Context</button>
            </div>
        </div>

        <!-- System Telemetry -->
        <div class="card">
            <h2>System Telemetry</h2>
            <div class="system-row">
                <div class="sys-item">
                    <span class="dot dot-green"></span>
                    <span>Backend: <b>OK (Port 8001)</b></span>
                </div>
                <div class="sys-item">
                    <span class="dot dot-green"></span>
                    <span>Database: <b>OK (SQLite)</b></span>
                </div>
                <div class="sys-item">
                    <span class="dot dot-green"></span>
                    <span>LLM Engine: <b id="sys-llm">Gemini</b></span>
                </div>
            </div>
        </div>
    </div>

    <script>
        const sessionId = "web_dev_" + Math.random().toString(36).substring(2, 9);

        async function updateStatus() {
            try {
                // 1. Health
                const hResp = await fetch('/api/v1/health');
                if (hResp.ok) {
                    const hData = await hResp.json();
                    document.getElementById('txt-backend').textContent = "Connected";
                    document.getElementById('dot-backend').className = "dot dot-green";
                    document.getElementById('txt-llm').textContent = hData.llm_provider.toUpperCase();
                    document.getElementById('sys-llm').textContent = hData.llm_provider.toUpperCase();
                }

                // 2. Google OAuth Status
                const gResp = await fetch('/api/v1/auth/google/status');
                if (gResp.ok) {
                    const gData = await gResp.json();
                    const isConn = gData.connected;
                    document.getElementById('dot-google').className = isConn ? "dot dot-green" : "dot dot-red";
                    document.getElementById('txt-google').textContent = isConn ? "Connected" : "Disconnected";
                    document.getElementById('dot-gmail').className = isConn ? "dot dot-green" : "dot dot-red";
                    document.getElementById('txt-gmail').textContent = isConn ? "Connected" : "Not Connected";

                    if (isConn) {
                        document.getElementById('btn-oauth').textContent = "GOOGLE CONNECTED (" + (gData.email || "OK") + ")";
                        document.getElementById('btn-oauth').style.background = "#00E676";
                    } else {
                        document.getElementById('btn-oauth').textContent = "CONNECT GOOGLE";
                        document.getElementById('btn-oauth').style.background = "#00E5FF";
                    }
                }

                // 3. Context
                const cResp = await fetch('/api/v1/context');
                if (cResp.ok) {
                    const cData = await cResp.json();
                    if (cData.time) {
                        document.getElementById('ctx-time').textContent = cData.time.local_time || "--";
                        document.getElementById('ctx-period').textContent = cData.time.period || "--";
                        document.getElementById('ctx-tz').textContent = cData.time.timezone || "Asia/Kolkata";
                    }
                    if (cData.location) {
                        document.getElementById('ctx-location').textContent = cData.location.city + ", " + cData.location.country;
                    }
                }
            } catch (err) {
                console.error("Status update error:", err);
            }
        }

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

        async function postMessage(messageText) {
            const chatBox = document.getElementById('chat-box');
            
            // Add user message
            const userDiv = document.createElement('div');
            userDiv.className = 'message msg-user';
            userDiv.innerHTML = '<span class="msg-header">USER</span><div>' + escapeHtml(messageText) + '</div>';
            chatBox.appendChild(userDiv);
            chatBox.scrollTop = chatBox.scrollHeight;

            // Placeholder for Assistant
            const astDiv = document.createElement('div');
            astDiv.className = 'message msg-assistant';
            astDiv.innerHTML = '<span class="msg-header">ASSISTANT</span><div id="loading-resp">Thinking...</div>';
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
                        context: null
                    })
                });

                const tDuration = (performance.now() - tStart).toFixed(0);

                if (resp.ok) {
                    const data = await resp.json();
                    const lat = data.metadata ? data.metadata.latency_ms : tDuration;
                    astDiv.innerHTML = '<span class="msg-header">ASSISTANT</span><div>' + escapeHtml(data.response) + '</div><div class="msg-latency">⏱️ Roundtrip: ' + lat.toFixed(0) + 'ms</div>';
                } else {
                    astDiv.innerHTML = '<span class="msg-header" style="color:var(--red);">ERROR</span><div>HTTP ' + resp.status + ' from backend.</div>';
                }
            } catch (err) {
                astDiv.innerHTML = '<span class="msg-header" style="color:var(--red);">ERROR</span><div>Could not reach backend: ' + escapeHtml(err.message) + '</div>';
            }

            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Initialize and poll status
        updateStatus();
        setInterval(updateStatus, 5000);
    </script>
</body>
</html>
"""
