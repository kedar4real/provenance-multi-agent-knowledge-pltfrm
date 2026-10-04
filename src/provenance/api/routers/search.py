"""Hybrid passage search. Results are limited to what the caller may see (row-level security
on the request's connection), and each hit carries what a citation needs."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from provenance.api.deps import DbDep, ResourcesDep
from provenance.api.errors import ApiError
from provenance.retrieval.types import Mode, SearchResult

router = APIRouter(prefix="/v1", tags=["search"])


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    k: int = Field(default=8, ge=1, le=20)
    # Switches exist so the eval harness can measure what each stage contributes.
    mode: Mode = "hybrid"
    rerank: bool = True
    rewrite: bool = True


@router.post("/search")
async def search(body: SearchRequest, resources: ResourcesDep, db: DbDep) -> SearchResult:
    if resources.retriever is None:
        raise ApiError(503, "search_unavailable", "search models are not loaded")
    return await resources.retriever.search(
        db, body.query, k=body.k, mode=body.mode, rerank=body.rerank, rewrite=body.rewrite
    )
