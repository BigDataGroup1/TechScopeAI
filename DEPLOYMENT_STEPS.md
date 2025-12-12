# TechScopeAI Deployment Steps

## ✅ Pre-Deployment Checklist

- [x] PostgreSQL completely removed from deployment
- [x] Code fix applied to skip PostgreSQL when Weaviate is enabled
- [x] All environment variables configured
- [x] All API keys stored in Secret Manager

## 🚀 Deployment Steps

### Option 1: Full Deployment (Recommended)

Run the complete deployment script:

```bash
cd /Users/akshtalati/Desktop/FinalProject/TechScopeAI
chmod +x DEPLOY_WITH_ALL_KEYS.sh
./DEPLOY_WITH_ALL_KEYS.sh
```

This will:
1. Set up GCP project and APIs
2. Store all secrets in Secret Manager
3. Build and deploy backend
4. Build and deploy frontend
5. Update CORS settings

### Option 2: Backend Only (If you just need to fix the competitive agent)

```bash
# Set variables
export PROJECT_ID=techscopeai
export REGION=us-central1
export BACKEND_SERVICE=techscopeai-api
export WEAVIATE_URL="tk2mnu2kqsw8n6wujmz89a.c0.us-west3.gcp.weaviate.cloud"

# Authenticate Docker
echo "y" | gcloud auth configure-docker $REGION-docker.pkg.dev

# Build backend image
gcloud builds submit \
  --tag $REGION-docker.pkg.dev/$PROJECT_ID/techscopeai-repo/$BACKEND_SERVICE:latest \
  --file backend/Dockerfile .

# Deploy backend
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

# Get backend URL
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region $REGION --format 'value(status.url)')
echo "✅ Backend deployed!"
echo "🔗 Backend URL: $BACKEND_URL"
```

### Option 3: Frontend Only (If backend is already deployed)

```bash
# Set variables
export PROJECT_ID=techscopeai
export REGION=us-central1
export FRONTEND_SERVICE=techscopeai-web
export BACKEND_URL=$(gcloud run services describe techscopeai-api --region us-central1 --format 'value(status.url)')

# Authenticate Docker
echo "y" | gcloud auth configure-docker $REGION-docker.pkg.dev

# Build frontend image
docker build -f frontend/Dockerfile \
  --build-arg _VITE_API_BASE_URL=$BACKEND_URL/api \
  -t $REGION-docker.pkg.dev/$PROJECT_ID/techscopeai-repo/$FRONTEND_SERVICE:latest .

# Push image
docker push $REGION-docker.pkg.dev/$PROJECT_ID/techscopeai-repo/$FRONTEND_SERVICE:latest

# Deploy frontend
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

# Update backend CORS
gcloud run services update techscopeai-api \
  --region $REGION \
  --update-env-vars ALLOWED_ORIGINS=$FRONTEND_URL
```

## 🔍 Verification

After deployment, test the competitive analysis:

1. Open your frontend URL
2. Login/Register
3. Go to Competitive Analysis page
4. Click "Run Competitive Analysis"
5. Should work without "Competitive agent not available" error

## 📝 Notes

- **PostgreSQL**: Completely removed from deployment. Only Weaviate is used.
- **Environment Variables**: 
  - `USE_WEAVIATE_QUERY_AGENT=true` - Enables Weaviate
  - `WEAVIATE_URL` - Your Weaviate Cloud URL
- **Secrets**: All API keys are stored in Secret Manager for security
