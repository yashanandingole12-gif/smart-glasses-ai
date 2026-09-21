def get_dashboard_html() -> str:
    """
    Returns EVA: The Living Digital Atmosphere & Private Intelligence Realm.
    Master Web Experience featuring 'Color Existing Inside Darkness',
    reusable Atmosphere Engine (GROUNDED, FOCUSED, CREATIVE, CURIOUS, REFLECTIVE,
    ENERGETIC, NIGHT, CUSTOM), organic Tone Shifting (800-1800ms),
    ambient Presence Orb, Document Knowledge System, and Research Constellation.
    """
    return r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <!-- LARA Smart Glasses Operations Console | ESP32 Smart Glasses & Android Hub | Private Intelligence & Control | Intent Inspector | Desk & Data Analysis | Automations Center | Smart Notifications -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EVA — Color Atmosphere System &amp; Private Intelligence</title>
    <script>
        function updateHardwareStatus(d){console.debug("Hardware sync", d);}
        function simulateIncomingSmsPrompt(){console.debug("Simulate SMS");}
        function triggerMultimodalCapture(){console.debug("Multimodal capture");}
    </script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            /* ========================================================= */
            /* EXTRACTED EVA PALETTE (Color Existing Inside Darkness)    */
            /* ========================================================= */
            /* FOUNDATION */
            --eva-void: #0C0805;
            --eva-night: #161411;
            --eva-earth-black: #190903;
            --eva-charcoal: #2B221E;

            /* EARTH */
            --eva-umber: #301306;
            --eva-copper: #552804;
            --eva-amber-brown: #703912;
            --eva-bronze: #7F582D;

            /* LIGHT */
            --eva-gold: #D3A95B;
            --eva-amber: #B1650E;
            --eva-sunlight: #ECDBA1;
            --eva-ivory: #F8F0E2;

            /* GREEN */
            --eva-olive-black: #0C0C08;
            --eva-moss: #484428;
            --eva-olive: #6D6333;
            --eva-sage: #848157;

            /* ROSE */
            --eva-wine: #510A16;
            --eva-crimson: #932D44;
            --eva-mauve: #A7788E;

            /* ========================================================= */
            /* ACTIVE DYNAMIC ATMOSPHERE TOKENS (Default: GROUNDED)      */
            /* ========================================================= */
            --atm-foundation: #0C0C08;
            --atm-night-base: #161411;
            --atm-accent: #6D6333;
            --atm-highlight: #B49E45;
            --atm-surface: rgba(22, 20, 15, 0.72);
            --atm-surface-elevated: rgba(33, 30, 22, 0.78);
            --atm-border: rgba(109, 99, 51, 0.32);
            --atm-border-focus: rgba(180, 158, 69, 0.55);
            --atm-glow: rgba(180, 158, 69, 0.22);
            --atm-glow-opacity: 0.22;
            --atm-motion-scale: 0.85;
            --atm-transition-ms: 1400ms;

            /* TYPOGRAPHY */
            --text-pure: #F8F0E2;
            --text-primary: #ECDBA1;
            --text-secondary: #848157;
            --text-muted: #645F45;
            --text-highlight: #D3A95B;

            --font-display: 'Cinzel', serif;
            --font-body: 'Inter', -apple-system, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;

            --radius-sm: 8px;
            --radius-md: 14px;
            --radius-lg: 24px;
            --radius-full: 9999px;

            --ease-organic: cubic-bezier(0.16, 1, 0.3, 1);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-font-smoothing: antialiased;
        }

        body {
            background-color: var(--atm-foundation);
            color: var(--text-primary);
            font-family: var(--font-body);
            min-height: 100vh;
            overflow-x: hidden;
            display: flex;
            flex-direction: column;
            position: relative;
            user-select: none;
            transition: background-color 1.4s var(--ease-organic), color 1.4s ease;
        }

        /* Living Particle & Depth Canvas */
        #living-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 0;
            pointer-events: none;
        }

        /* Atmospheric Header */
        .eva-header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 64px;
            padding: 0 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            z-index: 50;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--atm-border);
            background: rgba(12, 8, 5, 0.75);
            transition: background 1.4s var(--ease-organic), border-color 1.4s ease;
        }

        .eva-brand {
            display: flex;
            align-items: center;
            gap: 10px;
            cursor: pointer;
        }

        .eva-symbol {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: radial-gradient(circle, var(--atm-highlight) 0%, transparent 80%);
            box-shadow: 0 0 12px var(--atm-highlight);
            animation: pulseGlow 3.5s ease-in-out infinite alternate;
            transition: background 1.4s ease, box-shadow 1.4s ease;
        }

        @keyframes pulseGlow {
            0% { transform: scale(0.9); opacity: 0.7; }
            100% { transform: scale(1.2); opacity: 1; }
        }

        .eva-title {
            font-family: var(--font-display);
            font-size: 17px;
            letter-spacing: 4px;
            color: var(--text-pure);
            font-weight: 700;
        }

        .eva-presence-badge {
            font-size: 9px;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            color: var(--atm-highlight);
            border: 1px solid var(--atm-border);
            padding: 2px 8px;
            border-radius: var(--radius-full);
            background: var(--atm-surface);
            font-family: var(--font-mono);
            transition: all 1.2s var(--ease-organic);
        }

        /* Tone Atmosphere Switcher Bar */
        .eva-atmosphere-switcher {
            display: flex;
            align-items: center;
            gap: 4px;
            background: var(--atm-surface);
            padding: 3px 6px;
            border-radius: var(--radius-full);
            border: 1px solid var(--atm-border);
            backdrop-filter: blur(12px);
            transition: all 1.2s var(--ease-organic);
        }

        .atm-pill {
            background: transparent;
            border: 1px solid transparent;
            color: var(--text-secondary);
            font-size: 11px;
            font-weight: 500;
            padding: 4px 10px;
            border-radius: var(--radius-full);
            cursor: pointer;
            transition: all 0.4s var(--ease-organic);
            display: flex;
            align-items: center;
            gap: 6px;
            font-family: var(--font-body);
        }

        .atm-pill:hover {
            color: var(--text-pure);
            background: rgba(255, 255, 255, 0.04);
        }

        .atm-pill.active {
            color: var(--text-pure);
            background: rgba(255, 255, 255, 0.07);
            border-color: var(--atm-highlight);
            box-shadow: 0 0 12px var(--atm-glow);
        }

        .atm-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 6px currentColor;
        }

        .eva-nav-modes {
            display: flex;
            align-items: center;
            gap: 4px;
            background: var(--atm-surface);
            padding: 3px 6px;
            border-radius: var(--radius-full);
            border: 1px solid var(--atm-border);
            transition: all 1.2s var(--ease-organic);
        }

        .nav-mode-btn {
            background: transparent;
            border: 1px solid transparent;
            color: var(--text-secondary);
            font-size: 12px;
            font-weight: 500;
            padding: 5px 12px;
            border-radius: var(--radius-full);
            cursor: pointer;
            transition: all 0.3s var(--ease-organic);
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .nav-mode-btn:hover {
            color: var(--text-pure);
            background: rgba(255, 255, 255, 0.04);
        }

        .nav-mode-btn.active {
            color: var(--text-pure);
            background: rgba(255, 255, 255, 0.08);
            border-color: var(--atm-border);
            box-shadow: 0 0 12px var(--atm-glow);
        }

        .header-meta {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 11px;
            color: var(--text-muted);
            font-family: var(--font-mono);
        }

        .status-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: var(--atm-highlight);
            box-shadow: 0 0 8px var(--atm-highlight);
            transition: background 1.4s ease, box-shadow 1.4s ease;
        }

        /* Main Spatial Viewport */
        .spatial-viewport {
            flex: 1;
            padding: 84px 32px 130px 32px;
            max-width: 1200px;
            margin: 0 auto;
            width: 100%;
            z-index: 10;
            position: relative;
        }

        /* Spatial Panels */
        .spatial-panel {
            width: 100%;
            display: none;
            animation: fadeInLayer 0.4s var(--ease-organic) forwards;
        }

        .spatial-panel.active {
            display: block;
        }

        @keyframes fadeInLayer {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* ========================================================= */
        /* MODE 1: LIVING PRESENCE (Ambient Atmospheric Orb)         */
        /* ========================================================= */
        .presence-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 30px 0 20px 0;
            position: relative;
        }

        .core-presence-orb {
            width: 140px;
            height: 140px;
            border-radius: 50%;
            position: relative;
            cursor: pointer;
            transition: all 1.2s var(--ease-organic);
            margin-bottom: 24px;
        }

        .orb-halo {
            position: absolute;
            inset: -20px;
            border-radius: 50%;
            background: radial-gradient(circle, var(--atm-accent) 0%, transparent 70%);
            opacity: var(--atm-glow-opacity);
            animation: orbHaloBreath 6s ease-in-out infinite;
            transition: all 1.4s ease;
        }

        .orb-ring {
            position: absolute;
            inset: -4px;
            border-radius: 50%;
            border: 1px solid var(--atm-border);
            animation: orbRingRotate 22s linear infinite;
            transition: border-color 1.4s ease;
        }

        .orb-center {
            position: absolute;
            inset: 8px;
            border-radius: 50%;
            background: radial-gradient(circle at 35% 35%, var(--atm-highlight) 0%, var(--atm-accent) 45%, var(--atm-foundation) 90%);
            box-shadow: 0 0 32px var(--atm-glow), inset 0 0 18px rgba(255, 255, 255, 0.15);
            transition: all 1.4s ease;
        }

        @keyframes orbHaloBreath {
            0%, 100% { transform: scale(0.95); opacity: calc(var(--atm-glow-opacity) * 0.8); }
            50% { transform: scale(1.2); opacity: calc(var(--atm-glow-opacity) * 1.3); }
        }

        @keyframes orbRingRotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        /* Orb State Color Radiance */
        .core-presence-orb[data-state="LISTENING"] .orb-center {
            background: radial-gradient(circle at 35% 35%, var(--eva-sunlight) 0%, var(--eva-amber) 45%, var(--atm-foundation) 90%);
            box-shadow: 0 0 40px rgba(236, 219, 161, 0.6);
        }
        .core-presence-orb[data-state="THINKING"] .orb-center {
            background: radial-gradient(circle at 35% 35%, var(--eva-mauve) 0%, var(--eva-wine) 45%, var(--atm-foundation) 90%);
            box-shadow: 0 0 40px rgba(181, 123, 136, 0.6);
            animation: pulseGlow 1.4s ease-in-out infinite alternate;
        }
        .core-presence-orb[data-state="SPEAKING"] .orb-center {
            background: radial-gradient(circle at 35% 35%, var(--eva-ivory) 0%, var(--eva-gold) 45%, var(--atm-foundation) 90%);
            box-shadow: 0 0 40px rgba(211, 169, 91, 0.7);
        }

        .presence-state-text {
            font-family: var(--font-display);
            font-size: 14px;
            letter-spacing: 3px;
            color: var(--text-pure);
            text-transform: uppercase;
            margin-bottom: 12px;
            transition: color 1.2s ease;
        }

        .waveform-strip {
            display: flex;
            align-items: center;
            gap: 4px;
            height: 24px;
        }

        .waveform-bar {
            width: 3px;
            background: var(--atm-highlight);
            border-radius: var(--radius-full);
            transition: height 0.15s ease, background-color 1.4s ease;
        }

        /* Active Focus Card in Presence (Clean, focused) */
        .active-focus-container {
            max-width: 680px;
            margin: 20px auto 0 auto;
            width: 100%;
        }

        .active-focus-card {
            background: var(--atm-surface);
            backdrop-filter: blur(16px);
            border: 1px solid var(--atm-border);
            border-radius: var(--radius-md);
            padding: 24px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4), 0 0 20px var(--atm-glow);
            position: relative;
            transition: all 1.4s var(--ease-organic);
        }

        .focus-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 11px;
            color: var(--text-secondary);
            margin-bottom: 12px;
            font-family: var(--font-mono);
        }

        .focus-text {
            font-size: 15px;
            color: var(--text-pure);
            line-height: 1.6;
            margin-bottom: 16px;
        }

        .focus-footer {
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-top: 1px solid var(--atm-border);
            padding-top: 12px;
            transition: border-color 1.4s ease;
        }

        .proactive-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 16px;
            justify-content: center;
        }

        .meta-chip {
            font-size: 11px;
            color: var(--text-secondary);
            background: var(--atm-surface);
            border: 1px solid var(--atm-border);
            padding: 6px 14px;
            border-radius: var(--radius-full);
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: var(--font-body);
        }

        .meta-chip:hover {
            color: var(--text-pure);
            border-color: var(--atm-highlight);
            background: rgba(255, 255, 255, 0.05);
            box-shadow: 0 0 10px var(--atm-glow);
        }

        /* ========================================================= */
        /* MODE 2: ACTIVITY TIMELINE & OPERATIONAL SESSIONS          */
        /* ========================================================= */
        .activity-header-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 24px;
            flex-wrap: wrap;
            gap: 16px;
        }

        .activity-title-group h2 {
            font-family: var(--font-display);
            font-size: 20px;
            letter-spacing: 2px;
            color: var(--text-pure);
            margin-bottom: 4px;
        }

        .activity-title-group p {
            font-size: 13px;
            color: var(--text-secondary);
        }

        .timeline-filter-pills {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }

        .filter-pill {
            font-size: 11px;
            color: var(--text-muted);
            background: var(--atm-surface);
            border: 1px solid var(--atm-border);
            padding: 5px 12px;
            border-radius: var(--radius-full);
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: var(--font-mono);
        }

        .filter-pill.active {
            color: var(--text-pure);
            border-color: var(--atm-highlight);
            background: rgba(255, 255, 255, 0.08);
            box-shadow: 0 0 10px var(--atm-glow);
        }

        .sessions-summary-card {
            background: var(--atm-surface);
            border: 1px solid var(--atm-border);
            border-radius: var(--radius-md);
            padding: 16px 20px;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
            transition: all 1.4s var(--ease-organic);
        }

        .session-badge-active {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            color: var(--atm-highlight);
            font-family: var(--font-mono);
        }

        .timeline-stream {
            display: flex;
            flex-direction: column;
            gap: 14px;
        }

        .timeline-event-card {
            background: var(--atm-surface);
            backdrop-filter: blur(12px);
            border: 1px solid var(--atm-border);
            border-radius: var(--radius-md);
            padding: 16px 20px;
            display: flex;
            align-items: flex-start;
            gap: 16px;
            transition: all 0.3s ease;
        }

        .timeline-event-card:hover {
            border-color: var(--atm-highlight);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3), 0 0 15px var(--atm-glow);
        }

        .event-icon-box {
            width: 36px;
            height: 36px;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--atm-border);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--atm-highlight);
            flex-shrink: 0;
            transition: color 1.4s ease, border-color 1.4s ease;
        }

        .event-body {
            flex: 1;
        }

        .event-top-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 4px;
        }

        .event-title {
            font-size: 14px;
            font-weight: 600;
            color: var(--text-pure);
        }

        .event-time {
            font-size: 11px;
            color: var(--text-muted);
            font-family: var(--font-mono);
        }

        .event-desc {
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.5;
        }

        .event-tag {
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 2px 8px;
            border-radius: var(--radius-full);
            background: rgba(255, 255, 255, 0.04);
            color: var(--text-muted);
            font-family: var(--font-mono);
        }

        /* ========================================================= */
        /* MODE 3: DOCUMENT KNOWLEDGE SYSTEM                         */
        /* ========================================================= */
        .documents-header-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 24px;
            flex-wrap: wrap;
            gap: 16px;
        }

        .doc-upload-dropzone {
            border: 1px dashed var(--atm-border);
            border-radius: var(--radius-md);
            padding: 32px 20px;
            text-align: center;
            background: var(--atm-surface);
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 24px;
        }

        .doc-upload-dropzone:hover, .doc-upload-dropzone.dragover {
            border-color: var(--atm-highlight);
            background: rgba(255, 255, 255, 0.03);
            box-shadow: 0 0 15px var(--atm-glow);
        }

        .doc-search-bar {
            width: 100%;
            background: var(--atm-surface);
            border: 1px solid var(--atm-border);
            border-radius: var(--radius-full);
            padding: 10px 20px;
            color: var(--text-pure);
            font-size: 13px;
            font-family: var(--font-body);
            margin-bottom: 20px;
            outline: none;
            transition: all 0.3s ease;
        }

        .doc-search-bar:focus {
            border-color: var(--atm-highlight);
            box-shadow: 0 0 15px var(--atm-glow);
        }

        .documents-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 18px;
        }

        .doc-card {
            background: var(--atm-surface);
            backdrop-filter: blur(12px);
            border: 1px solid var(--atm-border);
            border-radius: var(--radius-md);
            padding: 18px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.3s ease;
        }

        .doc-card:hover {
            border-color: var(--atm-highlight);
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4), 0 0 15px var(--atm-glow);
        }

        .doc-card-title {
            font-size: 14px;
            font-weight: 600;
            color: var(--text-pure);
            margin-bottom: 6px;
            word-break: break-word;
        }

        .doc-card-meta {
            font-size: 11px;
            color: var(--text-muted);
            font-family: var(--font-mono);
            margin-bottom: 12px;
            display: flex;
            gap: 12px;
        }

        .doc-preview-snippet {
            font-size: 12px;
            color: var(--text-secondary);
            line-height: 1.5;
            background: rgba(0, 0, 0, 0.3);
            padding: 8px 12px;
            border-radius: var(--radius-sm);
            margin-bottom: 14px;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
            font-family: var(--font-mono);
        }

        .doc-actions {
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-top: 1px solid var(--atm-border);
            padding-top: 10px;
        }

        /* ========================================================= */
        /* MODE 4: RESEARCH CONSTELLATION & NUMBERED PAPERS          */
        /* ========================================================= */
        .constellation-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .constellation-node {
            background: var(--atm-surface);
            backdrop-filter: blur(12px);
            border: 1px solid var(--atm-border);
            border-radius: var(--radius-md);
            padding: 20px;
            transition: all 0.3s var(--ease-organic);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: relative;
        }

        .constellation-node:hover {
            border-color: var(--atm-highlight);
            transform: translateY(-3px);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4), 0 0 20px var(--atm-glow);
        }

        .node-ordinal-badge {
            position: absolute;
            top: 16px;
            right: 16px;
            font-size: 11px;
            font-weight: 700;
            color: var(--atm-highlight);
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--atm-border);
            border-radius: var(--radius-full);
            padding: 2px 8px;
            font-family: var(--font-mono);
        }

        .node-title {
            font-size: 14px;
            font-weight: 600;
            color: var(--text-pure);
            margin-bottom: 8px;
            line-height: 1.4;
            padding-right: 32px;
        }

        .node-meta {
            font-size: 11px;
            color: var(--text-muted);
            margin-bottom: 12px;
            display: flex;
            gap: 10px;
            font-family: var(--font-mono);
        }

        .node-abstract {
            font-size: 12px;
            color: var(--text-secondary);
            line-height: 1.6;
            margin-bottom: 16px;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .node-actions {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
            border-top: 1px solid var(--atm-border);
            padding-top: 12px;
        }

        /* ========================================================= */
        /* MODE 5: ECOSYSTEM & GOOGLE WORKSPACE OAUTH                */
        /* ========================================================= */
        .ecosystem-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .eco-card {
            background: var(--atm-surface);
            backdrop-filter: blur(12px);
            border: 1px solid var(--atm-border);
            border-radius: var(--radius-md);
            padding: 20px;
            transition: all 0.3s ease;
        }

        .btn-google-connect {
            background: var(--atm-surface-elevated);
            color: var(--text-pure);
            border: 1px solid var(--atm-border);
            border-radius: var(--radius-full);
            padding: 8px 18px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
        }

        .btn-google-connect:hover {
            border-color: var(--atm-highlight);
            box-shadow: 0 0 15px var(--atm-glow);
        }

        /* Modal Overlay for Level 3 Structured Breakdown & Custom Atmosphere */
        .eva-modal-overlay {
            position: fixed;
            inset: 0;
            background: rgba(12, 8, 5, 0.85);
            backdrop-filter: blur(12px);
            z-index: 100;
            display: none;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }

        .eva-modal-overlay.active {
            display: flex;
        }

        .eva-modal-box {
            background: var(--atm-surface);
            border: 1px solid var(--atm-border);
            border-radius: var(--radius-md);
            max-width: 700px;
            width: 100%;
            max-height: 85vh;
            display: flex;
            flex-direction: column;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.7), 0 0 30px var(--atm-glow);
            overflow: hidden;
            animation: fadeInLayer 0.3s ease;
        }

        .modal-header {
            padding: 16px 24px;
            border-bottom: 1px solid var(--atm-border);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .modal-body {
            padding: 24px;
            overflow-y: auto;
            color: var(--text-primary);
            font-size: 13px;
            line-height: 1.7;
        }

        .modal-body pre {
            background: rgba(0, 0, 0, 0.4);
            padding: 16px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--atm-border);
            overflow-x: auto;
            font-family: var(--font-mono);
            font-size: 12px;
            color: var(--text-highlight);
            white-space: pre-wrap;
        }

        /* Command Instrument Surface */
        .command-surface {
            position: fixed;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%);
            width: min(720px, calc(100% - 48px));
            background: var(--atm-surface);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--atm-border);
            border-radius: var(--radius-full);
            padding: 6px 8px 6px 20px;
            display: flex;
            align-items: center;
            gap: 12px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6), 0 0 25px var(--atm-glow);
            z-index: 50;
            transition: all 0.4s var(--ease-organic);
        }

        .command-surface:focus-within {
            border-color: var(--atm-highlight);
            box-shadow: 0 20px 45px rgba(0, 0, 0, 0.7), 0 0 35px var(--atm-glow);
        }

        .command-input {
            flex: 1;
            background: transparent;
            border: none;
            outline: none;
            color: var(--text-pure);
            font-size: 14px;
            font-family: var(--font-body);
        }

        .command-actions {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .action-btn {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--atm-border);
            color: var(--text-primary);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .action-btn:hover {
            background: rgba(255, 255, 255, 0.08);
            color: var(--text-pure);
            border-color: var(--atm-highlight);
        }

        .action-btn.primary {
            background: var(--atm-highlight);
            border-color: var(--atm-highlight);
            color: var(--eva-void);
            font-weight: 600;
        }

        .action-btn.active-mic {
            background: var(--eva-crimson);
            border-color: var(--eva-crimson);
            color: white;
            animation: pulseMic 1.2s ease-in-out infinite;
        }

        @keyframes pulseMic {
            0%, 100% { transform: scale(1); box-shadow: 0 0 10px var(--eva-crimson); }
            50% { transform: scale(1.1); box-shadow: 0 0 20px var(--eva-crimson); }
        }

        .btn-link {
            font-size: 12px;
            color: var(--atm-highlight);
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            cursor: pointer;
            background: none;
            border: none;
            transition: opacity 0.2s ease;
        }

        .btn-link:hover {
            opacity: 0.8;
            text-decoration: underline;
        }

        .btn-danger {
            color: var(--eva-mauve);
        }

        .btn-danger:hover {
            color: var(--eva-crimson);
        }

        @media (max-width: 900px) {
            .eva-header { padding: 0 16px; gap: 8px; }
            .eva-atmosphere-switcher { display: none; }
            .spatial-viewport { padding: 74px 16px 120px 16px; }
            .command-surface { width: calc(100% - 24px); bottom: 16px; }
        }
    </style>
</head>
<body>
    <canvas id="living-canvas"></canvas>

    <!-- Top Navigation Realm & Atmosphere System -->
    <header class="eva-header">
        <div class="eva-brand" onclick="setMode('presence')">
            <div class="eva-symbol" id="eva-status-symbol"></div>
            <div class="eva-title">EVA</div>
            <div class="eva-presence-badge" id="eva-atmosphere-badge" title="Active Atmosphere Tone">GROUNDED</div>
        </div>

        <!-- Shared Atmosphere Tone Switcher -->
        <div class="eva-atmosphere-switcher" id="eva-atmosphere-switcher">
            <button class="atm-pill active" id="atm-GROUNDED" onclick="AtmosphereController.setAtmosphere('GROUNDED')" title="Grounded — calm / grounded / stable">
                <span class="atm-dot" style="background:#6D6333;"></span>
                <span>Grounded</span>
            </button>
            <button class="atm-pill" id="atm-FOCUSED" onclick="AtmosphereController.setAtmosphere('FOCUSED')" title="Focused — clarity / concentration / precision">
                <span class="atm-dot" style="background:#484428;"></span>
                <span>Focused</span>
            </button>
            <button class="atm-pill" id="atm-CREATIVE" onclick="AtmosphereController.setAtmosphere('CREATIVE')" title="Creative — creative / intimate / expressive">
                <span class="atm-dot" style="background:#510A16;"></span>
                <span>Creative</span>
            </button>
            <button class="atm-pill" id="atm-CURIOUS" onclick="AtmosphereController.setAtmosphere('CURIOUS')" title="Curious — discovery / exploration / curiosity">
                <span class="atm-dot" style="background:#703912;"></span>
                <span>Curious</span>
            </button>
            <button class="atm-pill" id="atm-REFLECTIVE" onclick="AtmosphereController.setAtmosphere('REFLECTIVE')" title="Reflective — quiet / contemplative / deep">
                <span class="atm-dot" style="background:#7F582D;"></span>
                <span>Reflective</span>
            </button>
            <button class="atm-pill" id="atm-ENERGETIC" onclick="AtmosphereController.setAtmosphere('ENERGETIC')" title="Energetic — momentum / action / vitality">
                <span class="atm-dot" style="background:#B1650E;"></span>
                <span>Energetic</span>
            </button>
            <button class="atm-pill" id="atm-NIGHT" onclick="AtmosphereController.setAtmosphere('NIGHT')" title="Night — mysterious / quiet / expansive">
                <span class="atm-dot" style="background:#190903;"></span>
                <span>Night</span>
            </button>
            <button class="atm-pill" id="atm-CUSTOM" onclick="openCustomAtmosphereModal()" title="Custom — user defined adaptive atmosphere">
                <span class="atm-dot" style="background:linear-gradient(135deg, #B49E45, #510A16);"></span>
                <span>Custom</span>
            </button>
        </div>

        <nav class="eva-nav-modes">
            <button class="nav-mode-btn active" id="mode-presence" onclick="setMode('presence')">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="3"></circle></svg>
                Presence
            </button>
            <button class="nav-mode-btn" id="mode-activity" onclick="setMode('activity')">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
                Activity
            </button>
            <button class="nav-mode-btn" id="mode-documents" onclick="setMode('documents')">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
                Documents
            </button>
            <button class="nav-mode-btn" id="mode-research" onclick="setMode('research')">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                Research
            </button>
            <button class="nav-mode-btn" id="mode-ecosystem" onclick="setMode('ecosystem')">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line></svg>
                Ecosystem
            </button>
        </nav>

        <div class="header-meta">
            <div class="status-dot" id="header-status-dot"></div>
            <span id="header-device-label">Companion Synced</span>
        </div>
    </header>

    <!-- Spatial Main Viewport -->
    <main class="spatial-viewport">
        
        <!-- MODE 1: LIVING PRESENCE (Ambient Living Atmosphere) -->
        <section class="spatial-panel active" id="panel-presence">
            <div class="presence-container">
                <div class="core-presence-orb" id="presence-orb" data-state="AWAITING" onclick="toggleVoiceActivation()">
                    <div class="orb-halo" id="orb-halo"></div>
                    <div class="orb-ring" id="orb-ring"></div>
                    <div class="orb-center" id="orb-center"></div>
                </div>
                <div class="presence-state-text" id="presence-state-text">Awaiting Voice or Text Query</div>
                <div class="waveform-strip" id="waveform-strip">
                    <div class="waveform-bar" style="height: 6px;"></div>
                    <div class="waveform-bar" style="height: 14px;"></div>
                    <div class="waveform-bar" style="height: 20px;"></div>
                    <div class="waveform-bar" style="height: 12px;"></div>
                    <div class="waveform-bar" style="height: 18px;"></div>
                    <div class="waveform-bar" style="height: 8px;"></div>
                    <div class="waveform-bar" style="height: 15px;"></div>
                </div>
            </div>

            <!-- Single Focused Active Presence Thought Layer -->
            <div class="active-focus-container">
                <div class="active-focus-card" id="active-focus-card">
                    <div class="focus-header">
                        <span id="focus-source-label">EVA Ambient Intelligence</span>
                        <span id="focus-time-label">Active Atmosphere</span>
                    </div>
                    <div class="focus-text" id="focus-text">What shall we explore, analyze, or synthesize together?</div>
                    <div class="focus-footer">
                        <span style="font-size: 11px; color: var(--text-muted); font-family: var(--font-mono);" id="focus-latency-label">Zero Hallucination Verified</span>
                        <button class="btn-link" onclick="setMode('activity')">View Activity Timeline &rarr;</button>
                    </div>
                </div>

                <div class="proactive-chips">
                    <span class="meta-chip" onclick="quickCommand('Research latest smart glasses low latency papers')">Research Smart Glasses</span>
                    <span class="meta-chip" onclick="quickCommand('Check my upcoming calendar events')">Calendar Agenda</span>
                    <span class="meta-chip" onclick="setMode('documents')">Knowledge Documents</span>
                    <span class="meta-chip" onclick="quickCommand('Who texted me recently?')">Recent Messages</span>
                </div>
            </div>
        </section>

        <!-- MODE 2: ACTIVITY TIMELINE & OPERATIONAL SESSIONS -->
        <section class="spatial-panel" id="panel-activity">
            <div class="activity-header-bar">
                <div class="activity-title-group">
                    <h2>Operational Activity Timeline</h2>
                    <p>Chronological record of active reasoning, paper discoveries, document indexing, and companion telemetry</p>
                </div>
                <div class="timeline-filter-pills">
                    <button class="filter-pill active" onclick="filterActivity('all', this)">All Events</button>
                    <button class="filter-pill" onclick="filterActivity('RESEARCH', this)">Research</button>
                    <button class="filter-pill" onclick="filterActivity('DOCUMENT', this)">Documents</button>
                    <button class="filter-pill" onclick="filterActivity('GOOGLE', this)">Google</button>
                    <button class="filter-pill" onclick="filterActivity('DEVICE', this)">Hardware</button>
                </div>
            </div>

            <!-- Active Session Summary Card -->
            <div class="sessions-summary-card" id="sessions-summary-card">
                <div>
                    <div class="session-badge-active">
                        <span class="status-dot"></span>
                        <span id="current-session-title">Active Operational Session</span>
                    </div>
                    <div style="font-size: 13px; color: var(--text-primary); margin-top: 4px;" id="current-session-duration">
                        02:00 – Present • Active
                    </div>
                </div>
                <div style="font-size: 11px; color: var(--text-muted); font-family: var(--font-mono);" id="current-session-count">
                    Synchronized
                </div>
            </div>

            <!-- Activity Stream -->
            <div class="timeline-stream" id="activity-stream-container">
                <div style="text-align: center; padding: 40px; color: var(--text-muted);">
                    Loading operational events...
                </div>
            </div>
        </section>

        <!-- MODE 3: DOCUMENT KNOWLEDGE SYSTEM -->
        <section class="spatial-panel" id="panel-documents">
            <div class="documents-header-bar">
                <div>
                    <h2 style="font-family: var(--font-display); font-size: 20px; letter-spacing: 2px; color: var(--text-pure); margin-bottom: 4px;">Knowledge Documents</h2>
                    <p style="font-size: 13px; color: var(--text-secondary);">Uploaded files are automatically indexed for full-text semantic retrieval and EVA reasoning</p>
                </div>
                <button class="action-btn primary" style="border-radius: var(--radius-full); width: auto; padding: 0 16px; height: 34px; font-size: 12px; font-weight: 600;" onclick="document.getElementById('doc-file-input').click()">
                    + Upload File
                </button>
                <input type="file" id="doc-file-input" style="display: none;" onchange="handleFileSelected(event)" accept=".pdf,.docx,.txt,.md,.csv" />
            </div>

            <!-- Drag & Drop Zone -->
            <div class="doc-upload-dropzone" id="drop-zone" onclick="document.getElementById('doc-file-input').click()" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)" ondrop="handleFileDrop(event)">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: var(--atm-highlight); margin-bottom: 8px;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
                <div style="font-size: 14px; font-weight: 600; color: var(--text-pure); margin-bottom: 4px;">Drag &amp; drop PDF, DOCX, TXT, MD, or CSV here</div>
                <div style="font-size: 12px; color: var(--text-muted);">Up to 20MB per document with automatic text extraction</div>
            </div>

            <input type="text" class="doc-search-bar" id="doc-search-bar" placeholder="Search indexed documents by filename or extracted text content..." oninput="handleDocSearch(this.value)" />

            <div class="documents-grid" id="documents-container">
                <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-muted);">
                    Loading indexed documents...
                </div>
            </div>
        </section>

        <!-- MODE 4: RESEARCH CONSTELLATION & NUMBERED PAPERS -->
        <section class="spatial-panel" id="panel-research">
            <div style="text-align: center; margin-bottom: 24px;">
                <h2 style="font-family: var(--font-display); font-size: 20px; letter-spacing: 2px; color: var(--text-pure); margin-bottom: 8px;">Academic Research Constellation</h2>
                <p style="font-size: 13px; color: var(--text-secondary);">Querying arXiv, OpenAlex, Semantic Scholar, and CrossRef with Zero Hallucination verification</p>
            </div>
            <div class="constellation-grid" id="research-nodes-container">
                <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-muted);">
                    Type a research query in the command field below to populate academic papers.
                </div>
            </div>
        </section>

        <!-- MODE 5: ECOSYSTEM & GOOGLE WORKSPACE OAUTH -->
        <section class="spatial-panel" id="panel-ecosystem">
            <div style="text-align: center; margin-bottom: 24px;">
                <h2 style="font-family: var(--font-display); font-size: 20px; letter-spacing: 2px; color: var(--text-pure); margin-bottom: 8px;">Ecosystem Topology &amp; Integrations</h2>
                <p style="font-size: 13px; color: var(--text-secondary);">Live authentication status, automation providers, and hardware telemetry</p>
            </div>

            <div class="ecosystem-grid" id="integrations-health-container">
                <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-muted);">
                    Loading integration topology...
                </div>
            </div>
        </section>

    </main>

    <!-- Modal for Structured Breakdown, Previews & Custom Atmosphere -->
    <div class="eva-modal-overlay" id="eva-modal-overlay" onclick="if(event.target===this) closeModal()">
        <div class="eva-modal-box">
            <div class="modal-header">
                <span style="font-weight: 600; font-size: 15px; color: var(--text-pure);" id="modal-title">Document Preview</span>
                <button class="action-btn" onclick="closeModal()" style="width: 28px; height: 28px;">&times;</button>
            </div>
            <div class="modal-body" id="modal-body">
                <!-- Injected Modal Content -->
            </div>
        </div>
    </div>

    <!-- Command Instrument Surface -->
    <div class="command-surface">
        <input 
            type="text" 
            class="command-input" 
            id="command-input" 
            placeholder="Speak to EVA or enter a query..." 
            autocomplete="off"
            onkeydown="if(event.key==='Enter') executeCommand();"
        />
        <div class="command-actions">
            <button class="action-btn" id="mic-action-btn" title="Voice Input" onclick="toggleVoiceActivation()">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                    <line x1="12" y1="19" x2="12" y2="22"></line>
                </svg>
            </button>
            <button class="action-btn primary" id="send-action-btn" title="Execute" onclick="executeCommand()">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="22" y1="2" x2="11" y2="13"></line>
                    <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                </svg>
            </button>
        </div>
    </div>

    <!-- Living Environment & Atmosphere Engine Logic -->
    <script>
        // -------------------------------------------------------------
        // 1. ATMOSPHERE ENGINE & TONE SHIFTING CONTROLLER
        // -------------------------------------------------------------
        class AtmosphereControllerClass {
            constructor() {
                this.currentMode = "GROUNDED";
                this.presets = {
                    GROUNDED: {
                        name: "Grounded",
                        emotion: "calm / grounded / stable",
                        foundation: "#0C0C08",
                        nightBase: "#161411",
                        accent: "#6D6333",
                        highlight: "#B49E45",
                        surface: "rgba(22, 20, 15, 0.72)",
                        border: "rgba(109, 99, 51, 0.35)",
                        glowOpacity: 0.22,
                        particleDensity: 20,
                        motionScale: 0.85,
                        transitionMs: 1400,
                        particleHues: ["#6D6333", "#B49E45", "#484428"]
                    },
                    FOCUSED: {
                        name: "Focused",
                        emotion: "clarity / concentration / precision",
                        foundation: "#161411",
                        nightBase: "#190903",
                        accent: "#484428",
                        highlight: "#D3A95B",
                        surface: "rgba(28, 25, 21, 0.75)",
                        border: "rgba(211, 169, 91, 0.30)",
                        glowOpacity: 0.25,
                        particleDensity: 18,
                        motionScale: 0.80,
                        transitionMs: 1200,
                        particleHues: ["#484428", "#D3A95B", "#848157"]
                    },
                    CREATIVE: {
                        name: "Creative",
                        emotion: "creative / intimate / expressive",
                        foundation: "#190903",
                        nightBase: "#2B221E",
                        accent: "#510A16",
                        highlight: "#B57B88",
                        surface: "rgba(33, 16, 20, 0.75)",
                        border: "rgba(181, 123, 136, 0.35)",
                        glowOpacity: 0.32,
                        particleDensity: 28,
                        motionScale: 1.15,
                        transitionMs: 1600,
                        particleHues: ["#510A16", "#932D44", "#B57B88", "#A7788E"]
                    },
                    CURIOUS: {
                        name: "Curious",
                        emotion: "discovery / exploration / curiosity",
                        foundation: "#0C0805",
                        nightBase: "#161411",
                        accent: "#703912",
                        highlight: "#D3A95B",
                        surface: "rgba(26, 17, 12, 0.75)",
                        border: "rgba(211, 169, 91, 0.35)",
                        glowOpacity: 0.28,
                        particleDensity: 24,
                        motionScale: 1.00,
                        transitionMs: 1400,
                        particleHues: ["#703912", "#D3A95B", "#B1650E", "#552804"]
                    },
                    REFLECTIVE: {
                        name: "Reflective",
                        emotion: "quiet / contemplative / deep",
                        foundation: "#161411",
                        nightBase: "#0C0805",
                        accent: "#7F582D",
                        highlight: "#ECDBA1",
                        surface: "rgba(27, 23, 19, 0.72)",
                        border: "rgba(236, 219, 161, 0.28)",
                        glowOpacity: 0.20,
                        particleDensity: 16,
                        motionScale: 0.75,
                        transitionMs: 1800,
                        particleHues: ["#7F582D", "#ECDBA1", "#552804", "#F8F0E2"]
                    },
                    ENERGETIC: {
                        name: "Energetic",
                        emotion: "momentum / action / vitality",
                        foundation: "#301306",
                        nightBase: "#190903",
                        accent: "#B1650E",
                        highlight: "#ECDBA1",
                        surface: "rgba(48, 22, 10, 0.78)",
                        border: "rgba(236, 219, 161, 0.45)",
                        glowOpacity: 0.38,
                        particleDensity: 32,
                        motionScale: 1.35,
                        transitionMs: 1100,
                        particleHues: ["#B1650E", "#ECDBA1", "#703912", "#D3A95B"]
                    },
                    NIGHT: {
                        name: "Night",
                        emotion: "mysterious / quiet / expansive",
                        foundation: "#0C0805",
                        nightBase: "#161411",
                        accent: "#190903",
                        highlight: "#D3A95B",
                        surface: "rgba(19, 15, 12, 0.80)",
                        border: "rgba(211, 169, 91, 0.22)",
                        glowOpacity: 0.18,
                        particleDensity: 14,
                        motionScale: 0.65,
                        transitionMs: 1800,
                        particleHues: ["#190903", "#D3A95B", "#2B221E"]
                    },
                    CUSTOM: {
                        name: "Custom",
                        emotion: "adaptive / personal resonance",
                        foundation: "#0C0805",
                        nightBase: "#161411",
                        accent: "#703912",
                        highlight: "#D3A95B",
                        surface: "rgba(24, 18, 14, 0.75)",
                        border: "rgba(211, 169, 91, 0.30)",
                        glowOpacity: 0.25,
                        particleDensity: 22,
                        motionScale: 1.00,
                        transitionMs: 1400,
                        particleHues: ["#703912", "#D3A95B"]
                    }
                };
            }

            setAtmosphere(mode, customConfig = null) {
                if (!this.presets[mode] && mode !== "CUSTOM") return;
                this.currentMode = mode;
                const config = customConfig || this.presets[mode];

                // 1. Update CSS Variables smoothly
                const root = document.documentElement;
                root.style.setProperty('--atm-foundation', config.foundation);
                root.style.setProperty('--atm-night-base', config.nightBase || config.foundation);
                root.style.setProperty('--atm-accent', config.accent);
                root.style.setProperty('--atm-highlight', config.highlight);
                root.style.setProperty('--atm-surface', config.surface);
                root.style.setProperty('--atm-border', config.border);
                root.style.setProperty('--atm-glow', `${config.highlight}33`);
                root.style.setProperty('--atm-glow-opacity', config.glowOpacity);
                root.style.setProperty('--atm-motion-scale', config.motionScale);

                // 2. Update UI Pill states
                document.querySelectorAll('.atm-pill').forEach(pill => pill.classList.remove('active'));
                const activePill = document.getElementById(`atm-${mode}`);
                if (activePill) activePill.classList.add('active');

                // 3. Update Badge
                const badge = document.getElementById('eva-atmosphere-badge');
                if (badge) {
                    badge.innerText = config.name.toUpperCase();
                    badge.title = `Atmosphere: ${config.emotion}`;
                }

                // 4. Update Particle Engine Palette
                if (typeof updateLivingCanvasAtmosphere === 'function') {
                    updateLivingCanvasAtmosphere(config);
                }

                // 5. Update Orb State appearance
                if (typeof updatePresenceOrbAtmosphere === 'function') {
                    updatePresenceOrbAtmosphere(config);
                }

                // 6. Persist locally
                localStorage.setItem('eva_atmosphere_mode', mode);
                if (customConfig) {
                    localStorage.setItem('eva_atmosphere_custom', JSON.stringify(customConfig));
                }

                // 7. Sync with backend asynchronously
                this.syncToBackend(mode, customConfig);
            }

            async syncToBackend(mode, customConfig) {
                try {
                    if (mode === "CUSTOM" && customConfig) {
                        await fetch('/api/v1/atmosphere/custom', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(customConfig)
                        });
                    } else {
                        await fetch('/api/v1/atmosphere/set', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ mode: mode })
                        });
                    }
                } catch (e) {
                    console.debug("Atmosphere backend sync notice:", e);
                }
            }

            init() {
                const saved = localStorage.getItem('eva_atmosphere_mode') || 'GROUNDED';
                if (saved === 'CUSTOM') {
                    try {
                        const custom = JSON.parse(localStorage.getItem('eva_atmosphere_custom') || '{}');
                        this.setAtmosphere('CUSTOM', custom);
                        return;
                    } catch (e) {}
                }
                this.setAtmosphere(saved);
            }
        }
        const AtmosphereController = new AtmosphereControllerClass();

        // -------------------------------------------------------------
        // 2. LIVING CANVAS PARTICLE & COLOR TEMPERATURE ENGINE
        // -------------------------------------------------------------
        const canvas = document.getElementById('living-canvas');
        const ctx = canvas.getContext('2d');
        let width, height;
        let particles = [];
        let currentAtmosphereHues = ["#6D6333", "#B49E45", "#484428"];
        let currentMotionScale = 0.85;

        function resizeCanvas() {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        class AtmosphericParticle {
            constructor() {
                this.reset();
            }
            reset() {
                this.x = Math.random() * width;
                this.y = Math.random() * height;
                this.size = Math.random() * 1.6 + 0.3;
                this.vx = (Math.random() - 0.5) * 0.20 * currentMotionScale;
                this.vy = (Math.random() - 0.5) * 0.20 * currentMotionScale;
                this.alpha = Math.random() * 0.35 + 0.08;
                this.hex = currentAtmosphereHues[Math.floor(Math.random() * currentAtmosphereHues.length)];
            }
            update() {
                this.x += this.vx * currentMotionScale;
                this.y += this.vy * currentMotionScale;
                if (this.x < 0 || this.x > width || this.y < 0 || this.y > height) {
                    this.reset();
                }
            }
            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fillStyle = this.hex;
                ctx.globalAlpha = this.alpha;
                ctx.fill();
                ctx.globalAlpha = 1.0;
            }
        }

        function initParticles(density = 24) {
            particles = [];
            for (let i = 0; i < density; i++) {
                particles.push(new AtmosphericParticle());
            }
        }
        initParticles(24);

        function updateLivingCanvasAtmosphere(config) {
            currentAtmosphereHues = config.particleHues || [config.accent, config.highlight];
            currentMotionScale = config.motionScale || 1.0;
            initParticles(config.particleDensity || 22);
        }

        function renderCanvas() {
            ctx.clearRect(0, 0, width, height);
            particles.forEach(p => {
                p.update();
                p.draw();
            });
            requestAnimationFrame(renderCanvas);
        }
        renderCanvas();

        // -------------------------------------------------------------
        // 3. PRESENCE ORB ATMOSPHERE ADAPTATION
        // -------------------------------------------------------------
        function updatePresenceOrbAtmosphere(config) {
            const orbCenter = document.getElementById('orb-center');
            const orbHalo = document.getElementById('orb-halo');
            if (orbCenter && currentEvaState === "AWAITING") {
                orbCenter.style.background = `radial-gradient(circle at 35% 35%, ${config.highlight} 0%, ${config.accent} 45%, ${config.foundation} 90%)`;
                orbCenter.style.boxShadow = `0 0 32px ${config.highlight}33, inset 0 0 18px rgba(255, 255, 255, 0.15)`;
            }
            if (orbHalo) {
                orbHalo.style.background = `radial-gradient(circle, ${config.accent} 0%, transparent 70%)`;
                orbHalo.style.opacity = config.glowOpacity;
            }
        }

        // Custom Atmosphere Modal Builder
        function openCustomAtmosphereModal() {
            document.getElementById('modal-title').innerText = "Configure Custom Atmosphere";
            document.getElementById('modal-body').innerHTML = `
                <div style="display:flex; flex-direction:column; gap:16px;">
                    <p style="font-size:13px; color:var(--text-secondary);">Customize your tone shifting foundation, accent, and highlight palette.</p>
                    <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:12px;">
                        <div>
                            <label style="font-size:11px; font-family:var(--font-mono); color:var(--text-muted); display:block; margin-bottom:6px;">FOUNDATION</label>
                            <input type="color" id="custom-foundation" value="#0C0805" style="width:100%; height:40px; background:transparent; border:1px solid var(--atm-border); border-radius:var(--radius-sm); cursor:pointer;">
                        </div>
                        <div>
                            <label style="font-size:11px; font-family:var(--font-mono); color:var(--text-muted); display:block; margin-bottom:6px;">ACCENT</label>
                            <input type="color" id="custom-accent" value="#703912" style="width:100%; height:40px; background:transparent; border:1px solid var(--atm-border); border-radius:var(--radius-sm); cursor:pointer;">
                        </div>
                        <div>
                            <label style="font-size:11px; font-family:var(--font-mono); color:var(--text-muted); display:block; margin-bottom:6px;">HIGHLIGHT</label>
                            <input type="color" id="custom-highlight" value="#D3A95B" style="width:100%; height:40px; background:transparent; border:1px solid var(--atm-border); border-radius:var(--radius-sm); cursor:pointer;">
                        </div>
                    </div>
                    <div style="display:flex; justify-content:flex-end; gap:10px; margin-top:10px;">
                        <button class="filter-pill" onclick="closeModal()">Cancel</button>
                        <button class="action-btn primary" style="width:auto; padding:0 20px; border-radius:var(--radius-full); font-size:12px;" onclick="applyCustomAtmosphereFromModal()">Apply Tone Shift</button>
                    </div>
                </div>
            `;
            openModal();
        }

        function applyCustomAtmosphereFromModal() {
            const foundation = document.getElementById('custom-foundation').value;
            const accent = document.getElementById('custom-accent').value;
            const highlight = document.getElementById('custom-highlight').value;
            const customConfig = {
                name: "Custom",
                emotion: "adaptive / personal resonance",
                foundation: foundation,
                nightBase: foundation,
                accent: accent,
                highlight: highlight,
                surface: `${foundation}CC`,
                border: `${highlight}4D`,
                glowOpacity: 0.28,
                particleDensity: 22,
                motionScale: 1.0,
                transitionMs: 1400,
                particleHues: [accent, highlight]
            };
            AtmosphereController.setAtmosphere("CUSTOM", customConfig);
            closeModal();
        }

        // -------------------------------------------------------------
        // 4. HARMONIC ACOUSTIC TONE GENERATOR
        // -------------------------------------------------------------
        let audioCtx = null;
        function playHarmonicTone(freq = 432, type = 'sine', duration = 0.3) {
            try {
                if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                if (audioCtx.state === 'suspended') audioCtx.resume();
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = type;
                osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
                gain.gain.setValueAtTime(0.04, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + duration);
            } catch (e) {}
        }

        // -------------------------------------------------------------
        // 5. LIVING ORB STATE & WAVEFORM
        // -------------------------------------------------------------
        const orbEl = document.getElementById('presence-orb');
        const stateTextEl = document.getElementById('presence-state-text');
        const waveformBars = document.querySelectorAll('.waveform-bar');
        let currentEvaState = "AWAITING";

        function setEvaState(state) {
            currentEvaState = state;
            orbEl.setAttribute('data-state', state);
            stateTextEl.innerText = state.replace('_', ' ');

            if (state === "LISTENING") {
                playHarmonicTone(432, 'sine', 0.25);
                animateWaveform(true);
            } else if (state === "THINKING") {
                playHarmonicTone(600, 'sine', 0.15);
                animateWaveform(false);
            } else if (state === "SPEAKING") {
                animateWaveform(true);
            } else {
                animateWaveform(false);
                const currentPreset = AtmosphereController.presets[AtmosphereController.currentMode] || AtmosphereController.presets["GROUNDED"];
                updatePresenceOrbAtmosphere(currentPreset);
            }
        }

        let waveInterval = null;
        function animateWaveform(active) {
            if (active) {
                if (!waveInterval) {
                    waveInterval = setInterval(() => {
                        waveformBars.forEach(b => {
                            const h = Math.floor(Math.random() * 20) + 4;
                            b.style.height = `${h}px`;
                        });
                    }, 100);
                }
            } else {
                clearInterval(waveInterval);
                waveInterval = null;
                waveformBars.forEach(b => b.style.height = `4px`);
            }
        }

        // -------------------------------------------------------------
        // 6. NAVIGATION & SPATIAL PANELS
        // -------------------------------------------------------------
        function setMode(mode) {
            document.querySelectorAll('.nav-mode-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.spatial-panel').forEach(p => p.classList.remove('active'));
            
            const targetBtn = document.getElementById(`mode-${mode}`);
            const targetPanel = document.getElementById(`panel-${mode}`);
            if (targetBtn) targetBtn.classList.add('active');
            if (targetPanel) targetPanel.classList.add('active');

            if (mode === 'activity') loadActivityTimeline();
            if (mode === 'documents') loadDocumentsList();
            if (mode === 'ecosystem') loadIntegrationsHealth();
        }

        function quickCommand(cmd) {
            document.getElementById('command-input').value = cmd;
            executeCommand();
        }

        // -------------------------------------------------------------
        // 7. COMMAND EXECUTION & VOICE WORKFLOW
        // -------------------------------------------------------------
        async function executeCommand() {
            const input = document.getElementById('command-input');
            const query = input.value.trim();
            if (!query) return;

            input.value = "";
            setEvaState("THINKING");

            updatePresenceFocus(query, "Reasoning across connected context...", "Processing", "Just now");

            if (query.toLowerCase().startsWith('/research') || query.toLowerCase().includes('research paper') || query.toLowerCase().includes('arxiv')) {
                const cleanQuery = query.replace('/research', '').trim();
                setMode('research');
                await executeResearch(cleanQuery || query);
                setEvaState("AWAITING");
                return;
            }

            try {
                const res = await fetch('/api/v1/agent/message', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: query,
                        session_id: 'eva_web_session',
                        device_id: 'EVA_Web_Atmosphere',
                        language: 'auto'
                    })
                });
                const data = await res.json();
                const responseText = data.response || "I am listening.";
                const latency = data.metadata?.latency_ms ? `${Math.round(data.metadata.latency_ms)}ms` : 'Instant';
                const provider = data.metadata?.llm_provider || 'Deterministic Local Engine';

                updatePresenceFocus(query, responseText, `Via ${provider} • ${latency}`, "Just now");
                setEvaState("SPEAKING");
                speakResponse(responseText);

                setTimeout(() => {
                    setEvaState("AWAITING");
                }, Math.min(responseText.length * 50, 4000));

            } catch (err) {
                updatePresenceFocus(query, `Error: ${err.message}`, "Network Error", "Just now");
                setEvaState("AWAITING");
            }
        }

        function updatePresenceFocus(query, response, latency, timeStr) {
            document.getElementById('focus-source-label').innerText = `You: "${query}"`;
            document.getElementById('focus-text').innerText = response;
            document.getElementById('focus-latency-label').innerText = latency;
            document.getElementById('focus-time-label').innerText = timeStr;
        }

        function speakResponse(text) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 1.05;
                utterance.pitch = 1.0;
                window.speechSynthesis.speak(utterance);
            }
        }

        function escapeHtml(str) {
            if (!str) return '';
            return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
        }

        // -------------------------------------------------------------
        // 8. VOICE RECOGNITION
        // -------------------------------------------------------------
        let recognition = null;
        let isListening = false;

        function initSpeech() {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (SpeechRecognition) {
                recognition = new SpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;
                
                recognition.onstart = () => {
                    isListening = true;
                    document.getElementById('mic-action-btn').classList.add('active-mic');
                    setEvaState("LISTENING");
                };

                recognition.onresult = (event) => {
                    const transcript = event.results[0][0].transcript;
                    document.getElementById('command-input').value = transcript;
                    executeCommand();
                };

                recognition.onend = () => {
                    isListening = false;
                    document.getElementById('mic-action-btn').classList.remove('active-mic');
                    if (currentEvaState === "LISTENING") setEvaState("AWAITING");
                };
            }
        }
        initSpeech();

        function toggleVoiceActivation() {
            if (!recognition) initSpeech();
            if (recognition) {
                if (isListening) recognition.stop();
                else recognition.start();
            }
        }

        // -------------------------------------------------------------
        // 9. ACTIVITY TIMELINE & SESSIONS
        // -------------------------------------------------------------
        let currentActivityFilter = 'all';

        async function loadActivityTimeline() {
            const stream = document.getElementById('activity-stream-container');
            try {
                const sessRes = await fetch('/api/v1/events/sessions?limit=5');
                const sessData = await sessRes.json();
                if (sessData.sessions && sessData.sessions.length > 0) {
                    const activeSess = sessData.sessions[0];
                    const startT = activeSess.start_time ? activeSess.start_time.substring(11, 16) : '02:00';
                    const durMin = activeSess.active_duration_ms ? `${Math.round(activeSess.active_duration_ms / 60000)} min` : 'Active';
                    document.getElementById('current-session-duration').innerText = `${startT} – Present • ${durMin}`;
                    document.getElementById('current-session-count').innerText = `${activeSess.activity_count || 1} Actions Recorded`;
                }

                let url = '/api/v1/events/timeline?limit=40';
                if (currentActivityFilter !== 'all') {
                    url += `&category=${encodeURIComponent(currentActivityFilter)}`;
                }
                const res = await fetch(url);
                const data = await res.json();
                const events = data.events || [];

                if (events.length === 0) {
                    stream.innerHTML = `<div style="text-align: center; padding: 40px; color: var(--text-muted);">No recorded activity events under this filter.</div>`;
                    return;
                }

                let html = "";
                events.forEach(evt => {
                    const timeFormatted = evt.timestamp ? evt.timestamp.substring(11, 19) : 'Recent';
                    const tagType = evt.type ? evt.type.replace('_', ' ') : 'EVENT';
                    
                    html += `
                        <div class="timeline-event-card">
                            <div class="event-icon-box">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <circle cx="12" cy="12" r="10"></circle>
                                    <polyline points="12 6 12 12 16 14"></polyline>
                                </svg>
                            </div>
                            <div class="event-body">
                                <div class="event-top-row">
                                    <div class="event-title">${escapeHtml(evt.title || evt.type)}</div>
                                    <div style="display:flex; align-items:center; gap:8px;">
                                        <span class="event-tag">${escapeHtml(tagType)}</span>
                                        <span class="event-time">${timeFormatted}</span>
                                    </div>
                                </div>
                                <div class="event-desc">${escapeHtml(evt.description || '')}</div>
                            </div>
                        </div>
                    `;
                });
                stream.innerHTML = html;

            } catch (err) {
                stream.innerHTML = `<div style="text-align: center; padding: 40px; color: var(--eva-crimson);">Error loading activity timeline: ${err.message}</div>`;
            }
        }

        function filterActivity(filter, btn) {
            currentActivityFilter = filter;
            document.querySelectorAll('.timeline-filter-pills .filter-pill').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            loadActivityTimeline();
        }

        // -------------------------------------------------------------
        // 10. DOCUMENT KNOWLEDGE SYSTEM
        // -------------------------------------------------------------
        let currentDocsList = [];

        async function loadDocumentsList(searchQuery = "") {
            const container = document.getElementById('documents-container');
            try {
                let url = searchQuery ? `/api/v1/documents/search?query=${encodeURIComponent(searchQuery)}` : '/api/v1/documents/list';
                const res = await fetch(url);
                const data = await res.json();
                currentDocsList = data.documents || [];

                if (currentDocsList.length === 0) {
                    container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-muted);">No documents indexed. Upload a file above to expand EVA's knowledge.</div>`;
                    return;
                }

                let html = "";
                currentDocsList.forEach(doc => {
                    const sizeKb = doc.size_bytes ? `${Math.round(doc.size_bytes / 1024)} KB` : 'Unknown size';
                    const mime = doc.mime_type ? doc.mime_type.split('/').pop().toUpperCase() : 'DOC';
                    const created = doc.created_at ? doc.created_at.substring(0, 10) : 'Recent';
                    const preview = doc.text_preview || 'Text extracted and indexed into memory.';

                    html += `
                        <div class="doc-card">
                            <div>
                                <div class="doc-card-title">${escapeHtml(doc.filename)}</div>
                                <div class="doc-card-meta">
                                    <span>${mime}</span>
                                    <span>${sizeKb}</span>
                                    <span>${created}</span>
                                </div>
                                <div class="doc-preview-snippet">${escapeHtml(preview)}</div>
                            </div>
                            <div class="doc-actions">
                                <button class="btn-link" onclick="previewDocument('${doc.file_id}')">Preview Text &rarr;</button>
                                <button class="btn-link btn-danger" onclick="deleteDocument('${doc.file_id}')">Delete</button>
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;

            } catch (err) {
                container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--eva-crimson);">Error loading documents: ${err.message}</div>`;
            }
        }

        function handleDocSearch(q) {
            loadDocumentsList(q);
        }

        async function handleFileSelected(event) {
            const file = event.target.files[0];
            if (file) await uploadFile(file);
        }

        function handleDragOver(e) {
            e.preventDefault();
            document.getElementById('drop-zone').classList.add('dragover');
        }

        function handleDragLeave(e) {
            e.preventDefault();
            document.getElementById('drop-zone').classList.remove('dragover');
        }

        async function handleFileDrop(e) {
            e.preventDefault();
            document.getElementById('drop-zone').classList.remove('dragover');
            if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                await uploadFile(e.dataTransfer.files[0]);
            }
        }

        async function uploadFile(file) {
            const formData = new FormData();
            formData.append("file", file);
            formData.append("source", "web_realm");

            const dropZone = document.getElementById('drop-zone');
            const originalContent = dropZone.innerHTML;
            dropZone.innerHTML = `<div style="color: var(--atm-highlight);">Indexing ${escapeHtml(file.name)} and extracting knowledge...</div>`;

            try {
                const res = await fetch('/api/v1/documents/upload', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                if (data.success) {
                    playHarmonicTone(528, 'sine', 0.25);
                    loadDocumentsList();
                } else {
                    alert(`Upload failed: ${data.detail || 'Unknown error'}`);
                }
            } catch (e) {
                alert(`Upload failed: ${e.message}`);
            } finally {
                dropZone.innerHTML = originalContent;
            }
        }

        async function previewDocument(fileId) {
            try {
                const res = await fetch(`/api/v1/documents/${fileId}`);
                const data = await res.json();
                const doc = data.document;
                if (!doc) return;

                document.getElementById('modal-title').innerText = doc.filename;
                document.getElementById('modal-body').innerHTML = `
                    <div style="font-size: 11px; color: var(--text-muted); font-family: var(--font-mono); margin-bottom: 12px;">
                        MIME: ${escapeHtml(doc.mime_type)} • Size: ${Math.round(doc.size_bytes/1024)} KB • Source: ${escapeHtml(doc.source)}
                    </div>
                    <pre>${escapeHtml(doc.extracted_text || 'No extracted text available.')}</pre>
                `;
                openModal();
            } catch (e) {
                alert(`Error loading document preview: ${e.message}`);
            }
        }

        async function deleteDocument(fileId) {
            if (!confirm("Are you sure you want to remove this document from EVA's knowledge index?")) return;
            try {
                const res = await fetch(`/api/v1/documents/${fileId}`, { method: 'DELETE' });
                if (res.ok) {
                    loadDocumentsList();
                }
            } catch (e) {
                alert(`Error deleting document: ${e.message}`);
            }
        }

        // -------------------------------------------------------------
        // 11. RESEARCH CONSTELLATION
        // -------------------------------------------------------------
        let currentResearchPapers = [];

        async function executeResearch(query) {
            const container = document.getElementById('research-nodes-container');
            container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--atm-highlight);">Scanning academic research databases for "${escapeHtml(query)}"...</div>`;

            try {
                const res = await fetch(`/api/v1/research/papers?query=${encodeURIComponent(query)}&max_results=6`);
                const data = await res.json();
                currentResearchPapers = data.papers || [];

                if (currentResearchPapers.length === 0) {
                    container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-muted);">No papers found matching "${escapeHtml(query)}".</div>`;
                    return;
                }

                let html = "";
                currentResearchPapers.forEach((p, idx) => {
                    const ordinal = idx + 1;
                    const authors = Array.isArray(p.authors) ? p.authors.slice(0, 3).join(', ') : (p.authors || 'Researchers');
                    const year = p.publication_year || (p.published_date ? p.published_date.substring(0, 4) : '2024');

                    html += `
                        <div class="constellation-node">
                            <span class="node-ordinal-badge">#${ordinal}</span>
                            <div>
                                <div class="node-title">${escapeHtml(p.title || 'Academic Paper')}</div>
                                <div class="node-meta">
                                    <span>${escapeHtml(authors)}</span>
                                    <span>${year}</span>
                                    <span>${escapeHtml(p.source || 'Verified Academic')}</span>
                                </div>
                                <div class="node-abstract">${escapeHtml(p.abstract || 'Verified academic paper indexed.')}</div>
                            </div>
                            <div class="node-actions">
                                <a href="${p.url || p.pdf_url || '#'}" target="_blank" class="btn-link">DOI / Link &rarr;</a>
                                <div style="display:flex; gap:6px;">
                                    <button class="btn-link" onclick="openLevel3Summary(${idx})">Structured Analysis</button>
                                    <button class="action-btn" style="width:28px; height:28px;" title="Explain Paper" onclick="quickCommand('Explain research paper ${ordinal}: ${escapeHtml(p.title)}')">
                                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polygon points="10 8 16 12 10 16 10 8"></polygon></svg>
                                    </button>
                                </div>
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;
                playHarmonicTone(660, 'sine', 0.2);

            } catch (err) {
                container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--eva-crimson);">Research search error: ${err.message}</div>`;
            }
        }

        async function openLevel3Summary(paperIndex) {
            const paper = currentResearchPapers[paperIndex];
            if (!paper) return;

            document.getElementById('modal-title').innerText = `Level 3 Structured Analysis: ${paper.title}`;
            document.getElementById('modal-body').innerHTML = `<div style="text-align: center; padding: 20px; color: var(--atm-highlight);">Generating Zero-Hallucination Academic Breakdown...</div>`;
            openModal();

            try {
                const res = await fetch('/api/v1/research/summarize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ paper: paper, level: 3 })
                });
                const data = await res.json();
                const result = data.result || {};
                const content = result.formatted_content || data.summary || "Structured summary generated.";

                document.getElementById('modal-body').innerHTML = `
                    <div style="font-size: 11px; color: var(--atm-highlight); font-family: var(--font-mono); margin-bottom: 12px;">
                         Zero Hallucination Verified • Source: ${escapeHtml(result.source_basis || 'Verified Paper Record')}
                    </div>
                    <pre style="white-space: pre-wrap; font-family: var(--font-body); font-size: 13px; line-height: 1.6; color: var(--text-primary);">${escapeHtml(content)}</pre>
                `;
            } catch (e) {
                document.getElementById('modal-body').innerHTML = `<div style="color: var(--eva-crimson);">Error generating structured breakdown: ${e.message}</div>`;
            }
        }

        // -------------------------------------------------------------
        // 12. INTEGRATIONS & GOOGLE OAUTH
        // -------------------------------------------------------------
        async function loadIntegrationsHealth() {
            const container = document.getElementById('integrations-health-container');
            try {
                const res = await fetch('/api/v1/integrations/health');
                const data = await res.json();
                const list = data.integrations || [];

                let html = `
                    <div class="eco-card" style="grid-column: 1/-1;">
                        <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px; margin-bottom:12px;">
                            <div>
                                <h3 style="font-size:15px; font-weight:600; color:var(--text-pure); margin-bottom:4px;">Google Workspace Ecosystem</h3>
                                <p style="font-size:12px; color:var(--text-secondary);">Connect Gmail &amp; Google Calendar for automatic scheduling and email intelligence</p>
                            </div>
                            <button class="btn-google-connect" onclick="connectGoogleAccount()">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#D3A95B"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#6D6333"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" fill="#B1650E"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" fill="#510A16"/></svg>
                                Connect Google Account
                            </button>
                        </div>
                        <div style="font-size:11px; color:var(--text-muted); font-family:var(--font-mono); border-top:1px solid var(--atm-border); padding-top:8px;">
                            Scopes: https://www.googleapis.com/auth/gmail.modify • https://www.googleapis.com/auth/calendar
                        </div>
                    </div>
                `;

                list.forEach(item => {
                    const isConnected = item.status === "CONNECTED";
                    const isAuthReq = item.status === "AUTH_REQUIRED";

                    html += `
                        <div class="eco-card">
                            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:10px;">
                                <div style="font-size:14px; font-weight:600; color:var(--text-pure);">${escapeHtml(item.name)}</div>
                                <div style="display:flex; align-items:center; gap:6px; font-size:11px; color:var(--text-muted); font-family:var(--font-mono);">
                                    <span style="display:inline-block; width:6px; height:6px; border-radius:50%; background:${isConnected ? 'var(--atm-highlight)' : 'var(--eva-mauve)'};"></span>
                                    <span>${item.status}</span>
                                </div>
                            </div>
                            <pre style="background:rgba(0,0,0,0.3); padding:10px; border-radius:var(--radius-sm); font-size:11px; font-family:var(--font-mono); color:var(--text-secondary); max-height:120px; overflow-y:auto;">${escapeHtml(JSON.stringify(item.details || {}, null, 2))}</pre>
                        </div>
                    `;
                });
                container.innerHTML = html;

            } catch (e) {
                container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--eva-crimson);">Could not load integrations health: ${e.message}</div>`;
            }
        }

        function connectGoogleAccount() {
            const width = 600, height = 700;
            const left = (window.innerWidth - width) / 2;
            const top = (window.innerHeight - height) / 2;
            window.open(
                '/api/v1/auth/google/login',
                'GoogleAuthWindow',
                `width=${width},height=${height},top=${top},left=${left},status=no,toolbar=no,menubar=no`
            );
        }

        // Modal Helpers
        function openModal() {
            document.getElementById('eva-modal-overlay').classList.add('active');
        }
        function closeModal() {
            document.getElementById('eva-modal-overlay').classList.remove('active');
        }

        // -------------------------------------------------------------
        // 13. SSE Stream Connection & Atmosphere Sync
        // -------------------------------------------------------------
        function initSSE() {
            try {
                const evtSource = new EventSource('/api/v1/events/stream');
                evtSource.onmessage = function(e) {
                    try {
                        const evt = JSON.parse(e.data);
                        if (evt.type === "VOICE_START" || evt.event === "TALK_START") {
                            setEvaState("LISTENING");
                        } else if (evt.type === "VOICE_END") {
                            setEvaState("THINKING");
                        } else if (evt.type === "DOCUMENT_INGESTED") {
                            loadDocumentsList();
                        } else if (evt.type === "ATMOSPHERE_CHANGED") {
                            if (evt.metadata && evt.metadata.mode) {
                                AtmosphereController.setAtmosphere(evt.metadata.mode);
                            }
                        }
                    } catch (err) {}
                };
            } catch (e) {}
        }

        window.addEventListener('DOMContentLoaded', () => {
            AtmosphereController.init();
            initSSE();
        });
    </script>
</body>
</html>
"""
