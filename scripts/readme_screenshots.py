"""Take the README screenshots: docs/media/*.png, from the real app.

    uv run python -m provenance.api --port 8001
    cd web && PROVENANCE_API=http://127.0.0.1:8001 npx vite --port 5174
    uv run --with playwright python scripts/readme_screenshots.py

Run after scripts/demo_gif.py, so Ivan's answer comes from the cache (one fewer model run).
Temporary keys for ivan_internal and hana_health are minted, never printed, and revoked; the
script refuses to run if either already has a key.
"""

import json
import subprocess
import time
from pathlib import Path

from playwright.sync_api import Locator, Page, sync_playwright

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "docs" / "media"
BASE = "http://localhost:5174"
QUESTION = "How did Nvidia's revenue change from fiscal 2025 to fiscal 2026, and what drove it?"
PEOPLE = {
    "ivan_internal": ("Ivan (internal)", ["research_all", "internal_restricted", "auditor"]),
    "hana_health": ("Hana (healthcare analyst)", ["analyst_healthcare"]),
}


def run(*args: str) -> str:
    return subprocess.run(
        ["uv", "run", "python", "-m", "provenance.api.keys", *args],
        cwd=REPO, capture_output=True, text=True, check=True,
    ).stdout  # fmt: skip


def seed(key: dict[str, str]) -> str:
    state = {
        "identities": [
            {"key": key[n], "name": n, "displayName": PEOPLE[n][0], "groups": PEOPLE[n][1]}
            for n in PEOPLE
        ],
        "activeName": "ivan_internal",
    }
    return f"localStorage.setItem('provenance.identities.v1', {json.dumps(json.dumps(state))})"


def wait_for_run(page: Page, timeout_s: float = 420) -> None:
    running = page.locator("section[aria-label='Agent steps'] .animate-ping-soft")
    deadline = time.monotonic() + timeout_s
    while running.count() and time.monotonic() < deadline:
        page.wait_for_timeout(500)
    page.wait_for_timeout(1800)  # let the reveal animations finish


def region(page: Page, top: Locator, bottom: Locator, name: str, pad: int = 24) -> None:
    """Screenshot from the top of one element to the bottom of another, full width.
    Element boxes are relative to the viewport; a full-page clip is in page coordinates."""
    page.add_style_tag(content="header.sticky { position: static !important; }")
    a, b = top.bounding_box(), bottom.bounding_box()
    assert a and b, name
    scroll = float(page.evaluate("window.scrollY"))
    width = page.viewport_size["width"] if page.viewport_size else 1280
    y = a["y"] + scroll - pad
    page.screenshot(
        path=str(OUT / name),
        full_page=True,
        clip={
            "x": 0,
            "y": max(y, 0),
            "width": width,
            "height": b["y"] + b["height"] - a["y"] + 2 * pad,
        },
    )
    print("saved", name, flush=True)


def ask(page: Page) -> None:
    page.locator("#ask-question").fill(QUESTION)
    page.get_by_role("button", name="Ask", exact=True).click()
    page.wait_for_timeout(800)
    wait_for_run(page)


def main(key: dict[str, str]) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        ctx = browser.new_context(viewport={"width": 1280, "height": 900}, device_scale_factor=1.25)
        ctx.add_init_script(seed(key))
        page = ctx.new_page()
        page.goto(BASE)
        page.wait_for_load_state("networkidle")

        ask(page)
        article = page.locator("article").first
        region(
            page,
            article.locator("header").first,
            page.locator("figure:visible").first,
            "answer.png",
        )

        sentence = page.locator("article [role='button'][aria-pressed]", has_text="$").first
        sentence.click()
        page.wait_for_timeout(900)
        inspector = page.locator("section[aria-label='Evidence for the selected sentence']")
        region(page, sentence, inspector, "claim.png")
        page.get_by_role("button", name="Close").first.click()

        page.get_by_role("tab", name="Compare").click()
        page.locator("#compare-question").fill(QUESTION)
        page.get_by_role("button", name="Ask both").click()
        page.wait_for_timeout(800)
        wait_for_run(page)
        sections = page.locator("section[aria-label^='Answer for']")
        region(
            page,
            page.locator("#compare-question"),
            sections.first.locator("article header").first,
            "compare.png",
            pad=60,
        )

        page.get_by_role("tab", name="Dashboard").click()
        page.locator("text=Cache hit rate").wait_for(timeout=15_000)
        page.wait_for_timeout(1500)
        region(
            page,
            page.get_by_role("heading", name="Dashboard"),
            page.locator("figure:visible").nth(3),
            "dashboard.png",
        )

        page.get_by_role("tab", name="Audit").click()
        page.locator("text=Tool calls per day").wait_for(timeout=15_000)
        page.wait_for_timeout(1500)
        region(
            page,
            page.get_by_role("heading", name="Audit log"),
            page.locator("figure:visible").nth(1),
            "audit.png",
        )
        ctx.close()

        ctx = browser.new_context(
            viewport={"width": 1280, "height": 900}, device_scale_factor=1.25, color_scheme="dark"
        )
        ctx.add_init_script(seed(key))
        page = ctx.new_page()
        page.goto(BASE)
        page.wait_for_load_state("networkidle")
        ask(page)
        region(
            page,
            page.locator("section[aria-label='Agent steps']"),
            page.locator("figure").first,
            "answer-dark.png",
        )
        ctx.close()
        browser.close()


if __name__ == "__main__":
    listing = run("list").splitlines()
    taken = [n for n in PEOPLE if any(r.split()[:1] == [n] and "key issued" in r for r in listing)]
    if taken:
        raise SystemExit(f"{', '.join(taken)} already have keys; revoke them or pick others")
    minted = {n: run("issue", n).strip().splitlines()[-1] for n in PEOPLE}
    try:
        main(minted)
    finally:
        for n in PEOPLE:
            run("revoke", n)
        print("temporary keys revoked")
