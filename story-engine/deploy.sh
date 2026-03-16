#!/bin/bash
# Quick deploy script for Cloud Run
# Usage: ./deploy.sh YOUR_PROJECT_ID YOUR_GEMINI_API_KEY

set -e

PROJECT_ID=project-ea7cea6d-6f87-4633-be3
GEMINI_API_KEY=AIzaSyBjBNM4gbe8pqV6chRjViszOwGJ-3DALO4
SERVICE_NAME="story-engine"
REGION="us-central1"
IMAGE="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 Deploying Story Engine to Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Region:  $REGION"

# set project
gcloud config set project $PROJECT_ID

# enable required APIs
echo "Enabling APIs..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  aiplatform.googleapis.com \
  --quiet

# build and push image
echo "Building Docker image..."
gcloud builds submit \
  --tag $IMAGE \
  --quiet

# deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "GEMINI_API_KEY=$GEMINI_API_KEY" \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 3 \
  --quiet

# get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --format "value(status.url)")

echo ""
echo "✅ Deployed successfully!"
echo "🌐 Service URL: $SERVICE_URL"
echo ""
echo "To verify deployment:"
echo "  curl $SERVICE_URL/health"
