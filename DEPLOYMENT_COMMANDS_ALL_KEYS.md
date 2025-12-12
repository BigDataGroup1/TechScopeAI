# Cloud Run Deployment Commands - With All API Keys

## Quick Start - All Commands in One Place

### Step 1: Set Project Variables

```bash
export PROJECT_ID=techscopeai-prod  # CHANGE THIS
export REGION=us-central1
export BACKEND_SERVICE=techscopeai-api
export FRONTEND_SERVICE=techscopeai-web
```

### Step 2: Set All Your API Keys

```bash
export OPENAI_API_KEY="your-openai-api-key"  # REPLACE THIS
export GEMINI_API_KEY="AIzaSyDsGwBgkR3alhi5x2alZdQBNv6RH-rJsfA"
export GAMMA_API_KEY="sk-gamma-F0lUhCRTTl62BffH3dNbO6ww1CM17NG3SUdIpVZFs"
export WEAVIATE_API_KEY="Um9WbWtlUC9QaTVEaEFwaF9XNWhVQ3JNUy9YVzZqZm05dUpvMDNpZGZ0c2g4bjRhdFBKSDBMUE9kOWNVPV92MjAw"
export WEAVIATE_URL="tk2mnu2kqsw8n6wujmz89a.c0.us-west3.gcp.weaviate.cloud"
export PEXELS_API_KEY="4SsxbY5b5wpA0K5JHyW3Slw5ZIHMAc8iVfL3RMvFgWDNlO09guTcRxuu"
```

### Step 3: One-time GCP Setup

```bash
gcloud config set project $PROJECT_ID
gcloud services enable cloudbuild.googleapis.com run.googleapis.com secretmanager.googleapis.com artifactregistry.googleapis.com
gcloud auth login
gcloud auth application-default login
gcloud artifacts repositories create techscopeai-repo --repository-format=docker --location=$REGION
```

### Step 4: Store All Secrets

```bash
# Store all API keys in Secret Manager
echo -n "$OPENAI_API_KEY" | gcloud secrets create openai-api-key --data-file=-
echo -n "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-
echo -n "$GAMMA_API_KEY" | gcloud secrets create gamma-api-key --data-file=-
echo -n "$WEAVIATE_API_KEY" | gcloud secrets create weaviate-api-key --data-file=-
echo -n "$PEXELS_API_KEY" | gcloud secrets create pexels-api-key --data-file=-

# Grant Cloud Run access to all secrets
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

for secret in openai-api-key gemini-api-key gamma-api-key weaviate-api-key pexels-api-key; do
  gcloud secrets add-iam-policy-binding $secret \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor"
done
```

### Step 5: Deploy Backend

```bash
cd /Users/akshtalati/Desktop/FinalProject/TechScopeAI

# Authenticate Docker
gcloud auth configure-docker $REGION-docker.pkg.dev

# Build and push backend
gcloud builds submit --tag $REGION-docker.pkg.dev/$PROJECT_ID/techscopeai-repo/$BACKEND_SERVICE:latest --file backend/Dockerfile .

# Deploy backend with ALL secrets and environment variables
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
echo "Backend URL: $BACKEND_URL"
```

### Step 6: Deploy Frontend

```bash
# Build and push frontend
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

### Step 7: Update Backend CORS

```bash
gcloud run services update $BACKEND_SERVICE \
  --region $REGION \
  --update-env-vars ALLOWED_ORIGINS=$FRONTEND_URL
```

---

## Or Use the Automated Script

The script `DEPLOY_WITH_ALL_KEYS.sh` has all your API keys pre-configured. Just:

1. Edit the script to add your OPENAI_API_KEY (if you have one):
```bash
nano DEPLOY_WITH_ALL_KEYS.sh
# Find the OPENAI_API_KEY line and replace "your-openai-api-key"
```

2. Run the script:
```bash
chmod +x DEPLOY_WITH_ALL_KEYS.sh
./DEPLOY_WITH_ALL_KEYS.sh
```

---

## Update Secrets Later

If you need to update any secret:

```bash
# Update a secret
echo -n "new-api-key-value" | gcloud secrets versions add secret-name --data-file=-

# Update the service to use the new version
gcloud run services update $BACKEND_SERVICE \
  --region $REGION \
  --set-secrets SECRET_NAME=secret-name:latest
```

---

## All Secrets Being Used

✅ `OPENAI_API_KEY` - OpenAI API (if you have one)
✅ `GEMINI_API_KEY` - Google Gemini API
✅ `GAMMA_API_KEY` - Gamma presentation API
✅ `WEAVIATE_API_KEY` - Weaviate vector database API key
✅ `WEAVIATE_URL` - Weaviate instance URL (environment variable)
✅ `PEXELS_API_KEY` - Pexels image API
✅ `USE_WEAVIATE_QUERY_AGENT` - Boolean flag (environment variable)

---

## Testing

```bash
# Test backend
curl $BACKEND_URL/health

# Test frontend
open $FRONTEND_URL
```

---

## View Logs

```bash
# Backend logs
gcloud run services logs read $BACKEND_SERVICE --region $REGION --limit 50

# Frontend logs  
gcloud run services logs read $FRONTEND_SERVICE --region $REGION --limit 50
```





# PowerShell Commands

cd C:\Users\akshtalati\Desktop\FinalProject\TechScopeAI

# Build the image
docker build -f backend/Dockerfile -t us-central1-docker.pkg.dev/techscopeai/techscopeai-repo/techscopeai-api:latest .

# Push the image
docker push us-central1-docker.pkg.dev/techscopeai/techscopeai-repo/techscopeai-api:latest

# Deploy to Cloud Run
gcloud run deploy techscopeai-api `
  --image us-central1-docker.pkg.dev/techscopeai/techscopeai-repo/techscopeai-api:latest `
  --region us-central1 `
  --platform managed `
  --allow-unauthenticated `
  --memory 4Gi `
  --cpu 2 `
  --timeout 300 `
  --max-instances 10 `
  --min-instances 0 `
  --set-secrets OPENAI_API_KEY=openai-api-key:latest,GEMINI_API_KEY=gemini-api-key:latest,GAMMA_API_KEY=gamma-api-key:latest,WEAVIATE_API_KEY=weaviate-api-key:latest,PEXELS_API_KEY=pexels-api-key:latest `
  --set-env-vars USE_WEAVIATE_QUERY_AGENT=true,WEAVIATE_URL=tk2mnu2kqsw8n6wujmz89a.c0.us-west3.gcp.weaviate.cloud `
  --port 8000

# Get backend URL
$BACKEND_URL = (gcloud run services describe techscopeai-api --region us-central1 --format 'value(status.url)').Trim()
Write-Host "✅ Backend deployed!"
Write-Host "🔗 Backend URL: $BACKEND_URL"



# Build the image
docker build -f backend/Dockerfile -t us-central1-docker.pkg.dev/techscopeai/techscopeai-repo/techscopeai-api:latest .

# Push the image
docker push us-central1-docker.pkg.dev/techscopeai/techscopeai-repo/techscopeai-api:latest

# Deploy to Cloud Run
gcloud run deploy techscopeai-api \
  --image us-central1-docker.pkg.dev/techscopeai/techscopeai-repo/techscopeai-api:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --set-secrets OPENAI_API_KEY=openai-api-key:latest,GEMINI_API_KEY=gemini-api-key:latest,GAMMA_API_KEY=gamma-api-key:latest,WEAVIATE_API_KEY=weaviate-api-key:latest,PEXELS_API_KEY=pexels-api-key:latest \
  --set-env-vars USE_WEAVIATE_QUERY_AGENT=true,WEAVIATE_URL=tk2mnu2kqsw8n6wujmz89a.c0.us-west3.gcp.weaviate.cloud \
  --port 8000

# Get backend URL
BACKEND_URL=$(gcloud run services describe techscopeai-api --region us-central1 --format 'value(status.url)')
echo "✅ Backend deployed!"
echo "🔗 Backend URL: $BACKEND_URL"