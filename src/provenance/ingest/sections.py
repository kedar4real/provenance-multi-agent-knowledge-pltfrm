"""Turns 10-K HTML into plain text and extracts the narrative Items used for retrieval."""

import re

from pydantic import BaseModel
from selectolax.parser import HTMLParser

TARGET_ITEMS = ("1", "1A", "7")

_BLOCK_END = re.compile(r"(?i)<br\s*/?>|</(?:p|div|tr|li|h[1-6]|table|section)>")
_CELL_END = re.compile(r"(?i)</t[dh]>")
_PAGE_FOOTER = re.compile(r"^.{0,120}\|\s*\d{4}\s+Form\s+10-K\s*\|\s*\d+$", re.IGNORECASE)
_PAGE_NUMBER = re.compile(r"^\d{1,3}$")
_HEADING = re.compile(
    r"^[ \t]*item[ \t]+(?P<num>\d{1,2}[a-c]?)\b[ \t]*[.:\-\u2013\u2014]?[ \t]*(?P<rest>[^\n]*)",
    re.IGNORECASE | re.MULTILINE,
)
_MAX_TITLE_CHARS = 150
_MIN_SECTION_CHARS = 1000
_RUNNING_HEADER = re.compile(r"^(?:part\s+(?:i|ii|iii|iv)|item\s+\d{1,2}[a-c]?\.?)$", re.IGNORECASE)
_STANDALONE_LINE = re.compile(r"^[^\n]{1,150}$", re.MULTILINE)
_MDNA_END = re.compile(
    r"^(?:management's report on internal control|report of independent registered public"
    r" accounting firm|consolidated (?:statements? of [a-z ,'()]+|balance sheets?)$|quantitative and"
    r" qualitative disclosures about market risk|item\s+7a|item\s+8)"
)

# SEC-mandated Item titles. A line like "Item 1" whose title doesn't match is a running
# page header, not a section boundary.
_CANONICAL_TITLES: dict[str, tuple[str, ...]] = {
    "1": ("business",),
    "1A": ("risk factors",),
    "1B": ("unresolved staff comments",),
    "1C": ("cybersecurity",),
    "2": ("properties",),
    "3": ("legal proceedings",),
    "4": ("mine safety",),
    "5": ("market for",),
    "6": ("[reserved]", "reserved", "selected financial data"),
    "7": ("management's discussion",),
    "7A": ("quantitative and qualitative",),
    "8": ("financial statements",),
    "9": ("changes in and disagreements",),
    "9A": ("controls and procedures",),
    "9B": ("other information",),
    "9C": ("disclosure regarding foreign",),
    "10": ("directors",),
    "11": ("executive compensation",),
    "12": ("security ownership",),
    "13": ("certain relationships",),
    "14": ("principal account",),
    "15": ("exhibit",),
    "16": ("form 10-k summary",),
}


class Section(BaseModel):
    item: str
    title: str
    text: str
    char_start: int
    char_end: int


def html_to_text(html: str) -> str:
    """Block elements become line breaks; inline markup is joined without breaking words."""
    html = _CELL_END.sub(" ", _BLOCK_END.sub("\n", html))
    tree = HTMLParser(html)
    for node in tree.css("script, style, ix\\:header"):
        node.decompose()
    root = tree.body or tree.root
    raw = root.text(separator="") if root is not None else ""
    lines = []
    for line in raw.replace("\xa0", " ").splitlines():
        line = re.sub(r"[ \t]+", " ", line).strip()
        if not line or _PAGE_FOOTER.match(line) or _PAGE_NUMBER.match(line):
            continue
        lines.append(line)
    return "\n".join(lines)


def extract_items(text: str) -> dict[str, Section]:
    """For each target Item, the heading occurrence followed by the most text.

    10-Ks repeat every heading in the table of contents; those copies are followed by only a
    few characters before the next heading, so the longest span is the real section.
    """
    headings = [h for m in _HEADING.finditer(text) if (h := _parse_heading(m, text)) is not None]
    sections: dict[str, Section] = {}
    for i, (num, title, _start, body_start) in enumerate(headings):
        if num not in TARGET_ITEMS:
            continue
        end = headings[i + 1][2] if i + 1 < len(headings) else len(text)
        body = text[body_start:end]
        stripped_start = body_start + (len(body) - len(body.lstrip()))
        stripped_end = end - (len(body) - len(body.rstrip()))
        if stripped_end <= stripped_start:
            continue
        current = sections.get(num)
        if current is None or stripped_end - stripped_start > current.char_end - current.char_start:
            sections[num] = _section(num, title, text, stripped_start, stripped_end)
    mdna = sections.get("7")
    if mdna is None or len(mdna.text) < _MIN_SECTION_CHARS:
        fallback = _standalone_mdna(text)
        if fallback is not None and (mdna is None or len(fallback.text) > len(mdna.text)):
            sections["7"] = fallback
    return sections


def _section(item: str, title: str, text: str, start: int, end: int) -> Section:
    body = "\n".join(
        line for line in text[start:end].splitlines() if not _RUNNING_HEADER.match(line.strip())
    )
    return Section(item=item, title=title, text=body, char_start=start, char_end=end)


def _standalone_mdna(text: str) -> Section | None:
    """MD&A that Item 7 only points to ("Reference is made to the section entitled ...").

    Found as a line that is just the MD&A heading; it runs to the first line that starts the
    financial statements. The longest such span wins, which skips table-of-contents lines.
    """
    best: Section | None = None
    for line in _STANDALONE_LINE.finditer(text):
        if not _normalize(line.group()).startswith("management's discussion and analysis"):
            continue
        start = line.end() + 1
        end = len(text)
        for later in _STANDALONE_LINE.finditer(text, start):
            if _MDNA_END.match(_normalize(later.group())):
                end = later.start()
                break
        body = text[start:end].strip()
        if body and (best is None or len(body) > len(best.text)):
            offset = text.index(body, start)
            best = _section("7", line.group().strip(), text, offset, offset + len(body))
    return best


def _normalize(title: str) -> str:
    return title.lower().replace("\u2019", "'").strip(" .:-\u2013\u2014")


def _parse_heading(match: re.Match[str], text: str) -> tuple[str, str, int, int] | None:
    num = match.group("num").upper()
    title = match.group("rest").strip()
    body_start = match.end()
    if not title:
        next_line_end = text.find("\n", body_start + 1)
        next_line_end = len(text) if next_line_end == -1 else next_line_end
        title = text[body_start:next_line_end].strip()
        body_start = next_line_end
    if len(title) > _MAX_TITLE_CHARS:
        return None
    normalized = _normalize(title)
    if not any(normalized.startswith(p) for p in _CANONICAL_TITLES.get(num, ())):
        return None
    return num, title.rstrip("."), match.start(), body_start
