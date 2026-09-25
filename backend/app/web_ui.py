def get_dashboard_html() -> str:
    """
    Returns EVA: Immersive Liquid Glass Product Experience & Device Console.
    Design Philosophy: 'World First. Interface Second.'
    Palette: Warm Ivory (#F7F4EC, #F1EEE4), Pure White (#FFFFFF), Natural Green (#3F6B4F, #294A36, #6F9278), Controlled Dark (#111311).
    Sections:
      1. Minimal Liquid Glass Navigation
      2. Hero: Immersive Autumn Walkway ('SEE MORE. LIVE DEEPER.')
      3. Experience: Intelligence That Stays With You (Voice, Vision, Context, Memory, Assistance)
      4. Live Activity: Your Journey with EVA (Interactive Timeline)
      5. App Configuration: Your EVA Experience (Voice, Vision, Context, Notifications, Privacy, Integrations)
      6. Usage & Insights: Calm Editorial Analytics & Activity Waves
      7. Device Status Layer: Real-Time Glass Telemetry
      8. Device Console View: Health, Diagnostics, Firmware, Permissions, Connectivity
      9. Editorial Nature Footer: 'A More Present You.'
    """
    return r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <!-- EVA Smart Glasses Operations Console | ESP32 Smart Glasses & Android Hub | Private Intelligence & Control | Intent Inspector | Desk & Data Analysis | Automations Center | Smart Notifications -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>EVA — See More. Live Deeper. | Ambient Intelligence</title>
    
    <!-- Real-time Test Contract Hooks -->
    <script>
        function updateHardwareStatus(d) {
            console.debug("Hardware sync:", d);
            if (window.evaUpdateHardware) window.evaUpdateHardware(d);
        }
        function simulateIncomingSmsPrompt(sender, phone, body) {
            console.debug("Simulating SMS:", sender, phone, body);
            if (window.evaSimulateSms) window.evaSimulateSms(sender, phone, body);
        }
        function triggerMultimodalCapture(promptText) {
            console.debug("Multimodal capture trigger:", promptText);
            if (window.evaTriggerCapture) window.evaTriggerCapture(promptText);
        }
    </script>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;0,6..72,500;1,6..72,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

    <style>
        :root {
            /* 70% Ivory / White Foundation */
            --eva-bg: #F7F4EC;
            --eva-ivory: #F7F4EC;
            --eva-warm-ivory: #F1EEE4;
            --eva-pure-white: #FFFFFF;
            --eva-white-90: rgba(255, 255, 255, 0.90);
            --eva-white-75: rgba(255, 255, 255, 0.75);
            --eva-white-60: rgba(255, 255, 255, 0.60);
            --eva-white-40: rgba(255, 255, 255, 0.40);

            /* 20% Neutral Stone Surfaces */
            --eva-stone: #E8E5DC;
            --eva-stone-light: #EFECE4;
            --eva-border: rgba(255, 255, 255, 0.70);
            --eva-border-subtle: rgba(220, 216, 204, 0.55);

            /* 8-10% Natural Green Accent */
            --eva-primary-green: #3F6B4F;
            --eva-deep-green: #294A36;
            --eva-soft-green: #6F9278;
            --eva-pale-green: #DDE9DF;
            --eva-mist-green: #EEF4EF;
            --eva-green-glow: rgba(63, 107, 79, 0.25);

            /* <5% Controlled Contrast */
            --eva-primary-black: #111311;
            --eva-soft-black: #252824;
            --eva-text-body: #323631;
            --eva-text-muted: #626861;
            --eva-text-light: #8E968D;

            /* Liquid Glassmorphism Properties */
            --glass-bg: rgba(255, 255, 255, 0.68);
            --glass-bg-hover: rgba(255, 255, 255, 0.82);
            --glass-bg-subtle: rgba(255, 255, 255, 0.48);
            --glass-blur: blur(28px);
            --glass-border: 1px solid rgba(255, 255, 255, 0.65);
            --glass-shadow: 0 16px 40px -10px rgba(22, 28, 23, 0.08), 0 4px 12px -2px rgba(22, 28, 23, 0.04), inset 0 1px 1px rgba(255, 255, 255, 0.85);
            --glass-shadow-lg: 0 28px 60px -12px rgba(22, 28, 23, 0.12), inset 0 1.5px 1px rgba(255, 255, 255, 0.95);

            --radius-xs: 8px;
            --radius-sm: 14px;
            --radius-md: 20px;
            --radius-lg: 28px;
            --radius-xl: 36px;
            --radius-full: 9999px;

            --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            --font-editorial: 'Newsreader', Georgia, serif;
            --font-mono: 'JetBrains Mono', monospace;

            --transition-smooth: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
            --transition-fast: all 0.2s ease;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-font-smoothing: antialiased;
        }

        html {
            scroll-behavior: smooth;
            background-color: var(--eva-bg);
            font-family: var(--font-sans);
            color: var(--eva-text-body);
        }

        body {
            background-color: var(--eva-bg);
            overflow-x: hidden;
            line-height: 1.6;
        }

        /* Ambient scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: var(--eva-bg);
        }
        ::-webkit-scrollbar-thumb {
            background: var(--eva-stone);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--eva-soft-green);
        }

        /* SVG Icon Helper */
        .eva-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 20px;
            height: 20px;
            fill: currentColor;
            flex-shrink: 0;
        }

        /* ========================================================= */
        /* 1. MINIMAL LIQUID GLASS NAVIGATION BAR                     */
        /* ========================================================= */
        .eva-nav-wrapper {
            position: fixed;
            top: 20px;
            left: 0;
            right: 0;
            z-index: 1000;
            display: flex;
            justify-content: center;
            padding: 0 24px;
            pointer-events: none;
        }

        .eva-navbar {
            pointer-events: auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            width: 100%;
            max-width: 1180px;
            height: 62px;
            padding: 0 14px 0 24px;
            background: rgba(255, 255, 255, 0.72);
            backdrop-filter: var(--glass-blur);
            -webkit-backdrop-filter: var(--glass-blur);
            border: var(--glass-border);
            border-radius: var(--radius-full);
            box-shadow: var(--glass-shadow);
            transition: var(--transition-smooth);
        }

        .eva-navbar:hover {
            background: rgba(255, 255, 255, 0.85);
            box-shadow: var(--glass-shadow-lg);
        }

        .eva-brand {
            display: flex;
            align-items: center;
            gap: 12px;
            text-decoration: none;
            color: var(--eva-primary-black);
            font-weight: 800;
            font-size: 19px;
            letter-spacing: 3px;
        }

        .eva-brand-tag {
            font-size: 10px;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            font-weight: 700;
            color: var(--eva-primary-green);
            background: var(--eva-mist-green);
            padding: 3px 8px;
            border-radius: var(--radius-full);
            border: 1px solid var(--eva-pale-green);
        }

        .eva-nav-links {
            display: flex;
            align-items: center;
            gap: 28px;
            list-style: none;
        }

        .eva-nav-links a {
            text-decoration: none;
            color: var(--eva-text-muted);
            font-size: 14px;
            font-weight: 500;
            transition: var(--transition-fast);
            position: relative;
            padding: 6px 0;
        }

        .eva-nav-links a:hover,
        .eva-nav-links a.active {
            color: var(--eva-primary-black);
        }

        .eva-nav-links a.active::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: var(--eva-primary-green);
            border-radius: 2px;
        }

        .eva-nav-actions {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .eva-status-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(255, 255, 255, 0.85);
            border: 1px solid var(--eva-pale-green);
            padding: 6px 14px;
            border-radius: var(--radius-full);
            font-size: 12px;
            font-weight: 600;
            color: var(--eva-deep-green);
        }

        .status-dot-pulse {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--eva-primary-green);
            box-shadow: 0 0 0 0 rgba(63, 107, 79, 0.7);
            animation: pulse-green 2s infinite;
        }

        @keyframes pulse-green {
            0% { box-shadow: 0 0 0 0 rgba(63, 107, 79, 0.7); }
            70% { box-shadow: 0 0 0 8px rgba(63, 107, 79, 0); }
            100% { box-shadow: 0 0 0 0 rgba(63, 107, 79, 0); }
        }

        .eva-btn-nav {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: var(--eva-deep-green);
            color: var(--eva-pure-white);
            border: none;
            padding: 9px 18px;
            border-radius: var(--radius-full);
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            transition: var(--transition-fast);
        }

        .eva-btn-nav:hover {
            background: var(--eva-primary-green);
            transform: translateY(-1px);
        }

        /* ========================================================= */
        /* 2. HERO SECTION — IMMERSIVE AUTUMN WALKWAY                 */
        /* ========================================================= */
        .eva-hero-section {
            position: relative;
            min-height: 100vh;
            width: 100%;
            display: flex;
            align-items: flex-end;
            padding: 140px 32px 64px;
            background: url('/static/environments/autumn_walk.jpg') center center / cover no-repeat;
            overflow: hidden;
        }

        .eva-hero-backdrop-tint {
            position: absolute;
            inset: 0;
            background: linear-gradient(
                to bottom,
                rgba(17, 19, 17, 0.35) 0%,
                rgba(17, 19, 17, 0.15) 40%,
                rgba(247, 244, 236, 0.25) 75%,
                rgba(247, 244, 236, 0.95) 100%
            );
            pointer-events: none;
        }

        .eva-hero-container {
            position: relative;
            z-index: 2;
            width: 100%;
            max-width: 1180px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1.15fr 0.85fr;
            gap: 48px;
            align-items: flex-end;
        }

        .eva-hero-content {
            padding-bottom: 24px;
        }

        .eva-hero-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(255, 255, 255, 0.82);
            backdrop-filter: var(--glass-blur);
            -webkit-backdrop-filter: var(--glass-blur);
            border: var(--glass-border);
            padding: 7px 16px;
            border-radius: var(--radius-full);
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            color: var(--eva-deep-green);
            margin-bottom: 20px;
            box-shadow: var(--glass-shadow);
        }

        .eva-hero-title {
            font-family: var(--font-editorial);
            font-size: clamp(52px, 6.5vw, 84px);
            line-height: 1.05;
            font-weight: 400;
            color: var(--eva-primary-black);
            letter-spacing: -1.5px;
            margin-bottom: 22px;
            text-shadow: 0 2px 20px rgba(255, 255, 255, 0.4);
        }

        .eva-hero-title span {
            font-style: italic;
            font-weight: 300;
            color: var(--eva-deep-green);
        }

        .eva-hero-subtitle {
            font-size: 20px;
            font-weight: 400;
            color: var(--eva-soft-black);
            margin-bottom: 8px;
            max-width: 520px;
        }

        .eva-hero-secondary {
            font-size: 15px;
            font-weight: 500;
            color: var(--eva-text-muted);
            margin-bottom: 36px;
            letter-spacing: 0.5px;
        }

        .eva-hero-ctas {
            display: flex;
            align-items: center;
            gap: 16px;
            flex-wrap: wrap;
        }

        .eva-btn-primary {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            background: var(--eva-deep-green);
            color: var(--eva-pure-white);
            font-size: 15px;
            font-weight: 600;
            padding: 14px 28px;
            border-radius: var(--radius-full);
            text-decoration: none;
            border: 1px solid var(--eva-deep-green);
            box-shadow: 0 10px 24px -4px rgba(41, 74, 54, 0.35);
            transition: var(--transition-fast);
            cursor: pointer;
        }

        .eva-btn-primary:hover {
            background: var(--eva-primary-green);
            transform: translateY(-2px);
            box-shadow: 0 14px 28px -4px rgba(41, 74, 54, 0.45);
        }

        .eva-btn-secondary {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            background: rgba(255, 255, 255, 0.78);
            backdrop-filter: var(--glass-blur);
            -webkit-backdrop-filter: var(--glass-blur);
            color: var(--eva-primary-black);
            font-size: 15px;
            font-weight: 600;
            padding: 14px 26px;
            border-radius: var(--radius-full);
            text-decoration: none;
            border: var(--glass-border);
            box-shadow: var(--glass-shadow);
            transition: var(--transition-fast);
            cursor: pointer;
        }

        .eva-btn-secondary:hover {
            background: rgba(255, 255, 255, 0.95);
            transform: translateY(-2px);
            box-shadow: var(--glass-shadow-lg);
        }

        /* Hero Right Ambient Widget */
        .eva-hero-widget-card {
            background: rgba(255, 255, 255, 0.72);
            backdrop-filter: var(--glass-blur);
            -webkit-backdrop-filter: var(--glass-blur);
            border: var(--glass-border);
            border-radius: var(--radius-xl);
            padding: 32px;
            box-shadow: var(--glass-shadow-lg);
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .widget-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .widget-badge {
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            color: var(--eva-primary-green);
            background: var(--eva-mist-green);
            padding: 4px 10px;
            border-radius: var(--radius-full);
            border: 1px solid var(--eva-pale-green);
        }

        .widget-time {
            font-size: 13px;
            font-weight: 500;
            color: var(--eva-text-muted);
        }

        .widget-live-block {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .widget-live-title {
            font-size: 18px;
            font-weight: 700;
            color: var(--eva-primary-black);
        }

        .widget-live-desc {
            font-size: 14px;
            color: var(--eva-text-muted);
            line-height: 1.5;
        }

        .widget-metrics-row {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            padding-top: 12px;
            border-top: 1px solid var(--eva-border-subtle);
        }

        .widget-metric-cell {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }

        .widget-metric-num {
            font-size: 17px;
            font-weight: 700;
            color: var(--eva-primary-black);
        }

        .widget-metric-label {
            font-size: 11px;
            color: var(--eva-text-light);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* ========================================================= */
        /* 3. SECTION: EVA EXPERIENCE (FOREST CANOPY)                 */
        /* ========================================================= */
        .eva-section {
            padding: 110px 32px;
            position: relative;
        }

        .eva-section-env {
            position: relative;
            background: url('/static/environments/forest.jpg') center center / cover no-repeat;
            border-radius: var(--radius-xl);
            margin: 0 auto 40px;
            max-width: 1240px;
            padding: 90px 48px;
            overflow: hidden;
            box-shadow: 0 24px 60px -12px rgba(22, 28, 23, 0.15);
        }

        .eva-section-env::before {
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, rgba(247, 244, 236, 0.88) 0%, rgba(247, 244, 236, 0.65) 50%, rgba(238, 244, 239, 0.78) 100%);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            pointer-events: none;
        }

        .eva-container {
            position: relative;
            z-index: 2;
            max-width: 1140px;
            margin: 0 auto;
        }

        .eva-section-header {
            max-width: 680px;
            margin-bottom: 56px;
        }

        .eva-section-tag {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: var(--eva-primary-green);
            margin-bottom: 14px;
        }

        .eva-section-title {
            font-family: var(--font-editorial);
            font-size: clamp(38px, 4.5vw, 56px);
            font-weight: 400;
            line-height: 1.15;
            color: var(--eva-primary-black);
            margin-bottom: 16px;
            letter-spacing: -0.8px;
        }

        .eva-section-subtitle {
            font-size: 17px;
            color: var(--eva-text-muted);
            line-height: 1.6;
        }

        /* 5 Core Pillars Grid */
        .eva-pillars-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }

        .eva-pillar-card {
            background: rgba(255, 255, 255, 0.70);
            backdrop-filter: var(--glass-blur);
            -webkit-backdrop-filter: var(--glass-blur);
            border: var(--glass-border);
            border-radius: var(--radius-lg);
            padding: 28px 24px;
            box-shadow: var(--glass-shadow);
            transition: var(--transition-smooth);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 220px;
        }

        .eva-pillar-card:hover {
            background: rgba(255, 255, 255, 0.88);
            transform: translateY(-4px);
            box-shadow: var(--glass-shadow-lg);
            border-color: var(--eva-pale-green);
        }

        .pillar-icon-box {
            width: 44px;
            height: 44px;
            border-radius: var(--radius-sm);
            background: var(--eva-mist-green);
            border: 1px solid var(--eva-pale-green);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--eva-deep-green);
            margin-bottom: 20px;
        }

        .pillar-title {
            font-size: 18px;
            font-weight: 700;
            color: var(--eva-primary-black);
            margin-bottom: 8px;
        }

        .pillar-desc {
            font-size: 13px;
            color: var(--eva-text-muted);
            line-height: 1.5;
        }

        .pillar-status {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            font-weight: 600;
            color: var(--eva-primary-green);
            margin-top: 18px;
            padding-top: 12px;
            border-top: 1px solid rgba(220, 216, 204, 0.4);
        }

        /* ========================================================= */
        /* 4. SECTION: LIVE EVA ACTIVITY TIMELINE                     */
        /* ========================================================= */
        .eva-activity-wrapper {
            background: var(--eva-ivory);
            padding: 40px 0 80px;
        }

        .activity-card-container {
            background: rgba(255, 255, 255, 0.75);
            backdrop-filter: var(--glass-blur);
            -webkit-backdrop-filter: var(--glass-blur);
            border: var(--glass-border);
            border-radius: var(--radius-xl);
            padding: 48px;
            box-shadow: var(--glass-shadow-lg);
        }

        .activity-header-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 32px;
            flex-wrap: wrap;
            gap: 16px;
        }

        .filter-pills-row {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }

        .filter-pill {
            background: var(--eva-stone-light);
            border: 1px solid transparent;
            color: var(--eva-text-muted);
            padding: 6px 16px;
            border-radius: var(--radius-full);
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition-fast);
        }

        .filter-pill:hover,
        .filter-pill.active {
            background: var(--eva-deep-green);
            color: var(--eva-pure-white);
            border-color: var(--eva-deep-green);
        }

        .timeline-stream {
            display: flex;
            flex-direction: column;
            gap: 0;
            position: relative;
        }

        .timeline-stream::before {
            content: '';
            position: absolute;
            left: 23px;
            top: 12px;
            bottom: 12px;
            width: 2px;
            background: var(--eva-stone);
        }

        .timeline-item {
            position: relative;
            display: flex;
            align-items: flex-start;
            gap: 20px;
            padding: 16px 0;
            transition: var(--transition-fast);
        }

        .timeline-icon-node {
            position: relative;
            z-index: 2;
            width: 46px;
            height: 46px;
            border-radius: 50%;
            background: var(--eva-pure-white);
            border: 2px solid var(--eva-pale-green);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--eva-primary-green);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            flex-shrink: 0;
        }

        .timeline-content-card {
            flex: 1;
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid var(--eva-border-subtle);
            border-radius: var(--radius-md);
            padding: 16px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            transition: var(--transition-fast);
        }

        .timeline-content-card:hover {
            background: var(--eva-pure-white);
            border-color: var(--eva-pale-green);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04);
        }

        .timeline-main-info {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .timeline-title-row {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .timeline-title {
            font-size: 15px;
            font-weight: 700;
            color: var(--eva-primary-black);
        }

        .timeline-badge {
            font-size: 11px;
            font-weight: 600;
            color: var(--eva-deep-green);
            background: var(--eva-mist-green);
            padding: 2px 8px;
            border-radius: var(--radius-full);
        }

        .timeline-detail {
            font-size: 13px;
            color: var(--eva-text-muted);
        }

        .timeline-time {
            font-family: var(--font-mono);
            font-size: 12px;
            color: var(--eva-text-light);
            font-weight: 500;
        }

        /* ========================================================= */
        /* 5. SECTION: APP CONFIGURATION & INTEGRATIONS               */
        /* ========================================================= */
        .eva-config-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 24px;
        }

        .config-glass-card {
            background: rgba(255, 255, 255, 0.72);
            backdrop-filter: var(--glass-blur);
            -webkit-backdrop-filter: var(--glass-blur);
            border: var(--glass-border);
            border-radius: var(--radius-lg);
            padding: 32px;
            box-shadow: var(--glass-shadow);
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .config-card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .config-title-group {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .config-icon-badge {
            width: 40px;
            height: 40px;
            border-radius: var(--radius-sm);
            background: var(--eva-mist-green);
            border: 1px solid var(--eva-pale-green);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--eva-primary-green);
        }

        .config-title {
            font-size: 17px;
            font-weight: 700;
            color: var(--eva-primary-black);
        }

        .config-subtitle {
            font-size: 12px;
            color: var(--eva-text-muted);
        }

        .config-toggle-switch {
            position: relative;
            width: 44px;
            height: 24px;
            background: var(--eva-stone);
            border-radius: var(--radius-full);
            cursor: pointer;
            transition: var(--transition-fast);
        }

        .config-toggle-switch.active {
            background: var(--eva-primary-green);
        }

        .config-toggle-handle {
            position: absolute;
            top: 2px;
            left: 2px;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: var(--eva-pure-white);
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
            transition: var(--transition-fast);
        }

        .config-toggle-switch.active .config-toggle-handle {
            transform: translateX(20px);
        }

        .config-options-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .config-option-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 13px;
            color: var(--eva-text-body);
            padding: 8px 12px;
            background: rgba(255, 255, 255, 0.6);
            border-radius: var(--radius-xs);
            border: 1px solid var(--eva-border-subtle);
        }

        .config-option-val {
            font-weight: 600;
            color: var(--eva-deep-green);
        }

        /* ========================================================= */
        /* 6. SECTION: USAGE & INSIGHTS (CALM SVG WAVE)               */
        /* ========================================================= */
        .analytics-dashboard-card {
            background: rgba(255, 255, 255, 0.75);
            backdrop-filter: var(--glass-blur);
            -webkit-backdrop-filter: var(--glass-blur);
            border: var(--glass-border);
            border-radius: var(--radius-xl);
            padding: 44px;
            box-shadow: var(--glass-shadow-lg);
        }

        .analytics-metrics-strip {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            margin-bottom: 36px;
        }

        .metric-stat-box {
            background: rgba(255, 255, 255, 0.85);
            border: 1px solid var(--eva-border-subtle);
            border-radius: var(--radius-md);
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .metric-stat-value {
            font-size: 28px;
            font-weight: 800;
            color: var(--eva-primary-black);
            letter-spacing: -0.5px;
        }

        .metric-stat-label {
            font-size: 12px;
            color: var(--eva-text-muted);
            font-weight: 500;
        }

        .metric-stat-trend {
            font-size: 11px;
            color: var(--eva-primary-green);
            font-weight: 600;
            margin-top: 4px;
        }

        .wave-chart-container {
            width: 100%;
            height: 200px;
            background: rgba(255, 255, 255, 0.65);
            border: 1px solid var(--eva-border-subtle);
            border-radius: var(--radius-lg);
            padding: 24px;
            position: relative;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .wave-svg {
            width: 100%;
            height: 120px;
            overflow: visible;
        }

        .wave-axis-labels {
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            font-weight: 600;
            color: var(--eva-text-light);
            text-transform: uppercase;
        }

        /* ========================================================= */
        /* 7. SECTION: DEVICE STATUS LAYER                            */
        /* ========================================================= */
        .device-status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 16px;
        }

        .device-status-tile {
            background: rgba(255, 255, 255, 0.72);
            backdrop-filter: var(--glass-blur);
            -webkit-backdrop-filter: var(--glass-blur);
            border: var(--glass-border);
            border-radius: var(--radius-md);
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            box-shadow: var(--glass-shadow);
            transition: var(--transition-fast);
        }

        .device-status-tile:hover {
            background: var(--eva-pure-white);
            transform: translateY(-2px);
        }

        .tile-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: var(--eva-text-muted);
        }

        .tile-name {
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 700;
            color: var(--eva-text-light);
        }

        .tile-value {
            font-size: 18px;
            font-weight: 700;
            color: var(--eva-primary-black);
        }

        .tile-sub {
            font-size: 11px;
            color: var(--eva-primary-green);
            font-weight: 600;
        }

        /* ========================================================= */
        /* 8. DEVICE CONSOLE MODAL / VIEW                             */
        /* ========================================================= */
        .eva-console-modal {
            display: none;
            position: fixed;
            inset: 0;
            z-index: 2000;
            background: rgba(17, 19, 17, 0.55);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            padding: 40px 24px;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .eva-console-modal.active {
            display: flex;
            opacity: 1;
        }

        .console-container {
            width: 100%;
            max-width: 1080px;
            max-height: 88vh;
            background: var(--eva-ivory);
            border: 1px solid rgba(255, 255, 255, 0.9);
            border-radius: var(--radius-xl);
            box-shadow: 0 32px 80px rgba(0, 0, 0, 0.25);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .console-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 24px 32px;
            background: var(--eva-pure-white);
            border-bottom: 1px solid var(--eva-border-subtle);
        }

        .console-header-left {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .console-header-title {
            font-size: 19px;
            font-weight: 800;
            color: var(--eva-primary-black);
            letter-spacing: 1px;
        }

        .console-close-btn {
            background: var(--eva-stone-light);
            border: none;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            color: var(--eva-primary-black);
            transition: var(--transition-fast);
        }

        .console-close-btn:hover {
            background: var(--eva-stone);
        }

        .console-body {
            display: grid;
            grid-template-columns: 240px 1fr;
            flex: 1;
            overflow: hidden;
        }

        .console-sidebar {
            background: var(--eva-warm-ivory);
            border-right: 1px solid var(--eva-border-subtle);
            padding: 24px 16px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            overflow-y: auto;
        }

        .console-nav-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 16px;
            border-radius: var(--radius-sm);
            font-size: 13px;
            font-weight: 600;
            color: var(--eva-text-muted);
            text-decoration: none;
            cursor: pointer;
            transition: var(--transition-fast);
        }

        .console-nav-item:hover,
        .console-nav-item.active {
            background: var(--eva-pure-white);
            color: var(--eva-deep-green);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }

        .console-content {
            padding: 32px;
            overflow-y: auto;
            background: var(--eva-ivory);
            display: flex;
            flex-direction: column;
            gap: 24px;
        }

        .console-panel {
            display: none;
        }

        .console-panel.active {
            display: flex;
            flex-direction: column;
            gap: 24px;
        }

        /* ========================================================= */
        /* 9. FOOTER — SUNSET HORIZON                                 */
        /* ========================================================= */
        .eva-footer-section {
            position: relative;
            padding: 120px 32px 64px;
            background: url('/static/environments/night_autumn.jpg') center center / cover no-repeat;
            color: var(--eva-pure-white);
            overflow: hidden;
        }

        .eva-footer-tint {
            position: absolute;
            inset: 0;
            background: linear-gradient(
                to bottom,
                rgba(247, 244, 236, 1) 0%,
                rgba(17, 19, 17, 0.55) 25%,
                rgba(17, 19, 17, 0.92) 100%
            );
            pointer-events: none;
        }

        .eva-footer-container {
            position: relative;
            z-index: 2;
            max-width: 1140px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 64px;
        }

        .footer-hero-text {
            text-align: center;
            max-width: 640px;
            margin: 0 auto;
        }

        .footer-headline {
            font-family: var(--font-editorial);
            font-size: clamp(40px, 5vw, 64px);
            font-weight: 400;
            line-height: 1.1;
            margin-bottom: 16px;
            letter-spacing: -1px;
        }

        .footer-sub {
            font-size: 17px;
            color: rgba(255, 255, 255, 0.8);
        }

        .footer-nav-grid {
            display: grid;
            grid-template-columns: 2fr repeat(3, 1fr);
            gap: 40px;
            padding-top: 48px;
            border-top: 1px solid rgba(255, 255, 255, 0.15);
        }

        .footer-col-title {
            font-size: 12px;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            font-weight: 700;
            margin-bottom: 16px;
            color: var(--eva-pale-green);
        }

        .footer-links {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .footer-links a {
            color: rgba(255, 255, 255, 0.7);
            text-decoration: none;
            font-size: 13px;
            transition: var(--transition-fast);
        }

        .footer-links a:hover {
            color: var(--eva-pure-white);
        }

        .footer-bottom-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 12px;
            color: rgba(255, 255, 255, 0.5);
            padding-top: 24px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* Memory & Cloud Intelligence Styles */
        .memory-card-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
            max-height: 380px;
            overflow-y: auto;
            padding-right: 4px;
        }

        .memory-item-card {
            background: var(--eva-pure-white);
            border: 1px solid var(--eva-border-subtle);
            border-radius: var(--radius-md);
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            transition: var(--transition-fast);
        }

        .memory-item-card:hover {
            border-color: var(--eva-primary-green);
            box-shadow: 0 4px 16px rgba(0,0,0,0.04);
        }

        .memory-header-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
            flex-wrap: wrap;
        }

        .memory-id-badge {
            font-family: var(--font-mono);
            font-size: 11px;
            font-weight: 700;
            color: var(--eva-deep-green);
            background: var(--eva-pale-green);
            padding: 2px 8px;
            border-radius: 4px;
        }

        .memory-kind-badge {
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            padding: 2px 6px;
            border-radius: 4px;
            background: var(--eva-stone-light);
            color: var(--eva-text-muted);
        }

        .sens-badge {
            font-size: 10px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: var(--radius-full);
            color: #fff;
        }
        .sens-S0 { background: #294A36; }
        .sens-S1 { background: #3F6B4F; }
        .sens-S2 { background: #B38F00; }
        .sens-S3 { background: #8C2D4A; }
        .sens-S4 { background: #B32400; }

        .memory-content-text {
            font-size: 13px;
            color: var(--eva-primary-black);
            line-height: 1.5;
        }

        .memory-footer-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 11px;
            color: var(--eva-text-light);
            padding-top: 6px;
            border-top: 1px dashed var(--eva-stone);
        }

        .cloud-input-field {
            width: 100%;
            background: var(--eva-pure-white);
            border: 1px solid var(--eva-border-subtle);
            border-radius: var(--radius-sm);
            padding: 10px 14px;
            font-family: var(--font-mono);
            font-size: 13px;
            color: var(--eva-primary-black);
            outline: none;
            transition: var(--transition-fast);
        }

        .cloud-input-field:focus {
            border-color: var(--eva-primary-green);
            box-shadow: 0 0 0 3px rgba(63, 107, 79, 0.15);
        }

        .cloud-btn-action {
            background: var(--eva-primary-green);
            color: #fff;
            border: none;
            padding: 10px 20px;
            border-radius: var(--radius-sm);
            font-weight: 600;
            font-size: 13px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: var(--transition-fast);
        }

        .cloud-btn-action:hover {
            background: var(--eva-deep-green);
            transform: translateY(-1px);
        }

        /* Mobile Adjustments */
        @media (max-width: 900px) {
            .eva-hero-container {
                grid-template-columns: 1fr;
            }
            .eva-nav-links {
                display: none;
            }
            .console-body {
                grid-template-columns: 1fr;
            }
            .console-sidebar {
                display: flex;
                flex-direction: row;
                overflow-x: auto;
                border-right: none;
                border-bottom: 1px solid var(--eva-border-subtle);
            }
            .footer-nav-grid {
                grid-template-columns: 1fr;
                gap: 28px;
            }
        }
    </style>
</head>
<body>

    <!-- ============================================================= -->
    <!-- 1. MINIMAL LIQUID GLASS NAVIGATION BAR                        -->
    <!-- ============================================================= -->
    <header class="eva-nav-wrapper">
        <nav class="eva-navbar">
            <a href="#" class="eva-brand">
                EVA
                <span class="eva-brand-tag">Spatial AI</span>
            </a>

            <ul class="eva-nav-links">
                <li><a href="#hero" class="active">Product</a></li>
                <li><a href="#experience">Experience</a></li>
                <li><a href="#activity">Activity</a></li>
                <li><a href="#configuration">Configuration</a></li>
                <li><a href="#insights">Insights</a></li>
                <li><a href="#status">Status</a></li>
            </ul>

            <div class="eva-nav-actions">
                <div class="eva-status-pill" id="nav-device-pill">
                    <span class="status-dot-pulse"></span>
                    <span id="nav-status-label">EVA Connected</span>
                </div>
                <button class="eva-btn-nav" onclick="openConsole('overview')">
                    Device Console
                    <svg class="eva-icon" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>
                </button>
            </div>
        </nav>
    </header>

    <!-- ============================================================= -->
    <!-- 2. HERO: AUTUMN TREE-LINED WALKWAY                            -->
    <!-- ============================================================= -->
    <section class="eva-hero-section" id="hero">
        <div class="eva-hero-backdrop-tint"></div>

        <div class="eva-hero-container">
            <div class="eva-hero-content">
                <div class="eva-hero-pill">
                    <svg class="eva-icon" viewBox="0 0 24 24" style="width:14px;height:14px;"><circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2" fill="none"/><circle cx="12" cy="12" r="3" fill="currentColor"/></svg>
                    Ambient Spatial Intelligence
                </div>

                <h1 class="eva-hero-title">
                    SEE MORE.<br>
                    <span>LIVE DEEPER.</span>
                </h1>

                <p class="eva-hero-subtitle">
                    Ambient intelligence for a more present you.
                </p>

                <p class="eva-hero-secondary">
                    Voice. Vision. Context. Always with you.
                </p>

                <div class="eva-hero-ctas">
                    <a href="#experience" class="eva-btn-primary">
                        Explore EVA
                        <svg class="eva-icon" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>
                    </a>
                    <button class="eva-btn-secondary" onclick="openConsole('overview')">
                        Open Device Console
                    </button>
                </div>
            </div>

            <!-- Right Ambient Live Status Widget -->
            <div class="eva-hero-widget-card">
                <div class="widget-header">
                    <span class="widget-badge" id="hero-badge-location"><span class="status-dot-pulse"></span> Nagpur, IN</span>
                    <span class="widget-time" id="hero-live-clock">--:-- --</span>
                </div>

                <div class="widget-live-block">
                    <div class="widget-live-title" id="hero-context-title">Good morning, Yash</div>
                    <div class="widget-live-desc" id="hero-context-desc">
                        Nagpur: 29°C · Clear Sky · 68 AQI (Satisfactory). Microphones and telemetry calibrated for ambient walk.
                    </div>
                </div>

                <div class="widget-metrics-row">
                    <div class="widget-metric-cell">
                        <span class="widget-metric-num" id="hero-metric-temp">29°C</span>
                        <span class="widget-metric-label">Ambient Temp</span>
                    </div>
                    <div class="widget-metric-cell">
                        <span class="widget-metric-num" id="hero-metric-aqi" style="color:var(--eva-primary-green);">68 AQI</span>
                        <span class="widget-metric-label">Air Quality</span>
                    </div>
                    <div class="widget-metric-cell">
                        <span class="widget-metric-num" id="hero-metric-battery">85%</span>
                        <span class="widget-metric-label">Battery</span>
                    </div>
                    <div class="widget-metric-cell">
                        <span class="widget-metric-num" id="hero-metric-latency">48ms</span>
                        <span class="widget-metric-label">Cloud TTFA</span>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- ============================================================= -->
    <!-- 3. SECTION: EVA EXPERIENCE (FOREST SUNLIGHT)                 -->
    <!-- ============================================================= -->
    <section class="eva-section" id="experience">
        <div class="eva-section-env">
            <div class="eva-container">
                <div class="eva-section-header">
                    <span class="eva-section-tag">
                        <svg class="eva-icon" viewBox="0 0 24 24" style="width:14px;height:14px;"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                        Natural Understanding
                    </span>
                    <h2 class="eva-section-title">Intelligence that stays with you.</h2>
                    <p class="eva-section-subtitle">
                        EVA does not pull you into a screen. It brings subtle spatial clarity to the world you are already experiencing.
                    </p>
                </div>

                <!-- 5 Core Pillars Grid -->
                <div class="eva-pillars-grid">
                    <div class="eva-pillar-card">
                        <div>
                            <div class="pillar-icon-box">
                                <svg class="eva-icon" viewBox="0 0 24 24"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" fill="currentColor"/><path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v4M8 23h8" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/></svg>
                            </div>
                            <h3 class="pillar-title">Voice</h3>
                            <p class="pillar-desc">Natural whispered dialogue with ultra-low latency acoustic response.</p>
                        </div>
                        <div class="pillar-status">
                            <span class="status-dot-pulse" style="width:6px;height:6px;"></span> Active Listening
                        </div>
                    </div>

                    <div class="eva-pillar-card">
                        <div>
                            <div class="pillar-icon-box">
                                <svg class="eva-icon" viewBox="0 0 24 24"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" stroke="currentColor" stroke-width="2" fill="none"/><circle cx="12" cy="13" r="4" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                            </div>
                            <h3 class="pillar-title">Vision</h3>
                            <p class="pillar-desc">Edge scene analysis, OCR document translation, and instant spatial recognition.</p>
                        </div>
                        <div class="pillar-status">
                            <span class="status-dot-pulse" style="width:6px;height:6px;"></span> 640x480 Sensor
                        </div>
                    </div>

                    <div class="eva-pillar-card">
                        <div>
                            <div class="pillar-icon-box">
                                <svg class="eva-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" fill="currentColor"/></svg>
                            </div>
                            <h3 class="pillar-title">Context</h3>
                            <p class="pillar-desc">Location-aware transit radar, weather shifts, and scheduled obligations.</p>
                        </div>
                        <div class="pillar-status">
                            <span class="status-dot-pulse" style="width:6px;height:6px;"></span> Geofence Sync
                        </div>
                    </div>

                    <div class="eva-pillar-card">
                        <div>
                            <div class="pillar-icon-box">
                                <svg class="eva-icon" viewBox="0 0 24 24"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" stroke="currentColor" stroke-width="2" fill="none"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                            </div>
                            <h3 class="pillar-title">Memory</h3>
                            <p class="pillar-desc">Episodic personal vector memory for meeting notes, ideas, and observations.</p>
                        </div>
                        <div class="pillar-status">
                            <span class="status-dot-pulse" style="width:6px;height:6px;"></span> Encrypted Local
                        </div>
                    </div>

                    <div class="eva-pillar-card">
                        <div>
                            <div class="pillar-icon-box">
                                <svg class="eva-icon" viewBox="0 0 24 24"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" stroke="currentColor" stroke-width="2" fill="none"/><path d="M13.73 21a2 2 0 0 1-3.46 0" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                            </div>
                            <h3 class="pillar-title">Assistance</h3>
                            <p class="pillar-desc">Proactive calendar alerts, priority email previews, and intelligent summaries.</p>
                        </div>
                        <div class="pillar-status">
                            <span class="status-dot-pulse" style="width:6px;height:6px;"></span> Standby
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- ============================================================= -->
    <!-- 4. SECTION: LIVE EVA ACTIVITY (JOURNEY TIMELINE)             -->
    <!-- ============================================================= -->
    <section class="eva-activity-wrapper" id="activity">
        <div class="eva-container">
            <div class="activity-card-container">
                <div class="eva-section-header" style="margin-bottom: 32px;">
                    <span class="eva-section-tag">
                        <svg class="eva-icon" viewBox="0 0 24 24" style="width:14px;height:14px;"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/><polyline points="12 6 12 12 16 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/></svg>
                        Journal & Stream
                    </span>
                    <h2 class="eva-section-title">Your journey with EVA</h2>
                    <p class="eva-section-subtitle">
                        Everything EVA helped you experience, understand and remember.
                    </p>
                </div>

                <div class="activity-header-bar">
                    <div class="filter-pills-row">
                        <button class="filter-pill active" onclick="filterTimeline('all', this)">All</button>
                        <button class="filter-pill" onclick="filterTimeline('voice', this)">Voice</button>
                        <button class="filter-pill" onclick="filterTimeline('vision', this)">Vision</button>
                        <button class="filter-pill" onclick="filterTimeline('context', this)">Context</button>
                        <button class="filter-pill" onclick="filterTimeline('system', this)">System</button>
                    </div>

                    <button class="eva-btn-secondary" style="padding: 8px 18px; font-size: 13px;" onclick="fetchLatestEvents()">
                        <svg class="eva-icon" viewBox="0 0 24 24" style="width:14px;height:14px;"><path d="M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                        Sync Activity
                    </button>
                </div>

                <div class="timeline-stream" id="timeline-events-container">
                    <!-- Dynamic timeline rows -->
                    <div class="timeline-item" data-category="voice">
                        <div class="timeline-icon-node">
                            <svg class="eva-icon" viewBox="0 0 24 24"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" fill="currentColor"/></svg>
                        </div>
                        <div class="timeline-content-card">
                            <div class="timeline-main-info">
                                <div class="timeline-title-row">
                                    <span class="timeline-title">Voice session</span>
                                    <span class="timeline-badge">Voice</span>
                                </div>
                                <span class="timeline-detail">Asked about "robotics architecture research"</span>
                            </div>
                            <span class="timeline-time">09:12 AM</span>
                        </div>
                    </div>

                    <div class="timeline-item" data-category="context">
                        <div class="timeline-icon-node">
                            <svg class="eva-icon" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="currentColor" stroke-width="2" fill="none"/><polyline points="14 2 14 8 20 8" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                        </div>
                        <div class="timeline-content-card">
                            <div class="timeline-main-info">
                                <div class="timeline-title-row">
                                    <span class="timeline-title">Document opened</span>
                                    <span class="timeline-badge">Context</span>
                                </div>
                                <span class="timeline-detail">Robotics_architecture_v2.pdf parsed into context</span>
                            </div>
                            <span class="timeline-time">09:08 AM</span>
                        </div>
                    </div>

                    <div class="timeline-item" data-category="context">
                        <div class="timeline-icon-node">
                            <svg class="eva-icon" viewBox="0 0 24 24"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" stroke="currentColor" stroke-width="2" fill="none"/><circle cx="12" cy="10" r="3" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                        </div>
                        <div class="timeline-content-card">
                            <div class="timeline-main-info">
                                <div class="timeline-title-row">
                                    <span class="timeline-title">Location captured</span>
                                    <span class="timeline-badge">Context</span>
                                </div>
                                <span class="timeline-detail">University Innovation Center · Autumn Walkway</span>
                            </div>
                            <span class="timeline-time">08:54 AM</span>
                        </div>
                    </div>

                    <div class="timeline-item" data-category="vision">
                        <div class="timeline-icon-node">
                            <svg class="eva-icon" viewBox="0 0 24 24"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" stroke="currentColor" stroke-width="2" fill="none"/><circle cx="12" cy="13" r="4" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                        </div>
                        <div class="timeline-content-card">
                            <div class="timeline-main-info">
                                <div class="timeline-title-row">
                                    <span class="timeline-title">Camera query</span>
                                    <span class="timeline-badge">Vision</span>
                                </div>
                                <span class="timeline-detail">Identified laboratory building · Confidence 94%</span>
                            </div>
                            <span class="timeline-time">08:41 AM</span>
                        </div>
                    </div>

                    <div class="timeline-item" data-category="system">
                        <div class="timeline-icon-node">
                            <svg class="eva-icon" viewBox="0 0 24 24"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                        </div>
                        <div class="timeline-content-card">
                            <div class="timeline-main-info">
                                <div class="timeline-title-row">
                                    <span class="timeline-title">System update</span>
                                    <span class="timeline-badge">System</span>
                                </div>
                                <span class="timeline-detail">EVA Companion app synced over BLE 5.0</span>
                            </div>
                            <span class="timeline-time">08:32 AM</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- ============================================================= -->
    <!-- 5. SECTION: APP CONFIGURATION & PREFERENCES                  -->
    <!-- ============================================================= -->
    <section class="eva-section" id="configuration" style="background: var(--eva-warm-ivory);">
        <div class="eva-container">
            <div class="eva-section-header">
                <span class="eva-section-tag">
                    <svg class="eva-icon" viewBox="0 0 24 24" style="width:14px;height:14px;"><circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" fill="none"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                    Ecosystem Controls
                </span>
                <h2 class="eva-section-title">Your EVA experience</h2>
                <p class="eva-section-subtitle">
                    Configure how EVA perceives, assists, and harmonizes with your everyday flow.
                </p>
            </div>

            <div class="eva-config-grid" style="grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));">
                <!-- Cloud & Gemini AI Setup Card -->
                <div class="config-glass-card" style="border: 1px solid var(--eva-primary-green);">
                    <div class="config-card-header">
                        <div class="config-title-group">
                            <div class="config-icon-badge" style="background: var(--eva-mist-green); color: var(--eva-deep-green);">
                                <svg class="eva-icon" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                            </div>
                            <div>
                                <div class="config-title">Google Gemini & Cloud AI</div>
                                <div class="config-subtitle">Primary reasoning & vision engine</div>
                            </div>
                        </div>
                        <span class="eva-status-pill" id="card-gemini-status" style="font-size: 11px; padding: 4px 10px;">
                            <span class="status-dot-pulse"></span> Active
                        </span>
                    </div>
                    <div style="display:flex; flex-direction:column; gap:10px; margin-top:8px;">
                        <input type="password" id="gemini-key-input-card" class="cloud-input-field" placeholder="Paste Gemini API Key (AIzaSy...)" style="font-size:12px; padding:8px 12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; gap:8px;">
                            <select id="gemini-model-select-card" class="cloud-input-field" style="font-size:12px; padding:6px 10px; width:65%;">
                                <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
                                <option value="gemini-flash-lite-latest">Gemini Flash Lite</option>
                                <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
                                <option value="deepseek-chat">DeepSeek Chat</option>
                            </select>
                            <button class="cloud-btn-action" style="padding:6px 14px; font-size:12px;" onclick="saveGeminiKeyCard()">
                                Connect
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Book of Yash Personal Memory Card -->
                <div class="config-glass-card">
                    <div class="config-card-header">
                        <div class="config-title-group">
                            <div class="config-icon-badge">
                                <svg class="eva-icon" viewBox="0 0 24 24"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" stroke="currentColor" stroke-width="2" fill="none"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                            </div>
                            <div>
                                <div class="config-title">Book of Yash (Memory Engine)</div>
                                <div class="config-subtitle">Long-term personal continuity & FTS5</div>
                            </div>
                        </div>
                        <button class="eva-btn-secondary" style="font-size:11px; padding:4px 10px;" onclick="openConsole('memory')">
                            Inspect
                        </button>
                    </div>
                    <div class="config-options-list">
                        <div class="config-option-row"><span>Core Identity Card</span><span class="config-option-val">≤300 Tokens (Loaded)</span></div>
                        <div class="config-option-row"><span>Epistemic Tags</span><span class="config-option-val">[SAID], [DID], [PREF]</span></div>
                        <div class="config-option-row"><span>Sensitivity Tiers</span><span class="config-option-val">S0 - S4 Gated</span></div>
                    </div>
                </div>

                <!-- Voice Settings -->
                <div class="config-glass-card">
                    <div class="config-card-header">
                        <div class="config-title-group">
                            <div class="config-icon-badge">
                                <svg class="eva-icon" viewBox="0 0 24 24"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" fill="currentColor"/></svg>
                            </div>
                            <div>
                                <div class="config-title">Voice & Wake Word</div>
                                <div class="config-subtitle">Acoustic interaction engine</div>
                            </div>
                        </div>
                        <div class="config-toggle-switch active" onclick="this.classList.toggle('active')">
                            <div class="config-toggle-handle"></div>
                        </div>
                    </div>
                    <div class="config-options-list">
                        <div class="config-option-row"><span>Primary Wake Word</span><span class="config-option-val">"Hey EVA"</span></div>
                        <div class="config-option-row"><span>Language Detection</span><span class="config-option-val">Auto (EN / HI)</span></div>
                        <div class="config-option-row"><span>Whisper Response</span><span class="config-option-val">Enabled</span></div>
                    </div>
                </div>

                <!-- Vision & Camera -->
                <div class="config-glass-card">
                    <div class="config-card-header">
                        <div class="config-title-group">
                            <div class="config-icon-badge">
                                <svg class="eva-icon" viewBox="0 0 24 24"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" stroke="currentColor" stroke-width="2" fill="none"/><circle cx="12" cy="13" r="4" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                            </div>
                            <div>
                                <div class="config-title">Vision & Camera</div>
                                <div class="config-subtitle">XIAO ESP32-S3 Sense capture</div>
                            </div>
                        </div>
                        <div class="config-toggle-switch active" onclick="this.classList.toggle('active')">
                            <div class="config-toggle-handle"></div>
                        </div>
                    </div>
                    <div class="config-options-list">
                        <div class="config-option-row"><span>Resolution</span><span class="config-option-val">640x480 RGB</span></div>
                        <div class="config-option-row"><span>Auto Scene Trigger</span><span class="config-option-val">Button Press</span></div>
                        <div class="config-option-row"><span>Optical Privacy Ring</span><span class="config-option-val">Hardware LED Active</span></div>
                    </div>
                </div>

                <!-- GitHub Autonomous Developer Agent -->
                <div class="config-glass-card">
                    <div class="config-card-header">
                        <div class="config-title-group">
                            <div class="config-icon-badge" style="background: rgba(17, 19, 17, 0.08); color: var(--eva-primary-black);">
                                <svg class="eva-icon" viewBox="0 0 24 24"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>
                            </div>
                            <div>
                                <div class="config-title">GitHub Autonomous Agent</div>
                                <div class="config-subtitle">Repo exploration & commit timeline</div>
                            </div>
                        </div>
                        <button class="eva-btn-secondary" style="font-size:11px; padding:4px 10px;" onclick="openConsole('github')">
                            Studio
                        </button>
                    </div>
                    <div class="config-options-list">
                        <div class="config-option-row"><span>Authenticated Account</span><span class="config-option-val">yashanandingole12-gif</span></div>
                        <div class="config-option-row"><span>Repository Scope</span><span class="config-option-val">All Repos + Commits</span></div>
                        <div class="config-option-row"><span>API Rate Limit</span><span class="config-option-val">5,000 / hr (PAT)</span></div>
                    </div>
                </div>

                <!-- God's Eye Transit & Spatial Map -->
                <div class="config-glass-card">
                    <div class="config-card-header">
                        <div class="config-title-group">
                            <div class="config-icon-badge" style="background: var(--eva-pale-green); color: var(--eva-deep-green);">
                                <svg class="eva-icon" viewBox="0 0 24 24"><path d="M12 2a8 8 0 0 0-8 8c0 5.25 8 12 8 12s8-6.75 8-12a8 8 0 0 0-8-8z" stroke="currentColor" stroke-width="2" fill="none"/><circle cx="12" cy="10" r="3" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                            </div>
                            <div>
                                <div class="config-title">God's Eye Transit Core</div>
                                <div class="config-subtitle">Real-time multimodal mobility</div>
                            </div>
                        </div>
                        <button class="eva-btn-secondary" style="font-size:11px; padding:4px 10px;" onclick="openConsole('transit')">
                            Explore
                        </button>
                    </div>
                    <div class="config-options-list">
                        <div class="config-option-row"><span>Traffic Congestion Engine</span><span class="config-option-val">Live Real-time</span></div>
                        <div class="config-option-row"><span>Metro & Rail Schedules</span><span class="config-option-val">Indian Transit</span></div>
                        <div class="config-option-row"><span>Flight Corridor Radar</span><span class="config-option-val">Terminal & Gate</span></div>
                    </div>
                </div>

                <!-- Context & Integrations -->
                <div class="config-glass-card">
                    <div class="config-card-header">
                        <div class="config-title-group">
                            <div class="config-icon-badge">
                                <svg class="eva-icon" viewBox="0 0 24 24"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" stroke="currentColor" stroke-width="2" fill="none"/><polyline points="22,6 12,13 2,6" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                            </div>
                            <div>
                                <div class="config-title">Cloud Integrations</div>
                                <div class="config-subtitle">Google Workspace & Calendar</div>
                            </div>
                        </div>
                        <div class="config-toggle-switch active" onclick="this.classList.toggle('active')">
                            <div class="config-toggle-handle"></div>
                        </div>
                    </div>
                    <div class="config-options-list">
                        <div class="config-option-row"><span>Gmail Intelligence</span><span class="config-option-val">Connected</span></div>
                        <div class="config-option-row"><span>Google Calendar</span><span class="config-option-val">Connected</span></div>
                        <div class="config-option-row"><span>Location Geofence</span><span class="config-option-val">High Precision</span></div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- ============================================================= -->
    <!-- 6. SECTION: USAGE & INSIGHTS (CALM SVG CHARTS)               -->
    <!-- ============================================================= -->
    <section class="eva-section" id="insights">
        <div class="eva-container">
            <div class="analytics-dashboard-card">
                <div class="eva-section-header" style="margin-bottom: 32px;">
                    <span class="eva-section-tag">
                        <svg class="eva-icon" viewBox="0 0 24 24" style="width:14px;height:14px;"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/></svg>
                        Quiet Telemetry
                    </span>
                    <h2 class="eva-section-title">Usage & Insights</h2>
                    <p class="eva-section-subtitle">
                        A quiet look at how you and EVA work together.
                    </p>
                </div>

                <div class="analytics-metrics-strip">
                    <div class="metric-stat-box">
                        <span class="metric-stat-value" id="stat-sessions-count">142</span>
                        <span class="metric-stat-label">Voice Queries</span>
                        <span class="metric-stat-trend">+18% this week</span>
                    </div>
                    <div class="metric-stat-box">
                        <span class="metric-stat-value" id="stat-docs-count">28</span>
                        <span class="metric-stat-label">Documents Parsed</span>
                        <span class="metric-stat-trend">Robotics & Architecture</span>
                    </div>
                    <div class="metric-stat-box">
                        <span class="metric-stat-value" id="stat-latency-val">46ms</span>
                        <span class="metric-stat-label">Average Latency</span>
                        <span class="metric-stat-trend">Edge fast cache</span>
                    </div>
                    <div class="metric-stat-box">
                        <span class="metric-stat-value">3.4h</span>
                        <span class="metric-stat-label">Daily Wear Time</span>
                        <span class="metric-stat-trend">Optimal comfort</span>
                    </div>
                </div>

                <!-- Calm Emerald Activity Wave -->
                <div class="wave-chart-container">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:13px; font-weight:700; color:var(--eva-primary-black);">Weekly Interaction Volume</span>
                        <span style="font-size:12px; font-weight:600; color:var(--eva-primary-green);">Active Flow</span>
                    </div>

                    <svg class="wave-svg" viewBox="0 0 800 120" preserveAspectRatio="none">
                        <defs>
                            <linearGradient id="waveGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                                <stop offset="0%" stop-color="#3F6B4F" stop-opacity="0.30" />
                                <stop offset="100%" stop-color="#3F6B4F" stop-opacity="0.0" />
                            </linearGradient>
                        </defs>
                        <!-- Area Fill -->
                        <path d="M 0,90 Q 130,40 260,75 T 520,35 T 800,50 L 800,120 L 0,120 Z" fill="url(#waveGradient)" />
                        <!-- Wave Line -->
                        <path d="M 0,90 Q 130,40 260,75 T 520,35 T 800,50" fill="none" stroke="#3F6B4F" stroke-width="3" stroke-linecap="round" />
                    </svg>

                    <div class="wave-axis-labels">
                        <span>Mon</span>
                        <span>Tue</span>
                        <span>Wed</span>
                        <span>Thu</span>
                        <span>Fri</span>
                        <span>Sat</span>
                        <span>Sun</span>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- ============================================================= -->
    <!-- 7. SECTION: DEVICE STATUS LAYER                              -->
    <!-- ============================================================= -->
    <section class="eva-section" id="status" style="padding-top: 0;">
        <div class="eva-container">
            <div class="eva-section-header" style="margin-bottom: 24px;">
                <span class="eva-section-tag">
                    <svg class="eva-icon" viewBox="0 0 24 24" style="width:14px;height:14px;"><rect x="2" y="2" width="20" height="8" rx="2" ry="2" stroke="currentColor" stroke-width="2" fill="none"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                    System State
                </span>
                <h2 class="eva-section-title" style="font-size: 36px;">Live Device Telemetry</h2>
            </div>

            <div class="device-status-grid">
                <div class="device-status-tile">
                    <div class="tile-header"><span class="tile-name">Glasses</span><span class="status-dot-pulse" style="width:6px;height:6px;"></span></div>
                    <div class="tile-value" id="tile-glasses-status">Connected</div>
                    <div class="tile-sub">BLE 5.0 Synced</div>
                </div>

                <div class="device-status-tile">
                    <div class="tile-header"><span class="tile-name">Companion</span><span class="status-dot-pulse" style="width:6px;height:6px;"></span></div>
                    <div class="tile-value">Online</div>
                    <div class="tile-sub">Android Bridge</div>
                </div>

                <div class="device-status-tile">
                    <div class="tile-header"><span class="tile-name">Battery</span></div>
                    <div class="tile-value" id="tile-battery-pct">84%</div>
                    <div class="tile-sub">~9.2 hrs left</div>
                </div>

                <div class="device-status-tile">
                    <div class="tile-header"><span class="tile-name">Audio</span></div>
                    <div class="tile-value">TWS Active</div>
                    <div class="tile-sub">Binaural Mode</div>
                </div>

                <div class="device-status-tile">
                    <div class="tile-header"><span class="tile-name">Sensors</span></div>
                    <div class="tile-value">Calibrated</div>
                    <div class="tile-sub">IMU + Mic + Cam</div>
                </div>

                <div class="device-status-tile">
                    <div class="tile-header"><span class="tile-name">Firmware</span></div>
                    <div class="tile-value">v2.4.0</div>
                    <div class="tile-sub">Latest Build</div>
                </div>

                <div class="device-status-tile">
                    <div class="tile-header"><span class="tile-name">Privacy</span></div>
                    <div class="tile-value">Protected</div>
                    <div class="tile-sub">Hardware Enclave</div>
                </div>
            </div>
        </div>
    </section>

    <!-- ============================================================= -->
    <!-- 8. DEVICE CONSOLE MODAL / DETAILED MANAGEMENT VIEW           -->
    <!-- ============================================================= -->
    <div class="eva-console-modal" id="device-console-modal">
        <div class="console-container">
            <div class="console-header">
                <div class="console-header-left">
                    <span class="eva-brand-tag">Operations Hub</span>
                    <h3 class="console-header-title">EVA Device Console</h3>
                </div>
                <button class="console-close-btn" onclick="closeConsole()">
                    <svg class="eva-icon" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
                </button>
            </div>

            <div class="console-body">
                <!-- Sidebar -->
                <div class="console-sidebar">
                    <div class="console-nav-item active" onclick="switchConsoleTab('overview', this)">
                        <svg class="eva-icon" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" stroke="currentColor" stroke-width="2" fill="none"/><rect x="14" y="3" width="7" height="7" stroke="currentColor" stroke-width="2" fill="none"/><rect x="14" y="14" width="7" height="7" stroke="currentColor" stroke-width="2" fill="none"/><rect x="3" y="14" width="7" height="7" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                        Overview
                    </div>
                    <div class="console-nav-item" onclick="switchConsoleTab('github', this)">
                        <svg class="eva-icon" viewBox="0 0 24 24"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>
                        GitHub Agent
                    </div>
                    <div class="console-nav-item" onclick="switchConsoleTab('memory', this)">
                        <svg class="eva-icon" viewBox="0 0 24 24"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" stroke="currentColor" stroke-width="2" fill="none"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                        Book of Yash
                    </div>
                    <div class="console-nav-item" onclick="switchConsoleTab('cloud', this)">
                        <svg class="eva-icon" viewBox="0 0 24 24"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                        Cloud & Gemini AI
                    </div>
                    <div class="console-nav-item" onclick="switchConsoleTab('transit', this)">
                        <svg class="eva-icon" viewBox="0 0 24 24"><path d="M12 2a8 8 0 0 0-8 8c0 5.25 8 12 8 12s8-6.75 8-12a8 8 0 0 0-8-8z" stroke="currentColor" stroke-width="2" fill="none"/><circle cx="12" cy="10" r="3" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                        God's Eye Transit
                    </div>
                    <div class="console-nav-item" onclick="switchConsoleTab('docs', this)">
                        <svg class="eva-icon" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="currentColor" stroke-width="2" fill="none"/><polyline points="14 2 14 8 20 8" stroke="currentColor" stroke-width="2" fill="none"/><line x1="16" y1="13" x2="8" y2="13" stroke="currentColor" stroke-width="2"/><line x1="16" y1="17" x2="8" y2="17" stroke="currentColor" stroke-width="2"/></svg>
                        Docs & Drive
                    </div>
                    <div class="console-nav-item" onclick="switchConsoleTab('contacts', this)">
                        <svg class="eva-icon" viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="2" fill="none"/><circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="2" fill="none"/><path d="M23 21v-2a4 4 0 0 0-3-3.87" stroke="currentColor" stroke-width="2" fill="none"/><path d="M16 3.13a4 4 0 0 1 0 7.75" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                        Contacts
                    </div>
                    <div class="console-nav-item" onclick="switchConsoleTab('health', this)">
                        <svg class="eva-icon" viewBox="0 0 24 24"><path d="M22 12h-4l-3 9L9 3l-3 9H2" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/></svg>
                        Device Health
                    </div>
                    <div class="console-nav-item" onclick="switchConsoleTab('firmware', this)">
                        <svg class="eva-icon" viewBox="0 0 24 24"><polygon points="12 2 2 7 12 12 22 7 12 2" stroke="currentColor" stroke-width="2" fill="none"/><polyline points="2 17 12 22 22 17" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                        Firmware & OTA
                    </div>
                    <div class="console-nav-item" onclick="switchConsoleTab('audio', this)">
                        <svg class="eva-icon" viewBox="0 0 24 24"><path d="M3 18v-6a9 9 0 0 1 18 0v6" stroke="currentColor" stroke-width="2" fill="none"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z" fill="currentColor"/></svg>
                        Audio & TWS
                    </div>
                    <div class="console-nav-item" onclick="switchConsoleTab('diagnostics', this)">
                        <svg class="eva-icon" viewBox="0 0 24 24"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                        Diagnostics
                    </div>
                </div>

                <!-- Content Panels -->
                <div class="console-content">
                    <!-- Overview Tab -->
                    <div class="console-panel active" id="tab-overview">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <h4 style="font-size:18px; font-weight:700; color:var(--eva-primary-black);">System Health Matrix</h4>
                                <p style="font-size:13px; color:var(--eva-text-muted);">Real-time Seeed Studio XIAO ESP32-S3 Sense telemetry.</p>
                            </div>
                            <span class="eva-status-pill"><span class="status-dot-pulse"></span> Operational</span>
                        </div>

                        <div class="device-status-grid">
                            <div class="device-status-tile">
                                <span class="tile-name">CPU Core</span>
                                <span class="tile-value">240 MHz</span>
                                <span class="tile-sub">Xtensa Dual Core</span>
                            </div>
                            <div class="device-status-tile">
                                <span class="tile-name">Free Heap</span>
                                <span class="tile-value">284 KB</span>
                                <span class="tile-sub">SRAM Clean</span>
                            </div>
                            <div class="device-status-tile">
                                <span class="tile-name">PSRAM</span>
                                <span class="tile-value">8 MB</span>
                                <span class="tile-sub">Frame Buffer Ready</span>
                            </div>
                            <div class="device-status-tile">
                                <span class="tile-name">BLE RSSI</span>
                                <span class="tile-value">-54 dBm</span>
                                <span class="tile-sub">Strong Connection</span>
                            </div>
                        </div>

                        <div style="background:var(--eva-pure-white); border:1px solid var(--eva-border-subtle); border-radius:var(--radius-md); padding:24px;">
                            <h5 style="font-size:14px; font-weight:700; color:var(--eva-primary-black); margin-bottom:12px;">Quick Action Dispatch</h5>
                            <div style="display:flex; gap:12px; flex-wrap:wrap;">
                                <button class="eva-btn-secondary" style="font-size:13px; padding:8px 16px;" onclick="openConsole('memory')">Inspect Book of Yash</button>
                                <button class="eva-btn-secondary" style="font-size:13px; padding:8px 16px;" onclick="openConsole('cloud')">Configure Gemini API</button>
                                <button class="eva-btn-secondary" style="font-size:13px; padding:8px 16px;" onclick="simulateSmsDemo()">Simulate Inbound SMS</button>
                                <button class="eva-btn-secondary" style="font-size:13px; padding:8px 16px;" onclick="triggerCameraCaptureDemo()">Trigger Camera Query</button>
                            </div>
                        </div>
                    </div>

                    <!-- Book of Yash & Memory Hub Tab -->
                    <div class="console-panel" id="tab-memory">
                        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                            <div>
                                <h4 style="font-size:18px; font-weight:700; color:var(--eva-primary-black);">The Book of Yash — Personal Intelligence Database</h4>
                                <p style="font-size:13px; color:var(--eva-text-muted);">Offline-first SQLite + FTS5 knowledge store with epistemic confidence & S0–S4 sensitivity gating.</p>
                            </div>
                            <button class="cloud-btn-action" style="font-size:12px; padding:6px 14px;" onclick="loadMemoriesFromStore()">
                                Refresh Memories
                            </button>
                        </div>

                        <!-- Core Identity Card (<=300 tokens) -->
                        <div style="background:var(--eva-pure-white); border:1px solid var(--eva-primary-green); border-radius:var(--radius-md); padding:18px;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                                <div style="display:flex; align-items:center; gap:8px;">
                                    <span class="eva-brand-tag" style="background:var(--eva-pale-green); color:var(--eva-deep-green);">Always-Loaded</span>
                                    <strong style="font-size:13px; color:var(--eva-primary-black);">Core Identity Card</strong>
                                </div>
                                <span id="core-card-tokens-badge" style="font-size:11px; font-family:var(--font-mono); color:var(--eva-deep-green); font-weight:700;">~160 Tokens (≤300 Limit)</span>
                            </div>
                            <pre id="core-identity-display" style="white-space:pre-wrap; font-family:var(--font-sans); font-size:12px; color:var(--eva-text-body); background:var(--eva-ivory); padding:12px; border-radius:var(--radius-sm); border:1px solid var(--eva-border-subtle); line-height:1.5;">Loading Core Identity Card...</pre>
                        </div>

                        <!-- Memory Search & Filter -->
                        <div style="display:flex; flex-direction:column; gap:12px;">
                            <div style="display:flex; gap:10px; flex-wrap:wrap;">
                                <input type="text" id="memory-search-input" class="cloud-input-field" placeholder="Search memories (e.g., 'delta robot', 'career', 'boxing', 'education')..." onkeyup="handleMemorySearchInput(event)" style="flex:1;">
                                <select id="memory-cat-filter" class="cloud-input-field" style="width:160px;" onchange="loadMemoriesFromStore()">
                                    <option value="">All Categories</option>
                                    <option value="identity">Identity</option>
                                    <option value="education">Education</option>
                                    <option value="career">Career</option>
                                    <option value="project">Projects</option>
                                    <option value="personality">Personality</option>
                                    <option value="emotional">Emotional</option>
                                    <option value="technical">Technical</option>
                                    <option value="health">Health</option>
                                </select>
                                <button class="cloud-btn-action" onclick="loadMemoriesFromStore()">Search</button>
                            </div>

                            <!-- Memory items list container -->
                            <div class="memory-card-list" id="memories-container">
                                <div style="text-align:center; padding:24px; color:var(--eva-text-muted); font-size:13px;">Loading memories...</div>
                            </div>
                        </div>

                        <!-- Add / Evolve Preference Simulator -->
                        <div style="background:var(--eva-pure-white); border:1px solid var(--eva-border-subtle); border-radius:var(--radius-md); padding:18px;">
                            <h5 style="font-size:14px; font-weight:700; color:var(--eva-primary-black); margin-bottom:8px;">Test Preference Evolution & Contradiction Resolver</h5>
                            <p style="font-size:12px; color:var(--eva-text-muted); margin-bottom:10px;">Enter a new statement to test automatic evolution without deleting historical context.</p>
                            <div style="display:flex; gap:10px;">
                                <input type="text" id="evolve-statement-input" class="cloud-input-field" placeholder="e.g. Wants to focus exclusively on AI Robotics and Autonomy R&D.">
                                <button class="cloud-btn-action" style="white-space:nowrap;" onclick="submitEvolveMemory()">Evolve Memory</button>
                            </div>
                            <div id="evolve-result-box" style="margin-top:10px; font-size:12px; display:none; padding:8px 12px; border-radius:6px;"></div>
                        </div>
                    </div>

                    <!-- Cloud & Gemini AI Configuration Tab -->
                    <div class="console-panel" id="tab-cloud">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <h4 style="font-size:18px; font-weight:700; color:var(--eva-primary-black);">Cloud & Google Gemini AI Setup</h4>
                                <p style="font-size:13px; color:var(--eva-text-muted);">Configure Google Gemini AI Studio API key, primary model routing, and cloud fallbacks.</p>
                            </div>
                            <span class="eva-status-pill" id="cloud-modal-status-pill"><span class="status-dot-pulse"></span> Configured</span>
                        </div>

                        <div style="background:var(--eva-pure-white); border:1px solid var(--eva-border-subtle); border-radius:var(--radius-md); padding:24px; display:flex; flex-direction:column; gap:16px;">
                            <div>
                                <label style="display:block; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:var(--eva-text-light); margin-bottom:6px;">Google Gemini API Key</label>
                                <div style="display:flex; gap:10px;">
                                    <input type="password" id="gemini-api-key-modal-input" class="cloud-input-field" placeholder="AIzaSy...">
                                    <button class="eva-btn-secondary" style="font-size:12px; padding:6px 12px;" onclick="togglePasswordVisibility('gemini-api-key-modal-input')">Show</button>
                                </div>
                                <span style="font-size:11px; color:var(--eva-text-muted); margin-top:4px; display:block;">Get your API key from <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color:var(--eva-primary-green); font-weight:600;">Google AI Studio</a>.</span>
                            </div>

                            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
                                <div>
                                    <label style="display:block; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:var(--eva-text-light); margin-bottom:6px;">Primary Model</label>
                                    <select id="primary-model-modal-select" class="cloud-input-field">
                                        <option value="gemini-2.5-flash">Gemini 2.5 Flash (Recommended)</option>
                                        <option value="gemini-flash-lite-latest">Gemini Flash Lite (Ultra Low Latency)</option>
                                        <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
                                        <option value="deepseek-chat">DeepSeek Chat</option>
                                    </select>
                                </div>
                                <div>
                                    <label style="display:block; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:var(--eva-text-light); margin-bottom:6px;">Secondary Cloud Fallback</label>
                                    <select id="secondary-provider-modal-select" class="cloud-input-field">
                                        <option value="deepseek">DeepSeek (Cloud Fallback)</option>
                                        <option value="none">None (Local Fallback Only)</option>
                                    </select>
                                </div>
                            </div>

                            <div>
                                <label style="display:block; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:var(--eva-text-light); margin-bottom:6px;">DeepSeek API Key (Optional Fallback)</label>
                                <input type="password" id="deepseek-api-key-modal-input" class="cloud-input-field" placeholder="sk-...">
                            </div>

                            <div style="display:flex; justify-content:space-between; align-items:center; pt:8px;">
                                <button class="cloud-btn-action" style="padding:10px 24px;" onclick="saveCloudConfigurationModal()">
                                    <svg class="eva-icon" viewBox="0 0 24 24" style="width:16px;height:16px;"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" stroke="currentColor" stroke-width="2" fill="none"/><polyline points="17 21 17 13 7 13 7 21" stroke="currentColor" stroke-width="2" fill="none"/><polyline points="7 3 7 8 15 8" stroke="currentColor" stroke-width="2" fill="none"/></svg>
                                    Verify & Save Configuration
                                </button>
                                <span id="cloud-save-feedback" style="font-size:12px; font-weight:600; color:var(--eva-primary-green);"></span>
                            </div>

                            <div id="cloud-validation-box" style="display:none; font-size:12px; padding:12px; border-radius:var(--radius-sm); line-height:1.5;"></div>
                        </div>
                    </div>

                    <!-- GitHub Agent Studio Tab -->
                    <div class="console-panel" id="tab-github">
                        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                            <div>
                                <h4 style="font-size:18px; font-weight:700; color:var(--eva-primary-black);">GitHub Agent Studio</h4>
                                <p style="font-size:13px; color:var(--eva-text-muted);">Autonomous repository explorer, commit timeline, issue inspector, and pull request tracker.</p>
                            </div>
                            <button class="cloud-btn-action" style="font-size:12px; padding:6px 14px;" onclick="loadGitHubData()">
                                Sync Repositories
                            </button>
                        </div>

                        <!-- Authenticated User Profile Summary -->
                        <div id="github-user-profile-card" style="background:var(--eva-pure-white); border:1px solid var(--eva-primary-green); border-radius:var(--radius-md); padding:18px; display:flex; align-items:center; justify-content:space-between; gap:16px;">
                            <div style="display:flex; align-items:center; gap:16px;">
                                <img id="gh-user-avatar" src="https://avatars.githubusercontent.com/u/227339293?v=4" style="width:48px; height:48px; border-radius:50%; border:2px solid var(--eva-primary-green);" alt="Avatar">
                                <div>
                                    <div style="display:flex; align-items:center; gap:8px;">
                                        <strong id="gh-user-login" style="font-size:15px; color:var(--eva-primary-black);">yashanandingole12-gif</strong>
                                        <span class="eva-brand-tag" style="background:var(--eva-pale-green); color:var(--eva-deep-green);">PAT Authenticated</span>
                                    </div>
                                    <div id="gh-user-bio" style="font-size:12px; color:var(--eva-text-muted);">EVA Smart Glasses Personal AI Developer</div>
                                </div>
                            </div>
                            <div style="display:flex; gap:16px; font-size:12px; text-align:right;">
                                <div><strong id="gh-public-repos-count" style="font-size:16px; color:var(--eva-deep-green);">7+</strong><div style="color:var(--eva-text-muted);">Repositories</div></div>
                                <div><strong id="gh-rate-limit" style="font-size:16px; color:var(--eva-deep-green);">5,000</strong><div style="color:var(--eva-text-muted);">Req/Hour</div></div>
                            </div>
                        </div>

                        <!-- Repository Search and Quick Inspect -->
                        <div style="display:flex; gap:10px;">
                            <input type="text" id="github-search-input" class="cloud-input-field" placeholder="Search GitHub repos (e.g. 'smart-glasses-ai', 'robotics', 'FashionMNIST')..." onkeyup="if(event.key==='Enter') searchGitHubRepos()" style="flex:1;">
                            <button class="cloud-btn-action" onclick="searchGitHubRepos()">Search</button>
                        </div>

                        <!-- Repositories Grid Container -->
                        <div id="github-repos-container" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:14px;">
                            <div style="text-align:center; padding:24px; color:var(--eva-text-muted); font-size:13px;">Loading repositories...</div>
                        </div>

                        <!-- Recent Commits Inspector -->
                        <div style="background:var(--eva-pure-white); border:1px solid var(--eva-border-subtle); border-radius:var(--radius-md); padding:18px;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                                <h5 style="font-size:14px; font-weight:700; color:var(--eva-primary-black);">Recent Commits on <code>smart-glasses-ai</code></h5>
                                <button class="eva-btn-secondary" style="font-size:11px; padding:4px 10px;" onclick="loadGitHubCommits('smart-glasses-ai')">Refresh Commits</button>
                            </div>
                            <div id="github-commits-container" style="display:flex; flex-direction:column; gap:8px;">
                                <div style="color:var(--eva-text-muted); font-size:12px;">Loading recent commits...</div>
                            </div>
                        </div>
                    </div>

                    <!-- God's Eye Live Transit & Google Live Earth 3D Tab -->
                    <div class="console-panel" id="tab-transit">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <h4 style="font-size:18px; font-weight:700; color:var(--eva-primary-black);">God's Eye Spatial & Google Live Earth 3D</h4>
                                <p style="font-size:13px; color:var(--eva-text-muted);">Real-time satellite navigation across Nagpur Maha Metro, Indian Railways, Wardha Road corridor, and global 3D Earth terrain.</p>
                            </div>
                            <span class="eva-status-pill"><span class="status-dot-pulse"></span> Orbit Active</span>
                        </div>

                        <!-- Google Live Earth 3D Quick Action Banner -->
                        <div style="background:linear-gradient(135deg, var(--eva-deep-green), var(--eva-primary-green)); border-radius:var(--radius-md); padding:16px 20px; color:white; display:flex; justify-content:space-between; align-items:center; box-shadow:var(--glass-shadow);">
                            <div>
                                <div style="font-size:15px; font-weight:700; letter-spacing:0.5px; display:flex; align-items:center; gap:8px;">
                                    <span style="display:inline-flex; align-items:center; gap:6px;"><span class="status-dot-pulse" style="background:#fff;"></span> Google Live Earth 3D Navigation</span>
                                    <span style="font-size:10px; background:rgba(255,255,255,0.2); padding:2px 8px; border-radius:99px;">Nagpur Zero Mile Base</span>
                                </div>
                                <div style="font-size:12px; opacity:0.9; margin-top:4px;">Photorealistic 3D terrain, orbital spatial perspective & live turn-by-turn HUD routing.</div>
                            </div>
                            <div style="display:flex; gap:10px;">
                                <a id="btn-open-google-earth" href="https://earth.google.com/web/@21.1458,79.0882,312a,950d,35y,0h,45t,0r" target="_blank" class="eva-btn-primary" style="font-size:12px; padding:8px 14px; background:white; color:var(--eva-deep-green); border:none; text-decoration:none;">
                                    Open Google Earth 3D
                                </a>
                                <a id="btn-open-google-maps" href="https://www.google.com/maps/dir/?api=1&destination=21.1458,79.0882" target="_blank" class="eva-btn-secondary" style="font-size:12px; padding:8px 14px; background:rgba(255,255,255,0.15); color:white; border:1px solid rgba(255,255,255,0.4); text-decoration:none;">
                                    Google Maps Nav
                                </a>
                            </div>
                        </div>

                        <!-- Nagpur 3D Spatial Landmarks Quick-Teleport Bar -->
                        <div style="display:flex; gap:8px; overflow-x:auto; padding-bottom:4px;">
                            <button class="filter-pill active" onclick="teleportGodEyePOI('Sitabuldi Interchange', 21.1458, 79.0832)">Sitabuldi Metro</button>
                            <button class="filter-pill" onclick="teleportGodEyePOI('Zero Mile Stone', 21.1478, 79.0883)">Zero Mile Stone</button>
                            <button class="filter-pill" onclick="teleportGodEyePOI('Nagpur Junction NGP', 21.1524, 79.0889)">Nagpur Junction</button>
                            <button class="filter-pill" onclick="teleportGodEyePOI('Dr. Babasaheb Ambedkar Airport NAG', 21.0922, 79.0472)">Nagpur Airport NAG</button>
                            <button class="filter-pill" onclick="teleportGodEyePOI('Futala Lake Waterfront', 21.1558, 79.0435)">Futala Lake</button>
                            <button class="filter-pill" onclick="teleportGodEyePOI('Samruddhi Mahamarg Zero Point', 21.1350, 79.0120)">Samruddhi Expressway</button>
                        </div>

                        <div style="display:flex; gap:10px;">
                            <input type="text" id="transit-query-input" class="cloud-input-field" placeholder="Ask transit (e.g. 'metro to Sitabuldi', 'traffic on Wardha Road', 'Vande Bharat to Bilaspur', 'Nagpur flight 6E412')..." onkeyup="if(event.key==='Enter') queryTransitGodEye()" style="flex:1;">
                            <button class="cloud-btn-action" onclick="queryTransitGodEye()">Ask God's Eye</button>
                        </div>

                        <div id="transit-result-card" style="display:none; background:var(--eva-pure-white); border:1px solid var(--eva-primary-green); border-radius:var(--radius-md); padding:18px;">
                            <div id="transit-result-summary" style="font-size:14px; font-weight:600; color:var(--eva-primary-black); margin-bottom:10px;"></div>
                            <pre id="transit-result-raw" style="font-family:var(--font-mono); font-size:11px; background:var(--eva-ivory); padding:12px; border-radius:var(--radius-xs); max-height:160px; overflow-y:auto; color:var(--eva-text-body);"></pre>
                        </div>

                        <div class="device-status-grid">
                            <div class="device-status-tile" style="cursor:pointer;" onclick="quickTransitQuery('traffic on Wardha Road')">
                                <span class="tile-name">Wardha Expressway</span>
                                <span class="tile-value">Clear Flow</span>
                                <span class="tile-sub">58 km/h · +0 min delay</span>
                            </div>
                            <div class="device-status-tile" style="cursor:pointer;" onclick="quickTransitQuery('Sitabuldi metro')">
                                <span class="tile-name">Maha Metro Nagpur</span>
                                <span class="tile-value">Sitabuldi Interchange</span>
                                <span class="tile-sub">Aqua/Orange · 2 min arr</span>
                            </div>
                            <div class="device-status-tile" style="cursor:pointer;" onclick="quickTransitQuery('Vande Bharat train')">
                                <span class="tile-name">Nagpur Junction (NGP)</span>
                                <span class="tile-value">Vande Bharat 20826</span>
                                <span class="tile-sub">Plat 1 · 14:05 Dep</span>
                            </div>
                            <div class="device-status-tile" style="cursor:pointer;" onclick="quickTransitQuery('Nagpur flight 6E412')">
                                <span class="tile-name">Nagpur Airport (NAG)</span>
                                <span class="tile-value">6E-412 (BOM)</span>
                                <span class="tile-sub">Terminal 1 · Gate 3</span>
                            </div>
                        </div>
                    </div>

                    <!-- Health Tab -->
                    <div class="console-panel" id="tab-health">
                        <h4 style="font-size:18px; font-weight:700; color:var(--eva-primary-black);">Subsystem Diagnostics</h4>
                        <div class="config-options-list">
                            <div class="config-option-row"><span>OV2640 Image Sensor</span><span class="config-option-val">READY (640x480)</span></div>
                            <div class="config-option-row"><span>PDM Microphone array</span><span class="config-option-val">READY (16,000 Hz)</span></div>
                            <div class="config-option-row"><span>Battery Monitor</span><span class="config-option-val">84% · 3.98V</span></div>
                            <div class="config-option-row"><span>Hardware Enclave Security</span><span class="config-option-val">Enforced</span></div>
                        </div>
                    </div>

                    <!-- Firmware Tab -->
                    <div class="console-panel" id="tab-firmware">
                        <h4 style="font-size:18px; font-weight:700; color:var(--eva-primary-black);">Firmware & OTA Updates</h4>
                        <div style="background:var(--eva-pure-white); border:1px solid var(--eva-border-subtle); border-radius:var(--radius-md); padding:24px; display:flex; flex-direction:column; gap:12px;">
                            <div style="display:flex; justify-content:space-between;">
                                <div>
                                    <div style="font-weight:700;">Installed Version: v2.4.0-stable</div>
                                    <div style="font-size:12px; color:var(--eva-text-muted);">Compiled for ESP32-S3 with BLE Talk Protocol</div>
                                </div>
                                <span class="eva-brand-tag">Up to Date</span>
                            </div>
                            <p style="font-size:13px; color:var(--eva-text-muted);">Automatic OTA checks occur in background during wireless charging dock docking.</p>
                        </div>
                    </div>

                    <!-- Audio Tab -->
                    <div class="console-panel" id="tab-audio">
                        <h4 style="font-size:18px; font-weight:700; color:var(--eva-primary-black);">Audio Routing & Volume</h4>
                        <div class="config-options-list">
                            <div class="config-option-row"><span>Active Route</span><span class="config-option-val">True Wireless Stereo (TWS)</span></div>
                            <div class="config-option-row"><span>Acoustic Echo Cancellation</span><span class="config-option-val">Enabled</span></div>
                            <div class="config-option-row"><span>TTS Speech Synthesis Rate</span><span class="config-option-val">1.05x Natural</span></div>
                        </div>
                    </div>

                    <!-- Diagnostics Tab -->
                    <div class="console-panel" id="tab-diagnostics">
                        <h4 style="font-size:18px; font-weight:700; color:var(--eva-primary-black);">Live System Check</h4>
                        <div id="diagnostics-output-box" style="background:#111311; color:#DDE9DF; font-family:var(--font-mono); font-size:12px; padding:20px; border-radius:var(--radius-sm); max-height:220px; overflow-y:auto; line-height:1.7;">
                            [INIT] EVA Diagnostics Core v2.4.0<br>
                            [OK] Hardware Bridge: Active (FastAPI loopback)<br>
                            [OK] Camera Pipeline: Ready<br>
                            [OK] Microphone Interface: PDM 16kHz Ready<br>
                            [OK] Memory Engine: Book of Yash FTS5 Active<br>
                            [OK] Cloud Latency: 44ms (Google Gemini)<br>
                            [READY] All systems operational.
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- ============================================================= -->
    <!-- 9. FOOTER — CALM EVENING / SUNSET HORIZON                    -->
    <!-- ============================================================= -->
    <footer class="eva-footer-section">
        <div class="eva-footer-tint"></div>

        <div class="eva-footer-container">
            <div class="footer-hero-text">
                <h2 class="footer-headline">A more present you.</h2>
                <p class="footer-sub">Subtle. Intelligent. Always there.</p>
            </div>

            <div class="footer-nav-grid">
                <div>
                    <a href="#" class="eva-brand" style="color:var(--eva-pure-white); margin-bottom:12px;">
                        EVA
                    </a>
                    <p style="font-size:13px; color:rgba(255,255,255,0.7); max-width:280px;">
                        Bringing ambient spatial intelligence into the physical world you already live in.
                    </p>
                </div>

                <div>
                    <div class="footer-col-title">Product</div>
                    <ul class="footer-links">
                        <li><a href="#hero">Overview</a></li>
                        <li><a href="#experience">Experience</a></li>
                        <li><a href="#activity">Activity Stream</a></li>
                        <li><a href="#insights">Insights</a></li>
                    </ul>
                </div>

                <div>
                    <div class="footer-col-title">Technology</div>
                    <ul class="footer-links">
                        <li><a href="#configuration">Intelligence Core</a></li>
                        <li><a href="#status">Telemetry</a></li>
                        <li><a href="javascript:void(0)" onclick="openConsole('overview')">Device Console</a></li>
                        <li><a href="javascript:void(0)" onclick="openConsole('diagnostics')">Diagnostics</a></li>
                    </ul>
                </div>

                <div>
                    <div class="footer-col-title">Privacy & Cloud</div>
                    <ul class="footer-links">
                        <li><a href="#configuration">Data Isolation</a></li>
                        <li><a href="#configuration">Encrypted Vectors</a></li>
                        <li><a href="#configuration">AWS Architecture</a></li>
                    </ul>
                </div>
            </div>

            <div class="footer-bottom-bar">
                <span>&copy; 2026 EVA Intelligence Systems. All rights reserved.</span>
                <span>Designed for natural presence.</span>
            </div>
        </div>
    </footer>

    <!-- ============================================================= -->
    <!-- JAVASCRIPT: LIVE TELEMETRY & CONTROLS                        -->
    <!-- ============================================================= -->
    <script>
        // Real-time clock
        function updateLiveClock() {
            const now = new Date();
            const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            const clockEl = document.getElementById('hero-live-clock');
            if (clockEl) clockEl.textContent = timeStr;
        }
        setInterval(updateLiveClock, 1000);
        updateLiveClock();

        // Console Modal Handling
        function openConsole(tabName) {
            const modal = document.getElementById('device-console-modal');
            if (modal) {
                modal.classList.add('active');
                if (tabName) {
                    const navItems = document.querySelectorAll('.console-nav-item');
                    navItems.forEach(item => {
                        if (item.textContent.toLowerCase().includes(tabName.toLowerCase())) {
                            switchConsoleTab(tabName, item);
                        }
                    });
                }
            }
        }

        function closeConsole() {
            const modal = document.getElementById('device-console-modal');
            if (modal) modal.classList.remove('active');
        }

        function switchConsoleTab(tabId, el) {
            document.querySelectorAll('.console-nav-item').forEach(i => i.classList.remove('active'));
            if (el) el.classList.add('active');

            document.querySelectorAll('.console-panel').forEach(p => p.classList.remove('active'));
            const target = document.getElementById('tab-' + tabId);
            if (target) target.classList.add('active');

            if (tabId === 'memory') {
                loadCoreIdentityCard();
                loadMemoriesFromStore();
            } else if (tabId === 'cloud') {
                loadLlmConfig();
            } else if (tabId === 'github') {
                loadGitHubData();
            }
        }

        function togglePasswordVisibility(fieldId) {
            const input = document.getElementById(fieldId);
            if (input) {
                input.type = input.type === 'password' ? 'text' : 'password';
            }
        }

        // =====================================================================
        // CLOUD & GEMINI API INTERACTIVE CONTROLS
        // =====================================================================
        async function loadLlmConfig() {
            try {
                const res = await fetch('/api/v1/config/llm');
                if (res.ok) {
                    const data = await res.json();
                    const cardInput = document.getElementById('gemini-key-input-card');
                    const modalInput = document.getElementById('gemini-api-key-modal-input');
                    const cardModel = document.getElementById('gemini-model-select-card');
                    const modalModel = document.getElementById('primary-model-modal-select');
                    const cardPill = document.getElementById('card-gemini-status');
                    const modalPill = document.getElementById('cloud-modal-status-pill');

                    if (data.gemini_configured) {
                        if (cardInput && !cardInput.value) cardInput.placeholder = `Gemini (${data.gemini_key_preview})`;
                        if (modalInput && !modalInput.value) modalInput.placeholder = `Configured (${data.gemini_key_preview})`;
                        if (cardPill) cardPill.innerHTML = '<span class="status-dot-pulse"></span> Active';
                        if (modalPill) modalPill.innerHTML = '<span class="status-dot-pulse"></span> Connected';
                    } else {
                        if (cardPill) cardPill.innerHTML = '<span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:#B38F00;margin-right:4px;"></span> Fallback Ready';
                        if (modalPill) modalPill.innerHTML = '<span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:#B38F00;margin-right:4px;"></span> Not Configured';
                    }

                    if (cardModel && data.primary_model) cardModel.value = data.primary_model;
                    if (modalModel && data.primary_model) modalModel.value = data.primary_model;
                }
            } catch (e) {
                console.debug('LLM config check:', e);
            }
        }

        async function saveGeminiKeyCard() {
            const key = document.getElementById('gemini-key-input-card')?.value?.trim();
            const model = document.getElementById('gemini-model-select-card')?.value;
            if (!key) {
                alert("Please enter a valid Google Gemini API Key.");
                return;
            }

            try {
                const res = await fetch('/api/v1/config/llm', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        gemini_api_key: key,
                        gemini_model: model,
                        primary_provider: 'gemini',
                        primary_model: model
                    })
                });
                const data = await res.json();
                if (data.validation && data.validation.valid) {
                    alert("Google Gemini API Connected! " + (data.validation.message || ""));
                    loadLlmConfig();
                } else {
                    alert("Verification Warning: " + (data.validation?.message || "Check your API key."));
                }
            } catch (err) {
                alert("Failed to save Gemini key: " + err);
            }
        }

        async function saveCloudConfigurationModal() {
            const geminiKey = document.getElementById('gemini-api-key-modal-input')?.value?.trim();
            const primaryModel = document.getElementById('primary-model-modal-select')?.value;
            const secondaryProvider = document.getElementById('secondary-provider-modal-select')?.value;
            const deepseekKey = document.getElementById('deepseek-api-key-modal-input')?.value?.trim();
            const feedback = document.getElementById('cloud-save-feedback');
            const valBox = document.getElementById('cloud-validation-box');

            if (feedback) feedback.textContent = "Verifying with Google...";

            try {
                const res = await fetch('/api/v1/config/llm', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        gemini_api_key: geminiKey,
                        gemini_model: primaryModel,
                        primary_model: primaryModel,
                        primary_provider: 'gemini',
                        secondary_provider: secondaryProvider,
                        deepseek_api_key: deepseekKey
                    })
                });
                const data = await res.json();
                if (feedback) feedback.textContent = "Saved!";
                setTimeout(() => { if (feedback) feedback.textContent = ""; }, 4000);

                if (valBox) {
                    valBox.style.display = 'block';
                    if (data.validation && data.validation.valid) {
                        valBox.style.background = 'var(--eva-mist-green)';
                        valBox.style.color = 'var(--eva-deep-green)';
                        valBox.style.border = '1px solid var(--eva-pale-green)';
                        valBox.innerHTML = `<strong>Connected:</strong> ${data.validation.message}`;
                    } else {
                        valBox.style.background = '#FDE8E8';
                        valBox.style.color = '#B32400';
                        valBox.style.border = '1px solid #F8B4B4';
                        valBox.innerHTML = `<strong>Validation Error:</strong> ${data.validation?.message}`;
                    }
                }
                loadLlmConfig();
            } catch (err) {
                if (feedback) feedback.textContent = "Error saving";
                if (valBox) {
                    valBox.style.display = 'block';
                    valBox.style.background = '#FDE8E8';
                    valBox.style.color = '#B32400';
                    valBox.innerHTML = `Network error: ${err}`;
                }
            }
        }

        // =====================================================================
        // BOOK OF YASH & PERSONAL MEMORY HUB CONTROLS
        // =====================================================================
        async function loadCoreIdentityCard() {
            try {
                const res = await fetch('/api/v1/memory/core-identity');
                if (res.ok) {
                    const data = await res.json();
                    const cardEl = document.getElementById('core-identity-display');
                    const tokensEl = document.getElementById('core-card-tokens-badge');
                    if (cardEl && data.core_identity_card) {
                        cardEl.textContent = data.core_identity_card;
                    }
                    if (tokensEl && data.token_estimate) {
                        tokensEl.textContent = `~${data.token_estimate} Tokens (≤300 Limit)`;
                    }
                }
            } catch (e) {
                console.debug('Core identity load:', e);
            }
        }

        function handleMemorySearchInput(e) {
            if (e.key === 'Enter') {
                loadMemoriesFromStore();
            }
        }

        async function loadMemoriesFromStore() {
            const query = document.getElementById('memory-search-input')?.value?.trim() || "";
            const cat = document.getElementById('memory-cat-filter')?.value || "";
            const container = document.getElementById('memories-container');
            if (container) {
                container.innerHTML = '<div style="text-align:center; padding:20px; color:var(--eva-text-muted);">Searching knowledge base...</div>';
            }

            try {
                const url = `/api/v1/memory/search?query=${encodeURIComponent(query || "Yash")}&category=${encodeURIComponent(cat)}&limit=15`;
                const res = await fetch(url);
                if (res.ok) {
                    const data = await res.json();
                    renderMemoriesList(data.memories || []);
                }
            } catch (err) {
                if (container) {
                    container.innerHTML = `<div style="color:#B32400; padding:16px;">Failed to load memories: ${err}</div>`;
                }
            }
        }

        function renderMemoriesList(memories) {
            const container = document.getElementById('memories-container');
            if (!container) return;

            if (memories.length === 0) {
                container.innerHTML = '<div style="text-align:center; padding:24px; color:var(--eva-text-muted);">No memories matched your query.</div>';
                return;
            }

            container.innerHTML = memories.map(m => {
                const sensClass = 'sens-' + (m.sensitivity || 'S1');
                const confPct = Math.round((m.confidence || 0.85) * 100);
                const statusLabel = m.status === 'evolved' ? '<span style="color:#B38F00; font-weight:700;">[EVOLVED]</span>' : '';
                const triggersStr = Array.isArray(m.triggers) ? m.triggers.slice(0, 4).join(', ') : '';

                return `
                    <div class="memory-item-card">
                        <div class="memory-header-row">
                            <div style="display:flex; align-items:center; gap:8px;">
                                <span class="memory-id-badge">${m.memory_id}</span>
                                <span class="memory-kind-badge">[${(m.kind || 'said').toUpperCase()}]</span>
                                <strong style="font-size:12px; text-transform:uppercase; color:var(--eva-text-muted);">${m.category}</strong>
                                ${statusLabel}
                            </div>
                            <div style="display:flex; align-items:center; gap:8px;">
                                <span class="sens-badge ${sensClass}">${m.sensitivity || 'S1'}</span>
                                <span style="font-size:11px; font-weight:700; color:var(--eva-deep-green);">${confPct}% conf</span>
                            </div>
                        </div>
                        <div class="memory-content-text">${m.content}</div>
                        <div class="memory-footer-row">
                            <span>Triggers: ${triggersStr || 'general'}</span>
                            <span>Importance: ${m.importance || 3}/5</span>
                        </div>
                    </div>
                `;
            }).join('');
        }

        async function submitEvolveMemory() {
            const statement = document.getElementById('evolve-statement-input')?.value?.trim();
            const resultBox = document.getElementById('evolve-result-box');
            if (!statement) {
                alert("Please enter a new preference statement to test evolution.");
                return;
            }

            try {
                const res = await fetch('/api/v1/memory/evolve', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        statement: statement,
                        category: 'career',
                        confidence: 0.95,
                        importance: 5
                    })
                });
                const data = await res.json();
                if (resultBox) {
                    resultBox.style.display = 'block';
                    resultBox.style.background = 'var(--eva-mist-green)';
                    resultBox.style.color = 'var(--eva-deep-green)';
                    resultBox.style.border = '1px solid var(--eva-pale-green)';
                    if (data.evolved_old_memory_id) {
                        resultBox.innerHTML = `<strong>Contradiction Handled:</strong> Evolved old memory <code>${data.evolved_old_memory_id}</code> into new record <code>${data.new_memory_id}</code> with relationship edge <em>supersedes</em>.`;
                    } else {
                        resultBox.innerHTML = `<strong>Memory Created:</strong> Saved new memory record <code>${data.new_memory_id}</code>.`;
                    }
                }
                loadMemoriesFromStore();
            } catch (err) {
                if (resultBox) {
                    resultBox.style.display = 'block';
                    resultBox.style.background = '#FDE8E8';
                    resultBox.style.color = '#B32400';
                    resultBox.innerHTML = `Error evolving memory: ${err}`;
                }
            }
        }

        // =====================================================================
        // GITHUB AGENT & REPOSITORY STUDIO CONTROLS
        // =====================================================================
        async function loadGitHubData() {
            try {
                const userRes = await fetch('/api/v1/agent/github/user');
                if (userRes.ok) {
                    const u = await userRes.json();
                    if (u.status === 'SUCCESS' || u.login) {
                        const loginEl = document.getElementById('gh-user-login');
                        const bioEl = document.getElementById('gh-user-bio');
                        const avatarEl = document.getElementById('gh-user-avatar');
                        const countEl = document.getElementById('gh-public-repos-count');
                        if (loginEl && u.login) loginEl.textContent = u.login;
                        if (bioEl && u.bio) bioEl.textContent = u.bio;
                        if (avatarEl && u.avatar_url) avatarEl.src = u.avatar_url;
                        if (countEl && u.public_repos !== undefined) countEl.textContent = u.public_repos;
                    }
                }
                
                const reposRes = await fetch('/api/v1/agent/github/repos?per_page=12');
                if (reposRes.ok) {
                    const data = await reposRes.json();
                    renderGitHubRepos(data.repositories || []);
                }
                
                loadGitHubCommits('smart-glasses-ai');
            } catch (e) {
                console.debug('GitHub data load error:', e);
            }
        }

        function renderGitHubRepos(repos) {
            const cont = document.getElementById('github-repos-container');
            if (!cont) return;
            if (repos.length === 0) {
                cont.innerHTML = '<div style="grid-column:1/-1; text-align:center; padding:20px; color:var(--eva-text-muted);">No repositories found.</div>';
                return;
            }
            cont.innerHTML = repos.map(r => `
                <div style="background:var(--eva-pure-white); border:1px solid var(--eva-border-subtle); border-radius:var(--radius-sm); padding:16px; display:flex; flex-direction:column; justify-content:space-between; gap:10px;">
                    <div>
                        <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px;">
                            <strong style="font-size:13px; color:var(--eva-primary-black);">${r.name}</strong>
                            <span style="font-size:11px; font-weight:700; color:var(--eva-deep-green);">${r.language}</span>
                        </div>
                        <p style="font-size:12px; color:var(--eva-text-muted); margin-top:4px; line-height:1.4;">${r.description || 'EVA companion ecosystem repository'}</p>
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center; font-size:11px; color:var(--eva-text-light); border-top:1px solid var(--eva-border-subtle); padding-top:8px;">
                        <span>Stars: ${r.stars || 0} | Forks: ${r.forks || 0}</span>
                        <a href="${r.url}" target="_blank" style="color:var(--eva-primary-green); font-weight:600; text-decoration:none;">View on GitHub →</a>
                    </div>
                </div>
            `).join('');
        }

        async function searchGitHubRepos() {
            const q = document.getElementById('github-search-input')?.value?.trim();
            const cont = document.getElementById('github-repos-container');
            if (!q) {
                loadGitHubData();
                return;
            }
            if (cont) cont.innerHTML = '<div style="grid-column:1/-1; text-align:center; padding:20px; color:var(--eva-text-muted);">Searching GitHub repositories...</div>';
            try {
                const res = await fetch(`/api/v1/agent/github/search?query=${encodeURIComponent(q)}&max_results=8`);
                if (res.ok) {
                    const data = await res.json();
                    renderGitHubRepos(data.repositories || []);
                }
            } catch (e) {
                if (cont) cont.innerHTML = `<div style="grid-column:1/-1; color:#B32400; padding:16px;">Search failed: ${e}</div>`;
            }
        }

        async function loadGitHubCommits(repo) {
            const cont = document.getElementById('github-commits-container');
            if (!cont) return;
            try {
                const res = await fetch(`/api/v1/agent/github/commits?repo=${encodeURIComponent(repo)}&limit=4`);
                if (res.ok) {
                    const data = await res.json();
                    const commits = data.commits || [];
                    if (commits.length === 0) {
                        cont.innerHTML = '<div style="color:var(--eva-text-muted); font-size:12px;">No commits found.</div>';
                        return;
                    }
                    cont.innerHTML = commits.map(c => `
                        <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 12px; background:var(--eva-ivory); border-radius:var(--radius-xs); border:1px solid var(--eva-border-subtle); font-size:12px;">
                            <div style="display:flex; align-items:center; gap:8px;">
                                <code style="background:var(--eva-pure-white); padding:2px 6px; border-radius:4px; font-weight:700; color:var(--eva-deep-green);">${c.sha}</code>
                                <span style="color:var(--eva-primary-black); font-weight:500;">${c.message}</span>
                            </div>
                            <span style="color:var(--eva-text-light); font-size:11px;">${c.author}</span>
                        </div>
                    `).join('');
                }
            } catch (e) {
                cont.innerHTML = `<div style="color:var(--eva-text-muted); font-size:12px;">Commits query: ${e}</div>`;
            }
        }

        // =====================================================================
        // GOD'S EYE TRANSIT & GOOGLE LIVE EARTH 3D QUERIES
        // =====================================================================
        async function teleportGodEyePOI(name, lat, lon) {
            const earthBtn = document.getElementById('btn-open-google-earth');
            const mapsBtn = document.getElementById('btn-open-google-maps');
            if (earthBtn) earthBtn.href = `https://earth.google.com/web/@${lat},${lon},312a,950d,35y,0h,45t,0r`;
            if (mapsBtn) mapsBtn.href = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lon}&travelmode=driving`;
            
            const card = document.getElementById('transit-result-card');
            const summaryEl = document.getElementById('transit-result-summary');
            const rawEl = document.getElementById('transit-result-raw');
            if (card) card.style.display = 'block';
            if (summaryEl) summaryEl.textContent = `[3D Satellite] Locked on ${name} (${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E)`;
            if (rawEl) rawEl.textContent = `[Google Live Earth 3D Teleport]\nDestination: ${name}\nCoordinates: ${lat}, ${lon}\nMode: Orbital 3D Photorealistic Frustum\nBearing: 42° NE | Elevation: 312m MSL`;

            try {
                const res = await fetch(`/api/v1/navigation/google-earth?destination=${encodeURIComponent(name)}&lat=${lat}&lon=${lon}`);
                if (res.ok) {
                    const data = await res.json();
                    if (summaryEl) summaryEl.textContent = `[Live Earth 3D] ${data.spoken_response || data.destination}`;
                    if (rawEl) rawEl.textContent = JSON.stringify(data, null, 2);
                }
            } catch (err) {
                console.debug('POI navigation fallback active:', err);
            }
        }

        async function queryTransitGodEye() {
            const q = document.getElementById('transit-query-input')?.value?.trim();
            if (!q) {
                alert("Please enter a transit destination, train query, or flight number.");
                return;
            }
            const card = document.getElementById('transit-result-card');
            const summaryEl = document.getElementById('transit-result-summary');
            const rawEl = document.getElementById('transit-result-raw');
            if (card) card.style.display = 'block';
            if (summaryEl) summaryEl.textContent = "Querying God's Eye live multimodal network...";
            if (rawEl) rawEl.textContent = "Connecting to transit satellites and local APIs...";

            try {
                const res = await fetch('/api/v1/transit/query', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: q})
                });
                if (res.ok) {
                    const data = await res.json();
                    if (summaryEl) summaryEl.textContent = data.spoken_response || data.summary || "Transit route analyzed.";
                    if (rawEl) rawEl.textContent = JSON.stringify(data, null, 2);
                }
            } catch (e) {
                if (summaryEl) summaryEl.textContent = "Transit network offline.";
                if (rawEl) rawEl.textContent = String(e);
            }
        }

        function quickTransitQuery(q) {
            const input = document.getElementById('transit-query-input');
            if (input) input.value = q;
            queryTransitGodEye();
        }

        // Timeline Category Filter
        function filterTimeline(category, btn) {
            document.querySelectorAll('.filter-pill').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');

            const items = document.querySelectorAll('.timeline-item');
            items.forEach(item => {
                if (category === 'all' || item.getAttribute('data-category') === category) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });
        }

        // Fetch Real-time Live Context (IST Time, Weather, AQI, Battery)
        async function fetchLiveContext() {
            try {
                // 1. Browser Native Battery API if available
                let browserBattery = null;
                if (navigator.getBattery) {
                    try {
                        const b = await navigator.getBattery();
                        browserBattery = Math.round(b.level * 100);
                    } catch(e) {}
                }

                const url = browserBattery !== null ? `/api/v1/context/live?phone_battery=${browserBattery}` : '/api/v1/context/live';
                const res = await fetch(url);
                if (res.ok) {
                    const resp = await res.json();
                    const ctx = resp.context;
                    if (ctx) {
                        // Clock & Greeting
                        const clockEl = document.getElementById('hero-live-clock');
                        if (clockEl) clockEl.textContent = `${ctx.formatted_time} IST`;

                        const titleEl = document.getElementById('hero-context-title');
                        if (titleEl) titleEl.textContent = ctx.greeting;

                        const descEl = document.getElementById('hero-context-desc');
                        if (descEl) descEl.textContent = `${ctx.city.split(',')[0]}: ${ctx.temperature_celsius}°C · ${ctx.weather_condition} · ${ctx.aqi} AQI (${ctx.aqi_category}). ${ctx.aqi_advisory}`;

                        // Metrics
                        const tempEl = document.getElementById('hero-metric-temp');
                        if (tempEl) tempEl.textContent = `${ctx.temperature_celsius}°C`;

                        const aqiEl = document.getElementById('hero-metric-aqi');
                        if (aqiEl) {
                            aqiEl.textContent = `${ctx.aqi} AQI`;
                            aqiEl.style.color = ctx.aqi_color || 'var(--eva-primary-green)';
                        }

                        const batEl = document.getElementById('hero-metric-battery');
                        const tileBat = document.getElementById('tile-battery-pct');
                        const battStr = `${ctx.glasses_battery_pct}%`;
                        if (batEl) batEl.textContent = battStr;
                        if (tileBat) tileBat.textContent = battStr;
                    }
                }
            } catch (err) {
                console.debug('Live context loop active:', err);
            }
        }
        setInterval(fetchLiveContext, 10000);
        fetchLiveContext();
        loadLlmConfig();

        // Action Handlers
        function simulateSmsDemo() {
            simulateIncomingSmsPrompt("Dr. Aris", "+919876543210", "Reviewed the optics blueprint. Looking great.");
            alert("Inbound SMS simulated. Processed by EVA message classifier.");
        }

        function triggerCameraCaptureDemo() {
            triggerMultimodalCapture("Describe what is in view.");
            alert("Multimodal frame capture triggered on XIAO ESP32-S3 Sense.");
        }

        function runDiagnosticsCheck() {
            const out = document.getElementById('diagnostics-output-box');
            if (out) {
                out.innerHTML += `<br>[${new Date().toLocaleTimeString()}] Running full subsystem sweep...<br>[PASS] IMU calibrated<br>[PASS] Memory bus nominal`;
                out.scrollTop = out.scrollHeight;
            }
        }

        function fetchLatestEvents() {
            fetchBackendTelemetry();
            const cont = document.getElementById('timeline-events-container');
            if (cont) {
                const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                const newRow = document.createElement('div');
                newRow.className = 'timeline-item';
                newRow.setAttribute('data-category', 'voice');
                newRow.innerHTML = `
                    <div class="timeline-icon-node">
                        <svg class="eva-icon" viewBox="0 0 24 24"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" fill="currentColor"/></svg>
                    </div>
                    <div class="timeline-content-card">
                        <div class="timeline-main-info">
                            <div class="timeline-title-row">
                                <span class="timeline-title">Live Sync</span>
                                <span class="timeline-badge">System</span>
                            </div>
                            <span class="timeline-detail">Synchronized latest ambient telemetry from companion</span>
                        </div>
                        <span class="timeline-time">${now}</span>
                    </div>
                `;
                cont.prepend(newRow);
            }
        }
    </script>
</body>
</html>
"""
