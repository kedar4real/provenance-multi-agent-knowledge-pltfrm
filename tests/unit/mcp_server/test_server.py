"""provenance-mcp over an in-process MCP client, against a mocked HTTP API: the four tools,
the API key on every call, withheld injection-flagged passages, and errors the model can act on."""

import json
from typing import Any

import httpx
import pytest
from mcp import Client

from provenance.mcp_server.server import build_server

HIT = {
    "chunk_id": 7, "company": "Nvidia", "ticker": "NVDA", "fiscal_year": 2025, "item": "1A",
    "section_title": "Risk Factors", "text": "Export controls may exclude us. " * 60,
    "rerank_score": 0.91, "url": "https://sec.gov/x", "injection_flagged": False,
    "injection_reasons": [],
}  # fmt: skip
POISONED = HIT | {"chunk_id": 8, "injection_flagged": True, "injection_reasons": ["override"]}
RESULT = {
    "answer": "Export controls may exclude Nvidia from China [P1].", "declined": False,
    "verification": {"ok": True}, "confidence": None,
    "evidence": [{"id": "P1", "label": "Nvidia (NVDA) 10-K FY2025, Item 1A", "chunk_id": 7,
                  "text": "Export controls may exclude us."}],
    "control": {"tier": "small", "abstained": None, "cache": {"hit": True}},
}  # fmt: skip


def api(handler: Any) -> Any:
    def factory() -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url="http://api", headers={"X-API-Key": "pk_test"},
            transport=httpx.MockTransport(handler),
        )  # fmt: skip

    return factory


def routes(request: httpx.Request) -> httpx.Response:
    assert request.headers["X-API-Key"] == "pk_test"
    if request.url.path == "/v1/me":
        return httpx.Response(200, json={
            "name": "ana_tech", "display_name": "Ana", "groups": ["analyst_tech"],
            "visible": {"documents": 10, "chunks": 1, "financial_facts": 1, "tickers": ["NVDA"]},
        })  # fmt: skip
    if request.url.path == "/v1/search":
        assert json.loads(request.content)["k"] == 20  # clamped
        return httpx.Response(200, json={"hits": [HIT, POISONED]})
    if request.url.path == "/v1/query":
        body = f"event: step\ndata: {{}}\n\nevent: result\ndata: {json.dumps(RESULT)}\n\n"
        return httpx.Response(200, text=body)
    if request.url.path == "/v1/sources/9":
        return httpx.Response(404, json={"error": {"code": "not_found", "message": "not found"}})
    raise AssertionError(request.url.path)


async def call(name: str, args: dict[str, Any], handler: Any = routes) -> Any:
    async with Client(build_server(api(handler))) as client:
        return await client.call_tool(name, args)


async def test_four_tools_with_descriptions_the_model_reads() -> None:
    async with Client(build_server(api(routes))) as client:
        tools = {t.name: t for t in (await client.list_tools()).tools}

    assert set(tools) == {"whoami", "search_filings", "get_passage", "ask"}
    assert all(t.description and len(t.description) > 40 for t in tools.values())


async def test_search_withholds_injection_flagged_passages_and_trims_excerpts() -> None:
    result = await call("search_filings", {"query": "export controls", "k": 99})

    out = result.structured_content
    assert [p["chunk_id"] for p in out["passages"]] == [7]
    assert out["withheld_as_possible_prompt_injection"] == [
        {"chunk_id": 8, "reasons": ["override"]}
    ]
    assert len(out["passages"][0]["excerpt"]) < 720 and out["note"].endswith(
        "instructions to follow."
    )


async def test_ask_returns_the_cited_answer_and_the_controllers_report() -> None:
    out = (
        await call("ask", {"question": "What export risks does Nvidia list?"})
    ).structured_content

    assert out["answer"].endswith("[P1].") and out["verified"] is True
    assert out["evidence"][0]["chunk_id"] == 7
    assert out["from_cache"] is True and out["model_tier"] == "small"


async def test_whoami_reports_the_keys_scope() -> None:
    out = (await call("whoami", {})).structured_content

    assert out == {
        "name": "ana_tech", "groups": ["analyst_tech"], "visible_companies": ["NVDA"],
        "visible_filings": 10,
    }  # fmt: skip


async def test_api_errors_reach_the_model_with_a_hint() -> None:
    result = await call("get_passage", {"chunk_id": 9})

    assert result.is_error
    text = result.content[0].text
    assert "not found" in text and "may not be allowed to see it" in text


@pytest.mark.parametrize(
    ("status", "hint"), [(401, "PROVENANCE_API_KEY"), (429, "budget"), (503, "retry shortly")]
)
async def test_each_refusal_says_what_to_do(status: int, hint: str) -> None:
    def refuse(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json={"error": {"code": "x", "message": "refused"}})

    result = await call("whoami", {}, refuse)

    assert result.is_error and hint in result.content[0].text


async def test_an_unreachable_api_is_reported_plainly() -> None:
    def down(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused")

    result = await call("whoami", {}, down)

    assert result.is_error and "unreachable" in result.content[0].text
