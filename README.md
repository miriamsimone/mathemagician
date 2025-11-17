# Mathemagician 🎨

Math visualization API powered by Manim and FastAPI.

## Quick Start

### Local Development (Fast iteration without Docker)

```bash
# 1. Run setup script
./dev_setup.sh

# 2. Start Redis (if not already running)
brew services start redis
# or
docker run -d -p 6379:6379 redis:7-alpine

# 3. Activate virtual environment
source venv/bin/activate

# 4. Run the API
python app/main.py
# or
uvicorn app.main:app --reload

# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

**Note:** Local development without Docker won't have Manim installed (requires system dependencies). Use Docker for full rendering capabilities.

### Docker Development (Full functionality)

```bash
# Build and run with Docker Compose
docker-compose up --build

# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

## API Usage

### Generate a visualization

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "function": "sin(x)",
    "x_range": [-5, 5]
  }'

# Response:
# {
#   "job_id": "abc123-def456...",
#   "status": "queued",
#   "message": "Job queued successfully..."
# }
```

### Check job status

```bash
curl http://localhost:8000/status/{job_id}

# Response when completed:
# {
#   "job_id": "abc123-def456...",
#   "status": "completed",
#   "video_url": "https://storage.googleapis.com/...",
#   "thumbnail_url": "https://storage.googleapis.com/...",
#   ...
# }
```

## GCP Deployment

### Prerequisites

1. Enable billing for the GCP project:
   ```bash
   gcloud config set project mathemagician-demo
   # Go to console.cloud.google.com to enable billing
   ```

2. Run GCP setup:
   ```bash
   ./gcp_setup.sh
   ```

### Deploy to Cloud Run

```bash
./deploy.sh
```

The API will be deployed to Cloud Run with:
- 4GB memory
- 2 CPUs
- 10 minute timeout
- Auto-scaling

## Project Structure

```
mathemagician/
├── app/
│   ├── api/              # API endpoints
│   │   ├── generate.py   # POST /generate
│   │   └── status.py     # GET /status/{job_id}
│   ├── models/           # Pydantic models
│   ├── services/         # Business logic
│   │   ├── job_queue.py  # Redis job queue
│   │   ├── gcs_storage.py # Google Cloud Storage
│   │   └── renderer.py   # Manim rendering
│   ├── manim_scenes/     # Manim scene templates
│   │   └── function_graph.py
│   ├── workers/          # Background workers
│   │   └── render_worker.py
│   └── main.py           # FastAPI app
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── outputs/              # Local output files
```

## Environment Variables

See `.env.example` for all configuration options.

Key variables:
- `GCP_PROJECT_ID` - Your GCP project ID
- `GCS_BUCKET` - Cloud Storage bucket name
- `REDIS_HOST` - Redis host (localhost or Cloud Memorystore IP)
- `ANTHROPIC_API_KEY` - For natural language processing (Saturday feature)

## Development Workflow

1. **Fast iteration**: Use local dev without Docker for API changes
2. **Test rendering**: Use Docker Compose for full Manim testing
3. **Deploy**: Use Cloud Run for production deployment

## Tonight's Demo Checklist

- [x] Basic FastAPI app with health check
- [x] Function graph Manim scene
- [x] Redis job queue
- [x] POST /generate endpoint
- [x] GET /status endpoint
- [x] Background worker
- [x] GCS integration
- [ ] Docker build and test
- [ ] Cloud Run deployment
- [ ] End-to-end test

## Saturday Enhancements

- Natural language input using Claude API
- Additional scene types (geometric, vector, 3D)
- POST /edit endpoint
- Better styling and animations
- Performance optimizations

## Troubleshooting

### Manim not rendering
- Make sure you're using Docker (local dev doesn't have Manim dependencies)
- Check worker logs in Docker: `docker-compose logs -f api`

### Redis connection failed
- Local: `brew services start redis` or use Docker Compose
- Cloud Run: Set up Cloud Memorystore and update REDIS_HOST

### GCS upload failed
- Check credentials are configured
- Verify bucket permissions with `./gcp_setup.sh`
- For local dev, GCS is optional (files stored locally)

## License

MIT
