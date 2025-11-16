# FE-EKG REST API Documentation

REST API for the Financial Event Evolution Knowledge Graph system.

## Quick Start

### Start the Server

```bash
# From the project root
python api/app.py

# Or use the venv python
./venv/bin/python api/app.py
```

The server will start on **http://localhost:5000**

### Test the API

```bash
# Health check
curl http://localhost:5000/health

# Get database info
curl http://localhost:5000/api/info

# Get all entities
curl http://localhost:5000/api/entities

# Get graph data (for frontend visualization)
curl http://localhost:5000/api/graph/data
```

## API Endpoints

### Health & Info

#### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "service": "FE-EKG API",
  "version": "1.0.0"
}
```

#### `GET /api/info`
Get database overview

**Response:**
```json
{
  "status": "success",
  "data": {
    "nodes": [...],
    "relationships": [...],
    "risks": [...]
  }
}
```

### Entity Endpoints

#### `GET /api/entities`
Get all entities

**Response:**
```json
{
  "status": "success",
  "count": 10,
  "data": [
    {
      "id": "ent_evergrande",
      "name": "China Evergrande Group",
      "type": "Company",
      "description": "..."
    }
  ]
}
```

#### `GET /api/entities/<entity_id>`
Get specific entity details

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "ent_evergrande",
    "name": "China Evergrande Group",
    "type": "Company",
    "description": "..."
  }
}
```

#### `GET /api/entities/<entity_id>/risks`
Get risks for a specific entity

**Response:**
```json
{
  "status": "success",
  "count": 6,
  "data": [
    {
      "id": "risk_001",
      "type": "Solvency Risk",
      "score": 0.85,
      "severity": "critical",
      "status": "materialized"
    }
  ]
}
```

### Event Endpoints

#### `GET /api/events`
Get all events with optional filtering

**Query Parameters:**
- `start_date` (optional): Filter events from this date (YYYY-MM-DD)
- `end_date` (optional): Filter events until this date (YYYY-MM-DD)
- `type` (optional): Filter by event type

**Example:**
```bash
curl "http://localhost:5000/api/events?start_date=2021-01-01&end_date=2021-12-31"
```

**Response:**
```json
{
  "status": "success",
  "count": 20,
  "data": [
    {
      "id": "evt_001",
      "type": "regulatory_pressure",
      "date": "2020-08-20",
      "description": "...",
      "actor": "People's Bank of China",
      "target": "China Evergrande Group"
    }
  ]
}
```

#### `GET /api/events/<event_id>`
Get specific event details

### Evolution Endpoints

#### `GET /api/evolution/links`
Get evolution links between events

**Query Parameters:**
- `min_score` (default: 0.0): Minimum evolution score
- `limit` (default: 100): Maximum number of results

**Example:**
```bash
curl "http://localhost:5000/api/evolution/links?min_score=0.5&limit=20"
```

**Response:**
```json
{
  "status": "success",
  "count": 20,
  "data": [
    {
      "fromEvent": "debt_default",
      "fromDate": "2021-10-20",
      "toEvent": "credit_downgrade",
      "toDate": "2021-10-21",
      "overallScore": 0.709,
      "causalityScore": 0.900,
      "emotionalScore": 0.900
    }
  ]
}
```

#### `GET /api/evolution/chains`
Get causal event chains

**Query Parameters:**
- `min_causality` (default: 0.5): Minimum causality score
- `min_length` (default: 2): Minimum chain length
- `max_length` (default: 5): Maximum chain length

**Example:**
```bash
curl "http://localhost:5000/api/evolution/chains?min_causality=0.6"
```

**Response:**
```json
{
  "status": "success",
  "count": 10,
  "data": [
    {
      "eventChain": ["regulatory_pressure", "liquidity_warning", "credit_downgrade"],
      "chainLength": 2,
      "avgCausality": 0.900
    }
  ]
}
```

#### `GET /api/evolution/stats`
Get evolution statistics

**Response:**
```json
{
  "status": "success",
  "data": {
    "totalLinks": 154,
    "avgOverallScore": 0.366,
    "avgTemporal": 0.075,
    "avgEntityOverlap": 0.474,
    "avgSemantic": 0.071,
    "avgTopic": 0.665,
    "avgCausality": 0.434,
    "avgEmotional": 0.764
  }
}
```

### Risk Endpoints

#### `GET /api/risks`
Get all risks

**Response:**
```json
{
  "status": "success",
  "count": 10,
  "data": [
    {
      "id": "risk_001",
      "type": "Solvency Risk",
      "score": 0.85,
      "severity": "critical",
      "status": "materialized",
      "targetEntity": "China Evergrande Group"
    }
  ]
}
```

#### `GET /api/risks/systemic`
Get systemic/contagion risks

**Response:**
```json
{
  "status": "success",
  "count": 2,
  "data": [
    {
      "sourceEntity": "Anbang Insurance",
      "connectedEntities": ["Entity1", "Entity2"],
      "contagionScore": 0.5,
      "severity": "medium"
    }
  ]
}
```

#### `GET /api/risks/distribution`
Get risk distribution statistics

### Visualization Endpoints

All visualization endpoints return PNG images as base64-encoded strings.

#### `GET /api/visualizations/three-layer`
Generate three-layer graph visualization

**Query Parameters:**
- `limit` (default: 15): Maximum number of events

**Response:**
```json
{
  "status": "success",
  "image": "data:image/png;base64,..."
}
```

#### `GET /api/visualizations/evolution-network`
Generate evolution network visualization

**Query Parameters:**
- `min_score` (default: 0.4): Minimum evolution score

#### `GET /api/visualizations/risk-propagation`
Generate risk propagation visualization

#### `GET /api/visualizations/risk-timeline`
Generate risk timeline plot

**Query Parameters:**
- `entity` (default: "China Evergrande Group"): Entity name

#### `GET /api/visualizations/evolution-heatmap`
Generate evolution heatmap

#### `GET /api/visualizations/component-breakdown`
Generate component breakdown plot

### Graph Data Endpoint (for Frontend)

#### `GET /api/graph/data`
Get graph data in nodes/edges format for frontend visualization libraries (D3.js, Cytoscape.js, Vis.js)

**Query Parameters:**
- `limit` (default: 20): Maximum number of events

**Response:**
```json
{
  "status": "success",
  "nodes": [
    {
      "id": "ent_evergrande",
      "label": "China Evergrande Group",
      "type": "entity",
      "group": "entity",
      "data": {...}
    },
    {
      "id": "evt_001",
      "label": "regulatory_pressure",
      "type": "event",
      "group": "event",
      "data": {...}
    }
  ],
  "edges": [
    {
      "source": "evt_001",
      "target": "evt_002",
      "type": "evolves_to",
      "weight": 0.7,
      "data": {...}
    }
  ],
  "stats": {
    "entities": 10,
    "events": 20,
    "risks": 10,
    "evolution_links": 154
  }
}
```

## CORS

CORS is enabled by default, so the API can be accessed from any frontend origin.

## Error Responses

All error responses follow this format:

```json
{
  "status": "error",
  "message": "Error description"
}
```

Common status codes:
- `200`: Success
- `404`: Resource not found
- `500`: Internal server error

## Frontend Integration Example

### React Example

```javascript
import React, { useState, useEffect } from 'react';

function EvolutionLinks() {
  const [links, setLinks] = useState([]);

  useEffect(() => {
    fetch('http://localhost:5000/api/evolution/links?min_score=0.5')
      .then(res => res.json())
      .then(data => setLinks(data.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div>
      <h2>Evolution Links</h2>
      <ul>
        {links.map(link => (
          <li key={`${link.fromEvent}-${link.toEvent}`}>
            {link.fromEvent} → {link.toEvent} (score: {link.overallScore})
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### D3.js Graph Visualization Example

```javascript
import * as d3 from 'd3';

async function renderGraph() {
  const response = await fetch('http://localhost:5000/api/graph/data?limit=20');
  const graphData = await response.json();

  const svg = d3.select('#graph')
    .append('svg')
    .attr('width', 800)
    .attr('height', 600);

  const simulation = d3.forceSimulation(graphData.nodes)
    .force('link', d3.forceLink(graphData.edges).id(d => d.id))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(400, 300));

  // Draw edges
  const links = svg.append('g')
    .selectAll('line')
    .data(graphData.edges)
    .enter().append('line')
    .attr('stroke', '#999')
    .attr('stroke-width', d => d.weight * 3);

  // Draw nodes
  const nodes = svg.append('g')
    .selectAll('circle')
    .data(graphData.nodes)
    .enter().append('circle')
    .attr('r', 10)
    .attr('fill', d => d.group === 'entity' ? 'blue' : d.group === 'event' ? 'red' : 'orange');

  // Update positions
  simulation.on('tick', () => {
    links
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y);

    nodes
      .attr('cx', d => d.x)
      .attr('cy', d => d.y);
  });
}
```

## Development

### Adding New Endpoints

1. Edit `api/app.py`
2. Add new route with `@app.route` decorator
3. Return JSON response with `jsonify()`
4. Update this README

### Testing

```bash
# Run verification
python scripts/verify_stage6.py

# Or use Flask test client
python -c "from api.app import create_app; app = create_app(); client = app.test_client(); print(client.get('/health').get_json())"
```

## Production Deployment

For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "api.app:create_app()"
```

Or use Docker:

```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "api.app:create_app()"]
```
