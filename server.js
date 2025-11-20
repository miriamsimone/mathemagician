const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const OpenAI = require('openai');
const path = require('path');

// Load environment variables
dotenv.config();

const app = express();
const PORT = 3000;

// Initialize OpenAI
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

// Middleware
app.use(cors({ origin: 'http://localhost:3000' }));
app.use(express.json());
app.use(express.static('public'));

// System prompt for GPT
const SYSTEM_PROMPT = `You are an animation config generator. Convert natural language descriptions into JSON configurations for Three.js animations with physics simulations.

You must respond with ONLY valid JSON, no other text.

SUPPORTED MODES:

1. SCRIPTED ANIMATIONS (simple objects with predefined movements):
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
      "opacity": 1.0,
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

2. PHYSICS SIMULATIONS WITH PARTICLE GROUPS (realistic planetary formation):
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
      "moltenCore": {
        "enabled": false
      }
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

PARTICLE ELEMENTS AND PROPERTIES:
- iron/nickel (core): Dark gray/metallic colors, high mass (2.5-3.5), inner distribution
- silicate (mantle): Brown/orange colors, medium mass (1.0-2.0), middle distribution
- ice/volatiles (outer): Light blue/white colors, low mass (0.3-0.8), outer distribution
- Use opacity 0.4-0.8 so you can see through to inner layers when formed

OPACITY RULES:
- Particles should have opacity 0.5-0.8 to show internal structure
- As planet forms, reduce opacity slightly (0.8 → 0.5) to reveal layers
- Molten core can have higher opacity/glow
- Ice particles can be more transparent (0.4-0.6)

MOLTEN CORE PHASES:
- Phase 1: Dust cloud, no molten core
- Phase 2: Compression starts, molten core begins forming
- Phase 3: Fully formed planet with glowing molten core visible inside

RULES:
- Max total particles across all groups: 10000
- FPS: 30 or 60 only
- Background: "transparent" or hex color
- Camera types: "static" or "orbit"
- Distribution types: "sphere", "random", "grid"
- Clustering: 0.0-1.0 (how clumped particles are)
- For planetary formation, use particleGroups with different elements
- Heavy elements sink to core, light elements stay on surface

EXAMPLES:
"5 red spheres rotating" → scripted animation mode
"planetary formation" → physics simulation with particleGroups (iron core, silicate mantle, ice outer)
"dust cloud forming into a planet with visible layers" → particleGroups with transparency
"show me iron sinking to the core as a planet forms" → particleGroups with differentialMass

Output ONLY the JSON config, nothing else.`;

// POST /generate-animation
app.post('/generate-animation', async (req, res) => {
  const { prompt } = req.body;

  if (!prompt) {
    return res.status(400).json({ error: 'Prompt is required' });
  }

  console.log('[REQUEST] Generating animation for:', prompt);

  let lastError = null;
  
  // Retry up to 3 times
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      console.log('[ATTEMPT', attempt, '] Calling OpenAI...');
      
      const completion = await openai.chat.completions.create({
        model: 'gpt-4o-mini',
        messages: [
          { role: 'system', content: SYSTEM_PROMPT },
          { role: 'user', content: prompt }
        ],
        response_format: { type: 'json_object' },
        temperature: 0.7
      });

      const responseText = completion.choices[0].message.content;
      console.log('[RESPONSE] Generated config');

      // Parse and validate JSON
      const config = JSON.parse(responseText);

      // Basic validation
      if (!config.duration || !config.fps || !config.resolution) {
        throw new Error('Missing required fields: duration, fps, or resolution');
      }

      // Limit particle count (single particle system)
      if (config.particles && config.particles.count > 10000) {
        config.particles.count = 10000;
        console.log('[WARNING] Particle count limited to 10000');
      }

      // Limit total particle count (particle groups)
      if (config.particleGroups) {
        const totalCount = config.particleGroups.reduce((sum, group) => sum + group.count, 0);
        if (totalCount > 10000) {
          const scale = 10000 / totalCount;
          config.particleGroups = config.particleGroups.map(group => ({
            ...group,
            count: Math.floor(group.count * scale)
          }));
          console.log('[WARNING] Total particle count scaled down to 10000');
        }
      }

      console.log('[SUCCESS] Generated valid config on attempt', attempt);
      return res.json({ config });

    } catch (error) {
      lastError = error;
      console.error('[ATTEMPT', attempt, 'FAILED]', error.message);
      
      if (attempt < 3) {
        // Wait a bit before retrying
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
  }

  // All retries failed - provide helpful suggestions
  console.error('[FAILED] All retries exhausted');
  
  return res.status(400).json({
    error: 'Could not generate valid animation config',
    message: 'Your prompt might be unclear. Try being more specific.',
    suggestions: [
      'Try: "Show me a rotating red sphere"',
      'Try: "Create a planetary formation animation from dust"',
      'Try: "1000 particles with gravity forming into a ball"'
    ],
    details: lastError.message
  });
});

// POST /edit-animation
app.post('/edit-animation', async (req, res) => {
  const { currentConfig, editPrompt } = req.body;

  if (!currentConfig || !editPrompt) {
    return res.status(400).json({ error: 'currentConfig and editPrompt are required' });
  }

  console.log('[EDIT] Request:', editPrompt);

  const EDIT_SYSTEM_PROMPT = `You are an animation config editor. Given a current animation config and a user's edit request, modify ONLY the relevant parameters.

Rules:
- Preserve all unchanged fields exactly as they are
- Only modify parameters related to the user's request
- Return the COMPLETE modified config (not just changed fields)
- Maintain all required fields
- Provide brief explanation of what changed

USER REQUEST MAPPINGS:
"faster" / "speed up" → increase centerAttraction or reduce damping
"slower" / "slow down" → decrease centerAttraction or increase damping
"bigger particles" → increase particle size
"smaller particles" → decrease particle size
"more particles" → increase count (max 10000 total)
"fewer particles" → decrease count
"different color" / "more red/blue/etc" → change color values
"longer" / "shorter" → change duration
"more transparent" → reduce opacity
"less transparent" → increase opacity
"stronger gravity" → increase centerAttraction
"weaker gravity" → decrease centerAttraction
"more glow" → increase moltenCore temperature and adjust glowColor
"less glow" → decrease moltenCore temperature
"see inside better" → reduce particle opacity

For particle groups:
- Changes to "iron" affect iron-core group
- Changes to "rock" or "mantle" affect silicate group
- Changes to "ice" affect ice-volatiles group

Output JSON format:
{
  "config": { /* full modified config */ },
  "changes": "Brief description of what changed"
}`;

  try {
    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: EDIT_SYSTEM_PROMPT },
        { role: 'user', content: `Current config:\n${JSON.stringify(currentConfig, null, 2)}\n\nEdit request: ${editPrompt}` }
      ],
      response_format: { type: 'json_object' },
      temperature: 0.5
    });

    const response = JSON.parse(completion.choices[0].message.content);

    console.log('[EDIT SUCCESS]', response.changes);

    return res.json({
      config: response.config,
      changes: response.changes
    });

  } catch (error) {
    console.error('[EDIT ERROR]', error);
    return res.status(400).json({
      error: 'Failed to apply edit',
      details: error.message
    });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Start server
app.listen(PORT, () => {
  console.log('Mathemagician server running on http://localhost:' + PORT);
  console.log('Make sure OPENAI_API_KEY is set in .env file');
});
