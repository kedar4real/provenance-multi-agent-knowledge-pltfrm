"""PII redaction applied before any text is embedded, stored, or sent to a model provider.

`RedactedText` can only be produced by `redact()`. The embedder and the chunk store accept
only `RedactedText`, so unredacted text reaching them is a type error, not a code-review
catch. Names are deliberately not redacted: in public filings, who the executives are is
material information, and NER-based name detection adds a large model for little benefit.
"""

import re
from collections import Counter
from collections.abc import Callable

_TOKEN = object()

_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_CARD_CANDIDATE = re.compile(r"(?<![\d-])(?:\d[ -]?){12,18}\d(?![\d-])")
_SSN = re.compile(r"(?<![\d-])(?!000|666|9\d\d)\d{3}-(?!00)\d{2}-(?!0000)\d{4}(?![\d-])")
_US_PHONE = re.compile(r"(?<![\w+])(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?![\w-])")
_INTL_PHONE = re.compile(r"(?<![\w+])\+\d{1,3}(?:[ .-]\d{1,4}){2,4}(?![\w-])")
# Issuer prefixes (Visa, Mastercard incl. 2-series, Amex, Discover). Luhn alone passes ~10%
# of random digit strings, e.g. year column headers like "2025 2024 2025 2024".
_CARD_ISSUER = re.compile(
    r"^(?:4|5[1-5]|2(?:22[1-9]|2[3-9]\d|[3-6]\d\d|7[01]\d|720)|3[47]|6(?:011|5|4[4-9]))"
)


class RedactedText:
    __slots__ = ("counts", "text")

    def __init__(self, *, text: str, counts: dict[str, int], _token: object) -> None:
        if _token is not _TOKEN:
            raise TypeError("RedactedText can only be created by provenance.security.pii.redact")
        self.text = text
        self.counts = counts

    def slice(self, start: int, end: int) -> "RedactedText":
        """A substring of redacted text contains no PII, so it keeps the guarantee."""
        return RedactedText(text=self.text[start:end], counts={}, _token=_TOKEN)

    @property
    def total(self) -> int:
        return sum(self.counts.values())

    def __repr__(self) -> str:
        return f"RedactedText({self.text[:40]!r}..., redactions={self.total})"


def redact(text: str) -> RedactedText:
    counts: Counter[str] = Counter()
    text = _EMAIL.sub(_replacer("EMAIL", counts), text)
    text = _CARD_CANDIDATE.sub(_card_replacer(counts), text)
    text = _SSN.sub(_replacer("SSN", counts), text)
    text = _US_PHONE.sub(_replacer("PHONE", counts), text)
    text = _INTL_PHONE.sub(_replacer("PHONE", counts), text)
    return RedactedText(text=text, counts=dict(counts), _token=_TOKEN)


def _replacer(kind: str, counts: Counter[str]) -> Callable[[re.Match[str]], str]:
    def replace(_: re.Match[str]) -> str:
        counts[kind] += 1
        return f"[{kind}]"

    return replace


def _card_replacer(counts: Counter[str]) -> Callable[[re.Match[str]], str]:
    def replace(match: re.Match[str]) -> str:
        digits = re.sub(r"\D", "", match.group())
        if 13 <= len(digits) <= 19 and _CARD_ISSUER.match(digits) and _luhn_valid(digits):
            counts["CARD"] += 1
            return "[CARD]"
        return match.group()

    return replace


def _luhn_valid(digits: str) -> bool:
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 1:
            d = d * 2 - 9 if d > 4 else d * 2
        total += d
    return total % 10 == 0
