"""Issue or revoke local API keys. The key is printed once; only its hash is saved.

uv run python -m provenance.api.keys issue ana_tech
uv run python -m provenance.api.keys revoke ana_tech
uv run python -m provenance.api.keys list
"""

import argparse
import json
import secrets
import sys

from provenance.api.principals import PrincipalRegistry, hash_key, load_key_hashes
from provenance.config import Settings

KEY_PREFIX = "pk_"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="provenance.api.keys")
    parser.add_argument("action", choices=["issue", "revoke", "list"])
    parser.add_argument("principal", nargs="?")
    args = parser.parse_args(argv)

    settings = Settings()
    registry = PrincipalRegistry.load(settings.principals_path, settings.api_keys_path)
    hashes = load_key_hashes(settings.api_keys_path)

    if args.action == "list":
        issued = set(hashes.values())
        for name, p in registry.principals.items():
            mark = "key issued" if name in issued else "no key"
            print(f"{name:16} {mark:11} {','.join(p.groups)}")
        return 0

    if args.principal not in registry.principals:
        parser.error(f"unknown principal {args.principal!r}; see config/principals.yaml")
    # One key per principal: issuing replaces any previous key.
    hashes = {h: n for h, n in hashes.items() if n != args.principal}
    key = None
    if args.action == "issue":
        key = KEY_PREFIX + secrets.token_urlsafe(32)
        hashes[hash_key(key)] = args.principal
    settings.api_keys_path.write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")

    if key:
        print(f"API key for {args.principal} (shown once, store it somewhere safe):\n{key}")
    else:
        print(f"Revoked the key for {args.principal}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
