#!/bin/bash
# Usage: ./deploy.sh YOUR_PROJECT_ID YOUR_GEMINI_API_KEY

set -e

PROJECT_ID=${1:?"Usage: ./deploy.sh YOUR_PROJECT_ID YOUR_GEMINI_API_KEY"}
GEMINI_API_KEY=${2:?"Usage: ./deploy.sh YOUR_PROJECT_ID YOUR_GEMINI_API_KEY"}
SERVICE_NAME="story-engine"
REGION="us-central1"
IMAGE="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "Deploying Story Engine to Cloud Run..."
echo "Project: $PROJECT_ID"

gcloud config set project $PROJECT_ID

gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  containerregistry.googleapis.com aiplatform.googleapis.com --quiet

gcloud builds submit --tag $IMAGE --quiet

gcloud run deploy $SERVICE_NAME \
  --image $IMAGE \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "GEMINI_API_KEY=$GEMINI_API_KEY" \
  --memory 512Mi --cpu 1 \
  --min-instances 0 --max-instances 3 --quiet

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION --format "value(status.url)")

echo "Deployed: $SERVICE_URL"
