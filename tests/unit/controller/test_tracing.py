"""Each controller run is a span; each step is a child span with its decisions as attributes,
and answer text never reaches the trace."""

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from tests.unit.controller.test_executor import GOOD, INVENTED, RoleLLM, ask, controller


async def test_a_run_is_one_span_with_a_child_per_step() -> None:
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    llm = RoleLLM({"serve_small": [INVENTED, INVENTED], "serve_large": [GOOD]})

    _, events, _ = await ask(controller(llm, tracer=provider.get_tracer("test")))

    spans = exporter.get_finished_spans()
    run = next(s for s in spans if s.name == "controller.run")
    steps = [s for s in spans if s.name.startswith("step.")]
    assert [s.name for s in steps] == [f"step.{e.step}" for e in events]
    assert all(s.parent is not None and s.parent.span_id == run.context.span_id for s in steps)
    assert run.attributes is not None
    assert run.attributes["provenance.tier"] == "large"
    assert run.attributes["provenance.escalated"] == "failed_verification"
    route = next(s for s in steps if s.name == "step.route")
    assert route.attributes is not None and route.attributes["provenance.route.tier"] == "small"
    # Diagnostics such as the numbers that failed verification are kept; sentences aren't.
    exported = " ".join(str(v) for s in spans for v in (s.attributes or {}).values())
    assert "Net interest income was" not in exported
