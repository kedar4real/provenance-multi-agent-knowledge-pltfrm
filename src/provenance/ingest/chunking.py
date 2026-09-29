"""Semantic chunking: split where the topic shifts, bounded by the embedding model's limit."""

import re
from collections.abc import Callable

import numpy as np
from pydantic import BaseModel

_SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"“(])")

Embed = Callable[[list[str]], np.ndarray]
CountTokens = Callable[[str], int]


class Chunk(BaseModel):
    text: str
    char_start: int
    char_end: int
    token_count: int


def semantic_chunks(
    text: str,
    embed: Embed,
    count_tokens: CountTokens,
    max_tokens: int = 400,
    min_tokens: int = 80,
    breakpoint_percentile: float = 90.0,
) -> list[Chunk]:
    """Groups consecutive paragraphs; a new chunk starts at the section's largest topic shifts.

    A "topic shift" is the cosine distance between neighbouring paragraph embeddings; shifts
    above the section's `breakpoint_percentile` start a new chunk once the current one has
    `min_tokens`. The token limit always wins. Offsets index into `text`.
    """
    units = _units(text, count_tokens, max_tokens)
    if not units:
        return []
    shifts = _topic_shifts(embed([text[s:e] for s, e in units]))
    threshold = float(np.percentile(shifts, breakpoint_percentile)) if len(shifts) else 0.0

    groups: list[list[tuple[int, int]]] = [[units[0]]]
    for i in range(1, len(units)):
        current = groups[-1]
        tokens_now = count_tokens(text[current[0][0] : current[-1][1]])
        tokens_if_added = count_tokens(text[current[0][0] : units[i][1]])
        topic_break = shifts[i - 1] > threshold and tokens_now >= min_tokens
        if tokens_if_added > max_tokens or topic_break:
            groups.append([units[i]])
        else:
            current.append(units[i])

    if len(groups) > 1:
        tail, previous = groups[-1], groups[-2]
        tail_tokens = count_tokens(text[tail[0][0] : tail[-1][1]])
        merged_tokens = count_tokens(text[previous[0][0] : tail[-1][1]])
        if tail_tokens < min_tokens and merged_tokens <= max_tokens:
            previous.extend(groups.pop())

    return [_chunk(text, g[0][0], g[-1][1], count_tokens) for g in groups]


def _chunk(text: str, start: int, end: int, count_tokens: CountTokens) -> Chunk:
    body = text[start:end]
    return Chunk(text=body, char_start=start, char_end=end, token_count=count_tokens(body))


def _topic_shifts(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    unit = vectors / np.where(norms == 0, 1, norms)
    similarity: np.ndarray = (unit[:-1] * unit[1:]).sum(axis=1)
    return 1.0 - similarity


def _units(text: str, count_tokens: CountTokens, max_tokens: int) -> list[tuple[int, int]]:
    """Paragraph spans; paragraphs over the limit become sentence (then word-window) spans."""
    spans: list[tuple[int, int]] = []
    for para in re.finditer(r"[^\n]+", text):
        start, end = para.start(), para.end()
        if not text[start:end].strip():
            continue
        if count_tokens(text[start:end]) <= max_tokens:
            spans.append((start, end))
            continue
        for sentence in _split(start, end, _SENTENCE_END, text):
            if count_tokens(text[sentence[0] : sentence[1]]) <= max_tokens:
                spans.append(sentence)
            else:
                spans.extend(_word_windows(text, *sentence, count_tokens, max_tokens))
    return spans


def _split(start: int, end: int, pattern: re.Pattern[str], text: str) -> list[tuple[int, int]]:
    pieces, cursor = [], start
    for m in pattern.finditer(text, start, end):
        pieces.append((cursor, m.start()))
        cursor = m.end()
    pieces.append((cursor, end))
    return [(s, e) for s, e in pieces if text[s:e].strip()]


def _word_windows(
    text: str, start: int, end: int, count_tokens: CountTokens, max_tokens: int
) -> list[tuple[int, int]]:
    windows: list[tuple[int, int]] = []
    words = list(re.finditer(r"\S+", text[start:end]))
    w_start = 0
    for i in range(1, len(words) + 1):
        span_text = text[start + words[w_start].start() : start + words[i - 1].end()]
        if count_tokens(span_text) > max_tokens and i - 1 > w_start:
            windows.append((start + words[w_start].start(), start + words[i - 2].end()))
            w_start = i - 1
    if w_start < len(words):
        windows.append((start + words[w_start].start(), start + words[-1].end()))
    return windows
