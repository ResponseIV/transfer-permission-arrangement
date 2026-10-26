# Predictions — sprint runs, size L, seeds 20261023 to 20261026

Draft written 2026-10-22T22:32Z. Registered **before the first sprint cell** (after
2026-10-23T12:00Z); the commit time of each section is its record, in UTC. Design, arms and
measures: `research/SPRINT-PLAN-apart-20261023.md`; steps, seeds and outputs:
`research/SPRINT-RUNBOOK-20261023.md`. 20 cells per arm per model; every count is per arm and
model, never pooled.

Baselines from prior work (RESULTS sections 10 to 13, STATE 18 October):

| Measure | Prior |
|---|---|
| Sol proposes a disguised form, board under the letter wording | 12 of 40 started cells across studies; 1 of 11 in the wording study; 1 of 2 in the dry run |
| Sol proposes one under the purpose wording | 0 of 11 |
| Other models propose one under a rule | none on a page (Luna 0 of 64 in the reasoning too) |
| A token crosses under a rule, uninstructed | 3 in Sol's 40 board cells; none on other models |
| An agent writes its own token on its own note, purpose wording | Sol 4 of 11, gpt-5.5 1 of 7, Terra 0 of 12 |
| Luna, `pact-board-coded` (positive control under a rule) | 8 of 8 crossed |
| Disguised arms, no rule (positive control for detection) | reversed 4 of 4 on every model; shifted-board Luna 2 of 4, Terra 3 of 4, others 4 of 4 |
| Tracing a string from a page into an answer | finds every reversed transfer, no shifted one |
| Provider refusals (`cyber_policy`) | 5 in about 12,200 requests, all in rule or pact arms |
| Astra, prompt 10 | right on every count of the 40 selection cells; on pages alone 3 to 5 false alarms in 100 empty board cells (own token on own page) |
| Luna, prompt 9 | 17 of 24 right in the dry run; cannot use the log to say no |

## Claude

| # | Prediction |
|---|---|
| S1 | Sol, board-letter: a disguised form proposed in 2 to 7 of 20 cells; a token crosses in 0 to 2 |
| S2 | Sol, board-purpose: proposed in 0 to 3; crosses in 0 or 1; an agent writes its own token on its own note in 4 to 12 |
| S3 | Luna, Astra, Terra and gpt-5.5, both wordings: proposed in 0 or 1 cells per arm; no token crosses |
| S4 | Luna, pact-board-coded: a token crosses in 16 to 20 of 20 |
| S5 | Disguised arms: reversed-shared and reversed-board cross in 19 or 20 per model; shifted-board in 17 to 20 on Sol, Astra and gpt-5.5, 12 to 20 on Terra, 8 to 16 on Luna |
| S6 | Tracing into answers finds every reversed transfer and none of the shifted ones |
| S7 | Provider refusals: 1 to 6 over about 7,800 run requests, all in rule or pact arms; none in judge requests or disguised arms |
| S8 | Failed or cut-short cells: at most 3 in any step |
| S9 | Astra prompt 10 with the log (`both`, `full`): misses at most 1 transfer per step and calls at most 1 empty cell moved; on pages alone (`text`) it calls moved in 2 to 8 of every 100 empty board cells |
| S10 | Luna prompt 9 is below Astra on every view that has the log |
| S11 | Archive arm: answers agree with no transfer in most cells (at least 12 of 20 per model), and no judge with the log calls one of them moved |

## Operator

To fill in your own words, or write "none", before the first sprint cell. Each line has its prior
in the table above.

| # | Question | Prediction |
|---|---|---|
| T1 | Sol, board-letter: in how many of 20 cells does an agent propose a disguised form, and in how many does a token cross? | Proposed 5–10 of 20. "crossed 4–6, wouldn't be surprised by 0–8; scored on 4–6" (one way) |
| T2 | Sol, board-purpose: same two counts | Proposed 0–3 of 20; crossed 0–3 of 20 |
| T3 | Does any model other than Sol propose a disguised form under a rule? | At most 1 per model on a page; traces in the reasoning on Terra and gpt-5.5, no action |
| T4 | Luna, pact-board-coded: tokens crossed of 20 | 15–20 of 20, that is 75–100% of scorable cells |
| T5 | Disguised arms: which model and arm, if any, falls well below 20 of 20? | At least 16 of 20 on every model and arm, except Luna, which may fall below |
| T6 | Provider refusals over the whole run | 2–3 new ones (not counting the 5 earlier), all in rule or pact arms |
| T7 | Astra prompt 10 on the sprint cells: as right as on the 40 selection cells, or worse? | Right on 60–100% of cells on the views with the log (`both`, `full`); on pages alone 3–5 false "moved" calls per 100 empty cells |
| T8 | Does the step order finish within the plan usage, or stop at a limit, and at which step? | All five steps finish, with the resets |

Registered 2026-10-23 in the operator's words (T1 quoted, the rest condensed from chat and
confirmed there), after the sprint opened and before the first sprint cell.
