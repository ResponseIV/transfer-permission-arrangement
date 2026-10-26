"""Every number the website shows, at every reading level, is a fact registered here and found in the paper.

A fact is a claim as ``site_text.claims`` normalises it ("8", "19%", "20/20", a timestamp), a cue the sentence
showing it must match (so "4" in "in four, beta's request went unanswered" cannot borrow the "4" of "four
OpenAI models"), and verbatim snippets of ``paper/report.md`` that hold it. Distinctive values (100 or more, or
decimals) need no cue. The cautions every level must state are checked separately.
"""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_text  # noqa: E402

PAPER = site_text.ROOT / "paper" / "report.md"
README = site_text.ROOT / "README.md"

# (claim, cue or None, paper snippets)
FACTS = [
    ("0", r"from 0 to 28", ["nontransfers from 0 to 28 of 194"]),
    ("0", r"Rule arms 154|Shared archive 40", ["| Rule arms | 154 | 0 | 1 | 31 |", "| Shared archive | 40 | 0 | 12 | 29 |"]),
    ("0", r"Blind proposal", ["| Blind proposal hand read | 4 of 20 | 0 |"]),
    ("1", r"acceptance 1, completion 1", ["offer 4, acceptance 1, completion 1"]),
    ("1", r"Figure 1", ["**Figure 1. How often a transfer alarm would be right.**"]),
    ("1", r"Rule arms 154", ["| Rule arms | 154 | 0 | 1 | 31 |"]),
    ("1%", None, ["If 1% of audited episodes held a transfer"]),
    ("2", r"2 ended in a transfer", ["and 2 ended in a transfer"]),
    ("2", r"2 by the frozen signal", ["2 by the frozen signal"]),
    ("2", r"2 pending", ["17 wrong, 2 pending or not scored"]),
    ("2", r"Figure 2", ["**Figure 2. Two ways a token passed.**"]),
    ("2", r"Table 2", ["**Table 2. Frozen judges on the 450 primary episodes"]),
    ("2.3", r"question 2\.3", ["Question 2.3 asks"]),
    ("2.7", r"lower bound 2\.7", ["Pooling the retained cases gives 3.8, lower bound 2.7"]),
    ("3", r"3 instructed pacts", ["(3 instructed pacts, 9 authorized conventions)"]),
    ("3", r"only 3 pact episodes", ["only 3 pact episodes completed a transfer"]),
    ("3", r"Table 3", ["**Table 3. False alarms with page writes and log"]),
    ("3", r"Section 3", ["## 3. Methods"]),
    ("3.8", r"3\.8", ["looks 3.8 times as common under transfer"]),
    ("4", r"offer 4|4 offer disagreements", ["offer 4, acceptance 1, completion 1", "the 4 offer disagreements"]),
    ("4", r"four OpenAI models", ["on four\nOpenAI models"]),
    ("4", r"four label fields", ["(eight signals and four label fields)"]),
    ("4", r"four nontransfer columns", ["The four nontransfer columns total 194 retained cases"]),
    ("4", r"in four\b", ["in four, beta's request for alpha's token in return went unanswered"]),
    ("4", r"four earlier", ["shaped by the four earlier\nagent-arranged transfers"]),
    ("4", r"four cells", ["all four cells read were ones the judge flagged"]),
    ("4.0", r"CC BY-NC 4\.0", ["data CC BY-NC 4.0"]),
    ("4.3", r"Section 4\.3", ["### 4.3 Permission"]),
    ("5%", None, ["On page writes alone, 5%."]),
    ("6", r"six (registered )?follow-ups|Six follow-ups", ["Six follow-ups, each\nregistered"]),
    ("6", r"six (frozen )?(page and log )?signals|six warning signs|six that do not use|Six page and log signals",
     ["the six frozen page and log signals were identical"]),
    ("6", r"6 scorable|Scripted offer", ["(Qwen: 6 scorable episodes, Appendix B)", "Qwen3-32B (6 of\n8 attempted)"]),
    ("7", r"seven transfers", ["seven transfers went only\nto it"]),
    ("7", r"missed seven encoded carriers", ["one of eight transfers and misses seven encoded carriers"]),
    ("7", r"7 pending", ["14 wrong, 7 pending or not scored"]),
    ("8", r"eight (actions|turns)", ["Each has at most eight actions"]),
    ("8", r"8 an acceptance|all 8 completed", ["13 contained an offer, 8 an acceptance, and all 8 completed"]),
    ("8", r"8 transfers|few: 8|moved 8 times|every one of the 8", ["all eight transfers the agents arranged themselves"]),
    ("8", r"eight agent-arranged|eight successful offers", ["All eight successful offers came from alpha"]),
    ("8", r"eight (frozen )?signals|Eight signals", ["Eight frozen signals include these"]),
    ("8", r"of 8 attempted", ["Qwen3-32B (6 of\n8 attempted)"]),
    ("8", r"8 partly", ["51 held, 8 partly, 17 wrong"]),
    ("9", r"nine hexadecimal", ["an initial and nine hexadecimal characters"]),
    ("9", r"9 false alarms|9 in the 12", ["and 9 in the 12 prescribed exchanges"]),
    ("9", r"flagged 9", ["the proposal judge flagged 9"]),
    ("9", r"9 authorized conventions", ["(3 instructed pacts, 9 authorized conventions)"]),
    ("9", r"prompt 9", ["gpt-5.6-luna, prompt 9"]),
    ("9", r"Pages and log 244|Pages, log and answers 244|Failed prescribed exchanges",
     ["| Pages and log | 244 | 9 | 233 | 25 |", "| Pages, log and answers | 244 | 9 | 232 | 32 |",
      "| Failed prescribed exchanges | 12 | 9 | 12 | 9 |"]),
    ("10", r"prompt 10", ["gpt-6-astra, prompt 10"]),
    ("10", r"10 with a request", ["(10 with a request by hand\ncount"]),
    ("10", r"all ten agent-arranged", ["as the screen did on all ten agent-arranged\ntransfers"]),
    ("11", r"all 11 scripted", ["all 11 scripted episodes"]),
    ("11", r"11 excluded", ["(461 attempts; 11 excluded, one a provider refusal)"]),
    ("11%", None, ["(at least 11% at the interval bounds)"]),
    ("12", r"(in )?the 12 prescribed exchanges", ["and 9 in the 12 prescribed exchanges that did not complete"]),
    ("12", r"12 paired tests", ["Of the 12\npaired tests in that family"]),
    ("12", r"12 partly", ["32 held, 12 partly"]),
    ("12", r"In 12 of its 17", ["In 12 of its 17 pact episodes"]),
    ("12", r"Shared archive 40|Failed prescribed exchanges",
     ["| Shared archive | 40 | 0 | 12 | 29 |", "| Failed prescribed exchanges | 12 | 9 | 12 | 9 |"]),
    ("13", r"13 contained an offer", ["13 contained an offer"]),
    ("14", r"14 wrong", ["12 partly, 14 wrong"]),
    ("16", r"16 were not read", ["16 were not read"]),
    ("17", r"17 wrong", ["8 partly, 17 wrong"]),
    ("17", r"of its 17", ["In 12 of its 17 pact episodes"]),
    ("17", r"against 17", ["against 17 without the rule"]),
    ("18", r"Pages 240", ["| Pages | 240 | 39 | 195 | 18 |"]),
    ("19", r"19 of them|all 19|19 such calls", ["Astra called 19 of them transfers", "removed all 19"]),
    ("19", r"in 19 the reply", ["though in 19\nthe reply came before the offer could be read"]),
    ("19%", None, ["19% of Astra's alarms with the log\nwould be real"]),
    ("20", r"all 20 of its (archive|shared-cabinet) episodes", ["in all 20 of its archive episodes"]),
    ("20", r"20 (Luna )?(task |matched )?pairs", ["identical across the 20 task pairs"]),
    ("20", r"all 20 Luna", ["taken in all\n20 Luna episodes"]),
    ("20", r"fired on all 20", ["fired on all 20"]),
    ("20", r"Scripted offer", ["scripted offer with no rule on Sol (20)"]),
    ("25", r"Pages and log 244", ["| Pages and log | 244 | 9 | 233 | 25 |"]),
    ("26", r"all 26", ["called all 26 agent-made candidates"]),
    ("28", r"28 (in those same|false alarms)|raised 28", ["On page writes alone it\nraised 28 in the 194"]),
    ("29", r"Shared archive 40", ["| Shared archive | 40 | 0 | 12 | 29 |"]),
    ("31", r"Rule arms 154", ["| Rule arms | 154 | 0 | 1 | 31 |"]),
    ("32", r"32 held", ["the author 32 held"]),
    ("32", r"Pages, log and answers 244", ["| Pages, log and answers | 244 | 9 | 232 | 32 |"]),
    ("34", r"34 scorable|letter-rule arm on Qwen3-32B", ["no offer in 34 scorable episodes", "(34 of 39 attempted)"]),
    ("35%", None, ["the point\nestimate is 100% and the bound 35%"]),
    ("37", r"in 37", ["the request signal in 37"]),
    ("39", r"39 scorable|of 39 attempted", ["Of 39 scorable episodes", "(34 of 39 attempted)"]),
    ("39", r"Pages 240", ["| Pages | 240 | 39 | 195 | 18 |"]),
    ("40", r"40 new (Sol )?episodes", ["Before 40 new Sol episodes"]),
    ("40", r"all 40 episodes", ["both answers matched in all 40 episodes"]),
    ("40", r"40-episode", ["a 40-episode follow-up"]),
    ("40", r"Shared archive 40|Luna, Sol, Qwen3-32B", ["| Shared archive | 40 | 0 | 12 | 29 |",
                                                       "Luna (40), Sol (57) and Qwen3-32B (60)"]),
    ("43", r"43 failed", ["(43 failed, kept and\nflagged)"]),
    ("51", r"51 held", ["Claude 51 held"]),
    ("57", r"Luna, Sol, Qwen3-32B", ["Luna (40), Sol (57) and Qwen3-32B (60)"]),
    ("60", r"Luna, Sol, Qwen3-32B", ["Luna (40), Sol (57) and Qwen3-32B (60)"]),
    ("60", r"60 planted-leak", ["the 60 planted-leak transfers"]),
    ("60", r"(called|in) all 60", ["Astra with the log called all 60", "uptake and the informed read fired in all 60"]),
    ("39", r"new seed", ["39 Sol episodes on a new seed"]),
    ("95%", None, ["(Clopper–Pearson, 95%)"]),
    ("100%", None, ["the point\nestimate is 100%"]),
    (".77", None, ["rate ratio of .77, lower bound .72"]),
    ("0.72", None, ["(lower bound 0.72)"]),
    ("0.80", None, ["κ = 0.96, against 0.80 on page writes"]),
    ("0.96", None, ["κ = 0.96, against 0.80 on page writes"]),
    ("0.0001", None, ["(p = 0.0001)"]),
    ("0.0005", None, ["(raw\npaired p = 0.0005)"]),
    ("0.0007", None, ["adjusted p = 0.0007"]),
    ("0/0", r"0/0", ["A 0/0 entry has no eligible negative cases"]),
    ("143", None, ["All 143 registered forecasts"]),
    ("154", None, ["| Rule arms | 154 | 0 | 1 | 31 |"]),
    ("194", None, ["raised no false alarm on the\n194 episodes where no exchange was prescribed"]),
    ("195", None, ["| Pages | 240 | 39 | 195 | 18 |"]),
    ("206", None, ["false alarms in 206 episodes without one"]),
    ("232", None, ["| Pages, log and answers | 244 | 9 | 232 | 32 |"]),
    ("233", None, ["| Pages and log | 244 | 9 | 233 | 25 |"]),
    ("240", None, ["| Pages | 240 | 39 | 195 | 18 |"]),
    ("242", None, ["242 of them prescribed exchanges"]),
    ("244", None, ["found all 244 primary transfers"]),
    ("450", None, ["a 450-episode primary test"]),
    ("461", None, ["(461 attempts; 11 excluded"]),
    ("706", None, ["706 scorable episodes"]),
    ("1174", None, ["1,174 earlier episodes"]),
    ("1198", None, ["1,198 prior attempts, 1,174 scorable"]),
    ("1500", None, ["versus 1,500 per\nagent on the OpenAI route"]),
    ("4096", None, ["Its declared allowance was 4,096 tokens per action"]),
    ("1923", None, ["1,923 episode records (43 failed"]),
    ("1986", None, ["(Matsushita, 1986)"]),
    ("2011", None, ["Kovacic et al. (2011)"]),
    ("2016", None, ["Mehra (2016)"]),
    ("2026", None, ["accessed 26 October 2026"]),
    ("20261024", None, ["The no-rule and leak comparisons use 20261024"]),
    ("20261027", None, ["the separate Sol follow-up uses 20261027"]),
    ("2026-10-23T12:00Z", None, ["The public sprint opened at 2026-10-23T12:00Z."]),
    ("15:27:34Z", None, ["The annotated `sprint-freeze` tag was recorded at 15:27:34Z"]),
    ("15:27:57Z", None, ["before the first primary run\nmanifest at 15:27:57Z"]),
    # Pairs ("8 of 8", "17/20"), each with the paper's sentence or table row.
    ("0/10", r"^(opportunity|asks for|secret-like|string reused|informed read|answers agree|uptake)", ["| opportunity | 244/244 | 0/40 | 0/0 | 143/144 | 8/10 |", "| asks for a token | 58/244 | 0/40 | 0/0 | 144/144 | 0/10 |"]),
    ("0/40", r"^(opportunity|asks for|secret-like|string reused|informed read|answers agree|uptake)|^Archive", ["| asks for a token | 58/244 | 0/40 |", "0/40 (0.000–0.088)"]),
    ("0/144", r"^(string reused|informed read|answers agree|uptake)", ["| uptake | 174/244 | 0/40 | 0/0 | 0/144 | 0/10 |"]),
    ("0/154", None, ["0/154 (0.000–0.024)"]),
    ("1/8", None, ["only 1 of the 8 transfers in the Sol follow-up"]),
    ("1/8", r"retrospective|flow flag", ["Its flow flag finds\none of eight transfers and misses seven encoded carriers"]),
    ("1/31", None, ["1/31 (0.001–0.167)"]),
    ("2/2", None, ["2/2 (0.158–1.000)"]),
    ("2/3", r"two of the three models", ["signals unchanged on two models; a third model's traffic changed", "on three models"]),
    ("2/156", r"2 of 156", ["146 of 156 episodes contained a request for a token", "and 2 ended in a transfer"]),
    ("3/3", None, ["3/3 (0.292–1.000)"]),
    ("3/12", None, ["3 of the 12 failed prescribed exchanges"]),
    ("3/17", None, ["Sol 3/17 against 20/20"]),
    ("4/5", None, ["four of the five unanswered\noffers were never read"]),
    ("4/8", r"four of the eight", ["in four, beta's request for alpha's token in return went unanswered",
                                    "All eight successful offers came from alpha"]),
    ("4/20", None, ["| Blind proposal hand read | 4 of 20 | 0 |"]),
    ("5/20", None, ["(5 of 20 under the pact"]),
    ("6/9", None, ["6/9 (0.299–0.925)"]),
    ("8/8", None, ["| Sol follow-up | astra p10, both | 39/39 | 0/0/0 | 8/8 (0.631–1.000)"]),
    ("8/10", r"^opportunity", ["| opportunity | 244/244 | 0/40 | 0/0 | 143/144 | 8/10 |"]),
    ("9/10", None, ["9 of the 10 agent-arranged transfers"]),
    ("9/144", r"^secret-like", ["| secret-like string on a page | 243/244 | 20/40 | 0/0 | 9/144 | 0/10 |"]),
    ("11/20", None, ["Qwen 12/20 against\n11/20"]),
    ("11/144", r"^asks for a code", ["| asks for a code | 52/244 | 0/40 | 0/0 | 11/144 | 0/10 |"]),
    ("12/20", None, ["Qwen 12/20 against"]),
    ("17/17", None, ["17/17 (0.805–1.000)"]),
    ("17/20", None, ["Luna 17/20 against 20/20"]),
    ("20/20", None, ["in 20 of\n20 episodes", "20 of 20 without the rule"]),
    ("20/40", r"^secret-like", ["| secret-like string on a page | 243/244 | 20/40 |"]),
    ("22/24", None, ["(22 of 24 correct)"]),
    ("23/60", None, ["| Luna p9 | Pages | 23/60 |"]),
    ("24/38", None, ["The author's blind check covers 24 of 38 episodes"]),
    ("27/31", None, ["27 of the 31 the screen flagged"]),
    ("28/194", None, ["from 0 to 28 of 194"]),
    ("0/194", None, ["0 false alarms on 194 episodes with no prescribed exchange"]),
    ("39/39", None, ["agree on offer presence in 39/39 Sol follow-up"]),
    ("40/40", r"^answers agree|all 40", ["| answers agree | 189/244 | 40/40 |"]),
    ("52/244", r"^asks for a code", ["| asks for a code | 52/244 |"]),
    ("58/244", r"^asks for a token", ["| asks for a token | 58/244 |"]),
    ("59/60", None, ["| Luna p9 | Pages and log | 59/60 |"]),
    ("60/60", None, ["60 of 60"]),
    ("130/244", r"^string reused", ["| string reused across authors | 130/244 |"]),
    ("143/144", r"^opportunity", ["| opportunity | 244/244 | 0/40 | 0/0 | 143/144 |"]),
    ("144/144", r"^asks for a token", ["| asks for a token | 58/244 | 0/40 | 0/0 | 144/144 |"]),
    ("146/156", None, ["146 of 156 episodes contained a request for a token"]),
    ("157/244", r"^informed read", ["| informed read | 157/244 |"]),
    ("174/244", r"uptake", ["uptake found 174 of 244 primary transfers"]),
    ("189/244", r"[Aa]greeing answers|^answers agree", ["Agreeing answers occurred in 189 of 244 transfers"]),
    ("225/225", None, ["225/225 (0.984–1.000)"]),
    ("242/244", None, ["242 of them prescribed exchanges", "all 244 primary transfers"]),
    ("243/244", r"^secret-like", ["| secret-like string on a page | 243/244 |"]),
    ("244/244", r"^opportunity|primary transfers found", ["| opportunity | 244/244 |", "244/244 transfers found"]),
] + [(value, None, [snippet]) for value, snippet in [
    ("0.000", "0/154 (0.000–0.024)"), ("0.024", "0/154 (0.000–0.024)"), ("0.088", "0/40 (0.000–0.088)"),
    ("0.001", "1/31 (0.001–0.167)"), ("0.167", "1/31 (0.001–0.167)"), ("0.158", "2/2 (0.158–1.000)"),
    ("0.292", "3/3 (0.292–1.000)"), ("0.299", "6/9 (0.299–0.925)"), ("0.925", "6/9 (0.299–0.925)"),
    ("0.631", "8/8 (0.631–1.000)"), ("0.805", "17/17 (0.805–1.000)"), ("0.940", "60/60 (0.940–1.000)"),
    ("0.984", "225/225 (0.984–1.000)"), ("1.000", "2/2 (0.158–1.000)")]]

# Not in the paper: the sprint track, from the README as submitted.
README_FACTS = {("2", r"track 2"): "track 2, question 2.3"}

# Each level states the cautions in its own words; these numbers must appear at every level.
CAUTIONS = {"242/244", "24/38", "4/20", "20/20", "60/60"}


def squash(text: str) -> str:
    return " ".join(text.split())


def number_forms(claim: str) -> list[str]:
    """How a claim's numbers may be written in the paper: digits (with or without thousands separators)."""
    if "/" in claim:
        return claim.split("/")
    return [claim]


def written(value: str, text: str) -> bool:
    value = value.rstrip("%")
    words = {"1": "one", **{str(v): k for k, v in {**site_text.PAIR_WORDS, **site_text.WORDS}.items()}}
    pattern = re.escape(value) if not value.isdigit() or len(value) < 4 else re.escape(f"{int(value):,}") + "|" + value
    if value in words:
        pattern += "|" + words[value]
    return re.search(rf"(?<![\d.])(?:{pattern})(?![\d])", text, re.I) is not None


def rendered(level: str) -> list[str]:
    pages = [site_text.units((site_text.DOCS / name).read_text(encoding="utf-8"), level)
             for name in ("index.html", "explorer.html")]
    scripts = [text for name in ("explorer.js", "site.js")
               for text in site_text.script_strings(site_text.DOCS / "assets" / name)]
    return [unit for units in pages for unit in units] + site_text.episode_texts(level) + scripts


class Registry(unittest.TestCase):
    def test_every_snippet_is_in_the_paper_and_holds_its_number(self):
        paper = squash(PAPER.read_text(encoding="utf-8"))
        for claim, _, snippets in FACTS:
            for snippet in snippets:
                self.assertTrue(squash(snippet) in paper, f"{claim}: snippet not in the paper: {snippet!r}")
            joined = " ".join(snippets)
            for value in number_forms(claim):
                if re.fullmatch(r"\d{4}-\d{2}-\d{2}T.*|\d{2}:\d{2}:\d{2}Z", claim):
                    self.assertIn(claim, joined)
                else:
                    self.assertTrue(written(value, joined), f"{claim}: {value} not in its snippets")

    def test_readme_facts_are_in_the_readme(self):
        readme = squash(README.read_text(encoding="utf-8"))
        for snippet in README_FACTS.values():
            self.assertIn(snippet, readme)

    def test_cues_only_on_small_numbers(self):
        for claim, cue, _ in FACTS:
            if cue is None:
                self.assertTrue("/" in claim or "." in claim or ":" in claim or "%" in claim or int(claim) >= 100,
                                f"{claim} needs a cue")


class EveryLevel(unittest.TestCase):
    def check(self, level: str):
        unmatched = []
        found = set()
        for unit in rendered(level):
            for claim in site_text.claims(unit):
                found.add(claim)
                ok = any(fact == claim and (cue is None or re.search(cue, unit, re.I))
                         for fact, cue, _ in FACTS)
                ok = ok or any(fact == claim and re.search(cue, unit, re.I) for fact, cue in README_FACTS)
                if not ok:
                    unmatched.append(f"{claim!r} in: {unit[:160]}")
        self.assertEqual(unmatched, [], f"{level}: numbers not registered as paper facts")
        self.assertLessEqual(CAUTIONS, found, f"{level}: a caution is missing")

    def test_beginner(self):
        self.check("beginner")

    def test_amateur(self):
        self.check("amateur")

    def test_expert(self):
        self.check("expert")

    def test_the_readme_count_trap_is_not_on_the_site(self):
        # The README says 5 returns were asked for; the paper says 4, within the 8 Sol follow-up transfers.
        for level in site_text.LEVELS:
            for unit in rendered(level):
                self.assertNotRegex(unit, r"\b(5|five)\b[^.]*\b(asked for|request)[^.]*\breturn")


if __name__ == "__main__":
    unittest.main()
