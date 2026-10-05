"""Detectors for text an LLM will read: tool descriptions and schemas (tool poisoning) and tool
outputs (indirect prompt injection).

Heuristics first: fast, explainable, and they name what they found. An optional local
classifier is a second layer for phrasings the patterns miss. Both are evidence, not proof:
the gate's real protection is that a blocked tool is never shown or called.
"""

import re
from collections.abc import Iterator
from typing import Any, Protocol

from pydantic import BaseModel

# DOTALL: payloads wrap lines ("Do not mention\nthis to the user"); every gap is bounded.
_I = re.IGNORECASE | re.DOTALL
PATTERNS: dict[str, re.Pattern[str]] = {
    # Markup that hides instructions from a human skimming the description.
    "hidden_instruction_tag": re.compile(
        r"<\s*/?\s*(important|system|instructions?|secret|hidden|admin)\b[^>]*>|\[/?INST\]|<!--", _I
    ),
    "override": re.compile(
        r"\b(ignore|disregard|forget|override)\b.{0,40}\b(previous|prior|above|earlier|all|any|"
        r"other|system)\b.{0,20}\b(instructions?|rules|prompts?|guidelines|messages)\b",
        _I,
    ),
    "conceal_from_user": re.compile(
        r"\b(do not|don't|never|must not)\b.{0,30}\b(tell|inform|mention|reveal|show|notify|"
        r"alert)\b.{0,30}\buser\b|\bwithout\b.{0,20}\b(telling|informing|notifying)\b.{0,15}\buser\b|"
        r"\b(the )?user\b.{0,20}\b(must not|should not|shouldn't|need not)\b.{0,20}\b(know|see|"
        r"notice|be told)\b",
        _I,
    ),
    "sensitive_files": re.compile(
        r"~/\.ssh|\bid_(rsa|ed25519|ecdsa)\b|\.aws/credentials|/etc/(passwd|shadow)|"
        r"\bmcp\.json\b|\.cursor/|\.env\b|\bprivate[ _-]?key\b|\bkeychain\b|\bwallet\.dat\b",
        _I,
    ),
    "exfiltration": re.compile(
        r"\b(send|post|upload|forward|transmit|exfiltrate|leak|bcc|cc)\b.{0,60}\b(to|into)\b.{0,40}"
        r"(https?://|\b[\w.+-]+@[\w-]+\.[\w.]+|\bwebhook\b|\bremote server\b)|"
        r"\b(pass|put|include|embed)\b.{0,40}\b(contents?|file|key|token|password|credentials?)\b"
        r".{0,40}\b(as|in|into)\b.{0,20}\b(parameter|argument|field|sidenote|note)\b",
        _I,
    ),
    "tool_shadowing": re.compile(
        r"\b(when|whenever|before|after)\b.{0,40}\b(the|any|another|other)\b.{0,30}\btool\b.{0,40}"
        r"\b(is|are|gets?)\b.{0,10}\b(called|used|invoked|available)\b|"
        r"\b(instead of|rather than)\b.{0,30}\b(the )?\w+ tool\b|"
        # A description laying down rules for some *other* named tool.
        r"\bthe\s+[\w-]+\s+tool\b.{0,20}\b(must|should|shall|always|needs? to|has to)\b|"
        r"\b(all|every)\b.{0,20}\b(emails?|messages?|requests?)\b.{0,40}\bmust\b",
        _I,
    ),
    "role_injection": re.compile(
        r"(^|\n)\s*(system|assistant)\s*:|\byou are now\b|\bnew instructions?\b\s*:|"
        r"\bact as\b.{0,30}\b(admin|root|developer mode|dan)\b",
        _I,
    ),
    # Zero-width, bidi-override and Unicode "tag" characters: text a model reads but a human
    # reviewing the tool list can't see.
    "hidden_characters": re.compile(
        "[\u200b-\u200f\u202a-\u202e\u2060-\u2064\u2066-\u2069\ufeff\U000e0000-\U000e007f]"
    ),
    "encoded_payload": re.compile(r"[A-Za-z0-9+/]{120,}={0,2}"),
}
# Findings that only warrant a warning on their own.
SOFT = frozenset({"very_long"})
MAX_DESCRIPTION_CHARS = 2000


class Finding(BaseModel):
    where: str  # e.g. "description", "inputSchema.properties.city.description", "output"
    reason: str
    excerpt: str


class Classifier(Protocol):
    def injection_probability(self, texts: list[str]) -> list[float]: ...


def scan_text(text: str, where: str) -> list[Finding]:
    findings = []
    for reason, pattern in PATTERNS.items():
        match = pattern.search(text)
        if match:
            start = max(0, match.start() - 30)
            excerpt = text[start : match.end() + 30].encode("unicode_escape").decode("ascii")
            findings.append(Finding(where=where, reason=reason, excerpt=excerpt[:160]))
    return findings


def strings_in(value: Any, path: str) -> Iterator[tuple[str, str]]:
    """Every string in a JSON value with its path: descriptions, titles, defaults, enums,
    examples and property names all reach the model."""
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield f"{path}.{key}<key>", str(key)
            yield from strings_in(item, f"{path}.{key}")
    elif isinstance(value, list):
        for i, item in enumerate(value):
            yield from strings_in(item, f"{path}[{i}]")


def scan_tool(tool: dict[str, Any], classifier: Classifier | None = None) -> list[Finding]:
    """Tool poisoning: hidden instructions anywhere the model will read about this tool."""
    findings = []
    texts = [("name", str(tool.get("name", "")))]
    for field in ("title", "description"):
        if tool.get(field):
            texts.append((field, str(tool[field])))
    for field in ("inputSchema", "outputSchema", "annotations"):
        texts += list(strings_in(tool.get(field) or {}, field))
    for where, text in texts:
        findings += scan_text(text, where)
    description = str(tool.get("description") or "")
    if len(description) > MAX_DESCRIPTION_CHARS:
        findings.append(Finding(where="description", reason="very_long",
                                excerpt=f"{len(description)} characters"))  # fmt: skip
    if classifier is not None and description:
        (p,) = classifier.injection_probability([description])
        if p >= 0.9:
            findings.append(Finding(where="description", reason="classifier", excerpt=f"p={p:.2f}"))
    return findings


def scan_output(texts: list[str], classifier: Classifier | None = None) -> list[Finding]:
    """Indirect prompt injection in what a tool returned."""
    findings = [f for i, t in enumerate(texts) for f in scan_text(t, f"output[{i}]")]
    findings = [f for f in findings if f.reason != "encoded_payload"]  # data is often encoded
    if classifier is not None and texts:
        for i, p in enumerate(classifier.injection_probability(texts)):
            if p >= 0.9:
                findings.append(Finding(where=f"output[{i}]", reason="classifier",
                                        excerpt=f"p={p:.2f}"))  # fmt: skip
    return findings


def blocking(findings: list[Finding]) -> list[Finding]:
    return [f for f in findings if f.reason not in SOFT]


class TransformersClassifier:
    """protectai/deberta-v3-base-prompt-injection-v2 on CPU (the `classifier` extra)."""

    MODEL = "protectai/deberta-v3-base-prompt-injection-v2"

    def __init__(self) -> None:
        from transformers import pipeline

        self._pipe = pipeline("text-classification", model=self.MODEL, truncation=True,
                              max_length=512, device="cpu")  # fmt: skip

    def injection_probability(self, texts: list[str]) -> list[float]:
        out = []
        for result in self._pipe(texts):
            score = float(result["score"])
            out.append(score if result["label"] == "INJECTION" else 1 - score)
        return out
