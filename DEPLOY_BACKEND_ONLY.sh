#!/bin/bash

# TechScopeAI Backend Deployment (All Agents Fix)
# This fixes the PostgreSQL connection issue for ALL agents

set -e  # Exit on error

# ============================================
# SET VARIABLES
# ============================================
export PROJECT_ID=techscopeai
export REGION=us-central1
export BACKEND_SERVICE=techscopeai-api
export WEAVIATE_URL="tk2mnu2kqsw8n6wujmz89a.c0.us-west3.gcp.weaviate.cloud"

echo "🚀 Deploying backend with Weaviate-only configuration..."
echo "📍 Region: $REGION"
echo "🔗 Weaviate URL: $WEAVIATE_URL"
echo ""

# ============================================
# AUTHENTICATE DOCKER
# ============================================
echo "📋 Authenticating Docker with GCP..."
echo "y" | gcloud auth configure-docker $REGION-docker.pkg.dev

# ============================================
# BUILD BACKEND IMAGE
# ============================================
echo "📋 Building backend image..."
cd /Users/akshtalati/Desktop/FinalProject/TechScopeAI
gcloud builds submit \
  --tag $REGION-docker.pkg.dev/$PROJECT_ID/techscopeai-repo/$BACKEND_SERVICE:latest \
  --file backend/Dockerfile .

# ============================================
# DEPLOY TO CLOUD RUN
# ============================================
echo "📋 Deploying backend to Cloud Run..."
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
  --set-env-vars USE_WEAVIATE_QUERY_AGENT=true,WEAVIATE_URL=$WEAVIATE_URL \
  --port 8000

# ============================================
# GET BACKEND URL
# ============================================
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region $REGION --format 'value(status.url)')
echo ""
echo "✅ Backend deployed successfully!"
echo "🔗 Backend URL: $BACKEND_URL"
echo ""
echo "📝 All agents (Pitch, Marketing, Patent, Policy, Team, Competitive) should now work!"
echo "   They will use Weaviate QueryAgent instead of PostgreSQL."
