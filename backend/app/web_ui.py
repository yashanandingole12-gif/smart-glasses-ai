def get_dashboard_html() -> str:
    """
    Returns EVA: Immersive Nature-First Product Experience & Device Management Console.
    Visual Identity: Ivory (#F7F4EC) + Pure White (#FFFFFF) + Natural Green (#3F6B4F) + Controlled Black (#111311).
    Philosophy: 'THIS IS THE WORLD AS EXPERIENCED WITH EVA.' World First, Interface Second.
    
    Structure:
      - Immersive Environmental Hero (Eye-level Autumn Walkway)
      - World First Philosophy & 5 Core Pillars (Voice, Vision, Context, Memory, Assistance)
      - Environmental Journey (Forest, Campus, City, Night) with Ambient Glass HUD Layers
      - Personal Activity Journal (Chronological Real-Time Timeline)
      - App Configuration & Experience Controls (Voice, Vision, Context, Integrations)
      - Usage & Insights (Clean Green Environmental Metrics)
      - God's Eye Live Transit Intelligence (Traffic, Metro, Trains, Flights)
      - Full-Featured Device Management Console (/console)
    """
    return r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <!-- LARA Smart Glasses Operations Console | ESP32 Smart Glasses & Android Hub | Private Intelligence & Control | Intent Inspector | Desk & Data Analysis | Automations Center | Smart Notifications -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EVA — See More. Live Deeper. | Ambient Spatial Companion</title>
    <script>
        function updateHardwareStatus(d){console.debug("Hardware sync", d);}
        function simulateIncomingSmsPrompt(){console.debug("Simulate SMS");}
        function triggerMultimodalCapture(){console.debug("Multimodal capture");}
    </script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            /* ========================================================= */
            /* EVA DESIGN SYSTEM — IVORY + WHITE + GREEN + BLACK         */
            /* ========================================================= */
            --eva-ivory: #F7F4EC;
            --eva-warm-ivory: #F1EEE4;
            --eva-pure-white: #FFFFFF;
            --eva-soft-white: #FCFBF8;
            --eva-light-stone: #E8E5DC;
            --eva-border: #E2E0D8;
            --eva-border-light: rgba(226, 224, 216, 0.6);

            /* Glassmorphism Tokens */
            --eva-glass-bg: rgba(247, 244, 236, 0.78);
            --eva-glass-white: rgba(255, 255, 255, 0.82);
            --eva-glass-dark: rgba(17, 19, 17, 0.75);
            --eva-glass-border: rgba(255, 255, 255, 0.85);

            /* Green Accent (8-10%) */
            --eva-primary-green: #3F6B4F;
            --eva-deep-green: #294A36;
            --eva-soft-green: #6F9278;
            --eva-pale-green: #DDE9DF;
            --eva-mist-green: #EEF4EF;
            --eva-green-glow: rgba(63, 107, 79, 0.18);

            /* Black & Typography (5% Contrast) */
            --eva-primary-black: #111311;
            --eva-soft-black: #252824;
            --eva-muted-text: #626861;
            --eva-slate: #8C928B;

            /* Status */
            --eva-status-good: #3F6B4F;
            --eva-status-warn: #B46E28;
            --eva-status-alert: #9E3A3A;

            --font-body: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;

            --radius-sm: 8px;
            --radius-md: 14px;
            --radius-lg: 20px;
            --radius-xl: 28px;
            --radius-full: 9999px;

            --shadow-subtle: 0 2px 10px rgba(17, 19, 17, 0.03), 0 1px 3px rgba(17, 19, 17, 0.02);
            --shadow-glass: 0 8px 32px rgba(17, 19, 17, 0.08), 0 2px 8px rgba(17, 19, 17, 0.04);
            --shadow-elevated: 0 16px 40px rgba(17, 19, 17, 0.10);

            --ease-natural: cubic-bezier(0.16, 1, 0.3, 1);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-font-smoothing: antialiased;
        }

        html {
            scroll-behavior: smooth;
        }

        body {
            background-color: var(--eva-ivory);
            color: var(--eva-soft-black);
            font-family: var(--font-body);
            min-height: 100vh;
            overflow-x: hidden;
            display: flex;
            flex-direction: column;
            position: relative;
        }

        /* Top Navigation */
        .eva-nav-header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 70px;
            padding: 0 40px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            z-index: 1000;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--eva-border-light);
            background: rgba(247, 244, 236, 0.85);
            transition: all 0.3s ease;
        }

        .eva-brand {
            display: flex;
            align-items: center;
            gap: 12px;
            cursor: pointer;
            text-decoration: none;
        }

        .eva-brand-title {
            font-size: 21px;
            letter-spacing: 3px;
            color: var(--eva-primary-black);
            font-weight: 700;
        }

        .eva-brand-tag {
            font-size: 11px;
            font-weight: 500;
            color: var(--eva-deep-green);
            background: var(--eva-mist-green);
            border: 1px solid var(--eva-pale-green);
            padding: 2px 9px;
            border-radius: var(--radius-full);
            font-family: var(--font-mono);
        }

        .eva-nav-links {
            display: flex;
            align-items: center;
            gap: 32px;
        }

        .eva-nav-link {
            font-size: 14px;
            font-weight: 500;
            color: var(--eva-muted-text);
            text-decoration: none;
            cursor: pointer;
            transition: color 0.2s ease;
        }

        .eva-nav-link:hover, .eva-nav-link.active {
            color: var(--eva-primary-black);
        }

        .eva-nav-actions {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .btn-console-toggle {
            background: var(--eva-pure-white);
            color: var(--eva-deep-green);
            border: 1px solid var(--eva-border);
            padding: 8px 18px;
            border-radius: var(--radius-full);
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            box-shadow: var(--shadow-subtle);
        }

        .btn-console-toggle:hover {
            background: var(--eva-primary-green);
            color: var(--eva-pure-white);
            border-color: var(--eva-primary-green);
        }

        .btn-primary {
            background: var(--eva-primary-green);
            color: var(--eva-pure-white);
            border: none;
            padding: 12px 26px;
            border-radius: var(--radius-full);
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 4px 14px rgba(63, 107, 79, 0.25);
        }

        .btn-primary:hover {
            background: var(--eva-deep-green);
            transform: translateY(-1px);
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.85);
            color: var(--eva-primary-black);
            border: 1px solid var(--eva-border);
            padding: 12px 24px;
            border-radius: var(--radius-full);
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .btn-secondary:hover {
            background: var(--eva-pure-white);
            border-color: var(--eva-primary-green);
            color: var(--eva-deep-green);
        }

        /* Status Dot */
        .status-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: var(--eva-primary-green);
            display: inline-block;
            vertical-align: middle;
            margin-right: 4px;
        }

        /* ========================================================= */
        /* MAIN CONTAINERS & VIEWS                                   */
        /* ========================================================= */
        .main-container {
            margin-top: 70px;
            flex: 1;
            display: flex;
            flex-direction: column;
        }

        .view-section {
            display: none;
            opacity: 0;
            transition: opacity 0.4s ease;
        }

        .view-section.active {
            display: block;
            opacity: 1;
        }

        /* ========================================================= */
        /* IMMERSIVE NATURE-FIRST HERO (AUTUMN WALK)                */
        /* ========================================================= */
        .nature-hero-section {
            position: relative;
            min-height: 90vh;
            display: flex;
            align-items: center;
            padding: 60px 80px;
            background: url('/static/environments/autumn_walk.jpg') center/cover no-repeat;
            overflow: hidden;
        }

        .nature-hero-overlay {
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, rgba(17, 19, 17, 0.38) 0%, rgba(17, 19, 17, 0.20) 45%, rgba(247, 244, 236, 0.96) 100%);
            pointer-events: none;
        }

        .nature-hero-grid {
            position: relative;
            z-index: 2;
            width: 100%;
            max-width: 1300px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1.15fr 0.85fr;
            gap: 60px;
            align-items: center;
        }

        .hero-text-card {
            background: rgba(247, 244, 236, 0.88);
            border: 1px solid rgba(255, 255, 255, 0.9);
            border-radius: var(--radius-xl);
            padding: 48px 52px;
            backdrop-filter: blur(28px);
            -webkit-backdrop-filter: blur(28px);
            box-shadow: var(--shadow-glass);
            animation: fadeIn 0.8s var(--ease-natural);
        }

        .hero-eyebrow {
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: var(--eva-deep-green);
            margin-bottom: 16px;
            display: inline-block;
            font-family: var(--font-mono);
        }

        .hero-headline {
            font-size: 48px;
            line-height: 1.12;
            font-weight: 700;
            letter-spacing: -1.2px;
            color: var(--eva-primary-black);
            margin-bottom: 20px;
        }

        .hero-subheadline {
            font-size: 16px;
            line-height: 1.65;
            color: var(--eva-soft-black);
            margin-bottom: 34px;
            font-weight: 400;
        }

        .hero-cta-row {
            display: flex;
            align-items: center;
            gap: 16px;
            flex-wrap: wrap;
        }

        /* Ambient Glass HUD Layer (Looking through EVA) */
        .hero-hud-layer {
            display: flex;
            flex-direction: column;
            gap: 16px;
            animation: floatSlow 6s ease-in-out infinite alternate;
        }

        .hud-glass-chip {
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid rgba(255, 255, 255, 0.95);
            border-radius: var(--radius-lg);
            padding: 18px 22px;
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            box-shadow: var(--shadow-glass);
            transition: all 0.3s ease;
        }

        .hud-glass-chip:hover {
            transform: translateX(4px);
            background: rgba(255, 255, 255, 0.94);
        }

        .hud-chip-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 6px;
        }

        .hud-chip-label {
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: var(--eva-muted-text);
            font-family: var(--font-mono);
        }

        .hud-chip-tag {
            font-size: 11px;
            font-weight: 600;
            color: var(--eva-deep-green);
            background: var(--eva-mist-green);
            padding: 2px 8px;
            border-radius: var(--radius-full);
            border: 1px solid var(--eva-pale-green);
        }

        .hud-chip-content {
            font-size: 14px;
            font-weight: 600;
            color: var(--eva-primary-black);
        }

        .hud-chip-sub {
            font-size: 12px;
            color: var(--eva-muted-text);
            margin-top: 3px;
        }

        /* ========================================================= */
        /* PHILOSOPHY & STORY: WORLD FIRST, INTERFACE SECOND        */
        /* ========================================================= */
        .story-section {
            padding: 100px 40px 80px 40px;
            max-width: 1240px;
            margin: 0 auto;
            width: 100%;
        }

        .story-header {
            text-align: center;
            max-width: 780px;
            margin: 0 auto 60px auto;
        }

        .story-eyebrow {
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: var(--eva-primary-green);
            font-family: var(--font-mono);
            margin-bottom: 12px;
            display: inline-block;
        }

        .story-title {
            font-size: 36px;
            font-weight: 700;
            letter-spacing: -0.8px;
            color: var(--eva-primary-black);
            line-height: 1.25;
            margin-bottom: 18px;
        }

        .story-subtitle {
            font-size: 16px;
            line-height: 1.7;
            color: var(--eva-muted-text);
        }

        /* 5 Pillars Grid */
        .pillars-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 24px;
        }

        .pillar-card {
            background: var(--eva-pure-white);
            border: 1px solid var(--eva-border);
            border-radius: var(--radius-lg);
            padding: 32px 26px;
            box-shadow: var(--shadow-subtle);
            transition: all 0.3s var(--ease-natural);
            position: relative;
        }

        .pillar-card:hover {
            transform: translateY(-3px);
            border-color: var(--eva-soft-green);
            box-shadow: var(--shadow-card);
        }

        .pillar-icon-box {
            width: 44px;
            height: 44px;
            border-radius: var(--radius-md);
            background: var(--eva-mist-green);
            color: var(--eva-primary-green);
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 20px;
            border: 1px solid var(--eva-pale-green);
        }

        .pillar-name {
            font-size: 18px;
            font-weight: 700;
            color: var(--eva-primary-black);
            margin-bottom: 10px;
        }

        .pillar-desc {
            font-size: 13px;
            line-height: 1.6;
            color: var(--eva-muted-text);
        }

        /* ========================================================= */
        /* ENVIRONMENTAL TRANSITION BANNERS (IMMERSIVE SECTIONS)    */
        /* ========================================================= */
        .env-banner-section {
            position: relative;
            min-height: 480px;
            margin: 40px 0;
            display: flex;
            align-items: center;
            justify-content: center;
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            padding: 60px 40px;
        }

        .env-banner-overlay {
            position: absolute;
            inset: 0;
            background: rgba(17, 19, 17, 0.28);
        }

        .env-glass-card {
            position: relative;
            z-index: 2;
            max-width: 680px;
            background: rgba(247, 244, 236, 0.88);
            border: 1px solid rgba(255, 255, 255, 0.92);
            border-radius: var(--radius-xl);
            padding: 40px 48px;
            backdrop-filter: blur(28px);
            -webkit-backdrop-filter: blur(28px);
            box-shadow: var(--shadow-glass);
            text-align: center;
        }

        .env-glass-title {
            font-size: 28px;
            font-weight: 700;
            color: var(--eva-primary-black);
            margin-bottom: 12px;
            letter-spacing: -0.5px;
        }

        .env-glass-desc {
            font-size: 15px;
            line-height: 1.65;
            color: var(--eva-soft-black);
            margin-bottom: 20px;
        }

        .env-meta-tags {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            flex-wrap: wrap;
        }

        .env-meta-pill {
            font-size: 12px;
            font-weight: 600;
            color: var(--eva-deep-green);
            background: var(--eva-pure-white);
            border: 1px solid var(--eva-border);
            padding: 5px 14px;
            border-radius: var(--radius-full);
            font-family: var(--font-mono);
        }

        /* ========================================================= */
        /* PERSONAL ACTIVITY JOURNAL SECTION                        */
        /* ========================================================= */
        .journal-section {
            padding: 60px 40px;
            max-width: 1240px;
            margin: 0 auto;
            width: 100%;
        }

        .journal-container {
            background: var(--eva-pure-white);
            border: 1px solid var(--eva-border);
            border-radius: var(--radius-xl);
            padding: 44px;
            box-shadow: var(--shadow-subtle);
        }

        .journal-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            margin-bottom: 32px;
            flex-wrap: wrap;
            gap: 16px;
        }

        .timeline-stream {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .timeline-entry {
            display: flex;
            align-items: flex-start;
            gap: 20px;
            padding: 16px 20px;
            background: var(--eva-soft-white);
            border: 1px solid var(--eva-border-light);
            border-radius: var(--radius-md);
            transition: all 0.2s ease;
        }

        .timeline-entry:hover {
            border-color: var(--eva-pale-green);
            background: var(--eva-mist-green);
        }

        .entry-time {
            font-size: 12px;
            font-family: var(--font-mono);
            font-weight: 600;
            color: var(--eva-deep-green);
            min-width: 60px;
            padding-top: 2px;
        }

        .entry-body {
            flex: 1;
        }

        .entry-title {
            font-size: 14px;
            font-weight: 600;
            color: var(--eva-primary-black);
            margin-bottom: 3px;
        }

        .entry-desc {
            font-size: 12px;
            color: var(--eva-muted-text);
            line-height: 1.5;
        }

        .empty-state-journal {
            text-align: center;
            padding: 40px 20px;
            color: var(--eva-muted-text);
            font-size: 14px;
        }

        /* ========================================================= */
        /* APP CONFIGURATION & SETTINGS MODULES                     */
        /* ========================================================= */
        .config-section {
            padding: 40px 40px 80px 40px;
            max-width: 1240px;
            margin: 0 auto;
            width: 100%;
        }

        .config-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 24px;
        }

        .config-card {
            background: var(--eva-pure-white);
            border: 1px solid var(--eva-border);
            border-radius: var(--radius-lg);
            padding: 28px;
            box-shadow: var(--shadow-subtle);
        }

        .config-card-title {
            font-size: 16px;
            font-weight: 700;
            color: var(--eva-primary-black);
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 18px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--eva-border-light);
        }

        .config-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 0;
            font-size: 13px;
        }

        .config-row:not(:last-child) {
            border-bottom: 1px dashed var(--eva-border-light);
        }

        .config-label {
            color: var(--eva-muted-text);
            font-weight: 500;
        }

        .config-val {
            color: var(--eva-primary-black);
            font-weight: 600;
            font-family: var(--font-mono);
            font-size: 12px;
        }

        /* ========================================================= */
        /* USAGE & INSIGHTS (CLEAN GREEN LIGHT CHARTS)              */
        /* ========================================================= */
        .insights-section {
            padding: 40px 40px 80px 40px;
            max-width: 1240px;
            margin: 0 auto;
            width: 100%;
        }

        .insights-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 28px;
        }

        .insight-chart-card {
            background: var(--eva-pure-white);
            border: 1px solid var(--eva-border);
            border-radius: var(--radius-lg);
            padding: 30px;
            box-shadow: var(--shadow-subtle);
        }

        .chart-bar-canvas {
            height: 160px;
            display: flex;
            align-items: flex-end;
            gap: 12px;
            padding-top: 24px;
            border-bottom: 1px solid var(--eva-border);
        }

        .chart-bar-item {
            flex: 1;
            background: var(--eva-primary-green);
            border-radius: 4px 4px 0 0;
            transition: all 0.3s ease;
            position: relative;
        }

        .chart-bar-item.secondary {
            background: var(--eva-pale-green);
        }

        .chart-bar-item:hover {
            background: var(--eva-deep-green);
        }

        /* ========================================================= */
        /* GOD'S EYE LIVE TRANSIT RADAR                             */
        /* ========================================================= */
        .transit-live-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 20px;
            margin-top: 24px;
        }

        .transit-live-card {
            background: var(--eva-pure-white);
            border: 1px solid var(--eva-border);
            border-radius: var(--radius-md);
            padding: 22px;
            box-shadow: var(--shadow-subtle);
            transition: all 0.2s ease;
        }

        .transit-live-card:hover {
            border-color: var(--eva-primary-green);
            box-shadow: var(--shadow-card);
        }

        .transit-badge {
            font-size: 11px;
            font-weight: 600;
            color: var(--eva-deep-green);
            background: var(--eva-mist-green);
            border: 1px solid var(--eva-pale-green);
            padding: 2px 8px;
            border-radius: var(--radius-full);
            font-family: var(--font-mono);
        }

        /* ========================================================= */
        /* VIEW 2: DEVICE MANAGEMENT CONSOLE (/console)             */
        /* ========================================================= */
        .console-container {
            padding: 40px 60px 120px 60px;
            max-width: 1300px;
            margin: 0 auto;
            width: 100%;
        }

        .console-header-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 32px;
            flex-wrap: wrap;
            gap: 20px;
        }

        .console-title-group h1 {
            font-size: 28px;
            font-weight: 700;
            color: var(--eva-primary-black);
            letter-spacing: -0.5px;
        }

        .console-title-group p {
            font-size: 14px;
            color: var(--eva-muted-text);
            margin-top: 4px;
        }

        .console-status-badge {
            display: flex;
            align-items: center;
            gap: 8px;
            background: var(--eva-pure-white);
            border: 1px solid var(--eva-border);
            padding: 8px 16px;
            border-radius: var(--radius-full);
            font-size: 12px;
            font-weight: 600;
            color: var(--eva-deep-green);
            box-shadow: var(--shadow-subtle);
            font-family: var(--font-mono);
        }

        .overview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }

        .overview-chip-card {
            background: var(--eva-pure-white);
            border: 1px solid var(--eva-border);
            border-radius: var(--radius-md);
            padding: 18px;
            box-shadow: var(--shadow-subtle);
        }

        .overview-chip-label {
            font-size: 11px;
            font-weight: 600;
            color: var(--eva-muted-text);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
            font-family: var(--font-mono);
        }

        .overview-chip-value {
            font-size: 15px;
            font-weight: 700;
            color: var(--eva-primary-black);
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .overview-chip-sub {
            font-size: 11px;
            color: var(--eva-muted-text);
            margin-top: 4px;
        }

        .console-nav-strip {
            display: flex;
            gap: 8px;
            margin-bottom: 24px;
            border-bottom: 1px solid var(--eva-border);
            padding-bottom: 8px;
            overflow-x: auto;
        }

        .console-tab-btn {
            background: transparent;
            border: none;
            padding: 8px 18px;
            font-size: 13px;
            font-weight: 600;
            color: var(--eva-muted-text);
            cursor: pointer;
            border-radius: var(--radius-full);
            transition: all 0.2s ease;
        }

        .console-tab-btn:hover {
            color: var(--eva-primary-black);
            background: var(--eva-warm-ivory);
        }

        .console-tab-btn.active {
            background: var(--eva-primary-green);
            color: var(--eva-pure-white);
        }

        .console-panel {
            display: none;
        }

        .console-panel.active {
            display: block;
        }

        /* Floating Console Voice Bar */
        .console-voice-bar {
            position: fixed;
            bottom: 28px;
            left: 50%;
            transform: translateX(-50%);
            width: 90%;
            max-width: 680px;
            background: rgba(247, 244, 236, 0.94);
            border: 1px solid rgba(255, 255, 255, 0.95);
            border-radius: var(--radius-full);
            padding: 8px 14px;
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: var(--shadow-elevated);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            z-index: 1000;
        }

        .console-input {
            flex: 1;
            background: transparent;
            border: none;
            outline: none;
            padding: 8px 12px;
            font-size: 14px;
            color: var(--eva-primary-black);
            font-family: var(--font-body);
        }

        .btn-mic-action {
            width: 38px;
            height: 38px;
            border-radius: 50%;
            background: var(--eva-mist-green);
            color: var(--eva-primary-green);
            border: 1px solid var(--eva-pale-green);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .btn-mic-action.active {
            background: var(--eva-primary-green);
            color: var(--eva-pure-white);
            animation: pulseGreen 1.5s infinite;
        }

        @keyframes pulseGreen {
            0% { box-shadow: 0 0 0 0 rgba(63, 107, 79, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(63, 107, 79, 0); }
            100% { box-shadow: 0 0 0 0 rgba(63, 107, 79, 0); }
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes floatSlow {
            0% { transform: translateY(0px); }
            100% { transform: translateY(-8px); }
        }

        @media (max-width: 960px) {
            .nature-hero-grid { grid-template-columns: 1fr; gap: 30px; }
            .nature-hero-section { padding: 40px 24px; }
            .hero-text-card { padding: 32px 28px; }
            .hero-headline { font-size: 36px; }
            .insights-grid { grid-template-columns: 1fr; }
            .eva-nav-links { display: none; }
            .eva-nav-header { padding: 0 20px; }
            .console-container { padding: 24px 20px 120px 20px; }
        }
    </style>
</head>
<body>

    <!-- Top Navigation Header -->
    <header class="eva-nav-header">
        <div class="eva-brand" onclick="switchView('product'); scrollToSection('hero-top');">
            <span class="eva-brand-title">EVA</span>
            <span class="eva-brand-tag" id="nav-device-tag">EVA-GLS-01</span>
        </div>

        <nav class="eva-nav-links">
            <a class="eva-nav-link" onclick="switchView('product'); scrollToSection('hero-top');">Experience</a>
            <a class="eva-nav-link" onclick="switchView('product'); scrollToSection('story');">Philosophy</a>
            <a class="eva-nav-link" onclick="switchView('product'); scrollToSection('journal');">Activity</a>
            <a class="eva-nav-link" onclick="switchView('product'); scrollToSection('config');">Configuration</a>
            <a class="eva-nav-link" onclick="switchView('product'); scrollToSection('transit');">God's Eye</a>
            <a class="eva-nav-link" onclick="switchView('console'); setConsoleTab('health');">Console</a>
        </nav>

        <div class="eva-nav-actions">
            <button class="btn-console-toggle" id="btn-view-toggle" onclick="toggleMainView()">
                <span class="status-dot"></span>
                <span id="btn-toggle-label">Device Console</span>
            </button>
        </div>
    </header>

    <!-- Main Dynamic Content Container -->
    <main class="main-container">

        <!-- ========================================================= -->
        <!-- VIEW 1: IMMERSIVE NATURE-FIRST PRODUCT EXPERIENCE         -->
        <!-- ========================================================= -->
        <section class="view-section active" id="view-product">
            
            <!-- Hero: The World Through EVA (Autumn Walkway) -->
            <div class="nature-hero-section" id="hero-top">
                <div class="nature-hero-overlay"></div>
                <div class="nature-hero-grid">
                    
                    <!-- Left: Editorial Typography Card -->
                    <div class="hero-text-card">
                        <span class="hero-eyebrow">Ambient Spatial Intelligence</span>
                        <h1 class="hero-headline">SEE MORE.<br>LIVE DEEPER.</h1>
                        <p class="hero-subheadline">An AI companion designed to understand your world and stay out of your way. Ambient intelligence for a more present life — physical surroundings first, intelligence second.</p>
                        <div class="hero-cta-row">
                            <button class="btn-primary" onclick="scrollToSection('story')">Explore the Experience</button>
                            <button class="btn-secondary" onclick="switchView('console')">Device Console</button>
                        </div>
                    </div>

                    <!-- Right: Floating Ambient Glass HUD Layer -->
                    <div class="hero-hud-layer">
                        <div class="hud-glass-chip">
                            <div class="hud-chip-top">
                                <span class="hud-chip-label">Acoustic Sense</span>
                                <span class="hud-chip-tag"><span class="status-dot"></span> Active</span>
                            </div>
                            <div class="hud-chip-content">Full-Duplex VAD &amp; Spatial Voice</div>
                            <div class="hud-chip-sub">Ambient noise floor: 32 dB (Whisper Silent)</div>
                        </div>

                        <div class="hud-glass-chip">
                            <div class="hud-chip-top">
                                <span class="hud-chip-label">Live Transit Radar</span>
                                <span class="hud-chip-tag">God's Eye</span>
                            </div>
                            <div class="hud-chip-content">Indiranagar Metro • Platform 1 in 3m</div>
                            <div class="hud-chip-sub">Outer Ring Road traffic: Moderate (+4m delay)</div>
                        </div>

                        <div class="hud-glass-chip">
                            <div class="hud-chip-top">
                                <span class="hud-chip-label">Daily Context</span>
                                <span class="hud-chip-tag">Synced</span>
                            </div>
                            <div class="hud-chip-content">2 Messages Summarized • Next Sync 14:30</div>
                            <div class="hud-chip-sub">Local SLM active • Zero cloud pixel storage</div>
                        </div>
                    </div>

                </div>
            </div>

            <!-- Product Philosophy & 5 Core Pillars -->
            <div class="story-section" id="story">
                <div class="story-header">
                    <span class="story-eyebrow">World First. Interface Second.</span>
                    <h2 class="story-title">Technology that disappears into everyday life.</h2>
                    <p class="story-subtitle">EVA does not ask you to live inside a screen. It weaves intelligence into your natural gaze and hearing, preserving human presence and authentic focus.</p>
                </div>

                <div class="pillars-grid">
                    <div class="pillar-card">
                        <div class="pillar-icon-box">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="22"/></svg>
                        </div>
                        <h3 class="pillar-name">Voice</h3>
                        <p class="pillar-desc">Full-duplex natural audio with adaptive noise-floor VAD. EVA speaks in short, confident wearable sentences.</p>
                    </div>

                    <div class="pillar-card">
                        <div class="pillar-icon-box">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>
                        </div>
                        <h3 class="pillar-name">Vision</h3>
                        <p class="pillar-desc">Micro camera scene perception with immediate on-device pixel discard, protecting absolute personal privacy.</p>
                    </div>

                    <div class="pillar-card">
                        <div class="pillar-icon-box">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                        </div>
                        <h3 class="pillar-name">Context</h3>
                        <p class="pillar-desc">Temporal schedule integration and live spatial awareness without requiring phone taps or screen glance.</p>
                    </div>

                    <div class="pillar-card">
                        <div class="pillar-icon-box">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"/></svg>
                        </div>
                        <h3 class="pillar-name">Memory</h3>
                        <p class="pillar-desc">Private rolling encrypted associative memory that recalls facts, research, and contacts effortlessly.</p>
                    </div>

                    <div class="pillar-card">
                        <div class="pillar-icon-box">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
                        </div>
                        <h3 class="pillar-name">Assistance</h3>
                        <p class="pillar-desc">God's Eye transit navigation, automated scam protection, and concise spoken answers directly into your ears.</p>
                    </div>
                </div>
            </div>

            <!-- Environmental Transition 1: Deep Forest Walk -->
            <div class="env-banner-section" style="background-image: url('/static/environments/forest.jpg');">
                <div class="env-banner-overlay"></div>
                <div class="env-glass-card">
                    <h3 class="env-glass-title">Living in the Natural Flow</h3>
                    <p class="env-glass-desc">EVA's dual-I2S acoustic pipeline listens silently. It operates at 0ms local latency for daily tasks, letting you absorb the peace of nature without digital clutter.</p>
                    <div class="env-meta-tags">
                        <span class="env-meta-pill"><span class="status-dot"></span> Acoustic VAD Active</span>
                        <span class="env-meta-pill">Local Edge SLM</span>
                        <span class="env-meta-pill">Zero Cloud Audio Storage</span>
                    </div>
                </div>
            </div>

            <!-- Personal Activity Journal Section -->
            <div class="journal-section" id="journal">
                <div class="journal-container">
                    <div class="journal-header">
                        <div>
                            <span class="story-eyebrow">Personal Journal</span>
                            <h2 style="font-size:24px; font-weight:700; color:var(--eva-primary-black);">Your Journey with EVA</h2>
                            <p style="font-size:14px; color:var(--eva-muted-text); margin-top:4px;">Chronological timeline of voice interactions, spatial queries, and daily assists.</p>
                        </div>
                        <button class="btn-console-toggle" onclick="loadJournalActivity()">Refresh Activity</button>
                    </div>

                    <div class="timeline-stream" id="journal-timeline-list">
                        <!-- Loaded dynamically from real backend events -->
                        <div class="empty-state-journal">Loading real device journal...</div>
                    </div>
                </div>
            </div>

            <!-- Environmental Transition 2: Academic Campus & Work -->
            <div class="env-banner-section" style="background-image: url('/static/environments/campus.jpg');">
                <div class="env-banner-overlay"></div>
                <div class="env-glass-card">
                    <h3 class="env-glass-title">Focus &amp; Cognitive Flow</h3>
                    <p class="env-glass-desc">Walk through university corridors and workspaces with an assistant that recalls meeting topics, research papers, and calendar briefs instantly upon request.</p>
                    <div class="env-meta-tags">
                        <span class="env-meta-pill"><span class="status-dot"></span> Schedule Awareness</span>
                        <span class="env-meta-pill">Research Citation Engine</span>
                        <span class="env-meta-pill">Desk Analytics</span>
                    </div>
                </div>
            </div>

            <!-- App Configuration & Experience Controls -->
            <div class="config-section" id="config">
                <div class="story-header" style="margin-bottom:40px;">
                    <span class="story-eyebrow">Personalization</span>
                    <h2 class="story-title">Your EVA Experience</h2>
                    <p class="story-subtitle">Refined controls shaping how intelligence interacts with your everyday life.</p>
                </div>

                <div class="config-grid">
                    <div class="config-card">
                        <div class="config-card-title">
                            <span>Voice &amp; Audio</span>
                            <span class="transit-badge">I2S Ready</span>
                        </div>
                        <div class="config-row"><span class="config-label">VAD Sensitivity</span><span class="config-val">Adaptive Threshold</span></div>
                        <div class="config-row"><span class="config-label">Spoken Response Style</span><span class="config-val">Concise (Max 2 sentences)</span></div>
                        <div class="config-row"><span class="config-label">Echo Fallback</span><span class="config-val" style="color:var(--eva-primary-green);">Disabled (Pure Natural)</span></div>
                    </div>

                    <div class="config-card">
                        <div class="config-card-title">
                            <span>Privacy &amp; Boundaries</span>
                            <span class="transit-badge">Protected</span>
                        </div>
                        <div class="config-row"><span class="config-label">Camera Pixels</span><span class="config-val" style="color:var(--eva-primary-green);">Discard Immediately</span></div>
                        <div class="config-row"><span class="config-label">Local SLM Processing</span><span class="config-val">On-Device Preferred</span></div>
                        <div class="config-row"><span class="config-label">Data Retention</span><span class="config-val">Encrypted Local Roll</span></div>
                    </div>

                    <div class="config-card">
                        <div class="config-card-title">
                            <span>Integrations &amp; Workspace</span>
                            <span class="transit-badge">Live</span>
                        </div>
                        <div class="config-row"><span class="config-label">Google Workspace</span><span class="config-val" style="color:var(--eva-primary-green);">Connected</span></div>
                        <div class="config-row"><span class="config-label">GitHub Repository</span><span class="config-val" style="color:var(--eva-primary-green);">Synced</span></div>
                        <div class="config-row"><span class="config-label">Tavily Live Search</span><span class="config-val" style="color:var(--eva-primary-green);">Active</span></div>
                    </div>
                </div>
            </div>

            <!-- Environmental Transition 3: City Promenade & Evening -->
            <div class="env-banner-section" style="background-image: url('/static/environments/city.jpg');">
                <div class="env-banner-overlay"></div>
                <div class="env-glass-card">
                    <h3 class="env-glass-title">God's Eye Live Spatial Radar</h3>
                    <p class="env-glass-desc">Urban navigation without phone gazing. Real-time metro departures, traffic bottlenecks, and flight gate alerts whispered naturally into your glasses.</p>
                    <div class="env-meta-tags">
                        <span class="env-meta-pill"><span class="status-dot"></span> Real-time Heatmaps</span>
                        <span class="env-meta-pill">Metro Countdown</span>
                        <span class="env-meta-pill">Flight Gate Status</span>
                    </div>
                </div>
            </div>

            <!-- God's Eye Live Transit Explorer -->
            <div class="journal-section" id="transit">
                <div class="journal-container">
                    <div class="journal-header">
                        <div>
                            <span class="story-eyebrow">Spatial Telemetry</span>
                            <h2 style="font-size:24px; font-weight:700; color:var(--eva-primary-black);">God's Eye Live Transit Intelligence</h2>
                            <p style="font-size:14px; color:var(--eva-muted-text); margin-top:4px;">Live traffic corridors, upcoming metro platforms, rail running status, and airport flight radars.</p>
                        </div>
                        <button class="btn-console-toggle" onclick="refreshLiveTransit()">Refresh Transit</button>
                    </div>

                    <div class="transit-live-grid" id="transit-cards-container">
                        <div class="transit-live-card">
                            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                                <strong style="font-size:14px; color:var(--eva-primary-black);">Outer Ring Road</strong>
                                <span class="transit-badge">Moderate</span>
                            </div>
                            <p style="font-size:12px; color:var(--eva-muted-text); line-height:1.5;">Average speed 34 km/h. Delay +4m. Flow optimal towards Silk Board junction.</p>
                        </div>

                        <div class="transit-live-card">
                            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                                <strong style="font-size:14px; color:var(--eva-primary-black);">Purple Metro Line</strong>
                                <span class="transit-badge">Platform 2</span>
                            </div>
                            <p style="font-size:12px; color:var(--eva-muted-text); line-height:1.5;">Indiranagar Station. Next train to Whitefield in 3 mins. Frequency: Every 4m.</p>
                        </div>

                        <div class="transit-live-card">
                            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                                <strong style="font-size:14px; color:var(--eva-primary-black);">IndiGo Flight 6E-204</strong>
                                <span class="transit-badge">Gate 48B</span>
                            </div>
                            <p style="font-size:12px; color:var(--eva-muted-text); line-height:1.5;">BLR &rarr; DEL. Terminal 2. Status: ON TIME. Boarding starts at 14:35.</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Environmental Transition 4: Peaceful Night Walk -->
            <div class="env-banner-section" style="background-image: url('/static/environments/night.jpg');">
                <div class="env-banner-overlay"></div>
                <div class="env-glass-card">
                    <h3 class="env-glass-title">Calm Evening &amp; Night Rest</h3>
                    <p class="env-glass-desc">As day turns to evening, EVA transitions into low-power night awareness. Audio notifications attenuate into subtle chimes, ensuring uncompromised serenity.</p>
                    <div class="env-meta-tags">
                        <span class="env-meta-pill"><span class="status-dot"></span> Night Mode Enabled</span>
                        <span class="env-meta-pill">Low Power Standby</span>
                        <span class="env-meta-pill">Ambient Chimes</span>
                    </div>
                </div>
            </div>

            <!-- Usage & Insights Section -->
            <div class="insights-section" id="insights">
                <div class="story-header" style="margin-bottom:40px;">
                    <span class="story-eyebrow">Relationship with EVA</span>
                    <h2 class="story-title">Usage &amp; Ambient Insights</h2>
                    <p class="story-subtitle">Meaningful metrics reflecting how EVA supports your everyday life.</p>
                </div>

                <div class="insights-grid">
                    <div class="insight-chart-card">
                        <h3 style="font-size:16px; font-weight:700; color:var(--eva-primary-black); margin-bottom:4px;">Voice &amp; Spatial Sessions</h3>
                        <p style="font-size:12px; color:var(--eva-muted-text);">Daily conversational interactions and transit lookups.</p>
                        <div class="chart-bar-canvas">
                            <div class="chart-bar-item" style="height: 40%;" title="Mon: 12 sessions"></div>
                            <div class="chart-bar-item" style="height: 65%;" title="Tue: 22 sessions"></div>
                            <div class="chart-bar-item" style="height: 50%;" title="Wed: 18 sessions"></div>
                            <div class="chart-bar-item" style="height: 85%;" title="Thu: 30 sessions"></div>
                            <div class="chart-bar-item" style="height: 70%;" title="Fri: 25 sessions"></div>
                            <div class="chart-bar-item" style="height: 45%;" title="Sat: 15 sessions"></div>
                            <div class="chart-bar-item" style="height: 35%;" title="Sun: 10 sessions"></div>
                        </div>
                    </div>

                    <div class="insight-chart-card">
                        <h3 style="font-size:16px; font-weight:700; color:var(--eva-primary-black); margin-bottom:4px;">Local vs Cloud Inference Ratio</h3>
                        <p style="font-size:12px; color:var(--eva-muted-text);">78% of interactions processed privately on edge.</p>
                        <div class="chart-bar-canvas">
                            <div class="chart-bar-item" style="height: 80%;" title="Edge Local: 78%"></div>
                            <div class="chart-bar-item secondary" style="height: 22%;" title="Cloud Multi-Agent: 22%"></div>
                        </div>
                    </div>
                </div>
            </div>

        </section>

        <!-- ========================================================= -->
        <!-- VIEW 2: DEVICE MANAGEMENT CONSOLE & ANALYTICS             -->
        <!-- ========================================================= -->
        <section class="view-section" id="view-console">
            <div class="console-container">
                
                <!-- Console Top Header -->
                <div class="console-header-bar">
                    <div class="console-title-group">
                        <h1>EVA Device Console</h1>
                        <p>Real-time telemetry, device management, and operational analytics for your EVA hardware.</p>
                    </div>
                    <div class="console-status-badge">
                        <span class="status-dot"></span>
                        <span id="console-live-status">All systems operational • EVA-GLS-01</span>
                    </div>
                </div>

                <!-- System Overview Summary Chips -->
                <div class="overview-grid">
                    <div class="overview-chip-card">
                        <div class="overview-chip-label">Glasses</div>
                        <div class="overview-chip-value" style="color:var(--eva-primary-green);"><span class="status-dot"></span> Connected</div>
                        <div class="overview-chip-sub">Seeed XIAO S3 • BLE Ready</div>
                    </div>
                    <div class="overview-chip-card">
                        <div class="overview-chip-label">Phone Companion</div>
                        <div class="overview-chip-value" style="color:var(--eva-primary-green);"><span class="status-dot"></span> Connected</div>
                        <div class="overview-chip-sub">Android Edge Gateway</div>
                    </div>
                    <div class="overview-chip-card">
                        <div class="overview-chip-label">Battery</div>
                        <div class="overview-chip-value" id="val-battery">78%</div>
                        <div class="overview-chip-sub">Estimated 5.4h remaining</div>
                    </div>
                    <div class="overview-chip-card">
                        <div class="overview-chip-label">Firmware</div>
                        <div class="overview-chip-value">v1.2.0</div>
                        <div class="overview-chip-sub">Up to date</div>
                    </div>
                    <div class="overview-chip-card">
                        <div class="overview-chip-label">Audio Routing</div>
                        <div class="overview-chip-value">TWS Output</div>
                        <div class="overview-chip-sub">MAX98357A I2S 16kHz</div>
                    </div>
                    <div class="overview-chip-card">
                        <div class="overview-chip-label">Sensors</div>
                        <div class="overview-chip-value">Active</div>
                        <div class="overview-chip-sub">INMP441 Mic + VAD Ready</div>
                    </div>
                </div>

                <!-- Console Navigation Strip -->
                <div class="console-nav-strip">
                    <button class="console-tab-btn active" id="tab-btn-manage" onclick="setConsoleTab('manage')">Device Management</button>
                    <button class="console-tab-btn" id="tab-btn-health" onclick="setConsoleTab('health')">Health &amp; Analytics</button>
                    <button class="console-tab-btn" id="tab-btn-transit" onclick="setConsoleTab('transit')">God's Eye Transit</button>
                    <button class="console-tab-btn" id="tab-btn-activity" onclick="setConsoleTab('activity')">Activity Timeline</button>
                </div>

                <!-- TAB 1: DEVICE MANAGEMENT -->
                <div class="console-panel active" id="panel-manage">
                    <div class="config-grid">
                        <div class="config-card">
                            <div class="config-card-title">
                                <span>Firmware Management</span>
                                <button class="btn-console-toggle" style="padding:4px 12px; font-size:11px;" onclick="checkFirmwareUpdates()">Check Updates</button>
                            </div>
                            <div class="config-row"><span class="config-label">Current Version</span><span class="config-val">v1.2.0</span></div>
                            <div class="config-row"><span class="config-label">Build Architecture</span><span class="config-val">ESP32-S3 FreeRTOS</span></div>
                            <div class="config-row"><span class="config-label">OTA Status</span><span class="config-val" style="color:var(--eva-primary-green);">Up to Date</span></div>
                        </div>

                        <div class="config-card">
                            <div class="config-card-title">
                                <span>Audio Hardware</span>
                                <span class="transit-badge">I2S Active</span>
                            </div>
                            <div class="config-row"><span class="config-label">Primary Speaker</span><span class="config-val">MAX98357A Amp</span></div>
                            <div class="config-row"><span class="config-label">Microphone</span><span class="config-val">INMP441 I2S</span></div>
                            <div class="config-row"><span class="config-label">VAD Mode</span><span class="config-val">Dynamic Noise Floor</span></div>
                        </div>

                        <div class="config-card">
                            <div class="config-card-title">
                                <span>Security &amp; Permissions</span>
                                <span class="transit-badge">Secure</span>
                            </div>
                            <div class="config-row"><span class="config-label">Microphone Access</span><span class="config-val" style="color:var(--eva-primary-green);">Allowed</span></div>
                            <div class="config-row"><span class="config-label">Bluetooth BLE</span><span class="config-val" style="color:var(--eva-primary-green);">Connected</span></div>
                            <div class="config-row"><span class="config-label">Spatial Location</span><span class="config-val" style="color:var(--eva-primary-green);">Allowed</span></div>
                        </div>
                    </div>
                </div>

                <!-- TAB 2: HEALTH & ANALYTICS -->
                <div class="console-panel" id="panel-health">
                    <div class="insight-chart-card">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                            <div>
                                <h3 style="font-size:16px; font-weight:700; color:var(--eva-primary-black);">System Performance &amp; Memory Telemetry</h3>
                                <p style="font-size:12px; color:var(--eva-muted-text);">Free Heap: 171 KB • CPU Load: 14% • Audio Latency: 42ms</p>
                            </div>
                            <button class="btn-console-toggle" style="font-size:11px; padding:4px 12px;" onclick="refreshHardwareTelemetry()">Refresh</button>
                        </div>
                        <div class="chart-bar-canvas">
                            <div class="chart-bar-item" style="height: 45%;" title="Free Heap: 171 KB"></div>
                            <div class="chart-bar-item secondary" style="height: 25%;" title="CPU: 14%"></div>
                            <div class="chart-bar-item" style="height: 60%;"></div>
                            <div class="chart-bar-item secondary" style="height: 35%;"></div>
                            <div class="chart-bar-item" style="height: 75%;"></div>
                            <div class="chart-bar-item secondary" style="height: 20%;"></div>
                            <div class="chart-bar-item" style="height: 55%;"></div>
                            <div class="chart-bar-item secondary" style="height: 18%;"></div>
                            <div class="chart-bar-item" style="height: 80%;"></div>
                            <div class="chart-bar-item secondary" style="height: 22%;"></div>
                        </div>
                    </div>
                </div>

                <!-- TAB 3: GOD'S EYE TRANSIT -->
                <div class="console-panel" id="panel-transit">
                    <div class="transit-live-grid">
                        <div class="transit-live-card">
                            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                                <strong style="font-size:14px; color:var(--eva-primary-black);">Road Traffic</strong>
                                <span class="transit-badge">Western Express</span>
                            </div>
                            <p style="font-size:12px; color:var(--eva-muted-text); line-height:1.5;">Heavy congestion near Santacruz flyover. Delay +18m. Recommended: Coastal Road Link.</p>
                        </div>
                        <div class="transit-live-card">
                            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                                <strong style="font-size:14px; color:var(--eva-primary-black);">Metro Network</strong>
                                <span class="transit-badge">Line 1 Blue</span>
                            </div>
                            <p style="font-size:12px; color:var(--eva-muted-text); line-height:1.5;">Andheri Metro Station (0.4 km). Next train to Ghatkopar in 2 min (Platform 1).</p>
                        </div>
                        <div class="transit-live-card">
                            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                                <strong style="font-size:14px; color:var(--eva-primary-black);">Flight Radar</strong>
                                <span class="transit-badge">IndiGo 6E-204</span>
                            </div>
                            <p style="font-size:12px; color:var(--eva-muted-text); line-height:1.5;">Terminal 2, Gate 48B. Status: BOARDING. Estimated departure: 14:35.</p>
                        </div>
                    </div>
                </div>

                <!-- TAB 4: ACTIVITY TIMELINE -->
                <div class="console-panel" id="panel-activity">
                    <div class="timeline-stream" id="console-activity-list">
                        <div class="empty-state-journal">
                            Your EVA device activity and voice sessions will appear here in chronological order.
                        </div>
                    </div>
                </div>

            </div>
        </section>

    </main>

    <!-- Bottom Voice Interaction Bar (Always accessible in Console) -->
    <div class="console-voice-bar" id="console-voice-bar" style="display:none;">
        <input 
            type="text" 
            class="console-input" 
            id="voice-command-input" 
            placeholder="Ask EVA anything or query transit (e.g., 'traffic on western express')..." 
            autocomplete="off"
            onkeydown="if(event.key==='Enter') executeVoiceCommand();"
        />
        <button class="btn-mic-action" id="btn-mic" title="Voice Input" onclick="toggleVoiceInput()">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="22"/></svg>
        </button>
        <button class="btn-primary" style="padding:8px 18px; font-size:13px;" onclick="executeVoiceCommand()">Ask</button>
    </div>

    <!-- Scripts -->
    <script>
        let currentMainView = 'product';

        function switchView(viewName) {
            currentMainView = viewName;
            document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
            const target = document.getElementById(`view-${viewName}`);
            if (target) target.classList.add('active');

            const voiceBar = document.getElementById('console-voice-bar');
            const toggleBtn = document.getElementById('btn-toggle-label');

            if (viewName === 'console') {
                voiceBar.style.display = 'flex';
                toggleBtn.innerText = 'Product Experience';
                loadConsoleActivity();
                refreshHardwareTelemetry();
            } else {
                voiceBar.style.display = 'none';
                toggleBtn.innerText = 'Device Console';
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        }

        function toggleMainView() {
            if (currentMainView === 'product') {
                switchView('console');
            } else {
                switchView('product');
            }
        }

        function scrollToSection(id) {
            const el = document.getElementById(id);
            if (el) el.scrollIntoView({ behavior: 'smooth' });
        }

        function setConsoleTab(tabName) {
            document.querySelectorAll('.console-tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.console-panel').forEach(p => p.classList.remove('active'));
            
            const btn = document.getElementById(`tab-btn-${tabName}`);
            const panel = document.getElementById(`panel-${tabName}`);
            if (btn) btn.classList.add('active');
            if (panel) panel.classList.add('active');

            if (tabName === 'activity') loadConsoleActivity();
        }

        async function loadJournalActivity() {
            const container = document.getElementById('journal-timeline-list');
            try {
                const res = await fetch('/api/v1/events/timeline?limit=10');
                const data = await res.json();
                const events = data.events || [];

                if (events.length === 0) {
                    container.innerHTML = `<div class="empty-state-journal">Your EVA activity and voice journeys will appear here as you interact.</div>`;
                    return;
                }

                let html = "";
                events.forEach(e => {
                    const timeStr = e.timestamp ? e.timestamp.substring(11, 16) : 'Just now';
                    html += `
                        <div class="timeline-entry">
                            <div class="entry-time">${timeStr}</div>
                            <div class="entry-body">
                                <div class="entry-title">${escapeHtml(e.title || e.type)}</div>
                                <div class="entry-desc">${escapeHtml(e.description || '')}</div>
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;
            } catch (e) {
                container.innerHTML = `<div class="empty-state-journal">Could not load journal activity.</div>`;
            }
        }

        async function loadConsoleActivity() {
            const container = document.getElementById('console-activity-list');
            try {
                const res = await fetch('/api/v1/events/timeline?limit=15');
                const data = await res.json();
                const events = data.events || [];

                if (events.length === 0) {
                    container.innerHTML = `<div class="empty-state-journal">Your EVA device activity will appear here.</div>`;
                    return;
                }

                let html = "";
                events.forEach(e => {
                    const timeStr = e.timestamp ? e.timestamp.substring(11, 16) : 'Just now';
                    html += `
                        <div class="timeline-entry">
                            <div class="entry-time">${timeStr}</div>
                            <div class="entry-body">
                                <div class="entry-title">${escapeHtml(e.title || e.type)}</div>
                                <div class="entry-desc">${escapeHtml(e.description || '')}</div>
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;
            } catch (e) {
                container.innerHTML = `<div class="empty-state-journal">Could not load activity: ${e.message}</div>`;
            }
        }

        async function refreshLiveTransit() {
            try {
                const res = await fetch('/api/v1/transit/traffic');
                const data = await res.json();
                if (data.corridors && data.corridors.length > 0) {
                    let html = "";
                    data.corridors.forEach(c => {
                        html += `
                            <div class="transit-live-card">
                                <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                                    <strong style="font-size:14px; color:var(--eva-primary-black);">${escapeHtml(c.name)}</strong>
                                    <span class="transit-badge">${escapeHtml(c.congestion_level)}</span>
                                </div>
                                <p style="font-size:12px; color:var(--eva-muted-text); line-height:1.5;">Speed ${c.average_speed_kmh} km/h. Delay +${c.delay_minutes}m. Status: ${escapeHtml(c.status)}</p>
                            </div>
                        `;
                    });
                    document.getElementById('transit-cards-container').innerHTML = html;
                }
            } catch (e) {
                console.debug("Transit refresh fallback:", e);
            }
        }

        async function refreshHardwareTelemetry() {
            try {
                const res = await fetch('/api/v1/hardware/status');
                const data = await res.json();
                if (data.battery_percentage !== undefined) {
                    document.getElementById('val-battery').innerText = `${data.battery_percentage}%`;
                }
            } catch (e) {}
        }

        function checkFirmwareUpdates() {
            alert("EVA Firmware v1.2.0 is currently up to date. (Channel: Stable)");
        }

        async function executeVoiceCommand() {
            const input = document.getElementById('voice-command-input');
            const query = input.value.trim();
            if (!query) return;

            input.value = "";
            const micBtn = document.getElementById('btn-mic');
            micBtn.classList.add('active');

            try {
                const res = await fetch('/api/v1/agent/message', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: query,
                        session_id: 'eva_web_session',
                        device_id: 'EVA_Device_Console',
                        language: 'auto'
                    })
                });
                const data = await res.json();
                const reply = data.response || "I am listening.";
                speak(reply);
            } catch (e) {
                alert(`Query error: ${e.message}`);
            } finally {
                micBtn.classList.remove('active');
            }
        }

        function speak(text) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                const u = new SpeechSynthesisUtterance(text);
                u.rate = 1.05;
                window.speechSynthesis.speak(u);
            }
        }

        function toggleVoiceInput() {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (SpeechRecognition) {
                const rec = new SpeechRecognition();
                const micBtn = document.getElementById('btn-mic');
                rec.onstart = () => { micBtn.classList.add('active'); };
                rec.onresult = (e) => {
                    document.getElementById('voice-command-input').value = e.results[0][0].transcript;
                    executeVoiceCommand();
                };
                rec.onend = () => { micBtn.classList.remove('active'); };
                rec.start();
            } else {
                alert("Speech recognition is not supported in this browser.");
            }
        }

        function escapeHtml(str) {
            if (!str) return '';
            return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
        }

        window.addEventListener('DOMContentLoaded', () => {
            loadJournalActivity();
            if (window.location.pathname.includes('/console')) {
                switchView('console');
            }
        });
    </script>
</body>
</html>
"""
