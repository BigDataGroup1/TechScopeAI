# 🚀 Deploy TechScopeAI with Weaviate Cloud

This guide walks you through deploying TechScopeAI using:
- **Weaviate Cloud** (free tier) - Vector database
- **Railway / Render / Fly.io** - Backend hosting
- **Vercel / Netlify** (optional) - Frontend hosting

---

## 📋 Prerequisites

1. GitHub account (for deployment)
2. API keys ready:
   - OpenAI API key and/or Gemini API key
   - (Weaviate API key - you'll create this below)

---

## Step 1: Set Up Weaviate Cloud (Free) 🗄️

### 1.1 Create Account & Cluster

1. Go to **[console.weaviate.cloud](https://console.weaviate.cloud)**
2. Sign up (free)
3. Click **"Create cluster"**
4. Choose:
   - **Free Sandbox** (14-day trial, or free tier after)
   - Pick any region close to you
   - Name it something like `techscope`
5. Wait ~2 minutes for cluster to be ready

### 1.2 Get Your Credentials

Once your cluster is ready:

1. Click on your cluster
2. Copy the **Cluster URL** (looks like: `https://abc123.weaviate.cloud`)
3. Go to **API Keys** tab → Click **+ Add key**
4. Create a key with **Admin** access
5. Copy the **API Key** (save it somewhere safe!)

**Your Weaviate credentials:**
```
WEAVIATE_URL=https://your-cluster-id.weaviate.cloud
WEAVIATE_API_KEY=your-api-key-here
```

---

## Step 2: Deploy Backend (Choose One)

### Option A: Railway (Recommended) 🚂

Railway is the easiest for Docker deployments.

1. Go to **[railway.app](https://railway.app)** → Sign up with GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your TechScopeAI repository
4. Railway will auto-detect the Dockerfile

**Set environment variables in Railway dashboard:**

```
OPENAI_API_KEY=sk-your-key
GEMINI_API_KEY=your-gemini-key
USE_WEAVIATE_QUERY_AGENT=true
WEAVIATE_URL=https://your-cluster-id.weaviate.cloud
WEAVIATE_API_KEY=your-weaviate-api-key
ALLOWED_ORIGINS=https://your-frontend-url.vercel.app
```

5. Railway will build and deploy automatically
6. Get your backend URL (e.g., `https://techscopeai-production.up.railway.app`)

---

### Option B: Render 🎨

1. Go to **[render.com](https://render.com)** → Sign up
2. Click **"New"** → **"Web Service"**
3. Connect your GitHub repo
4. Settings:
   - **Environment**: Docker
   - **Dockerfile Path**: `backend/Dockerfile`
   - **Docker Context**: `.`
5. Add environment variables (same as Railway above)
6. Click **"Create Web Service"**

---

### Option C: Fly.io 🚀

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch (from project root)
fly launch --dockerfile backend/Dockerfile

# Set secrets
fly secrets set OPENAI_API_KEY=sk-your-key
fly secrets set GEMINI_API_KEY=your-gemini-key
fly secrets set USE_WEAVIATE_QUERY_AGENT=true
fly secrets set WEAVIATE_URL=https://your-cluster-id.weaviate.cloud
fly secrets set WEAVIATE_API_KEY=your-weaviate-api-key
fly secrets set ALLOWED_ORIGINS=https://your-frontend.vercel.app

# Deploy
fly deploy
```

---

## Step 3: Deploy Frontend (Optional)

### Option A: Vercel (Easiest)

1. Go to **[vercel.com](https://vercel.com)** → Sign up
2. Click **"Add New Project"** → Import your GitHub repo
3. Set:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite
4. Add environment variable:
   ```
   VITE_API_URL=https://your-backend-url.railway.app
   ```
5. Click **Deploy**

### Option B: Netlify

1. Go to **[netlify.com](https://netlify.com)** → Sign up
2. Click **"Add new site"** → **"Import an existing project"**
3. Connect GitHub repo
4. Settings:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`
5. Add environment variable:
   ```
   VITE_API_URL=https://your-backend-url.railway.app
   ```
6. Deploy!

---

## Step 4: Load Data into Weaviate Cloud 📊

Your Weaviate cluster is empty! You need to populate it with your RAG data.

### Option 1: Run Migration Script Locally

```bash
# Set environment variables
export USE_WEAVIATE_QUERY_AGENT=true
export WEAVIATE_URL=https://your-cluster-id.weaviate.cloud
export WEAVIATE_API_KEY=your-weaviate-api-key

# Run migration (from project root)
python migrate_postgres_to_weaviate.py
```

### Option 2: Use Test Data Script

```bash
python scripts/test_weaviate.py
```

---

## 🔧 Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | Yes (or GEMINI) |
| `GEMINI_API_KEY` | Google Gemini API key | Yes (or OPENAI) |
| `USE_WEAVIATE_QUERY_AGENT` | Enable Weaviate | Yes (`true`) |
| `WEAVIATE_URL` | Weaviate Cloud URL | Yes |
| `WEAVIATE_API_KEY` | Weaviate API key | Yes |
| `ALLOWED_ORIGINS` | Frontend URLs for CORS | Yes (in prod) |

---

## ✅ Verify Deployment

### Check Backend Health
```bash
curl https://your-backend-url.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "openai": true,
  "gemini": true,
  "weaviate": true
}
```

### Check Weaviate Connection
Visit your backend's `/docs` endpoint to test the API.

---

## 💰 Cost Estimate

| Service | Cost |
|---------|------|
| **Weaviate Cloud** | Free (sandbox) or ~$25/mo (production) |
| **Railway** | Free tier → ~$5-20/mo |
| **Render** | Free tier → ~$7/mo |
| **Vercel** | Free for hobby use |
| **Total** | $0-30/month |

---

## 🆘 Troubleshooting

### "Weaviate connection failed"
- Check your `WEAVIATE_URL` starts with `https://`
- Verify API key is correct (no extra spaces/newlines)
- Make sure cluster is running in Weaviate console

### "No results from RAG"
- Your Weaviate cluster might be empty
- Run the migration script to populate data

### CORS errors
- Add your frontend URL to `ALLOWED_ORIGINS`
- Format: `https://your-app.vercel.app` (no trailing slash)

---

## 🎉 You're Done!

Your TechScopeAI is now deployed with:
- ✅ Weaviate Cloud for vector search
- ✅ Backend on Railway/Render/Fly.io
- ✅ Frontend on Vercel/Netlify

No more managing database infrastructure!

