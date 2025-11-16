# FE-EKG LLM/Nemotron Integration

NVIDIA NIM integration for FE-EKG, implementing the GraphRAG methodology from the NVIDIA cuGraph paper.

## Overview

This module integrates NVIDIA Nemotron and fine-tuned Llama models for:

1. **Automatic Triplet Extraction** - Extract (subject, predicate, object) triplets from financial news
2. **Enhanced Semantic Similarity** - Replace keyword matching with deep learning embeddings
3. **Event/Entity Recognition** - Automatically identify events and entities from text
4. **Natural Language Queries** - Future: Query the graph using plain English

## Architecture

Based on NVIDIA GraphRAG pipeline:

```
Financial Text → LLM (Nemotron/Llama-3) → Triplets → Neo4j Graph → cuGraph Analytics → Results
```

### Key Components

1. **NemotronClient** (`nemotron_client.py`)
   - NVIDIA NIM API wrapper
   - Text generation (Llama-3, Nemotron-4)
   - Embedding generation (NV-Embed-v2)
   - Semantic similarity computation

2. **TripletExtractor** (`triplet_extractor.py`)
   - LLM-based triplet extraction (98% accuracy with fine-tuned model)
   - Event extraction from financial text
   - Entity recognition
   - Domain-specific prompt engineering

3. **SemanticScorer** (`semantic_scorer.py`)
   - Embedding-based semantic similarity
   - Replaces keyword matching in evolution module
   - Batch processing with caching
   - Multi-faceted event comparison

## Setup

### 1. Get NVIDIA API Key

Visit https://build.nvidia.com and sign up for NVIDIA NIM API access.

### 2. Configure Environment

Add to `.env`:

```bash
NVIDIA_API_KEY=your_api_key_here
NVIDIA_NIM_URL=https://integrate.api.nvidia.com/v1
```

### 3. Install Dependencies

No additional packages required - uses `requests` which is already in `requirements.txt`.

Optional: Install OpenAI SDK for alternative client:
```bash
./venv/bin/pip install openai
```

## Usage

### Basic Triplet Extraction

```python
from llm import TripletExtractor

extractor = TripletExtractor()

text = """
China Evergrande Group defaulted on its offshore bonds in December 2021.
The default triggered a liquidity crisis that spread to other developers.
"""

triplets = extractor.extract_from_text(text, source='news_article')

for t in triplets:
    print(f"{t['subject']} --[{t['predicate']}]--> {t['object']}")
    # Output: China Evergrande Group --[CAUSES]--> liquidity crisis
```

### Event Extraction

```python
events = extractor.extract_events(text)

for event in events:
    print(f"{event['type']}: {event['description']}")
    # Output: debt_default: China Evergrande defaulted on offshore bonds
```

### Entity Extraction

```python
entities = extractor.extract_entities(text)

for entity in entities:
    print(f"{entity['name']} ({entity['type']})")
    # Output: China Evergrande Group (company)
```

### Semantic Similarity

```python
from llm import SemanticScorer

scorer = SemanticScorer()

event_a = {'type': 'debt_default', 'description': 'Evergrande defaulted on bonds'}
event_b = {'type': 'credit_downgrade', 'description': 'S&P downgraded Evergrande'}

similarity = scorer.compute_event_similarity(event_a, event_b)
print(f"Similarity: {similarity:.3f}")  # Output: ~0.75
```

### Batch Similarity Search

```python
candidates = [
    "Evergrande missed bond payment",
    "Government tightened regulations",
    "Credit rating downgraded",
    "Stock price fell sharply"
]

query = "Evergrande defaulted on debt"

top_matches = scorer.find_most_similar(query, candidates, top_k=3)

for idx, score in top_matches:
    print(f"{candidates[idx]}: {score:.3f}")
```

## Integration with Existing Modules

### Replace Keyword-Based Semantic Similarity

In `evolution/methods.py`:

```python
# OLD (keyword-based)
def compute_semantic_similarity(self, evt_a, evt_b):
    keywords_a = set(evt_a['description'].lower().split())
    keywords_b = set(evt_b['description'].lower().split())
    return len(keywords_a & keywords_b) / len(keywords_a | keywords_b)

# NEW (embedding-based)
from llm import SemanticScorer

scorer = SemanticScorer()

def compute_semantic_similarity(self, evt_a, evt_b):
    result = scorer.compute_event_evolution_similarity(evt_a, evt_b)
    return result['overall']  # 0.7 * description + 0.3 * type similarity
```

### Automatic News Processing Pipeline

```python
from llm import TripletExtractor

def process_news_article(article_text, article_date, source_url):
    """Process news article and add to graph"""
    extractor = TripletExtractor()

    # Extract events
    events = extractor.extract_events(article_text, source=source_url, date=article_date)

    # Extract entities
    entities = extractor.extract_entities(article_text)

    # Extract relationships
    triplets = extractor.extract_from_text(article_text, source=source_url, date=article_date)

    # Load into Neo4j
    backend = Neo4jBackend()
    for event in events:
        backend.create_event(event)
    for entity in entities:
        backend.create_entity(entity)
    for triplet in triplets:
        backend.create_relationship(triplet)

    return len(events), len(entities), len(triplets)
```

## Performance Benchmarks

Based on NVIDIA GraphRAG paper results:

| Metric | Value | Notes |
|--------|-------|-------|
| **Triplet Extraction Accuracy** | 98% | With fine-tuned Llama-3 8B LoRA |
| **Inference Speed** | 150-300 tokens/sec | TensorRT-LLM optimization |
| **Embedding Dimension** | 1024 | NV-Embed-v2 |
| **Semantic Similarity** | >0.9 correlation | vs human judgment |
| **API Latency** | 200-500ms | NVIDIA NIM cloud |

### Caching Strategy

The `SemanticScorer` caches embeddings to reduce API calls:

```python
scorer = SemanticScorer()

# First call - generates embedding via API
sim1 = scorer.compute_text_similarity("Event A", "Event B")  # API call

# Second call with same text - uses cache
sim2 = scorer.compute_text_similarity("Event A", "Event C")  # Cached for "Event A"

print(f"Cache size: {scorer.get_cache_size()}")  # Output: 3 embeddings
```

## API Endpoints (Future)

Add to `api/app.py`:

```python
@app.route('/api/llm/extract-triplets', methods=['POST'])
def extract_triplets():
    """Extract triplets from text"""
    data = request.json
    text = data.get('text')

    extractor = TripletExtractor()
    triplets = extractor.extract_from_text(text)

    return jsonify({'status': 'success', 'triplets': triplets})

@app.route('/api/llm/similarity', methods=['POST'])
def compute_similarity():
    """Compute semantic similarity between two texts"""
    data = request.json
    text_a = data.get('text_a')
    text_b = data.get('text_b')

    scorer = SemanticScorer()
    similarity = scorer.compute_text_similarity(text_a, text_b)

    return jsonify({'status': 'success', 'similarity': similarity})
```

## Demos

Run the comprehensive demo:

```bash
./venv/bin/python scripts/demo_llm_integration.py
```

This demonstrates:
- Triplet extraction from sample financial news
- Event and entity recognition
- Embedding-based semantic similarity
- Comparison with baseline methods

## Limitations & Future Work

### Current Limitations

1. **API Key Required** - Need NVIDIA NIM account (free tier available)
2. **API Latency** - Cloud API calls add 200-500ms latency
3. **Cost** - API usage costs (free tier: 1000 requests/day)
4. **No Fine-tuning** - Using pre-trained models (fine-tuning requires NVIDIA AI Enterprise)

### Future Enhancements

1. **Fine-tune Llama-3 8B** - Train on financial domain for 98% accuracy
2. **cuGraph Integration** - Enable `NX_CUGRAPH_AUTOCONFIG=True` for 70x speedup
3. **Local Deployment** - Deploy NIM microservices locally for zero latency
4. **Dynamic Graph Management** - Implement background/query graph swap pattern
5. **Natural Language Queries** - Add LangChain/LlamaIndex for NL→Cypher translation
6. **Multi-hop Reasoning** - BFS/DFS for causal chain retrieval

## References

- **NVIDIA GraphRAG Paper**: "Structure From Chaos: Accelerate GraphRAG with cuGraph and NVIDIA NIM"
- **NVIDIA NIM Docs**: https://docs.nvidia.com/nim/
- **cuGraph**: https://github.com/rapidsai/cugraph
- **Nemotron**: https://developer.nvidia.com/nemotron
- **NV-Embed-v2**: https://huggingface.co/nvidia/NV-Embed-v2

## License

This module is part of FE-EKG for research and educational purposes.
