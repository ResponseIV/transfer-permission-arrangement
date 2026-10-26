# Research records

The plan, registrations, analysis log, hand codings, blind checks and numbers behind the paper
([`../paper/report.md`](../paper/report.md)). Times in file names and inside files are UTC. Each file's
commit time in the working repository was its record; this release flattens that history into one
commit, so the times written inside each file are the ones to read.

## Reading order

1. **Before the sprint: design.**
   [`SPRINT-PLAN-apart-20261023.md`](SPRINT-PLAN-apart-20261023.md) (arms, measures, risks) and
   [`SPRINT-RUNBOOK-20261023.md`](SPRINT-RUNBOOK-20261023.md) (how each step was run).
   [`PRIOR-AND-NEW-WORK-20261023.md`](PRIOR-AND-NEW-WORK-20261023.md) draws the line between preexisting and
   new work, file by file.
2. **Registrations**, each written before the first episode of its run, in this order:

   | File | Run it registers |
   |---|---|
   | [`PREDICTIONS-sprint-20261023.md`](PREDICTIONS-sprint-20261023.md) | The 450-episode primary test |
   | [`PREDICTIONS-sprint-heldout-analyses-20261023.md`](PREDICTIONS-sprint-heldout-analyses-20261023.md) | The after-freeze analyses, on episodes not yet run |
   | [`PREDICTIONS-sprint-step6-20261023.md`](PREDICTIONS-sprint-step6-20261023.md) | The 40-episode Sol follow-up (step 6) |
   | [`PREDICTIONS-sprint-agreement-20261024.md`](PREDICTIONS-sprint-agreement-20261024.md) | The event definition of an arrangement, before step 6 |
   | [`PREDICTIONS-sprint-authorized-scripted-20261024.md`](PREDICTIONS-sprint-authorized-scripted-20261024.md) | The pact without the rule (Luna) |
   | [`PREDICTIONS-sprint-negligent-leak-20261024.md`](PREDICTIONS-sprint-negligent-leak-20261024.md) | The planted leak (Luna) |
   | [`PREDICTIONS-sprint-replication-sol-20261024.md`](PREDICTIONS-sprint-replication-sol-20261024.md) | No-rule and leak replicated on Sol |
   | [`PREDICTIONS-sprint-openweight-20261025.md`](PREDICTIONS-sprint-openweight-20261025.md) | Pact, no-rule and leak on Qwen3-32B |
   | [`PREDICTIONS-sprint-openweight-judge-20261025.md`](PREDICTIONS-sprint-openweight-judge-20261025.md) | Qwen3-32B as a third judge |
   | [`PREDICTIONS-sprint-qwen-letter-20261025.md`](PREDICTIONS-sprint-qwen-letter-20261025.md) | The letter rule on Qwen3-32B |
   | [`PREDICTIONS-sprint-scripted-offer-20261026.md`](PREDICTIONS-sprint-scripted-offer-20261026.md) | The scripted-offer control |

3. **Analysis log.** [`SPRINT-ANALYSIS-20261023.md`](SPRINT-ANALYSIS-20261023.md): findings in the order they
   were made, with the scoring of each registered forecast. Everything not scoring a registration is
   exploratory. [`AUDIT-codex-20261023.md`](AUDIT-codex-20261023.md) is an independent adversarial audit made
   during the sprint, kept as written; [`PROTOCOL-evidence-layers-20261024.md`](PROTOCOL-evidence-layers-20261024.md)
   summarizes what each observer record supports, with three example episodes.
4. **Hand codings** from the event logs; each file says when it was made and which judge verdicts had
   been seen:
   [`CODING-step6-agreement-20261024.md`](CODING-step6-agreement-20261024.md) (the Sol follow-up, cell by cell),
   [`CODING-qwen-letter-20261026.md`](CODING-qwen-letter-20261026.md) and
   [`CODING-scripted-offer-20261026.md`](CODING-scripted-offer-20261026.md).
5. **Blind checks by the author.** Each has a sheet, the author's answers, a key opened only afterwards, and
   for the arrangement check a comparison listing every disagreement:
   - proposals: [`HANDREAD-proposals-20261023.md`](HANDREAD-proposals-20261023.md),
     [`-answers.md`](HANDREAD-proposals-20261023-answers.md), [`-key.json`](HANDREAD-proposals-20261023-key.json)
     (4 of 20 episodes read);
   - arrangements: [`CHECK-blind-arrangement-20261026.md`](CHECK-blind-arrangement-20261026.md),
     [`-answers.md`](CHECK-blind-arrangement-20261026-answers.md),
     [`-key.json`](CHECK-blind-arrangement-20261026-key.json),
     [`-comparison.md`](CHECK-blind-arrangement-20261026-comparison.md) (24 of 38 episodes read).
6. **Numbers.** [`numbers-writeup-v6.3/`](numbers-writeup-v6.3) holds every number in the paper as generated
   output, with the hash of each input (`inputs.sha256`) and the command that produced each file
   (`REPORT-INPUTS.json`, under `commands`).
7. **Release.** [`RELEASE-REWRITES.txt`](RELEASE-REWRITES.txt) lists the files whose absolute local paths were
   made relative for this release.

## Files cited but not released

The notes cite interim outputs and drafts by path (earlier `numbers-final-*`, `numbers-interim-*` and
`numbers-writeup-*` folders, `FUNNEL-*`, `PLUS-FACTORS-*`, `POSTERIOR-*` and `EVIDENCE-*` files, report drafts).
They were superseded and are not in this release; the paper's numbers all come from `numbers-writeup-v6.3/`.
