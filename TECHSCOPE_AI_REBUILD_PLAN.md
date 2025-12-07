TechScope AI - Agentic Co-Founder Rebuild Plan
Current State Assessment
✅ COMPLETED
Dataset Infrastructure (100% Complete)
Downloaders: Kaggle, HuggingFace, GitHub, RSS, HackerNews, Reddit, Article Scraper
Configuration: scripts/config/dataset_config.yaml with 30+ datasets
Download script: scripts/download_datasets.py with skip logic
Data downloaded: ~2GB across competitive, marketing, pitch, ip_legal, policy, team
Data Processing (Partial)
Product Hunt tagline extraction: scripts/extract_producthunt_taglines.py
Data assessment: scripts/assess_data_sufficiency.py
❌ NOT STARTED
Backend/FastAPI server
Agent implementations (6 agents + supervisor)
Shared Startup Workspace (JSON structure)
RAG infrastructure (ChromaDB, embeddings, retrieval)
Data processing pipeline (chunking, embedding, indexing)
Frontend (Streamlit/React)
Consistency checker
Report generator (PDF/Markdown)
Clarifying questions flow
MCP integration
---

Phase 1: Data Processing & RAG Infrastructure
1.1 Data Processing Pipeline
Location: scripts/processors/

Files to Create:

scripts/processors/__init__.py - Export all processors
scripts/processors/base_processor.py - Base class with common utilities
scripts/processors/competitive_processor.py - Process startup/competitor datasets
scripts/processors/marketing_processor.py - Process ad copy, taglines
scripts/processors/ip_legal_processor.py - Process privacy/IP datasets
scripts/processors/policy_processor.py - Process privacy policy datasets
scripts/processors/team_processor.py - Process job/skills datasets
scripts/processors/pitch_processor.py - Process pitch examples
Key Functions:

Clean text (remove noise, normalize)
Chunk with semantic boundaries (preserve context per agent)
Extract metadata (source, category, timestamp)
Output JSONL format: {text, metadata, chunk_id}
Output: data/processed/{agent_name}/*.jsonl

1.2 RAG Infrastructure Setup
Location: backend/app/rag/

Files to Create:

backend/app/rag/__init__.py
backend/app/rag/vector_store.py - ChromaDB wrapper
backend/app/rag/embeddings.py - Embedding generation (sentence-transformers)
backend/app/rag/retrieval.py - RAG retrieval logic
backend/app/rag/collections.py - Collection definitions
ChromaDB Collections:

competitors_corpus - Competitive analysis data
marketing_corpus - Marketing/ad copy data
ip_policy_corpus - IP/legal/privacy data
job_roles_corpus - Team/job data
pitch_examples_corpus - Pitch examples
Embedding Model: sentence-transformers/all-MiniLM-L6-v2 (384 dim)

Setup Script: scripts/setup_rag.py - Initialize ChromaDB, load processed data, generate embeddings

---

Phase 2: Backend Infrastructure
2.1 FastAPI Server
Location: backend/

Files to Create:

backend/main.py - FastAPI app entry point
backend/app/__init__.py
backend/app/config.py - Configuration (LLM keys, ChromaDB path)
backend/app/models/workspace.py - Startup Workspace Pydantic models
backend/app/api/__init__.py
backend/app/api/routes.py - API endpoints
backend/app/session_manager.py - Session lifecycle (ephemeral ChromaDB)
API Endpoints:

POST /api/session/init - Initialize session, return session_id
POST /api/session/{session_id}/clarifying-questions - Get/set clarifying questions
POST /api/session/{session_id}/workspace - Get current workspace
POST /api/session/{session_id}/agent/{agent_name}/run - Run specific agent
POST /api/session/{session_id}/consistency-check - Run consistency checker
POST /api/session/{session_id}/report/generate - Generate final report
DELETE /api/session/{session_id} - Delete session (cleanup ChromaDB)
2.2 Shared Startup Workspace
Location: backend/app/models/workspace.py

JSON Schema:

{
  "idea": {
    "one_liner": str,
    "problem": str,
    "solution": str,
    "target_user": str,
    "stage": str,  # "idea" | "mvp" | "early_revenue" | "scaling"
    "b2b_or_b2c": str  # "b2b" | "b2c" | "both"
  },
  "competition": {
    "score": float,  # 0-10
    "matrix": List[Dict],  # Competitor matrix
    "differentiation_points": List[str]
  },
  "marketing": {
    "strategy": str,
    "positioning": str,
    "assets": {
      "instagram": List[Dict],
      "ads": List[Dict],
      "youtube": Dict
    }
  },
  "ip_strategy": {
    "choice": str,  # "no_patent" | "provisional_later" | "defensive_publication"
    "posture": str,
    "notes": List[str]
  },
  "policies": {
    "privacy": str,
    "terms": str,
    "ai_statement": str,
    "tone": str  # "formal" | "friendly" | "minimalist"
  },
  "team": {
    "stage": str,
    "current_roles": List[str],
    "gaps": List[Dict]  # {title, reason, responsibilities}
  },
  "pitch": {
    "angle": str,  # "tech_first" | "product_first" | "market_first"
    "elevator": str,
    "long_form": str,
    "deck_outline": List[Dict]
  },
  "readiness": {
    "overall": float,
    "market": float,
    "team": float,
    "ip_policy": float,
    "pitch": float,
    "notes": List[str]
  }
}
Storage: In-memory dict per session (session_id → workspace)

---

Phase 3: Agent Implementations
3.1 Supervisor Agent
Location: backend/app/agents/supervisor.py

Responsibilities:

Initialize workspace from clarifying questions
Route to appropriate agents based on workspace state
Suggest next steps
Coordinate agent execution order
Trigger consistency checker
Key Methods:

ask_clarifying_questions() - Generate questions based on current workspace
suggest_next_agent() - Determine which agent to run next
orchestrate_workflow() - Execute agent playbook
3.2 Competitive Analysis Agent
Location: backend/app/agents/competitive.py

RAG Collection: competitors_corpus

Inputs: idea section from workspace

Outputs: Updates competition section:

Top N similar products
Competitor matrix (features, pricing, segment, channel, differentiator)
Score (0-10) on: problem clarity, differentiation, market crowdedness, monetization
Differentiation opportunities
LLM Prompt: Use RAG context + idea description → structured JSON output

3.3 Marketing & Content Agent
Location: backend/app/agents/marketing.py

RAG Collection: marketing_corpus

Inputs: idea + competition.differentiation_points

Outputs: Updates marketing section:

Positioning statement ("Notion for X" style)
2-3 marketing strategies (thought-leadership, paid performance, partnerships)
Content assets: 3 Instagram posts, 2 ad copies, 1 YouTube script
User Selection: Marketing strategy + favorite content angle

3.4 Patent/Legal Helper Agent
Location: backend/app/agents/ip_legal.py

RAG Collection: ip_policy_corpus

Inputs: idea (tech description, OSS components)

Outputs: Updates ip_strategy section:

IP posture classification
Things to document
OSS license concerns
Options (user selects): no patent, provisional later, defensive publication
Disclaimers: Always include "Not legal advice" warnings

3.5 Policy Drafting Agent
Location: backend/app/agents/policy.py

RAG Collection: ip_policy_corpus

Inputs: idea (product type, data handled, region)

Outputs: Updates policies section:

Draft Privacy Policy skeleton
Draft Terms of Service skeleton
Draft AI Use & Transparency Statement
User selects tone: formal, friendly, minimalist
Disclaimers: "Not legal advice. Please have counsel review."

3.6 Team Composition Agent
Location: backend/app/agents/team.py

RAG Collection: job_roles_corpus (optional, for examples)

Inputs: idea.stage, existing team roles, industry type

Logic: Rule-based matrix + optional RAG examples

Idea + non-technical → must-have: founding engineer + product/UX
MVP + technical → must-have: customer success / marketing
Regulated space → add: compliance / legal advisor
Outputs: Updates team section:

Missing roles with reasons
Mini job descriptions for each role
3.7 Pitch & Story Agent
Location: backend/app/agents/pitch.py

RAG Collection: pitch_examples_corpus

Inputs: Entire workspace (idea, competition, marketing, ip_strategy, policies, team)

Outputs: Updates pitch section:

1-2 elevator pitches (15-30 seconds)
1 longer meeting script (60-90 seconds)
Slide outline for deck (Problem, Solution, Why now, Market, Moat, Team, GTM, Ask)
User Selection: Pitch angle (tech-first, product-first, market-first)

3.8 Consistency Checker / Readiness Scorer
Location: backend/app/agents/consistency.py

Inputs: Entire workspace

Outputs: Updates readiness section:

Consistency checks (competition vs pitch, IP vs marketing, policy vs claims)
Readiness scores: overall, market, team, ip_policy, pitch
Notes on contradictions or gaps
Logic: LLM-based analysis + simple rule checks

---

Phase 4: Agent Base Infrastructure
4.1 Base Agent Class
Location: backend/app/agents/base.py

Base Class Features:

RAG retrieval method (query collection, get top-K chunks)
LLM call method (with prompt templates)
Workspace read/write methods
Error handling and logging
All agents inherit from this base class

4.2 Agent Manager
Location: backend/app/agents/manager.py

Responsibilities:

Register all agents
Route agent execution requests
Pass workspace slice to agents
Merge agent outputs back into workspace
Handle agent errors
---

Phase 5: Frontend
5.1 Streamlit UI (MVP)
Location: frontend/streamlit_app.py

Pages/Sections:

Onboarding: Clarifying questions form
Workspace View: Display current workspace state
Agent Selection: Buttons to run each agent
Results Display: Show agent outputs
Report Download: Generate and download PDF/Markdown
Alternative: React frontend in frontend/react/ (if preferred)

---

Phase 6: Report Generator
6.1 Report Generation
Location: backend/app/report_generator.py

Output Formats:

Markdown (structured sections)
PDF (using reportlab or weasyprint)
Sections:

Startup canvas (one-page summary)
Competitor matrix (table)
Readiness radar (scores visualization)
Draft policies (full text)
Team plan (roles + JDs)
Pitch (elevator + long-form + deck outline)
Actionable next steps (per section)
---

Phase 7: MCP Integration (Optional)
7.1 MCP Tools
Location: backend/app/mcp/

Tools to Integrate:

Web search (for patent abstracts, public docs)
File tools (for reading external documents)
Usage: Called by agents when needed (e.g., IP agent for patent search)

---

Implementation Order
Week 1: Data Processing & RAG
Build data processors (scripts/processors/)
Process all datasets → data/processed/
Set up ChromaDB infrastructure (backend/app/rag/)
Create setup script (scripts/setup_rag.py)
Index all collections with embeddings
Week 2: Backend Core
Create FastAPI server (backend/main.py)
Implement workspace models (backend/app/models/workspace.py)
Build session manager (backend/app/session_manager.py)
Create API routes (backend/app/api/routes.py)
Test API endpoints
Week 3: Agents
Build base agent class (backend/app/agents/base.py)
Implement Supervisor agent
Implement Competitive agent
Implement Marketing agent
Implement IP/Legal agent
Implement Policy agent
Implement Team agent
Implement Pitch agent
Implement Consistency checker
Week 4: Frontend & Polish
Build Streamlit frontend
Implement report generator
Add MCP integration (if needed)
End-to-end testing
Documentation
---

File Structure Summary
TechScopeAI/
├── backend/
│   ├── main.py
│   └── app/
│       ├── __init__.py
│       ├── config.py
│       ├── models/
│       │   └── workspace.py
│       ├── api/
│       │   └── routes.py
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── manager.py
│       │   ├── supervisor.py
│       │   ├── competitive.py
│       │   ├── marketing.py
│       │   ├── ip_legal.py
│       │   ├── policy.py
│       │   ├── team.py
│       │   ├── pitch.py
│       │   └── consistency.py
│       ├── rag/
│       │   ├── __init__.py
│       │   ├── vector_store.py
│       │   ├── embeddings.py
│       │   ├── retrieval.py
│       │   └── collections.py
│       ├── session_manager.py
│       ├── report_generator.py
│       └── mcp/ (optional)
├── frontend/
│   └── streamlit_app.py
├── scripts/
│   ├── processors/ (create)
│   ├── setup_rag.py (create)
│   └── ... (existing)
└── data/
    ├── raw/ (existing)
    └── processed/ (create)
---

Key Dependencies to Add
fastapi - Backend server
uvicorn - ASGI server
pydantic - Data validation
chromadb - Vector store
sentence-transformers - Embeddings
streamlit - Frontend (or React)
reportlab or weasyprint - PDF generation
openai or anthropic - LLM provider
---

Testing Strategy
Unit Tests: Each agent, processor, RAG component
Integration Tests: Agent → RAG → Workspace flow
End-to-End Tests: Full user flow (questions → agents → report)
Retrieval Quality Tests: RAG relevance for sample queries
---

Success Metrics
All 6 agents produce structured outputs
Supervisor coordinates workflow correctly
RAG retrieval returns relevant context
Workspace updates correctly across agents
Consistency checker flags contradictions
Report generator produces downloadable output
Frontend provides smooth user experience