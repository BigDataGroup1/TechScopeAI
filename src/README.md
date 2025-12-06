# TechScope AI - Data Processing Pipeline

This directory contains the data processing pipeline for TechScope AI agents.

## Structure

```
src/
├── __init__.py
├── processors/
│   ├── __init__.py
│   ├── base_processor.py          # Base class with common utilities
│   ├── competitive_processor.py   # Competitive analysis data
│   ├── marketing_processor.py    # Marketing/ad copy data
│   ├── ip_legal_processor.py     # IP/Legal/privacy data
│   ├── policy_processor.py       # Policy documents
│   ├── team_processor.py         # Team/job data
│   └── pitch_processor.py       # Pitch examples
└── process_data.py               # Main processing script
```

## Usage

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

## Next Steps

After processing, the next step is to:
1. Set up RAG infrastructure (ChromaDB)
2. Generate embeddings for all chunks
3. Index into vector collections

See `TECHSCOPE_AI_REBUILD_PLAN.md` for the full implementation plan.








