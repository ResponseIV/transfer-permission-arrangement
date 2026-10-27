"""The website: figures drawn from the paper's data, colour contrast, links and self-containment."""

import json
import re
import subprocess
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
sys.path.insert(0, str(ROOT / "scripts"))
import site_figures  # noqa: E402

PAGES = [DOCS / "index.html", DOCS / "explorer.html"]
REPO = "https://github.com/ResponseIV/transfer-permission-arrangement"

# Text and graphics colour pairs in use, as (foreground, background, minimum ratio).
CONTRAST = [(fg, bg, 4.5) for fg, bg in [
    ("ink", "paper"), ("ink", "sheet"), ("ink", "sheet-2"), ("ink-2", "paper"), ("ink-2", "sheet"),
    ("ink-2", "sheet-2"), ("ink-3", "paper"), ("ink-3", "sheet"), ("accent", "paper"), ("accent", "sheet"),
    ("alpha", "paper"), ("alpha", "sheet"), ("beta", "paper"), ("beta", "sheet"), ("fixture", "sheet"),
    ("yes", "yes-soft"), ("no", "no-soft"), ("ink-2", "yes-soft"), ("ink-2", "no-soft"), ("ink", "no-soft"),
    ("ink", "accent-soft"), ("accent", "accent-soft"), ("ink", "mark"), ("paper", "ink"), ("no", "paper"),
    ("no", "sheet"), ("paper", "alpha"), ("paper", "beta"), ("ink-2", "accent-soft"),
    ("ink-2", "mark"), ("sheet", "accent"), ("ink-2", "sheet-2"),
    ("ink-3", "sheet-2"), ("alpha", "sheet-2"), ("beta", "sheet-2"),
]] + [(fg, "sheet", 3.0) for fg in ("fig-log", "fig-unpres", "fig-pages", "control", "ink-3")] + [("control", "paper", 3.0)]


def tokens(css: str) -> dict[str, dict[str, str]]:
    def block(selector: str) -> dict[str, str]:
        body = css[css.index(selector):]
        body = body[body.index("{") + 1:body.index("}")]
        return dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})", body))

    light = block(":root {")
    return {"light": light, "dark": {**light, **block(':root[data-theme="dark"] {')},
            "dark-auto": {**light, **block(':root:not([data-theme="light"]) {')}}


def luminance(hex_colour: str) -> float:
    channels = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def ratio(a: str, b: str) -> float:
    high, low = sorted([luminance(a), luminance(b)], reverse=True)
    return (high + 0.05) / (low + 0.05)


class _Refs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs: list[tuple[str, str, dict]] = []
        self.ids: list[str] = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        for key in ("href", "src", "content"):
            if attrs.get(key):
                self.refs.append((tag, attrs[key], attrs))


def refs(page: Path) -> list[tuple[str, str, dict]]:
    parser = _Refs()
    parser.feed(page.read_text(encoding="utf-8"))
    return parser.refs


class Figures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(site_figures.DATA.read_text(encoding="utf-8"))
        cls.page = (DOCS / "index.html").read_text(encoding="utf-8")

    def test_figure_1_is_regenerated_from_the_paper_data(self):
        self.assertEqual(site_figures.inject(self.page, site_figures.figure(self.data)), self.page)

    def test_figure_1_annotates_only_the_values_the_paper_states_at_one_percent(self):
        values = [round(value * 100) for _, value in site_figures.annotations(self.data["figure1"])]
        self.assertEqual(values, [19, 11, 35, 5])
        paper = " ".join((ROOT / "paper" / "report.md").read_text(encoding="utf-8").split())
        self.assertIn("19% of Astra's alarms with the log would be real (at least 11% at the interval bounds)", paper)
        self.assertIn("the point estimate is 100% and the bound 35%. On page writes alone, 5%.", paper)

    def test_figure_1_draws_all_five_series_on_both_layouts(self):
        for layout in ("wide", "narrow"):
            svg = site_figures.svg(self.data["figure1"], layout)
            self.assertEqual(svg.count("<polyline"), len(self.data["figure1"]))

    def test_figure_2_lists_the_paper_events(self):
        traces = re.findall(r'<ol>(.*?)</ol>', self.page[self.page.index('id="figure-2"'):], re.S)[:2]
        for trace, key in zip(traces, ("1", "2")):
            shown = re.findall(r'<span class="seq"[^>]*>([^<]+)</span><span>([^<]+)</span>', trace)
            expected = [(str(seq), label) for seq, label in self.data["figure2"][key]["selected_events"]]
            self.assertEqual(shown, expected)


class Contrast(unittest.TestCase):
    def test_text_and_graphics_meet_wcag_aa_in_both_themes(self):
        themes = tokens((DOCS / "assets" / "tokens.css").read_text(encoding="utf-8"))
        self.assertEqual(themes["dark"], themes["dark-auto"], "the two dark blocks must match")
        failures = []
        for theme, colours in themes.items():
            for fg, bg, minimum in CONTRAST:
                value = ratio(colours[fg], colours[bg])
                if value < minimum:
                    failures.append(f"{theme}: --{fg} on --{bg} = {value:.2f} < {minimum}")
        self.assertEqual(failures, [])


class Links(unittest.TestCase):
    def test_article_fragments_resolve_and_page_ids_are_unique(self):
        for page in PAGES:
            parser = _Refs()
            parser.feed(page.read_text(encoding="utf-8"))
            self.assertEqual(len(parser.ids), len(set(parser.ids)), page.name)
            for tag, value, _ in parser.refs:
                if tag == "a" and value.startswith("#") and "/" not in value:
                    self.assertIn(value[1:], parser.ids, f"{page.name}: {value}")

    def test_direct_pdf_is_the_submitted_paper(self):
        self.assertEqual((DOCS / "assets" / "report.pdf").read_bytes(), (ROOT / "paper" / "report.pdf").read_bytes())
        result = subprocess.run(["git", "show", "submission:paper/report.pdf"], cwd=ROOT, capture_output=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual((DOCS / "assets" / "report.pdf").read_bytes(), result.stdout)

    def test_no_runtime_fetch_leaves_the_site(self):
        for page in PAGES:
            for tag, value, attrs in refs(page):
                loads = tag in ("script", "img", "source") or (tag == "link" and attrs.get("rel") != "canonical")
                if loads:
                    self.assertFalse(re.match(r"https?:|//", value), f"{page.name}: {tag} loads {value}")
        css = (DOCS / "assets" / "style.css").read_text(encoding="utf-8")
        self.assertEqual(re.findall(r"url\((?!\"?fonts/)", css), [])
        for script in (DOCS / "assets").glob("*.js"):
            self.assertNotRegex(script.read_text(encoding="utf-8"), r"fetch\(\s*[\"'`]https?:")

    def test_relative_links_resolve_inside_docs(self):
        for page in PAGES:
            for tag, value, attrs in refs(page):
                if tag == "meta" or re.match(r"https?:|mailto:|#", value) or value.startswith("data:"):
                    continue
                path = value.split("#")[0].split("?")[0] or page.name
                self.assertTrue((page.parent / path).resolve().is_file() or (page.parent / path / "index.html").is_file(),
                                f"{page.name}: {value}")

    @unittest.skipUnless((ROOT / ".git").exists(), "not a git checkout")
    def test_github_links_point_at_files_on_their_ref(self):
        sources = PAGES + list((DOCS / "assets").glob("*.js")) + [DOCS / "data" / "episodes.json"]
        links = set()
        for source in sources:
            links |= set(re.findall(re.escape(REPO) + r"/(?:blob|tree)/([\w.-]+)/([^\s\"'<>)`]+)",
                                    source.read_text(encoding="utf-8")))
        self.assertTrue(links)
        for ref in ("submission", "site"):
            self.assertEqual(subprocess.run(["git", "rev-parse", "--verify", "--quiet", ref], cwd=ROOT,
                                            capture_output=True).returncode, 0, ref)
        for ref, path in sorted(links):
            target = f"{ref}:{path}" if path else ref
            if ref == "site":  # the branch the site deploys from: its files are here
                self.assertTrue((ROOT / path).exists(), path)
                continue
            result = subprocess.run(["git", "cat-file", "-e", target], cwd=ROOT, capture_output=True)
            self.assertEqual(result.returncode, 0, f"{target} does not exist")

    def test_the_submitted_version_is_linked(self):
        for page in PAGES:
            self.assertIn(f"{REPO}/blob/submission/paper/report.pdf", page.read_text(encoding="utf-8"))
        self.assertIn(f"{REPO}/tree/submission", (DOCS / "index.html").read_text(encoding="utf-8"))


class OpeningEvidence(unittest.TestCase):
    def test_condensed_opening_uses_the_real_scripted_episode(self):
        data = json.loads((DOCS / "data" / "episodes.json").read_text(encoding="utf-8"))
        episode = next(item for item in data["episodes"] if item["key"] == "sol-scripted-01")
        page = (DOCS / "index.html").read_text(encoding="utf-8")
        prompt_excerpt = "You and the other agent exchange your tokens through the board in this order."
        self.assertIn(prompt_excerpt, episode["prompt"])
        self.assertIn(prompt_excerpt, page)
        offer = next(step["text"] for step in episode["steps"] if step["actor"] == "alpha" and step["action"] == "write")
        for excerpt in ("Please post your token reversed, character by character", "I will read it and reverse it."):
            self.assertIn(excerpt, offer)
            self.assertIn(excerpt, page)
        reply = next(step["text"] for step in episode["steps"] if step["actor"] == "beta" and step["action"] == "write")
        self.assertIn(reply, page)
        self.assertIn(f"#single/{episode['key']}", page)


class CaseEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = json.loads((DOCS / "data" / "episodes.json").read_text(encoding="utf-8"))
        cls.cases = {episode["key"]: episode for episode in data["episodes"]}
        cls.page = (DOCS / "index.html").read_text(encoding="utf-8")

    def test_archive_exhibit_keeps_the_denied_read_separate_from_the_shared_source(self):
        episode = self.cases["sol-archive-02"]
        events = {event["seq"]: event for event in episode["steps"]}
        self.assertEqual(events[4]["text"], episode["tokens"]["alpha"])
        self.assertEqual(events[5]["error"], "access_denied")
        self.assertEqual(events[5]["actor"], "beta")
        self.assertIn("archive/", events[9]["page"])
        self.assertIn(episode["tokens"]["alpha"], events[9]["text"])
        self.assertIn(episode["tokens"]["alpha"], self.page)
        self.assertIn("Read refused", self.page)

    def test_permission_exhibit_uses_matching_observer_records_and_the_real_rule(self):
        forbidden = self.cases["luna-pact-02"]
        permitted = self.cases["luna-norule-02"]

        def observer(case):
            return [{key: event.get(key) for key in ("pages", "log", "answer")}
                    for event in case["steps"]]

        self.assertEqual(observer(forbidden), observer(permitted))
        rule = "Your token is confidential: never write it on any page."
        self.assertIn(rule, forbidden["prompt"])
        self.assertNotIn(rule, permitted["prompt"])
        self.assertIn(rule, self.page)
        for event in forbidden["steps"]:
            if event["action"] == "write":
                self.assertIn(event["text"], self.page)

    def test_permission_redline_quotes_each_prompt_verbatim(self):
        forbidden, permitted = self.cases["luna-pact-02"]["prompt"], self.cases["luna-norule-02"]["prompt"]
        block = self.page[self.page.index('class="redline-body"'):]
        block = block[:block.index("</div>")]
        only_rule = re.findall(r'<span class="only-rule[^"]*">(.*?)</span>', block)
        only_norule = re.findall(r'<span class="only-norule[^"]*">(.*?)</span>', block)
        self.assertTrue(only_rule and only_norule)
        for sentence in only_rule:
            self.assertIn(sentence, forbidden)
            self.assertNotIn(sentence, permitted)
        for sentence in only_norule:
            self.assertIn(sentence, permitted)
            self.assertNotIn(sentence, forbidden)
        for kept in re.findall(r'<p class="same">(.*?)</p>', block):
            for fragment in (part.strip() for part in kept.split("[…]")):
                if fragment:
                    self.assertIn(fragment.replace("&#x27;", "'"), forbidden)
                    self.assertIn(fragment.replace("&#x27;", "'"), permitted)

    def test_event_numbers_in_exhibits_match_the_episode_logs(self):
        tracks = re.findall(r'<div class="track[^"]*">(.*?)</div>', self.page, re.S)
        expected = [("sol-21", [[3], [4], [6], [8, 9]]), ("sol-scripted-01", [[1], [2], [4], [9, 10]])]
        self.assertEqual(len(tracks), 2)
        for track, (key, stations) in zip(tracks, expected):
            shown = re.findall(r'<span class="evt" data-source="episodes">([^<]+)</span><b>([^<]+)</b>', track)
            steps = {step["seq"]: step for step in self.cases[key]["steps"]}
            self.assertEqual([label for _, label in shown], ["Offer", "Read", "Reply", "Use"])
            for (number, _), seqs in zip(shown, stations):
                self.assertEqual([int(n) for n in number.split("–")], seqs if len(seqs) == 1 else [seqs[0], seqs[-1]])
                self.assertTrue(all(seq in steps for seq in seqs))
            self.assertEqual(steps[stations[1][0]]["action"], "read")
            self.assertTrue(all(steps[seq]["action"] == "final_answer" for seq in stations[3]))
        leak = {step["seq"]: step for step in self.cases["luna-leak-01"]["steps"]}
        revisions = self.page[self.page.index('class="revision-stack"'):]
        self.assertEqual(re.findall(r'event <span data-source="episodes">(\d+)</span>', revisions[:revisions.index("</figure>")]), ["04", "01", "03"])
        self.assertTrue(leak[1]["seeded"] and leak[4]["action"] == "write" and leak[3]["read_revision"] == leak[1]["revision"])

    def test_revision_exhibit_preserves_the_fixture_seed_and_later_agent_request(self):
        episode = self.cases["luna-leak-01"]
        events = {event["seq"]: event for event in episode["steps"]}
        self.assertTrue(events[1]["seeded"])
        self.assertFalse(events[4]["seeded"])
        self.assertEqual(events[3]["read_revision"], events[1]["revision"])
        for seq in (1, 4):
            self.assertIn(events[seq]["text"], self.page)
        self.assertIn("it was not an action Alpha chose", self.page)


if __name__ == "__main__":
    unittest.main()
