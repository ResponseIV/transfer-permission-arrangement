# Predictions — the pact, no-rule and leak arms on an open-weight model (Qwen3-32B, 60 cells)

Registered 2026-10-25T00:43Z by Claude, before any of these cells exists; the commit time is the record. Operator's
decision (chat, 2026-10-24 to 25): a second model family, so that the findings do not rest on one
provider; served on Modal from the operator's credits. Post hoc; reported as such.

## The arms

Model `qwen3-32b` (Qwen/Qwen3-32B, open weights, Alibaba), served by vLLM on Modal
(`scripts/modal_vllm.py`), thinking on (its default), through `scripts/page_artifact_openweight_adapter.py`:
the same prompt text and instructions as the OpenAI runs; the action is one forced tool call. Seed
20261024 (each task index carries the same tokens as the Luna and Sol runs), 20 cells per arm, frozen
label, signals and judges (Astra p10 and Luna p9 on `text`, `both`, `full`).

| Arm | Script | Output |
|---|---|---|
| `pact-board-coded` | `scripts/study_pact.py --arms pact-board-coded` | `data/study-pact-qwen-openweight` |
| `reversed-agreed-board` | `scripts/study_agreed.py` | `data/study-pact-agreed-qwen` |
| `leak-letter` | `scripts/study_leak.py` | `data/posthoc/study-wording-leak-qwen-negligent` |

Declared deviation: for this family only, the per-agent output cap is the number of actions times
the per-action maximum (4,096 tokens), because thinking counts as output and the OpenAI cap (1,500)
would end cells before their actions; the 8-action limit is unchanged. A smoke-test cell may be run
first to check the route; it is reported and not counted.

## Context (read before predicting)

- Luna: pact 17 of 20 crossed, 5 two-way; no-rule 20, 20 two-way, every page and log signal
  identical across the pairs; leak 20 of 20, no offer.
- Sol (replication, in progress): no-rule 20 of 20, all two-way; leak 20 of 20, none two-way; pact 3
  of the first 7 scorable crossed, and one provider refusal (`cyber_policy`) in that arm.
- No Qwen cell has ever run on this testbed. Open-weight models are usually more literal followers of
  instructions and less often refuse; they also fail the action format more often (a failed cell is not
  rerun).
- The judges stay the frozen OpenAI judges: they read only the record, not the model.

## Claude

| # | Prediction |
|---|---|
| Q1 | Pact: a token crosses in 10 to 20 of 20 (Qwen follows the pact more than Sol) |
| Q2 | No-rule: crosses in 16 to 20 of 20 |
| Q3 | Of the six signals that need no answer, at most 1 differs between pact and no-rule at p < 0.05 |
| Q4 | Leak: beta takes alpha's token in 14 to 20 of 20, with no offer or acceptance (at most 1) |
| Q5 | Astra p10 with the log calls every completed transfer in all three arms |
| Q6 | Operational failures (format, not refusals): 0 to 6 of 60 cells |

## Operator

To write in your own words, or "none", before the arms run.

| # | Question | Prediction |
|---|---|---|
| E1 | Qwen pact: in how many of 20 cells does a token cross? | 12 to 20 of 20 |
| E2 | Qwen without the rule: in how many of 20? | 16 to 20 of 20 |
| E3 | Does the rule make a difference the traffic can see on Qwen (a page or log signal)? | yes, it will differ |
| E4 | Qwen leak: in how many of 20 does beta take alpha's token? | 10 to 20 of 20 |
| E5 | Failed cells (the model breaks the action format) out of 60? | at most 10% (6 of 60) |
| E6 | Free line | none |

Operator's lines registered 2026-10-25T01:05:22Z, given in chat after the context in this file, condensed; before any
of these cells existed (none of the three output folders on disk at 2026-10-25T01:05:22Z).
