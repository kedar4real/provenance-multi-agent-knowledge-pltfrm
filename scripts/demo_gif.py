"""Record the README demo: docs/media/demo.gif.

    cd web && npm run dev -- --port 5174     # with the API running on :8000
    uv run --with playwright python scripts/demo_gif.py     # needs ffmpeg on PATH

An analyst who can see Nvidia asks a question and gets a cited answer, opens a source, then
switches to a healthcare analyst who can't see it and asks the same. Temporary API keys for
ivan_internal and hana_health (they must have none) are minted, never printed, and revoked.
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
QUESTION = "How does Nvidia describe its dependence on TSMC?"
PEOPLE = {
    "ivan_internal": ("Ivan (internal)", ["research_all", "internal_restricted"]),
    "hana_health": ("Hana (healthcare analyst)", ["analyst_healthcare"]),
}
MAX_FRAME_S = 1.0
PALETTE = (
    "split[a][b];[a]palettegen=max_colors=96:stats_mode=diff[p];"
    "[b][p]paletteuse=dither=bayer:bayer_scale=4"
)
log: list[tuple[float, str]] = []
t0 = time.monotonic()


def snap(page: Page) -> None:
    name = f"f{len(log):05d}.png"
    page.screenshot(path=str(FRAMES / name))
    log.append((time.monotonic() - t0, name))


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


def type_question(page: Page) -> None:
    page.get_by_role("textbox").click()
    for i, ch in enumerate(QUESTION):
        page.keyboard.type(ch)
        if i % 3 == 0:
            snap(page)
        page.wait_for_timeout(40)
    snap(page)


def ask(page: Page) -> None:
    type_question(page)
    pause(page, 600)
    page.get_by_role("button", name="Ask", exact=True).click()
    pause(page, 1000)
    spinner = page.locator("section[aria-label='Agent steps'] .animate-spin")
    deadline = time.monotonic() + 420
    while spinner.count() and time.monotonic() < deadline:
        snap(page)
        page.wait_for_timeout(250)
    pause(page, 1500)


def stitch() -> None:
    lines = []
    for i, (t, name) in enumerate(log):
        following = log[i + 1][0] if i + 1 < len(log) else t + 2.5
        lines.append(f"file '{(FRAMES / name).as_posix()}'")
        lines.append(f"duration {min(following - t, MAX_FRAME_S):.3f}")
    lines.append(f"file '{(FRAMES / log[-1][1]).as_posix()}'")
    listing = FRAMES / "frames.txt"
    listing.write_text("\n".join(lines), encoding="utf-8")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
         "-vf", f"fps=6,scale=880:-1:flags=lanczos,{PALETTE}", str(OUT)],
        check=True,
    )  # fmt: skip
    print(f"{len(log)} frames over {log[-1][0]:.0f} s -> {OUT} ({OUT.stat().st_size // 1024} KB)")


def record(minted: dict[str, str]) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        ctx = browser.new_context(viewport={"width": 1100, "height": 760}, color_scheme="light")
        page = ctx.new_page()
        seed(page, minted)
        page.goto(BASE)
        page.wait_for_load_state("networkidle")
        pause(page, 1800)

        ask(page)  # a cited answer, with its steps streaming in
        page.mouse.wheel(0, 360)
        pause(page, 1500)
        cite = page.locator("article button[aria-label^='Source P']").first
        if cite.count():  # the cited passage, highlighted in the filing
            cite.click()
            page.locator("mark.evidence").wait_for(timeout=20_000)
            pause(page, 3500)
            page.keyboard.press("Escape")
            pause(page, 700)

        page.mouse.wheel(0, -2000)
        pause(page, 600)
        page.locator("button", has_text="Ivan").first.click()  # switch who is asking
        pause(page, 1400)
        page.get_by_role("menuitemradio", name="Hana", exact=False).click()
        pause(page, 1400)
        ask(page)  # the same question, from someone who can't see the filing
        pause(page, 2500)
        ctx.close()
        browser.close()


if __name__ == "__main__":
    minted = {n: keys("issue", n) for n in PEOPLE}
    try:
        record(minted)
        stitch()
    finally:
        shutil.rmtree(FRAMES, ignore_errors=True)
        for n in PEOPLE:
            keys("revoke", n)
        print("temporary keys revoked")
