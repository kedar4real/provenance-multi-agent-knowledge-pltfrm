"""Split an answer into claims: one per sentence or bullet, with the evidence it cites.

Deterministic on purpose: the same answer always yields the same claims, and splitting
costs no model call. Lead-in lines ("This was driven by:") make no claim and are dropped.
"""

import re

from pydantic import BaseModel

from provenance.verifier.numbers import CITATION, DECLINE

_SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"“($])")
_BULLET = re.compile(r"^\s*(?:[*-]|\d+[.)])\s+")
_MIN_WORDS = 4


class Claim(BaseModel):
    text: str
    cited: list[str]


def split_claims(answer: str) -> list[Claim]:
    if answer.strip() == DECLINE:
        return []
    claims: list[Claim] = []
    for line in answer.splitlines():
        line = _BULLET.sub("", line).strip()
        if not line:
            continue
        for sentence in _SENTENCE_END.split(line):
            cited = [c.strip() for g in CITATION.findall(sentence) for c in g.split(",")]
            text = re.sub(r"\s+", " ", CITATION.sub("", sentence)).strip(" .")
            text = text.replace("**", "")
            if len(text.split()) < _MIN_WORDS or (text.endswith(":") and not cited):
                continue
            claims.append(Claim(text=text, cited=cited))
    return claims
