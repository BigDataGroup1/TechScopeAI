#!/bin/bash

# TechScopeAI Cloud Run Deployment with All API Keys
# This script includes all your API keys

set -e  # Exit on error

# ============================================
# STEP 1: SET YOUR PROJECT VARIABLES
# ============================================
export PROJECT_ID=techscopeai 
export REGION=us-central1         
export BACKEND_SERVICE=techscopeai-api
export FRONTEND_SERVICE=techscopeai-web

# ============================================
# STEP 2: SET ALL YOUR API KEYS HERE
# ============================================
export OPENAI_API_KEY="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"
export GEMINI_API_KEY="AIzaSyDsGwBgkR3alhi5x2alZdQBNv6RH-rJsfA"
export GAMMA_API_KEY="sk-gamma-F0lUhCRTTl62BffH3dNbO6ww1CM17NG3SUdIpVZFs"
export WEAVIATE_API_KEY="WFdLekthYzIvYXJQaEhra19NK0tGUVluRmJiRU9YOGlkL1JkWGlqSEZyaW5xN3ZPYXNVemcwbDg5aUhrPV92MjAw"
export WEAVIATE_URL="tk2mnu2kqsw8n6wujmz89a.c0.us-west3.gcp.weaviate.cloud"
export PEXELS_API_KEY="4SsxbY5b5wpA0K5JHyW3Slw5ZIHMAc8iVfL3RMvFgWDNlO09guTcRxuu"
export USE_WEAVIATE_QUERY_AGENT="true"
echo "🚀 Starting deployment for project: $PROJECT_ID"
echo "📍 Region: $REGION"
echo ""

# ============================================
# STEP 3: INITIAL GCP SETUP
# ============================================
echo "📋 Step 3: Setting up GCP project..."
gcloud config set project $PROJECT_ID
echo "Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable artifactregistry.googleapis.com
echo "Authenticating..."
gcloud auth login
gcloud auth application-default login
echo "Creating Artifact Registry..."
gcloud artifacts repositories create techscopeai-repo \
  --repository-format=docker \
  --location=$REGION \
  --description="TechScopeAI Docker images" \
  2>/dev/null || echo "Repository already exists"

echo "✅ GCP setup complete!"
echo ""

# ============================================
# STEP 4: STORE ALL SECRETS
# ============================================
echo "📋 Step 4: Storing all secrets in Secret Manager..."
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
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
for secret in openai-api-key gemini-api-key gamma-api-key weaviate-api-key pexels-api-key; do
  echo "Setting IAM policy for $secret..."
  gcloud secrets add-iam-policy-binding $secret \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor" \
    2>/dev/null || echo "IAM policy already set for $secret"
done
echo "✅ All secrets stored!"
echo ""

# ============================================
# STEP 5: DEPLOY BACKEND
# ============================================
echo "📋 Step 5: Deploying backend..."
cd /Users/akshtalati/Desktop/FinalProject/TechScopeAI
echo "y" | gcloud auth configure-docker $REGION-docker.pkg.dev
echo "Building and pushing backend image..."
echo "y" | gcloud auth configure-docker $REGION-docker.pkg.dev
docker build -f backend/Dockerfile \
  -t $REGION-docker.pkg.dev/$PROJECT_ID/techscopeai-repo/$BACKEND_SERVICE:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/techscopeai-repo/$BACKEND_SERVICE:latest
echo "Deploying backend to Cloud Run..."
# Get frontend URL for CORS (will be set after frontend deployment, but we'll update it)
FRONTEND_URL="https://techscopeai-web-nsdjmmvvea-uc.a.run.app"

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
  --set-env-vars USE_WEAVIATE_QUERY_AGENT=true,WEAVIATE_URL=$WEAVIATE_URL,ALLOWED_ORIGINS=$FRONTEND_URL \
  --port 8000
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region $REGION --format 'value(status.url)')
echo "✅ Backend deployed!"
echo "🔗 Backend URL: $BACKEND_URL"
echo ""

# ============================================
# STEP 6: DEPLOY FRONTEND
# ============================================
echo "📋 Step 6: Deploying frontend..."

# Build and push frontend image with API URL
echo "Building and pushing frontend image..."
docker build -f frontend/Dockerfile \
  --build-arg _VITE_API_BASE_URL=$BACKEND_URL/api \
  -t $REGION-docker.pkg.dev/$PROJECT_ID/techscopeai-repo/$FRONTEND_SERVICE:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/techscopeai-repo/$FRONTEND_SERVICE:latest

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

# Get frontend URL (get the actual URL that will be used)
FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --region $REGION --format 'value(status.url)')
echo "✅ Frontend deployed!"
echo "🔗 Frontend URL: $FRONTEND_URL"
echo ""

# ============================================
# STEP 7: UPDATE BACKEND CORS
# ============================================
echo "📋 Step 7: Updating backend CORS with frontend URL..."
# Update CORS to use the actual frontend URL
gcloud run services update $BACKEND_SERVICE \
  --region $REGION \
  --update-env-vars ALLOWED_ORIGINS=$FRONTEND_URL

echo "✅ CORS updated with frontend URL: $FRONTEND_URL"
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

