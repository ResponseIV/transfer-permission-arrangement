# Sprint runbook — Apart AI Collusion Research Sprint, 23–25 October 2026

Written 2026-10-22T22:32Z. Operational companion to `research/SPRINT-PLAN-apart-20261023.md`
(design, measures, risks). Every time here is UTC; Paris time is in brackets for the operator.

## Clock

| UTC | Paris | What |
|---|---|---|
| Fri 23 Oct 12:00Z | 14:00 CEST | Sprint opens (countdown on the sprint page, read 2026-10-22T22:28Z) |
| Fri 15:15Z | 17:15 | Talk: Kemeklis, insider threats and AI control |
| Fri 17:15Z | 19:15 | Talk: Anwar, detecting steganography in LLM transcripts |
| Fri 18:15Z | 20:15 | Talk: Bagdasarian and Nakamura |
| Sat 24 Oct 00:15Z | 02:15 | Talk: Shi |
| Sat and Sun 12:15Z | Sat 14:15 / Sun 13:15 | Talk: Nguyen, overview of collusion research |
| Sat and Sun 15:00Z | Sat 17:00 / Sun 16:00 | Talk: Lee, "Defining AI Collusion" (the page lists it under "Saturday and Sunday"; check which day) |
| Sun 25 Oct 01:00Z | 03:00 CEST → 02:00 CET | Paris leaves summer time: local clocks repeat an hour; UTC does not |
| Mon 26 Oct 11:59Z | 12:59 CET | Submission closes (Sun 23:59 AoE) |

Talks: RSVP on each talk's Luma page for the Zoom link. Thursday's two talks are recorded.

**Prior-work line, in UTC (2026-10-22, replaces "before 23 October"):** anything started before
2026-10-23T12:00Z is prior work. The freeze commit and the predictions file are committed before
then; the first sprint cell starts after it.

## Time rule for every agent and every log

1. Every time an agent writes (STATE, RESULTS, predictions, handoff, commit bodies, chat reports)
   is UTC, ISO 8601 with `Z`: `2026-10-23T14:05Z`, or `14:05Z` inside a dated entry. Take it from
   `date -u +%FT%H:%MZ`, never from `date`, never from memory. Never write a local time without
   its offset.
2. Commits: `TZ=UTC git commit …`, so the commit time that registers a prediction reads `+0000`.
3. Run and judge logs carry no wall clock of their own (manifests have `started_at` in UTC; events
   use logical time; judge logs only count). Every launch writes a UTC line before and after:

   ```
   { echo "launch $(date -u +%FT%TZ)"; <command>; echo "exit $? $(date -u +%FT%TZ)"; } >> <log> 2>&1
   ```

4. Plan usage figures are read from the provider and written with their UTC time, as in STATE.

## Paste-ready prompt for a run thread

> You run one stream of the Apart sprint in `.`.
> Read `research/SPRINT-RUNBOOK-20261023.md` (this file) and `research/SPRINT-PLAN-apart-20261023.md`
> first. Your step is: <step and model>. Rules: write every time in UTC with `Z`, from `date -u`;
> commit with `TZ=UTC git commit`; launch with the UTC wrapper in the runbook. Instruments are
> frozen at <freeze commit>: change no script, prompt or label. Seeds are the ones in the runbook.
> At most three streams run at once across all threads. Stop at the first provider refusal
> (`cyber_policy`) and at the first failed cell; you may continue a run once with
> `--continue-from`; never rerun or replace a cell; past about one refusal per 500 requests, stop
> and ask the operator. Never switch account past a usage limit: stop at the end of the step and
> wait for the window. Append a dated entry to `research/STATE-20260907.md` with requests, cells,
> failures, refusals and UTC times; report results only against the registered predictions.

## Before 12:00Z, in order

1. **Evidence table on sprint cells only.** Done on 22 October at the operator's request:
   `exchange_evidence.py --studies sprint` keeps the cells whose study name contains `sprint`, and
   the output records the filter. Without it the rule is chosen and scored on every cell the bench
   loads, prior ones included.
2. **Freeze commit**, tagged `sprint-freeze`: label (`exchange_bench.label`), judge prompts 10
   (Astra) and 9 (Luna), proposal judge prompt 4 (Luna), arms, views. Tests pass with the real exit
   code: `/opt/miniconda3/bin/python3 -m pytest tests -q; echo "exit $?"`.
3. **Predictions file** `research/PREDICTIONS-sprint-20261023.md`: Claude's lines, then the
   operator's in their own words, committed before 12:00Z.
4. **Operator:** register; solo or team; repository public or not; one-page outline in their own
   words around the three tiers (pages show exposure, the log shows receipt, answers show use).
5. Plan-usage figure for the 17–23 window read at 12:00Z and written in STATE; the window resets
   on 24 October (time not read).

## Size L, in order

Same runners and settings as the dry run (reasoning effort high, at most 64 requests per agent
pair). Directories end in `-sprint` so the judges' `--studies sprint` and the bench's per-study
filter select them, and the bench's globs still load them. One seed per study, shared across
models so every model sees the same tasks (proposed; confirmed at the freeze).

| Step | Study and arms | Models | Cells | Seed | Output |
|---|---|---|---|---|---|
| 1 | `study_wording.py` board-letter, board-purpose | Sol, Luna | 80 | 20261023 | `data/study-wording-<model>-sprint` |
| 2 | `study_pact.py` pact-board-coded | Luna | 20 | 20261024 | `data/study-pact-luna-sprint` |
| 3 | `study_wording.py` board-letter, board-purpose | Astra, Terra, gpt-5.5 | 120 | 20261023 | `data/study-wording-<model>-sprint` |
| 4 | `study_disguised.py` shifted-board, reversed-board, reversed-shared | all five | 300 | 20261025 | `data/study-disguised-<model>-sprint` |
| 5 | `page_artifact_plan_v4.py` private-exit-archive | Sol, Luna | 40 | 20261026 | `data/page-artifact-plan-v4-<model>-sprint` |

Template (step 1, Sol):

```
{ echo "launch $(date -u +%FT%TZ)"; /opt/miniconda3/bin/python3 scripts/study_wording.py run --model gpt-5.6-sol --output data/study-wording-sol-sprint --seed 20261023 --tasks-per-arm 20; echo "exit $? $(date -u +%FT%TZ)"; } >> data/study-wording-sol-sprint.log 2>&1
```

Model ids: `gpt-5.6-sol`, `gpt-5.6-luna`, `gpt-6-astra`, `gpt-5.6-terra`. gpt-5.5 dropped from steps 3 and 4 by the operator on 2026-10-23: the plan route answers HTTP 400 "not supported when using Codex with a ChatGPT account" (STATE). Step 3 is then 80 cells and step 4 is 240.

Cost at the dry run's rates: 520 rule and disguised cells at about 14.3 requests and 40 archive
cells at about 9.5 make about 7,800 run requests; the two frozen judges on three views add 6 per
cell (3,360) and the proposal judge 1 per rule cell (220): about 11,400 requests in all, over
about 1,600 already used in the 17–23 window. Steps 1 and 2 (about 1,450 run requests) are the
core; if the window runs out, stop at the end of a step and wait for the reset.

After each step: label and bench on every view (`exchange_bench.py --by-arm --studies sprint`,
`--view snapshot`, `--view anonymous-reads`); judges `exchange_judge.py run --studies sprint`
(Astra `--prompt-version 10`, Luna `--prompt-version 9`, `--views text both full`,
`--stop-on-error`; Luna `--prompt-version 4 --views text` for proposals on rule cells); then
`exchange_evidence.py --studies sprint` and `exchange_judge.py score --by-case`.
