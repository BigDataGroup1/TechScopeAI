# 🚀 TechScopeAI

> Multi-Agent Intelligence System for Technical Startup Founders

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen?style=for-the-badge)](https://techscopeai-web-541402991388.us-central1.run.app/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?style=flat-square)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61dafb.svg?style=flat-square)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?style=flat-square)](https://fastapi.tiangolo.com)
[![Weaviate](https://img.shields.io/badge/Weaviate-Cloud-orange.svg?style=flat-square)](https://weaviate.io)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178c6.svg?style=flat-square)](https://typescriptlang.org)

---

## 🌐 Live Demo

### **[👉 Click Here to Try TechScopeAI](https://techscopeai-web-541402991388.us-central1.run.app/)**

No setup required - just open and use!

---

## 📖 About

TechScopeAI is a multi-agent intelligence system designed to support founders of technical startups through structured, contextual, and low-risk guidance. The platform leverages **Retrieval-Augmented Generation (RAG)**, multiple specialized AI agents, and external tools to provide personalized advice across various domains.

---

## ✨ Features

| Agent | Description |
|-------|-------------|
| 🎯 **Pitch Agent** | Generate pitch decks, elevator pitches, and investor-ready presentations |
| 📊 **Competitive Agent** | Analyze competitors and market positioning |
| 📱 **Marketing Agent** | Create marketing content and growth strategies |
| 💡 **Patent Agent** | Assess patentability and IP strategy |
| 📋 **Policy Agent** | Generate company policies and compliance documents |
| 👥 **Team Agent** | Team analysis and job description generation |

### Key Capabilities

- 🔄 **Automatic LLM Failover** - Seamlessly switches between OpenAI GPT-4 and Google Gemini
- 🗄️ **Weaviate Cloud RAG** - Semantic search across domain-specific knowledge bases
- 🖼️ **MCP Tools** - Web search, image search (Pexels), patent search (USPTO)
- 📊 **Dual Export** - PowerPoint generation + Gamma.ai AI-designed presentations
- 🎨 **Modern UI** - React 18 with TypeScript and TailwindCSS

---

## 🏗️ Architecture

**[View Architecture Diagram →](https://app.eraser.io/workspace/oAEPgjs5TnrFlUA3olc2?origin=share)**

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│                    Vite + TypeScript + TailwindCSS               │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                           │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │  Pitch  │ │Marketing│ │Competit.│ │ Patent  │ │  Team   │   │
│  │  Agent  │ │  Agent  │ │  Agent  │ │  Agent  │ │  Agent  │   │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘   │
│       └───────────┴───────────┼───────────┴───────────┘         │
│                               ▼                                  │
│                    ┌─────────────────────┐                       │
│                    │    Base Agent       │                       │
│                    │  (RAG + LLM + MCP)  │                       │
│                    └─────────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
            ┌───────────┐ ┌───────────┐ ┌───────────┐
            │  Weaviate │ │  OpenAI/  │ │   MCP     │
            │   Cloud   │ │  Gemini   │ │  Tools    │
            └───────────┘ └───────────┘ └───────────┘
```

---

## 🛠️ Tech Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| React 18 | UI Framework |
| TypeScript | Type Safety |
| Vite | Build Tool |
| TailwindCSS | Styling |
| React Router | Navigation |
| Axios | HTTP Client |
| Lucide React | Icons |

### Backend
| Technology | Purpose |
|------------|---------|
| FastAPI | Web Framework |
| Python 3.10+ | Language |
| Pydantic | Data Validation |
| Uvicorn | ASGI Server |
| python-pptx | PowerPoint Generation |

### AI/ML
| Technology | Purpose |
|------------|---------|
| OpenAI GPT-4 | Primary LLM |
| Google Gemini 2.0 | Fallback LLM |
| Sentence-BERT | Embeddings (all-MiniLM-L6-v2) |
| Weaviate Cloud | Vector Database |

### Infrastructure
| Technology | Purpose |
|------------|---------|
| Docker | Containerization |
| Google Cloud Run | Hosting |
| Nginx | Frontend Server |
| Weaviate Cloud | Managed Vector DB |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Git
- API Keys (see below)

### Required API Keys

You'll need at least one LLM provider and Weaviate:

| Service | Where to Get | Required |
|---------|--------------|----------|
| OpenAI | https://platform.openai.com/api-keys | Yes (or Gemini) |
| Google Gemini | https://aistudio.google.com/app/apikey | Yes (or OpenAI) |
| Weaviate Cloud | https://console.weaviate.cloud | Yes |
| Pexels | https://www.pexels.com/api/ | Optional |

---

## 💻 Run on Your Machine

### Step 1: Clone the Repository

```bash
git clone https://github.com/BigDataGroup1/TechScopeAI.git
cd TechScopeAI
```

### Step 2: Set Up Environment Variables

```bash
# Copy the example env file
cp env.example .env
```

Edit `.env` and add your API keys:

```env
# LLM API Keys (at least one required)
OPENAI_API_KEY=sk-your-openai-key-here
GEMINI_API_KEY=your-gemini-api-key-here

# Weaviate Cloud (required)
USE_WEAVIATE_QUERY_AGENT=true
WEAVIATE_URL=https://your-cluster-id.weaviate.cloud
WEAVIATE_API_KEY=your-weaviate-api-key-here

# Optional
PEXELS_API_KEY=your-pexels-api-key
GAMMA_API_KEY=your-gamma-api-key
```

### Step 3: Install Backend Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### Step 5: Run the Application

**Terminal 1 - Start Backend:**
```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend
npm run dev
```

### Step 6: Open in Browser

Go to: **http://localhost:5173**

---

## 🔑 Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 | Yes (or Gemini) |
| `GEMINI_API_KEY` | Google Gemini API key | Yes (or OpenAI) |
| `WEAVIATE_URL` | Weaviate Cloud cluster URL | Yes |
| `WEAVIATE_API_KEY` | Weaviate API key | Yes |
| `USE_WEAVIATE_QUERY_AGENT` | Enable Weaviate (`true`) | Yes |
| `GAMMA_API_KEY` | Gamma.ai API for presentations | Optional |
| `PEXELS_API_KEY` | Pexels API for slide images | Optional |
| `ALLOWED_ORIGINS` | Frontend URLs for CORS | Production |
| `VITE_API_BASE_URL` | Backend API URL | Production |

---

## 🐳 Running with Docker

### Option 1: With Local Weaviate

```bash
# Start Weaviate container
docker-compose -f docker-compose.weaviate.yml up -d

# Then run backend and frontend as shown above
```

### Option 2: Build Docker Images

```bash
# Build backend
docker build -f backend/Dockerfile -t techscopeai-api .

# Build frontend
docker build -f frontend/Dockerfile -t techscopeai-web .

# Run
docker run -p 8000:8000 --env-file .env techscopeai-api
docker run -p 80:80 techscopeai-web
```

---

## ☁️ Deployment

### Google Cloud Run (Production)

See [DEPLOYMENT_STEPS.md](./DEPLOYMENT_STEPS.md) for full deployment guide.

### Railway (Easiest)

1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Add environment variables in dashboard
4. Deploy!

### Fly.io

```bash
fly launch --dockerfile backend/Dockerfile
fly secrets set OPENAI_API_KEY=<key> WEAVIATE_URL=<url> ...
fly deploy
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Register company |
| `GET` | `/api/auth/session` | Get current session |
| `POST` | `/api/pitch/deck` | Generate pitch deck |
| `POST` | `/api/pitch/elevator` | Generate elevator pitch |
| `POST` | `/api/marketing/content` | Generate marketing content |
| `POST` | `/api/competitive/analyze` | Competitive analysis |
| `POST` | `/api/patent/assess` | Patent assessment |
| `POST` | `/api/policy/generate` | Generate policies |
| `POST` | `/api/team/analyze` | Team analysis |
| `GET` | `/health` | Health check |

---

## 📁 Project Structure

```
TechScopeAI/
├── backend/                 # FastAPI application
│   ├── api/routes/          # API route handlers
│   ├── services/            # Business logic
│   ├── models/              # Pydantic schemas
│   └── main.py              # App entry point
├── frontend/                # React application
│   ├── src/
│   │   ├── pages/           # Page components
│   │   ├── components/      # Reusable components
│   │   ├── services/        # API client
│   │   └── store/           # State management
│   ├── vite.config.ts       # Vite configuration
│   └── package.json
├── src/
│   ├── agents/              # AI agents
│   │   ├── base_agent.py    # Base class with RAG + LLM
│   │   ├── pitch_agent.py   # Pitch deck generation
│   │   ├── marketing_agent.py
│   │   ├── competitive_agent.py
│   │   ├── patent_agent.py
│   │   ├── policy_agent.py
│   │   └── team_agent.py
│   ├── rag/                 # RAG pipeline
│   │   ├── retriever.py     # Weaviate retriever
│   │   ├── embeddings.py    # Sentence-BERT
│   │   └── vector_store.py
│   ├── mcp/                 # MCP tools
│   │   ├── client.py
│   │   └── tools/           # Web search, image search
│   └── utils/               # Utilities
│       ├── exporters.py     # PowerPoint export
│       └── gamma_integration.py
├── docker-compose.yml
├── docker-compose.weaviate.yml
├── requirements.txt
└── env.example
```

---

## 👥 Team

- Tapas Desai
- Aksh Ashish Talati
- Swathi Jinka Radhakrishana

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- [OpenAI](https://openai.com) - GPT-4 API
- [Google AI](https://ai.google.dev) - Gemini API
- [Weaviate](https://weaviate.io) - Vector Database
- [Pexels](https://pexels.com) - Stock Images API
- [Gamma.ai](https://gamma.app) - Presentation Design

---

<p align="center">
  <strong>Made with ❤️ by the TechScopeAI Team</strong>
</p>

<p align="center">
  <a href="https://techscopeai-web-541402991388.us-central1.run.app/">Live Demo</a> •
  <a href="https://github.com/BigDataGroup1/TechScopeAI">GitHub</a>
</p>
