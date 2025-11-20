# Mathemagician - Task List for Claude Code

## Project Overview
Build a local microservice that converts natural language descriptions into Three.js physics-based animations, with video export capability. Features real-time physics simulation (gravity, particles) for impressive visualizations like planetary formation from dust clouds.

## Tech Stack
- **Backend**: Node.js + Express
- **Frontend**: Vanilla HTML + Three.js
- **Physics**: Rapier physics engine (WASM-based, client-side)
- **LLM**: OpenAI GPT-4o-mini (API key via .env)
- **Video**: Canvas recording to WebM (client-side)

## File Structure
```
mathemagician/
├── server.js
├── public/
│   └── player.html
├── package.json
├── .env
├── .gitignore
└── README.md
```

## Tasks

### 1. Project Setup
- [ ] Initialize npm project (package.json)
- [ ] Install backend dependencies: express, dotenv, openai, cors
- [ ] Create .env file with OPENAI_API_KEY= placeholder
- [ ] Create .gitignore (include node_modules/, .env)
- [ ] Create basic README.md with setup instructions

### 2. Server Implementation (server.js)
- [ ] Set up Express server on port 3000
- [ ] Load OpenAI API key from .env
- [ ] Enable CORS for localhost
- [ ] Serve static files from public/ directory
- [ ] Create POST endpoint /generate-animation that:
  - Accepts JSON body: { "prompt": "natural language description" }
  - Calls GPT-4o-mini with strict JSON schema prompt
  - Returns animation config JSON
  - Retries up to 3 times if JSON is invalid
  - Returns helpful suggestions if prompt is unclear after retries
- [ ] Add error handling for API failures

### 3. GPT Prompt Engineering
Design system prompt that converts natural language to strict JSON schema supporting physics simulations:

**Example 1: Simple Objects**
```json
{
  "duration": 10,
  "fps": 60,
  "resolution": [1920, 1080],
  "camera": {
    "type": "static",
    "position": [0, 0, 20],
    "lookAt": [0, 0, 0]
  },
  "objects": [
    {
      "type": "sphere",
      "radius": 1,
      "color": "#ff0000",
      "position": [0, 0, 0],
      "animation": {
        "type": "rotation",
        "axis": [0, 1, 0],
        "speed": 0.01
      }
    }
  ],
  "background": "transparent"
}
```

**Example 2: Physics Simulation (Planetary Formation)**
```json
{
  "duration": 15,
  "fps": 60,
  "resolution": [1920, 1080],
  "simulation": {
    "type": "gravity",
    "centerAttraction": 0.1,
    "damping": 0.99
  },
  "particles": {
    "count": 2000,
    "distributionType": "sphere",
    "cloudRadius": 15,
    "particleSize": 0.08,
    "color": "#8B7355",
    "mass": 1
  },
  "camera": {
    "type": "orbit",
    "distance": 25,
    "speed": 0.1
  },
  "background": "transparent"
}
```

- [ ] Write system prompt that ensures GPT outputs ONLY valid JSON
- [ ] Support both simple scripted animations AND physics simulations
- [ ] Include examples for: rotating objects, particle systems, planetary formation
- [ ] Handle edge cases and provide retry logic
- [ ] Limit particle count to max 10,000 for performance

### 4. Three.js + Physics Player (public/player.html)
- [ ] Create single HTML file with embedded CSS and JS
- [ ] Add Three.js from CDN
- [ ] Add Rapier physics engine from CDN
- [ ] Create UI:
  - Text input for natural language prompt
  - "Generate" button
  - "Record Video" button (disabled until animation loaded)
  - "Download Video" button (appears after recording)
  - Canvas for Three.js rendering
  - Status messages area (including suggestions if prompt unclear)
- [ ] Implement Three.js scene setup:
  - Scene, camera, renderer with WebGL
  - Lighting (ambient + directional)
  - Set canvas to fixed pixel dimensions from config resolution
  - Canvas container can scroll/scale if needed to fit viewport
  - Default background to transparent (alpha: 0)
  - Allow background color override via config
- [ ] Implement Rapier physics engine:
  - Initialize WASM physics world
  - Configurable gravity (point-based or directional)
  - Particle system with rigid bodies
  - Custom forces (center attraction for planetary formation)
  - Damping and collision detection
- [ ] Implement config loader for scripted animations:
  - Parse JSON from server
  - Create objects dynamically based on config
  - Set up camera (static or orbiting)
  - Implement animation types: rotation, orbit, scale, translate
  - Handle background color
- [ ] Implement config loader for physics simulations:
  - Create particle clouds with specified distribution
  - Apply physics forces (gravity, attraction)
  - Sync Three.js mesh positions with physics bodies
  - Handle particle merging/clumping effects
- [ ] Implement animation loop:
  - Configurable FPS (30 or 60)
  - Step physics simulation each frame
  - Update camera animations (orbit, pan)
  - Render scene
- [ ] Implement video recording:
  - Use MediaRecorder API with canvas stream
  - Capture at specified FPS
  - Stop after duration completes
  - Generate WebM blob with alpha channel
  - Trigger download

### 5. Testing & Validation
- [ ] Test simple animation: "5 red spheres rotating"
- [ ] Test physics simulation: "Show planetary formation from dust cloud to planet over 15 seconds"
- [ ] Test with: "1000 brown dust particles forming into a planet with gravity"
- [ ] Test with: "Colorful particle explosion"
- [ ] Verify video downloads correctly as WebM
- [ ] Verify video has transparency (transparent background)
- [ ] Verify physics runs smoothly at 60fps with 2000+ particles
- [ ] Test error handling (bad API key, invalid JSON, unclear prompt)
- [ ] Test retry mechanism and suggestions for unclear prompts
- [ ] **IMPORTANT**: Run the application myself, capture screenshots/frames, and use Claude's vision API to verify the animation actually matches what was requested (e.g., does the planetary formation actually look like dust forming into a planet?)

### 6. Documentation
- [ ] Add usage instructions to README
- [ ] Document JSON schema format (both scripted and physics modes)
- [ ] Add example prompts that work well
- [ ] Document physics simulation parameters
- [ ] Document how to run locally: npm install, npm start
- [ ] Note system requirements (modern browser with WebGL + WASM support)

## Nice-to-Haves (Optional)
- [ ] Add loading spinner during generation and physics simulation
- [ ] Preview animation before recording
- [ ] Adjustable quality settings (particle count, resolution)
- [ ] Save/load animation configs
- [ ] Gallery of example animations
- [ ] Additional physics types (collision-based, spring-based)
- [ ] Particle color gradients and size variations
- [ ] Post-processing effects (bloom, glow for space scenes)

## Success Criteria
✅ Can run locally with `node server.js`
✅ Can type natural language prompt and see animation
✅ Physics simulation works: planetary formation from dust cloud
✅ Can record physics animation to WebM file with transparency
✅ Handles 2000+ particles at 60fps smoothly
✅ GPT interprets prompts accurately with retry logic
✅ Ready to extend with more physics types and visualizations

**First Milestone: Get "Show planetary formation from dust cloud" working end-to-end!** 🚀
