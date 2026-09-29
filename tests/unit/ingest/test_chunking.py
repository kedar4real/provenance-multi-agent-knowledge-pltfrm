import numpy as np

from provenance.ingest.chunking import Chunk, semantic_chunks


def fake_embed(texts: list[str]) -> np.ndarray:
    """Two-topic embedding: 'alpha' paragraphs point one way, everything else the other."""
    return np.array([[1.0, 0.0] if "alpha" in t else [0.0, 1.0] for t in texts])


def words(text: str) -> int:
    return len(text.split())


def para(topic: str, n_words: int) -> str:
    return " ".join([topic] * n_words) + "."


def chunk(text: str, **kw: int) -> list[Chunk]:
    kw = {"max_tokens": 100, "min_tokens": 10, **kw}
    return semantic_chunks(text, fake_embed, words, **kw)


def test_offsets_point_back_into_the_source_text() -> None:
    text = "\n".join([para("alpha", 30), para("alpha", 30), para("beta", 30)])

    for c in chunk(text):
        assert text[c.char_start : c.char_end] == c.text


def test_splits_at_a_topic_shift_even_when_size_allows_merging() -> None:
    text = "\n".join([para("alpha", 15), para("alpha", 15), para("beta", 15), para("beta", 15)])

    chunks = chunk(text, max_tokens=500)

    assert [("alpha" in c.text, "beta" in c.text) for c in chunks] == [(True, False), (False, True)]


def test_no_chunk_exceeds_the_token_limit() -> None:
    text = "\n".join(para("alpha", 40) for _ in range(10))

    assert all(c.token_count <= 100 for c in chunk(text))


def test_a_paragraph_longer_than_the_limit_is_split_by_sentence() -> None:
    long_paragraph = " ".join(f"Sentence {i} is about alpha things here." for i in range(60))

    chunks = chunk(long_paragraph)

    assert len(chunks) > 1
    assert all(c.token_count <= 100 for c in chunks)


def test_every_paragraph_lands_in_exactly_one_chunk_in_order() -> None:
    sizes = [("alpha", 20), ("beta", 25), ("alpha", 35), ("beta", 10)]
    paragraphs = [f"marker{i} " + para(topic, n) for i, (topic, n) in enumerate(sizes)]
    text = "\n".join(paragraphs)

    joined = "\n".join(c.text for c in chunk(text))

    positions = [joined.index(p) for p in paragraphs]
    assert positions == sorted(positions)
    assert all(joined.count(p) == 1 for p in paragraphs)


def test_small_trailing_piece_is_merged_into_the_previous_chunk() -> None:
    text = "\n".join([para("alpha", 60), para("beta", 3)])

    chunks = chunk(text, min_tokens=10)

    assert len(chunks) == 1


def test_empty_text_gives_no_chunks() -> None:
    assert chunk("   \n  ") == []
