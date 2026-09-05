def get_dashboard_html() -> str:
    """Returns the luxury personal assistant dashboard for the Smart Glasses AI."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Glasses AI — Personal Assistant</title>
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
            max-width: 840px;
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

        .btn-gold {
            background: var(--surface);
            color: var(--espresso);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 10px 18px;
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
            margin-bottom: 20px;
            padding: 10px 16px;
            background: var(--surface-subtle);
            border-radius: var(--radius-sm);
        }

        .context-item {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .context-sep {
            color: var(--border);
        }

        /* Chat / Conversation Feed */
        .conversation-feed {
            display: flex;
            flex-direction: column;
            gap: 12px;
            max-height: 280px;
            overflow-y: auto;
            padding: 16px;
            background: var(--surface-subtle);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            margin-bottom: 18px;
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
        }

        .msg-user .msg-sender {
            color: var(--espresso);
        }

        .msg-time {
            font-size: 10px;
            color: var(--text-light);
            margin-top: 4px;
            align-self: flex-end;
        }

        /* Inputs & Controls */
        .control-row {
            display: flex;
            gap: 12px;
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
            color: #FFFFFF;
            border: 1px solid var(--espresso);
            border-radius: var(--radius-sm);
            padding: 12px 22px;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .btn-primary:hover {
            background: #423632;
            border-color: #423632;
        }

        .btn-talk {
            background: var(--gold-light);
            color: var(--espresso);
            border: 1px solid var(--gold);
            border-radius: var(--radius-sm);
            padding: 12px 22px;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .btn-talk:hover {
            background: var(--gold);
            color: #FFFFFF;
        }

        /* Today's Schedule Card */
        .schedule-list {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .schedule-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 16px;
            background: var(--surface-subtle);
            border-radius: var(--radius-sm);
            border: 1px solid var(--border);
        }

        .schedule-time {
            font-weight: 600;
            font-size: 13px;
            color: var(--gold-hover);
            min-width: 80px;
        }

        .schedule-title {
            font-size: 14px;
            font-weight: 500;
            color: var(--espresso);
            flex: 1;
            margin-left: 12px;
        }

        .schedule-loc {
            font-size: 12px;
            color: var(--text-light);
        }

        /* 2-Column Grid for Services & Device */
        .grid-2col {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        @media (max-width: 680px) {
            .grid-2col { grid-template-columns: 1fr; }
            .header { flex-direction: column; align-items: flex-start; gap: 12px; }
            .context-bar { flex-direction: column; align-items: flex-start; gap: 6px; }
        }

        /* Status Badges */
        .status-table {
            width: 100%;
            border-collapse: collapse;
        }

        .status-table td {
            padding: 10px 0;
            border-bottom: 1px solid var(--surface-subtle);
            font-size: 13px;
        }

        .status-table tr:last-child td {
            border-bottom: none;
        }

        .status-table td:first-child {
            color: var(--text-muted);
            font-weight: 500;
        }

        .status-table td:last-child {
            text-align: right;
        }

        .badge-status {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 20px;
        }

        .badge-connected {
            background: var(--sage-bg);
            color: var(--sage);
        }

        .badge-disconnected {
            background: var(--terracotta-bg);
            color: var(--terracotta);
        }

        /* Diagnostics Collapsible */
        .diagnostics-details {
            border-top: 1px solid var(--border);
            padding-top: 16px;
        }

        .diagnostics-summary {
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.8px;
            text-transform: uppercase;
            color: var(--text-light);
            outline: none;
            user-select: none;
        }

        .diagnostics-summary:hover {
            color: var(--gold-hover);
        }

        .diagnostics-content {
            margin-top: 14px;
            background: var(--surface-subtle);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 14px;
            font-family: inherit;
            font-size: 12px;
            color: var(--text-muted);
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Top Luxury Header -->
        <header class="header">
            <div>
                <div class="brand-title">Smart Glasses AI</div>
                <div class="brand-subtitle">Personal AI Assistant</div>
            </div>
            <div style="display:flex; align-items:center; gap:12px;">
                <span class="badge-status badge-connected" id="badge-ai-mode" style="font-size:11px; letter-spacing:0.6px; text-transform:uppercase;">Cloud AI</span>
                <a href="/api/v1/auth/google" target="_blank" class="btn-gold" id="btn-oauth">
                    Connect Google Account
                </a>
            </div>
        </header>

        <!-- Assistant Main Card -->
        <div class="card">
            <div class="card-header">
                <div>
                    <h2 class="card-title">Assistant</h2>
                    <div class="card-subtitle" id="greeting-txt">Good evening. How may I assist?</div>
                </div>
            </div>

            <!-- Current Context Sub-Bar -->
            <div class="context-bar">
                <div class="context-item" id="ctx-time-item">
                    <span>Time:</span> <strong id="ctx-time">--:--</strong>
                </div>
                <span class="context-sep">·</span>
                <div class="context-item">
                    <span>Location:</span> <strong id="ctx-location">Nagpur, India</strong>
                </div>
                <span class="context-sep">·</span>
                <div class="context-item">
                    <span>Battery:</span> <strong>82%</strong>
                </div>
            </div>

            <!-- Conversation Feed -->
            <div class="conversation-feed" id="chat-box">
                <div class="msg-bubble msg-assistant">
                    <span class="msg-sender">Assistant</span>
                    <div>I am ready. You may speak or type your request below.</div>
                </div>
            </div>

            <!-- Input & Controls -->
            <div class="control-row">
                <input type="text" id="user-input" class="input-luxury" placeholder="What can I help you with?" onkeydown="if(event.key==='Enter') sendMessage()">
                <button class="btn-primary" onclick="sendMessage()">Send</button>
                <button class="btn-talk" onclick="sendQuickMessage('What do I have today?')">Talk</button>
            </div>
        </div>

        <!-- Schedule Card -->
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">Today's Schedule</h2>
                <span class="card-subtitle" id="schedule-date-tag">Today</span>
            </div>
            <div class="schedule-list" id="schedule-list">
                <div style="color:var(--text-muted); font-size:13px; padding:12px; text-align:center;">No events scheduled.</div>
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
                        <td>Gmail API</td>
                        <td><span class="badge-status badge-disconnected" id="badge-gmail">Disconnected</span></td>
                    </tr>
                    <tr>
                        <td>Google Calendar</td>
                        <td><span class="badge-status badge-disconnected" id="badge-cal">Disconnected</span></td>
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
                    <h2 class="card-title">Device</h2>
                </div>
                <table class="status-table">
                    <tr>
                        <td>Glasses Hardware</td>
                        <td><strong style="color:var(--espresso);">Connected (ESP32)</strong></td>
                    </tr>
                    <tr>
                        <td>Battery Level</td>
                        <td><strong style="color:var(--espresso);">82%</strong></td>
                    </tr>
                    <tr>
                        <td>Microphone (STT)</td>
                        <td><span class="badge-status badge-connected">Ready</span></td>
                    </tr>
                    <tr>
                        <td>Speaker (TTS)</td>
                        <td><span class="badge-status badge-connected">Ready</span></td>
                    </tr>
                </table>
            </div>
        </div>

        <!-- Developer Diagnostics (Discreet Accordion, Collapsed by Default) -->
        <details class="diagnostics-details">
            <summary class="diagnostics-summary">Developer Diagnostics</summary>
            <div class="diagnostics-content">
                <div>Backend Engine: <strong>FastAPI · Port 8001</strong></div>
                <div>LLM Provider: <strong id="diag-llm">Gemini Flash</strong></div>
                <div>Fast-Path Intent: <strong id="diag-fastpath">Active (&lt;30ms)</strong></div>
                <div>Session ID: <span id="diag-session" style="font-family:monospace;">--</span></div>
            </div>
        </details>
    </div>

    <script>
        const sessionId = "web_user_" + Math.random().toString(36).substring(2, 9);
        document.getElementById('diag-session').textContent = sessionId;

        async function updateStatus() {
            try {
                // 1. Health
                const hResp = await fetch('/api/v1/health');
                if (hResp.ok) {
                    const hData = await hResp.json();
                    document.getElementById('badge-backend').className = "badge-status badge-connected";
                    document.getElementById('badge-backend').textContent = "Connected";
                    document.getElementById('diag-llm').textContent = hData.llm_provider || "Gemini";
                }

                // 2. Integration Diagnostics
                const dResp = await fetch('/api/v1/diagnostics/integrations');
                if (dResp.ok) {
                    const diagData = await dResp.json();
                    const isGoogle = diagData.google === 'connected';
                    const isGemini = diagData.gemini === 'available';

                    const badgeAi = document.getElementById('badge-ai-mode');
                    if (isGemini) {
                        badgeAi.className = "badge-status badge-connected";
                        badgeAi.textContent = "Cloud AI (Gemini)";
                    } else {
                        badgeAi.className = "badge-status badge-disconnected";
                        badgeAi.textContent = "Offline / Local";
                    }

                    const bGoogle = document.getElementById('badge-google');
                    const bGmail = document.getElementById('badge-gmail');
                    const bCal = document.getElementById('badge-cal');
                    const btnOauth = document.getElementById('btn-oauth');

                    if (isGoogle) {
                        bGoogle.className = "badge-status badge-connected";
                        bGoogle.textContent = "Connected";
                        bGmail.className = "badge-status badge-connected";
                        bGmail.textContent = "Active";
                        bCal.className = "badge-status badge-connected";
                        bCal.textContent = "Active";

                        btnOauth.textContent = "Google Connected";
                        btnOauth.style.borderColor = "var(--sage)";
                    } else {
                        bGoogle.className = "badge-status badge-disconnected";
                        bGoogle.textContent = "Disconnected";
                        bGmail.className = "badge-status badge-disconnected";
                        bGmail.textContent = "Disconnected";
                        bCal.className = "badge-status badge-disconnected";
                        bCal.textContent = "Disconnected";

                        btnOauth.textContent = "Connect Google Account";
                        btnOauth.style.borderColor = "var(--border)";
                    }
                }

                // 3. Dynamic Context & Live Schedule
                const cResp = await fetch('/api/v1/context');
                if (cResp.ok) {
                    const cData = await cResp.json();
                    if (cData.time) {
                        document.getElementById('ctx-time').textContent = cData.time.local_time || "--";
                        const period = cData.time.period || "evening";
                        document.getElementById('greeting-txt').textContent = "Good " + period + ". How may I assist?";
                    }
                    if (cData.location) {
                        document.getElementById('ctx-location').textContent = cData.location.city + ", " + cData.location.country;
                    }

                    // Render Schedule Dynamically
                    const scheduleList = document.getElementById('schedule-list');
                    const events = (cData.calendar && cData.calendar.today_events) ? cData.calendar.today_events : [];
                    if (events.length === 0) {
                        scheduleList.innerHTML = '<div style="color:var(--text-light); font-size:13px; padding:12px; text-align:center;">No upcoming events scheduled for today.</div>';
                    } else {
                        let html = '';
                        events.forEach(function(ev) {
                            html += '<div class="schedule-item">' +
                                '<span class="schedule-time">' + escapeHtml(ev.start_time || '') + '</span>' +
                                '<span class="schedule-title">' + escapeHtml(ev.title || 'Event') + '</span>' +
                                '<span class="schedule-loc">' + escapeHtml(ev.location || '') + '</span>' +
                                '</div>';
                        });
                        scheduleList.innerHTML = html;
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
            
            // User message
            const userDiv = document.createElement('div');
            userDiv.className = 'msg-bubble msg-user';
            userDiv.innerHTML = '<span class="msg-sender">You</span><div>' + escapeHtml(messageText) + '</div>';
            chatBox.appendChild(userDiv);
            chatBox.scrollTop = chatBox.scrollHeight;

            // Assistant placeholder
            const astDiv = document.createElement('div');
            astDiv.className = 'msg-bubble msg-assistant';
            astDiv.innerHTML = '<span class="msg-sender">Assistant</span><div>Thinking...</div>';
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
                    const lat = data.metadata && data.metadata.latency_ms ? data.metadata.latency_ms.toFixed(0) : tDuration;
                    astDiv.innerHTML = '<span class="msg-sender">Assistant</span><div>' + escapeHtml(data.response) + '</div><div class="msg-time">' + lat + ' ms</div>';
                } else {
                    astDiv.innerHTML = '<span class="msg-sender" style="color:var(--terracotta);">Error</span><div>HTTP ' + resp.status + ' from backend.</div>';
                }
            } catch (err) {
                astDiv.innerHTML = '<span class="msg-sender" style="color:var(--terracotta);">Error</span><div>Unable to reach assistant: ' + escapeHtml(err.message) + '</div>';
            }

            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        updateStatus();
        setInterval(updateStatus, 5000);
    </script>
</body>
</html>
"""
