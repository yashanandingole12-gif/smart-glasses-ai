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

        // Periodic Telemetry Updates (Every 5 seconds)
        async function updateHardwareStatus() {
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

        setInterval(updateHardwareStatus, 5000);
        updateHardwareStatus();
        checkGoogleAuthStatus();
        refreshAuditLogs();
    </script>
</body>
</html>"""
