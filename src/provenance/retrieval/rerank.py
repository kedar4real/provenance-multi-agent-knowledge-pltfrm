"""Cross-encoder reranking (CPU). Reads query and passage together, so it judges relevance
far better than comparing two independently computed vectors, but costs one model pass
per passage; it only sees the candidates fusion already picked.

Torch's thread count is process-wide; the caller sets it (see Embedder's `threads`)."""

from sentence_transformers import CrossEncoder

MODEL_NAME = "BAAI/bge-reranker-base"


class Reranker:
    def __init__(self, model_name: str = MODEL_NAME) -> None:
        self._model = CrossEncoder(model_name, device="cpu", max_length=512)

    def score(self, query: str, passages: list[str]) -> list[float]:
        if not passages:
            return []
        scores = self._model.predict([(query, p) for p in passages], batch_size=16)
        return [float(s) for s in scores]
