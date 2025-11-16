# Results Directory

This directory contains all generated outputs from the FE-EKG (Financial Event Evolution Knowledge Graph) system, organized for easy access and understanding.

## Directory Structure

```
results/
├── visualizations/      # All PNG visualizations
├── data/               # Processed data files (JSON)
├── rdf/                # RDF exports in multiple formats
│   ├── evergrande/     # Evergrande crisis knowledge graph
│   └── lehman/         # Lehman Brothers crisis knowledge graph
└── README.md           # This file
```

---

## 📊 Visualizations

**Location:** `visualizations/`

All visualization files are high-resolution PNGs generated from the knowledge graph analysis.

### Graph Structure Visualizations

#### `three_layer_graph.png` (611 KB)
- **Description:** Complete three-layer architecture visualization
- **Layers:** Entities (green), Events (blue), Risks (red)
- **Shows:** Full Evergrande crisis knowledge graph with all relationships
- **Use Case:** Overview presentations, paper figures

#### `evolution_network.png` (557 KB)
- **Description:** Event evolution network with causal links
- **Highlights:** 154 evolution links between 20 financial events
- **Edge Width:** Proportional to evolution score
- **Use Case:** Understanding event causality and temporal progression

### Timeline & Progression

#### `event_network_timeline.png` (593 KB)
- **Description:** Temporal progression of events (Aug 2020 - Aug 2022)
- **Layout:** Time-ordered visualization
- **Shows:** How events unfolded chronologically
- **Use Case:** Timeline analysis, crisis progression studies

### Risk Analysis

#### `risk_distribution.png` (166 KB)
- **Description:** Distribution of risk types across the crisis
- **Chart Type:** Bar/pie chart showing 12 risk categories
- **Includes:** Liquidity, credit, market, operational risks, etc.
- **Use Case:** Risk management presentations, quantitative analysis

#### `risk_propagation.png` (475 KB)
- **Description:** How risks propagate through the knowledge graph
- **Shows:** Risk → Entity → Event chains
- **Highlights:** Systemic risk connections
- **Use Case:** Risk assessment, propagation modeling

### Method Analysis

#### `component_breakdown.png` (226 KB)
- **Description:** Breakdown of 6 evolution methods
- **Methods:**
  1. Temporal Correlation
  2. Entity Overlap
  3. Semantic Similarity
  4. Topic Relevance
  5. Event Type Causality
  6. Emotional Consistency
- **Use Case:** Method comparison, algorithm analysis

#### `evolution_heatmap.png` (468 KB)
- **Description:** Heatmap of evolution scores between events
- **Format:** 20x20 matrix (event pairs)
- **Color:** Darker = stronger evolution link
- **Use Case:** Pattern identification, dense connection areas

---

## 📁 Data Files

**Location:** `data/`

### `evolution_links.json` (66 KB)

**Format:** JSON
**Description:** Complete evolution link dataset with all computed scores

**Contents:**
```json
{
  "metadata": {
    "threshold": 0.2,
    "total_links": 154,
    "avg_score": 0.366,
    "max_score": 0.709,
    "min_score": 0.205
  },
  "links": [
    {
      "from": "evt_001",
      "to": "evt_002",
      "score": 0.37,
      "components": {
        "temporal": 0.0,
        "entity_overlap": 0.5,
        "semantic": 0.0,
        "topic": 0.3,
        "causality": 0.9,
        "emotional": 0.9
      },
      "from_date": "2020-08-20",
      "to_date": "2021-05-10",
      "from_type": "regulatory_pressure",
      "to_type": "liquidity_warning"
    },
    ...
  ]
}
```

**Key Fields:**
- `from/to`: Event IDs
- `score`: Overall evolution score (0-1)
- `components`: Breakdown by 6 methods
- `from_date/to_date`: Event timestamps
- `from_type/to_type`: Event types

**Use Case:** Machine learning, custom analysis, re-computation

---

## 🔗 RDF Exports

**Location:** `rdf/`

All knowledge graphs exported in three standard RDF formats for interoperability.

### Evergrande Crisis (`rdf/evergrande/`)

#### `feekg_graph.ttl` (13 KB)
- **Format:** Turtle (TTL) - Most readable
- **Prefix:** `@prefix feekg: <http://feekg.org/ontology#>`
- **Content:** Entities, Events, Risks, Evolution Links
- **Lines:** ~400 triples

#### `feekg_graph.nt` (38 KB)
- **Format:** N-Triples (NT) - Line-based
- **Use Case:** Streaming, large-scale processing
- **Format:** One triple per line

#### `feekg_graph.xml` (29 KB)
- **Format:** RDF/XML - Standard XML serialization
- **Use Case:** XML toolchains, SPARQL endpoints
- **Namespace:** `http://feekg.org/ontology#`

### Lehman Brothers Crisis (`rdf/lehman/`)

#### `lehman_graph.ttl` (11 KB)
- **Format:** Turtle
- **Content:** Lehman Brothers crisis data (if generated)
- **Purpose:** Comparative crisis analysis

#### `lehman_graph.nt` (30 KB)
- **Format:** N-Triples
- **Content:** Same as TTL, different serialization

#### `lehman_graph.xml` (22 KB)
- **Format:** RDF/XML
- **Content:** Same as TTL, XML format

---

## 📈 Statistics Summary

### Dataset Overview
- **Total Events:** 20 (Evergrande)
- **Total Entities:** 10 (companies, banks, regulators)
- **Total Risks:** 10 instances across 12 types
- **Evolution Links:** 154 computed causal connections
- **Time Range:** Aug 2020 - Aug 2022 (24 months)

### RDF Triple Counts
- **Events:** ~180 triples
- **Entities:** ~40 triples
- **Risks:** ~50 triples
- **Evolution Links:** 154 triples
- **Total:** ~424 triples

### Visualization Sizes
- **Total Visualizations:** 7 PNG files
- **Total Size:** ~3.0 MB
- **Resolution:** High-DPI suitable for publications

---

## 🎯 Usage Recommendations

### For Presentations
1. Use `three_layer_graph.png` for overall architecture
2. Use `evolution_network.png` for causal analysis
3. Use `risk_distribution.png` for risk overview

### For Publications
- All PNGs are high-resolution (300+ DPI)
- `three_layer_graph.png` works well as main figure
- `evolution_heatmap.png` good for methods section
- `component_breakdown.png` for methodology comparison

### For Further Analysis
- Load `evolution_links.json` for custom processing
- Import RDF files into:
  - Neo4j (via apoc.import)
  - AllegroGraph (via agload)
  - Protégé (for ontology viewing)
  - Python RDFLib (for SPARQL queries)

### For Web Integration
- Visualizations can be directly embedded in HTML
- Use RDF data with D3.js or vis.js for interactive graphs
- JSON data easily consumable by JavaScript

---

## 🔄 Regenerating Results

If you need to regenerate any of these files:

### Visualizations
```bash
./venv/bin/python scripts/demo_visualizations.py
```

### Evolution Links
```bash
./venv/bin/python evolution/run_evolution.py
```

### RDF Exports
```bash
./venv/bin/python scripts/convert_to_rdf.py
```

---

## 📝 File Formats

### RDF Format Comparison

| Format | Size | Readability | Use Case |
|--------|------|-------------|----------|
| Turtle (.ttl) | Small | High | Human reading, development |
| N-Triples (.nt) | Large | Medium | Streaming, line-by-line processing |
| RDF/XML (.xml) | Medium | Low | XML tools, SPARQL endpoints |

### Recommended Formats by Task

- **Reading/Debugging:** Use `.ttl` (Turtle)
- **Large-scale Import:** Use `.nt` (N-Triples)
- **Standard Tools:** Use `.xml` (RDF/XML)
- **Custom Analysis:** Use `.json` (evolution_links)

---

## 🔗 Related Documentation

- [Main README](../README.md) - Project overview
- [CLAUDE.md](../CLAUDE.md) - Development guide
- [VISUALIZATION_IMPROVEMENTS.md](../VISUALIZATION_IMPROVEMENTS.md) - Viz details
- [Timeline Visualization](../api/timeline.html) - Interactive demo

---

## ⚠️ Important Notes

1. **Do not manually edit** RDF files - regenerate from source data
2. **PNG files are large** - use git LFS if committing to repo
3. **Evolution links** are computed with threshold=0.2 (adjustable)
4. **Timestamps** in JSON are in YYYY-MM-DD format
5. **Scores** are normalized to [0, 1] range

---

## 🎓 Citation

If using these results in publications, please cite:

```bibtex
@article{feekg2024,
  title={FE-EKG: Financial Event Evolution Knowledge Graph Implementation},
  author={Based on Liu et al. (2024)},
  journal={Implementation Study},
  year={2024}
}
```

---

Last Updated: 2025-11-10
Version: 1.0.0
Generated by: FE-EKG System
