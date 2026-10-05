"""Load Hugging Face models from the local cache first; download only when missing.

Without this, every start makes several network round trips to check for updates (20-90 s
of a 25 s API startup) and contacts huggingface.co even when nothing needs downloading.

A cache-only load does not always fail loudly when files are missing: with only config.json
cached, transformers 5 builds a tokenizer with an empty vocabulary and maps every word to
[UNK], and the model then returns the same answer for every input. So a cache hit is
accepted only if `check` passes; otherwise the files are fetched.
"""

from collections.abc import Callable


def load_cached_first[T](load: Callable[..., T], check: Callable[[T], bool] | None = None) -> T:
    """`load(local_files_only=...)` builds the model; `check` validates a cache-only load."""
    try:
        loaded = load(local_files_only=True)
        if check is None or check(loaded):
            return loaded
    except OSError:
        pass
    return load(local_files_only=False)


def tokenizer_works(tokenizer: object) -> bool:
    """A real vocabulary maps an ordinary sentence to more than one distinct token id."""
    encode = getattr(tokenizer, "encode", None)
    if encode is None:
        return False
    ids = encode("revenue grew in the fiscal year", add_special_tokens=False)
    return len(set(ids)) > 1
