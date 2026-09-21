# EVA — Living Digital Phenomenon: Design Language Specification

## 1. Philosophy: Living Darkness & Radiant Presence

EVA is not an application, a dashboard, or a chatbot. EVA is a **living digital phenomenon** across Web, Android, Smart Glasses, Voice, Context, and AI Intelligence.

```text
DARK BUT RADIANT
ELEGANT BUT WILD
MINIMAL BUT INFINITE
SILENT BUT IRRESISTIBLE
TECHNICAL BUT HUMAN
FUTURISTIC BUT INTIMATE
```

### Living Darkness vs Flat Black
The foundation of EVA is never flat `#000000`. Flat black is dead space; **living darkness** is deep atmospheric night imbued with latent chromatic energy, subtle particulate motion, and low-frequency luminous breathing.

- **Primary Canvas**: Obsidian Void (`#07080B`), Deep Night (`#0D0F14`), and Atmosphere Indigo (`#141722`).
- **Hidden Radiance**: Peacock Teal (`#14B8A6`), Deep Cosmic Violet (`#8B5CF6`), Radiant Cyan (`#06B6D4`), and Soft Luminous Gold (`#EAB308`).
- **Luminosity Principle**: Light is never constant or garish. Light emerges only when interaction creates gravity, expands during reasoning, and gently settles into dark velvet silence.

---

## 2. Shared Visual State Machine

Every interface state across Web and Android represents an **emotional and cognitive state**:

```
 ┌────────────┐        Voice / Input       ┌─────────────┐
 │  AWAITING  ├───────────────────────────►│  LISTENING  │
 └─────▲──────┘                            └──────┬──────┘
       │                                          │ Audio Ingest
       │               ┌─────────────┐            ▼
       │ Settle        │  SPEAKING   │◄────┐ ┌─────────────┐
       └───────────────┤  / OUTPUT   │     └─┤  THINKING   │
                       └─────────────┘       └──────┬──────┘
                              ▲                     │ Complex Task
                              │                     ▼
                       ┌──────┴──────┐       ┌─────────────┐
                       │  CREATING   │◄──────┤ DISCOVERING │
                       └─────────────┘       └─────────────┘
```

| State | Visual Behavior | Dominant Color | Acoustic Tone |
| :--- | :--- | :--- | :--- |
| **AWAITING** | Slow, rhythmic 4.2s orbital breathing, resting core | Deep Indigo / Charcoal | Absolute silence |
| **LISTENING** | Reactive organic waveform, expanding radius, high sensitivity | Peacock Cyan / Teal | Soft air resonance (432 Hz harmonic) |
| **THINKING** | Dual-orbit particle rotation, shifting internal hue | Deep Violet / Indigo | Distant glass harmonic |
| **SPEAKING** | Luminous cadence waves matching TTS amplitude | Radiant Teal / Warm White | Smooth natural vocal stream |
| **DISCOVERING** | Orbital constellation nodes expanding outward | Celestial Cyan / Indigo | Low subtle chime |
| **CREATING** | Expanding velvet canvas with structured artifact reveal | Radiant Gold / Violet | Soft metallic timbre |
| **OFFLINE** | Deepened velvet obsidian state with subtle local awareness | Muted Steel / Slate | Restrained single tone |

---

## 3. The Color Ecosystem

```css
:root {
    /* Living Dark Canvas */
    --eva-void: #07080B;
    --eva-night: #0D0F14;
    --eva-indigo: #141722;
    --eva-surface-velvet: #1B1F2C;
    --eva-surface-elevated: #242938;

    /* Hidden Radiant Accents */
    --eva-teal: #14B8A6;
    --eva-cyan: #06B6D4;
    --eva-violet: #8B5CF6;
    --eva-gold: #EAB308;
    --eva-rose: #F43F5E;

    /* Typography & Contrast */
    --eva-text-pure: #F8FAFC;
    --eva-text-primary: #E2E8F0;
    --eva-text-secondary: #94A3B8;
    --eva-text-muted: #64748B;
    --eva-border-subtle: rgba(255, 255, 255, 0.08);
    --eva-border-glow: rgba(20, 184, 166, 0.35);
}
```

---

## 4. Motion Grammar

Motion in EVA follows natural fluid mechanics rather than mechanical easing curves:

1. **Breath** (4.0s–5.0s ease-in-out cycle): Subtle atmospheric expansion and contraction of the central presence.
2. **Gather** (350ms spring dynamic): Contextual elements converge toward the command surface upon wake.
3. **Flow** (500ms smooth cubic-bezier): Text and typography stream organically onto the spatial field.
4. **Orbit** (Continuous low-frequency rotational drift): Constellation nodes rotate around active inquiry anchors.
5. **Dissolve** (400ms alpha fade): Completed ephemeral states settle gracefully back into darkness.

---

## 5. Typographic Architecture

- **Primary Display / Title**: High-contrast, spacious, refined editorial font (`Cinzel`, `Inter Display`, or serif system font) with generous letter-spacing (`1.5px–3px`).
- **Body & Spoken Field**: Ultra-legible humanist sans-serif (`Inter`, `-apple-system`, `Roboto`) with relaxed line-height (`1.65`).
- **Code & Telemetry**: Monospace precision (`JetBrains Mono`, `Fira Code`) formatted with muted syntax highlighting.

---

## 6. Audio Design Language

Sound in EVA is minimal, organic, and non-intrusive:
- **Wake Acknowledgment**: 528 Hz soft glass ping (0.15s decay).
- **Processing Cadence**: Ultra-low 60 Hz warm ambient drone during deep LLM reasoning.
- **Completion / Success**: Ascending dual-tone (440 Hz → 660 Hz) harmonic sweep.
- **Disconnection / Mute**: Descending soft breath (0.2s duration).

---

## 7. Platform Primitives

### Android Jetpack Compose
- `EvaAtmosphere`: Ambient gradient canvas with particle drift.
- `EvaPresence`: Multi-state visual core with orbital breathing.
- `EvaCommandField`: Minimal voice & text instrument.
- `EvaWaveform`: Real-time 16kHz PCM audio amplitude visualizer.
- `EvaDevicePresence`: Recognition ritual for ESP32 glasses and TWS.
- `EvaContextCard`: Non-invasive proactive awareness cards.

### Web Canvas & CSS
- `#eva-canvas`: High-performance background particle & atmospheric depth renderer.
- `.eva-presence-core`: SVG + CSS keyframe orbital state system.
- `.eva-command-surface`: Floating instrument input bar with Web Speech API integration.
- `.eva-constellation`: Dynamic SVG node-link graph for academic papers and memory connections.
