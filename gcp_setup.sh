#!/bin/bash

# GCP Setup Script for Mathemagician

set -e

echo "🎨 Mathemagician GCP Setup"
echo "=========================="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get current project
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo "❌ No GCP project set. Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "📋 Using GCP Project: $PROJECT_ID"
echo ""

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable \
    run.googleapis.com \
    storage.googleapis.com \
    cloudbuild.googleapis.com \
    --project=$PROJECT_ID

echo "✅ APIs enabled"
echo ""

# Create GCS bucket
BUCKET_NAME="mathemagician-outputs-${PROJECT_ID}"
echo "📦 Creating GCS bucket: $BUCKET_NAME"

if gsutil ls -b gs://$BUCKET_NAME 2>/dev/null; then
    echo "⚠️  Bucket already exists"
else
    gsutil mb -p $PROJECT_ID gs://$BUCKET_NAME
    echo "✅ Bucket created"
fi

# Set bucket permissions
echo "🔒 Setting bucket permissions..."
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME 2>/dev/null || true
echo ""

# Create service account (optional - Cloud Run can use default)
SERVICE_ACCOUNT="mathemagician-sa"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "👤 Checking service account..."
if gcloud iam service-accounts describe $SERVICE_ACCOUNT_EMAIL --project=$PROJECT_ID 2>/dev/null; then
    echo "⚠️  Service account already exists"
else
    echo "Creating service account: $SERVICE_ACCOUNT_EMAIL"
    gcloud iam service-accounts create $SERVICE_ACCOUNT \
        --display-name="Mathemagician API Service Account" \
        --project=$PROJECT_ID
    echo "✅ Service account created"
fi

# Grant permissions
echo "🔑 Granting Storage permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/storage.objectAdmin" \
    --condition=None \
    --quiet

echo ""
echo "✅ GCP Setup Complete!"
echo ""
echo "📝 Update your .env file with:"
echo "   GCP_PROJECT_ID=$PROJECT_ID"
echo "   GCS_BUCKET=$BUCKET_NAME"
echo ""
echo "🚀 Ready to deploy!"
echo ""
echo "To deploy to Cloud Run:"
echo "   ./deploy.sh"
echo ""
