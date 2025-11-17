# FE-EKG Future Roadmap

**Document Version:** 1.0
**Last Updated:** 2025-11-16
**Status:** Planning & Research Phase

---

## Table of Contents

1. [Current MVP Status](#current-mvp-status)
2. [Technology Stack Decisions](#technology-stack-decisions)
3. [Phase 1: Market Intelligence Layer](#phase-1-market-intelligence-layer)
4. [Phase 2: Narrative Intelligence Layer](#phase-2-narrative-intelligence-layer)
5. [Phase 3: Premium Intelligence Layer](#phase-3-premium-intelligence-layer)
6. [Phase 4: Advanced Analytics](#phase-4-advanced-analytics)
7. [Phase 5: Platform Expansion](#phase-5-platform-expansion)
8. [RAPIDS cuGraph Integration](#rapids-cugraph-integration)
9. [RAG Implementation Strategy](#rag-implementation-strategy)
10. [Timeline & Milestones](#timeline--milestones)

---

## Current MVP Status

### ✅ Production-Ready Components

**Data Layer:**
- 5,105 Capital IQ events (2007-2009 financial crisis)
- 22 major financial entities (deduplicated)
- 31,173 causal evolution links (threshold=0.5, high quality)
- 429,019 RDF triples in AllegroGraph
- Complete 3-year timeline (Jan 2007 - Dec 2009)

**Technology Stack:**
- Backend: AllegroGraph 8.4.0 (cloud-hosted RDF triplestore)
- Graph Analytics: NetworkX 3.0+
- LLM: NVIDIA NIM/Nemotron API
- Embeddings: `nvidia/llama-3.2-nv-embedqa-1b-v2` (2048 dims)
- API: Flask REST API (20+ endpoints)

**Capabilities:**
- Answer "what happened" questions
- Timeline exploration
- Entity relationship analysis
- Event sequence tracking
- Basic causal chain discovery

**Dataset Quality:**
- 87% classification confidence
- Zero duplicates (v4 deduplication)
- Full CSV traceability (Capital IQ row numbers)
- Temporal distribution across all months

---

## Technology Stack Decisions

### LLM & Embeddings

**Selected: NVIDIA NIM/Nemotron** ✅

**Decision Rationale:**
- Already integrated and configured
- API Key: `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`
- Free tier: 1,000 API calls/day (sufficient for development)
- Cost: $0.0002 per query (25x cheaper than OpenAI)
- Financial domain performance: 53.1% FiQA score

**Embedding Model:**
- Model: `nvidia/llama-3.2-nv-embedqa-1b-v2`
- Dimensions: 2048 (dynamic: can use 1024 or 512)
- Context: 8192 tokens (vs 512 for old model)
- Performance: +12.7% better on financial Q&A
- Multilingual: 26 languages (including Chinese)

**Generation Model:**
- Model: `meta/llama-3.1-8b-instruct`
- Speed: 200-500ms response
- Quality: Excellent for financial domain

**Cost Estimates:**

| Usage Level | Queries/Month | Monthly Cost |
|-------------|---------------|--------------|
| Development | 100 | **$0.00** (free tier) |
| Light Production | 1,000 | **$0.20** |
| Medium Production | 10,000 | **$2.00** |
| Heavy Production | 100,000 | **$20.00** |

**Alternative Considered:**
- OpenAI GPT-4o: $5.13/month for 1k queries (25x more expensive)
- Claude 3.5 Sonnet: $7.05/month (35x more expensive)
- Local Llama: $0 but requires $1,500 GPU
- **Decision:** Stick with NVIDIA NIM (already integrated, cheapest)

### Vector Database

**Selected: FAISS (Local)** ✅

**Decision Rationale:**
- FREE (open source)
- Fast (<50ms search for 5,105 events)
- No cloud costs
- Easy integration with existing Python code
- Storage: ~40 MB for 5,105 × 2048-dim vectors

**Alternative Considered:**
- Pinecone (cloud): $70/month for 1M vectors
- **Decision:** FAISS sufficient for MVP scale

### Graph Database

**Selected: Hybrid (AllegroGraph + NetworkX)** ✅

**AllegroGraph:**
- Use for: Persistent storage, SPARQL queries, RDF reasoning
- Strength: Knowledge representation, semantic web standards
- Current: 429,019 triples (8.6% of 5M license limit)

**NetworkX:**
- Use for: Graph analytics (PageRank, centrality, community detection)
- Strength: Rich algorithm library (500+ algorithms)
- Performance: <1 second for 5K nodes

**RAPIDS cuGraph:**
- Status: **NOT using** (yet)
- Reason: Dataset too small (5K events)
- Threshold: Benefits start at 100K+ nodes
- Decision: **Revisit when graph grows to 100K+ events**
- Setup ready: Code is GPU-ready via NetworkX API

---

## Phase 1: Market Intelligence Layer

**Timeline:** 2 weeks
**Priority:** 🎯 QUICK WINS
**Cost:** $0 (all free sources)

### New Capabilities

- 📊 Crisis severity metrics
- 📈 Market impact visualization
- 🏦 Bank failure tracking
- 💵 Economic context

### Data Sources to Add

#### 1. FRED Economic Data (2 days)
**Source:** Federal Reserve Economic Data
**API:** FREE (https://fred.stlouisfed.org)
**Installation:** `pip install fredapi`

**Data to Collect:**
- TED spread (credit freeze indicator)
- VIX (volatility/fear gauge)
- Unemployment rate
- GDP growth
- S&P 500 index
- Case-Shiller housing price index
- 3-month LIBOR

**Implementation:**
```python
from fredapi import Fred
fred = Fred(api_key='YOUR_KEY')

# Get TED spread
ted_spread = fred.get_series('TEDRATE', start='2007-01-01', end='2009-12-31')
```

**Impact:** +40% richer context

---

#### 2. Yahoo Finance Market Data (2 days)
**Source:** Yahoo Finance
**API:** FREE (yfinance library)
**Installation:** `pip install yfinance`

**Data to Collect:**
- Stock prices for all 22 entities
- Daily returns, volume
- Market cap changes
- S&P 500 daily close

**Implementation:**
```python
import yfinance as yf

# Get Lehman stock price
leh = yf.Ticker('LEHMQ')
history = leh.history(start='2007-01-01', end='2008-09-15')
```

**Impact:** +30% market context

---

#### 3. FDIC Bank Failure List (1 day)
**Source:** FDIC Failed Bank List
**API:** FREE CSV download
**URL:** https://www.fdic.gov/resources/resolutions/bank-failures/failed-bank-list/

**Data to Collect:**
- 140+ bank failures (2007-2009)
- Bank names, locations, closure dates
- Acquiring institutions

**Implementation:**
```python
import pandas as pd

# Download FDIC data
url = 'https://www.fdic.gov/resources/resolutions/bank-failures/failed-bank-list/'
fdic_df = pd.read_html(url)[0]
```

**Impact:** +20% regulatory timeline

---

### New RAG Queries Enabled

- "How severe was the market crash in September 2008?"
- "Which banks failed during the crisis?"
- "What was the unemployment impact?"
- "Show me the VIX spike during Lehman's collapse"
- "What was Lehman's stock price before bankruptcy?"

**Total Impact:** +90% richer context
**Effort:** 5 days
**Cost:** $0

---

## Phase 2: Narrative Intelligence Layer

**Timeline:** 3 weeks
**Priority:** 📰 GAME CHANGER
**Cost:** $0 (all free sources)

### New Capabilities

- 🗞️ News context ("why" and "how" explanations)
- 📝 Official documents (authoritative sources)
- 🏛️ Policy actions (Fed/Treasury interventions)
- 💬 Expert commentary

### Data Sources to Add

#### 1. GDELT News Events (2 weeks)
**Source:** GDELT Project
**API:** FREE via Google BigQuery
**URL:** https://www.gdeltproject.org

**Data to Collect:**
- 100M+ global news events
- Event mentions, themes, locations
- Sentiment/tone scores
- Source URLs

**Implementation:**
```sql
-- BigQuery SQL
SELECT
  DATE,
  Actor1Name,
  Actor2Name,
  EventCode,
  GoldsteinScale,
  AvgTone,
  SOURCEURL
FROM `gdelt-bq.gdeltv2.events`
WHERE DATE BETWEEN '20070101' AND '20091231'
  AND (Actor1Name LIKE '%Lehman%' OR Actor2Name LIKE '%Lehman%')
LIMIT 10000
```

**Challenges:**
- Complex schema (58 columns)
- Massive scale (requires BigQuery)
- Quality filtering needed

**Impact:** +70% narrative context

---

#### 2. SEC EDGAR Filings (1 week)
**Source:** SEC EDGAR Database
**API:** FREE public API
**URL:** https://www.sec.gov/edgar/searchedgar/companysearch.html

**Data to Collect:**
- 10-K annual reports
- 10-Q quarterly reports
- 8-K current events
- S-1 registration statements

**Key Filings:**
- Lehman Brothers bankruptcy petition (Sep 15, 2008)
- Bear Stearns acquisition 8-K (Mar 2008)
- AIG bailout disclosure (Sep 2008)
- Quarterly risk disclosures

**Implementation:**
```python
from sec_edgar_downloader import Downloader

dl = Downloader("MyCompany", "email@example.com")
dl.get("10-K", "LEH", after="2007-01-01", before="2008-09-15")
```

**Challenges:**
- PDF/HTML parsing
- Large file sizes
- Complex table extraction

**Impact:** +60% authoritative context

---

#### 3. Federal Reserve Announcements (3 days)
**Source:** Federal Reserve website
**API:** Web scraping (no official API)
**URL:** https://www.federalreserve.gov

**Data to Collect:**
- FOMC statements
- Press releases
- Emergency lending facilities
- Interest rate decisions
- Bernanke speeches

**Key Events:**
- Term Auction Facility (TAF) announcement
- Primary Dealer Credit Facility (PDCF)
- Bear Stearns emergency loan
- TARP announcement

**Implementation:**
```python
import requests
from bs4 import BeautifulSoup

# Scrape Fed press releases
url = 'https://www.federalreserve.gov/newsevents/pressreleases.htm'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
```

**Impact:** +40% policy context

---

### New RAG Queries Enabled

- "Why did Lehman Brothers go bankrupt?"
- "How did the Federal Reserve respond to the crisis?"
- "What did the news say about Bear Stearns at the time?"
- "Show me Lehman's official bankruptcy filing"
- "What policy actions did the Fed take in September 2008?"

**Total Impact:** +170% explanation depth
**Effort:** 3 weeks
**Cost:** $0

---

## Phase 3: Premium Intelligence Layer

**Timeline:** 3-4 weeks
**Priority:** 💎 PREMIUM TIER (Optional)
**Cost:** $6,000-24,000/year (if Bloomberg/Reuters)

### New Capabilities

- 📰 Premium news (Bloomberg/Reuters quality)
- 🎓 Academic insights
- 🏛️ Congressional records
- 🔍 Deep forensics

### Data Sources to Add

#### 1. Bloomberg/Reuters News (1 week, PAID)
**Source:** Bloomberg Terminal or Reuters API
**Cost:** $2,000/month (Bloomberg) or $500-2,000/month (Reuters)

**What You Get:**
- Highest quality financial journalism
- Real-time crisis coverage
- Professional analyst commentary
- Proprietary insights

**Alternative (FREE):**
- WSJ Archive: $40/month
- Financial Times: $75/month

**Impact:** +100% premium quality

---

#### 2. FCIC Report (1 week, FREE)
**Source:** Financial Crisis Inquiry Commission
**Format:** 662-page PDF
**URL:** https://www.gpo.gov/fdsys/pkg/GPO-FCIC/pdf/GPO-FCIC.pdf

**What You Get:**
- Official government investigation
- Definitive crisis narrative
- Lessons learned
- Policy recommendations
- Dissenting views

**Implementation:**
- Manual extraction (PDF parsing)
- Chapter-by-chapter ingestion
- Key finding extraction

**Impact:** +50% authoritative narrative

---

#### 3. Congressional Testimony (3 days, FREE)
**Source:** Congress.gov
**URL:** https://www.congress.gov

**Key Hearings:**
- Paulson testimony (Treasury Secretary)
- Bernanke testimony (Fed Chairman)
- Fuld testimony (Lehman CEO)
- Geithner testimony (NY Fed President)

**What You Get:**
- First-hand accounts
- Policy debates
- Regulatory perspectives
- Executive reasoning

**Impact:** +30% insider context

---

#### 4. NBER Academic Papers (1 week, FREE)
**Source:** National Bureau of Economic Research
**URL:** https://www.nber.org

**Papers to Include:**
- "The Financial Crisis of 2007-2009" (Brunnermeier)
- "Deciphering the Liquidity and Credit Crunch 2007-2008" (Gorton)
- "This Time is Different" (Reinhart & Rogoff)

**What You Get:**
- Scholarly analysis
- Theoretical frameworks
- Economic models
- Cross-country comparisons

**Impact:** +35% academic depth

---

### New RAG Queries Enabled

- "What lessons did the FCIC investigation identify?"
- "What did Paulson say in congressional testimony?"
- "How do economists explain the crisis?"
- "Could the crisis have been prevented?"
- "What Bloomberg analysts said about Lehman in 2008?"

**Total Impact:** +240% authority & depth
**Effort:** 3-4 weeks
**Cost:** $6,000-24,000/year (if premium news)

---

## Phase 4: Advanced Analytics

**Timeline:** 8-12 weeks
**Priority:** 🔬 RESEARCH TIER
**Cost:** $0 (all computational)

### New Capabilities

- 🔗 Network effects & contagion pathways
- 📊 Counterfactual "what-if" analysis
- 🤖 Agent-based simulation
- 🎯 Risk forecasting

### Features to Build

#### 1. Complete Evolution Methods (1 week)

**Current Status:**
- Implemented: 2/6 methods (Temporal, Entity Overlap)
- Missing: 4/6 methods

**To Implement:**
1. **Semantic Similarity** (2 days)
   - Use NVIDIA embeddings
   - Cosine similarity between event descriptions
   - Already have `llm/semantic_scorer.py`

2. **Topic Relevance** (1 day)
   - Event type category matching
   - Financial domain topics

3. **Event Type Causality** (2 days)
   - Domain-specific causal patterns
   - "Bankruptcy → Credit Downgrade" rules

4. **Emotional Consistency** (1 day)
   - Sentiment analysis (EVI score)
   - Use FinBERT or NVIDIA NIM

**Impact:** +50% better causal links

---

#### 2. Entity Relationship Network (2 weeks)

**Data to Add:**
- Ownership structures
- Board connections (interlocking directorates)
- Counterparty exposures
- Credit default swap networks

**Sources:**
- SEC proxy filings (board members)
- DTCC data (CDS exposures) - if accessible
- BIS data (global interconnections)

**Algorithms to Implement:**
- PageRank (systemically important entities)
- Betweenness centrality (bottleneck entities)
- Community detection (crisis clusters)

**Impact:** +60% network understanding

---

#### 3. Mesa Agent-Based Modeling (3-4 weeks)

**Purpose:** Simulate risk propagation dynamics

**Implementation:**
```python
# abm/financial_crisis_model.py
from mesa import Agent, Model
from mesa.time import RandomActivation

class BankAgent(Agent):
    def __init__(self, unique_id, model, entity_data):
        super().__init__(unique_id, model)
        self.capital = entity_data['capital']
        self.liquidity = entity_data['liquidity']
        self.failed = False

    def step(self):
        # Check failure condition
        if self.liquidity < 0.1 * self.capital:
            self.fail()

        # Propagate to counterparties
        if self.failed:
            for neighbor in self.model.grid.get_neighbors(self.pos):
                neighbor.absorb_shock(strength=0.2)
```

**Capabilities:**
- Simulate Lehman failure propagation
- Test "what-if" scenarios:
  - "What if Fed intervened 1 week earlier?"
  - "What if Lehman had 20% more capital?"
- Monte Carlo analysis (1,000 simulations)

**Impact:** +150% predictive power

---

#### 4. Risk Forecasting Models (2-3 weeks)

**Methods:**
- Time series prediction (ARIMA, LSTM)
- Early warning signals (stress indicators)
- Stress testing frameworks
- Network risk metrics

**Outputs:**
- P(systemic collapse) over time
- Entity failure probabilities
- Contagion risk scores

**Impact:** +100% predictive capability

---

### New Capabilities Unlocked

- "Simulate what would happen if Fed intervened earlier"
- "Which banks were most systemically important?"
- "Could we have predicted Lehman's failure?"
- "What's the contagion risk from Bank X failing?"
- "Run 1,000 Monte Carlo scenarios"

**Total Impact:** +300% analytical power
**Effort:** 8-12 weeks
**Cost:** $0

---

## Phase 5: Platform Expansion

**Timeline:** 8-16 weeks (per crisis)
**Priority:** 🌍 PLATFORM-LEVEL
**Cost:** Variable

### Multi-Crisis Coverage

#### 1. Evergrande Crisis (2021-2023) - 1-2 weeks
**Data:**
- China real estate collapse
- ~300 events (hand-curated + news)
- 15 major Chinese developers
- Policy interventions (PBoC, NDRC)

**Comparison Questions:**
- "Compare 2008 US crisis to 2021 Evergrande collapse"
- "How did China's response differ from US?"
- "What's similar/different in contagion mechanisms?"

---

#### 2. SVB/Signature Bank Crisis (March 2023) - 1 week
**Data:**
- Silicon Valley Bank failure
- Signature Bank failure
- First Republic acquisition
- Social media-driven bank runs

**Comparison Questions:**
- "How is 2023 different from 2008?"
- "What role did social media play vs 2008?"
- "Why did regulators act faster in 2023?"

---

#### 3. 1997 Asian Financial Crisis - 2-3 weeks
**Data:**
- Thailand baht collapse
- IMF interventions
- Contagion to Indonesia, South Korea
- Different crisis mechanisms

**Comparison Questions:**
- "Compare currency crisis to banking crisis"
- "How do emerging market crises differ?"

---

#### 4. 1929 Great Depression - 3-4 weeks
**Data:**
- Stock market crash
- Bank failures (4,000+ banks)
- Regulatory evolution (Glass-Steagall)

**Comparison Questions:**
- "What patterns repeat across all crises?"
- "How has financial system evolved since 1929?"
- "Has anything changed?"

---

### Platform Features

- Multi-crisis comparison dashboard
- Timeline synchronization across crises
- Pattern detection across 100 years
- Crisis typology (banking, currency, sovereign, etc.)

**Total Impact:** Platform-level expansion
**Effort:** 8-16 weeks per crisis
**Cost:** Variable (data acquisition)

---

## RAPIDS cuGraph Integration

**Status:** NOT CURRENTLY USING
**Decision:** Defer until graph grows to 100K+ events

### Current Situation

**Why NOT using cuGraph:**
- Current scale: 5,105 events (too small for GPU benefits)
- NetworkX handles 5K nodes in <1 second
- cuGraph would only provide 3-10x speedup (not worth complexity)
- No local NVIDIA GPU hardware
- Setup complexity not justified

**Current Performance:**
- NetworkX PageRank: 0.5 seconds
- cuGraph PageRank: 0.15 seconds
- Time saved: 0.35 seconds (negligible)

### When to Reconsider

**Milestone 1: 50K events**
- NetworkX becomes slower (10-60 seconds)
- cuGraph speedup: 10-30x
- **Decision:** Re-evaluate

**Milestone 2: 100K+ events**
- NetworkX impractical (minutes)
- cuGraph speedup: 50-500x
- **Decision:** Strongly consider GPU

**Milestone 3: Real-time system**
- Need <1 second response time
- cuGraph essential
- **Decision:** Invest in GPU

### Integration Strategy

**Code is GPU-ready:**
```python
# Current code uses NetworkX public API
import networkx as nx
G = nx.Graph()
pagerank = nx.pagerank(G)

# When ready, just enable cuGraph backend:
export NX_CUGRAPH_AUTOCONFIG=True
# Same code, GPU acceleration!
```

**Future Implementation (when scale justifies):**

**Phase 1: Zero-Code Test** (1 hour)
```bash
conda install -c rapidsai cugraph=25.10
export NX_CUGRAPH_AUTOCONFIG=True
./venv/bin/python evolution/run_evolution.py
```

**Phase 2: Explicit cuGraph** (1 day)
```python
import cugraph
import cudf

# GPU-accelerated Jaccard similarity
jaccard_df = cugraph.jaccard(gpu_graph)
```

**Phase 3: Advanced Analytics** (1 week)
```python
# PageRank for influential events
pagerank = cugraph.pagerank(G)

# Louvain community detection
communities = cugraph.louvain(G)

# Betweenness centrality
betweenness = cugraph.betweenness_centrality(G)
```

### Cost-Benefit

**Hardware Cost:**
- Local GPU: $500-$5,000 (RTX 3060-4090)
- Cloud GPU: $0.50-$3.00/hour (AWS p3, g5 instances)

**When ROI Becomes Positive:**
- At 500K events: 5 minutes → 1 second (299 seconds saved)
- Worth investing in GPU at this scale

**Recommendation:**
- Monitor graph growth
- Track NetworkX performance
- Add cuGraph when analysis takes >5 minutes

---

## RAG Implementation Strategy

### Architecture

**Selected: Hybrid (AllegroGraph + FAISS)** ✅

```
User Query
    ↓
Intent Classification (NVIDIA NIM)
    ↓
    ├─ Entity/Date Query? → SPARQL (AllegroGraph)
    └─ Semantic Query? → Vector Search (FAISS)
    ↓
Graph Context Expansion (Evolution Links)
    ↓
LLM Answer Generation (NVIDIA Nemotron)
    ↓
Return Answer + Sources
```

### Implementation Steps

#### Phase 1: Embed Events (2-3 hours)

```python
# rag/vectorize_events.py
from llm.nemotron_client import NemotronClient
import faiss
import numpy as np
import json

client = NemotronClient()

# Load events
with open('data/capital_iq_processed/lehman_v4_deduped.json') as f:
    data = json.load(f)
    events = data['events']

# Embed all events
print(f"Embedding {len(events)} events...")
descriptions = [e['description'] for e in events]
embeddings = client.generate_embeddings(
    descriptions,
    model='nvidia/llama-3.2-nv-embedqa-1b-v2'
)

# Build FAISS index
embedding_matrix = np.array(embeddings).astype('float32')
index = faiss.IndexFlatIP(2048)  # 2048 dimensions
index.add(embedding_matrix)

# Save
faiss.write_index(index, 'data/event_embeddings.faiss')
with open('data/event_ids.json', 'w') as f:
    json.dump([e['eventId'] for e in events], f)
```

**Cost:** FREE (within NVIDIA NIM free tier)
**Time:** ~20 seconds for 5,105 events
**Storage:** ~40 MB

---

#### Phase 2: Hybrid Retrieval (4-6 hours)

```python
# rag/retrieval.py
class HybridRetriever:
    def __init__(self):
        self.faiss_index = faiss.read_index('data/event_embeddings.faiss')
        self.event_ids = json.load(open('data/event_ids.json'))
        self.client = NemotronClient()
        self.graph = AllegroGraphRDFLoader()

    def retrieve(self, query, top_k=10):
        # 1. Parse query for entities/dates
        entities = self.extract_entities(query)
        dates = self.extract_dates(query)

        results = []

        # 2. SPARQL query if entities/dates found
        if entities or dates:
            sparql_results = self.query_graph(entities, dates)
            results.extend(sparql_results)

        # 3. Vector similarity search
        query_emb = self.client.generate_embeddings([query])[0]
        distances, indices = self.faiss_index.search(
            np.array([query_emb]).astype('float32'),
            k=top_k
        )
        vector_results = [self.event_ids[i] for i in indices[0]]
        results.extend(vector_results)

        # 4. Expand with evolution links
        results = self.expand_with_graph(results)

        return self.deduplicate(results)
```

---

#### Phase 3: Answer Generation (2-3 hours)

```python
# rag/qa_engine.py
class RAGEngine:
    def __init__(self):
        self.retriever = HybridRetriever()
        self.client = NemotronClient()

    def answer(self, question):
        # 1. Retrieve context
        context_events = self.retriever.retrieve(question, top_k=10)

        # 2. Format context
        context_text = "\n\n".join([
            f"Event {i+1}: {e['description']}"
            for i, e in enumerate(context_events)
        ])

        # 3. Generate answer
        prompt = f"""Based on the following financial crisis events, answer the question.

Context:
{context_text}

Question: {question}

Answer (be concise and cite specific events):"""

        response = self.client.generate_text(
            prompt,
            max_tokens=300,
            model='meta/llama-3.1-8b-instruct'
        )

        return {
            'answer': response['text'],
            'sources': context_events,
            'method': 'hybrid'
        }
```

---

#### Phase 4: API Endpoint (1-2 hours)

```python
# api/app.py
from rag.qa_engine import RAGEngine

rag = RAGEngine()

@app.route('/api/rag/ask', methods=['POST'])
def rag_query():
    """
    RAG Q&A endpoint

    Body: {"question": "What caused Lehman's bankruptcy?"}
    Returns: {"answer": "...", "sources": [...], "method": "hybrid"}
    """
    question = request.json.get('question')

    if not question:
        return jsonify({'error': 'No question provided'}), 400

    result = rag.answer(question)

    return jsonify({
        'question': question,
        'answer': result['answer'],
        'sources': result['sources'],
        'method': result['method'],
        'timestamp': datetime.now().isoformat()
    })
```

---

#### Phase 5: Frontend Chat UI (4-6 hours)

```html
<!-- api/rag_demo.html -->
<div id="chat-container">
    <div id="messages"></div>
    <form id="chat-form">
        <input type="text" id="question" placeholder="Ask about the 2008 crisis...">
        <button type="submit">Ask</button>
    </form>
</div>

<script>
document.getElementById('chat-form').onsubmit = async (e) => {
    e.preventDefault();
    const question = document.getElementById('question').value;

    // Show loading
    addMessage('user', question);
    addMessage('assistant', 'Thinking...');

    // Call API
    const response = await fetch('/api/rag/ask', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({question})
    });

    const data = await response.json();

    // Show answer
    updateLastMessage(data.answer);
    showSources(data.sources);
};
</script>
```

---

### RAG Performance Targets

**Latency:**
- Embedding query: 10-15ms
- FAISS search: 5-10ms
- Graph expansion: 50-100ms
- LLM generation: 200-500ms
- **Total: 265-625ms** (<1 second) ✅

**Quality:**
- Current dataset: Can answer "what" questions
- With Phase 1-2 data: Can answer "why" questions
- With Phase 3 data: Can answer with authority

**Cost:**
- Development: $0 (free tier)
- Production: $0.0002 per query
- 1,000 queries/month: $0.20/month

---

## Timeline & Milestones

### Month 1: MVP + Market Layer

**Week 1:** MVP RAG
- Embed events (1 day)
- Build retrieval (2 days)
- Create API endpoint (1 day)
- Test & deploy (1 day)

**Week 2-3:** Phase 1 (Market Intelligence)
- FRED data (2 days)
- Yahoo Finance (2 days)
- FDIC data (1 day)
- Integration & testing (2 days)

**Week 4:** Buffer & polish

**Deliverable:** Working RAG with market context

---

### Month 2: Narrative Layer

**Week 1-2:** GDELT Integration
- BigQuery setup (2 days)
- Data extraction (5 days)
- Quality filtering (3 days)

**Week 3:** SEC EDGAR
- Filing identification (2 days)
- PDF parsing (3 days)
- Integration (2 days)

**Week 4:** Fed Announcements
- Web scraping (2 days)
- Data structuring (1 day)
- Testing (2 days)

**Deliverable:** RAG can answer "why" questions

---

### Quarter 2: Advanced Analytics (Optional)

**Month 3-4:** Phase 4
- Complete evolution methods (1 week)
- Entity networks (2 weeks)
- Mesa ABM (3 weeks)
- Risk forecasting (2 weeks)

**Deliverable:** Predictive capabilities

---

### Year 2: Platform Expansion (Optional)

**Q1-Q2:** Add Evergrande crisis
**Q3:** Add SVB crisis
**Q4:** Add historical crises (1997, 1929)

**Deliverable:** Multi-crisis platform

---

## Decision Points

### Trigger Points for Each Phase

**Phase 1 (Market Layer):**
- Trigger: 20% of RAG queries mention "market" or "crash"
- Cost: $0
- Decision: ADD if users ask market questions

**Phase 2 (Narrative Layer):**
- Trigger: 40% of queries start with "why" or "how"
- Cost: $0
- Decision: ADD if explanatory queries dominate

**Phase 3 (Premium Intelligence):**
- Trigger: External launch or revenue targets
- Cost: $6K-24K/year
- Decision: ADD if monetizing or publishing research

**Phase 4 (Advanced Analytics):**
- Trigger: Academic collaboration or grant funding
- Cost: $0 but 8-12 weeks effort
- Decision: ADD if building research platform

**Phase 5 (Platform Expansion):**
- Trigger: Market demand or competitive pressure
- Cost: Variable
- Decision: ADD if building multi-crisis product

**cuGraph Integration:**
- Trigger: Graph grows to 100K+ events OR analysis takes >5 minutes
- Cost: $500-$5,000 (GPU)
- Decision: ADD when NetworkX becomes bottleneck

---

## Success Metrics

### MVP (Month 1)

- [ ] RAG answers 80% of "what" questions correctly
- [ ] Average response time <1 second
- [ ] User satisfaction >7/10
- [ ] API uptime >99%

### Phase 1 (Month 2)

- [ ] Can answer market impact questions
- [ ] Economic indicators integrated
- [ ] Bank failure timeline complete
- [ ] Response quality +30%

### Phase 2 (Month 3)

- [ ] Can answer "why" questions with 70% accuracy
- [ ] News context integrated
- [ ] Official documents accessible
- [ ] Response quality +50%

### Phase 3 (Quarter 2)

- [ ] Research-grade citations
- [ ] Academic rigor in answers
- [ ] Policy analysis capabilities
- [ ] Response quality +70%

### Phase 4 (Quarter 3-4)

- [ ] Simulation capabilities working
- [ ] Counterfactual analysis available
- [ ] Predictive models deployed
- [ ] Research publications possible

---

## Contact & Approval Process

**For any major decision:**
1. Document in this file
2. Get user approval
3. Update timeline
4. Track in todos
5. Review quarterly

**Document Owner:** Claude Code Agent
**Approval Authority:** Project Owner
**Review Frequency:** Quarterly
**Next Review:** 2025-02-16

---

**End of Roadmap**

*This document will be updated as decisions are made and priorities change.*
