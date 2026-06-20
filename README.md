# Investment Advisory AI Agent

> **DISCLAIMER:** This is an educational demo only. It does not constitute real financial advice.
> Always consult a SEBI-registered investment advisor before making investment decisions.

A beginner-friendly Investment Advisory AI Agent for banking customers, built with **Python** and **Streamlit**.

---

## What It Does

Collects 5 inputs from the user and suggests a personalised investment allocation across 5 categories using simple rule-based logic:

| Input | Options |
|-------|---------|
| Age | 18–80 |
| Monthly Income (₹) | Any positive amount |
| Monthly Savings (₹) | 0 to income |
| Risk Preference | Low / Medium / High |
| Investment Goal | Short-term / Medium-term / Long-term |

**Output:** Portfolio allocation pie chart + rupee breakdown + plain-language explanation.

---

## Investment Categories

| Category | Risk | Best For |
|----------|------|----------|
| Fixed Deposit | Low | Capital safety, short-to-medium term |
| Recurring Deposit | Low | Building savings discipline |
| Bonds | Low–Medium | Steady income, medium term |
| Mutual Funds | Medium | Diversified growth |
| Equity | High | Long-term wealth creation |

---

## Architecture

```
InvestmentAdvisoryAIAgent/
├── src/
│   ├── frontend/app.py          # Streamlit UI
│   ├── backend/advisor.py       # Rule engine + allocation logic
│   ├── backend/plugins.py       # Internal tool plugins for agents
│   └── rag/engine.py            # RAG retriever (ChromaDB + keyword fallback)
├── mcp/
│   ├── server.py                # Custom MCP server (stdio)
│   └── claude_mcp_config.json   # MCP client configuration
├── config/
│   ├── isolation.yaml           # Sub-agent isolation scopes
│   ├── delegation.yaml          # Task routing and context trimming
│   ├── reusable_setup.yaml      # Scalable app configuration
│   └── prompt_engineering.yaml  # System prompts and few-shot examples
├── tests/
│   ├── test_advisor.py          # 24 rule engine tests
│   ├── test_plugins.py          # 4 plugin tool tests
│   └── test_rag.py              # 5 RAG engine tests
├── observability/
│   ├── otel_config.py           # OpenTelemetry traces + metrics
│   ├── metrics_exporter.py      # Prometheus metrics exporter (:8502)
│   ├── prometheus.yml           # Prometheus scrape config
│   └── grafana_dashboard.json   # Import-ready Grafana dashboard
├── load-testing/
│   └── k6_script.js             # K6 load test (10 VUs, 30s)
├── knowledge-vault/
│   ├── investment_products.md   # Obsidian-ready knowledge base
│   ├── graph_nodes.json         # Graphify relational nodes + edges
│   └── vault_viewer.py          # Web viewer for vault (:8503)
├── docs/
│   └── triage-reports/          # P3-Triage-Agent review reports
└── .claude/
    ├── Settings.md              # Skills registry
    ├── settings.json            # Hooks + env config
    └── agents/
        ├── frontend-agent.md    # Frontend sub-agent definition
        ├── backend-agent.md     # Backend sub-agent definition
        └── p3-triage-agent.md   # Review and triage agent
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
pip install flask                   # required for Knowledge Vault viewer
```

---

## Running Each Service

### Streamlit App (Investment Advisor UI)

```bash
streamlit run src/frontend/app.py
```

| URL | Address |
|-----|---------|
| Local | http://localhost:8501 |
| Network | http://<your-ip>:8501 |

---

### Knowledge Vault (Obsidian-style Graph Viewer)

A web-based viewer for the investment knowledge base with Markdown rendering and an interactive concept graph.

```bash
python3 knowledge-vault/vault_viewer.py
```

Opens at **http://localhost:8503**

- **Document tab** — browse and read all investment product notes
- **Graph View tab** — interactive node graph showing relationships between investment concepts, risk levels, goals, and system components (19 nodes, 27 edges)

> **Obsidian desktop:** Alternatively open `knowledge-vault/` as a vault in the Obsidian app for full backlinks, graph view, and search.

---

### Observability Stack

#### Step 1 — Start the Prometheus metrics exporter

Exposes live app metrics (recommendations, latency, MCP calls, active sessions):

```bash
python3 observability/metrics_exporter.py
```

Metrics endpoint: **http://localhost:8502/metrics**

#### Step 2 — Start Prometheus

Scrapes the metrics exporter every 5 seconds:

```bash
prometheus --config.file=observability/prometheus.yml \
  --storage.tsdb.path=/tmp/prometheus-data \
  --web.listen-address=0.0.0.0:9091
```

Prometheus UI: **http://localhost:9091**

#### Step 3 — Start Grafana

Download Grafana OSS (one-time):

```bash
curl -sL https://dl.grafana.com/oss/release/grafana-11.4.0.linux-amd64.tar.gz \
  -o /tmp/grafana.tar.gz
tar -xzf /tmp/grafana.tar.gz -C /tmp
```

Start Grafana:

```bash
GF_SERVER_HTTP_PORT=3000 \
GF_SECURITY_ADMIN_USER=admin \
GF_SECURITY_ADMIN_PASSWORD=admin \
GF_AUTH_ANONYMOUS_ENABLED=true \
/tmp/grafana-v11.4.0/bin/grafana server \
  --homepath /tmp/grafana-v11.4.0 \
  > /tmp/grafana.log 2>&1 &
```

Grafana: **http://localhost:3000** — login: `admin` / `admin`

#### Step 4 — Add datasource and import dashboard

```bash
# Add Prometheus datasource
curl -X POST http://admin:admin@localhost:3000/api/datasources \
  -H "Content-Type: application/json" \
  -d '{"name":"Prometheus","type":"prometheus","url":"http://localhost:9091","access":"proxy","isDefault":true}'

# Import the pre-built dashboard via Grafana UI:
# Dashboards → Import → Upload observability/grafana_dashboard.json
```

Pre-built dashboard: **http://localhost:3000/d/invest-advisory-v1**

Dashboard panels:
- Total recommendations counter
- Recommendation latency p95 (timeseries)
- Breakdown by risk profile (pie chart)
- Breakdown by goal horizon (pie chart)

---

### MCP Server

Exposes the rule engine, portfolio allocator, risk profiler, and RAG retriever as Claude-compatible tools over stdio:

```bash
python3 mcp/server.py
```

Register with Claude Code by adding to your MCP config:

```bash
cat mcp/claude_mcp_config.json
```

---

### Run All Services at Once

#### Windows (recommended)

Run the one-time setup script to download Prometheus and Grafana into `tools/`:

```powershell
.\setup.ps1
```

Then launch all 5 services in separate windows:

```powershell
.\start-all.ps1
```

#### Linux / macOS (manual)

```bash
# Terminal 1 — Streamlit App
streamlit run src/frontend/app.py

# Terminal 2 — Knowledge Vault Viewer
python3 knowledge-vault/vault_viewer.py

# Terminal 3 — Metrics Exporter
python3 observability/metrics_exporter.py

# Terminal 4 — Prometheus
prometheus --config.file=observability/prometheus.yml \
  --storage.tsdb.path=/tmp/prometheus-data \
  --web.listen-address=0.0.0.0:9091

# Terminal 5 — Grafana (after downloading, see above)
GF_SERVER_HTTP_PORT=3000 GF_SECURITY_ADMIN_USER=admin GF_SECURITY_ADMIN_PASSWORD=admin \
/tmp/grafana-v11.4.0/bin/grafana server --homepath /tmp/grafana-v11.4.0
```

| Service | URL | Purpose |
|---------|-----|---------|
| Streamlit App | http://localhost:8501 | Main investment advisor UI |
| Knowledge Vault | http://localhost:8503 | Markdown notes + graph view |
| Grafana Dashboard | http://localhost:3000/d/invest-advisory-v1 | Live metrics dashboard |
| Prometheus | http://localhost:9091 | Metrics store + query UI |
| Metrics Exporter | http://localhost:8502/metrics | Raw Prometheus metrics |

---

### Run Tests

```bash
python3 -m pytest tests/ -v
```

---

## Rule-Based Logic

The advisor uses a 9-entry rule table (3 risk levels × 3 goal horizons) with two adjustments:

1. **Age adjustment:** If age ≥ 55, equity is reduced by 10% and reallocated to Fixed Deposit.
2. **Savings-rate adjustment:** If monthly savings < 20% of income, equity is reduced by 5% and reallocated to Recurring Deposit.

All allocations are normalised to sum to exactly 100%.

---

## Multi-Agent Architecture (AIDLC Steps 3–9)

Claude Code orchestrates three sub-agents with bounded context windows:

| Agent | Scope | Memory Budget |
|-------|-------|---------------|
| `frontend-agent` | `src/frontend/` | 12% |
| `backend-agent` | `src/backend/`, `mcp/` | 12% |
| `p3-triage-agent` | cross-cutting review | 8% |

**Context trimming:** Each agent stores only the last 8–10 prompts plus a ≤150-word rolling summary of older history.

---

## MCP Server

The custom MCP server exposes 4 tools over stdio:

| Tool | Description |
|------|-------------|
| `investment_advisory` | Full recommendation for a user profile |
| `portfolio_allocator` | Convert % allocations to ₹ amounts |
| `risk_profiler` | Composite risk score (0–10) |
| `rag_retriever` | Investment knowledge retrieval |

Register with Claude Code:

```bash
# Add to your Claude MCP config
cat mcp/claude_mcp_config.json
```

---

## Observability

- **OpenTelemetry:** Traces and metrics exported to OTLP endpoint (Grafana/SigNoz compatible).
- **Grafana Dashboard:** Import `observability/grafana_dashboard.json` for real-time metrics.
- **Hooks log:** `.claude/settings.json` hooks write to `observability/hooks.log`.

---

## Load Testing

```bash
k6 run load-testing/k6_script.js
```

Thresholds: p95 latency < 2s, error rate < 1%.

---

## Knowledge Vault (Obsidian)

Open `knowledge-vault/` as an Obsidian vault for graph view of investment concepts.  
The `graph_nodes.json` file defines relational nodes and edges for Graphify.

---

## Test Results

```
33 passed in 0.11s
```

All allocation rules verified. Disclaimer presence confirmed across all risk/goal combinations.

---

## Disclaimer

This educational demo does not constitute financial advice, is not affiliated with any bank or SEBI-registered entity, and must not be used for real investment decisions. The rule-based logic is illustrative only.
