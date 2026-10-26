# Audit execution record

**26 October 2026, Europe/Paris.** Baseline `site` / `769913f6c93f4fe46112f3354ad7cbe34484e745`; working tree was clean. Existing server at `http://127.0.0.1:4173/` responded, so no replacement was launched. Only this audit folder is intended for the commit; `.agents/LEDGER.md` is a local ignored continuity note.

## Commands and source checks

Run from `/Users/tom/AutomationStack/projects/transfer-permission-arrangement`:

```sh
git status --short
git branch --show-current
git rev-parse HEAD
python3 -m unittest discover -s tests -p 'test_site*.py' -q
node --check docs/assets/site.js
node --check docs/assets/explorer.js
shasum -a 256 paper/report.pdf docs/assets/report.pdf
git show submission:paper/report.md | shasum -a 256
shasum -a 256 paper/report.md
```

Results: **28 tests passed**, both syntax checks exited zero. Both PDFs: `7248f336a6c14a3537180dd6524959ea14db1318d4effa8970689ac4179c92a4`. Both Markdown reports: `cac86f14b4144464baca15c3df42f4f794a0652d6504821425769e7e69d7b24c`.

Scientific spot checks: primary 244 / prescribed 242; 194 clean negatives versus 12 failed prescribed exchanges; script 20/20; planted leaks 60/60; Sol follow-up 39 scorable of 40, eight transfers; partial human checks 24/38 and 4/20. Checked source excerpt/attribution in `sol-scripted-01` and scope at paper Appendix A. Full scientific-review notes were integrated into AUDIT.md; this audit does not independently validate experiment execution.

Approximate text lengths using existing `tests/site_text.py` `units()` extraction: beginner 1,668, amateur 3,003, expert 4,564 words. Includes headings/captions; excludes code. Not a measured reading time.

## Rendered checks

Used the Browser skill's in-app browser. Viewport values below were explicitly set; measurements use actual DOM bounding boxes. Native screenshots are viewport captures, not design mockups. When a capture caught an intermediate state, it was replaced or omitted. Reference screenshots document those pages on the access date, not their intended appearance on all devices.

| Viewport | Flows inspected | Observed result / limits |
| --- | --- | --- |
| 1440×1000 | Opening pages/read/instruction reveal; first story continuation; Transfer; all depths; hidden Methods arrival; paper handoff | Clear cover and reading measure. Instruction reveal verified by selected record and finding text. `beginner#methods` selects expert and reveals it. Paper bytes checked; browser PDF rendering not evaluated. |
| 1440×1000 | Direct Transfer arrival, then visible Investigation label | Reproduced twice: heading y=182.54→4220.77; scrollY=2368.5→1343. Remained displaced on a later call. F1. |
| 1440×1000 | Explorer all eight cases through Show all; three pair choices and reveals; all record types; compare→single; browser Back/Forward | No broken case rendering found. Unknown verdicts remain “No verdict.” Case/pair URL changes and tested history work. Changing record/step then reloading resets them. |
| 1440×1000 | Keyboard Tab to depth radio, ArrowRight; desktop accessibility tree | Focus outline visible; native arrow navigation selects next depth and URL updates. Pane record/truth labels absent from tree at desktop. No screen reader used. |
| 768×1024 | Opening, Transfer table/measure, masthead, keyboard focus | No page-wide overflow observed; masthead remains one line; contents collapses rather than occupying rail. Body column about 672px. Not every comparison/record combination tested at this size. |
| 375×812 | Opening and exhibit; explorer arrival; steps 2, 3 and 9; long offer; comparison; chart; dark theme | No page-wide overflow observed on these flows. Fixed stepper kept tested current events above it. Comparison stacks A then B. Small depth labels are readable but visually slight. This is viewport testing, not touch hardware testing. |
| 320×740 | Investigation base-rate chapter and narrow reflow | 321px document scroll width: about 1px excess at depth labels. Not treated as a major overflow defect. Dense caption and numerical explanation remain a comprehension issue. Not equivalent to actual zoom/text enlargement. |

Case inventory exercised: `sol-21`, `sol-19`, `luna-leak-01`, `sol-scripted-01`, `sol-archive-02`, `luna-pact-02`, `luna-norule-02`, `qwen-letter-37`. Comparisons: `arranged-scripted`, `arranged-leak`, `forbidden-permitted`.

Share-state reproduction: at `explorer.html?level=beginner#single/sol-21`, **+ Instructions**, **Step 3 of 9**; reload same URL → **+ Access log**, **Step 1 of 9**. The record/step are intentionally held in memory in current code; the audit recommends a shareable representation.

The reading-depth choice persisted across navigation; explicit query values selected the requested depth. No browser storage was inspected. A browser tool's attempt to click an invisible 1px radio input hit an adjacent input; visible-label clicks and actual keyboard navigation worked. That automation targeting problem was **not** reported as a website bug.

## Source-inspected, not live-verified

- No-JS: static essentials article and explicit script explanation; explorer supplies raw JSON link. No actual browser session with scripting disabled.
- Print: controls hidden; `.event.ahead` remains hidden. Partial-case printing is a source-derived risk, not a captured print failure.
- Reduced motion: global disabling rule exists; no continuous animation found. No media-preference emulation.
- Loading/failure: fetch rejection/error path and lack of pending indicator inspected; no throttled or failed-network run.
- Performance/portability: no build/runtime CDN; relative assets and self-hosted fonts. Episode JSON about 92KB on disk; four font files total about 360KB; shared/explorer JS about 8KB/24KB by rounded disk usage. No measured CWV, CPU profile or cold-network timings. Subpath hosting inferred from relative paths and existing checks, not a second deployed mount.
- Semantics/contrast/links: HTML/source and existing checks reviewed. This is not comprehensive WCAG certification. Actual text zoom, screen-reader combinations, touch-device safe areas, browser-family compatibility and print remain open.

## Reference interactions

Anthropic: opening, cookie rejection, caveats navigation and settled chapter state. Swarmchasers: opening and expanded contents. Distill: cognitive-load section and Toggle Notation. Works in Progress: opening/reading composition, cookie denial. Pudding: explode switch and cut slider 10→9, visible pieces and 37.3%→48.3% feedback. No form submission or account interaction.

See [REFERENCES.md](REFERENCES.md) for direct primary links and design implications. External examples were reviewed on desktop only and were not themselves audited for conformance.

## Evidence and closeout

The findings link directly to relevant images and the desktop accessibility-tree capture in `evidence/`. Extra intermediate/duplicate captures and working review notes were removed after integration. No implementation or research files were changed. Before commit: check every Markdown evidence link, inspect staged paths and diff, and verify `docs/`, `paper/`, `tests/` remain unchanged from the baseline. Do not push or publish.
