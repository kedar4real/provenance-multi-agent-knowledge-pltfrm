import json

from provenance.llm.types import ChatRequest, ChatResponse, Usage
from provenance.retrieval.rewrite import REWRITE_ROLE, QueryRewriter
from provenance.retrieval.types import SearchFilters
from provenance.security.pii import redact

COMPANIES = {"AAPL": "Apple Inc.", "JPM": "JPMorgan Chase & Co"}


class FakeLLM:
    def __init__(self, content: str | Exception) -> None:
        self.content = content
        self.requests: list[tuple[str, ChatRequest]] = []

    async def complete(self, role: str, request: ChatRequest) -> ChatResponse:
        self.requests.append((role, request))
        if isinstance(self.content, Exception):
            raise self.content
        return ChatResponse(
            content=self.content, provider="fake", model="fake", usage=Usage(), latency_ms=1
        )


def reply(**fields: object) -> str:
    return json.dumps(fields)


async def test_returns_query_and_filters() -> None:
    llm = FakeLLM(
        reply(query="Apple tariff risk", tickers=["aapl"], fiscal_years=[2025], items=["1a"])
    )

    result = await QueryRewriter(llm, COMPANIES).rewrite(redact("apple tariffs 2025 risk factors?"))

    assert result is not None
    assert result.query == "Apple tariff risk"
    assert result.filters == SearchFilters(tickers=["AAPL"], fiscal_years=[2025], items=["1A"])


async def test_drops_unknown_tickers_items_and_absurd_years() -> None:
    llm = FakeLLM(
        reply(query="q", tickers=["AAPL", "TSLA"], fiscal_years=[2024, 20245], items=["9", "7"])
    )

    result = await QueryRewriter(llm, COMPANIES).rewrite(redact("2024 MD&A of Apple, Tesla"))

    assert result is not None
    assert result.filters == SearchFilters(tickers=["AAPL"], fiscal_years=[2024], items=["7"])


async def test_missing_optional_fields_mean_no_filters() -> None:
    result = await QueryRewriter(FakeLLM(reply(query="bank liquidity")), COMPANIES).rewrite(
        redact("bank liquidity")
    )

    assert result is not None
    assert result.filters.is_empty


async def test_unusable_output_returns_none() -> None:
    for content in ["not json", reply(tickers=["AAPL"]), reply(query="  "), "[1, 2]"]:
        result = await QueryRewriter(FakeLLM(content), COMPANIES).rewrite(redact("q"))
        assert result is None, content


async def test_provider_failure_returns_none() -> None:
    llm = FakeLLM(RuntimeError("all providers rate limited"))

    assert await QueryRewriter(llm, COMPANIES).rewrite(redact("q")) is None


async def test_prompt_lists_companies_and_sends_only_redacted_text() -> None:
    llm = FakeLLM(reply(query="q"))

    await QueryRewriter(llm, COMPANIES).rewrite(redact("email me at a.b@example.com"))

    role, request = llm.requests[0]
    assert role == REWRITE_ROLE
    assert request.json_mode
    assert "AAPL: Apple Inc." in (request.messages[0].content or "")
    assert "a.b@example.com" not in (request.messages[1].content or "")


async def test_section_filter_needs_the_section_named_in_the_question() -> None:
    llm = FakeLLM(reply(query="Nvidia data center demand", tickers=["AAPL"], items=["7"]))

    result = await QueryRewriter(llm, COMPANIES).rewrite(redact("What drives Apple's demand?"))

    assert result is not None
    assert result.filters.items == []


async def test_named_sections_are_kept() -> None:
    cases = {
        "Apple risk factors on tariffs": ["1A"],
        "What does Item 1A say?": ["1A"],
        "Summarize JPM's MD&A": ["7"],
        "management's discussion of liquidity": ["7"],
        "Describe Apple's business section": ["1"],
    }
    for question, items in cases.items():
        llm = FakeLLM(reply(query="q", items=["1", "1A", "7"]))
        result = await QueryRewriter(llm, COMPANIES).rewrite(redact(question))
        assert result is not None
        assert result.filters.items == items, question


async def test_year_filter_needs_the_year_in_the_question() -> None:
    llm = FakeLLM(reply(query="q", fiscal_years=[2024, 2025]))

    result = await QueryRewriter(llm, COMPANIES).rewrite(redact("JPM net interest income 2025"))

    assert result is not None
    assert result.filters.fiscal_years == [2025]
