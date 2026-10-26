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

An investigative journal with a small evidence plate, rather than a product landing page. Cool white,
blue ink, fine rules, a compact single-line masthead, underlined depth tabs and text-led actions.
No decorative motion, shader, canvas, 3D, scroll reveal, external component library or runtime CDN.

The system is defined in [DESIGN-SYSTEM.md](DESIGN-SYSTEM.md) and `assets/tokens.css`. It uses an 8px spacing
unit: 24px phone gutters (16px on compact phones), 48px larger gutters, a 48–64px column gap, a 176px contents
rail and a 656px prose measure. Small interface gaps can use a 4px half-step. Body type is 18/28px;
notes and literal source records are 14/24px. Rules and optical adjustments are not spacing tokens.
The cover stacks below 1024px. The contents rail becomes a native disclosure at that breakpoint.
Charts and tables can use the wider article area; tables scroll within their own container.

Type is self-hosted: Newsreader for editorial headings and reading text, Instrument Sans for navigation and
signposts, and JetBrains Mono for recorded strings. Their OFL licences are in `assets/fonts/`.
Colour and type tokens live in `assets/tokens.css`; the manual and system dark themes share the same values.
Agent identities and verdicts have text labels in addition to colour.

The font size, type contrast, prose measure, quiet navigation and ruled comparisons carry the character.
There is no continuous animation. Reduced-motion preferences are respected. Controls have visible
keyboard focus; principal controls have 48px targets. The reading bar is measured to keep
anchors below it. The desk’s controls are in the document flow; records remain the focal point.
At narrow widths the masthead uses the compact T/P/A title and short text links. Comparison landmarks
remain adjacent on phones, with original event numbers.

## Evidence desk

The explorer starts with the arranged/scripted comparison: offer, read, reply, uptake and instructions.
These are explicitly selected landmarks, not fabricated matched turns. Long page excerpts disclose
their full text in place; complete logs remain available in the inspector. Other cases and comparisons
are selected inside a native disclosure, leaving the first source event near the opening question.

It supports both legacy `#sol-21` and explicit `#single/sol-21` links, and `#compare/<pair>` comparisons.
Case and mode changes enter browser history; event, record and interpretation changes replace the
current entry. The fragment stores all three states, so copied links and reloads restore the view.
A direct comparison carries its left example into single-case mode.

Record selection adds page history, reads, final answers and instructions. Instructions were never
shown to the model judges; the interface says so. Observer and experiment-fixture lanes have visible
and programmatic names at every width. Interpretation and benchmark labels stay behind an explicit
reveal or the complete inspector. Unknown verdicts remain unknown. Source extraction, carrier checks
and figure data retain their original generators. Page-specific desk CSS is separate from shared styles.

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
