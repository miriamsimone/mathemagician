# Mathemagician Testing Guide

## Project Context

**Goal**: Test the Mathemagician physics visualization application to verify it's working correctly using automated browser testing and vision AI verification.

## What We Built

A natural language → physics-based 3D animation tool:
- **Backend**: Node.js server with OpenAI GPT-4o-mini integration
- **Frontend**: Three.js + Rapier physics engine (WASM)
- **Features**: Multi-element particle systems, planetary formation, molten core effects, transparency, video recording

## Server Status

- **Running on**: `http://localhost:3000`
- **Main page**: `http://localhost:3000/player.html`
- **API endpoints**:
  - `POST /generate-animation` - Convert natural language to animation config
  - `POST /edit-animation` - Modify existing config with natural language edits
- **API Key**: Already set in `.env` file (OPENAI_API_KEY)

## Test Scenarios

### Primary Test: Planetary Formation

**Prompt to use**:
```
Show planetary formation from dust cloud with iron core, rocky mantle, and icy outer layer
```

**Expected behavior**:
1. User enters prompt and clicks "Generate Animation"
2. Server calls GPT-4o-mini to generate config with `particleGroups`
3. Frontend loads ~4000 particles in 3 groups:
   - Iron core (dark gray, heavy, inner region)
   - Silicate mantle (brown/orange, medium mass, middle)
   - Ice volatiles (light blue, low mass, outer)
4. Physics simulation starts:
   - Particles begin in spherical cloud
   - Center attraction pulls particles inward
   - Heavy iron sinks to core faster (differential mass)
   - Particles become more transparent over time (0.8 → 0.5 opacity)
   - Molten core begins glowing orange/red in center
   - Camera orbits around the forming planet
5. Animation runs for ~20 seconds
6. Final result: Layered planet sphere with visible internal structure

**What to verify visually**:
- ✅ Particles are visible and moving
- ✅ Different colored particles (gray iron, brown rock, blue ice)
- ✅ Particles converging toward center
- ✅ Can see through the sphere to inner layers (transparency working)
- ✅ Orange/red glow in the core region
- ✅ Camera is rotating around the scene
- ✅ Heavy particles (iron) are concentrated in center
- ✅ Light particles (ice) stay more on the surface

### Secondary Tests

**Test 2: Simple Animation**
- Prompt: `"5 red spheres rotating"`
- Expected: 5 red spheres spinning on their axes

**Test 3: Edit Functionality**
After generating planetary formation:
- Edit prompt: `"Make it faster"`
- Expected: Animation reloads with increased center attraction

**Test 4: Video Recording**
- Click "Record Video" button
- Wait for duration to complete
- Click "Download Video"
- Expected: WebM file downloads

## Testing Steps with Playwright MCP

### Step 1: Navigate to Player
```javascript
// Navigate to the page
goto('http://localhost:3000/player.html')
// Wait for page load
waitForSelector('#prompt')
```

### Step 2: Generate Animation
```javascript
// Fill in the prompt
fill('#prompt', 'Show planetary formation from dust cloud with iron core, rocky mantle, and icy outer layer')

// Click generate button
click('#generateBtn')

// Wait for status to show success (may take 5-10 seconds for GPT)
waitForSelector('#status.success', { timeout: 30000 })
```

### Step 3: Wait for Animation to Start
```javascript
// Wait 2-3 seconds for particles to be created and physics to start
wait(3000)
```

### Step 4: Take Screenshots
```javascript
// Take screenshot of initial state (dust cloud)
screenshot('planetary_formation_start.png')

// Wait for mid-animation (compression phase)
wait(8000)
screenshot('planetary_formation_middle.png')

// Wait for final state (formed planet)
wait(8000)
screenshot('planetary_formation_end.png')
```

### Step 5: Vision AI Verification
For each screenshot, use Claude's vision capabilities to verify:
- Are particles visible?
- Are there different colors (gray, brown, blue)?
- Are particles forming a sphere shape?
- Can you see layers inside (transparency)?
- Is there an orange/red glow in the center?
- Does it look like planetary formation?

## Server Logs Location

Check server output for debugging:
```bash
# Server is running in background, check logs with:
# Look for background bash IDs in system reminders
# Use BashOutput tool to see server logs
```

Look for these log messages:
- `[REQUEST] Generating animation for: ...`
- `[RESPONSE] Generated config`
- `[SUCCESS] Generated valid config on attempt X`
- `[EDIT] Request: ...` (for edit tests)

## Common Issues & Solutions

**Issue**: 404 File not found
- **Solution**: Server needs restart. Kill node process and restart `node server.js`

**Issue**: "Physics engine not loaded yet"
- **Solution**: Rapier WASM takes time to load. Wait 2-3 seconds after page load.

**Issue**: No particles visible
- **Solution**: Check browser console for errors. Verify WebGL is supported.

**Issue**: Animation too slow/fast
- **Solution**: Use edit endpoint: `"Make it faster"` or `"Make it slower"`

**Issue**: Can't see inside the planet
- **Solution**: Use edit: `"Make particles more transparent"`

## Expected Config JSON Structure

GPT should generate something like this:

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
    },
    {
      "name": "silicate-mantle",
      "count": 2000,
      "element": "silicate",
      "color": "#8B4513",
      "opacity": 0.6,
      "mass": 1.5,
      "size": 0.08,
      "distribution": {
        "type": "sphere",
        "radiusMin": 5,
        "radiusMax": 15,
        "clustering": 0.5
      }
    },
    {
      "name": "ice-volatiles",
      "count": 1200,
      "element": "ice",
      "color": "#B0E0E6",
      "opacity": 0.5,
      "mass": 0.5,
      "size": 0.06,
      "distribution": {
        "type": "sphere",
        "radiusMin": 12,
        "radiusMax": 20,
        "clustering": 0.3
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
    },
    {
      "time": 16,
      "centerAttraction": 0.15,
      "particleOpacity": 0.5,
      "moltenCore": {
        "enabled": true,
        "radius": 2.0,
        "glowColor": "#FF6347",
        "temperature": 3000,
        "surfaceCrust": true
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

## Success Criteria

✅ **Generation works**: Prompt → GPT generates config → Particles load
✅ **Physics works**: Particles move toward center, heavy particles sink faster
✅ **Transparency works**: Can see inside the formed planet
✅ **Molten core works**: Orange/red glow visible in center
✅ **Camera works**: Scene rotates/orbits
✅ **Layering works**: Different colored particles separate by density
✅ **Edit works**: Natural language edits modify the animation
✅ **Video recording works**: Can export as WebM

## Files to Check

- `server.js` - Backend with OpenAI integration
- `public/player.html` - Frontend with Three.js + Rapier
- `.env` - OpenAI API key (already set)
- `package.json` - Dependencies

## Important Notes

- **Server must be running** on port 3000
- **Browser must support WebGL and WASM** (any modern browser)
- **First load takes 2-3 seconds** for Rapier WASM to initialize
- **GPT call takes 5-10 seconds** to generate config
- **Physics runs client-side** at 60fps
- **Particle limit is 10,000** (for performance)

## Vision AI Verification Questions

When analyzing screenshots, ask:
1. "Do you see particles/spheres in the image?"
2. "What colors are visible? (Should see gray, brown, blue)"
3. "Are the particles forming a sphere/cluster?"
4. "Can you see through the sphere to particles inside?"
5. "Is there any orange or red glow in the center?"
6. "Does this look like dust forming into a planet?"
7. "Are there distinct layers or regions of different colors?"

Expected vision AI response should confirm:
- Multiple particle colors visible
- Spherical formation
- Transparency (can see internal structure)
- Molten core glow effect
- Realistic planetary formation appearance
