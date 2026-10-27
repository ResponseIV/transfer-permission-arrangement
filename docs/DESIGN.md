# An editorial companion to the paper

This site was redesigned after submission, on 26 October 2026. The scientific source remains
`paper/report.md`, the `submission` tag and the extracted benchmark. The site changes no result.

## The reading experience

Lead with a question a reader can understand: **A secret moved. Was there a deal?** A condensed real
episode sits beside it. Adding reads establishes the event order; adding the instructions reveals
that the experiment supplied the sequence. The interface demonstrates why a plausible trace is
not sufficient evidence of an agent-made plan.

The opening quotes and reversed token come from `sol-scripted-01` in `data/episodes.json`; the
complete episode is linked beside them. The fixed order in the original log is preserved, but
intermediate actions are omitted and explicitly labelled as a condensation. The anonymous observer
records themselves are available in the explorer; the opening uses the fixture's attribution for
explanation. It is not an invented chat or a new observation.

The story is a case notebook. A private note looks incriminating until its read is refused. Matching
traffic acquires a different meaning under different instructions. A recorded offer survives an
event test, but a supplied script reproduces the pattern. An earlier revision exposes a planted leak.
Each case separates the record, the supported finding and an alternative left open. Real tokens,
source excerpts and links to full episodes give the article its character.

The investigation adds a failed shortcut: a retrospective flow flag missed encoded carriers. Its
timing and development-data limits are stated beside it. The base-rate section introduces a simple
hypothetical scenario before the curves and uncertainty. The end offers a direct local PDF, the
submitted repository, readable text and citation, with a factual source docket instead of a fake cover.

## Three depths with different substance

| Depth | Contents |
| --- | --- |
| The essentials | Plain-language setup, the concrete cases, record requirements and limits. No statistical tables. Terms are explained when introduced. |
| The investigation | Adds constructed alternatives, the research reversals, comparative tables, a base-rate lesson and discussion of matching answers. Technical detail is disclosed in place. |
| The research | Adds an evidence map, operational definitions, full breakdowns, intervals, judges, registration history, human-check coverage and reproduction notes. |

The first visit defaults to the essentials. Existing `?level=beginner`, `amateur`, `expert` URLs and
stored choices remain compatible. The radio group uses these stable internal values but gives readers
task-oriented labels. Choices persist across pages, are announced, and preserve a shared reading anchor.
Links to hidden specialist sections select a sufficient depth and open any containing disclosure before
scrolling. Without JavaScript the essentials still read as a complete article; the opening discloses
the scripted explanation in a `noscript` note and the desk offers a static comparison as well as raw data.

## Layout and visual language

An investigator's annotated printout: cool white paper, navy ink, one blue for links, the active control and the
turn of the headline, and a yellow **highlighter** on the record that changes the verdict: the instructions, the
decisive line of a log, the inserted sentence, the planted token. Agents keep their own colours (Alpha blue, Beta
plum), always with their names. Space separates chapters; there are no eyebrow labels, tracked capitals, dot
separators or decorative rules. A caption gives the source and a link, never a restatement of the figure.

**One sheet, five compositions.** Exhibits share plain sans labels, mono event numbers, hairline rows and the
highlighter. What varies is the shape, chosen to fit what each case shows:

| Case | Composition |
| --- | --- |
| Opening | A record sheet with tabs: add records one at a time; the instructions arrive highlighted |
| Transfer | A record sheet with the refused read struck through and highlighted, then a unit chart of the 194 episodes (28 against 0) |
| Permission | A redline of the two real prompts: the rule struck, the reworded sentence inserted, the shared trace beneath |
| Arrangement | Two aligned tracks (offer, read, reply, use) with original event numbers; solid for agent-made, dashed for scripted |
| Leak | A revision stack: the page an auditor finds lies over the planted revision Beta read |

The page varies its width and rhythm: a cover split between the question and the opening exhibit, a full-width
band of the three questions (echoed by the three-column "what to keep"), a measured reading column with a
contents rail, exhibits that alternate between a white sheet and open compositions, and, on wide screens,
cautions set as notes in the right margin.

Type is self-hosted: Newsreader for reading and display (large, light, tight), Instrument Sans for controls and
notes and labels, JetBrains Mono for anything recorded. Licences are in `assets/fonts/`. Tokens live
in `assets/tokens.css`; `tests/test_site.py` checks every colour pair in use, including the highlighter, in both themes.

## Evidence desk

Controls first. A sticky band holds the view (compare two, or one episode), the case, and the record stack
(1 Pages, 2 + Access log, 3 + Answers, 4 + Instructions; cumulative, the fourth highlighted). The question
is the heading; the reveal comes after the evidence, below the instructions row, so a reader holds every record
before seeing the answer. It names the true actors of unsigned board events in blue and gives each side's verdict.

Compare is a ledger: landmarks in a gutter, A and B as columns, original event numbers, page text clamped with
"Show the whole page". The instructions row is closed until the instructions record is held, and offers a button
that adds it; once open it quotes the deciding sentences, with the whole prompt one tap away. Columns stay
adjacent down to 320px.

One episode is a stepped log. The first depth is a guided walk: the fixture side sits beside each event as a guide
(what happens, what to notice), and the verdict comes at the last step. From the second depth the reader audits:
only the observer record is shown until "Reveal what happened" adds the fixture's record and the verdict; the third
depth adds raw fields. Labels, signals and every
judge verdict are in a closed inspector at the end. The router keeps `#compare/<pair>`, `#single/<case>` and legacy
`#<case>` links, with record, step and reveal state.

## References

These informed the design, rather than supplying copied components or claims:

- [Anthropic, Alignment faking](https://www.anthropic.com/research/alignment-faking): a concrete opening,
  a sustained explanation and substantive caveats.
- [Swarmchasers, Tencent fleet report](https://swarmcha.se/posts/chinese-agent-fleet-full-report): visible
  chapter navigation and a documented investigation process.
- [Distill, Communicating with Interactive Articles](https://distill.pub/2020/communicating-with-interactive-articles/):
  a small interaction that helps readers reason about the claim.
- [Works in Progress](https://worksinprogress.co/archive/): compact publication furniture and editorial hierarchy.
- [The Pudding](https://pudding.cool/about/): visual explanation shaped around the subject.
- [Bencho](https://bencho.dev/): inspected its evidence-inspector and step-player ideas; no source or dependency copied.

The user's explicit direction is calm, instructive and editorial, with an 8px grid. Local commits only;
ask before any push or publication.

## Verification and maintenance

Run `python3 -m unittest discover -s tests -p 'test_site*.py' -q` and
`node --test tests/site-reading-state.test.cjs tests/site-explorer.test.cjs`. They check the numeric registry
at every depth, source extraction, generated figures, contrast, links, fragment targets, real case excerpts,
reading state and curated event references, plus the PDF's byte identity with the submitted PDF.
These checks use the Python and Node standard libraries.

Browser QA covers 320px, 375px, 768px and 1440px layouts, all depths, record selection, hidden deep links,
case and mode history, comparison reveal and source-lane names. The revision record at
`audit/site-2026-10-26/IMPLEMENTATION.md` describes fallbacks exercised and remaining assistive checks.
No scientific experiment or paid model call is part of site development.

If the submitted paper changes intentionally, update the local PDF and provenance checks together.
Do not silently replace the scientific source with a later draft.
