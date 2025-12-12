# Cloud Run Deployment Commands

## Quick Start

All files have been created! Follow these commands step by step.

---

## Step 1: Set Your Project Variables

```bash
export PROJECT_ID=techscopeai-prod  # CHANGE THIS
export REGION=us-central1
export BACKEND_SERVICE=techscopeai-api
export FRONTEND_SERVICE=techscopeai-web
```

---

## Step 2: Initial GCP Setup (One-time only)

```bash
# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Authenticate
gcloud auth login
gcloud auth application-default login

# Create Artifact Registry
gcloud artifacts repositories create techscopeai-repo \
  --repository-format=docker \
  --location=$REGION \
  --description="TechScopeAI Docker images"
```

---

## Step 3: Store Secrets (One-time only)

**⚠️ Replace the API keys with your actual keys!**

```bash
# Store OpenAI API key
echo -n "YOUR_OPENAI_API_KEY" | gcloud secrets create openai-api-key --data-file=-

# Store Gemini API key
echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-

# Grant Cloud Run access
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding openai-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## Step 4: Deploy Backend

```bash
cd /Users/akshtalati/Desktop/FinalProject/TechScopeAI

# Authenticate Docker
gcloud auth configure-docker $REGION-docker.pkg.dev

# Build and push backend image
gcloud builds submit --tag $REGION-docker.pkg.dev/$PROJECT_ID/techscopeai-repo/$BACKEND_SERVICE:latest \
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
  --set-secrets OPENAI_API_KEY=openai-api-key:latest,GEMINI_API_KEY=gemini-api-key:latest \
  --set-env-vars USE_WEAVIATE_QUERY_AGENT=true \
  --port 8000

# Get backend URL
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region $REGION --format 'value(status.url)')
echo "Backend URL: $BACKEND_URL"
```

---

## Step 5: Deploy Frontend

```bash
# Build and push frontend image (with API URL)
gcloud builds submit \
  --tag $REGION-docker.pkg.dev/$PROJECT_ID/techscopeai-repo/$FRONTEND_SERVICE:latest \
  --file frontend/Dockerfile \
  --substitutions=_VITE_API_BASE_URL=$BACKEND_URL/api .

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
echo "Frontend URL: $FRONTEND_URL"
```

---

## Step 6: Update Backend CORS

```bash
# Update backend to allow frontend origin
gcloud run services update $BACKEND_SERVICE \
  --region $REGION \
  --update-env-vars ALLOWED_ORIGINS=$FRONTEND_URL
```

---

## Testing

```bash
# Test backend health
curl $BACKEND_URL/health

# Open frontend in browser
open $FRONTEND_URL
```

---

## View Logs

```bash
# Backend logs
gcloud run services logs read $BACKEND_SERVICE --region $REGION --limit 50

# Frontend logs
gcloud run services logs read $FRONTEND_SERVICE --region $REGION --limit 50

# Follow logs in real-time
gcloud run services logs tail $BACKEND_SERVICE --region $REGION
```

---

## Update/Redploy

```bash
# Rebuild and redeploy backend
gcloud builds submit --tag $REGION-docker.pkg.dev/$PROJECT_ID/techscopeai-repo/$BACKEND_SERVICE:latest \
  --file backend/Dockerfile .
gcloud run deploy $BACKEND_SERVICE \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/techscopeai-repo/$BACKEND_SERVICE:latest \
  --region $REGION

# Rebuild and redeploy frontend
gcloud builds submit \
  --tag $REGION-docker.pkg.dev/$PROJECT_ID/techscopeai-repo/$FRONTEND_SERVICE:latest \
  --file frontend/Dockerfile \
  --substitutions=_VITE_API_BASE_URL=$BACKEND_URL/api .
gcloud run deploy $FRONTEND_SERVICE \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/techscopeai-repo/$FRONTEND_SERVICE:latest \
  --region $REGION
```

---

## Update Environment Variables

```bash
# Update backend env vars
gcloud run services update $BACKEND_SERVICE \
  --region $REGION \
  --update-env-vars KEY=value

# Update secrets
gcloud run services update $BACKEND_SERVICE \
  --region $REGION \
  --set-secrets OPENAI_API_KEY=openai-api-key:latest
```

---

## Alternative: Run the Deployment Script

You can also run the automated script:

```bash
cd /Users/akshtalati/Desktop/FinalProject/TechScopeAI

# Edit the script first to set your PROJECT_ID and API keys
nano DEPLOY_TO_CLOUD_RUN.sh

# Then run it
./DEPLOY_TO_CLOUD_RUN.sh
```

---

## Files Created

✅ `backend/Dockerfile` - Backend container definition
✅ `frontend/Dockerfile` - Frontend container definition  
✅ `frontend/nginx.conf` - Nginx configuration for frontend
✅ `backend/main.py` - Updated with production CORS support
✅ `frontend/src/services/api.ts` - Updated to use environment variable for API URL

---

## Troubleshooting

### Build fails
- Check that all files exist
- Verify Docker is running
- Check gcloud authentication

### Deployment fails
- Verify project ID is correct
- Check API quotas
- Review logs: `gcloud run services logs read $BACKEND_SERVICE --region $REGION`

### CORS errors
- Verify `ALLOWED_ORIGINS` is set correctly
- Check frontend URL matches backend CORS config

### Service not accessible
- Check service is deployed: `gcloud run services list --region $REGION`
- Verify `--allow-unauthenticated` flag is set

