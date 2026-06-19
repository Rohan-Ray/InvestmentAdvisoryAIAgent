"""
Step 15: OpenTelemetry instrumentation for Investment Advisory AI Agent.
Exports traces, logs, and metrics to OTLP endpoint (Grafana/SigNoz compatible).
"""

import os
import logging
import functools
import time
from typing import Callable, Any

# ── Logger ────────────────────────────────────────────────────────────────────
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    level=getattr(logging, LOG_LEVEL),
)
logger = logging.getLogger("investment.otel")


# ── OpenTelemetry setup (optional, graceful degradation) ─────────────────────

def _setup_otel():
    """Attempt to configure OpenTelemetry SDK; no-op if not installed."""
    try:
        from opentelemetry import trace, metrics
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
        from opentelemetry.sdk.resources import Resource

        endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
        service_name = os.environ.get("OTEL_SERVICE_NAME", "investment-advisory-agent")

        resource = Resource.create({"service.name": service_name})

        # Traces
        tracer_provider = TracerProvider(resource=resource)
        tracer_provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True))
        )
        trace.set_tracer_provider(tracer_provider)

        # Metrics
        metric_reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=endpoint, insecure=True),
            export_interval_millis=5000,
        )
        meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
        metrics.set_meter_provider(meter_provider)

        logger.info(f"OpenTelemetry configured → {endpoint}")
        return trace.get_tracer(service_name), metrics.get_meter(service_name)

    except ImportError:
        logger.warning("opentelemetry packages not installed — tracing disabled")
        return None, None
    except Exception as e:
        logger.warning(f"OpenTelemetry setup failed: {e} — tracing disabled")
        return None, None


_tracer, _meter = _setup_otel()

# ── Metrics ───────────────────────────────────────────────────────────────────

_recommendation_counter = None
_latency_histogram = None

if _meter:
    _recommendation_counter = _meter.create_counter(
        "investment.recommendations.total",
        description="Total investment recommendations generated",
        unit="1",
    )
    _latency_histogram = _meter.create_histogram(
        "investment.recommendation.latency_ms",
        description="Latency of recommendation generation",
        unit="ms",
    )


# ── Decorators ────────────────────────────────────────────────────────────────

def trace_call(operation_name: str):
    """Decorator: wrap a function with an OTel span and latency metric."""
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs) -> Any:
            start = time.perf_counter()

            if _tracer:
                with _tracer.start_as_current_span(operation_name) as span:
                    span.set_attribute("function", fn.__name__)
                    result = fn(*args, **kwargs)
                    span.set_attribute("success", True)
            else:
                result = fn(*args, **kwargs)

            elapsed_ms = (time.perf_counter() - start) * 1000
            if _latency_histogram:
                _latency_histogram.record(elapsed_ms, {"operation": operation_name})
            logger.debug(f"{operation_name} completed in {elapsed_ms:.1f}ms")
            return result

        return wrapper
    return decorator


def record_recommendation(risk: str, goal: str):
    """Record a recommendation metric event."""
    if _recommendation_counter:
        _recommendation_counter.add(1, {"risk": risk, "goal": goal})
    logger.info(f"Recommendation generated: risk={risk} goal={goal}")
