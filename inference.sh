#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ "${INFERENCE_SKIP_INSTALL:-0}" != "1" ]; then
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
fi

MODEL="${MODEL:-dummy}"
SPLIT="${SPLIT:-test}"
OUTPUT="${OUTPUT:-outputs/run.json}"
DATASET="${DATASET:-SU-FMI-AI/ImageCLEF-MR2026-OpenQA-Visual}"

python -m src.predict \
  --dataset "$DATASET" \
  --split "$SPLIT" \
  --model "$MODEL" \
  --output "$OUTPUT" \
  ${MODEL_ID:+--model_id "$MODEL_ID"} \
  ${MAX_NEW_TOKENS:+--max_new_tokens "$MAX_NEW_TOKENS"} \
  ${LIMIT:+--limit "$LIMIT"}

echo "Submission written to $OUTPUT"
