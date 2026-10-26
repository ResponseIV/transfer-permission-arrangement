# Predictions — step 6: more agent-made collusion, Sol board-letter, 40 cells

Registered 2026-10-23T23:11Z before the first step 6 cell; the commit time is the record.
Added to size L by the operator's decision of 2026-10-23 (plan, Deviations): the exchanges the
agents arrange themselves under a rule rested on 4 cells, all Sol. Same arm and runner as step 1
(`study_wording.py --arms board-letter`), seed 20261027, 40 tasks, one stream, after the armed runs.
Measured with the frozen tools: proposal judge (Luna p4, `text`) then a hand read of flagged
cells; crossing by the frozen label; direction from the answers; reasoning headlines.

Priors (Sol, board, letter wording): wording pilot 1 proposed and 1 crossed of 11; all earlier
letter board cells 12 proposed and 3 crossed of 40; dry run 1 proposed of 2; sprint step 1 7
proposed and 2 crossed of 20, a design named in the reasoning in 10 of 20; every crossing so far
one way; an earlier 20-cell pressure-board run crossed in 0 of 20. Refusals: none in Sol's 612
sprint requests; 6 in about 15,000 over the project.

## Claude

| # | Prediction |
|---|---|
| W1 | A disguised form proposed on a page in 9 to 18 of 40 |
| W2 | A token crosses in 1 to 5 of 40 |
| W3 | No crossing is two way (0, at most 1) |
| W4 | A design in the reasoning and no proposal on a page in 3 to 10 cells |
| W5 | Provider refusals: 0 to 2 |

## Operator

Registered in the operator's words, as shares of 40 cells; "intentionally wide since i dont have
much enough context to do more precise ones, i dont wanna throw random numbers".

| # | Question | Prediction |
|---|---|---|
| V1 | Cells with a disguised form proposed on a page | 40–80% (16–32 of 40) |
| V2 | Cells where a token crosses | 20–60% (8–24 of 40) |
| V3 | Crossings that are two way | 10–40% |
| V4 | Cells with a design in the reasoning and no proposal on a page | 5–50% (2–20 of 40) |
| V5 | Provider refusals in about 600 requests | at most 50 |
