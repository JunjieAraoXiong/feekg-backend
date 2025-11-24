# FE-EKG Backend

Financial Event Evolution Knowledge Graph with RAG-enhanced Agent-Based Modeling for crisis simulation.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Overview

Implementation of the FE-EKG system based on:
> "Risk identification and management through knowledge Association: A financial event evolution knowledge graph approach" (Liu et al., 2024)

**Key Features:**
- Three-layer knowledge graph (Entity → Event → Risk)
- 6 event evolution algorithms
- RAG pipeline with 440K+ document chunks
- Agent-based crisis simulation with SLM-powered decision making

**Data:** 4,000 real Capital IQ events from 2007-2009 Lehman Brothers crisis

**Frontend:** [feekg-frontend](https://github.com/JunjieAraoXiong/feekg-frontend)

## Architecture

```
Risk Layer      [LiquidityRisk] ──> [CreditRisk]
                       ↑
Event Layer     [DebtDefault] ──evolves──> [CreditDowngrade]
                       ↑                           ↑
Entity Layer    [LehmanBros] ─────────────> [MorganStanley]
```

## Tech Stack

- **Database:** AllegroGraph (RDF/SPARQL)
- **API:** Flask + CORS
- **RAG:** ChromaDB + BGE embeddings + Reranker
- **ABM:** Mesa framework
- **SLM:** Llama 3.2 1B

## Quick Start

### 1. Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure

Create `.env` with AllegroGraph credentials:

```bash
AG_URL=https://your-instance.com/
AG_USER=your_user
AG_PASS=your_password
AG_CATALOG=mycatalog
AG_REPO=FEEKG
```

### 3. Run API

```bash
python api/app.py
# API available at http://localhost:5000
```

### 4. Test

```bash
curl http://localhost:5000/health
curl http://localhost:5000/api/entities
```

## Project Structure

```
feekg/
├── api/              # Flask REST API
├── abm/              # Agent-based model (Mesa)
├── rag/              # RAG pipeline (ChromaDB, embeddings)
├── slm/              # Small language model integration
├── evolution/        # 6 event evolution algorithms
├── query/            # SPARQL queries
├── ingestion/        # Data loading scripts
├── config/           # Configuration and secrets
├── data/             # Capital IQ data
└── results/          # Output visualizations
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /api/info` | Database stats |
| `GET /api/entities` | All entities (22) |
| `GET /api/events` | All events (4,000) |
| `GET /api/evolution/links` | Evolution relationships |
| `GET /api/graph/data` | Graph data for visualization |

## RAG Pipeline

The RAG system provides historical financial intelligence to ABM agents:

- **442K chunks** from JPM Weekly, BIS Reports, FT Archive, FCIC
- **BGE embeddings** (BAAI/bge-large-en-v1.5)
- **Reranker** (BAAI/bge-reranker-v2-m3)

```bash
# Run experiment
source .env && export PYTHONPATH=. && python run_experiment.py
```

## ABM Simulation

Compares RAG-enabled "insider" agents vs uninformed "noise trader" agents:

- **Group A (Bank 0-4):** RAG-enabled, historical context
- **Group B (Bank 5-9):** No RAG, hallucination-prone

Metrics: Survival rate, decision distribution, capital preservation

## Documentation

- [CLAUDE.md](CLAUDE.md) - Developer guide
- [docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md) - Project overview
- [docs/DATABASE_SETUP.md](docs/DATABASE_SETUP.md) - Database setup
- [rag/EVALUATION_PLAN.md](rag/EVALUATION_PLAN.md) - RAG evaluation

## References

- Liu et al. (2024) - FE-EKG paper
- [AllegroGraph](https://allegrograph.com/)
- [Mesa ABM](https://mesa.readthedocs.io/)
- [ChromaDB](https://www.trychroma.com/)

## License

MIT - Research and educational purposes.
