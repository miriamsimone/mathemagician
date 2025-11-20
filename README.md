# 🪐 Mathemagician

Natural language → Physics-based 3D animations with Three.js and Rapier physics engine.

## Features

- 🤖 **AI-Powered**: Describe what you want in plain English, GPT-4o-mini generates the config
- ⚛️ **Real Physics**: Rapier WASM physics engine with gravity simulation
- 🌍 **Planetary Formation**: Multi-element particle systems (iron core, silicate mantle, ice outer layer)
- 🎨 **Transparency**: See inside the forming planet with adjustable opacity
- 🔥 **Molten Core Effects**: Glowing core visualization as particles compress
- ✏️ **Natural Language Editing**: "Make it faster", "add more particles", "make iron sink quicker"
- 📹 **Video Export**: Record animations as WebM with transparency

## Quick Start

```bash
# Install dependencies
npm install

# Set your OpenAI API key
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# Start server
node server.js

# Open browser
open http://localhost:3000/player.html
```

## Example Prompts

Try these to get started:

- `"Show planetary formation from dust cloud with iron core, rocky mantle, and icy outer layer"`
- `"1000 brown particles forming into a planet with gravity"`
- `"Dust cloud with different elements that separate by density"`
- `"Colorful particle explosion"`
- `"5 red spheres rotating"`

## Editing Animations

After generating an animation, you can refine it:

- `"Make it faster"` → Increases center attraction
- `"Add more particles"` → Increases particle count
- `"Make particles more transparent"` → Reduces opacity to see inside better
- `"Stronger molten core glow"` → Increases core temperature effect
- `"Make the iron particles bigger"` → Adjusts iron-core group size

## How It Works

### Architecture

1. **Server (Node.js + Express)**
   - `/generate-animation` - Converts natural language to JSON config via GPT-4o-mini
   - `/edit-animation` - Modifies existing config based on natural language edits
   - Retry logic (3 attempts) with helpful suggestions

2. **Client (Three.js + Rapier)**
   - Loads config and creates particle systems
   - Physics simulation runs client-side (60fps)
   - Custom gravity forces (center attraction)
   - Differential mass (heavy particles sink to core)
   - Phase-based animation (parameters change over time)
   - Video recording via MediaRecorder API

### Physics Simulation

```javascript
// Each frame:
1. Apply center attraction force (gravity toward origin)
2. Scale force by particle mass (heavy iron sinks faster)
3. Apply damping (friction/energy loss)
4. Step physics engine (Rapier calculates collisions, velocities)
5. Update visual meshes to match physics positions
6. Add molten core glow effect for particles near center
```

### JSON Schema

**Particle Groups (Multi-Element System)**:
```json
{
  "duration": 20,
  "fps": 60,
  "resolution": [1920, 1080],
  "simulation": {
    "type": "gravity",
    "centerAttraction": 0.15,
    "damping": 0.98,
    "differentialMass": true
  },
  "particleGroups": [
    {
      "name": "iron-core",
      "count": 800,
      "element": "iron",
      "color": "#2F4F4F",
      "opacity": 0.7,
      "mass": 3.0,
      "size": 0.1,
      "distribution": {
        "type": "sphere",
        "radiusMin": 0,
        "radiusMax": 8,
        "clustering": 0.7
      }
    }
  ],
  "phases": [
    {
      "time": 0,
      "centerAttraction": 0.05,
      "particleOpacity": 0.8,
      "moltenCore": { "enabled": false }
    },
    {
      "time": 8,
      "centerAttraction": 0.25,
      "particleOpacity": 0.6,
      "moltenCore": {
        "enabled": true,
        "radius": 2.5,
        "glowColor": "#FF4500",
        "temperature": 5000
      }
    }
  ],
  "camera": {
    "type": "orbit",
    "distance": 30,
    "speed": 0.1
  },
  "background": "transparent"
}
```

## System Requirements

- Modern browser with WebGL and WASM support
- Node.js 14+
- OpenAI API key

## Tech Stack

- **Backend**: Express, OpenAI API (GPT-4o-mini)
- **Frontend**: Three.js (WebGL rendering)
- **Physics**: Rapier3D (WASM-based rigid body physics)
- **Video**: MediaRecorder API (WebM with VP9 codec)

## Roadmap

- [ ] More physics types (collision-based, spring systems)
- [ ] Particle color gradients
- [ ] Post-processing effects (bloom, glow)
- [ ] Preset gallery
- [ ] Quality settings (particle count, resolution)
- [ ] Server-side rendering option for high-quality exports

## License

MIT
