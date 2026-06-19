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
│   └── grafana_dashboard.json   # Import-ready Grafana dashboard
├── load-testing/
│   └── k6_script.js             # K6 load test (10 VUs, 30s)
├── knowledge-vault/
│   ├── investment_products.md   # Obsidian-ready knowledge base
│   └── graph_nodes.json         # Graphify relational nodes + edges
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
```

### 2. Run the app

```bash
streamlit run src/frontend/app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

### 3. Run tests

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
