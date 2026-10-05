"""The answer cache on the in-memory store: exact and semantic hits, the entity guard,
permission scoping, expiry and the off switch."""

import json

import numpy as np

from provenance.controller.cache import AnswerCache, MemoryCacheStore, groups_hash
from provenance.controller.policy import CacheConfig

TECH, FINANCE = ["analyst_tech"], ["analyst_finance"]


class TableEmbedder:
    """Every question maps to the same vector unless told otherwise: the worst case for a
    semantic cache, where only the threshold and the guard stand between it and a wrong hit."""

    def __init__(self, vectors: dict[str, list[float]] | None = None) -> None:
        self.vectors = vectors or {}

    def __call__(self, question: str) -> np.ndarray:
        return np.asarray(self.vectors.get(question, [1.0, 0.0, 0.0]), dtype=np.float32)


def payload(question: str) -> str:
    return json.dumps({"question": question, "result": {"answer": "cached"}})


def make(guard: bool = True, vectors: dict[str, list[float]] | None = None) -> AnswerCache:
    config = CacheConfig(similarity=0.95, entity_guard=guard)
    return AnswerCache(MemoryCacheStore(), TableEmbedder(vectors), config)


async def test_the_same_question_hits_exactly_whatever_its_case_or_spacing() -> None:
    cache = make()
    await cache.store("What risks does Nvidia list?", TECH, payload("q"))

    found, lookup = await cache.lookup("  what risks does NVIDIA list ", TECH)

    assert found is not None and lookup.kind == "exact" and lookup.similarity == 1.0


async def test_a_paraphrase_with_the_same_entities_hits_semantically() -> None:
    cache = make()
    await cache.store("What risks does Nvidia list?", TECH, payload("What risks does Nvidia list?"))

    found, lookup = await cache.lookup("Which risk factors does Nvidia report?", TECH)

    assert found is not None and lookup.kind == "semantic"
    assert lookup.matched_question == "What risks does Nvidia list?"


async def test_the_guard_blocks_a_near_miss_that_embeds_identically() -> None:
    guarded, unguarded = make(guard=True), make(guard=False)
    for cache in (guarded, unguarded):
        await cache.store("Apple revenue in 2024", TECH, payload("Apple revenue in 2024"))

    assert (await guarded.lookup("Apple revenue in 2023", TECH))[0] is None
    assert (await guarded.lookup("Microsoft revenue in 2024", TECH))[0] is None
    assert (await guarded.lookup("Apple net income in 2024", TECH))[0] is None
    # Without the guard the identical embedding is a (wrong) hit: why the guard exists.
    assert (await unguarded.lookup("Apple revenue in 2023", TECH))[0] is not None


async def test_dissimilar_questions_miss_and_report_the_nearest_similarity() -> None:
    cache = make(vectors={"Nvidia risks": [1, 0, 0], "Nvidia risks, briefly": [0.6, 0.8, 0]})
    await cache.store("Nvidia risks", TECH, payload("Nvidia risks"))

    found, lookup = await cache.lookup("Nvidia risks, briefly", TECH)

    assert found is None and not lookup.hit and lookup.similarity == 0.6


async def test_answers_never_cross_permission_groups() -> None:
    cache = make()
    await cache.store("JPMorgan net interest income", FINANCE, payload("x"))

    assert (await cache.lookup("JPMorgan net interest income", TECH))[0] is None
    assert (await cache.lookup("JPMorgan net interest income", FINANCE))[0] is not None
    assert groups_hash(["a", "b"]) == groups_hash(["b", "a", "a"])


async def test_an_expired_answer_misses_and_its_vector_is_dropped() -> None:
    store = MemoryCacheStore()
    cache = AnswerCache(store, TableEmbedder(), CacheConfig(similarity=0.95))
    await cache.store("Nvidia risks", TECH, payload("Nvidia risks"))
    namespace = cache.namespace(TECH)
    store.payloads.clear()  # what a TTL expiry looks like

    found, _ = await cache.lookup("Nvidia risk factors", TECH)

    assert found is None and store.vectors[namespace] == {}


async def test_a_disabled_cache_neither_stores_nor_finds() -> None:
    store = MemoryCacheStore()
    cache = AnswerCache(store, TableEmbedder(), CacheConfig(enabled=False))
    await cache.store("Nvidia risks", TECH, payload("x"))

    found, lookup = await cache.lookup("Nvidia risks", TECH)

    assert found is None and lookup.kind == "off" and store.payloads == {}
