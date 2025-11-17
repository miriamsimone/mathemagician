# Mathemagician API - Task List (TONIGHT DEPLOYMENT)

**Timeline: Demo tonight (Monday), final submission Saturday**
**Stack: Cloud Run + Redis (in-container) + GCS**

---

## TONIGHT'S SPRINT (Next 8-10 hours)

### Hour 1-2: MVP Setup & First Scene

#### Task 1.1: Project Initialization (15 min)
- [ ] Create project directory structure
- [ ] Initialize git repository
- [ ] Create requirements.txt with MINIMAL dependencies:
  ```
  fastapi==0.104.1
  uvicorn[standard]==0.24.0
  pydantic==2.5.0
  manim==0.18.0
  google-cloud-storage==2.10.0
  redis==5.0.1
  pillow==10.1.0
  ```

#### Task 1.2: Docker Configuration (20 min)
- [ ] Create Dockerfile with Manim dependencies
- [ ] Include Redis in same container (simplest for tonight)
- [ ] Test local build: `docker build -t math-viz .`
- [ ] Test local run: `docker run -p 8000:8000 math-viz`

#### Task 1.3: Minimal FastAPI App (25 min)
- [ ] Create FastAPI application (main.py)
- [ ] Health check endpoint: GET `/health`
- [ ] CORS middleware for Tanner's frontend
- [ ] Basic error handling

#### Task 1.4: Single Manim Scene - Function Graph (60 min)
- [ ] Create `scenes/function_graph.py`
- [ ] Hardcode simple scene: plot f(x) from JSON input
- [ ] Test locally with: `{"function": "x**2", "x_range": [-3, 3]}`
- [ ] Render to local file
- [ ] Generate thumbnail (first frame)
- **GOAL**: One working scene type before moving on

---

### Hour 3-4: API Endpoints & Async Processing

#### Task 2.1: Job Queue with Redis (30 min)
- [ ] Start Redis in background (in same container)
- [ ] Create simple job queue (Redis lists)
- [ ] Job model: id, status, input, output_path
- [ ] Store jobs in Redis with TTL

#### Task 2.2: POST /generate Endpoint (45 min)
- [ ] Accept request: `{"function": "sin(x)", "x_range": [-5, 5]}`
- [ ] Create job ID (UUID)
- [ ] Queue job in Redis
- [ ] Return job_id immediately
- [ ] Add basic validation (function string safety)

#### Task 2.3: Background Worker (45 min)
- [ ] Create worker process
- [ ] Poll Redis queue
- [ ] Call Manim render
- [ ] Save video locally (for now)
- [ ] Update job status
- [ ] Run worker in background thread (simple for tonight)

---

### Hour 5-6: GCP Integration & Deploy Prep

#### Task 3.1: GCS Setup (20 min)
- [ ] Enable Cloud Storage API
- [ ] Create bucket: `gsutil mb gs://math-viz-outputs-[random]`
- [ ] Set up service account with Storage permissions
- [ ] Test upload from local: `gsutil cp test.mp4 gs://bucket/`

#### Task 3.2: Upload to GCS After Render (30 min)
- [ ] Install google-cloud-storage
- [ ] After render completes, upload to GCS
- [ ] Generate signed URL (7-day expiry)
- [ ] Store URL in job metadata
- [ ] Delete local file after upload

#### Task 3.3: GET /status/{job_id} Endpoint (20 min)
- [ ] Query job from Redis
- [ ] Return status: queued/processing/completed/failed
- [ ] If completed, return GCS signed URL
- [ ] If failed, return error message

#### Task 3.4: Dockerfile Optimization (20 min)
- [ ] Multi-stage build (if time)
- [ ] Health check command
- [ ] Proper entrypoint (start Redis, worker, API)
- [ ] Set memory limits
- [ ] Test full build locally

---

### Hour 7-8: Deploy to Cloud Run

#### Task 4.1: Cloud Run Configuration (15 min)
- [ ] Enable Cloud Run API: `gcloud services enable run.googleapis.com`
- [ ] Set up gcloud CLI and authenticate
- [ ] Create `.gcloudignore` file
- [ ] Set environment variables (GCS bucket name)

#### Task 4.2: Deploy (30 min)
- [ ] Deploy: `gcloud run deploy math-visualizer --source . --memory 4Gi --timeout 600 --allow-unauthenticated`
- [ ] Wait for deployment
- [ ] Test health endpoint
- [ ] Note the Cloud Run URL

#### Task 4.3: Test End-to-End (30 min)
- [ ] POST to /generate with test function
- [ ] Poll /status endpoint
- [ ] Verify video renders and uploads to GCS
- [ ] Test signed URL in browser
- [ ] Fix any deployment issues

#### Task 4.4: Share with Tanner (15 min)
- [ ] Document API endpoints
- [ ] Share Cloud Run URL
- [ ] Provide example request/response
- [ ] Test CORS from his frontend

---

### Hour 9-10: Demo Polish

#### Task 5.1: Error Handling (20 min)
- [ ] Better error messages
- [ ] Handle invalid functions gracefully
- [ ] Timeout handling
- [ ] Return helpful errors in API

#### Task 5.2: Simple Styling (20 min)
- [ ] Add color scheme to Manim scene
- [ ] Better axis labels
- [ ] Grid background
- [ ] Make it look nice!

#### Task 5.3: Basic Natural Language (Optional) (40 min)
- [ ] Add Claude API call for function parsing
- [ ] Simple prompt: "Convert to math function"
- [ ] Input: "plot sine wave" → Output: sin(x)
- [ ] If time permits!

---

## SATURDAY TASKS (Final Submission)

### Phase 1: Core Manim Integration (Saturday Morning)

#### Task 6.1: Additional Scene Templates
- [ ] Implement GeometricShapeScene template
  - Basic shapes (circle, square, polygon)
  - Transformations
- [ ] Implement VectorScene template
  - Vector visualization
  - Vector operations
- [ ] Create 3D scene template (if time)

#### Task 6.2: Full LLM Integration (Saturday Morning)
- [ ] Add anthropic package to requirements
- [ ] Design system prompt for scene generation
- [ ] Implement `generate_scene_config(description: str) -> dict`
- [ ] Test with various natural language inputs
- [ ] Add fallback for LLM failures

#### Task 6.3: POST /edit Endpoint (Saturday Afternoon)
- [ ] Accept job_id and edit description
- [ ] Load original scene config from Redis
- [ ] Call Claude API for edit interpretation
- [ ] Create new render job with modifications
- [ ] Return new job_id

### Phase 2: Production Readiness (Saturday Afternoon)

#### Task 7.1: Migration to Managed Services (If Needed)
- [ ] Consider Cloud Memorystore (Redis) if in-container Redis struggles
- [ ] Consider Cloud Tasks for better queue management
- [ ] Migrate if traffic/reliability issues arise

#### Task 7.2: Better Async with Celery (Optional)
- [ ] Replace background thread with Celery worker
- [ ] Add Celery to requirements
- [ ] Deploy separate worker on Cloud Run
- [ ] Better retry logic and error handling

#### Task 7.3: Monitoring & Logging
- [ ] Add structured logging throughout
- [ ] Log render times
- [ ] Log success/failure rates
- [ ] Set up Cloud Logging dashboard

#### Task 7.4: Performance Optimization
- [ ] Parallel rendering (if multiple quality outputs needed)
- [ ] Cache common scenes
- [ ] Optimize Manim render settings
- [ ] Add render time estimates to /status

### Phase 3: Polish & Integration (Saturday Evening)

#### Task 8.1: Enhanced Styling
- [ ] Multiple color schemes
- [ ] Better default styling
- [ ] Animation speed control
- [ ] Custom fonts/LaTeX rendering

#### Task 8.2: Integration Testing
- [ ] Full integration test with Tanner's frontend
- [ ] Coordinate with Remi on timing metadata
- [ ] Test various edge cases
- [ ] Fix integration issues

#### Task 8.3: Documentation
- [ ] API documentation (auto-generated with FastAPI)
- [ ] Example requests for common visualizations
- [ ] Troubleshooting guide
- [ ] README with deployment instructions

---

## Phase 2: Additional Features (If Time Saturday)

## Phase 2: Additional Features (If Time Saturday)

- [ ] Multiple scenes in one video
- [ ] Export formats (GIF, WebM)
- [ ] Batch generation endpoint
- [ ] WebSocket for real-time render progress

---

## File Structure (Simplified for Tonight)

```
mathemagician/
├── Dockerfile
├── requirements.txt
├── README.md
├── .env.example
├── .gcloudignore
├── main.py                  # FastAPI app + startup
├── models.py                # Pydantic models
├── worker.py                # Background render worker
├── scenes/
│   ├── __init__.py
│   └── function_graph.py    # Tonight: just this one!
├── services/
│   ├── __init__.py
│   ├── gcs_storage.py       # GCS upload/download
│   ├── job_queue.py         # Redis job management
│   └── renderer.py          # Manim render wrapper
└── tests/
    └── test_basic.py
```

### Saturday: Add These

```
├── services/
│   ├── llm_service.py       # Claude API integration
│   └── edit_service.py      # Edit logic
├── scenes/
│   ├── geometric.py
│   ├── vector.py
│   └── templates.py         # Scene factory
```

---

## Critical Path for Tonight

**Must Complete:**
1. ✅ Dockerfile with Manim + Redis
2. ✅ One working scene (function graph)
3. ✅ /generate endpoint
4. ✅ /status endpoint
5. ✅ GCS upload
6. ✅ Cloud Run deployment
7. ✅ End-to-end test

**Everything else is Saturday work!**

---

## Quick Start Commands

```bash
# Local development
docker build -t mathemagician .
docker run -p 8000:8000 mathemagician

# Test locally
curl http://localhost:8000/health
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"function": "sin(x)", "x_range": [-5, 5]}'

# Deploy to GCP
gcloud run deploy mathemagician \
  --source . \
  --memory 4Gi \
  --timeout 600 \
  --cpu 2 \
  --allow-unauthenticated \
  --set-env-vars GCS_BUCKET=mathemagician-outputs-[random]

# Check status
curl https://[cloud-run-url]/status/{job_id}
```

---

## Environment Variables

```bash
# .env (local)
GCS_BUCKET=mathemagician-outputs-dev
REDIS_URL=redis://localhost:6379
ENVIRONMENT=local

# Cloud Run (set via console or CLI)
GCS_BUCKET=mathemagician-outputs-prod
ENVIRONMENT=production
```

---

## Tonight's Demo Script

For demo tonight (even if not fully deployed):

1. Show local Docker running
2. POST to /generate with "sin(x)"
3. Poll /status until complete
4. Show rendered video
5. Explain: "By Saturday we'll have natural language editing and more scene types"

---

## Notes for Claude Code

When implementing with Claude Code tonight:
- **Start with Dockerfile** - get Manim working first
- **Test each scene locally** before adding API
- **Deploy early** - don't wait for perfection
- **Simple is better** - background thread > Celery for tonight
- **Log everything** - you'll need it for debugging Cloud Run
- **GCS signed URLs** are 7-day expiry by default (fine for demo)
- [ ] Design system prompt for visualization generation
  - Explain available scene types
  - Specify output format (JSON SceneConfig)
  - Include examples
- [ ] Create prompt templates for each visualization type
- [ ] Design edit operation prompts
  - Parse natural language edits
  - Generate scene config diffs

### Task 2.2: Claude API Integration
- [ ] Create LLM service module
- [ ] Implement `generate_scene_config(description: str) -> SceneConfig`
- [ ] Implement `edit_scene_config(original: SceneConfig, edit_request: str) -> SceneConfig`
- [ ] Add error handling and retry logic
- [ ] Cache LLM responses (optional optimization)

### Task 2.3: Validation Layer
- [ ] Validate LLM-generated configs
  - Check required fields
  - Validate parameter ranges
  - Sanitize LaTeX/code strings
- [ ] Implement safety checks
  - Prevent code injection
  - Resource limits (scene complexity)
- [ ] Create fallback templates for invalid configs

---

## Phase 3: API Endpoints (Day 4-5)

### Task 3.1: POST /generate Endpoint
- [ ] Accept visualization request
- [ ] Call LLM service to generate config
- [ ] Create render job
- [ ] Queue job with Celery
- [ ] Return job_id immediately
- [ ] Add request validation
- [ ] Add rate limiting

### Task 3.2: POST /edit Endpoint
- [ ] Accept job_id and edit description
- [ ] Load original scene config
- [ ] Call LLM service for edit
- [ ] Create new render job
- [ ] Return new job_id
- [ ] Handle case where original job doesn't exist

### Task 3.3: GET /status/{job_id} Endpoint
- [ ] Query job status from database/cache
- [ ] Return status and metadata
- [ ] If completed, include result URLs
- [ ] If failed, include error message
- [ ] Add polling recommendations in response

### Task 3.4: Additional Endpoints
- [ ] GET /result/{job_id} - Direct file download
- [ ] GET /thumbnail/{job_id} - Thumbnail image
- [ ] DELETE /job/{job_id} - Cancel/cleanup job
- [ ] GET /templates - List available visualization types

---

## Phase 4: Storage & State Management (Day 5)

### Task 4.1: Job State Storage
- [ ] Set up Redis for job status tracking
- [ ] Implement job CRUD operations
- [ ] Add TTL for completed jobs
- [ ] Implement job cleanup mechanism

### Task 4.2: File Storage
- [ ] Configure output directory structure
  - /outputs/{job_id}/video.mp4
  - /outputs/{job_id}/thumbnail.png
  - /outputs/{job_id}/config.json
- [ ] Implement file serving
- [ ] Add cleanup for old files (configurable retention)
- [ ] (Optional) Add S3/cloud storage support

### Task 4.3: Caching
- [ ] Cache scene configs by content hash
- [ ] Cache LLM responses for identical requests
- [ ] Implement cache invalidation strategy

---

## Phase 5: Testing & Refinement (Day 6)

### Task 5.1: Unit Tests
- [ ] Test scene generation for each template
- [ ] Test LLM prompt parsing
- [ ] Test config validation
- [ ] Test API request/response models

### Task 5.2: Integration Tests
- [ ] Test full generate flow
- [ ] Test edit flow
- [ ] Test concurrent requests
- [ ] Test error handling paths

### Task 5.3: Manual Testing
- [ ] Test variety of mathematical functions
- [ ] Test edge cases (invalid input, complex expressions)
- [ ] Test natural language editing
- [ ] Test integration with frontend (with Tanner)
- [ ] Performance testing (render times)

---

## Phase 6: Polish & Documentation (Day 7)

### Task 6.1: Error Messages & UX
- [ ] Improve error messages for common issues
- [ ] Add helpful suggestions in errors
- [ ] Validate and improve status messages
- [ ] Add progress percentage if possible

### Task 6.2: Documentation
- [ ] API documentation (OpenAPI/Swagger)
- [ ] README with setup instructions
- [ ] Example requests and responses
- [ ] Troubleshooting guide
- [ ] Docker deployment guide

### Task 6.3: Configuration
- [ ] Environment variable configuration
- [ ] Quality/speed profiles (low/medium/high)
- [ ] Configurable resource limits
- [ ] API key management (if needed)

### Task 6.4: Monitoring
- [ ] Add logging throughout
- [ ] Log render times and success rates
- [ ] Add healthcheck endpoint
- [ ] (Optional) Add metrics endpoint for Prometheus

---

## Integration Tasks (Throughout)

### With Frontend (Tanner)
- [ ] Provide API endpoint documentation
- [ ] Test CORS configuration
- [ ] Implement WebSocket for real-time updates (optional)
- [ ] Coordinate response format needs

### With Narrator (Remi)
- [ ] Define metadata format for timing
- [ ] Provide scene duration/segment info
- [ ] Test video format compatibility
- [ ] Coordinate on synchronization needs

---

## Optional Enhancements (If Time Permits)

### Advanced Visualizations
- [ ] 3D surface plots
- [ ] Complex number visualizations
- [ ] Parametric surfaces
- [ ] Group theory visualizations (Cayley tables, etc.)

### Performance Optimizations
- [ ] Parallel rendering for multiple quality outputs
- [ ] Preview generation (low quality, fast)
- [ ] Smart caching for similar requests
- [ ] GPU acceleration (if available)

### Features
- [ ] Custom color schemes
- [ ] Animation speed control
- [ ] Multiple scenes in one video
- [ ] Export formats (GIF, WebM)
- [ ] Batch generation endpoint

---

## File Structure

```
math-visualizer/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── .env.example
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py      # Pydantic request models
│   │   ├── responses.py     # Pydantic response models
│   │   └── scene_config.py  # Scene configuration models
│   ├── api/
│   │   ├── __init__.py
│   │   ├── generate.py      # /generate endpoint
│   │   ├── edit.py          # /edit endpoint
│   │   └── status.py        # /status endpoint
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py   # Claude API integration
│   │   ├── render_service.py # Manim rendering
│   │   ├── storage_service.py # File management
│   │   └── job_service.py   # Job state management
│   ├── manim_scenes/
│   │   ├── __init__.py
│   │   ├── base.py          # Base scene class
│   │   ├── function_graph.py
│   │   ├── geometric.py
│   │   ├── vector.py
│   │   └── templates.py     # Scene factory
│   ├── workers/
│   │   ├── __init__.py
│   │   └── render_worker.py # Celery worker
│   └── utils/
│       ├── __init__.py
│       ├── validation.py    # Input validation
│       └── safety.py        # Security checks
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_scenes.py
│   └── test_llm_service.py
└── outputs/                 # Generated files (volume mount)
```

---

## Daily Breakdown (7-day timeline)

**Day 1**: Setup, Docker, basic API structure
**Day 2**: Manim templates and scene configuration
**Day 3**: LLM integration and validation
**Day 4**: API endpoints implementation
**Day 5**: Storage, caching, state management
**Day 6**: Testing and debugging
**Day 7**: Polish, documentation, integration testing

---

## Notes for Claude Code

When implementing this with Claude Code:
- Start with the file structure and Dockerfile
- Build incrementally, testing each component
- Use `manim-sideview` for quick previews during development
- Test with simple functions first (e.g., `f(x) = x^2`)
- Keep LLM prompts in separate files for easy iteration
- Use environment variables for API keys and config
- Log extensively for debugging
