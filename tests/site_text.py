"""Rendered text of the website per reading level, and the numeric claims in it.

Shared by the website tests. A page is parsed as the browser would render it at one level: blocks marked
``data-lv`` for other levels are dropped (as ``docs/assets/style.css`` hides them), and so are scripts, styles,
code and the document head. Text is grouped into units (a paragraph, list item, heading, caption, table row or
SVG label) so that each number can be checked against the sentence it appears in.
"""

import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LEVELS = {"beginner": "b", "amateur": "a", "expert": "e"}
UNITS = {"p", "li", "h1", "h2", "h3", "h4", "figcaption", "dt", "dd", "caption", "tr", "summary", "text", "blockquote"}
SKIP = {"script", "style", "code", "pre", "head", "title", "desc"}
SPACED = {"td", "th", "div", "dt", "dd", "span", "li", "p", "br"}
# Labels, not claims: episode identifiers (checked against the cell ids by test_site_data) and the paper's
# figure, table and section numbers are matched as references instead.
IDENTIFIER = re.compile(r"\b(?:cells?|episodes?|tasks?|events?)\s+\d+(?:\s+and\s+\d+)?\b", re.I)
VOID = {"meta", "link", "br", "img", "input", "hr", "source", "wbr", "circle", "rect", "path", "line", "polyline"}

PAIR_WORDS = {"two": 2, "three": 3}
WORDS = {"four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
         "eleven": 11, "twelve": 12, "twenty": 20}
_NUM = r"\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?|\.\d+"
_WORD = "|".join(WORDS)
_PAIR_WORD = "|".join([*PAIR_WORDS, *WORDS])
_EDGE_L = r"(?<![\w.\-/])"
_EDGE_R = r"(?![\w/]|\.\d)"
STAMP = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?Z|\b\d{2}:\d{2}:\d{2}Z")
PAIR = re.compile(rf"{_EDGE_L}({_NUM}|{_PAIR_WORD}|all)\s*(?:/|\bof\s+(?:the\s+)?)({_NUM}|{_PAIR_WORD}){_EDGE_R}", re.I)
SINGLE = re.compile(rf"{_EDGE_L}({_NUM})(%?){_EDGE_R}|\b({_WORD})\b", re.I)


def norm(value: str) -> str:
    value = value.lower().replace(",", "")
    if value in WORDS or value in PAIR_WORDS:
        return str({**PAIR_WORDS, **WORDS}[value])
    return value.lstrip("0") if re.fullmatch(r"0\d+", value) else value


def claims(text: str) -> list[str]:
    """Numeric claims in one unit of text: timestamps, pairs ("8 of 8", "17/20", "all 20" stays single) and the rest."""
    found = [match.group(0) for match in STAMP.finditer(text)]
    text = IDENTIFIER.sub(" ", STAMP.sub(" ", text))
    for match in PAIR.finditer(text):
        if match.group(1).lower() != "all":
            found.append(f"{norm(match.group(1))}/{norm(match.group(2))}")
    text = PAIR.sub(lambda m: f" {m.group(2)} " if m.group(1).lower() == "all" else " ", text)
    for match in SINGLE.finditer(text):
        found.append(norm(match.group(1)) + match.group(2) if match.group(1) else norm(match.group(3)))
    return found


class _Page(HTMLParser):
    def __init__(self, level: str):
        super().__init__(convert_charrefs=True)
        self.code = LEVELS[level]
        self.stack: list[tuple[str, bool, bool]] = []  # (tag, hidden, opens a unit)
        self.units: list[list[str]] = []
        self.open: list[int] = []

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        attrs = dict(attrs)
        hidden = bool(self.stack and self.stack[-1][1]) or tag in SKIP or attrs.get("aria-hidden") == "true"
        if "data-lv" in attrs and self.code not in attrs["data-lv"].split():
            hidden = True
        if "tick" in (attrs.get("class") or "").split() or attrs.get("data-source") in ("figure-data", "episodes"):
            hidden = True  # axis labels; event numbers, checked against the figure or episode data
        if tag in SPACED and self.open and not hidden:
            self.units[self.open[-1]].append(" ")
        classes = set((attrs.get("class") or "").split())
        unit = (tag in UNITS or bool({"tile", "result-row", "sequence-result"} & classes)) and not hidden
        if unit:
            self.units.append([])
            self.open.append(len(self.units) - 1)
        self.stack.append((tag, hidden, unit))

    def handle_startendtag(self, tag, attrs):
        pass  # self-closing SVG shapes hold no text

    def handle_endtag(self, tag):
        if tag not in (name for name, _, _ in self.stack):
            return
        while self.stack:
            name, _, unit = self.stack.pop()
            if unit:
                self.open.pop()
            if name == tag:
                break

    def handle_data(self, data):
        if self.stack and self.stack[-1][1]:
            return
        if self.open:
            self.units[self.open[-1]].append(data)


def units(html: str, level: str) -> list[str]:
    parser = _Page(level)
    parser.feed(html)
    return [" ".join("".join(parts).split()) for parts in parser.units if "".join(parts).strip()]


def episode_texts(level: str, data: dict | None = None) -> list[str]:
    """The prose the explorer shows at one level: stories, notes, guides, verdicts, instruction notes, pairs."""
    data = data or json.loads((DOCS / "data" / "episodes.json").read_text(encoding="utf-8"))
    code = LEVELS[level]
    texts = []
    for episode in data["episodes"]:
        texts += [episode["title"], episode["story"][code], episode["verdict"][code], episode["instructions"][code]]
        for step in episode["steps"]:
            if code == "b":
                texts += [step["guide"]["says"], step["guide"]["notice"] or ""]
            elif step["note"]:
                texts.append(step["note"])
    for pair in data["compare"]:
        texts += [pair["title"], pair["question"][code], pair["answer"][code]]
    return [text for text in texts if text]


def script_strings(path: Path) -> list[str]:
    """String and template literals in a script, the text it can put on the page."""
    source = path.read_text(encoding="utf-8")
    source = re.sub(r"^\s*//.*$", "", source, flags=re.M)
    literals = [match.group(2) for match in re.finditer(r"([\"'`])((?:\\.|(?!\1).)*)\1", source)]
    return [re.sub(r"\$\{[^}]*\}", " ", literal) for literal in literals]
