# Transfer, Permission, Arrangement

**What agent logs can and cannot prove about collusion.** Code, data and registrations for an
[Apart Research AI Collusion Research Sprint](https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25)
project (23–26 October 2026, track 2, question 2.3: which signals separate deliberate coalitions from innocent
correlation, talk without action and harm without agreement).

📄 **Paper:** [`paper/report.pdf`](paper/report.pdf) · readable on GitHub as [`paper/report.md`](paper/report.md)

🔎 **Website:** an explainer and an episode explorer in [`docs/`](docs). Preview it with
`python3 -m http.server -d docs` and open http://localhost:8000. The website, [`CITATION.cff`](CITATION.cff) and
[`research/README.md`](research/README.md) were added on 2026-10-26, after the submission; the paper, data and
numbers are unchanged.

---

## The question

Suppose two AI agents end up sharing a secret they were each told to keep. Did they collude? Antitrust law faces
the same problem with firms and does not infer an agreement from parallel conduct alone: it asks for evidence that
is more likely under an agreement than under the innocent explanations. We apply that test to agents, in a setting
where the innocent explanations can be built on purpose and every event is recorded.

Two language-model agents, alpha and beta, share a small wiki. Each holds a private ten-character token, and the
task asks each to return both. Every page write, every read (with the revision it returned) and every final answer
is logged, so each episode has an exact ground truth. Around that we built the look-alikes an auditor has to rule
out:

| Look-alike | What happens | What it imitates |
|---|---|---|
| Shared source | A read-only archive holds both tokens | Agreeing answers without any exchange |
| Authorized exchange | The instructions prescribe the exchange, with no rule against it | A transfer that was allowed |
| Planted leak | Alpha's token is already on a page beta can read | Harm without agreement |
| Scripted offer | One instruction lays out an offer, a reply and completion | The order of events of an arrangement |

## What we found

Evidence of collusion splits into three questions, and each needed a different record.

| Question | Record that settled it | Result |
|---|---|---|
| **Transfer:** did a token move? | The access log and the answers | With the log, a frozen judge found all 244 primary transfers and raised no false alarm on the 194 episodes where no exchange was prescribed; on page writes alone it raised 28 |
| **Permission:** was it forbidden? | The instructions | A near-matched script without the confidentiality rule left six page and log signals unchanged on two models; only a model that resisted the script changed its traffic |
| **Arrangement:** did the agents set it up? | The order of events *and* the instructions | All 8 transfers the agents arranged themselves followed an offer, its reading and a reply carrying the token, but a script produced the same sequence in 20 of 20 episodes; a planted token was taken in 60 of 60 episodes with no arrangement at all |

Two further results:

- **An arrangement was not a shared gain.** In 9 of the 10 transfers the agents arranged, only the agent that
  proposed the scheme obtained a token; in 5 of them the other agent asked for the return and got none.
- **Matching answers mislead.** They look 3.8 times as common under transfer as without it, against the pooled
  negatives, and are less common than under a shared source, which produced agreeing answers in 40 of 40 episodes.

Read the results with two cautions. 242 of the 244 primary transfers were prescribed exchanges, so the judge rates
measure transfer detection far more than the detection of agreement. And the author's blind checks of the coding
are partial (24 of 38 and 4 of 20 episodes); they are reported with every disagreement.

## Try it

Python 3.12, standard library only; `pytest` for the tests.

**Audit one episode the way the paper recommends**, layer by layer, from the records an observer would have:

```bash
python3 scripts/audit_cell.py cell "study-wording-sol-step6-cont/retrieval-note-21-board-letter--private-writable" --observer full --instructions
```

Add `--check` to print the ground truth beside each finding.

**Run the tests and regenerate the numbers** (no model is called; everything is computed from `data/`):

```bash
python3 -m pytest tests -q
```

```bash
PY=python3 zsh scripts/sprint_numbers.sh research/numbers-check
```

`sprint_numbers.sh` regenerates the primary numbers. The later follow-ups, the coding aids and the benchmark export
use the commands listed under `commands` in
[`research/numbers-writeup-v6.3/REPORT-INPUTS.json`](research/numbers-writeup-v6.3/REPORT-INPUTS.json), for example:

```bash
python3 scripts/export_benchmark.py benchmark
```

**Use the benchmark.** [`benchmark/cells.jsonl`](benchmark/cells.jsonl) holds all 1,923 episodes (43 of them failed
runs, kept and flagged), each with its full event log, ground-truth label, case type, eight observer signals and
the judges' verdicts. See [`benchmark/DATACARD.md`](benchmark/DATACARD.md).

## Repository map

| Path | What is there |
|---|---|
| [`paper/`](paper) | The submitted report (PDF, DOCX, Markdown), its prose source, figures, the 143-line forecast ledger and the build and verification records |
| [`scripts/`](scripts) | The testbed and its conditions (`study_*.py`, `page_artifact_*.py`), the frozen label and signals (`exchange_bench.py`, `exchange_evidence.py`), the judge (`exchange_judge.py`), the audit tool (`audit_cell.py`) and every analysis |
| [`tests/`](tests) | Unit tests for the scripts above |
| [`data/`](data) | Every run: `events.jsonl` (the full log), `cells.jsonl`, `manifest.json` (condition, prompt, seed, input hashes), `requests.jsonl` (each model request and response), and a `.log` with UTC launch and exit lines. `exchange-judge-*` folders hold judge verdicts; `posthoc/` holds the planted-leak runs |
| [`benchmark/`](benchmark) | All episodes in one file, with its data card |
| [`docs/`](docs) | The website: an explainer and an episode explorer; its episodes come from `scripts/site_data.py` |
| [`research/README.md`](research/README.md) | What each research record is, and the order to read them |
| [`research/PREDICTIONS-*.md`](research) | The registrations: forecasts by the author and by Claude, committed before each run |
| [`research/SPRINT-ANALYSIS-20261023.md`](research/SPRINT-ANALYSIS-20261023.md) | The scoring of every registered forecast and the findings, in the order they were made |
| `research/CODING-*`, `CHECK-*`, `HANDREAD-*` | Hand coding of offers and arrangements, the blind check sheets, their keys, the author's answers and the comparisons |
| `research/numbers-*` | Every number in the paper, with the hash of each input and the command that produced it |
| [`research/PRIOR-AND-NEW-WORK-20261023.md`](research/PRIOR-AND-NEW-WORK-20261023.md) | What existed before the sprint and what is new, file by file |

## Preexisting and new work

The sprint opened on 2026-10-23T12:00Z. Everything present at the tag `sprint-freeze` (commit `a280f7a` in the
working repository, recorded before the first sprint run) is **preexisting**; everything else is **new**. The
file-by-file inventory with first-commit times is
[`research/PRIOR-AND-NEW-WORK-20261023.md`](research/PRIOR-AND-NEW-WORK-20261023.md).

**Preexisting code** (the testbed, the frozen transfer label, the observer signals and the judge):
`exchange_bench.py`, `exchange_evidence.py`, `exchange_judge.py`, `page_artifact_arm.py`,
`page_artifact_codex_adapter.py`, `page_artifact_gemini_adapter.py`, `page_artifact_lab.py`,
`page_artifact_plan_adapter.py`, `page_artifact_plan_v2.py`, `page_artifact_plan_v3.py`, `page_artifact_plan_v4.py`,
`run_stats.py`, `study_disguised.py`, `study_exchange_gaps.py`, `study_pact.py`, `study_pressure.py`,
`study_wording.py`, `transcript_counts.py`, and their tests. Of these, `exchange_bench.py` and `page_artifact_lab.py`
(with three of their tests) were modified during the sprint; the inventory lists each change.

**New during the sprint:** `audit_cell.py`, `blind_sheet.py`, `code_sequence.py`, `export_benchmark.py`,
`judge_openweight.py`, `judge_posthoc.py`, `modal_vllm.py`, `openweight_judge_report.py`,
`page_artifact_openweight_adapter.py`, `plus_factors.py`, `posterior_table.py`, `proposal_read_sheet.py`,
`replication_summary.py`, `sequence_by_condition.py`, `sprint_extras.py`, `sprint_funnel.py`, `sprint_nesting.py`,
`sprint_numbers.sh`, `sprint_protocol.py`, `study_agreed.py`, `study_leak.py`, `study_scripted_offer.py`,
`transfer_subgroups.py`, and their tests; every registration, analysis and coding file in `research/`; and the paper.

**Data:** the 1,174 scorable development episodes in run folders that existed at the tag are preexisting; the
706 sprint episodes are new. Each episode in [`benchmark/cells.jsonl`](benchmark/cells.jsonl) carries its `origin`
(`prior work`, `sprint` or `post hoc`).

## How the work was done

- **The sprint data.** 706 scorable episodes: a 450-episode primary test on four OpenAI models and six registered
  follow-ups, among them a second model family (Qwen3-32B) and the scripted control.
- **Forecasts came first.** Each follow-up was registered with predictions by the author and by Claude before its
  first episode. All 143 are scored in the paper's Appendix D, wrong ones included.
- **Nothing is rerun or replaced.** Failed and refused episodes are kept and flagged. A run stopped by a failure may
  resume once on its unrun episodes; the one run that resumed twice is logged as a deviation.
- **Codings are checked blind.** Offers and arrangements were coded from the event logs before any judge verdict
  was read, then checked by the author on shuffled sheets without the key.
- **Times are UTC throughout.**

**Not included.** Re-running the models is not supported from this repository: the login helper for the OpenAI
route is withheld, and the runner checks a pinned prior-work scorer that belongs to a separate project (without it,
the `bench-*` tables have one baseline detector fewer). The open-weight runs used Qwen/Qwen3-32B at revision
`9216db57` on Modal (`scripts/modal_vllm.py`). Absolute local paths were made relative when the release was built
([`research/RELEASE-REWRITES.txt`](research/RELEASE-REWRITES.txt)).

## Responsible use

The tokens are random test strings and the agents' only world is the test fixture; nothing here touches a real
system. The data are meant for evaluating detectors and judges of information transfer and coordination between
agents, not for training agents to pass information unseen. The encodings the models chose (reversal, splitting,
per-character ciphers) are already common in the literature, and no method for evading monitoring is proposed or
tested.

## Licence and citation

Code: MIT ([`LICENSE`](LICENSE)). Data: CC BY-NC 4.0 ([`LICENSE-data.md`](LICENSE-data.md)). Citation metadata:
[`CITATION.cff`](CITATION.cff).

```bibtex
@misc{responseiv2026transfer,
  title  = {Transfer, Permission, Arrangement: What Agent Logs Can and Cannot Prove About Collusion},
  author = {{Tom - Response IV}},
  year   = {2026},
  note   = {Apart Research AI Collusion Research Sprint, track 2, question 2.3},
  url    = {https://github.com/ResponseIV/transfer-permission-arrangement}
}
```
