"""Local sentence embeddings (CPU). Passages must be PII-redacted; the type enforces it."""

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from provenance.security.pii import RedactedText

MODEL_NAME = "BAAI/bge-small-en-v1.5"
DIMENSIONS = 384
# bge models are trained with this instruction on queries (not on passages).
_QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "


class Embedder:
    def __init__(self, model_name: str = MODEL_NAME, threads: int = 4) -> None:
        """`threads` sets torch's process-wide CPU thread count: 4 keeps the laptop usable
        during ingestion; the API passes all cores, since reranking is latency-bound."""
        torch.set_num_threads(threads)
        self._model = SentenceTransformer(model_name, device="cpu")

    def count_tokens(self, text: str) -> int:
        return len(self._model.tokenizer(text, add_special_tokens=True, verbose=False)["input_ids"])

    def embed_passages(self, passages: list[RedactedText], headers: list[str]) -> np.ndarray:
        """`headers` is non-sensitive context (company, filing, section) prepended to each."""
        texts = [f"{h}\n{p.text}" if h else p.text for p, h in zip(passages, headers, strict=True)]
        return self._encode(texts)

    def embed_query(self, query: RedactedText) -> np.ndarray:
        vector: np.ndarray = self._encode([_QUERY_INSTRUCTION + query.text])[0]
        return vector

    def embed_for_chunking(self, units: list[str]) -> np.ndarray:
        """Only for measuring topic shifts inside already-redacted section text; never stored."""
        return self._encode(units)

    def _encode(self, texts: list[str]) -> np.ndarray:
        vectors: np.ndarray = self._model.encode(
            texts, batch_size=32, normalize_embeddings=True, convert_to_numpy=True
        )
        return vectors
