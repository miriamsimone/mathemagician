#!/bin/bash

# Deploy pre-built image to Cloud Run

set -e

echo "🚀 Deploying Mathemagician to Cloud Run (from pre-built image)"
echo "=============================================================="
echo ""

# Load .env file if it exists
if [ -f .env ]; then
    echo "📄 Loading environment variables from .env"
    export $(grep -v '^#' .env | xargs)
fi

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo "❌ No GCP project set. Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "📋 Using GCP Project: $PROJECT_ID"

# Set region
REGION=${REGION:-us-central1}
echo "🌍 Region: $REGION"

# Service and image details
SERVICE_NAME="mathemagician"
REPO_NAME="mathemagician"
IMAGE_NAME="mathemagician"
IMAGE_TAG=${IMAGE_TAG:-latest}
BUCKET_NAME="mathemagician-outputs-${PROJECT_ID}"

# Check for Anthropic API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  Warning: ANTHROPIC_API_KEY not set. The service will not work without it."
    echo "Set it with: export ANTHROPIC_API_KEY=your-api-key"
    echo ""
fi

# Full image path
IMAGE_PATH="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "🐳 Image: $IMAGE_PATH"
echo ""

echo "🏗️  Deploying to Cloud Run..."
echo ""

# Deploy to Cloud Run from pre-built image
ENV_VARS="GCP_PROJECT_ID=${PROJECT_ID},GCS_BUCKET=${BUCKET_NAME},ENVIRONMENT=production,REDIS_HOST=localhost,REDIS_PORT=6379"

# Add Anthropic API key if set
if [ -n "$ANTHROPIC_API_KEY" ]; then
    ENV_VARS="${ENV_VARS},ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}"
fi

gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_PATH \
    --platform managed \
    --region $REGION \
    --memory 4Gi \
    --cpu 2 \
    --timeout 600 \
    --allow-unauthenticated \
    --port 8000 \
    --min-instances 1 \
    --max-instances 1 \
    --set-env-vars "$ENV_VARS" \
    --project=$PROJECT_ID

echo ""
echo "✅ Deployment complete!"
echo ""

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --project=$PROJECT_ID \
    --format 'value(status.url)')

echo "🎉 Your API is live at: $SERVICE_URL"
echo ""
echo "Test endpoints:"
echo "  Health: $SERVICE_URL/health"
echo "  Docs:   $SERVICE_URL/docs"
echo ""
