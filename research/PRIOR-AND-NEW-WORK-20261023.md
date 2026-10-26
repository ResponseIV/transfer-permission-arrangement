# Prior and new work — source inventory

Updated 2026-10-25T14:36:24Z. The committed-code table below was generated from Git at
`c685e05`; later audit and report-build additions through v5 are listed explicitly below it.

The sprint boundary is **2026-10-23T12:00Z**. `sprint-freeze` (`a280f7a`) records the instruments before that boundary.

## Preexisting

Files present at `sprint-freeze` are preexisting. The original fixture, frozen transfer label, observer
views, signals and judge prompts were developed before the sprint. Freeze membership, not filename
suffixes, identifies preexisting data: later step-6, Sol/Qwen replication and leak folders often do
not have `-sprint` in their names. Run manifests provide the actual start times.

At this inventory, the frozen-loader directories whose event files exist at `sprint-freeze` contain
1,198 attempted / 1,174 scorable cells. This includes three prior Gemini attempts, which the
OpenAI/Qwen benchmark export excludes. These counts describe current files in those directories;
the tag remains the exact historical source of truth.

## New or changed during the sprint

The table below lists code/test changes since the freeze. First-addition times come from Git
committer timestamps; modifications to existing files are listed separately. Follow-up analyses
are exploratory or later-cell confirmation as stated in their registrations, not retroactively
part of the original 450-cell frozen-instrument test.

| Added file | First committed (UTC) |
|---|---|
| `scripts/audit_cell.py` | 2026-10-25T02:30:44Z |
| `scripts/build_release.py` | 2026-10-25T00:02:48Z |
| `scripts/export_benchmark.py` | 2026-10-24T22:58:57Z |
| `scripts/judge_openweight.py` | 2026-10-25T02:27:07Z |
| `scripts/judge_posthoc.py` | 2026-10-24T01:39:04Z |
| `scripts/modal_vllm.py` | 2026-10-25T00:43:31Z |
| `scripts/openweight_judge_report.py` | 2026-10-25T04:49:09Z |
| `scripts/page_artifact_openweight_adapter.py` | 2026-10-25T00:43:31Z |
| `scripts/plus_factors.py` | 2026-10-23T21:01:40Z |
| `scripts/posterior_table.py` | 2026-10-23T23:22:07Z |
| `scripts/proposal_read_sheet.py` | 2026-10-23T20:48:27Z |
| `scripts/replication_summary.py` | 2026-10-25T04:49:09Z |
| `scripts/sprint_extras.py` | 2026-10-23T23:51:23Z |
| `scripts/sprint_funnel.py` | 2026-10-23T20:48:27Z |
| `scripts/sprint_nesting.py` | 2026-10-24T01:34:15Z |
| `scripts/sprint_numbers.sh` | 2026-10-23T23:04:09Z |
| `scripts/sprint_protocol.py` | 2026-10-24T22:57:33Z |
| `scripts/study_agreed.py` | 2026-10-24T00:51:32Z |
| `scripts/study_leak.py` | 2026-10-24T01:39:04Z |
| `tests/test_audit_cell.py` | 2026-10-25T02:30:44Z |
| `tests/test_build_release.py` | 2026-10-25T04:49:09Z |
| `tests/test_export_benchmark.py` | 2026-10-24T22:58:57Z |
| `tests/test_openweight_judge_report.py` | 2026-10-25T04:49:09Z |
| `tests/test_page_artifact_openweight_adapter.py` | 2026-10-25T00:43:31Z |
| `tests/test_plus_factors.py` | 2026-10-23T21:01:40Z |
| `tests/test_posterior_table.py` | 2026-10-23T23:22:07Z |
| `tests/test_proposal_read_sheet.py` | 2026-10-23T20:48:27Z |
| `tests/test_replication_summary.py` | 2026-10-25T04:49:09Z |
| `tests/test_sprint_extras.py` | 2026-10-23T23:51:23Z |
| `tests/test_sprint_funnel.py` | 2026-10-23T20:48:27Z |
| `tests/test_sprint_nesting.py` | 2026-10-24T01:34:15Z |
| `tests/test_sprint_protocol.py` | 2026-10-24T22:57:33Z |
| `tests/test_study_agreed.py` | 2026-10-24T00:51:32Z |
| `tests/test_study_leak.py` | 2026-10-24T01:39:04Z |

Modified preexisting files: `scripts/exchange_bench.py`, `scripts/page_artifact_lab.py`, `tests/test_exchange_bench.py`, `tests/test_page_artifact_plan_v2.py`.

The later review and report build add `scripts/build_submission.py`, `scripts/verify_submission.py`
and `tests/test_build_submission.py`. They generate the official-template document, figures and
complete prediction ledger, and verify the saved PDF, input hashes and figure arithmetic without
model calls. The review also changes the new `audit_cell.py`, `sprint_numbers.sh`, `build_release.py`
and their relevant tests; these corrections do not change the frozen instruments.

The changes to `exchange_bench.py` allow omission of the unreleased prior-work scorer; they do not
change the frozen label or observer functions. `page_artifact_lab.py` adds the declared open-weight
route and its family-specific token cap. Judge prompts, primary labels and existing signals remain
the frozen definitions; `audit_cell.py` is a separate post-hoc tool.

## New data and documents

- Original sprint: `*-sprint*` run folders and judges; 461 attempted, 450 scorable, including one
  provider refusal among 11 operational exclusions.
- Step 6: `study-wording-sol-step6*`, seed 20261027, 40 attempted / 39 scorable; a later-cell
  follow-up to the selected Sol/letter condition.
- Registered post-hoc comparisons: Luna no-rule/leak, Sol pact/no-rule/leak, Qwen pact/no-rule/leak;
  the three leak runs live under `data/posthoc/` and are loaded explicitly.
- New registrations and analysis: `PREDICTIONS-sprint-*.md`, `SPRINT-ANALYSIS-20261023.md`, the
  protocol, manuscript versions, analysis tools and hashed numbers snapshots.
- Open-weight judge: Qwen p10 on the registered six dataset groups; incomplete coverage is reported
  explicitly until completion. It is a post-hoc cross-family judge check.
- Report v4: `research/report-versions/REPORT-DRAFT-v4.0.source.md` and its generated manuscript;
  `research/figures/writeup-v4/`; `research/numbers-writeup-20261025T051247Z/`;
  `research/report-support-20261025/`; the review evidence and report; and
  `dist/submission-draft-v4/` with PDF, DOCX, Markdown, forecast CSV and verification records.
  These are sprint writing, analysis and presentation work, not preexisting instruments or new
  model-generated episodes. Their source snapshot is identified by hashes, independently of
  subsequent live judge progress.
- The second review adds `scripts/prepare_report_inputs.py`, portable prompt excerpts and two
  unchanged event streams in `research/report-inputs-v4.1/`, the official template copy with its
  provenance, failure-detection tests for the document verifier, the v4.1 draft and figure files,
  and the three `AUDIT2-*.md` reviews. The source-release README/data card were corrected to match
  the paper's scope, and the selected license notices were added. These are analysis, review
  and reproduction work, not additional experiments.
- Draft v5 restarts the paper's structure and prose around the recorded research sequence.
  Its source, generated manuscript, `research/figures/writeup-v5.0/`, and
  `dist/submission-draft-v5.0/` use the same numerical capture and portable document inputs.
  The stage and judge tables are also checked against their saved JSON. The RETHINK notes
  identify the editorial and evidence choices. No new episodes were run for this rewrite.
- v5.1 changes the reference to Apart's question and the document spacing. It retains the
  template font and geometry and the same analysis inputs; its figures and document are saved
  separately under the v5.1 paths. This is presentation work, not additional experimental data.
- v5.2 adds the remaining safe registered Qwen judgments, a descriptive breakdown of frozen
  detector results by study condition, and a practical evidence table. It adds no task episodes
  or new experimental arms. The durable completion runner and interruption record preserve one
  possible in-flight judgment as unknown instead of replaying it. The new fact-sheet transformer
  and `research/numbers-writeup-v5.2/` record Qwen coverage and forecast scores separately from
  the earlier capture. The v5.2 source, figures, PDF/DOCX, reviews and verification records are
  new sprint analysis, writing and reproduction work.

Reproduce the inventory with `git diff --name-status sprint-freeze HEAD -- scripts tests` and
`git log --diff-filter=A --format=%cI -- <path>`. For data, compare event/manifest paths with
`git ls-tree -r --name-only sprint-freeze`, then inspect manifest timestamps. Do not classify data
by the presence or absence of `-sprint` in its name.
