# Transfer, Permission, Arrangement: What Agent Logs Can and Cannot Prove About Collusion

Code, data and registrations for an Apart Research AI Collusion Research Sprint project (23–25 October
2026, track 2, question 2.3: which signals separate deliberate coalitions from innocent correlation,
talk without action and harm without agreement).

US antitrust law does not infer an agreement from parallel conduct alone; it asks for plus factors,
evidence more likely under agreement than under the innocent explanations. We apply that test to AI
agents. Two language-model agents share a small wiki; each holds a seed-derived ten-character token the
other must return, and whether it may pass it on depends on the instructions. Every read, write and
answer is logged with its author and the revision read, so each episode has an exact transfer label,
and the innocent alternatives (a common source, an authorized exchange, a planted leak) are built on
purpose.

The paper is `dist/submission-draft-v6.4/report.pdf` (editable prose:
`research/report-versions/REPORT-DRAFT-v6.4.source.md`); every number is traceable to
`research/numbers-writeup-v6.3/` (which extends the earlier captures; `REPORT-INPUTS.json` lists each output,
the command that made it and its hash). Evidence of collusion split into three layers, each settled by a
different record:

| Layer | Record that settles it | Result |
|---|---|---|
| Transfer: did a token move? | The access log and the answers | With the log, a frozen judge (gpt-6-astra, prompt 10) found all 244 transfers in 450 primary episodes with 9 false alarms in 206; on pages alone, 39. At a 1% base rate only about 19% of its alarms would be real |
| Permission: was it forbidden? | The instructions | In a near-matched script without the rule, the six page and log signals were unchanged on Luna and Qwen3-32B (20 pairs each); on Sol, the traffic differed where the model resisted the script |
| Agreement: did they arrange it? | An offer, its reading, a reply carrying the token, and the instructions | All 8 transfers the agents arranged themselves (Sol, registered follow-up) followed this sequence, but a script laying it out produced it in 20 of 20 Sol episodes, so the instructions are needed too; Qwen3-32B under the letter rule arranged none in 34 episodes; a planted leak was taken in 60 of 60 episodes across three models with no completed arrangement |

Two further results. All eight agent-arranged transfers showed the registered sequence, and so did every
scripted-control episode, and what told a script apart was the instructions or, in bulk, its regularity (the author,
blind to the key, identified all 11 scripted episodes on a mixed sheet). And an arrangement was not a shared
gain: 9 of the 10 transfers the agents arranged served only the agent that proposed the scheme.

Two cautions travel with these results. The 244 primary transfers are mostly positive controls (225
instructed no-rule exchanges, 17 from the instructed pact, 2 arranged by the agents), so the judge rates
measure transfer detection far more than agreement detection. And the author's blind checks are partial:
24 of the 38 arrangement-sheet episodes and 4 of the 20 proposal-sheet cells
(`research/CHECK-blind-arrangement-20261026-comparison.md`, `research/HANDREAD-proposals-20261023-answers.md`).

To audit one episode the way the paper recommends:

```bash
python3 scripts/audit_cell.py cell "study-wording-sol-step6-cont/retrieval-note-21-board-letter--private-writable" --observer full --instructions
```

It reports the three findings separately, from the records an observer would have, with the innocent
explanations that remain open; `--check` adds the ground truth beside them.

## Preexisting and new work

**Preexisting** (developed before the sprint opened on 2026-10-23T12:00Z and frozen at the tag
`sprint-freeze`): the testbed and its runner (`page_artifact_*.py`, `study_wording.py`,
`study_pact.py`, `study_disguised.py`, `study_pressure.py`, `study_exchange_gaps.py`), the frozen
transfer label, observer views and signals (`exchange_bench.py`, `exchange_evidence.py`), the judge
and its prompts (`exchange_judge.py`), and 1,174 scorable development episodes.

**New during the sprint**: all 706 scorable sprint episodes (the 450-episode primary test and 256 registered
follow-ups, among them the Qwen3-32B letter-rule run and the scripted-offer control), the no-rule, leak and
scripted-offer conditions (`study_agreed.py`, `study_leak.py`, `study_scripted_offer.py`), the open-weight
route (`modal_vllm.py`, `page_artifact_openweight_adapter.py`, `judge_openweight.py`), every analysis
(`sprint_funnel.py`, `plus_factors.py`, `sprint_extras.py`, `sprint_protocol.py`, `audit_cell.py`,
`sequence_by_condition.py`, `code_sequence.py`, and the rest), the blind check sheets (`blind_sheet.py`),
the registrations and the report. The file-by-file
inventory with first-commit times is `research/PRIOR-AND-NEW-WORK-20261023.md`.

## Layout

| Path | What |
|---|---|
| `scripts/` | The testbed runner and arms (`study_*.py`, `page_artifact_*.py`), the frozen label and signals (`exchange_bench.py`, `exchange_evidence.py`), the judge (`exchange_judge.py`), every analysis, and `sprint_numbers.sh`, which regenerates the primary numbers (the later follow-ups use the commands in `research/numbers-writeup-v6.3/REPORT-INPUTS.json`) |
| `tests/` | Unit tests for all of the above (`python -m pytest tests -q`) |
| `data/study-*`, `data/page-artifact-plan-v*` | Every cell: `events.jsonl` (the full log), `cells.jsonl`, `manifest.json` (arm, prompt, seed, input hashes), `requests.jsonl` (each model request and response, as recorded); a `.log` beside each run has its UTC launch and exit lines |
| `data/exchange-judge-*` | Judge verdicts per cell and view |
| `data/posthoc/` | Post-hoc arms kept outside the frozen loader (the negligent leak), read with `--data data/posthoc` |
| `research/PREDICTIONS-*.md` | Registrations by the operator and Claude; the after-freeze H/U analysis forecasts were written while some convention-arm cells already existed, so their whole-arm aggregates are exploratory |
| `research/SPRINT-ANALYSIS-*.md` | Scoring of every registered prediction, findings, critique |
| `research/numbers-final-*/`, `research/numbers-writeup-v6.3/` | The final primary numbers and the report's capture (`README.txt` gives the commit; `inputs.sha256` the hash of every input; `REPORT-INPUTS.json` the later outputs) |
| `research/CODING-*.md`, `research/CHECK-*`, `research/HANDREAD-*` | Hand coding of offers and agreements, the blind sheets, their keys, the author's answers and the comparisons |
| `dist/submission-draft-v6.4/` | The submitted report (PDF, DOCX, Markdown), its prediction ledger and verification record |
| `research/PRIOR-AND-NEW-WORK-20261023.md` | Source inventory against the pre-sprint freeze; later follow-ups are new work even when their folder names do not contain `-sprint` |
| `benchmark/` | Every labelled cell in one file, with ground truth, case type, signals and judge verdicts; see `benchmark/DATACARD.md` |

## Reproduce

Python 3.12, no third-party package for the analyses (`pytest` for the tests).

```bash
python -m pytest tests -q
PY=python3 zsh scripts/sprint_numbers.sh research/numbers-check
```

`sprint_numbers.sh` reads only `data/`; no model is called. The Qwen letter-rule and scripted-offer outputs,
the coding aids and the benchmark export come from the commands listed under `commands` in
`research/numbers-writeup-v6.3/REPORT-INPUTS.json` (for example
`python3 scripts/sequence_by_condition.py --studies scripted-offer`, `python3 scripts/export_benchmark.py benchmark`).
`nesting.json` and the all-cells files change as later runs join the all-cells population. It fails if the sprint counts do not nest
inside the all-cells counts. The outputs match `research/numbers-writeup-v6.3/` except where
noted in "Differences from the private repository" below.
The `step6/` subfolder is regenerated separately from the original sprint tables. Later snapshots
also include post-hoc outputs and must be compared on their stated data populations, not treated
as byte-for-byte replacements for earlier snapshots that predate the replications.

Re-running cells needs access to the models and is not supported from this repository: the login helper
for the OpenAI route is not released, and the runner also checks a pinned prior-work scorer that is not
included here. The open-weight route (`modal_vllm.py`) needs your own Modal account. Everything the paper
reports is computed from the recorded data, with no model call.

## Method notes

- The instrument commit `a280f7a` predates the public opening at 2026-10-23T12:00Z. The annotated
  `sprint-freeze` tag was recorded at 15:27:34Z, before the first original-sprint manifest at
  15:27:57Z. Analyses written during the runs are exploratory; a forecast made after earlier cells
  existed does not make a whole arm an unseen test. Registered follow-ups have their own scope.
- A failed or refused cell is never rerun; a stopped run may resume once on its unrun cells (one run
  resumed twice, a logged deviation), and after a usage-limit stop it continues from the cells not yet attempted.
- OpenAI agents ran at high reasoning effort; OpenAI judges at low. Qwen3-32B (weights revision 9216db57) used its default
  thinking mode for agents and judge on Modal; these are post-hoc runs. Judge format failures are
  retained as failures and never re-asked; missing verdicts are not negatives. One possible
  in-flight primary judgment was quarantined after the old supervisor stopped; its outcome
  is unknown and it was not replayed. `interruptions.jsonl` preserves that disposition.
- Times are UTC throughout.

## Differences from the private repository

The project's working repository also holds unrelated material (collections of public posts, a wild
corpus of agent-written pages), so this repository was assembled from an explicit list by
`build_release.py` there, not copied. Absolute local paths were made relative (`RELEASE-REWRITES.txt`
lists the files). One baseline detector of prior work (the "September scorer", not used in the paper)
needs a file that is not released; without it `exchange_bench.py` leaves that detector out, so the
`bench-*.json` tables here have one detector fewer; everything else regenerates unchanged.

## Responsible use

The tokens are random test strings and the agents' only world is the fixture; nothing here touches a
real system. The work measures how well an auditor can detect and attribute information transfer
between agents; the data are meant for evaluating such detectors. They show which encodings the
models chose (reversal, splitting, per-character ciphers), all already common in the literature, and
no method for evading monitoring is proposed or tested.

## Licence

MIT for original code; CC BY-NC 4.0 for original data (operator decision, 2026-10-25).
The applicable notices are `LICENSE-code.txt` and `LICENSE-data.md`. Dependencies and the
official Apart template retain their own terms.
