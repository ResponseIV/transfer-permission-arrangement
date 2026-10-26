# Predictions — the after-freeze analyses, tested on cells not yet run

Written 2026-10-23 (22:09Z), before steps 4 and 5 resume (armed for the five-hour reset, about
23:30Z). The analyses in `research/SPRINT-ANALYSIS-20261023.md` (funnel, plus factors, receipt
within one edit) were built after seeing steps 1 to 3. The cells still to run — step 5, the
common-source archive on Sol and Luna (40), and step 4 on Astra and Terra plus the rest of Sol and
Luna (about 180) — have not been seen, so they test those findings. The tools are frozen at the
commit that registers this file (tag `analysis-freeze`); nothing in them changes before these
lines are scored. The commit time is the record.

Archive arm (`private-exit-archive`): private notes, an UNAVAILABLE exit, and a read-only archive
listing verified records. Prior: on all cells, every common-source cell (52 of 52) has agreeing
answers and none has uptake; dry run 2 cells.

## Claude

| # | Prediction |
|---|---|
| H1 | Archive, per model: at least 15 of 20 cells are common source (both answers drawn from the archive) |
| H2 | Answers agree in every common-source archive cell; uptake in none |
| H3 | Once step 5 is in, the sprint plus-factor table names common source as "answers agree"'s closest innocent case, with a one-sided lower bound below 1.5 |
| H4 | Astra prompt 10 with the log (`both`, `full`) calls moved in at most 2 of the 40 archive cells; on pages alone at most 4 |
| H5 | Luna prompt 9 on `full` calls moved in more archive cells than Astra does (it is shown the agreeing answers) |
| H6 | Disguised arms, all four models: uptake finds every reversed transfer and no shifted one |
| H7 | Receipt within one edit adds 0 to 2 cells beyond the frozen label in steps 4 and 5 |
| H8 | The registered evidence table on all sprint cells does not choose "answers agree" for the observer with answers |
| H9 | No emergent exchange (against a rule, uninstructed) appears in steps 4 and 5 (none of their arms carries a rule) |

## Operator

To write in your own words, or "none", before the runs resume. Prior in the paragraph above.

| # | Question | Prediction |
|---|---|---|
| U1 | Archive: in how many of 40 cells do both answers agree because both agents read the archive? | 35–40 of 40 |
| U2 | Does a judge with the log mistake those cells for an exchange? Astra, Luna | Astra: mistakes at least 20% overall, up to 80% on `text` alone. Luna: 30–70% overall ("really unsure"), could reach 80–90% on `both` |
| U3 | Disguised arms on Astra and Terra: what share crosses? | Floor about 70%, more likely around 90%; "so around T5" |
| U4 | Does "answers agree" survive as evidence once the common-source cells are in? | It reproduces the collapse: answers agree in 80–98% of the common-source cells |

Operator's lines registered in chat after the context above (the dry run's archive verdicts were
shown first), condensed and quoted where marked; "overall" in U2 is read as across the three views.
