"""Callers and their access groups. An API key identifies a principal; the principal's groups
are what row-level security filters on."""

import hashlib
import json
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class Principal(BaseModel):
    name: str
    display_name: str
    groups: list[str] = Field(min_length=1)


def hash_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()


class PrincipalRegistry:
    """Resolves API keys to principals. Only SHA-256 hashes of keys are held, so a leaked key
    file can't be replayed; keys are random 256-bit tokens, so an unsalted hash is enough."""

    def __init__(
        self,
        principals: dict[str, Principal],
        key_hashes: dict[str, str],
        api_keys_path: Path | None = None,
    ) -> None:
        self.principals = principals
        self._by_hash = self._checked(key_hashes)
        # With a path, the key file is watched: keys issued or revoked while the API runs
        # take effect on the next request (one stat() per request), no restart needed.
        self._path = api_keys_path
        self._mtime = _mtime(api_keys_path) if api_keys_path else None

    @classmethod
    def load(cls, principals_path: Path, api_keys_path: Path) -> "PrincipalRegistry":
        raw = yaml.safe_load(principals_path.read_text(encoding="utf-8"))
        principals = {
            name: Principal(name=name, **spec) for name, spec in raw["principals"].items()
        }
        return cls(principals, load_key_hashes(api_keys_path), api_keys_path)

    def authenticate(self, api_key: str) -> Principal | None:
        self._reload_if_changed()
        name = self._by_hash.get(hash_key(api_key))
        return self.principals[name] if name else None

    def _reload_if_changed(self) -> None:
        if self._path is None:
            return
        mtime = _mtime(self._path)
        if mtime != self._mtime:
            self._by_hash = self._checked(load_key_hashes(self._path))
            self._mtime = mtime

    def _checked(self, key_hashes: dict[str, str]) -> dict[str, str]:
        unknown = set(key_hashes.values()) - self.principals.keys()
        if unknown:
            raise ValueError(f"API keys issued for unknown principals: {sorted(unknown)}")
        return key_hashes


def _mtime(path: Path) -> int | None:
    try:
        return path.stat().st_mtime_ns
    except FileNotFoundError:
        return None


def load_key_hashes(path: Path) -> dict[str, str]:
    """{sha256: principal name}; an absent file means no keys have been issued yet."""
    if not path.exists():
        return {}
    data: dict[str, str] = json.loads(path.read_text(encoding="utf-8"))
    return data
