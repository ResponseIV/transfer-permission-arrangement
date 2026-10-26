# Website design brief

Post hoc (2026-10-26). The site in this folder explains the paper `paper/report.md` and lets readers step
through logged episodes. It changes no result. Every number on it comes from the paper and is checked by
`tests/test_site_numbers.py`.

## Concept: the record you hold

The paper's one idea is that what you can prove depends on which record you hold: the pages, the access log,
the final answers, the instructions. The site makes that its form. Records are drawn as stacked sheets, each with a
numbered tab. Wherever evidence appears (the explainer's diagrams, the explorer's record switch, the comparison
mode) the same rule holds: adding a sheet shows more, and what a sheet cannot show is greyed and labelled, never
silently hidden. The explorer gains the fourth sheet, the instructions, because that is the record that tells a
scripted exchange from an arranged one, and a permitted exchange from a forbidden one.

## Three reading levels, one set of facts

One site with a persistent switch: **Beginner** (no AI or statistics background), **AI amateur** (knows what an
LLM and an agent are), **Field expert** (works on multi-agent safety, evals or monitoring). Structure, figures,
headline numbers and cautions are shared markup and identical at every level; only the prose around them changes.

| Level | Their question | They leave with |
|---|---|---|
| Beginner | "Did the AIs secretly team up, and how would anyone know?" | A token can move without a plan; a plan can be faked by a script; you need the right records to tell. And the limits: a small, synthetic test. |
| AI amateur | "What does this say about monitoring agents?" | The three questions, which record settles each, the headline counts and the two cautions. |
| Field expert | "What exactly was measured, against what denominators, and what can I reuse?" | Tables with intervals, the judge and prompt identities, signals, paired tests, the scripted control's design, blind-check coverage, the prior-work boundary, the freeze timeline, and how to reproduce. |

Default: **AI amateur**. It is the level the first-pass site was written at, it suits most people who arrive from a
sprint or news link, and both neighbours are one click away. No first-visit question: a modal before the first
sentence costs every reader and helps few. The choice persists in `localStorage` (guarded) and in `?level=`.

Implementation: prose blocks carry `data-lv="b"`, `"a"`, `"e"` or combinations; an inline head script sets
`<html data-level>` before first paint; CSS hides the other levels. Without JavaScript the page shows the AI-amateur
level. On a switch the page keeps the nearest shared element at the same screen position, so the reader does not
lose their place, and a polite live region announces the change. The switch is a native radio group.

## Typography

- **Newsreader** (variable, optical sizes 6–72, OFL) for text and headings: an editorial serif that stays calm at
  body size and gains contrast at display size.
- **Instrument Sans** (OFL) for interface: controls, labels, tabs, captions of data.
- **JetBrains Mono** (OFL) for what the fixture recorded: page bodies, tokens, paths, event numbers.

Scale (1.25, from 18 px body on desktop, 17 px on phones): 13 · 14.5 · 18 · 22.5 · 28 · 35 · 44 (hero, fluid).
Measure 64–70 characters. Numbers in tables are tabular.

## Colour

Paper and ink, one accent for "visible in this record", two agent colours, and a red-brown for the fourth sheet,
the instructions. Tokens are defined on `:root` and redefined for dark mode (`prefers-color-scheme` and a manual
toggle). `tests/test_site.py` computes the WCAG ratio of every text pair in use (at least 4.5:1) and of chart lines
and control borders (at least 3:1), in both themes.

| Token | Light | Dark | Use |
|---|---|---|---|
| `--paper` | #f6f4ee | #131412 | page background |
| `--sheet` | #fffdf8 | #1b1c1a | cards, sheets |
| `--ink` | #1b1a17 | #ebe8e0 | text |
| `--ink-2` / `--ink-3` | #514e47 / #69655c | #b3afa5 / #9a968c | secondary text, labels |
| `--control` | #857f72 | #73766b | borders of controls (3:1) |
| `--accent` | #1d5878 | #8ac2df | links, the records you hold |
| `--alpha` / `--beta` | #1d5878 / #94401e | #8ac2df / #eda17e | the two agents |
| `--fixture` | #536220 | #b8c680 | fixture, archive |
| `--yes` / `--no` | #1d6a3a / #8e2f21 | #8fd3a5 / #f2a191 | ground truth and verdicts, always with a word |
| `--fig-*` | blue, green, red | lighter tints | Figure 1, in the paper's hues |

## Grid and components

A single 680 px text column centred in a 1120 px frame; figures, tables and the explorer may break out to the
frame. 16 px gutters on phones. Components: the record stack (diagram and control), finding blocks (question,
record, headline number, prose), number tiles, a glossary, an expert "methods" section, the episode timeline with
an observer column and a ground-truth column, and a side-by-side comparison.

## Motion

Only to show change: a sheet sliding onto the stack, the current explorer step highlighted. 150–250 ms ease-out.
None under `prefers-reduced-motion`.

## Figures

Figure 1 is redrawn as inline SVG from `paper/figures/figure-data.json` (the same values the paper plotted) by
`scripts/site_figures.py`, once wide and once for phones, so it follows the theme; it is annotated only at the 1%
base rate, where the paper states the values. Figure 2 becomes two HTML timelines with the paper's event numbers and labels. The beginner diagrams
(the task, the record stack, the four look-alikes) are hand-drawn SVG, labelled in text.

## Cut

- The white-background PNG plates of the paper's figures.
- The "One-sided gains, and matching answers" section as a separate block: folded into the arrangement and
  look-alike sections where each point belongs.
- Repeated summary of the scripted control (it was told twice).
- The pill-cloud of label fields and signals at every level; it is now expert-only, each with a yes or no.
- The instructions as a collapsed footnote; they are now the fourth record, the one that answers two questions.
- Inline `<details>` of the full prompt in every summary; the instructions sheet replaces it.
- Inline styles in the HTML.
