#!/bin/zsh
# Regenerates every sprint number from the data on disk; no model is called.
# Usage: zsh scripts/sprint_numbers.sh [output directory, default research/numbers-<UTC date>]
set -e
cd "$(dirname "$0")/.."
PY=${PY:-/opt/miniconda3/bin/python3}
OUT=${1:-research/numbers-$(date -u +%Y%m%dT%H%MZ)}
mkdir -p $OUT
echo "generated $(date -u +%FT%TZ) at $(git rev-parse --short HEAD)" > $OUT/README.txt
# Every input file read, with its hash, so each table names the exact snapshot it came from.
for f in data/*/events.jsonl(N) data/*/manifest.json(N) data/*/requests.jsonl(N) data/*/judgments.jsonl(N) data/*/errors*.jsonl(N) data/*/interruptions.jsonl(N) \
  data/posthoc/*/events.jsonl(N) data/posthoc/*/manifest.json(N) data/posthoc/*/requests.jsonl(N) \
  data/posthoc/*/judgments.jsonl(N) data/posthoc/*/errors*.jsonl(N) data/posthoc/*/interruptions.jsonl(N); do
  [ -f "$f" ] && shasum -a 256 "$f"
done > $OUT/inputs.sha256
for view in logged snapshot anonymous-reads; do
  $PY scripts/exchange_bench.py --by-arm --studies sprint --view $view > $OUT/bench-$view.json
done
$PY scripts/exchange_evidence.py --studies sprint > $OUT/evidence.json
$PY scripts/sprint_funnel.py > $OUT/funnel.json
$PY scripts/plus_factors.py --judge astra-p10 data/exchange-judge-astra-p10-sprint \
  --judge luna-p9 data/exchange-judge-luna-p9-sprint > $OUT/plus-factors-sprint.json
$PY scripts/plus_factors.py --studies study- page-artifact > $OUT/plus-factors-all-cells.json
$PY scripts/sprint_nesting.py $OUT/plus-factors-sprint.json $OUT/plus-factors-all-cells.json > $OUT/nesting.json
$PY scripts/posterior_table.py $OUT/plus-factors-sprint.json > $OUT/posterior-sprint.json
$PY scripts/posterior_table.py $OUT/plus-factors-all-cells.json > $OUT/posterior-all-cells.json
JUDGES=(--judge astra-p10 data/exchange-judge-astra-p10-sprint --judge luna-p9 data/exchange-judge-luna-p9-sprint)
$PY scripts/sprint_extras.py variants $JUDGES > $OUT/variants-sprint.json
$PY scripts/sprint_extras.py variants --studies study- page-artifact > $OUT/variants-all-cells.json
$PY scripts/sprint_extras.py judge-receipt $JUDGES > $OUT/judge-receipt.json
$PY scripts/sprint_extras.py board-names > $OUT/board-names.json
$PY scripts/sprint_extras.py grouped-split > $OUT/evidence-grouped-split.json
$PY scripts/sprint_extras.py matched-arms --studies luna-sprint > $OUT/matched-pact-reversed-luna.json
for check in discordance coded masked-names arm-shortcut; do
  $PY scripts/sprint_extras.py $check > $OUT/$check-sprint.json
done
$PY scripts/sprint_extras.py arm-shortcut --studies luna-sprint > $OUT/arm-shortcut-luna.json
$PY scripts/sprint_extras.py absent-ratios $JUDGES > $OUT/absent-ratios-sprint.json
$PY scripts/sprint_extras.py paired-arms --studies pact-luna-sprint pact-agreed-luna > $OUT/paired-pact-agreed-luna.json
$PY scripts/sprint_extras.py paired-arms --studies pact-sol-replication pact-agreed-sol > $OUT/paired-pact-agreed-sol.json
$PY scripts/sprint_extras.py paired-arms --studies pact-qwen-openweight pact-agreed-qwen > $OUT/paired-pact-agreed-qwen.json
$PY scripts/sprint_protocol.py $OUT > /dev/null
$PY scripts/audit_cell.py evaluate --studies sprint > $OUT/audit-sprint.json
$PY scripts/audit_cell.py evaluate --studies step6 > $OUT/audit-step6.json
$PY scripts/audit_cell.py evaluate --studies leak --data data/posthoc > $OUT/audit-leak.json
$PY scripts/sequence_by_condition.py > $OUT/sequence-by-condition.json
$PY scripts/exchange_judge.py score --by-case data/exchange-judge-astra-p10-sprint \
  data/exchange-judge-luna-p9-sprint > $OUT/judges.json
$PY scripts/openweight_judge_report.py > $OUT/openweight-judge.json
$PY scripts/transfer_subgroups.py > $OUT/transfer-subgroups.json
$PY scripts/replication_summary.py > $OUT/replication-summary.json
# Keep the registered follow-up separate from the original 450-cell sprint.
mkdir -p $OUT/step6
echo "generated $(date -u +%FT%TZ) at $(git rev-parse --short HEAD); step 6 alone (--studies step6)" > $OUT/step6/README.txt
for f in data/*step6*/events.jsonl(N) data/*step6*/manifest.json(N) data/*step6*/requests.jsonl(N) \
  data/*step6*/judgments.jsonl(N) data/*step6*/errors*.jsonl(N) data/*step6*/interruptions.jsonl(N); do
  shasum -a 256 "$f"
done > $OUT/step6/inputs.sha256
for view in logged snapshot anonymous-reads; do
  $PY scripts/exchange_bench.py --by-arm --studies step6 --view $view > $OUT/step6/bench-$view.json
done
$PY scripts/exchange_evidence.py --studies step6 > $OUT/step6/evidence.json
$PY scripts/sprint_funnel.py --studies step6 --proposals data/exchange-judge-luna-p4-step6/judgments.jsonl > $OUT/step6/funnel.json
$PY scripts/plus_factors.py --studies step6 --judge astra-p10 data/exchange-judge-astra-p10-step6 \
  --judge luna-p9 data/exchange-judge-luna-p9-step6 > $OUT/step6/plus-factors.json
$PY scripts/exchange_judge.py score --by-case data/exchange-judge-astra-p10-step6 \
  data/exchange-judge-luna-p9-step6 > $OUT/step6/judges.json
echo "wrote $(ls $OUT | wc -l | tr -d ' ') files to $OUT"
