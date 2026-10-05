"""Prompt-injection detection: transparent heuristics plus a local classifier.

Two layers because they fail differently. Heuristics are fast, explainable and catch the
common phrasings ("ignore previous instructions", fake SYSTEM: turns, exfiltration links)
but miss paraphrases; the classifier generalizes but is a black box with its own false
positives. A passage is flagged if either is confident. Detection is one layer; isolation
(flagged passages never reach the model) and least privilege (the agent can't do anything
dangerous even if fooled) are the others.
"""

import re
from dataclasses import dataclass, field

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from provenance.retrieval.models import load_cached_first, tokenizer_works

CLASSIFIER = "protectai/deberta-v3-base-prompt-injection-v2"
CLASSIFIER_THRESHOLD = 0.9  # the model is trigger-happy on imperative business prose below this

_PATTERNS: dict[str, re.Pattern[str]] = {
    "override": re.compile(
        r"\b(ignore|disregard|forget|override)\b[^.\n]{0,40}\b(previous|prior|above|earlier|all|your)\b"
        r"[^.\n]{0,20}\b(instructions?|prompts?|rules|directions)\b",
        re.I,
    ),
    "role_injection": re.compile(r"(^|\n|\s)(system|assistant|developer)\s*:\s*\S", re.I),
    "persona": re.compile(
        r"\byou are now\b|\bact as (an? )?(admin|administrator|root|developer)\b", re.I
    ),
    "prompt_leak": re.compile(
        r"\b(reveal|print|show|repeat|output)\b[^.\n]{0,30}\b(system prompt|instructions|hidden prompt)\b",
        re.I,
    ),
    "privilege": re.compile(
        r"\b(grant|give|elevate)\b[^.\n]{0,30}\b(access|research_all|admin|privileges?)\b"
        r"|\bset\s+app\.groups\b|\bset_config\s*\(",
        re.I,
    ),
    "exfiltration": re.compile(
        r"!\[[^\]]*\]\(https?://[^)]*[?&]\w+=|\bsend\b[^.\n]{0,40}\bhttps?://", re.I
    ),
}


@dataclass
class InjectionVerdict:
    flagged: bool
    heuristics: list[str] = field(default_factory=list)
    classifier_score: float | None = None


def heuristic_hits(text: str) -> list[str]:
    return [name for name, pattern in _PATTERNS.items() if pattern.search(text)]


class InjectionClassifier:
    def __init__(self, model_name: str = CLASSIFIER) -> None:
        self._tokenizer = load_cached_first(
            lambda **kw: AutoTokenizer.from_pretrained(model_name, **kw), tokenizer_works
        )
        self._model = load_cached_first(
            lambda **kw: AutoModelForSequenceClassification.from_pretrained(model_name, **kw)
        ).eval()

    def scores(self, texts: list[str]) -> list[float]:
        """Probability of INJECTION per text (label 1 in the model's config)."""
        if not texts:
            return []
        batch = self._tokenizer(
            texts, truncation=True, max_length=512, padding=True, return_tensors="pt"
        )
        with torch.no_grad():
            logits = self._model(**batch).logits
        return [float(p) for p in torch.softmax(logits, dim=-1)[:, 1]]


class InjectionScanner:
    def __init__(self, classifier: InjectionClassifier | None) -> None:
        self._classifier = classifier

    def scan(self, texts: list[str]) -> list[InjectionVerdict]:
        scores: list[float | None] = (
            list(self._classifier.scores(texts)) if self._classifier else [None] * len(texts)
        )
        verdicts = []
        for text, score in zip(texts, scores, strict=True):
            hits = heuristic_hits(text)
            flagged = bool(hits) or (score is not None and score >= CLASSIFIER_THRESHOLD)
            verdicts.append(InjectionVerdict(flagged, hits, score))
        return verdicts
