def get_dashboard_html() -> str:
    """Returns the LARA Operations Console — Quiet Luxury, Reductive Design & Slide-over Developer Drawer (Zero Emojis)."""
    return r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LARA Smart Glasses — Private Intelligence & Control</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-base: #111215;
            --bg-surface: #181A20;
            --bg-surface-elevated: #22252E;
            --bg-subtle: #1C1E26;
            --border: #2B2F3B;
            --border-light: rgba(255, 255, 255, 0.08);
            --border-focus: #D96B27;
            
            --orange: #D96B27;
            --orange-light: #FBEFE8;
            --orange-subtle: rgba(217, 107, 39, 0.12);
            --orange-hover: #C05817;
            
            --emerald: #2D7D46;
            --emerald-bg: rgba(45, 125, 70, 0.15);
            --amber: #C88220;
            --amber-bg: rgba(200, 130, 32, 0.15);
            --red: #B83A3A;
            --red-bg: rgba(184, 58, 58, 0.15);
            --sand: #EED9C4;
            
            --text-primary: #F5F2EB;
            --text-secondary: #9E9B95;
            --text-muted: #6E6B65;
            
            --shadow-card: 0 4px 20px rgba(0, 0, 0, 0.25);
            --shadow-drawer: -8px 0 32px rgba(0, 0, 0, 0.5);
            --radius-lg: 12px;
            --radius-md: 8px;
            --radius-sm: 6px;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-base);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
            overflow-x: hidden;
        }

        /* Top Executive System Bar */
        .system-top-bar {
            background-color: var(--bg-surface);
            border-bottom: 1px solid var(--border);
            padding: 14px 28px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .brand-logo-area {
            display: flex;
            align-items: baseline;
            gap: 12px;
        }

        .brand-title {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 20px;
            font-weight: 700;
            letter-spacing: 2px;
            color: var(--text-primary);
            text-transform: uppercase;
        }

        .brand-subtitle {
            font-size: 11px;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: var(--orange);
            font-weight: 600;
        }

        .subsystem-pills {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .pill-status {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            background: var(--bg-subtle);
            border: 1px solid var(--border);
            color: var(--text-secondary);
        }

        .pill-status.active {
            background: var(--emerald-bg);
            border-color: rgba(45, 125, 70, 0.4);
            color: #68D391;
        }

        .pill-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: #68D391;
        }

        /* Layout: Left Rail + Center Spacious Workspace */
        .console-workspace {
            display: grid;
            grid-template-columns: 220px 1fr;
            min-height: calc(100vh - 61px);
            background: var(--bg-base);
            position: relative;
        }

        @media (max-width: 800px) {
            .console-workspace { grid-template-columns: 1fr; }
            .nav-panel { display: none; }
        }

        /* Left Navigation Rail */
        .nav-panel {
            background-color: var(--bg-surface);
            border-right: 1px solid var(--border);
            padding: 24px 16px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .nav-group {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .nav-section-title {
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            font-weight: 700;
            color: var(--text-muted);
            margin: 16px 12px 6px 12px;
        }

        .nav-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 14px;
            border-radius: var(--radius-sm);
            font-size: 13px;
            font-weight: 500;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.15s ease;
        }

        .nav-item:hover {
            color: var(--text-primary);
            background-color: var(--bg-surface-elevated);
        }

        .nav-item.active {
            color: var(--text-primary);
            background-color: var(--bg-surface-elevated);
            font-weight: 600;
            border-left: 2px solid var(--orange);
        }

        /* Center Main Operations Workspace */
        .main-panel {
            padding: 32px 40px;
            overflow-y: auto;
            max-width: 1100px;
            margin: 0 auto;
            width: 100%;
        }

        .console-view {
            display: none;
            flex-direction: column;
            gap: 24px;
        }

        .console-view.active { display: flex; }

        /* Card System */
        .card-luxury {
            background-color: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 24px;
            box-shadow: var(--shadow-card);
        }

        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border);
        }

        .card-title {
            font-size: 13px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* Center Assistant Message Stream */
        .chat-stream {
            display: flex;
            flex-direction: column;
            gap: 16px;
            max-height: 480px;
            overflow-y: auto;
            padding-right: 8px;
        }

        .message-row {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .message-row.user { align-items: flex-end; }
        .message-row.assistant { align-items: flex-start; }

        .message-bubble {
            max-width: 82%;
            padding: 14px 18px;
            border-radius: var(--radius-md);
            font-size: 14px;
            line-height: 1.6;
        }

        .message-bubble.user {
            background-color: var(--orange);
            color: #FFFFFF;
            border-bottom-right-radius: 2px;
        }

        .message-bubble.assistant {
            background-color: var(--bg-surface-elevated);
            border: 1px solid var(--border);
            color: var(--text-primary);
            border-bottom-left-radius: 2px;
        }

        /* Multimodal Quick Actions Bar */
        .quick-actions-bar {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }

        .btn-quick-chip {
            background: var(--bg-surface-elevated);
            color: var(--text-primary);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 8px 14px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s ease;
        }

        .btn-quick-chip:hover {
            border-color: var(--orange);
            color: var(--orange);
        }

        .btn-quick-chip.primary {
            background: var(--orange);
            color: #FFFFFF;
            border-color: var(--orange);
        }

        .btn-quick-chip.primary:hover {
            background: var(--orange-hover);
        }

        /* Command Input Bar */
        .command-bar {
            display: flex;
            gap: 10px;
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 8px 12px;
        }

        .command-input {
            flex: 1;
            background: transparent;
            border: none;
            color: var(--text-primary);
            font-size: 14px;
            outline: none;
            padding: 6px 8px;
        }

        .btn-send {
            background: var(--orange);
            color: #FFFFFF;
            border: none;
            border-radius: var(--radius-sm);
            padding: 8px 18px;
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
        }

        .btn-voice {
            background: var(--bg-surface-elevated);
            color: var(--text-primary);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 8px 14px;
            font-size: 13px;
            cursor: pointer;
        }

        /* Slide-Over Drawer: Intent Inspector (Closed by default) */
        .inspector-drawer {
            position: fixed;
            top: 0;
            right: -420px;
            width: 400px;
            height: 100vh;
            background-color: var(--bg-surface);
            border-left: 1px solid var(--border);
            box-shadow: var(--shadow-drawer);
            padding: 24px 20px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            z-index: 1000;
            transition: right 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            overflow-y: auto;
        }

        .inspector-drawer.open {
            right: 0;
        }

        .drawer-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--border);
            padding-bottom: 12px;
        }

        .btn-close-drawer {
            background: transparent;
            border: none;
            color: var(--text-secondary);
            font-size: 18px;
            cursor: pointer;
            padding: 4px 8px;
        }

        .btn-close-drawer:hover { color: var(--text-primary); }

        .inspector-field {
            display: flex;
            flex-direction: column;
            gap: 4px;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        }

        .inspector-label {
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
            font-weight: 700;
        }

        .inspector-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: var(--text-primary);
            word-break: break-all;
        }

        /* Luxury Tables */
        .table-luxury {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }

        .table-luxury th {
            text-align: left;
            padding: 10px 14px;
            border-bottom: 1px solid var(--border);
            color: var(--text-muted);
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 700;
        }

        .table-luxury td {
            padding: 12px 14px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            color: var(--text-secondary);
        }

        .table-luxury tr:hover td {
            background: var(--bg-surface-elevated);
            color: var(--text-primary);
        }

        /* VU Meter */
        .vu-meter-bar {
            width: 100%;
            height: 6px;
            background: var(--bg-subtle);
            border-radius: 3px;
            overflow: hidden;
            border: 1px solid var(--border);
        }

        .vu-meter-fill {
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, #68D391, #D96B27);
            transition: width 0.15s ease;
        }

        .dropzone-box {
            border: 2px dashed var(--border);
            border-radius: var(--radius-md);
            padding: 24px;
            text-align: center;
            background: var(--bg-subtle);
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .dropzone-box:hover {
            border-color: var(--orange);
        }
    </style>
</head>
<body>

    <!-- Top Executive System Bar -->
    <header class="system-top-bar">
        <div class="brand-logo-area">
            <span class="brand-title">LARA</span>
            <span class="brand-subtitle">Private Intelligence & Control</span>
        </div>

        <div class="subsystem-pills">
            <span class="pill-status active"><span class="pill-dot"></span> Smart Glasses</span>
            <span class="pill-status active"><span class="pill-dot"></span> Android</span>
            <span class="pill-status" id="pill-google"><span class="pill-dot" style="background:#6E6B65;"></span> Google Workspace</span>
            <button class="btn-quick-chip" onclick="openInspectorDrawer()" style="padding:4px 10px; font-size:11px;">Intent Inspector</button>
        </div>
    </header>

    <div class="console-workspace">

        <!-- Panel 1: Left Navigation Rail -->
        <nav class="nav-panel">
            <div class="nav-group">
                <div class="nav-section-title">Workspace</div>
                <div class="nav-item active" onclick="showTab('overview', this)">Overview</div>
                <div class="nav-item" onclick="showTab('assistant', this)">Assistant</div>
                <div class="nav-item" onclick="showTab('activity', this)">Activity</div>
                <div class="nav-item" onclick="showTab('devices', this)">Devices</div>
                <div class="nav-item" onclick="showTab('glasses-logs', this)">Glasses Live Logs</div>
                <div class="nav-item" onclick="showTab('conv-stream', this)">Glasses Conversation</div>
                <div class="nav-item" onclick="showTab('requests', this)">Request Status Hub</div>
                <div class="nav-item" onclick="showTab('contacts', this)">Quick Contacts Hub</div>
                <div class="nav-item" onclick="showTab('files', this)">Files</div>
                <div class="nav-item" onclick="showTab('desk', this)">Desk & Data Analysis</div>
                <div class="nav-item" onclick="showTab('automations', this)">Automations Center</div>
                <div class="nav-item" onclick="showTab('notifications', this)">Smart Notifications</div>
                <div class="nav-item" onclick="showTab('settings', this)">Settings</div>
            </div>

            <div class="nav-group">
                <div class="nav-section-title">Developer</div>
                <div class="nav-item" onclick="showTab('developer', this)">Developer Diagnostics</div>
            </div>
        </nav>

        <!-- Panel 2: Center Spacious Operations Workspace -->
        <main class="main-panel">

            <!-- View 1: Overview ("Is LARA Working?") -->
            <div id="view-overview" class="console-view active">
                <div class="card-luxury">
                    <div class="card-header">
                        <span class="card-title">System Readiness</span>
                        <span class="pill-status active"><span class="pill-dot"></span> Operational</span>
                    </div>
                    <p style="font-size:14px; color:var(--text-secondary); margin-bottom:20px; line-height:1.6;">
                        LARA is private, synchronized, and operational. Hands-free Smart Glasses speech and vision pipelines are active.
                    </p>

                    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:16px;">
                        <div style="background:var(--bg-subtle); padding:16px; border-radius:var(--radius-md); border:1px solid var(--border);">
                            <div style="font-size:11px; text-transform:uppercase; color:var(--text-muted); font-weight:700;">Smart Glasses</div>
                            <div style="font-size:16px; font-weight:700; color:var(--text-primary); margin-top:4px;">Connected (S3)</div>
                            <div style="font-size:12px; color:#68D391; margin-top:2px;">Camera & Mic Ready</div>
                        </div>
                        <div style="background:var(--bg-subtle); padding:16px; border-radius:var(--radius-md); border:1px solid var(--border);">
                            <div style="font-size:11px; text-transform:uppercase; color:var(--text-muted); font-weight:700;">Android Companion</div>
                            <div style="font-size:16px; font-weight:700; color:var(--text-primary); margin-top:4px;">Foreground Daemon</div>
                            <div style="font-size:12px; color:#68D391; margin-top:2px;">Pocket Mode Active</div>
                        </div>
                        <div style="background:var(--bg-subtle); padding:16px; border-radius:var(--radius-md); border:1px solid var(--border);">
                            <div style="font-size:11px; text-transform:uppercase; color:var(--text-muted); font-weight:700;">Cloud Intelligence</div>
                            <div style="font-size:16px; font-weight:700; color:var(--text-primary); margin-top:4px;">Gemini 2.5 Flash</div>
                            <div style="font-size:12px; color:#68D391; margin-top:2px;">Fast Reasoning Tier</div>
                        </div>
                    </div>
                </div>

                <div class="card-luxury">
                    <div class="card-header">
                        <span class="card-title">Live Operational Session</span>
                        <span style="font-size:12px; color:var(--text-muted);" id="session-summary-label">Active</span>
                    </div>
                    <div id="overview-activity-list" style="display:flex; flex-direction:column; gap:12px; font-size:13px;">
                        <div style="color:var(--text-secondary);">Ready for instructions. All actions will appear here dynamically.</div>
                    </div>
                </div>
            </div>

            <!-- View 2: Assistant Conversational Workspace -->
            <div id="view-assistant" class="console-view">
                
                <!-- Quick Actions Chips -->
                <div class="quick-actions-bar">
                    <button class="btn-quick-chip primary" onclick="triggerVisionCaptureDescribe()">Capture + Describe</button>
                    <button class="btn-quick-chip" onclick="triggerMultimodalCapture()">Multimodal (ESP32 Mic+Cam)</button>
                    <button class="btn-quick-chip" onclick="triggerQuadraticVision()">Solve Quadratic x²+5x+6=0</button>
                    <button class="btn-quick-chip" onclick="triggerQrScan()">Scan QR Code</button>
                    <button class="btn-quick-chip" onclick="sendQuickMessage('Check my unread emails')">Check Email</button>
                    <button class="btn-quick-chip" onclick="sendQuickMessage('What is on my calendar today?')">Calendar</button>
                    <button class="btn-quick-chip" onclick="sendQuickMessage('Check my github status')">GitHub Status</button>
                    <button class="btn-quick-chip" onclick="sendQuickMessage('What did staff upload?')">Staff Data</button>
                    <button class="btn-quick-chip" onclick="simulateIncomingSmsPrompt()">Simulate SMS Alert</button>
                </div>

                <!-- Chat & Interaction Stream -->
                <div class="card-luxury" style="min-height:420px; display:flex; flex-direction:column; justify-content:space-between;">
                    <div class="card-header">
                        <span class="card-title">Interaction Stream</span>
                        <span style="font-size:11px; color:var(--text-muted);" id="session-display">Session: lara_web</span>
                    </div>

                    <div class="chat-stream" id="chat-messages">
                        <div class="message-row assistant">
                            <div class="message-bubble assistant">
                                <strong>LARA:</strong> System initialized. Ask a question, inspect your schedule, compose messages, or analyze uploaded data.
                            </div>
                        </div>
                    </div>

                    <div style="margin-top:20px;">
                        <div class="command-bar">
                            <input type="text" id="user-input" class="command-input" placeholder="Ask LARA anything..." onkeydown="if(event.key==='Enter') sendMessage()">
                            <button class="btn-voice" onclick="toggleVoiceInput()" id="mic-btn">Voice</button>
                            <button class="btn-send" onclick="sendMessage()">Execute</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- View 3: Activity Feed -->
            <div id="view-activity" class="console-view">
                <div class="card-luxury">
                    <div class="card-header">
                        <span class="card-title">Chronological Activity</span>
                        <button class="btn-quick-chip" onclick="clearActivityFeed()">Clear History</button>
                    </div>
                    <table class="table-luxury">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Action / Query</th>
                                <th>Category</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody id="activity-table-body">
                            <tr><td colspan="4" style="text-align:center; color:var(--text-muted);">No activity recorded yet in this session.</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- View 4: Devices Hub -->
            <div id="view-devices" class="console-view">
                <div class="card-luxury">
                    <div class="card-header">
                        <span class="card-title">ESP32 Smart Glasses & Android Hub (Seeed Studio XIAO ESP32-S3 Sense)</span>
                        <span id="badge-esp-live" class="pill-status active">CONNECTED (COM5)</span>
                    </div>

                    <table class="table-luxury">
                        <tr><td>Hardware Model</td><td>Seeed Studio XIAO ESP32-S3 Sense (Dual-Core LX7, 240MHz)</td></tr>
                        <tr><td>Camera Sensor</td><td>OV3660 / OV2640 (640x480 VGA) · <strong style="color:#68D391;">READY</strong></td></tr>
                        <tr><td>Digital Microphone</td><td>MSM261D PDM Digital Mic (16kHz PCM WAV) · <strong style="color:#68D391;">READY</strong></td></tr>
                        <tr><td>Microphone Energy VU</td><td><div class="vu-meter-bar"><div id="hw-mic-fill" class="vu-meter-fill"></div></div></td></tr>
                        <tr><td>BLE Subsystem</td><td>SmartGlasses-S3 (Service UUID 19B10000...) · <strong style="color:#68D391;">CONNECTED</strong></td></tr>
                        <tr><td>Battery & RSSI</td><td><span id="hw-batt-val">85%</span> · <span id="hw-rssi-val">-58 dBm</span></td></tr>
                        <tr><td>Last Vision Diagnostic</td><td><strong style="color:#68D391;" id="hw-last-vis-status">PASS</strong> · <span id="hw-last-cap-id">cap_live_s3</span></td></tr>
                    </table>
                </div>
            </div>

            <!-- View 5: Files & Documents Workspace + Staff Upload -->
            <div id="view-files" class="console-view">
                <div class="card-luxury">
                    <div class="card-header">
                        <span class="card-title">Staff Data Upload for Smart Glasses Analysis</span>
                    </div>
                    <p style="font-size:13px; color:var(--text-secondary); margin-bottom:16px;">
                        Upload spreadsheet datasets (CSV/Excel/JSON) for executive queries on Smart Glasses.
                    </p>
                    <div class="dropzone-box" onclick="document.getElementById('file-upload-input').click()">
                        <input type="file" id="file-upload-input" style="display:none;" onchange="handleStaffFileUpload(this)">
                        <div style="font-size:14px; font-weight:700; color:var(--orange);">Choose file or drag here to upload</div>
                        <div style="font-size:12px; color:var(--text-muted); margin-top:4px;">Supports .csv, .xlsx, .json, .pdf (Max 50MB)</div>
                    </div>
                    <div id="upload-status-box" style="margin-top:14px; font-size:13px; display:none;"></div>
                </div>

                <div class="card-luxury">
                    <div class="card-header">
                        <span class="card-title">Document Repository</span>
                    </div>
                    <table class="table-luxury">
                        <thead>
                            <tr>
                                <th>Document</th>
                                <th>Uploader</th>
                                <th>Status</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody id="files-table-body">
                            <tr><td>Quarterly_Financials.xlsx</td><td>Staff Assistant</td><td><span class="pill-status active">Parsed (24,582 rows)</span></td><td><button class="btn-quick-chip" onclick="showTab('desk')">Analyze</button></td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- View 6: Desk & Data Analysis -->
            <div id="view-desk" class="console-view">
                <div class="card-luxury">
                    <div class="card-header">
                        <span class="card-title">Universal Tabular & Document Data Analysis</span>
                        <span class="pill-status active" id="desk-dataset-badge">Active Dataset: Quarterly_Financials.csv</span>
                    </div>

                    <p style="font-size:13px; color:var(--text-secondary); margin-bottom:16px;">
                        Statistical, numerical, and anomaly analysis on structured CSV datasets. Accessible via cloud endpoints on Web and Smart Glasses.
                    </p>

                    <div class="quick-actions-bar" style="margin-bottom:16px;">
                        <button class="btn-quick-chip primary" onclick="runDeskAnalysis('summarize')">Summarize Dataset</button>
                        <button class="btn-quick-chip" onclick="runDeskAnalysis('anomalies')">Find Anomalies</button>
                        <button class="btn-quick-chip" onclick="runDeskAnalysis('calculate')">Calculate Metrics</button>
                    </div>

                    <div style="display:flex; gap:8px; margin-bottom:16px;">
                        <input type="text" id="desk-query-input" placeholder="Ask a question about this data (e.g. 'What is the average revenue?', 'Find outliers', 'Total units')..." style="flex:1; background:var(--bg-subtle); border:1px solid var(--border); border-radius:var(--radius-sm); padding:10px 14px; color:var(--text-main); font-size:13px;" onkeydown="if(event.key==='Enter') executeCustomDataQuery()">
                        <button class="btn-quick-chip primary" onclick="executeCustomDataQuery()">Query Data</button>
                    </div>

                    <div id="desk-results" style="background:var(--bg-subtle); border:1px solid var(--border); border-radius:var(--radius-sm); padding:16px; font-size:13px; line-height:1.6;">
                        Select an action above or type a natural language query to analyze the active dataset.
                    </div>
                </div>
            </div>

            <!-- View 7: Automations Center -->
            <div id="view-automations" class="console-view">
                <div class="card-luxury">
                    <div class="card-header">
                        <span class="card-title">Automations Center</span>
                        <button class="btn-quick-chip primary" onclick="scheduleNewBriefing()">+ New Automation</button>
                    </div>
                    <table class="table-luxury">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Trigger / Schedule</th>
                                <th>Permissions</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody id="automations-table">
                            <tr>
                                <td>Daily Morning Briefing</td>
                                <td>Schedule (08:00 AM Daily)</td>
                                <td>Calendar, Gmail</td>
                                <td><span class="pill-status active">ACTIVE</span></td>
                            </tr>
                            <tr>
                                <td>Executive Email Digest</td>
                                <td>Recurring (Every 4h)</td>
                                <td>Gmail</td>
                                <td><span class="pill-status active">ACTIVE</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- View 8: Smart Notifications -->
            <div id="view-notifications" class="console-view">
                <div class="card-luxury">
                    <div class="card-header">
                        <span class="card-title">Smart Notifications</span>
                    </div>
                    <table class="table-luxury">
                        <thead>
                            <tr>
                                <th>Category</th>
                                <th>Routing Policy</th>
                                <th>Delivery Mode</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td>Critical Alerts</td><td>Always Deliver</td><td>Audible + Wearable</td></tr>
                            <tr><td>Important Communications</td><td>Filtered / Priority</td><td>Audible</td></tr>
                            <tr><td>Normal Updates</td><td>Silent / Allow</td><td>Digest</td></tr>
                            <tr><td>Promotions</td><td>Silent</td><td>Muted</td></tr>
                            <tr><td>Spam</td><td>Block</td><td>Discarded</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- View 9: Settings & Google OAuth Integration -->
            <div id="view-settings" class="console-view">
                <div class="card-luxury">
                    <div class="card-header">
                        <span class="card-title">Connected Services & Authentication</span>
                    </div>
                    <table class="table-luxury">
                        <tr>
                            <td>Google Workspace (Gmail & Calendar)</td>
                            <td id="google-auth-status-cell">
                                <span class="pill-status" id="google-status-pill">Checking...</span>
                            </td>
                            <td>
                                <button class="btn-quick-chip primary" id="btn-google-auth" onclick="connectGoogleOAuth()">Connect Google</button>
                            </td>
                        </tr>
                        <tr>
                            <td>GitHub Integration</td>
                            <td><span class="pill-status active">Connected</span></td>
                            <td><button class="btn-quick-chip" onclick="sendQuickMessage('Check GitHub status')">Check Status</button></td>
                        </tr>
                        <tr>
                            <td>Android Companion Service</td>
                            <td><span class="pill-status active">Foreground Daemon Active</span></td>
                            <td><button class="btn-quick-chip" onclick="showTab('devices')">View Device</button></td>
                        </tr>
                    </table>
                </div>
            </div>

            <!-- View 10: Dedicated Developer Diagnostics -->
            <div id="view-developer" class="console-view">
                <div class="card-luxury">
                    <div class="card-header">
                        <span class="card-title">Developer Latency Waterfall</span>
                        <button class="btn-quick-chip" onclick="openInspectorDrawer()">Open Live Inspector</button>
                    </div>
                    <table class="table-luxury">
                        <tr><td>Total Request Latency</td><td><strong id="diag-lat-total">42.5ms</strong></td></tr>
                        <tr><td>Intent Router Tier</td><td><strong id="diag-tier">FAST (Direct Deterministic)</strong></td></tr>
                        <tr><td>LLM Response Time</td><td><strong id="diag-lat-llm">0.0ms (Fast Path)</strong></td></tr>
                        <tr><td>Tool Execution Time</td><td><strong id="diag-lat-tool">1.2ms</strong></td></tr>
                        <tr><td>Vision Pipeline Latency</td><td><strong id="diag-lat-vision">68.0ms</strong></td></tr>
                    </table>
                </div>

                <div class="card-luxury">
                    <div class="card-header">
                        <span class="card-title">Security & Audit Traces</span>
                        <button class="btn-quick-chip" onclick="refreshAuditLogs()">Refresh Logs</button>
                    </div>
                    <div id="audit-log-content" style="max-height:240px; overflow-y:auto; font-family:'JetBrains Mono', monospace; font-size:11px; background:var(--bg-subtle); padding:12px; border-radius:var(--radius-sm); border:1px solid var(--border);">
                        Loading security audit entries...
                    </div>
                </div>
            </div>

            <!-- View: Glasses & BLE Live Logs -->
            <div id="view-glasses-logs" class="console-view">
                <div class="card-luxury">
                    <div class="card-header">
                        <span class="card-title">Seeed Studio XIAO ESP32-S3 Sense — Live BLE & Hardware Stream</span>
                        <div style="display:flex; gap:8px;">
                            <button class="btn-quick-chip primary" onclick="refreshGlassesLogs()">Refresh Stream</button>
                            <span class="pill-status active"><span class="pill-dot"></span> LIVE POLLING (3s)</span>
                        </div>
                    </div>
                    <p style="font-size:13px; color:var(--text-secondary); margin-bottom:16px;">
                        Real-time hardware event stream from ESP32-S3 smart glasses temple button, digital microphone, OV2640 camera frames, and BLE characteristic writes.
                    </p>
                    <table class="table-luxury">
                        <thead>
                            <tr>
                                <th style="width:90px;">Time</th>
                                <th style="width:180px;">Event Type</th>
                                <th style="width:90px;">Source</th>
                                <th style="width:70px;">Level</th>
                                <th>Details / Payload</th>
                            </tr>
                        </thead>
                        <tbody id="glasses-logs-tbody">
                            <tr><td colspan="5" style="text-align:center; color:var(--text-muted);">Loading smart glasses hardware logs...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- View: Glasses <-> Android <-> Cloud Conversation Stream -->
            <div id="view-conv-stream" class="console-view">
                <div class="card-luxury">
                    <div class="card-header">
                        <span class="card-title">Glasses & Android Conversation History</span>
                        <button class="btn-quick-chip" onclick="refreshConversationStream()">Refresh Stream</button>
                    </div>
                    <p style="font-size:13px; color:var(--text-secondary); margin-bottom:16px;">
                        Chronological record of all spoken user queries captured on Glasses / Android and synthesized voice replies.
                    </p>
                    <div id="conv-stream-container" style="display:flex; flex-direction:column; gap:12px; max-height:500px; overflow-y:auto; padding:8px 0;">
                        <div style="color:var(--text-muted); font-size:13px;">Loading conversation history...</div>
                    </div>
                </div>
            </div>

            <!-- View: Request Telemetry (Generated vs Failed Requests) -->
            <div id="view-requests" class="console-view">
                <div class="card-luxury">
                    <div class="card-header">
                        <span class="card-title">Request Execution Telemetry & Status</span>
                        <button class="btn-quick-chip" onclick="refreshRequestLogs()">Refresh Requests</button>
                    </div>
                    <p style="font-size:13px; color:var(--text-secondary); margin-bottom:16px;">
                        Real-time audit of all assistant requests, fast-path routing outcomes, execution latency, and error diagnostics.
                    </p>
                    <table class="table-luxury">
                        <thead>
                            <tr>
                                <th style="width:90px;">Time</th>
                                <th>Request ID / Query</th>
                                <th style="width:120px;">Status</th>
                                <th style="width:110px;">Latency</th>
                                <th>Error / Diagnostic Reason</th>
                            </tr>
                        </thead>
                        <tbody id="requests-tbody">
                            <tr><td colspan="5" style="text-align:center; color:var(--text-muted);">Loading request telemetry...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- View: Quick Contacts Action Hub -->
            <div id="view-contacts" class="console-view">
                <div class="card-luxury">
                    <div class="card-header">
                        <span class="card-title">Quick-Action Contact Hub</span>
                        <span class="pill-status active"><span class="pill-dot"></span> 1-Tap Telephony Ready</span>
                    </div>
                    <p style="font-size:13px; color:var(--text-secondary); margin-bottom:20px;">
                        Instant telephony, SMS, and Email dispatch for hands-free smart glasses and mobile companion. Phone numbers are synthesized with natural digit spacing.
                    </p>

                    <div id="contacts-card-grid" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:16px;">
                        <!-- Rendered by JS -->
                    </div>
                </div>

                <!-- Fast Custom Contact Action Card -->
                <div class="card-luxury">
                    <div class="card-header">
                        <span class="card-title">Fast Manual Dispatch</span>
                    </div>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:16px;">
                        <div>
                            <label style="font-size:12px; color:var(--text-muted); font-weight:600; text-transform:uppercase;">Recipient Name / Number</label>
                            <input type="text" id="manual-contact-target" class="command-input" style="margin-top:6px;" placeholder="e.g. Rahul or +1 555-0100">
                        </div>
                        <div>
                            <label style="font-size:12px; color:var(--text-muted); font-weight:600; text-transform:uppercase;">Message / Subject</label>
                            <input type="text" id="manual-contact-msg" class="command-input" style="margin-top:6px;" placeholder="e.g. I am running 5 minutes late">
                        </div>
                    </div>
                    <div style="display:flex; gap:10px;">
                        <button class="btn-quick-chip primary" onclick="triggerManualCall()">1-Tap Call</button>
                        <button class="btn-quick-chip" onclick="triggerManualSms()">Send Fast SMS</button>
                        <button class="btn-quick-chip" onclick="triggerManualEmail()">Send Fast Email</button>
                    </div>
                    <div id="manual-dispatch-status" style="margin-top:12px; font-size:13px; display:none;"></div>
                </div>
            </div>

        </main>

        <!-- Slide-Over Drawer: Intent Inspector (Closed by default) -->
        <aside class="inspector-drawer" id="inspector-drawer">
            <div class="drawer-header">
                <span class="card-title">Intent Inspector</span>
                <button class="btn-close-drawer" onclick="closeInspectorDrawer()">Close</button>
            </div>

            <div class="inspector-field">
                <span class="inspector-label">Raw User Input</span>
                <div class="inspector-value" id="insp-raw">"What is in front of me?"</div>
            </div>

            <div class="inspector-field">
                <span class="inspector-label">Normalized Intent</span>
                <div class="inspector-value" id="insp-intent">VISION_SCENE_UNDERSTANDING</div>
            </div>

            <div class="inspector-field">
                <span class="inspector-label">Detected Entities</span>
                <div class="inspector-value" id="insp-entities">{"target": "camera_frame", "device": "SmartGlasses-S3"}</div>
            </div>

            <div class="inspector-field">
                <span class="inspector-label">Selected Router</span>
                <div class="inspector-value" id="insp-router">SMART_ROUTER (Fast Vision Path)</div>
            </div>

            <div class="inspector-field">
                <span class="inspector-label">Execution Target</span>
                <div class="inspector-value" id="insp-target">vision_service.analyze_image</div>
            </div>

            <div class="inspector-field">
                <span class="inspector-label">Risk Level</span>
                <div class="inspector-value" id="insp-risk" style="color:#68D391;">READ_ONLY (Safe Execution)</div>
            </div>

            <div class="inspector-field">
                <span class="inspector-label">Confirmation Required</span>
                <div class="inspector-value" id="insp-conf">FALSE</div>
            </div>

            <div class="inspector-field">
                <span class="inspector-label">Final Result Status</span>
                <div class="inspector-value" id="insp-status" style="color:#68D391;">SUCCESS (Latency: 48ms)</div>
            </div>
        </aside>

    </div>

    <script>
        const sessionId = "lara_web_" + Math.random().toString(36).substring(2, 9);
        document.getElementById('session-display').textContent = "Session: " + sessionId;
        const liveActivityRecords = [];

        function showTab(tabId, el) {
            document.querySelectorAll('.console-view').forEach(v => v.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));

            const target = document.getElementById('view-' + tabId);
            if (target) target.classList.add('active');

            if (el) {
                el.classList.add('active');
            } else {
                const matchedNav = Array.from(document.querySelectorAll('.nav-item')).find(n => n.getAttribute('onclick')?.includes(tabId));
                if (matchedNav) matchedNav.classList.add('active');
            }
        }

        function openInspectorDrawer() {
            document.getElementById('inspector-drawer').classList.add('open');
        }

        function closeInspectorDrawer() {
            document.getElementById('inspector-drawer').classList.remove('open');
        }

        function appendMessage(role, text, showDetailsLink = false) {
            const stream = document.getElementById('chat-messages');
            const row = document.createElement('div');
            row.className = `message-row ${role}`;
            let content = `<div class="message-bubble ${role}"><strong>${role === 'user' ? 'You' : 'LARA'}:</strong> ${text}`;
            if (role === 'assistant' && showDetailsLink) {
                content += `<div style="margin-top:8px; font-size:11px;"><a href="javascript:void(0)" onclick="openInspectorDrawer()" style="color:var(--orange); text-decoration:underline;">View details</a></div>`;
            }
            content += `</div>`;
            row.innerHTML = content;
            stream.appendChild(row);
            stream.scrollTop = stream.scrollHeight;

            if (role === 'user') {
                recordActivity(text, 'User Query');
            }
        }

        function recordActivity(title, category) {
            const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            liveActivityRecords.unshift({ time: timeStr, title: title, category: category });
            renderActivityTable();
        }

        function renderActivityTable() {
            const tbody = document.getElementById('activity-table-body');
            const overviewList = document.getElementById('overview-activity-list');
            if (liveActivityRecords.length === 0) {
                tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color:var(--text-muted);">No activity recorded yet in this session.</td></tr>`;
                overviewList.innerHTML = `<div style="color:var(--text-secondary);">Ready for instructions. All actions will appear here dynamically.</div>`;
                return;
            }
            tbody.innerHTML = liveActivityRecords.map(r => `
                <tr>
                    <td>${r.time}</td>
                    <td>${r.title}</td>
                    <td>${r.category}</td>
                    <td><span class="pill-status active">COMPLETED</span></td>
                </tr>
            `).join('');

            overviewList.innerHTML = liveActivityRecords.slice(0, 3).map(r => `
                <div style="display:flex; justify-content:space-between;">
                    <span>${r.title}</span>
                    <span style="color:var(--text-muted);">${r.time}</span>
                </div>
            `).join('');
        }

        function clearActivityFeed() {
            liveActivityRecords.length = 0;
            renderActivityTable();
        }

        async function sendMessage() {
            const input = document.getElementById('user-input');
            const text = input.value.trim();
            if (!text) return;

            appendMessage('user', text);
            input.value = '';

            // Update Inspector Preview
            document.getElementById('insp-raw').textContent = `"${text}"`;
            document.getElementById('insp-intent').textContent = "PROCESSING...";

            try {
                const resp = await fetch('/api/v1/chat/message', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: sessionId,
                        message: text
                    })
                });
                const data = await resp.json();
                if (resp.ok) {
                    appendMessage('assistant', data.response, true);
                    speakText(data.response);

                    // Update Inspector with actual router metadata
                    const meta = data.metadata || {};
                    const routing = meta.routing || {};
                    document.getElementById('insp-intent').textContent = routing.tier_used || "EXECUTED";
                    document.getElementById('insp-router').textContent = `Tier: ${routing.tier_used || 'FAST'}`;
                    document.getElementById('insp-target').textContent = data.sources ? data.sources.join(', ') : "Agent Engine";
                    document.getElementById('insp-risk').textContent = data.requires_confirmation ? "HIGH (CONFIRMATION REQUIRED)" : "LOW (AUTOMATIC)";
                    document.getElementById('insp-status').textContent = `SUCCESS (${meta.latency_ms ? meta.latency_ms.toFixed(1) : 0}ms)`;
                    document.getElementById('diag-lat-total').textContent = `${meta.latency_ms ? meta.latency_ms.toFixed(1) : 0}ms`;
                } else {
                    appendMessage('assistant', "Encountered an error: " + (data.detail || "Server error"));
                }
            } catch (err) {
                appendMessage('assistant', "Network communication error: " + err.message);
            }
        }

        function sendQuickMessage(text) {
            document.getElementById('user-input').value = text;
            sendMessage();
        }

        async function triggerVisionCaptureDescribe() {
            appendMessage('user', 'Capture + Describe scene from Smart Glasses');
            appendMessage('assistant', 'Capturing camera frame and analyzing scene...');
            document.getElementById('insp-raw').textContent = '"Capture + Describe"';
            document.getElementById('insp-intent').textContent = 'VISION_SCENE_UNDERSTANDING';

            try {
                const resp = await fetch('/api/v1/vision/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: sessionId,
                        prompt: "What do you see in front of me?",
                        device_id: "SmartGlasses-S3"
                    })
                });
                const data = await resp.json();
                if (resp.ok) {
                    let out = `Vision Analysis (${data.provider}):\n\n${data.description}`;
                    if (data.objects && data.objects.length > 0) {
                        out += `\n\nDetected Objects: ${data.objects.join(', ')}`;
                    }
                    appendMessage('assistant', out, true);
                    speakText(data.description);
                    document.getElementById('insp-status').textContent = `COMPLETE (${data.latency_ms.toFixed(0)}ms)`;
                    document.getElementById('hw-last-cap-id').textContent = data.capture_id || "cap_s3";
                }
            } catch (err) {
                appendMessage('assistant', 'Vision capture error: ' + err.message);
            }
        }

        async function triggerMultimodalCapture() {
            appendMessage('user', 'Multimodal Capture (ESP32 Mic + Camera)');
            appendMessage('assistant', 'Capturing photo and listening to ESP32 digital mic...');
            try {
                const resp = await fetch('/api/v1/hardware/multimodal/capture', { method: 'POST' });
                const data = await resp.json();
                if (resp.ok) {
                    appendMessage('assistant', `ESP32 Mic: "${data.spoken_query}"\n\nLARA: ${data.speech_response}`, true);
                    speakText(data.speech_response);
                }
            } catch (err) {
                appendMessage('assistant', 'Multimodal capture error: ' + err.message);
            }
        }

        async function triggerQuadraticVision() {
            sendQuickMessage("Solve quadratic equation x^2 + 5x + 6 = 0");
        }

        async function triggerQrScan() {
            appendMessage('user', 'Scan QR Code from Glasses Camera');
            try {
                const resp = await fetch('/api/v1/vision/qr/scan', { method: 'POST' });
                const data = await resp.json();
                if (resp.ok) {
                    appendMessage('assistant', `QR Code: ${data.speech_response || data.raw_content}`, true);
                    speakText(data.speech_response);
                }
            } catch (err) {
                appendMessage('assistant', 'QR Scan error: ' + err.message);
            }
        }

        async function simulateIncomingSmsPrompt() {
            const sender = "+15550192834";
            const text = prompt("Enter SMS Body to simulate inbound alert:", "URGENT: Executive review required for contract #982");
            if (!text) return;
            appendMessage('user', `[Incoming SMS from ${sender}]: ${text}`);
            try {
                const resp = await fetch('/api/v1/sms/receive', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sender: sender, body: text })
                });
                const data = await resp.json();
                if (resp.ok) {
                    appendMessage('assistant', `SMS Processed: ${data.reply_sent || data.action || 'Alert prioritized and queued'}`, true);
                }
            } catch (err) {
                appendMessage('assistant', 'SMS processing error: ' + err.message);
            }
        }

        async function handleStaffFileUpload(input) {
            const file = input.files[0];
            if (!file) return;
            const statusBox = document.getElementById('upload-status-box');
            statusBox.style.display = 'block';
            statusBox.innerHTML = `Uploading and parsing <strong>${file.name}</strong>...`;

            try {
                const formData = new FormData();
                formData.append('file', file);

                const resp = await fetch('/api/v1/desk/upload', {
                    method: 'POST',
                    body: formData
                });
                const data = await resp.json();
                if (resp.ok) {
                    const ds = data.dataset || {};
                    statusBox.innerHTML = `<span style="color:#68D391; font-weight:bold;">[SUCCESS] Ingested '${file.name}'</span> (${ds.rows || 0} rows, ${ds.columns || 0} columns). Ready for queries.`;
                    document.getElementById('desk-dataset-badge').textContent = `Active Dataset: ${file.name}`;
                    recordActivity(`Staff uploaded '${file.name}' (${ds.rows} records)`, 'Data Upload');
                    runDeskAnalysis('summarize');
                } else {
                    statusBox.innerHTML = `<span style="color:#B83A3A;">Upload failed: ${data.detail || data.message}</span>`;
                }
            } catch (err) {
                statusBox.innerHTML = `<span style="color:#B83A3A;">Upload network error: ${err.message}</span>`;
            }
        }

        async function runDeskAnalysis(op) {
            const resultsBox = document.getElementById('desk-results');
            resultsBox.innerHTML = `Running <strong>${op.toUpperCase()}</strong> on active dataset...`;
            try {
                const resp = await fetch('/api/v1/desk/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ operation: op })
                });
                const data = await resp.json();
                if (resp.ok) {
                    resultsBox.innerHTML = `
                        <div style="color:#68D391; font-weight:bold; margin-bottom:8px;">[COMPLETED] ${data.operation.toUpperCase()} (Confidence: ${(data.confidence*100).toFixed(0)}%)</div>
                        <div style="margin-bottom:8px;">${data.findings}</div>
                        <div style="color:var(--text-muted); font-size:11px;">Source: ${data.source} · Records: ${data.rows} rows · Columns: ${data.columns}</div>
                    `;
                }
            } catch (err) {
                resultsBox.textContent = "Error executing desk analysis: " + err.message;
            }
        }

        async function executeCustomDataQuery() {
            const queryInput = document.getElementById('desk-query-input');
            const query = queryInput.value.trim();
            if (!query) return;

            const resultsBox = document.getElementById('desk-results');
            resultsBox.innerHTML = `Analyzing dataset for query: <em>"${query}"</em>...`;

            try {
                const resp = await fetch('/api/v1/data-analysis/query', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                });
                const data = await resp.json();
                if (resp.ok) {
                    resultsBox.innerHTML = `
                        <div style="color:#68D391; font-weight:bold; margin-bottom:8px;">[QUERY RESULT] for "${query}"</div>
                        <div style="font-size:14px; margin-bottom:8px;">${data.answer}</div>
                        <div style="color:var(--text-muted); font-size:11px;">Target Dataset: ${data.dataset}</div>
                    `;
                    recordActivity(`Analyzed dataset: "${query}"`, 'Analytics Query');
                } else {
                    resultsBox.textContent = "Query failed: " + (data.detail || "Unknown error");
                }
            } catch (err) {
                resultsBox.textContent = "Error querying dataset: " + err.message;
            }
        }

        async function checkGoogleAuthStatus() {
            try {
                const resp = await fetch('/api/v1/auth/status');
                if (resp.ok) {
                    const data = await resp.json();
                    const pill = document.getElementById('google-status-pill');
                    const topPill = document.getElementById('pill-google');
                    const btn = document.getElementById('btn-google-auth');
                    if (data.is_authenticated) {
                        pill.className = 'pill-status active';
                        pill.innerHTML = `<span class="pill-dot"></span> Authorized (${data.email || 'Google'})`;
                        topPill.className = 'pill-status active';
                        btn.textContent = 'Disconnect';
                        btn.className = 'btn-quick-chip';
                        btn.onclick = disconnectGoogleOAuth;
                    } else {
                        pill.className = 'pill-status';
                        pill.textContent = 'Not Connected';
                        btn.textContent = 'Connect Google';
                        btn.className = 'btn-quick-chip primary';
                        btn.onclick = connectGoogleOAuth;
                    }
                }
            } catch (e) {}
        }

        function connectGoogleOAuth() {
            window.location.href = '/api/v1/auth/google';
        }

        async function disconnectGoogleOAuth() {
            if (!confirm('Disconnect Google Workspace?')) return;
            try {
                await fetch('/api/v1/auth/disconnect', { method: 'POST' });
                checkGoogleAuthStatus();
            } catch (e) {}
        }

        async function refreshAuditLogs() {
            const box = document.getElementById('audit-log-content');
            box.textContent = "Fetching audit logs...";
            try {
                const resp = await fetch('/api/v1/security/audit-log');
                const data = await resp.json();
                if (resp.ok && data.audit_logs) {
                    box.innerHTML = data.audit_logs.map(l => `[${new Date(l.timestamp*1000).toLocaleTimeString()}] <strong>${l.event_type}</strong> · ${l.status} · user=${l.user_id}`).join('<br>');
                } else {
                    box.textContent = "No audit log entries recorded.";
                }
            } catch (err) {
                box.textContent = "Could not load audit logs: " + err.message;
            }
        }

        function speakText(text) {
            if (!text || !('speechSynthesis' in window)) return;
            window.speechSynthesis.cancel();
            const clean = text.replace(/[\*\_`#]/g, '').replace(/https?:\/\/\S+/g, '');
            const utter = new SpeechSynthesisUtterance(clean);
            utter.rate = 1.05;
            utter.pitch = 1.0;
            window.speechSynthesis.speak(utter);
        }

        function toggleVoiceInput() {
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                alert("Speech recognition is not supported in this browser.");
                return;
            }
            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            const rec = new SpeechRec();
            rec.lang = 'en-US';
            rec.start();
            const btn = document.getElementById('mic-btn');
            btn.textContent = "Listening...";
            rec.onresult = (e) => {
                const trans = e.results[0][0].transcript;
                document.getElementById('user-input').value = trans;
                sendMessage();
            };
            rec.onend = () => { btn.textContent = "Voice"; };
            rec.onerror = () => { btn.textContent = "Voice"; };
        }

        // -------------------------------------------------------------
        // Glasses Logs, Conversation Stream, Requests & Contacts Hub
        // -------------------------------------------------------------

        async function refreshGlassesLogs() {
            try {
                const resp = await fetch('/api/v1/telemetry/glasses-logs?limit=40');
                const data = await resp.json();
                const tbody = document.getElementById('glasses-logs-tbody');
                if (data.success && data.logs && data.logs.length > 0) {
                    tbody.innerHTML = data.logs.map(l => {
                        let lvlColor = l.level === 'ERROR' ? 'var(--red)' : (l.level === 'WARN' ? 'var(--amber)' : '#68D391');
                        return `
                            <tr>
                                <td style="font-family:'JetBrains Mono',monospace; font-size:11px; color:var(--text-muted);">${l.time_str}</td>
                                <td><strong style="color:var(--text-primary);">${l.event_type}</strong></td>
                                <td><span class="pill-status">${l.source}</span></td>
                                <td><span style="color:${lvlColor}; font-weight:700; font-size:11px;">${l.level}</span></td>
                                <td style="font-family:'JetBrains Mono',monospace; font-size:12px; color:var(--text-secondary);">${typeof l.details === 'object' ? JSON.stringify(l.details) : l.details}</td>
                            </tr>
                        `;
                    }).join('');
                } else {
                    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:var(--text-muted);">No hardware events logged yet.</td></tr>';
                }
            } catch (err) {
                console.error("Failed to fetch glasses logs", err);
            }
        }

        async function refreshConversationStream() {
            try {
                const resp = await fetch('/api/v1/telemetry/conversation-stream?limit=30');
                const data = await resp.json();
                const container = document.getElementById('conv-stream-container');
                if (data.success && data.messages && data.messages.length > 0) {
                    container.innerHTML = data.messages.map(m => {
                        const isUser = m.role === 'user';
                        const timeStr = new Date(m.timestamp * 1000).toLocaleTimeString();
                        return `
                            <div style="background:${isUser ? 'var(--bg-subtle)' : 'var(--bg-surface-elevated)'}; border:1px solid var(--border); border-left:3px solid ${isUser ? 'var(--orange)' : '#68D391'}; padding:12px 16px; border-radius:var(--radius-sm);">
                                <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                                    <span style="font-size:11px; font-weight:700; color:${isUser ? 'var(--orange)' : '#68D391'}; text-transform:uppercase;">
                                        ${isUser ? 'Glasses User (Voice/Button)' : 'LARA AI Assistant'}
                                    </span>
                                    <span style="font-size:10px; color:var(--text-muted);">${timeStr}</span>
                                </div>
                                <div style="font-size:13px; color:var(--text-primary); line-height:1.5;">${m.content}</div>
                                <div style="margin-top:6px; display:flex; justify-content:flex-end;">
                                    <button class="btn-quick-chip" style="padding:2px 8px; font-size:10px;" onclick="speakText('${m.content.replace(/'/g, "\\'")}')">Speak</button>
                                </div>
                            </div>
                        `;
                    }).join('');
                } else {
                    container.innerHTML = '<div style="color:var(--text-muted); font-size:13px;">No conversation history available.</div>';
                }
            } catch (err) {
                console.error("Failed to fetch conversation stream", err);
            }
        }

        async function refreshRequestLogs() {
            try {
                const resp = await fetch('/api/v1/telemetry/requests?limit=40');
                const data = await resp.json();
                const tbody = document.getElementById('requests-tbody');
                if (data.success && data.requests && data.requests.length > 0) {
                    tbody.innerHTML = data.requests.map(r => {
                        const isSuccess = r.status === 'SUCCESS';
                        const badgeStyle = isSuccess 
                            ? 'background:rgba(45,125,70,0.2); color:#68D391; border:1px solid rgba(45,125,70,0.4);' 
                            : 'background:rgba(184,58,58,0.2); color:#F56565; border:1px solid rgba(184,58,58,0.4);';
                        return `
                            <tr>
                                <td style="font-family:'JetBrains Mono',monospace; font-size:11px; color:var(--text-muted);">${r.time_str}</td>
                                <td>
                                    <div style="font-size:13px; font-weight:600; color:var(--text-primary);">${r.query}</div>
                                    <div style="font-size:10px; font-family:'JetBrains Mono',monospace; color:var(--text-muted);">${r.request_id}</div>
                                </td>
                                <td>
                                    <span style="padding:3px 8px; border-radius:12px; font-size:11px; font-weight:700; ${badgeStyle}">
                                        ${r.status}
                                    </span>
                                </td>
                                <td><strong style="color:var(--orange);">${r.latency_ms}ms</strong></td>
                                <td style="font-size:12px; color:${r.error ? '#F56565' : 'var(--text-muted)'};">${r.error || 'None (Processed cleanly)'}</td>
                            </tr>
                        `;
                    }).join('');
                } else {
                    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:var(--text-muted);">No requests recorded yet.</td></tr>';
                }
            } catch (err) {
                console.error("Failed to fetch requests", err);
            }
        }

        async function loadContactsHub() {
            try {
                const resp = await fetch('/api/v1/contacts/list');
                const data = await resp.json();
                const grid = document.getElementById('contacts-card-grid');
                if (data.success && data.contacts) {
                    grid.innerHTML = data.contacts.map(c => `
                        <div style="background:var(--bg-subtle); border:1px solid var(--border); border-radius:var(--radius-md); padding:16px;">
                            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
                                <div>
                                    <div style="font-size:15px; font-weight:700; color:var(--text-primary);">${c.name}</div>
                                    <div style="font-size:11px; color:var(--orange); font-weight:600; text-transform:uppercase;">${c.role}</div>
                                </div>
                                ${c.starred ? '<span style="font-size:11px; color:#ECC94B; font-weight:700;">★ Priority</span>' : ''}
                            </div>
                            <div style="font-size:12px; font-family:'JetBrains Mono',monospace; color:var(--text-secondary); margin-bottom:4px;">${c.phone}</div>
                            <div style="font-size:12px; color:var(--text-muted); margin-bottom:14px;">${c.email}</div>
                            <div style="display:flex; gap:6px;">
                                <button class="btn-quick-chip primary" style="padding:4px 10px; font-size:11px;" onclick="triggerQuickCall('${c.name}', '${c.phone}')">Call</button>
                                <button class="btn-quick-chip" style="padding:4px 10px; font-size:11px;" onclick="triggerQuickSms('${c.name}', '${c.phone}')">SMS</button>
                                <button class="btn-quick-chip" style="padding:4px 10px; font-size:11px;" onclick="triggerQuickEmail('${c.name}', '${c.email}')">Email</button>
                            </div>
                        </div>
                    `).join('');
                }
            } catch (err) {
                console.error("Failed to load contacts", err);
            }
        }

        async function triggerQuickCall(name, phone) {
            try {
                const resp = await fetch('/api/v1/contacts/call', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: name, phone: phone })
                });
                const data = await resp.json();
                if (resp.ok) {
                    speakText(data.speech_response);
                    recordActivity(`Initiated call to ${name} (${phone})`, 'Telephony');
                    refreshGlassesLogs();
                    refreshRequestLogs();
                }
            } catch (e) {
                alert("Call trigger failed: " + e.message);
            }
        }

        async function triggerQuickSms(name, phone) {
            const msg = prompt(`Enter SMS message for ${name}:`, "I am on my way.");
            if (!msg) return;
            try {
                const resp = await fetch('/api/v1/contacts/sms', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: name, phone: phone, message: msg })
                });
                const data = await resp.json();
                if (resp.ok) {
                    speakText(data.speech_response);
                    recordActivity(`Sent SMS to ${name}: "${msg}"`, 'SMS Dispatch');
                    refreshGlassesLogs();
                    refreshRequestLogs();
                }
            } catch (e) {
                alert("SMS dispatch failed: " + e.message);
            }
        }

        async function triggerQuickEmail(name, email) {
            const subj = prompt(`Enter Email subject for ${name}:`, "Smart Glasses Update");
            if (!subj) return;
            try {
                const resp = await fetch('/api/v1/contacts/email', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: name, email: email, subject: subj, body: "Sent from Smart Glasses Web Console." })
                });
                const data = await resp.json();
                if (resp.ok) {
                    speakText(data.speech_response);
                    recordActivity(`Sent Email to ${name} (${subj})`, 'Email Dispatch');
                    refreshGlassesLogs();
                    refreshRequestLogs();
                }
            } catch (e) {
                alert("Email dispatch failed: " + e.message);
            }
        }

        async function triggerManualCall() {
            const target = document.getElementById('manual-contact-target').value.trim();
            if (!target) { alert("Please specify recipient name or phone number."); return; }
            triggerQuickCall(target, target);
        }

        async function triggerManualSms() {
            const target = document.getElementById('manual-contact-target').value.trim();
            const msg = document.getElementById('manual-contact-msg').value.trim() || "Status update from smart glasses.";
            if (!target) { alert("Please specify recipient name or phone number."); return; }
            try {
                const resp = await fetch('/api/v1/contacts/sms', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: target, phone: target, message: msg })
                });
                const data = await resp.json();
                const statusBox = document.getElementById('manual-dispatch-status');
                statusBox.style.display = 'block';
                statusBox.innerHTML = `<span style="color:#68D391;">✓ ${data.speech_response}</span>`;
                speakText(data.speech_response);
                refreshGlassesLogs();
                refreshRequestLogs();
            } catch (e) {
                alert("Manual SMS failed: " + e.message);
            }
        }

        async function triggerManualEmail() {
            const target = document.getElementById('manual-contact-target').value.trim();
            const msg = document.getElementById('manual-contact-msg').value.trim() || "Smart Glasses report.";
            if (!target) { alert("Please specify recipient name or email address."); return; }
            try {
                const resp = await fetch('/api/v1/contacts/email', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: target, email: target, subject: "Smart Glasses Dispatch", body: msg })
                });
                const data = await resp.json();
                const statusBox = document.getElementById('manual-dispatch-status');
                statusBox.style.display = 'block';
                statusBox.innerHTML = `<span style="color:#68D391;">✓ ${data.speech_response}</span>`;
                speakText(data.speech_response);
                refreshGlassesLogs();
                refreshRequestLogs();
            } catch (e) {
                alert("Manual Email failed: " + e.message);
            }
        }

        // Periodic Telemetry Updates (Every 3-5 seconds)
        async function updateHardwareStatus() {
            refreshGlassesLogs();
            refreshRequestLogs();
            return await updateLiveTelemetry();
        }

        async function updateLiveTelemetry() {
            try {
                const resp = await fetch('/api/v1/hardware/status');
                if (resp.ok) {
                    const hw = await resp.json();
                    if (hw.microphone && hw.microphone.live_rms) {
                        const pct = Math.min(100, Math.max(5, (hw.microphone.live_rms / 2500.0) * 100));
                        document.getElementById('hw-mic-fill').style.width = pct + '%';
                    }
                    if (hw.last_vision_status) {
                        document.getElementById('hw-last-vis-status').textContent = hw.last_vision_status;
                    }
                }
            } catch (e) {}
        }

        setInterval(updateHardwareStatus, 3500);
        updateHardwareStatus();
        checkGoogleAuthStatus();
        refreshAuditLogs();
        loadContactsHub();
        refreshConversationStream();
    </script>
</body>
</html>"""
