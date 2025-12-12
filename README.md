# TechScopeAI: Intelligent System for Technical Startup Founders

A production-grade, cloud-native platform that combines RAG (Retrieval-Augmented Generation), multi-agent orchestration, and LLM failover to deliver comprehensive guidance for technical startup founders across pitch creation, competitive analysis, marketing, patents, policies, and team building.

## What It Does

TechScopeAI is an AI-powered platform that helps technical startup founders with essential tasks. Instead of generic AI responses, it uses a specialized knowledge base and multiple specialized agents to provide domain-specific, actionable guidance.

## Key Components

### 1. RAG (Retrieval-Augmented Generation) System
- **Knowledge Base**: Curated datasets from Kaggle, HuggingFace, GitHub, and other sources
- **Vector Search**: Uses Weaviate Cloud with HNSW indexing for fast similarity search
- **Domain Expertise**: Separate knowledge bases for competitors, marketing, IP/legal, policies, team building, and pitch examples
- **How it works**: Agents query the knowledge base before generating responses, ensuring answers are grounded in relevant startup knowledge

### 2. Multi-Agent Orchestration
- **Specialized Agents**: Each agent handles a specific domain:
  - **Pitch Agent**: Creates pitch decks, elevator pitches, and presentation slides. Integrates with Gamma.ai to generate professional presentations with automatic image enhancement via MCP Image Search. Supports multiple themes (startup-pitch, venture-capital, minimalist, modern-tech, executive)
  - **Competitive Agent**: Analyzes competitors and market positioning
  - **Marketing Agent**: Generates marketing strategies and content
  - **Patent Agent**: Conducts patent searches and IP analysis
  - **Policy Agent**: Drafts privacy policies and legal documents
  - **Team Agent**: Analyzes team needs and generates job descriptions
- **Coordinator Agent**: Orchestrates multiple agents for complex tasks
- **How it works**: Agents use RAG for context, MCP tools for external data, and LLMs for generation

### 3. MCP (Model Context Protocol) Tools
- **External Service Integration**: Connects agents to real-time data sources
- **Available Tools**:
  - **Web Search**: DuckDuckGo for real-time information
  - **Image Search**: Pexels/Unsplash for professional images (used by Pitch Agent for Gamma presentations)
  - **Patent Search**: USPTO database for IP research
  - **Content Extraction**: Web page content extraction
- **How it works**: Centralized tool server that agents call when they need external data, avoiding hardcoded API calls

## What Founders Get

- **Pitch Decks**: AI-generated pitch decks with professional visuals via Gamma.ai integration
- **Competitive Analysis**: Market positioning and competitor insights
- **Marketing Strategies**: Data-driven marketing recommendations
- **IP Guidance**: Patent searches and intellectual property advice
- **Legal Documents**: Privacy policies and compliance documents
- **Team Planning**: Job descriptions and team structure recommendations




TechScopeAI combines specialized knowledge, real-time data access, and multi-agent orchestration to provide technical startup founders with actionable, domain-specific guidance across all critical business areas.
---

## 🌐 Live Demo

### 👉 https://techscopeai-web-541402991388.us-central1.run.app/

---

## 📋 Project Resources

| Resource | Link |
|----------|------|
| **Live Application** | [TechScopeAI Web App](https://techscopeai-web-541402991388.us-central1.run.app/) |
| **GitHub Repository** | [BigDataGroup1/TechScopeAI](https://github.com/BigDataGroup1/TechScopeAI) |
| **Google Codelab** | [Project Documentation](#) |
| **Architecture Diagram** | [View on Eraser.io](https://app.eraser.io/workspace/oAEPgjs5TnrFlUA3olc2?origin=share) |

---

## 🛠️ Technologies

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React"/>
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript"/>
  <img src="https://img.shields.io/badge/Weaviate-FF6B6B?style=for-the-badge" alt="Weaviate"/>
  <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI"/>
  <img src="https://img.shields.io/badge/Google%20Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini"/>
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"/>
  <img src="https://img.shields.io/badge/Google%20Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white" alt="GCP"/>
  <img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white" alt="Vite"/>
</p>

---

## 🏗️ Architecture Diagram

![Architecture Diagram](architecture%20diagram.png)

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🎯 **Pitch Agent** | Generate pitch decks, elevator pitches, and investor-ready presentations and gamma ppt  |
| 📊 **Competitive Agent** | Analyze competitors and market positioning |
| 📱 **Marketing Agent** | Create marketing content and growth strategies |
| 💡 **Patent Agent** | Assess patentability and IP strategy |
| 📋 **Policy Agent** | Generate company policies and compliance documents |
| 👥 **Team Agent** | Team analysis and job description generation |
| 🔄 **LLM Failover** | Automatic switching between OpenAI GPT-4 and Google Gemini |
| 🗄️ **Weaviate RAG** | Semantic search across domain-specific knowledge bases |
| 🖼️ **MCP Tools** | Web search, image search (Pexels), patent search (USPTO) |

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### Step 1: Clone Repository

```bash
git clone https://github.com/BigDataGroup1/TechScopeAI.git
cd TechScopeAI
```

### Step 2: Environment Variables

```bash
cp env.example .env
```

Edit `.env` with your API keys:

```env
# LLM (at least one required)
OPENAI_API_KEY=your-openai-key
GEMINI_API_KEY=your-gemini-key

# Weaviate Cloud (required)
USE_WEAVIATE_QUERY_AGENT=true
WEAVIATE_URL=https://your-cluster.weaviate.cloud
WEAVIATE_API_KEY=your-weaviate-key

# Optional
PEXELS_API_KEY=your-pexels-key
GAMMA_API_KEY=your-gamma-key
```

### Step 3: Install Dependencies

```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
cd ..
```

### Step 4: Run Application

**Terminal 1 - Backend:**
```bash
python -m uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 5: Open Browser

Go to: **http://localhost:5173**

---

## 📁 Project Structure

```
TechScopeAI/
├── backend/              # FastAPI application
│   ├── api/routes/       # API endpoints
│   ├── services/         # Business logic
│   └── main.py           # Entry point
├── frontend/             # React + TypeScript
│   ├── src/pages/        # Page components
│   ├── src/services/     # API client
│   └── src/store/        # State management
├── src/
│   ├── agents/           # AI agents (pitch, marketing, etc.)
│   ├── rag/              # RAG pipeline (Weaviate)
│   └── mcp/              # MCP tools
├── docker-compose.yml
└── requirements.txt
```

---

## 👥 Team Contributions

| **Name** | **Contribution** |
|----------|------------------|
| Tapas Desai | 33.3% - Frontend Development, FastAPI backend, Cloud Run Deployment, |
| Aksh Ashish Talati | 33.3% - AI Agents Implementation, Weaviate Cloud , Cloud run deployment |
| Swathi Jinka Radhakrishna | 33.3% - RAG Pipeline, Weaviate cloud ,MCP integration, Cloud Run Deployment |

---

## 📝 Attestation

WE ATTEST THAT WE HAVEN'T USED ANY OTHER STUDENTS' WORK IN OUR ASSIGNMENT AND ABIDE BY THE POLICIES LISTED IN THE STUDENT HANDBOOK.

**Contribution Declaration:**
- All code written collaboratively with clear division of responsibilities
- External libraries and APIs properly attributed
- No code copied from previous course submissions or other teams

---

## 📄 License

This project is licensed under the MIT License.

---

<p align="center">
  <strong>Made with ❤️ by the TechScopeAI Team</strong>
</p>
