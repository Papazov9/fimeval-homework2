#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

RUN_JSON="${1:-outputs/run.json}"
ZIP_PATH="${2:-outputs/submission.zip}"

if [ ! -f "$RUN_JSON" ]; then
  echo "No such run.json at $RUN_JSON" >&2
  exit 1
fi

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT
cp "$RUN_JSON" "$TMPDIR/run.json"
rm -f "$ZIP_PATH"
(cd "$TMPDIR" && zip -q "$SCRIPT_DIR/$ZIP_PATH" run.json)
echo "Wrote $ZIP_PATH"
