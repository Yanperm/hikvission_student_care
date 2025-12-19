#!/bin/bash

# Student Care System - Google Cloud Run Deployment Script

echo "🚀 Deploying Student Care System to Google Cloud Run..."

# Set variables
PROJECT_ID="solutions-4e649"
SERVICE_NAME="student-care-system"
REGION="asia-southeast1"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK not installed. Please install it first."
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Login to Google Cloud (if needed)
echo "🔐 Checking Google Cloud authentication..."
gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -1
if [ $? -ne 0 ]; then
    echo "Please login to Google Cloud:"
    gcloud auth login
fi

# Set project
echo "📋 Setting project: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable firestore.googleapis.com

# Build and deploy
echo "🏗️ Building and deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --max-instances 10 \
    --port 8080 \
    --set-env-vars "PYTHONUNBUFFERED=1"

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo "✅ Deployment completed!"
echo "🌐 Service URL: $SERVICE_URL"
echo "📊 Admin Panel: $SERVICE_URL/admin"
echo "⭐ Features: $SERVICE_URL/features"

echo ""
echo "📝 Next steps:"
echo "1. Set up Firebase credentials"
echo "2. Configure database in config.json"
echo "3. Upload student photos"
echo "4. Test the system"