# Mathemagician - Deployment Guide

## Current Status

✅ **Completed:**
- Project structure and dependencies
- FastAPI application with CORS
- Redis job queue integration
- Manim function graph scene
- POST /generate endpoint
- GET /status/{job_id} endpoint
- Background render worker
- GCS upload integration
- Dockerfile and docker-compose.yml
- GCP setup scripts

🔄 **In Progress:**
- Docker build and local testing

⏳ **Pending:**
- Enable billing on `mathemagician-demo` GCP project
- Run `./gcp_setup.sh` to create GCS bucket
- Cloud Run deployment
- End-to-end testing

## Next Steps for Tonight's Demo

### Step 1: Test Locally with Docker

```bash
# Build (currently running in background)
docker-compose build

# Start services
docker-compose up

# Test in another terminal:
curl http://localhost:8000/health

# Generate a visualization
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"function": "sin(x)", "x_range": [-5, 5]}'

# Get the job_id from response, then check status:
curl http://localhost:8000/status/{job_id}
```

### Step 2: Enable GCP Billing

1. Go to: https://console.cloud.google.com/billing
2. Select project: `mathemagician-demo`
3. Link a billing account

### Step 3: Run GCP Setup

```bash
./gcp_setup.sh
```

This will:
- Enable required APIs (Cloud Run, Cloud Storage, Cloud Build)
- Create GCS bucket for outputs
- Set up service account with proper permissions

### Step 4: Deploy to Cloud Run

```bash
./deploy.sh
```

This deploys with:
- **Memory:** 4GB (needed for Manim rendering)
- **CPU:** 2 cores
- **Timeout:** 600s (10 minutes)
- **Concurrency:** Auto-scaling
- **Redis:** In-container (simple for tonight, can migrate to Cloud Memorystore Saturday)

### Step 5: Test Deployed API

```bash
# Get the Cloud Run URL from deploy output
SERVICE_URL="https://mathemagician-xxxxx.run.app"

# Health check
curl $SERVICE_URL/health

# Generate visualization
curl -X POST $SERVICE_URL/generate \
  -H "Content-Type: application/json" \
  -d '{"function": "cos(x)", "x_range": [-10, 10]}'

# Check status (replace job_id)
curl $SERVICE_URL/status/{job_id}
```

## Demo Script for Tonight

**What to show:**

1. **API Documentation** - Navigate to `$SERVICE_URL/docs`
   - Show interactive Swagger UI
   - Demonstrate `/generate` endpoint

2. **Generate a Visualization**
   ```bash
   curl -X POST $SERVICE_URL/generate \
     -H "Content-Type: application/json" \
     -d '{"function": "sin(x) + cos(x*2)", "x_range": [-6, 6]}'
   ```

3. **Poll for Status**
   ```bash
   # Every few seconds
   curl $SERVICE_URL/status/{job_id}
   ```

4. **Show the Result**
   - Open the `video_url` from the status response
   - Download and play the MP4

5. **Explain Saturday Additions**
   - "Right now you need to know the math function syntax"
   - "By Saturday, you'll be able to say: 'Show me a sine wave' and Claude will interpret it"
   - "We'll add geometric shapes, vectors, and editing capabilities"

## Architecture Overview

```
User Request
    ↓
FastAPI (/generate)
    ↓
Redis Job Queue
    ↓
Background Worker
    ↓
Manim Renderer → Video File
    ↓
Google Cloud Storage
    ↓
Signed URL → User
```

## Troubleshooting

### Docker Build Issues
```bash
# Clear cache and rebuild
docker-compose build --no-cache

# Check logs
docker-compose logs api
```

### Redis Connection Issues
```bash
# Check Redis is running
docker-compose ps

# View Redis logs
docker-compose logs redis
```

### Rendering Failures
```bash
# View worker logs
docker-compose logs -f api | grep "Worker"

# Check outputs directory
ls -la outputs/
```

### GCS Upload Issues
- Verify bucket exists: `gsutil ls`
- Check permissions: `./gcp_setup.sh`
- For local testing, GCS is optional (files stored in `outputs/`)

## Cloud Run Specific Notes

### Memory Requirements
- Manim rendering requires **4GB minimum**
- Consider 8GB for complex scenes (Saturday)

### Timeout
- Default timeout is 60s (too short)
- Set to 600s (10 minutes) for rendering
- Can increase to 3600s if needed

### Cold Starts
- First request may be slow (~30-60s)
- Consider Cloud Run min instances (costs $$) for demo

### Redis in Container
- **Tonight:** Simple in-container Redis
- **Saturday:** Migrate to Cloud Memorystore for persistence and reliability
  ```bash
  # Create Memorystore instance
  gcloud redis instances create math-viz-redis \
      --size=1 \
      --region=us-central1

  # Get IP and update REDIS_HOST env var
  ```

## Saturday Enhancement Checklist

- [ ] Migrate to Cloud Memorystore Redis
- [ ] Add Claude API integration for natural language
- [ ] Implement additional scene types
- [ ] Add POST /edit endpoint
- [ ] Improve scene styling
- [ ] Add progress WebSocket (optional)
- [ ] Performance monitoring
- [ ] Error recovery and retries

## Cost Estimates (GCP)

**Tonight (Demo):**
- Cloud Run: ~$0.50 (free tier likely covers it)
- Cloud Storage: < $0.10
- **Total: < $1**

**Saturday (With Memorystore):**
- Cloud Run: ~$2-5
- Cloud Storage: ~$0.50
- Cloud Memorystore (1GB): ~$5/day
- Claude API: ~$1-5 depending on usage
- **Total: ~$10-15/day**

## Contact Info for Team

**For Frontend (Tanner):**
- API Base URL: Will provide after deployment
- Swagger Docs: `{BASE_URL}/docs`
- CORS enabled for `localhost:3000` and `localhost:5173`

**For Narrator (Remi):**
- Video format: MP4 (H.264)
- Duration: ~5 seconds per scene
- Metadata: Can add timing info in job response (Saturday)

## Files Reference

- `main.py:26` - Worker startup
- `generate.py:14` - Generate endpoint
- `status.py:9` - Status endpoint
- `render_worker.py:38` - Main worker loop
- `renderer.py:20` - Manim rendering logic
- `gcs_storage.py:18` - GCS upload
- `job_queue.py:15` - Redis queue management
