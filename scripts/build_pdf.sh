#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

SRC="${SRC:-approach.md}"
OUT="${OUT:-approach.pdf}"

if ! command -v pandoc >/dev/null 2>&1; then
  cat >&2 <<'EOF'
pandoc not found. Install one of:
  brew install pandoc                 # macOS
  sudo apt-get install pandoc         # Debian/Ubuntu
Then re-run this script.
EOF
  exit 1
fi

ENGINE=""
if command -v xelatex >/dev/null 2>&1; then
  ENGINE="xelatex"
elif command -v lualatex >/dev/null 2>&1; then
  ENGINE="lualatex"
fi

if [ -n "$ENGINE" ]; then
  pandoc "$SRC" \
    --pdf-engine="$ENGINE" \
    --from=markdown+yaml_metadata_block \
    --variable=geometry:margin=2.2cm \
    --toc \
    -o "$OUT"
  echo "Wrote $OUT (via $ENGINE)"
  exit 0
fi

# Fallback: no LaTeX engine → produce styled HTML and tell the user to print.
HTML_OUT="${OUT%.pdf}.html"
pandoc "$SRC" \
  --from=markdown+yaml_metadata_block \
  --standalone \
  --metadata=lang:bg \
  --css=/dev/stdin \
  --toc \
  -o "$HTML_OUT" <<'CSS'
body { font-family: "DejaVu Serif", Georgia, serif; max-width: 780px; margin: 2.2cm auto; padding: 0 1cm; line-height: 1.45; color: #111; }
h1, h2, h3 { font-family: "DejaVu Sans", Helvetica, sans-serif; }
table { border-collapse: collapse; margin: 0.6em 0; }
th, td { border: 1px solid #888; padding: 4px 8px; }
code, pre { font-family: "DejaVu Sans Mono", Menlo, monospace; background: #f4f4f4; }
pre { padding: 8px 12px; overflow-x: auto; }
@media print { body { max-width: none; margin: 0; padding: 1.5cm; } }
CSS

cat >&2 <<EOF
No xelatex/lualatex found — wrote HTML instead: $HTML_OUT
To get a PDF: open the HTML in Chrome/Safari and use File → Print → Save as PDF.
Or install a LaTeX engine for direct PDF output:
  brew install --cask basictex && sudo tlmgr install xetex collection-fontsrecommended
  brew install --cask mactex-no-gui
EOF
