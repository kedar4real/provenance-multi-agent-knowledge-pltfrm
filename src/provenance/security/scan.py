"""Scan stored chunks for prompt injection and record the verdict on each row.

uv run python -m provenance.security.scan            # every chunk not scanned yet
uv run python -m provenance.security.scan --rescan   # all chunks (after changing the rules)

Resumable: it only picks up chunks whose verdict is NULL and commits per batch, so it can
be stopped and restarted. The ingest command runs it after storing new filings; until a
chunk is scanned, the agent guards it with the runtime heuristics only. Runs as the owner
role, since verdicts are written into chunks, which the app role can only read.
"""

import argparse
import sys
import time
from typing import Protocol

import psycopg

from provenance.config import Settings
from provenance.security.injection import InjectionVerdict

BATCH = 32


class Scanner(Protocol):
    def scan(self, texts: list[str]) -> list[InjectionVerdict]: ...


def scan_unscanned(
    conn: psycopg.Connection, scanner: Scanner, rescan: bool = False
) -> tuple[int, int]:
    """Returns (scanned, flagged)."""
    if rescan:
        conn.execute("UPDATE chunks SET injection_flagged = NULL")
        conn.commit()
    scanned = flagged = 0
    started = time.perf_counter()
    while True:
        rows = conn.execute(
            "SELECT id, text FROM chunks WHERE injection_flagged IS NULL ORDER BY id LIMIT %s",
            (BATCH,),
        ).fetchall()
        if not rows:
            return scanned, flagged
        verdicts = scanner.scan([text for _, text in rows])
        with conn.cursor() as cur:
            cur.executemany(
                "UPDATE chunks SET injection_flagged = %s, injection_reasons = %s,"
                " injection_score = %s WHERE id = %s",
                [
                    (v.flagged, v.heuristics or (["classifier"] if v.flagged else []),
                     v.classifier_score, chunk_id)
                    for (chunk_id, _), v in zip(rows, verdicts, strict=True)
                ],
            )  # fmt: skip
        conn.commit()
        scanned += len(rows)
        flagged += sum(v.flagged for v in verdicts)
        rate = scanned / max(time.perf_counter() - started, 1e-9)
        print(f"  scanned {scanned} ({rate:.1f}/s), flagged {flagged}", flush=True)


def main(rescan: bool) -> int:
    from provenance.security.injection import InjectionClassifier, InjectionScanner

    scanner = InjectionScanner(InjectionClassifier())
    with psycopg.connect(Settings().owner_dsn) as conn:
        scanned, flagged = scan_unscanned(conn, scanner, rescan)
    print(f"done: {scanned} chunks scanned, {flagged} flagged")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rescan", action="store_true")
    sys.exit(main(parser.parse_args().rescan))
