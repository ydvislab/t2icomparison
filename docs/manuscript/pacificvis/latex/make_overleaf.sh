#!/bin/sh
# Assemble the Overleaf project (sources, VGTC class and styles, figures) and test-compile it on the server with
# pdfLaTeX + BibTeX (TinyTeX in $T2IC_DATA/tools/.TinyTeX), the same toolchain Overleaf uses.
# Usage: sh make_overleaf.sh   (writes ../pvis_overleaf.zip and ../pvis_overleaf_test.pdf; figures come from ../figures)
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
B=$(mktemp -d)
mkdir -p "$B/figures"
cp "$HERE"/main.tex "$HERE"/refs.bib "$HERE"/vgtc.cls "$HERE"/abbrv-doi*.bst "$B/"
for f in fig3_failures.pdf fig4_interface.png fig3_design.png fig4_case1.png fig5_case2.png; do cp "$HERE/../figures/$f" "$B/figures/"; done
ZIPBASE=$(cygpath -w "$HERE/../pvis_overleaf" 2>/dev/null || echo "$HERE/../pvis_overleaf")
SRCDIR=$(cygpath -w "$B" 2>/dev/null || echo "$B")
rm -f "$HERE/../pvis_overleaf.zip"
python -c "import shutil, sys; shutil.make_archive(sys.argv[1], 'zip', sys.argv[2])" "$ZIPBASE" "$SRCDIR"
ssh h200 'rm -rf /tmp/pvis && mkdir -p /tmp/pvis'
scp -q -r "$B"/* h200:/tmp/pvis/
ssh h200 'cd /tmp/pvis && export PATH=/mnt/data/yd/t2icomparison/data/tools/.TinyTeX/bin/x86_64-linux:$PATH &&
  pdflatex -interaction=nonstopmode main >/dev/null 2>&1; bibtex main >/dev/null 2>&1;
  pdflatex -interaction=nonstopmode main >/dev/null 2>&1; pdflatex -interaction=nonstopmode main >/dev/null 2>&1;
  grep -E "^! |LaTeX Warning: (Reference|Citation)|Overfull" main.log | sort -u | head -20; grep -E "^Warning" main.blg | head -5; pdfinfo main.pdf | grep Pages'
scp -q h200:/tmp/pvis/main.pdf "$HERE/../pvis_overleaf_test.pdf"
rm -rf "$B"
