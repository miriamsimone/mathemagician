#!/bin/bash

# Deploy to Cloud Run

set -e

echo "🚀 Deploying Mathemagician to Cloud Run"
echo "======================================="
echo ""

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo "❌ No GCP project set. Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "📋 Using GCP Project: $PROJECT_ID"

# Get bucket name
BUCKET_NAME="mathemagician-outputs-${PROJECT_ID}"

# Set region
REGION=${REGION:-us-central1}
echo "🌍 Region: $REGION"

# Service name
SERVICE_NAME="mathemagician"

echo ""
echo "🏗️  Building and deploying..."
echo ""

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --memory 4Gi \
    --cpu 2 \
    --timeout 600 \
    --allow-unauthenticated \
    --set-env-vars "GCP_PROJECT_ID=${PROJECT_ID}" \
    --set-env-vars "GCS_BUCKET=${BUCKET_NAME}" \
    --set-env-vars "ENVIRONMENT=production" \
    --set-env-vars "REDIS_HOST=localhost" \
    --set-env-vars "REDIS_PORT=6379" \
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
