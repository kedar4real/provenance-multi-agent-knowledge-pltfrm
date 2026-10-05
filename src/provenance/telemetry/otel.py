"""OpenTelemetry tracing over OTLP (Jaeger in docker compose, profile "observability").

Off unless OTEL_EXPORTER_OTLP_ENDPOINT is set (e.g. http://127.0.0.1:4318). Then every HTTP
request is a trace (FastAPI instrumentation), the controller adds a span for the run, and
each controller decision and agent step becomes a child span with its measured duration
and its decision details as attributes: route, cache, plan, search, sql, write, verify,
score, escalate, abstain.

Only scalar attributes are exported and long strings are cut, so answers and evidence
passages never leave the process (short diagnostics do, such as a number that failed
verification); questions are already redacted before any step sees them.
"""

import time
from collections.abc import Iterator
from typing import Any

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.context import Context
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter
from opentelemetry.trace import Span, Tracer

from provenance.agents.types import TraceEvent

MAX_ATTRIBUTE_CHARS = 200


def setup_tracing(
    app: FastAPI, endpoint: str, exporter: SpanExporter | None = None
) -> TracerProvider:
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    provider = TracerProvider(resource=Resource.create({"service.name": "provenance-api"}))
    exporter = exporter or OTLPSpanExporter(endpoint=endpoint.rstrip("/") + "/v1/traces")
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(
        app, tracer_provider=provider, excluded_urls="health/live,health/ready,metrics"
    )
    return provider


def tracer() -> Tracer:
    """The process tracer: a no-op until setup_tracing has run."""
    return trace.get_tracer("provenance")


def record_step(t: Tracer, parent: Span, event: TraceEvent) -> None:
    """A step that just finished, as a child span lasting the step's measured time.
    Spans are created after the fact because the steps run inside LangGraph's tasks."""
    end = time.time_ns()
    span = t.start_span(
        f"step.{event.step}",
        context=trace.set_span_in_context(parent, Context()),
        start_time=end - int(event.ms * 1_000_000),
    )
    for key, value in _flatten(event.detail):
        span.set_attribute(f"provenance.{event.step}.{key}", value)
    span.end(end_time=end)


def _flatten(detail: dict[str, Any], prefix: str = "") -> Iterator[tuple[str, Any]]:
    for key, value in detail.items():
        name = f"{prefix}{key}"
        if isinstance(value, dict):
            yield from _flatten(value, f"{name}.")
        elif isinstance(value, bool | int | float):
            yield name, value
        elif isinstance(value, str):
            yield name, value[:MAX_ATTRIBUTE_CHARS]
        elif isinstance(value, list) and all(isinstance(v, str | int | float) for v in value):
            yield name, [str(v)[:MAX_ATTRIBUTE_CHARS] for v in value[:20]]
