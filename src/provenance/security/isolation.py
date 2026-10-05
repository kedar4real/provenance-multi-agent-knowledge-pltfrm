"""Keep suspected prompt injections away from the model that writes answers.

A retrieved passage is withheld if it was flagged when ingested (heuristics plus the
classifier) or, for passages not scanned yet, if the runtime heuristics fire. Withheld
passages are reported, never silently dropped, so a reviewer can see what was held back.
"""

from pydantic import BaseModel

from provenance.retrieval.types import Hit
from provenance.security.injection import heuristic_hits


class Withheld(BaseModel):
    chunk_id: int
    ticker: str
    reasons: list[str]


def quarantine(hits: list[Hit]) -> tuple[list[Hit], list[Withheld]]:
    kept: list[Hit] = []
    withheld: list[Withheld] = []
    for hit in hits:
        reasons = list(hit.injection_reasons) if hit.injection_flagged else []
        if hit.injection_flagged is None:  # not scanned at ingest: heuristics only
            reasons = heuristic_hits(hit.text)
        if reasons or hit.injection_flagged:
            withheld.append(
                Withheld(
                    chunk_id=hit.chunk_id, ticker=hit.ticker, reasons=reasons or ["classifier"]
                )
            )
        else:
            kept.append(hit)
    return kept, withheld
