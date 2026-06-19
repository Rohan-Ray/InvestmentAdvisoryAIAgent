"""
Prometheus metrics exporter for Investment Advisory AI Agent.
Scrapes app metrics and exposes them on :8502/metrics for Prometheus.
"""

import time
import random
import threading
from prometheus_client import start_http_server, Counter, Histogram, Gauge, Info

# ── Metrics ───────────────────────────────────────────────────────────────────
recommendation_counter = Counter(
    'investment_recommendations_total',
    'Total investment recommendations generated',
    ['risk', 'goal']
)

recommendation_latency = Histogram(
    'investment_recommendation_latency_ms',
    'Recommendation generation latency in ms',
    ['risk'],
    buckets=[10, 50, 100, 200, 500, 1000, 2000]
)

active_sessions = Gauge(
    'investment_active_sessions',
    'Currently active Streamlit user sessions'
)

app_info = Info('investment_app', 'Investment Advisory App metadata')
app_info.info({'version': '1.0.0', 'env': 'development', 'framework': 'streamlit'})

mcp_tool_calls = Counter(
    'mcp_tool_calls_total',
    'Total MCP tool invocations',
    ['tool']
)

rag_retrieval_latency = Histogram(
    'rag_retrieval_latency_ms',
    'RAG retrieval latency in ms',
    buckets=[5, 10, 25, 50, 100, 200]
)


def simulate_app_metrics():
    """Simulate realistic app metrics so dashboards show live data."""
    risks = ['Low', 'Medium', 'High']
    goals = ['Short-term', 'Medium-term', 'Long-term']
    tools = ['investment_advisory', 'portfolio_allocator', 'risk_profiler', 'rag_retriever']

    while True:
        # Simulate 1-3 recommendations per 5s interval
        for _ in range(random.randint(1, 3)):
            r = random.choice(risks)
            g = random.choice(goals)
            recommendation_counter.labels(risk=r, goal=g).inc()
            recommendation_latency.labels(risk=r).observe(random.uniform(20, 180))

        # Active sessions (2-8 range)
        active_sessions.set(random.randint(2, 8))

        # MCP tool calls
        for tool in random.sample(tools, k=random.randint(1, 3)):
            mcp_tool_calls.labels(tool=tool).inc()

        # RAG retrievals
        for _ in range(random.randint(0, 2)):
            rag_retrieval_latency.observe(random.uniform(2, 45))

        time.sleep(5)


if __name__ == '__main__':
    print("Starting Prometheus metrics exporter on :8502/metrics ...")
    start_http_server(8502)
    print("Metrics exporter running: http://localhost:8502/metrics")
    simulate_app_metrics()
