# TechScopeAI Source Code

This directory contains the core implementation of TechScopeAI's multi-agent system and data processing pipeline.

## 📁 Structure

```
src/
├── agents/          # Agent implementations
│   ├── base_agent.py      # Base class for all agents
│   ├── pitch_agent.py     # Pitch deck agent (3 modes)
│   ├── competitive_agent.py
│   ├── marketing_agent.py
│   ├── patent_agent.py
│   ├── policy_agent.py
│   ├── team_agent.py
│   ├── coordinator_agent.py
│   └── supervisor_agent.py
│
├── rag/             # RAG (Retrieval Augmented Generation) system
│   ├── embedder.py        # Text embeddings (sentence-transformers/OpenAI)
│   ├── vector_store.py    # FAISS vector database
│   ├── retriever.py       # Document retrieval
│   ├── collections.py     # Vector collections management
│   ├── embeddings.py      # Embedding generation
│   ├── retrieval.py       # Advanced retrieval
│   └── setup_rag.py       # RAG setup utilities
│
├── processors/      # Data processing pipeline
│   ├── base_processor.py          # Base class with common utilities
│   ├── competitive_processor.py   # Competitive analysis data
│   ├── marketing_processor.py    # Marketing/ad copy data
│   ├── ip_legal_processor.py     # IP/Legal/privacy data
│   ├── policy_processor.py       # Policy documents
│   ├── team_processor.py         # Team/job data
│   └── pitch_processor.py        # Pitch examples
│
├── api/             # Interfaces
│   └── chat_interface.py  # Streamlit web UI
│
├── data/            # User data storage
│   └── user_companies/    # Company details JSON files
│
├── utils/           # Utility modules
│   ├── exporters.py      # Export functionality (PDF, PPTX)
│   └── image_fetcher.py  # Image fetching utilities
│
└── process_data.py  # Main data processing script
```

## 🤖 Agents

### BaseAgent
Base class providing:
- RAG integration
- LLM query interface
- Response formatting

### PitchAgent
Specialized agent for pitch decks with 3 modes:

1. **Generate from Company Details**
   - Input: Company information (JSON)
   - Output: Complete pitch deck

2. **Generate from Outline**
   - Input: Outline with sections and notes
   - Output: Complete pitch deck

3. **Evaluate Pitch**
   - Input: Existing pitch text
   - Output: Evaluation with scores, strengths, weaknesses, improvements

### Other Agents
- **CompetitiveAgent**: Analyzes competitors and market positioning
- **MarketingAgent**: Creates marketing content and social media posts
- **PatentAgent**: Patent research, filing, and IP strategy
- **PolicyAgent**: Legal policies, compliance, and regulations
- **TeamAgent**: Team building, job descriptions, hiring
- **CoordinatorAgent**: Manages knowledge base and context
- **SupervisorAgent**: Routes queries to appropriate agents

## 🔍 RAG System

### Embedder
- Generates text embeddings
- Supports: sentence-transformers (free) or OpenAI (paid)
- Default: `all-MiniLM-L6-v2` (384 dimensions)

### VectorStore
- FAISS-based vector database
- Stores embeddings and metadata
- Fast similarity search
- Also supports PostgreSQL with pgvector

### Retriever
- Semantic search over documents
- Returns relevant context with sources
- Filters by category

## 📊 Data Processing Pipeline

### Process All Datasets

```bash
# From project root
python -m src.process_data

# Or with custom paths
python -m src.process_data --raw-dir data/raw --output-dir data/processed
```

### Process Specific Agents

```bash
# Only competitive and marketing
python -m src.process_data --agents competitive marketing

# Only pitch data
python -m src.process_data --agents pitch
```

## What Each Processor Does

### Competitive Processor
- Processes startup/competitor datasets (CSV, JSON, JSONL)
- Extracts company information, descriptions, pitches
- Preserves full company context (one chunk per company)

### Marketing Processor
- Processes ad copy, taglines, creative content
- Handles Product Hunt taglines, ad creative datasets
- Processes review datasets (IMDB, Yelp, Amazon) for marketing insights

### IP/Legal Processor
- Processes PrivacyQA datasets (Q&A pairs)
- Processes OSS policy documents (markdown, text)
- Processes patent guide documents (HTML)

### Policy Processor
- Processes privacy policy documents (markdown, JSON)
- Handles annotated/compliance policy datasets
- Chunks by sections while preserving structure

### Team Processor
- Processes job skills datasets (CSV)
- Processes hiring guide articles (text, markdown)
- Extracts job descriptions, skills, responsibilities

### Pitch Processor
- Processes pitch examples (CSV, JSON)
- Processes blog articles (investor blogs, startup blogs, templates)
- Handles one-line pitches and full pitch examples

## Output Format

All processors output JSONL files with the following structure:

```json
{
  "text": "Chunk text content...",
  "metadata": {
    "agent": "competitive",
    "source": "data/raw/competitive/startup_data.csv",
    "source_file": "startup_data.csv",
    "chunk_id": "startup_data_0",
    "company_name": "Example Startup",
    "source_type": "csv",
    ...
  }
}
```

## Output Location

Processed data is saved to:
```
data/processed/
├── competitive/
│   └── competitive_data.jsonl
├── marketing/
│   └── marketing_data.jsonl
├── ip_legal/
│   └── ip_legal_data.jsonl
├── policy/
│   └── policy_data.jsonl
├── team/
│   └── team_data.jsonl
└── pitch/
    └── pitch_data.jsonl
```

## 💬 API

### Chat Interface (Streamlit)
- Web-based chat UI
- Company details form
- Real-time pitch generation/evaluation
- Source citations

## 📝 Usage

### Initialize Agent

```python
from src.rag.embedder import Embedder
from src.rag.vector_store import VectorStore
from src.rag.retriever import Retriever
from src.agents.pitch_agent import PitchAgent

# Initialize RAG
embedder = Embedder(use_openai=False)
vector_store = VectorStore(category="pitch", dimension=embedder.get_embedding_dimension())
retriever = Retriever(vector_store, embedder)

# Initialize agent
agent = PitchAgent(retriever)
```

### Generate Pitch

```python
# From company details
company_data = {
    "company_name": "MyStartup",
    "industry": "SaaS",
    "problem": "...",
    "solution": "..."
}
response = agent.generate_from_details(company_data)
```

### Evaluate Pitch

```python
pitch_text = "My startup solves..."
response = agent.evaluate_pitch(pitch_text)
```

## 🔧 Configuration

- **LLM Model**: Set in `PitchAgent.__init__(model="gpt-4-turbo-preview")`
- **Embeddings**: Set in `Embedder(use_openai=False)` for free embeddings
- **Top-K Retrieval**: Adjust in `retrieve_context(top_k=5)`

## 📚 Data Flow

1. **User Query** → Agent
2. **Agent** → Retriever (semantic search)
3. **Retriever** → VectorStore (find similar documents)
4. **Agent** → LLM (generate response with context)
5. **Agent** → User (formatted response with sources)

## 🚀 Next Steps

- See `SETUP_PITCH_AGENT.md` for agent setup instructions
- See `TECHSCOPE_AI_REBUILD_PLAN.md` for the full implementation plan
- After processing data, set up RAG infrastructure (ChromaDB or PostgreSQL with pgvector)
- Generate embeddings for all chunks
- Index into vector collections
