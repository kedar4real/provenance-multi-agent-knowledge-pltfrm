"""Natural-language inference on CPU: does this evidence entail, contradict, or neither?"""

import numpy as np
from sentence_transformers import CrossEncoder

from provenance.retrieval.models import load_cached_first

MODEL_NAME = "cross-encoder/nli-deberta-v3-base"
# The model's label order (from its config): contradiction, entailment, neutral.
CONTRADICTION, ENTAILMENT, NEUTRAL = 0, 1, 2
# Evidence is split into overlapping word windows so long passages fit the model (512
# tokens shared between evidence and claim); a claim is entailed if any window entails it.
WINDOW_WORDS, STRIDE_WORDS = 220, 160


class NliModel:
    def __init__(self, model_name: str = MODEL_NAME) -> None:
        self._model = load_cached_first(
            lambda **kw: CrossEncoder(model_name, device="cpu", max_length=512, **kw)
        )

    def scores(self, evidence: list[str], claim: str) -> tuple[float, float]:
        """(max entailment, max contradiction) probability over all evidence windows."""
        windows = [w for text in evidence for w in _windows(text)]
        if not windows:
            return 0.0, 0.0
        logits = np.asarray(self._model.predict([(w, claim) for w in windows], batch_size=16))
        probs = _softmax(logits)
        return float(probs[:, ENTAILMENT].max()), float(probs[:, CONTRADICTION].max())


def _windows(text: str) -> list[str]:
    words = text.split()
    if len(words) <= WINDOW_WORDS:
        return [text] if words else []
    starts = range(0, len(words) - WINDOW_WORDS + STRIDE_WORDS, STRIDE_WORDS)
    return [" ".join(words[s : s + WINDOW_WORDS]) for s in starts]


def _softmax(logits: np.ndarray) -> np.ndarray:
    shifted = np.exp(logits - logits.max(axis=1, keepdims=True))
    out: np.ndarray = shifted / shifted.sum(axis=1, keepdims=True)
    return out
