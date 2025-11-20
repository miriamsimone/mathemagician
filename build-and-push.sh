#!/bin/bash

# Build and push Docker image to Artifact Registry

set -e

echo "🏗️  Building and pushing Docker image to Artifact Registry"
echo "=========================================================="
echo ""

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

# Repository and image name
REPO_NAME="mathemagician"
IMAGE_NAME="mathemagician"
IMAGE_TAG=${IMAGE_TAG:-latest}

# Full image path
IMAGE_PATH="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "🐳 Image: $IMAGE_PATH"
echo ""

# Create Artifact Registry repository if it doesn't exist
echo "📦 Ensuring Artifact Registry repository exists..."
gcloud artifacts repositories describe $REPO_NAME \
    --location=$REGION \
    --project=$PROJECT_ID 2>/dev/null || \
gcloud artifacts repositories create $REPO_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="Mathemagician Docker images" \
    --project=$PROJECT_ID

echo ""
echo "🔨 Building Docker image using Cloud Build (AMD64 platform for Cloud Run)..."
# Use cloudbuild.yaml to specify platform for Cloud Run compatibility
gcloud builds submit \
    --config=cloudbuild.yaml \
    --substitutions=_IMAGE_PATH=$IMAGE_PATH \
    --timeout=20m

echo ""
echo "✅ Image pushed successfully!"
echo ""
echo "📍 Image location: $IMAGE_PATH"
echo ""
echo "To deploy this image, run:"
echo "  ./deploy-from-image.sh"
echo ""
