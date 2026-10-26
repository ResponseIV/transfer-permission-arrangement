# Predictions — replicating the no-rule and leak findings on Sol (60 cells)

Registered 2026-10-24T22:54Z by Claude, before any of these cells exists; the commit time is the record. Operator's
decision (chat, received after 22:37Z on 2026-10-24): replicate on a second model the two post-hoc findings
that rest on Luna alone (SPRINT-ANALYSIS sections 15 and 16). Post hoc, a replication; reported as
such.

## The arms

All on Sol (`gpt-5.6-sol`), seed 20261024 (each task index carries the same tokens in every arm, as
in the Luna runs), 20 cells each, frozen label, signals and judges (Astra p10 and Luna p9 on `text`,
`both`, `full`). Nothing in any arm changes; only the model.

| Arm | Script | Output | Pairs with |
|---|---|---|---|
| `pact-board-coded` (forbidden pact) | `scripts/study_pact.py --arms pact-board-coded` | `data/study-pact-sol-replication` | the two arms below, by task |
| `reversed-agreed-board` (the pact without the rule) | `scripts/study_agreed.py` | `data/study-pact-agreed-sol` | the pact, by task |
| `leak-letter` (negligent leak) | `scripts/study_leak.py` | `data/posthoc/study-wording-leak-sol-negligent` | analysed on its own |

Measures: completed transfer (frozen label), two-way exchange (both answers carry the other's
token), the eight signals, judges per view; per signal, pact against no-rule paired by task (exact
test on discordant pairs, Fisher alongside); for the leak, offers and acceptances by the registered
agreement definition, read by hand; refusals.

## Context (read before predicting)

- Luna (sections 15 and 16): pact transfer 17 of 20, two-way 5; no-rule transfer 20, two-way 20;
  every page and log signal identical across the pairs. Leak: beta took the token in 20 of 20,
  never with an offer; every transfer signal and both judges fired.
- Sol on the pact, earlier (prior work, pilot, seed 20261015): `pact-board-coded` 0 transfers in 5
  cells; `pact-board` (plain) 1 in 6. Sol often keeps the rule even when the prompt says the agents
  agreed to break it.
- Sol under the letter rule without a pact (step 1 and step 6): offers a disguised form in about a
  third of cells, completes a transfer in 2 of 20 and 8 of 39, mostly one way.
- Sol wrote its own token on its own note in 7 of 20 purpose cells and in all 20 archive cells.
- Refusals: none in Sol's sprint requests; 6 in about 15,000 over the project.
- Cost: about 15 requests per Sol cell, so about 900 for the three arms, plus 360 judge requests.

## Claude

| # | Prediction |
|---|---|
| C1 | Sol pact: transfer in 3 to 12 of 20 (Sol resists the pact more than Luna) |
| C2 | Sol no-rule: transfer in 16 to 20 of 20 |
| C3 | Transfer differs between pact and no-rule at paired exact p < 0.05 on Sol (unlike Luna) |
| C4 | Of the six signals that need no answer (opportunity, asks for a token, asks for a code, secret-like string, string reuse, informed read), at most 1 differs between pact and no-rule at p < 0.05 |
| C5 | Sol leak: beta takes alpha's token in 8 to 18 of 20 |
| C6 | Sol leak: no offer and acceptance in any cell (at most 1) |
| C7 | Astra p10 with the log calls every completed transfer in all three arms |
| C8 | Provider refusals: 0 to 2 in the 60 cells |

## Operator

To write in your own words, or "none", before the arms run.

| # | Question | Prediction |
|---|---|---|
| D1 | Sol pact: in how many of 20 cells does a token cross? | 4 to 15 of 20 |
| D2 | Sol without the rule: in how many of 20? | 16 to 20 of 20 |
| D3 | Does the rule make a difference on Sol the traffic can see (a page or log signal), unlike Luna? | yes, unlike on Luna ("it does differ in previous run"); no rate given |
| D4 | Sol leak: in how many of 20 does beta take alpha's token? | 12 to 20 of 20 |
| D5 | Any refusals? | at most 2 |
| D6 | Free line | no offer or acceptance in the leak; taken from Claude's C6, "not my idea, i just agree on the prediction" |

Operator's lines registered 2026-10-24T23:08:26Z, given in chat after the context in this file, condensed and quoted
where marked; before any of these cells existed (none of the three output folders on disk at 2026-10-24T23:08:26Z).
