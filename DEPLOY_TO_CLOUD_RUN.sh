#!/bin/bash

# TechScopeAI Cloud Run Deployment Script
# Run this script step by step, or execute the entire script

set -e  # Exit on error

# ============================================
# STEP 1: SET YOUR PROJECT VARIABLES
# ============================================
export PROJECT_ID=techscopeai-prod  # CHANGE THIS to your project ID
export REGION=us-central1           # CHANGE THIS if needed
export BACKEND_SERVICE=techscopeai-api
export FRONTEND_SERVICE=techscopeai-web

echo "🚀 Starting deployment for project: $PROJECT_ID"
echo "📍 Region: $REGION"
echo ""

# ============================================
# STEP 2: INITIAL GCP SETUP (One-time only)
# ============================================
echo "📋 Step 2: Setting up GCP project..."
echo "⚠️  Skip this step if you've already done it"

# Uncomment these if creating a new project:
# gcloud projects create $PROJECT_ID
# gcloud config set project $PROJECT_ID

gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Authenticate (if not already done)
echo "Authenticating..."
gcloud auth login
gcloud auth application-default login

# Create Artifact Registry
echo "Creating Artifact Registry..."
gcloud artifacts repositories create techscopeai-repo \
  --repository-format=docker \
  --location=$REGION \
  --description="TechScopeAI Docker images" \
  2>/dev/null || echo "Repository already exists"

echo "✅ GCP setup complete!"
echo ""

# ============================================
# STEP 3: STORE SECRETS (One-time only)
# ============================================
echo "📋 Step 3: Storing secrets..."
echo "⚠️  Make sure to set all your API keys in this script before running!"

# Set your API keys here (REPLACE WITH YOUR ACTUAL KEYS)
OPENAI_API_KEY="${OPENAI_API_KEY:-your-openai-api-key}"
GEMINI_API_KEY="${GEMINI_API_KEY:-AIzaSyDsGwBgkR3alhi5x2alZdQBNv6RH-rJsfA}"
GAMMA_API_KEY="${GAMMA_API_KEY:-sk-gamma-F0lUhCRTTl62BffH3dNbO6ww1CM17NG3SUdIpVZFs}"
WEAVIATE_API_KEY="${WEAVIATE_API_KEY:-Um9WbWtlUC9QaTVEaEFwaF9XNWhVQ3JNUy9YVzZqZm05dUpvMDNpZGZ0c2g4bjRhdFBKSDBMUE9kOWNVPV92MjAw}"
WEAVIATE_URL="${WEAVIATE_URL:-tk2mnu2kqsw8n6wujmz89a.c0.us-west3.gcp.weaviate.cloud}"
PEXELS_API_KEY="${PEXELS_API_KEY:-4SsxbY5b5wpA0K5JHyW3Slw5ZIHMAc8iVfL3RMvFgWDNlO09guTcRxuu}"
# Hugging Face token (used to avoid HF rate limits when loading models)
HF_TOKEN="${HF_TOKEN:-}"

# Store API keys in Secret Manager
echo "Storing secrets in Secret Manager..."

echo -n "$OPENAI_API_KEY" | gcloud secrets create openai-api-key --data-file=- 2>/dev/null || \
  (echo "Updating openai-api-key..." && echo -n "$OPENAI_API_KEY" | gcloud secrets versions add openai-api-key --data-file=-)

echo -n "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=- 2>/dev/null || \
  (echo "Updating gemini-api-key..." && echo -n "$GEMINI_API_KEY" | gcloud secrets versions add gemini-api-key --data-file=-)

echo -n "$GAMMA_API_KEY" | gcloud secrets create gamma-api-key --data-file=- 2>/dev/null || \
  (echo "Updating gamma-api-key..." && echo -n "$GAMMA_API_KEY" | gcloud secrets versions add gamma-api-key --data-file=-)

echo -n "$WEAVIATE_API_KEY" | gcloud secrets create weaviate-api-key --data-file=- 2>/dev/null || \
  (echo "Updating weaviate-api-key..." && echo -n "$WEAVIATE_API_KEY" | gcloud secrets versions add weaviate-api-key --data-file=-)

echo -n "$PEXELS_API_KEY" | gcloud secrets create pexels-api-key --data-file=- 2>/dev/null || \
  (echo "Updating pexels-api-key..." && echo -n "$PEXELS_API_KEY" | gcloud secrets versions add pexels-api-key --data-file=-)

# Grant Cloud Run access to secrets
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

for secret in openai-api-key gemini-api-key gamma-api-key weaviate-api-key pexels-api-key; do
  gcloud secrets add-iam-policy-binding $secret \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor" \
    2>/dev/null || echo "IAM policy already set for $secret"
done

echo "✅ Secrets stored!"
echo ""

# ============================================
# STEP 4: DEPLOY BACKEND
# ============================================
echo "📋 Step 4: Deploying backend..."
cd /Users/akshtalati/Desktop/FinalProject/TechScopeAI

# Authenticate Docker
gcloud auth configure-docker $REGION-docker.pkg.dev

# Build and push backend image
echo "Building and pushing backend image..."
gcloud builds submit --tag $REGION-docker.pkg.dev/$PROJECT_ID/techscopeai-repo/$BACKEND_SERVICE:latest \
  --file backend/Dockerfile .

# Deploy backend to Cloud Run
echo "Deploying backend to Cloud Run..."
gcloud run deploy $BACKEND_SERVICE \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/techscopeai-repo/$BACKEND_SERVICE:latest \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --set-secrets OPENAI_API_KEY=openai-api-key:latest,GEMINI_API_KEY=gemini-api-key:latest,GAMMA_API_KEY=gamma-api-key:latest,WEAVIATE_API_KEY=weaviate-api-key:latest,PEXELS_API_KEY=pexels-api-key:latest \
  --set-env-vars USE_WEAVIATE_QUERY_AGENT=true,WEAVIATE_URL=$WEAVIATE_URL,HF_TOKEN=$HF_TOKEN \
  --port 8000

# Get backend URL
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region $REGION --format 'value(status.url)')
echo "✅ Backend deployed!"
echo "🔗 Backend URL: $BACKEND_URL"
echo ""

# ============================================
# STEP 5: DEPLOY FRONTEND
# ============================================
echo "📋 Step 5: Deploying frontend..."

# Build and push frontend image with API URL
echo "Building and pushing frontend image..."
gcloud builds submit \
  --tag $REGION-docker.pkg.dev/$PROJECT_ID/techscopeai-repo/$FRONTEND_SERVICE:latest \
  --file frontend/Dockerfile \
  --substitutions=_VITE_API_BASE_URL=$BACKEND_URL/api .

# Deploy frontend to Cloud Run
echo "Deploying frontend to Cloud Run..."
gcloud run deploy $FRONTEND_SERVICE \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/techscopeai-repo/$FRONTEND_SERVICE:latest \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60 \
  --max-instances 10 \
  --min-instances 0 \
  --port 80

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --region $REGION --format 'value(status.url)')
echo "✅ Frontend deployed!"
echo "🔗 Frontend URL: $FRONTEND_URL"
echo ""

# ============================================
# STEP 6: UPDATE BACKEND CORS
# ============================================
echo "📋 Step 6: Updating backend CORS with frontend URL..."
gcloud run services update $BACKEND_SERVICE \
  --region $REGION \
  --update-env-vars ALLOWED_ORIGINS=$FRONTEND_URL

echo "✅ CORS updated!"
echo ""

# ============================================
# DEPLOYMENT COMPLETE
# ============================================
echo "🎉 Deployment Complete!"
echo ""
echo "📊 Service URLs:"
echo "   Backend:  $BACKEND_URL"
echo "   Frontend: $FRONTEND_URL"
echo ""
echo "🧪 Test the deployment:"
echo "   curl $BACKEND_URL/health"
echo "   open $FRONTEND_URL"
echo ""
echo "📝 View logs:"
echo "   gcloud run services logs read $BACKEND_SERVICE --region $REGION"
echo "   gcloud run services logs read $FRONTEND_SERVICE --region $REGION"

