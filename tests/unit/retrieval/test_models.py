from provenance.retrieval.models import load_cached_first, tokenizer_works


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


def test_a_cache_hit_that_fails_its_check_is_downloaded_properly() -> None:
    calls: list[bool] = []

    def load(local_files_only: bool) -> str:
        calls.append(local_files_only)
        return "broken" if local_files_only else "model"

    assert load_cached_first(load, check=lambda m: m != "broken") == "model"
    assert calls == [True, False]


class EmptyVocab:
    def encode(self, text: str, add_special_tokens: bool = True) -> list[int]:
        return [1 for _ in text.split()]  # every word is [UNK]


class RealVocab:
    def encode(self, text: str, add_special_tokens: bool = True) -> list[int]:
        return [hash(w) % 1000 for w in text.split()]


def test_an_empty_vocabulary_tokenizer_is_detected() -> None:
    assert not tokenizer_works(EmptyVocab())
    assert tokenizer_works(RealVocab())
    assert not tokenizer_works(object())
