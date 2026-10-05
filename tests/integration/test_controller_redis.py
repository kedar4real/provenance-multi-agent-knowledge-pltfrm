"""The answer cache and budgets on a real Redis 8: vector-set search, the attribute-filter
entity guard, permission scoping, expiry clean-up and daily budget counters."""

import json
from datetime import UTC, datetime

import numpy as np
import pytest
import redis
from redis.asyncio import Redis

from provenance.config import Settings
from provenance.controller.budget import RedisBudgetStore
from provenance.controller.cache import AnswerCache, RedisCacheStore
from provenance.controller.policy import CacheConfig

pytestmark = [pytest.mark.integration, pytest.mark.usefixtures("redis_db")]

TECH, FINANCE = ["analyst_tech"], ["analyst_finance"]
VECTORS = {
    "What risks does Nvidia list?": [1.0, 0.0, 0.0],
    "Which risk factors does Nvidia report?": [0.98, 0.199, 0.0],  # cosine 0.98
    "Nvidia risks for the data center business": [0.8, 0.6, 0.0],  # cosine 0.80
    "What risks does Nvidia list for 2024?": [1.0, 0.0, 0.0],  # identical vector, new year
}


def embed(question: str) -> np.ndarray:
    return np.asarray(VECTORS[question], dtype=np.float32)


def payload(question: str) -> str:
    return json.dumps({"question": question, "result": {}})


async def make(settings: Settings) -> tuple[AnswerCache, Redis]:
    client = Redis.from_url(settings.redis_url)
    return AnswerCache(RedisCacheStore(client), embed, CacheConfig(similarity=0.95)), client


async def test_semantic_hits_need_similarity_and_matching_entities(settings: Settings) -> None:
    cache, client = await make(settings)
    stored = "What risks does Nvidia list?"
    await cache.store(stored, TECH, payload(stored))

    paraphrase, hit = await cache.lookup("Which risk factors does Nvidia report?", TECH)
    _, far = await cache.lookup("Nvidia risks for the data center business", TECH)
    other_year, _ = await cache.lookup("What risks does Nvidia list for 2024?", TECH)
    other_groups, _ = await cache.lookup(stored, FINANCE)
    await client.aclose()

    assert paraphrase is not None and hit.kind == "semantic"
    assert hit.similarity == pytest.approx(0.98, abs=1e-3) and hit.matched_question == stored
    assert not far.hit and far.similarity == pytest.approx(0.80, abs=1e-3)
    assert other_year is None  # same embedding, but the guard filters on entities
    assert other_groups is None  # another group's namespace


async def test_an_expired_answer_removes_its_vector(
    settings: Settings, redis_db: redis.Redis
) -> None:
    cache, client = await make(settings)
    stored = "What risks does Nvidia list?"
    await cache.store(stored, TECH, payload(stored))
    namespace = cache.namespace(TECH)
    assert redis_db.ttl(f"{namespace}:vec") > 0  # unused namespaces expire as a whole
    for key in redis_db.scan_iter(f"{namespace}:item:*"):
        redis_db.delete(key)  # what a TTL expiry looks like

    found, _ = await cache.lookup("Which risk factors does Nvidia report?", TECH)
    await client.aclose()

    assert found is None and redis_db.vset().vcard(f"{namespace}:vec") == 0


async def test_daily_budgets_accumulate_per_caller_and_expire(
    settings: Settings, redis_db: redis.Redis
) -> None:
    client = Redis.from_url(settings.redis_url)
    budgets = RedisBudgetStore(client)

    await budgets.add("ana", 1200)
    total = await budgets.add("ana", 300)
    other = await budgets.spent("ben")
    await client.aclose()

    assert total == 1500 and other == 0
    assert 0 < redis_db.ttl(f"budget:ana:{datetime.now(UTC):%Y%m%d}") <= 2 * 86400
