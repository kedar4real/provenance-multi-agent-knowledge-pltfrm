"""Record the README demo: docs/media/demo.gif.

    uv run python -m provenance.api --port 8001                 # the API (any port)
    cd web && PROVENANCE_API=http://127.0.0.1:8001 npx vite --port 5174
    uv run --with playwright python scripts/demo_gif.py         # needs ffmpeg on PATH

Ivan (internal research) asks a question: the steps and the answer's text stream in, the
verified answer gets its stamp and a chart of the data it cites, a sentence is opened to
show its evidence, and a citation opens the filing with the passage highlighted. Then
Compare asks the same question as Hana, a healthcare analyst who can't see Nvidia, and the
dashboard closes the tour.

Temporary API keys for ivan_internal and hana_health are minted, never printed, and revoked;
the script refuses to run if either already has a key (issuing would replace it).
Screenshots are captured as the page runs (no Playwright video download) and stitched with
ffmpeg; idle waits are capped at one second per frame, so the GIF is shorter than the run.
"""

import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

REPO = Path(__file__).resolve().parents[1]
FRAMES = Path(tempfile.mkdtemp(prefix="provenance-demo-"))
OUT = REPO / "docs" / "media" / "demo.gif"
BASE = "http://localhost:5174"
QUESTION = "How did Nvidia's revenue change from fiscal 2025 to fiscal 2026, and what drove it?"
PEOPLE = {
    "ivan_internal": ("Ivan (internal)", ["research_all", "internal_restricted", "auditor"]),
    "hana_health": ("Hana (healthcare analyst)", ["analyst_healthcare"]),
}
MAX_FRAME_S = 1.0
# While the agent works, frames are taken less often and played fast: the steps arrive in
# fast-forward instead of in real time.
WAIT_FRAME_S = 0.18
PALETTE = (
    "split[a][b];[a]palettegen=max_colors=192:stats_mode=full[p];"
    "[b][p]paletteuse=dither=bayer:bayer_scale=4"
)
log: list[tuple[float, str, float]] = []  # (taken at, file, longest it may show)
t0 = time.monotonic()


def snap(page: Page, cap: float = MAX_FRAME_S) -> None:
    name = f"f{len(log):05d}.png"
    page.screenshot(path=str(FRAMES / name))
    log.append((time.monotonic() - t0, name, cap))


def pause(page: Page, ms: int, every: int = 200) -> None:
    end = time.monotonic() + ms / 1000
    while time.monotonic() < end:
        snap(page)
        page.wait_for_timeout(every)


def keys(action: str, name: str) -> str:
    out = subprocess.run(
        ["uv", "run", "python", "-m", "provenance.api.keys", action, name],
        cwd=REPO, capture_output=True, text=True, check=True,
    ).stdout  # fmt: skip
    return out.strip().splitlines()[-1]


def assert_keyless(names: list[str]) -> None:
    """Issuing replaces a principal's key, so never mint over one the owner uses."""
    listing = _list()
    taken = [n for n in names if any(r.split()[:1] == [n] and "key issued" in r for r in listing)]
    if taken:
        raise SystemExit(f"{', '.join(taken)} already have keys; revoke them or pick others")


def _list() -> list[str]:
    return subprocess.run(
        ["uv", "run", "python", "-m", "provenance.api.keys", "list"],
        cwd=REPO, capture_output=True, text=True, check=True,
    ).stdout.splitlines()  # fmt: skip


def seed(page: Page, minted: dict[str, str]) -> None:
    state = {
        "identities": [
            {"key": minted[n], "name": n, "displayName": PEOPLE[n][0], "groups": PEOPLE[n][1]}
            for n in PEOPLE
        ],
        "activeName": "ivan_internal",
    }
    page.add_init_script(
        f"localStorage.setItem('provenance.identities.v1', {json.dumps(json.dumps(state))})"
    )


def type_into(page: Page, selector: str, text: str) -> None:
    page.locator(selector).click()
    page.locator(selector).fill("")
    for i, ch in enumerate(text):
        page.keyboard.type(ch)
        if i % 3 == 0:
            snap(page)
        page.wait_for_timeout(35)
    snap(page)


def wait_for_run(page: Page, timeout_s: float = 420) -> None:
    running = page.locator("section[aria-label='Agent steps'] .animate-ping-soft")
    deadline = time.monotonic() + timeout_s
    while running.count() and time.monotonic() < deadline:
        snap(page, cap=WAIT_FRAME_S)
        page.wait_for_timeout(700)


def show(page: Page, locator: str, ms: int) -> None:
    target = page.locator(locator).first
    if target.count():
        target.scroll_into_view_if_needed()
        page.mouse.wheel(0, 120)
    pause(page, ms)


def record(minted: dict[str, str]) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        ctx = browser.new_context(viewport={"width": 1200, "height": 800}, color_scheme="light")
        page = ctx.new_page()
        seed(page, minted)
        page.goto(BASE)
        page.wait_for_load_state("networkidle")
        pause(page, 1500)

        # Ask: the steps and the draft stream in, then the verified, stamped answer.
        type_into(page, "#ask-question", QUESTION)
        pause(page, 500)
        page.get_by_role("button", name="Ask", exact=True).click()
        pause(page, 800)
        wait_for_run(page)
        pause(page, 800)
        show(page, "article header", 2200)
        show(page, "figure", 2500)  # the chart of the data the answer cites

        # A sentence opens its evidence, with the numbers matched in the data.
        sentence = page.locator("article [role='button'][aria-pressed]", has_text="$").first
        if sentence.count():
            sentence.scroll_into_view_if_needed()
            pause(page, 500)
            sentence.click()
            show(page, "section[aria-label='Evidence for the selected sentence']", 3000)

        # A passage citation opens the filing, the cited span highlighted.
        cite = page.locator("article button[aria-label^='Source P']").first
        if cite.count():
            cite.scroll_into_view_if_needed()
            pause(page, 400)
            cite.click()
            page.locator("mark.evidence").first.wait_for(timeout=20_000)
            pause(page, 3200)
            close = page.get_by_role("button", name="Close source").first
            if close.count():
                close.click()
            pause(page, 500)

        # Compare: the same question as someone who can't see Nvidia's filings.
        page.mouse.wheel(0, -5000)
        pause(page, 400)
        page.get_by_role("tab", name="Compare").click()
        pause(page, 900)
        page.locator("#compare-question").fill(QUESTION)
        pause(page, 700)
        page.get_by_role("button", name="Ask both").click()
        pause(page, 800)
        wait_for_run(page)
        pause(page, 800)
        # The two answers side by side: one traced, one "no answer from the evidence".
        page.locator(
            "section[aria-label^='Answer for'] > article, section[aria-label^='Answer for'] > div"
        ).first.scroll_into_view_if_needed()
        page.mouse.wheel(0, -140)
        pause(page, 4500)

        # The dashboard: what these questions cost and how they were routed.
        page.mouse.wheel(0, -5000)
        page.get_by_role("tab", name="Dashboard").click()
        page.locator("text=Cache hit rate").wait_for(timeout=15_000)
        pause(page, 3500)
        ctx.close()
        browser.close()


def stitch() -> None:
    lines = []
    for i, (t, name, cap) in enumerate(log):
        following = log[i + 1][0] if i + 1 < len(log) else t + 2.5
        lines.append(f"file '{(FRAMES / name).as_posix()}'")
        lines.append(f"duration {min(following - t, cap):.3f}")
    lines.append(f"file '{(FRAMES / log[-1][1]).as_posix()}'")
    listing = FRAMES / "frames.txt"
    listing.write_text("\n".join(lines), encoding="utf-8")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
         "-vf", f"fps=6,scale=900:-1:flags=lanczos,{PALETTE}", str(OUT)],
        check=True,
    )  # fmt: skip
    print(f"{len(log)} frames over {log[-1][0]:.0f} s -> {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    assert_keyless(list(PEOPLE))
    minted = {n: keys("issue", n) for n in PEOPLE}
    try:
        record(minted)
        stitch()
    finally:
        shutil.rmtree(FRAMES, ignore_errors=True)
        for n in PEOPLE:
            keys("revoke", n)
        print("temporary keys revoked")
