from typing import Any, Literal

from pydantic import BaseModel, Field

from provenance.controller.cache import CacheLookup
from provenance.llm.metering import RunUsage
from provenance.retrieval.types import Hit
from provenance.security.isolation import Withheld
from provenance.sql.worker import SqlResult
from provenance.verifier.scorer import ScoredClaim


class Plan(BaseModel):
    """The supervisor's routing decision."""

    needs_text: bool = True
    needs_numbers: bool = False
    search_query: str = ""
    sql_question: str = ""


class Evidence(BaseModel):
    """One citable item: a passage (P1, P2, ...) or a row of financial data (F1, ...)."""

    id: str
    kind: Literal["passage", "fact"]
    label: str
    text: str
    chunk_id: int | None = None


class Verification(BaseModel):
    ok: bool
    unknown_citations: list[str] = Field(default_factory=list)
    unsupported_numbers: list[str] = Field(default_factory=list)
    uncited: bool = False

    def feedback(self) -> str:
        problems = []
        if self.unknown_citations:
            problems.append(
                f"cites evidence that doesn't exist: {', '.join(self.unknown_citations)}"
            )
        if self.unsupported_numbers:
            problems.append(
                "states numbers not found in the cited evidence: "
                + ", ".join(self.unsupported_numbers)
            )
        if self.uncited:
            problems.append("makes claims without citations")
        return "; ".join(problems)


class TraceEvent(BaseModel):
    """One step of the run, streamed to the client and kept in the final result."""

    step: str
    detail: dict[str, Any] = Field(default_factory=dict)
    ms: float = 0.0


class ControlReport(BaseModel):
    """What the controller decided around the agent run, and what the run cost."""

    tier: Literal["small", "large"]
    tier_reasons: list[str] = Field(default_factory=list)
    escalated: str | None = None  # the reason, when a small-tier answer was redone large
    abstained: str | None = None  # the reason, when the answer was withheld
    cache: CacheLookup | None = None
    usage: RunUsage = Field(default_factory=RunUsage)
    budget_left: int | None = None  # the caller's tokens left today


class AgentResult(BaseModel):
    question: str
    answer: str
    declined: bool
    evidence: list[Evidence]
    passages: list[Hit]
    sql: SqlResult | None
    plan: Plan
    verification: Verification | None
    revisions: int
    steps: int
    trace: list[TraceEvent]
    # Calibrated per-claim confidence (None until a calibrator has been fit); the answer's
    # confidence is its weakest claim's.
    claims: list[ScoredClaim] = Field(default_factory=list)
    # Retrieved passages kept away from the writer as suspected prompt injections.
    withheld: list[Withheld] = Field(default_factory=list)
    # Injection heuristics that matched the question itself (recorded, not blocked).
    question_flags: list[str] = Field(default_factory=list)
    confidence: float | None = None
    tier: str = "large"
    control: ControlReport | None = None
