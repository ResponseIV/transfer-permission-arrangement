#!/usr/bin/env python3
"""Redraw the paper's Figure 1 for the website as theme-aware inline SVG, from the paper's own figure data.

Post hoc (2026-10-26), for ``docs/index.html``. The five series are the plotted values in
``paper/figures/figure-data.json``; the only annotations are the values the paper states at a 1% base rate.
The markup is written between the ``figure-1`` markers in the page, once wide and once for phones.
"""

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "paper" / "figures" / "figure-data.json"
PAGE = ROOT / "docs" / "index.html"
BEGIN, END = "<!-- figure-1:begin -->\n", "<!-- figure-1:end -->"
X_MIN, X_MAX = 0.001, 0.5
X_TICKS = [(0.001, "0.1%"), (0.01, "1%"), (0.1, "10%"), (0.5, "50%")]
Y_TICKS = [0, 0.25, 0.5, 0.75, 1]
# (view, negatives, bound) -> CSS class; the paper's colours are blue, green and red in this order.
SERIES = {("both", "all"): "s-log", ("both", "unprescribed"): "s-unpres", ("text", "all"): "s-pages"}
LEGEND = [("s-log", False, "Pages and log, all 206 nontransfers"),
          ("s-unpres", True, "Pages and log, the 194 with no prescribed exchange (bound)"),
          ("s-pages", False, "Pages alone, all 206")]
LAYOUTS = {
    "wide": {"w": 640, "h": 316, "left": 46, "right": 624, "top": 12, "bottom": 272, "font": 12},
    "narrow": {"w": 340, "h": 302, "left": 38, "right": 330, "top": 12, "bottom": 254, "font": 11},
}


def annotations(series: list[dict]) -> list[tuple[str, float]]:
    """The 1% values the paper states: both views' point and bound, the unprescribed bound, pages alone (point)."""
    wanted = [("both", "all", False), ("both", "all", True), ("both", "unprescribed", True), ("text", "all", False)]
    found = {(s["view"], s["negatives"], s["bound"]): s for s in series}
    return [(SERIES[key[:2]], found[key]["at_priors"]["0.01"]) for key in wanted]


def svg(series: list[dict], layout: str) -> str:
    g = LAYOUTS[layout]
    span = math.log10(X_MAX) - math.log10(X_MIN)

    def x(value: float) -> float:
        return g["left"] + (math.log10(value) - math.log10(X_MIN)) / span * (g["right"] - g["left"])

    def y(value: float) -> float:
        return g["bottom"] - value * (g["bottom"] - g["top"])

    font = g["font"]
    out = [f'<svg class="chart chart-{layout}" viewBox="0 0 {g["w"]} {g["h"]}" role="img" '
           f'aria-label="Line chart. At a 1% base rate, 19% of Astra\'s alarms with the log would be real '
           f'transfers (11% at the conservative bound); against episodes with no prescribed exchange the bound is '
           f'35%; on page writes alone, 5%. All curves rise towards 100% as the base rate rises to 50%.">']
    out.append('<g class="grid">')
    for tick in Y_TICKS:
        out.append(f'<line x1="{g["left"]}" x2="{g["right"]}" y1="{y(tick):.1f}" y2="{y(tick):.1f}"/>')
    out.append("</g>")
    for tick in Y_TICKS:
        out.append(f'<text class="tick" x="{g["left"] - 8}" y="{y(tick) + font * 0.35:.1f}" text-anchor="end" '
                   f'font-size="{font}">{round(tick * 100)}%</text>')
    for value, label in X_TICKS:
        anchor = "end" if value == X_MAX else "start" if value == X_MIN else "middle"
        out.append(f'<text class="tick" x="{x(value):.1f}" y="{g["bottom"] + font + 6}" text-anchor="{anchor}" '
                   f'font-size="{font}">{label}</text>')
    out.append(f'<text class="axis-title" x="{(g["left"] + g["right"]) / 2:.1f}" y="{g["h"] - 4}" '
               f'text-anchor="middle" font-size="{font}">Assumed transfer prevalence (log scale)</text>')
    marker = x(0.01)
    out.append(f'<line class="marker-line" x1="{marker:.1f}" x2="{marker:.1f}" y1="{g["top"]}" y2="{g["bottom"]}"/>')
    for s in series:
        css = SERIES[(s["view"], s["negatives"])]
        points = " ".join(f"{x(px):.1f},{y(py):.1f}" for px, py in s["points"])
        out.append(f'<polyline class="series {css}{" bound" if s["bound"] else ""}" points="{points}"/>')
    floor = math.inf  # labels are placed bottom-up, each a line plus a 4px gap above the previous
    for css, value in sorted(annotations(series), key=lambda item: item[1]):
        out.append(f'<circle class="dot {css}" cx="{marker:.1f}" cy="{y(value):.1f}" r="3.5"/>')
        floor = min(y(value) + font * 0.35, floor - font - 4)
        out.append(f'<text class="val" x="{marker - 8:.1f}" y="{floor:.1f}" text-anchor="end" '
                   f'font-size="{font}">{round(value * 100)}%</text>')
    out.append("</svg>")
    return "\n".join(out)


def legend() -> str:
    rows = []
    for css, bound, label in LEGEND:
        rows.append(f'<li><svg width="28" height="8" viewBox="0 0 28 8" aria-hidden="true">'
                    f'<line class="series {css}{" bound" if bound else ""}" x1="1" x2="27" y1="4" y2="4"/></svg>'
                    f"{label}</li>")
    rows.append('<li><svg width="28" height="8" viewBox="0 0 28 8" aria-hidden="true">'
                '<line class="series key" x1="1" x2="11" y1="4" y2="4"/>'
                '<line class="series key bound" x1="16" x2="27" y1="4" y2="4"/></svg>'
                "Solid: point rate; dashed: conservative bound</li>")
    return '<ul class="legend">\n' + "\n".join(rows) + "\n</ul>"


def figure(data: dict) -> str:
    series = data["figure1"]
    return "\n".join([legend(), svg(series, "wide"), svg(series, "narrow")]) + "\n"


def inject(page: str, markup: str) -> str:
    start = page.index(BEGIN) + len(BEGIN)
    return page[:start] + markup + page[page.index(END):]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--page", type=Path, default=PAGE)
    page = parser.parse_args().page
    data = json.loads(DATA.read_text(encoding="utf-8"))
    page.write_text(inject(page.read_text(encoding="utf-8"), figure(data)), encoding="utf-8")
    print(page)


if __name__ == "__main__":
    main()
