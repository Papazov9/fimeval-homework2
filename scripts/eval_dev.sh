#!/usr/bin/env bash
# Score a predictor on the dev split using the official vendored evaluator.
# Requires the full requirements.txt installed (torch + unbabel-comet).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

MODEL="${MODEL:-dummy}"
MODEL_ID="${MODEL_ID:-}"
PRED="${PRED:-outputs/dev_${MODEL}.json}"
GOLD="${GOLD:-outputs/gold_dev.json}"
METRICS="${METRICS:-outputs/metrics_${MODEL}.json}"

python -m src.predict \
  --split dev \
  --model "$MODEL" \
  --output "$PRED" \
  ${MODEL_ID:+--model_id "$MODEL_ID"}

python -m scripts.prepare_gold --split dev --output "$GOLD"

python src/evaluation/evaluate_qa.py \
  --pred_file "$PRED" \
  --gold_file "$GOLD" \
  --out_file "$METRICS" \
  --verbose
