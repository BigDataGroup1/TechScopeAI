# TechScopeAI Source Code

This directory contains the core implementation of TechScopeAI's multi-agent system.

## 📁 Structure

```
src/
├── agents/          # Agent implementations
│   ├── base_agent.py      # Base class for all agents
│   └── pitch_agent.py     # Pitch deck agent (3 modes)
│
├── rag/             # RAG (Retrieval Augmented Generation) system
│   ├── embedder.py        # Text embeddings (sentence-transformers/OpenAI)
│   ├── vector_store.py    # FAISS vector database
│   └── retriever.py       # Document retrieval
│
├── api/             # Interfaces
│   └── chat_interface.py  # Streamlit web UI
│
└── data/            # User data storage
    └── user_companies/    # Company details JSON files
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

## 🔍 RAG System

### Embedder
- Generates text embeddings
- Supports: sentence-transformers (free) or OpenAI (paid)
- Default: `all-MiniLM-L6-v2` (384 dimensions)

### VectorStore
- FAISS-based vector database
- Stores embeddings and metadata
- Fast similarity search

### Retriever
- Semantic search over documents
- Returns relevant context with sources
- Filters by category

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

See `SETUP_PITCH_AGENT.md` for setup instructions.

