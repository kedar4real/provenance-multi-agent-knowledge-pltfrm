"""Load Hugging Face models from the local cache first; download only when missing.

Without this, every start makes several network round trips to check for updates (20-90 s
of a 25 s API startup) and contacts huggingface.co even when nothing needs downloading.
"""

from collections.abc import Callable


def load_cached_first[T](load: Callable[..., T]) -> T:
    """`load(local_files_only=...)` builds the model. OSError means it isn't cached yet."""
    try:
        return load(local_files_only=True)
    except OSError:
        return load(local_files_only=False)
