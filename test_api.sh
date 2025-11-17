#!/bin/bash

# API testing script

API_URL=${1:-"http://localhost:8000"}

echo "🧪 Testing Mathemagician API at $API_URL"
echo "=========================================="
echo ""

# Test health endpoint
echo "1️⃣  Testing health endpoint..."
HEALTH=$(curl -s "$API_URL/health")
echo "$HEALTH" | jq '.'

if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    exit 1
fi

echo ""

# Test generate endpoint
echo "2️⃣  Generating visualization: sin(x)..."
GENERATE_RESPONSE=$(curl -s -X POST "$API_URL/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "function": "sin(x)",
    "x_range": [-5, 5]
  }')

echo "$GENERATE_RESPONSE" | jq '.'

JOB_ID=$(echo "$GENERATE_RESPONSE" | jq -r '.job_id')

if [ "$JOB_ID" = "null" ] || [ -z "$JOB_ID" ]; then
    echo "❌ Failed to get job_id"
    exit 1
fi

echo "✅ Job created: $JOB_ID"
echo ""

# Poll for status
echo "3️⃣  Polling for status..."
MAX_ATTEMPTS=60
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    STATUS_RESPONSE=$(curl -s "$API_URL/status/$JOB_ID")
    STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status')

    echo -ne "\rAttempt $((ATTEMPT+1))/$MAX_ATTEMPTS - Status: $STATUS    "

    if [ "$STATUS" = "completed" ]; then
        echo ""
        echo "✅ Rendering completed!"
        echo ""
        echo "$STATUS_RESPONSE" | jq '.'
        echo ""

        VIDEO_URL=$(echo "$STATUS_RESPONSE" | jq -r '.video_url')
        echo "📹 Video URL: $VIDEO_URL"

        if [ "$VIDEO_URL" != "null" ]; then
            echo "✅ Test passed!"
            exit 0
        else
            echo "⚠️  No video URL in response"
            exit 1
        fi
    elif [ "$STATUS" = "failed" ]; then
        echo ""
        echo "❌ Rendering failed"
        echo "$STATUS_RESPONSE" | jq '.'
        exit 1
    fi

    ATTEMPT=$((ATTEMPT+1))
    sleep 2
done

echo ""
echo "⏱️  Timeout waiting for completion"
exit 1
