from provenance.retrieval.models import load_cached_first


def test_uses_the_local_cache_when_it_has_the_model() -> None:
    calls: list[bool] = []

    def load(local_files_only: bool) -> str:
        calls.append(local_files_only)
        return "model"

    assert load_cached_first(load) == "model"
    assert calls == [True]


def test_downloads_only_when_the_cache_misses() -> None:
    calls: list[bool] = []

    def load(local_files_only: bool) -> str:
        calls.append(local_files_only)
        if local_files_only:
            raise OSError("not in cache")
        return "model"

    assert load_cached_first(load) == "model"
    assert calls == [True, False]
