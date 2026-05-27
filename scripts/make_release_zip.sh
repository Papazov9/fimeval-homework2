#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

OUT="${1:-code.zip}"

REQUIRED=(
  inference.sh
  requirements.txt
  README.md
  approach.pdf
  src
  scripts
  outputs/run.json
  outputs/metrics_qwen_vl.json
  outputs/dev_qwen_vl.json
  outputs/gold_dev.json
)

missing=0
for path in "${REQUIRED[@]}"; do
  if [ ! -e "$path" ]; then
    echo "missing: $path" >&2
    missing=1
  fi
done
if [ "$missing" = "1" ]; then
  echo "Refusing to build $OUT — see missing files above." >&2
  exit 1
fi

rm -f "$OUT"
zip -r "$OUT" \
  inference.sh requirements.txt README.md approach.pdf \
  src scripts \
  outputs/run.json outputs/metrics_qwen_vl.json \
  outputs/dev_qwen_vl.json outputs/gold_dev.json \
  -x '*/__pycache__/*' '*.pyc' '.DS_Store' '*/.DS_Store'

echo "Wrote $OUT"
unzip -l "$OUT" | tail -20
