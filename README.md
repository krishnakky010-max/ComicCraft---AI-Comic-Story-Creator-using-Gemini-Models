# ComicCraft // AI Comic, Manga & Manhwa Creation Studio

**ComicCraft** is an AI-powered storytelling and digital storyboard platform driven by Google Gemini models. Designed with a futuristic deep space aesthetic (`#0B0D17`), neon cyan (`#00F0FF`), electric purple (`#8A2BE2`), and dynamic glassmorphism.

---

## 🚀 Quick Start

### 1. Launch the Server
To launch ComicCraft, run the included batch file or start the server via Node.js:

```bash
# Using the Windows batch launcher
start.bat

# Or directly with agy-node
agy-node server.mjs
```

Then open your browser and navigate to:
👉 **`http://localhost:3000/`**

---

## 🎨 Core Features & Architecture

### 1. 3 Storytelling Format Engines
- **Western Comic Book**: Multi-tier grid layouts, vibrant CMYK-style halftones, dynamic dialogue pointers, and superhero splash frames.
- **Manga (Right-to-Left RTL)**: Right-to-left panel flow, high-contrast black-and-white ink, dynamic screentones, action speedlines, and Japanese SFX onomatopoeia.
- **Manhwa / Webtoon**: Infinite vertical continuous scroll, mobile-optimized widescreen panels, and cinematic vertical pacing.

### 2. Gemini-Driven Character Design & Consistency Studio
- **Turnaround Sheets**: 4-angle visual model reference (Front 0°, 3/4 Dynamic 45°, Side Profile 90°, Rear View 180°).
- **Expression Sheets**: Emotional range matrix (Neutral, Determined, Smirk, Shocked, Battle Cry).
- **Consistency Locking Engine**:
  - Reproducible seed number lock (`[Seed: 849201]`).
  - Visual embedding tokens (`[VisualEmbed: "ren_kurogane, messy black hair with cyan highlight, silver right cybernetic eye"]`).
  - Signature outfit and gear locks.
  - Negative prompt filters.
- **Dynamic Relationship Matrix**: Interactive SVG node graph visualizing ties (Allies, Rivals, Mentors, Nemeses, Partners).

### 3. Voice & Sound Lab (Web Speech & Web Audio API)
- **Character Voice Assignment**: Distinct TTS voices, vocal pitch sliders, cadence/rate tuning, and emotional tone presets (Stoic, Aggressive, Cheerful, Mysterious, Cybernetic AI, Heroic).
- **Interactive Speech Bubbles**: Click any dialogue bubble on the canvas to hear the character speak their lines aloud in real time with an animated audio reactive pulse.
- **Autoplay Narration Mode**: Sequences through the entire story, highlighting each panel and speaking character dialogues sequentially.
- **Procedural Comic SFX Synthesizer**: Web Audio API generated sound effects:
  - 💥 BOOM / Heavy Impact Punch
  - ⚡ Laser Blast / Neon Plasma
  - 💨 Action Swoosh / Blade Slash
  - ✨ Shonen Power Aura Flare
  - ⛈️ Low Rumble Thunderclap
  - 📖 Tactile Page Flip

### 4. Interactive Story Board Canvas
- **Panel Tools**: Add, delete, reorder, aspect ratio presets (`16:9`, `4:3`, `Splash`, `21:9`, `9:16`), and camera angles (Wide, Medium, Close-up, Splash, Dutch Action).
- **Style Filters**: Vibrant Color, Manga Screentone B&W, Retro Comic Print.
- **Customizable Speech Bubbles**: Draggable across canvas with Dialogue, Shout (spiky), Whisper (dashed), Thought (cloudy), and Caption styles.
- **Gemini Script-to-Panels Generator**: Converts a story beat or premise into a fully paced multi-panel script with camera angles and dialogues.

### 5. Export Manager
- Export PNG high-resolution comic pages.
- Compile continuous vertical Webtoon strips.
- Interactive digital reader presentation mode.
- Backup and restore full project JSON archives.

---

## 🔑 Gemini AI Integration

ComicCraft is equipped with a dual AI engine:
1. **Built-in ComicCraft AI Engine**: Fully operational offline and demo-ready with curated high-fidelity comic artwork and procedural storyboard pacing.
2. **Live Google Gemini API**: Enter your Google Gemini API key via the **Gemini AI Engine** button to enable live calls to `gemini-1.5-flash` / `gemini-2.0-flash` for real-time script writing, dynamic dialogue generation, and prompt refinement.
