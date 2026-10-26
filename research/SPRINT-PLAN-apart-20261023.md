# Sprint plan — Apart AI Collusion Research Sprint, 23–25 October 2026

Rewritten 2026-10-07 after the pilots of 6–7 October, arms and filter rule revised 2026-10-11; it replaces the plan of 6 October, which
entered on question 2.2 with a pooled accuracy as its measure (kept in git, 80f9b6f). The report
itself is the operator's own writing; this file is planning, not report text. The sprint rules
require prior work to be declared ("Undisclosed prior work can lead to disqualification"), so
the line between the two is drawn below and moves only forward: anything run before 23 October
is prior work. Stated in UTC on 2026-10-22: the sprint opens at 2026-10-23T12:00Z, and anything
started before then is prior work (`research/SPRINT-RUNBOOK-20261023.md`).

## Question

Track 2, question 2.3: what should count as convincing evidence of collusion. The page asks
which signals "separate deliberate coalitions from innocent correlation, talk without action,
and harm without agreement", and notes that antitrust answered this with plus factors while the
ML literature re-derives it.

Claim to test, in one sentence: between two agents under a rule, asking for the forbidden thing
is the norm, proposing a disguised way to pass it is a distinct and detectable stage, the
passing itself is rare, and only evidence that ties an outcome to a channel separates it from
innocent agreement.

Why not 2.2 as planned: the page frames 2.2 as an agent's words against its own actions. Our
two views are two recordings of one act. The pooled comparison did not survive either: the rule
joining both views was fitted to one model's habit, and a pooled figure reports the arm mix.

## What exists before the sprint (declared prior work)

| Item | Where | State on 2026-10-07 |
|---|---|---|
| Two-agent wiki testbed with exact read and write logging | `scripts/page_artifact_lab.py`, `scripts/study_*.py` | 13 studies |
| About 1,000 logged cells on five models with ground truth | `data/page-artifact-plan-*`, `data/study-*` | complete as listed in RESULTS |
| Labels: transfer by any route, coded transfer, own token written, exposure | `scripts/exchange_bench.py` | route-agnostic since 19e6651 |
| Rule-based detectors and the per-arm breakdown | `scripts/exchange_bench.py --by-arm` | complete |
| Model judges: Luna and Astra; prompt version 2, version 3 (question defined) with and without the answers, version 5 | `scripts/exchange_judge.py`, `data/exchange-judge-*` | run on the 243 cells under a rule |
| Evidence by kind of case, rule chosen on half and scored on half | `scripts/exchange_evidence.py` | run on 992 cells |
| Arms under a confidentiality rule: stakes, board, stated monitor, pact, wording | `scripts/study_pressure.py`, `scripts/study_pact.py`, `scripts/study_wording.py` | 243 cells |
| Disguised exchanges with no rule (positive control for detection) | `scripts/study_disguised.py` | written, pilot pending |
| Real-data slice: Wikimedia's attributed edits | `scripts/wikimedia_edits.py` | 46 revisions |

Findings in hand, to be cited as prior and not re-claimed (RESULTS sections 10 to 13): under
"never write it on any page" an agent wrote its token in 2 of 244 cells; told to break the rule,
0 of 14; a disguised form proposed in 12 of 40 Sol board cells and completed in 3, each time
one-way; two judge models that disagree on 69 of 243 cells agree on all but 8 once the question
is defined, and the stronger one then makes no error on those cells; tracing a string from a
page into an answer finds every exchange but the key-exchange, which a judge reading the pages
finds; agreement between answers alone also appears with a common source.

## What is new during the sprint

1. **The three stages at size, on new seeds, with frozen instruments:** asking, proposing a
   disguised form, passing; per model, with the rule worded by its letter and by its purpose.
2. **The evidence table on held-out cells:** case types fixed beforehand, the decision rule
   chosen on half the sprint cells and scored on the other half, for an observer with and
   without the final answers.
3. **Judges with the question defined** (what counts, what standard of proof), two models, on
   the sprint cells: whether stating the standard removes their disagreement.
4. **The write-up.**

## Design to freeze just before 23 October (not before: the operator's decision of 7 October)

- **Models:** those that produce the stages in the pilots; at least two families.
- **Arms:** the rule by its letter and by its purpose, each with stakes and the unnamed board;
  `pact-board-coded` on Luna as the positive control under a rule (8 of 8 in the pilot; Sol 0
  of 7); disguised exchanges with no rule on every model as the positive control for detection
  (`study_disguised.py`: reversed on a shared wiki, reversed on the board, shifted on the
  board); a common-source control (the archive). Dropped: `pact-plain` and `pact-board`, which
  gave 1 exchange in 29 cells; "told to break it, they do not" is cited as prior.
- **Observer views (added 2026-10-17):** every detector and rule is scored on the logged views
  and on the two wild views, `snapshot` and `anonymous-reads` (`exchange_bench.py --view`), so the
  evidence table says what an observer with only a scrape, or with reads but no reader, can
  conclude. Results on the prior cells: RESULTS section 11.
- **Judge (operator's decision of 17 October, replacing that of 8 October):** Astra on prompt
  version 10 as the sprint judge; Luna on prompt version 9 as a second, weaker judge, reported as
  such (it cannot use a log to say no). Views `text`, `both`, `full`. Both prompts were chosen on
  the 40 cells of `research/cells-judge-factors-20261017.txt` after ten versions (RESULTS section
  13): their scores there are not a test; the sprint cells are. No further prompt changes.
- **Size:** 20 cells per arm per model where a rate is claimed; the pilots showed 8 is too few.
  Operator's choice of 18 October: size L, sized to one account, in this order so the core ends
  first: (1) board-letter and board-purpose on Sol and Luna; (2) pact-board-coded on Luna; (3)
  board-letter and board-purpose on Astra, Terra and gpt-5.5; (4) shifted-board, reversed-board
  and reversed-shared on every model; (5) private-exit-archive on Sol and Luna. Cost from the
  dry run (STATE, 18 October): about 14 requests per rule or disguised cell, 10 per archive
  cell, 6 judge requests per cell. Never a second account past a usage limit: wait for the
  window or stop at the end of a step.
- **Ground truth:** `exchange_bench.label`, frozen at the freeze commit.
- **Measures, by case type and model, never pooled:** cells with a request; cells with a proposed
  disguised form (judge with a defined question, checked against a hand read of a sample);
  cells with a transfer, plain or coded; for each signal and for the frozen rule, exchanges
  found and negatives called wrongly, with exact intervals.
- **Positive control:** reported whatever it gives. If no instructed arm yields positives, that
  is stated and the detection part rests on the instructed-obfuscation cells.
- **Predictions:** in a dated file before the first sprint cell.

## Budget and timing

- Plan usage is the constraint; the weekly window resets on 10 and 17 October. Runs spread over
  the three days, at most three streams.
- Friday: freeze, register, start runs. Saturday: finish runs, judges, scoring. Sunday: figures
  and writing; submission closes 23:59 AoE.

## Risks

- **The provider's policy filter.** Four requests refused with `cyber_policy` in about 12,000,
  one each on Astra, Terra, gpt-5.5 and Sol; two in pact arms and two in `pressure-board` and
  `board-letter`, so no choice of arms removes them. A refused cell is never rerun. Rule: a run
  stops at its first refusal and may be continued once; if a study passes about one refusal per
  500 requests, stop and ask the operator. Whether repeated refusals put the account at risk is
  not known. The filter reacting to this planning is also a result and belongs in the report.
- **One model.** Code proposals come from Sol so far. If no second family shows them, the claim
  narrows to one model and says so.
- **Rare event.** One completed exchange against a rule in the whole set. The claim is about the
  stages before it and about what evidence would settle it, not about its rate.
- **Elicited setting, two agents, one task family.** Unchanged, and stated.
- **The answers.** The strongest evidence needs the final answers, which this testbed keeps
  private; a real auditor may or may not have them. Both observers are reported.
- **Prior-work share.** Most of the machinery is prior; the sprint's own contribution is the
  held-out, frozen run and the write-up. Declared as such.

## Report requirements (from the sprint page, read 2026-10-06)

PDF on the official template; abstract of 150 words or fewer; authors and affiliations;
methodology detailed enough to replicate; results with variance, seeds, baselines and the
positive control; a required "Limitations and Dual-Use / Ethical Considerations" appendix; 4 to
8 pages. "The report itself has to be your team's own writing." The dual-use appendix has real
content here: the arms show which rule wordings invite circumvention.

## Open decisions for the operator

1. Sign up, and hub or online.
2. Solo or team; no reply yet to the heads-up of 6 October.
3. Whether to make the repository public for the submission.
4. Settled 8 to 11 October: judge prompt version 3; arms and filter rule as above.

## Deviations during the sprint

- 2026-10-23: gpt-5.5 dropped from steps 3 and 4 (operator's decision). The plan route refused the
  model with HTTP 400 ("not supported when using Codex with a ChatGPT account") on its first
  request; no gpt-5.5 cell ran in the sprint. Four models remain, all from one provider.
- 2026-10-23: step 5 (common-source archive) moved before step 4 on Astra and Terra (operator's
  decision), so the "innocent correlation" case of question 2.3 is not the one a usage stop cuts.
- 2026-10-23: the sprint page now asks for an abstract of 150 to 250 words (the plan's "150 or
  fewer" above is out of date) and for code written before the sprint to be marked as preexisting
  in the README and the report.
- 2026-10-23: step 6 added (operator's decision): 40 more Sol board-letter cells, seed 20261027,
  after the armed runs, to grow the agent-made exchanges (4 cells before it). Predictions in
  `research/PREDICTIONS-sprint-step6-20261023.md`.
- 2026-10-23: the report may be written with AI help (operator's decision, replacing "the report is
  the operator's own writing"): rough drafts by either, then turns of refining and judging; the
  operator refines last and is responsible for every claim.
- 2026-10-24T05:31Z: Luna step 4 continued a second time (operator's decision, in chat), against the
  runbook's "you may continue a run once": its first continuation (after a timeout) stopped at 05:24:55Z
  on a format failure (`expected_exactly_one_action`, retrieval-note-13-shifted-board), not a
  refusal, with 21 cells never run. The failed cells are not rerun; the 21 unrun cells run into
  `study-disguised-luna-sprint-cont2`. Reported as a deviation.
