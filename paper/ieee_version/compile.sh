#!/usr/bin/env bash
# IEEE submission build (Linux/macOS/Git Bash).
#   English: pdflatex -> bibtex -> pdflatex x2
#   Chinese: xelatex  -> bibtex -> xelatex  x2
set -u
failed=0

echo "[1/2] Building English manuscript (main.tex)..."
pdflatex -interaction=nonstopmode main.tex >/dev/null || failed=1
bibtex main >/dev/null 2>&1
pdflatex -interaction=nonstopmode main.tex >/dev/null || failed=1
pdflatex -interaction=nonstopmode main.tex >/dev/null || failed=1

echo "[2/2] Building Chinese manuscript (main_zh.tex)..."
xelatex -interaction=nonstopmode main_zh.tex >/dev/null || failed=1
bibtex main_zh >/dev/null 2>&1
xelatex -interaction=nonstopmode main_zh.tex >/dev/null || failed=1
xelatex -interaction=nonstopmode main_zh.tex >/dev/null || failed=1

for f in main main_zh; do
  if grep -qE "^!|Citation .* undefined" "$f.log" 2>/dev/null; then
    echo "[ERROR] $f.log reports errors or undefined citations"
    failed=1
  fi
  pages=$(grep -o "Output written on $f.pdf ([0-9]* pages" "$f.log" | grep -o "[0-9]*" | tail -1)
  echo "  $f.pdf -> ${pages:-?} pages"
done

rm -f ./*.aux ./*.log ./*.out ./*.blg ./*.bbl ./*.toc ./*.synctex.gz
if [ "$failed" -eq 0 ]; then
  echo "Build successful: main.pdf, main_zh.pdf"
else
  echo "Build FAILED."
fi
exit "$failed"
