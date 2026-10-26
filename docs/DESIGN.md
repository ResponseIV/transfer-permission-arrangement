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

The story then asks three questions: transfer, permission, arrangement. Each heading states the
problem in ordinary language, each finding names the needed record, and the cautions remain beside
the result. The end offers a direct local PDF, the submitted repository, readable text and citation.

## Three depths with different substance

| Depth | Contents |
| --- | --- |
| The essentials | Plain-language setup, the three findings, event traces, recommendations and limits. No statistical tables. Terms are explained when introduced. |
| The investigation | Adds the constructed look-alikes, the research process, cumulative records, comparative tables, base-rate chart and discussion of matching answers. |
| The research | Adds operational definitions, full breakdowns, intervals, judges, registration history, human-check coverage and reproduction notes. |

The first visit defaults to the essentials. Existing `?level=beginner`, `amateur`, `expert` URLs and
stored choices remain compatible. The radio group uses these stable internal values but gives readers
task-oriented labels. Choices persist across pages, are announced, and preserve a shared reading anchor.
Links to hidden specialist sections select a sufficient depth before scrolling. Without JavaScript the
essentials still read as a complete article; the opening discloses the scripted explanation in a
`noscript` note and the explorer links its raw data.

## Layout and visual language

An investigative journal with a small evidence plate, rather than a product landing page. Cool white,
blue ink, fine rules, a compact single-line masthead, underlined depth tabs and text-led actions.
No decorative motion, shader, canvas, 3D, scroll reveal, external component library or runtime CDN.

The main grid uses an 8px spacing unit: 24px phone gutters, 48px larger gutters, a 64px column gap,
a 176px contents rail and a 656px prose measure. Small interface gaps can use a 4px half-step.
Body line height is 1.68. Rules and optical adjustments are not constrained to the spacing unit.
The cover stacks below 1000px. The contents rail becomes a native disclosure at that breakpoint.
Charts and tables can use the wider article area; tables scroll within their own container.

Type is self-hosted: Instrument Sans for navigation and the opening question, Newsreader for reading
and chapter headings, JetBrains Mono for recorded strings. Their OFL licences are in `assets/fonts/`.
Colour tokens live in `assets/style.css`; the manual and system dark themes share the same values.
Agent identities and verdicts have text labels in addition to colour.

The font size, type contrast, prose measure, quiet navigation and ruled comparisons carry the character.
There is no continuous animation. Reduced-motion preferences are respected. Controls have visible
keyboard focus; principal controls have at least 44px targets. Header and explorer-control measurements
keep sticky elements from overlapping. The phone stepper reserves room so the current event is visible.

## Evidence desk

The explorer opens its cases through reader-facing questions in a native selector, with exact case
identifiers retained in a source disclosure. It supports both legacy `#sol-21` and explicit
`#single/sol-21` links, and `#compare/<pair>` comparisons. Case changes enter browser history;
step and record changes do not. A direct comparison carries its left example into single-case mode.

Record selection adds page history, reads, final answers and instructions. Instructions were never
shown to the model judges; the interface says so. Unknown verdicts remain unknown. Source extraction,
carrier checks and figure data retain their original generators.

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

Run `python3 -m unittest discover -s tests -p 'test_site*.py' -q`. It checks the numeric registry at every
depth, source extraction, generated figures, contrast, links, fragment targets, real opening excerpts and
the local PDF's byte identity with the submitted PDF. This uses the standard library.

Browser QA covers 375px, 768px and 1440px layouts; all depths, record tabs, hidden deep links, case and mode
history, comparison reveal, theme and the phone stepper. A browser record is in the local session ledger.
No scientific experiment or paid model call is part of site development.

If the submitted paper changes intentionally, update the local PDF and provenance checks together.
Do not silently replace the scientific source with a later draft.
