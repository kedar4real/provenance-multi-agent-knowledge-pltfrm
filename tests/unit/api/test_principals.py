import json
from pathlib import Path

import pytest

from provenance.api import keys
from provenance.api.principals import Principal, PrincipalRegistry, hash_key

ANA = Principal(name="ana", display_name="Ana", groups=["analyst_tech"])


def test_authenticates_a_known_key() -> None:
    registry = PrincipalRegistry({"ana": ANA}, {hash_key("pk_secret"): "ana"})

    assert registry.authenticate("pk_secret") == ANA


def test_rejects_an_unknown_key() -> None:
    registry = PrincipalRegistry({"ana": ANA}, {hash_key("pk_secret"): "ana"})

    assert registry.authenticate("pk_other") is None


def test_refuses_keys_for_principals_that_do_not_exist() -> None:
    with pytest.raises(ValueError, match="ghost"):
        PrincipalRegistry({"ana": ANA}, {hash_key("pk_x"): "ghost"})


def test_principal_needs_a_group() -> None:
    with pytest.raises(ValueError):
        Principal(name="nobody", display_name="Nobody", groups=[])


def test_missing_key_file_means_no_keys(principals_path: Path, tmp_path: Path) -> None:
    registry = PrincipalRegistry.load(principals_path, tmp_path / "absent.json")

    assert set(registry.principals) == {"ana_tech", "rhea_research"}
    assert registry.authenticate("pk_anything") is None


@pytest.fixture
def key_env(principals_path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    keys_path = tmp_path / "api_keys.json"
    monkeypatch.setenv("PRINCIPALS_PATH", str(principals_path))
    monkeypatch.setenv("API_KEYS_PATH", str(keys_path))
    monkeypatch.setenv("RLS_SIGNING_KEY", "unit-test-key")
    return keys_path


def _issued_key(output: str) -> str:
    return output.strip().splitlines()[-1]


def test_issue_stores_only_the_hash(key_env: Path, capsys: pytest.CaptureFixture[str]) -> None:
    keys.main(["issue", "ana_tech"])
    key = _issued_key(capsys.readouterr().out)

    stored = key_env.read_text(encoding="utf-8")
    assert key.startswith("pk_")
    assert key not in stored
    assert json.loads(stored) == {hash_key(key): "ana_tech"}


def test_reissue_replaces_the_old_key(key_env: Path, capsys: pytest.CaptureFixture[str]) -> None:
    keys.main(["issue", "ana_tech"])
    old = _issued_key(capsys.readouterr().out)
    keys.main(["issue", "ana_tech"])
    new = _issued_key(capsys.readouterr().out)

    assert json.loads(key_env.read_text(encoding="utf-8")) == {hash_key(new): "ana_tech"}
    assert old != new


def test_revoke_removes_the_key(key_env: Path) -> None:
    keys.main(["issue", "ana_tech"])
    keys.main(["issue", "rhea_research"])
    keys.main(["revoke", "ana_tech"])

    assert list(json.loads(key_env.read_text(encoding="utf-8")).values()) == ["rhea_research"]


def test_issue_for_unknown_principal_fails(key_env: Path) -> None:
    with pytest.raises(SystemExit):
        keys.main(["issue", "ghost"])
    assert not key_env.exists()
