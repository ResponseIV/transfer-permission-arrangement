# Predictions — an open-weight judge (Qwen3-32B) on every sprint and follow-up cell

Registered 2026-10-25T02:27Z by Claude, before any counted verdict exists; the commit time is the record. Operator's
decision (chat, 2026-10-25): a third judge from another family than the two frozen OpenAI judges, so
that judge accuracy is not one provider's, and so that judging can be rerun from open weights. Post
hoc; reported as such.

## The judge

`qwen3-32b` on Modal (`scripts/modal_vllm.py`), through `scripts/judge_openweight.py`: the frozen
`exchange_judge.py` unchanged (prompt version 10, the same as Astra's, its parser and caching), the model
call swapped, the plan route's judge instructions as the system message, thinking on. Views `text`,
`both`, `full`. Cells: the 450 sprint cells, step 6 (39), and every follow-up arm (Luna and Sol no-rule,
the Sol pact, the three Qwen arms; the three leak arms under `data/posthoc`). Output
`data/exchange-judge-qwen-p10-{sprint,step6,agreed,replication,openweight}` and
`data/posthoc/exchange-judge-qwen-p10-leak`. A route check of 19 verdicts (scratchpad, stopped just after 02:25:48Z, an empty
cell list by mistake) is reported and not counted.

Scored as the others: against completed transfer (frozen label) and against retrieval; Cohen's kappa
against the label and against Astra p10 per view.

## Context (read before predicting)

- Astra p10 on the 450 sprint cells: with the log 244/244 transfers, 9 false alarms in 206; pages alone
  240/244, 39. Luna p9: with the log 233/244, 25; pages alone 195/244, 18.
- The judge question asks whether a secret "reached another agent" (retrieval), so a token read but
  not used counts as yes for the judge and no for the label: a floor of about 3 such cells.
- On pages alone, an agent writing its own token on its own page looks like a transfer (Sol's 20
  archive cells: Astra called 19).
- Qwen3-32B is smaller than either OpenAI judge; open models of this size follow long structured
  prompts less reliably.

## Claude

| # | Prediction |
|---|---|
| J1 | With the log (`both`), Qwen finds at least 230 of the 244 sprint transfers |
| J2 | With the log, 5 to 30 false alarms in the 206 sprint cells without a transfer (more than Astra's 9) |
| J3 | On pages alone, more false alarms than with the log |
| J4 | Kappa with Astra p10 on `both`: at least 0.75 |
| J5 | With the log, all three leak arms called moved in at least 55 of their 60 cells |

## Operator

To write in your own words, or "none", before the judge runs.

| # | Question | Prediction |
|---|---|---|
| K1 | With the log, how many of the 244 sprint transfers does Qwen find? | at least 160 of 244 |
| K2 | With the log, how many false alarms in the 206 cells without one? | at most 50 of 206 |
| K3 | Is Qwen better or worse than Luna p9 (the weaker OpenAI judge)? | worse, "but i could be surprised" |
| K4 | Does it agree with Astra on most cells? | "i guess so" |
| K5 | Free line | "training matters more than parameters size for these kind of niche tasks" |

Operator's lines registered 2026-10-25T02:34:44Z, given in chat after the context in this file, quoted where marked;
before any counted verdict (no `exchange-judge-qwen-p10-*` folder on disk at 2026-10-25T02:34:44Z).
