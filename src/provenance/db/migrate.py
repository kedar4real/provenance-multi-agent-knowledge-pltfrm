"""Applies db/migrations/*.sql in order, once each, and syncs the RLS signing key.

uv run python -m provenance.db.migrate
"""

from pathlib import Path

import psycopg

from provenance.config import Settings

MIGRATIONS_DIR = Path(__file__).parents[3] / "db" / "migrations"


def apply_migrations(owner_dsn: str, migrations_dir: Path, rls_signing_key: str) -> list[str]:
    """Returns the versions applied by this call. Each migration runs in its own transaction."""
    applied: list[str] = []
    with psycopg.connect(owner_dsn) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations"
            " (version text PRIMARY KEY, applied_at timestamptz NOT NULL DEFAULT now())"
        )
        conn.commit()
        done = {r[0] for r in conn.execute("SELECT version FROM schema_migrations").fetchall()}
        for path in sorted(migrations_dir.glob("*.sql")):
            if path.stem in done:
                continue
            with conn.transaction():
                conn.execute(path.read_text(encoding="utf-8"))
                conn.execute("INSERT INTO schema_migrations (version) VALUES (%s)", (path.stem,))
            applied.append(path.stem)
        conn.execute(
            "INSERT INTO app_secrets (name, value) VALUES ('rls_signing_key', %s)"
            " ON CONFLICT (name) DO UPDATE SET value = EXCLUDED.value",
            (rls_signing_key,),
        )
        conn.commit()
    return applied


if __name__ == "__main__":
    settings = Settings()
    versions = apply_migrations(
        settings.owner_dsn, MIGRATIONS_DIR, settings.rls_signing_key.get_secret_value()
    )
    print(f"applied: {', '.join(versions) or 'nothing (up to date)'}")
