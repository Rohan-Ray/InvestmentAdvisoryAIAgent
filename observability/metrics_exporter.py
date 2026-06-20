"""
Prometheus metrics exporter for Investment Advisory AI Agent.
Exposes real app metrics on :8502/metrics for Prometheus.

Metrics are written by:
  - src/backend/advisor.py  → recommendation_counter, recommendation_latency,
                               claude_input_tokens, claude_output_tokens, claude_cost_usd
  - src/frontend/app.py     → active_sessions
This process simply hosts the HTTP endpoint and polls the token totals dict.
"""

import sys
import os
import time
import threading
from prometheus_client import start_http_server, Counter, Histogram, Gauge, Info

# Allow imports from project root so we can read live token totals from advisor.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
try:
    from src.backend.advisor import token_usage_totals, _CLAUDE_MODEL
    _ADVISOR_AVAILABLE = True
except ImportError:
    token_usage_totals = {"input_tokens": 0.0, "output_tokens": 0.0, "cost_usd": 0.0}
    _CLAUDE_MODEL = "bedrock.anthropic.claude-sonnet-4-6"
    _ADVISOR_AVAILABLE = False

# ── Metric definitions (imported and incremented by advisor.py and app.py) ────

recommendation_counter = Counter(
    'investment_recommendations_total',
    'Total investment recommendations generated',
    ['risk', 'goal']
)

recommendation_latency = Histogram(
    'investment_recommendation_latency_ms',
    'End-to-end recommendation latency in ms (rule engine + Sonnet)',
    ['risk'],
    buckets=[100, 250, 500, 1000, 2000, 4000, 8000]
)

active_sessions = Gauge(
    'investment_active_sessions',
    'Currently active Streamlit user sessions'
)

app_info = Info('investment_app', 'Investment Advisory App metadata')
app_info.info({'version': '1.0.0', 'env': 'development', 'framework': 'streamlit'})

# ── Claude token & cost metrics ───────────────────────────────────────────────

claude_input_tokens = Gauge(
    'claude_input_tokens_total',
    'Cumulative Claude input tokens consumed by the app',
    ['model']
)
claude_output_tokens = Gauge(
    'claude_output_tokens_total',
    'Cumulative Claude output tokens consumed by the app',
    ['model']
)
claude_cost_usd = Gauge(
    'claude_cost_usd_total',
    'Cumulative Claude API cost in USD',
    ['model']
)


def _scrape_token_metrics():
    """Poll token_usage_totals from advisor.py and push to Prometheus Gauges every 5s."""
    while True:
        claude_input_tokens.labels(model=_CLAUDE_MODEL).set(token_usage_totals["input_tokens"])
        claude_output_tokens.labels(model=_CLAUDE_MODEL).set(token_usage_totals["output_tokens"])
        claude_cost_usd.labels(model=_CLAUDE_MODEL).set(token_usage_totals["cost_usd"])
        time.sleep(5)


if __name__ == '__main__':
    print("Starting Prometheus metrics exporter on :8502/metrics ...")
    start_http_server(8502)
    print("Metrics exporter running at http://localhost:8502/metrics")
    print(f"Model: {_CLAUDE_MODEL} | Advisor module loaded: {_ADVISOR_AVAILABLE}")
    threading.Thread(target=_scrape_token_metrics, daemon=True).start()
    # Keep the process alive — metrics are written by the Streamlit process
    while True:
        time.sleep(60)
