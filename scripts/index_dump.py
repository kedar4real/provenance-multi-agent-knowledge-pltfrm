"""Export and restore the search index (documents, sections, chunks, embeddings, facts).

    uv run python scripts/index_dump.py export data/index.dump
    uv run python scripts/index_dump.py restore data/index.dump [--db NAME]

CI can't re-ingest from EDGAR (rate limits, 10 minutes of embedding), so the retrieval gate
restores this dump into a freshly migrated database instead. It holds only what's public or
synthetic: SEC filings, XBRL facts and the demo's internal notes. Never `app_secrets` (the
signing key comes from the environment) or `audit_log`. Uses pg_dump and pg_restore inside
the compose `postgres` container, so no client tools are needed on the host.
"""

import argparse
import subprocess
import sys
from pathlib import Path

TABLES = ["companies", "documents", "sections", "chunks", "financial_facts"]
SEQUENCED = ["documents", "sections", "chunks", "financial_facts"]  # identity columns
USER = "provenance_owner"
PSQL = ["docker", "compose", "exec", "-T", "postgres"]


def export(path: Path, db: str) -> None:
    table_args = [arg for t in TABLES for arg in ("-t", t)]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as out:
        subprocess.run(
            [*PSQL, "pg_dump", "-U", USER, "-d", db, "--data-only", "-Z", "6", "-Fc", *table_args],
            stdout=out, check=True,
        )  # fmt: skip
    print(f"exported {', '.join(TABLES)} -> {path} ({path.stat().st_size // 1024} KB)")


def restore(path: Path, db: str) -> None:
    """Into a migrated, empty database; fails loudly if the tables already hold rows."""
    count = subprocess.run(
        [*PSQL, "psql", "-U", USER, "-d", db, "-tA", "-c", "SELECT count(*) FROM companies"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()  # fmt: skip
    if count != "0":
        raise SystemExit(f"refusing to restore: companies already has {count} rows")
    with path.open("rb") as dump:
        subprocess.run(
            [*PSQL, "pg_restore", "-U", USER, "-d", db, "--data-only", "--no-owner", "-1"],
            stdin=dump, check=True,
        )  # fmt: skip
    # Restored ids came from the dump; make new inserts continue after them.
    resets = "; ".join(
        f"SELECT setval(pg_get_serial_sequence('{t}', 'id'), (SELECT coalesce(max(id), 1) FROM {t}))"
        for t in SEQUENCED
    )
    subprocess.run(
        [*PSQL, "psql", "-U", USER, "-d", db, "-v", "ON_ERROR_STOP=1", "-c", resets], check=True
    )
    counts = subprocess.run(
        [*PSQL, "psql", "-U", USER, "-d", db, "-tA", "-F", " ", "-c",
         " UNION ALL ".join(f"SELECT '{t}', count(*) FROM {t}" for t in TABLES)],
        capture_output=True, text=True, check=True,
    ).stdout  # fmt: skip
    print("restored:", ", ".join(f"{a}={b}" for a, b in (r.split() for r in counts.splitlines())))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["export", "restore"])
    parser.add_argument("path", type=Path)
    parser.add_argument("--db", default="provenance", help="database name (default: provenance)")
    args = parser.parse_args()
    {"export": export, "restore": restore}[args.action](args.path, args.db)
    sys.exit(0)
