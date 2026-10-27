#!/bin/sh
# Assemble the Overleaf project (sources, VGTC class and style, figures) and test-compile it with Tectonic on the server.
# Usage: sh make_overleaf.sh   (writes ../pvis_overleaf.zip and ../pvis_overleaf_test.pdf; figures come from ../figures)
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
B=$(mktemp -d)
mkdir -p "$B/figures"
cp "$HERE"/main.tex "$HERE"/refs.bib "$HERE"/vgtc.cls "$HERE"/abbrv-doi.bst "$HERE"/abbrv-doi-hyperref.bst "$B/"
for f in fig3_failures.pdf fig4_interface.png fig3_design.png fig4_case1.png fig5_case2.png; do cp "$HERE/../figures/$f" "$B/figures/"; done
ZIPBASE=$(cygpath -w "$HERE/../pvis_overleaf" 2>/dev/null || echo "$HERE/../pvis_overleaf")
SRCDIR=$(cygpath -w "$B" 2>/dev/null || echo "$B")
rm -f "$HERE/../pvis_overleaf.zip"
python -c "import shutil, sys; shutil.make_archive(sys.argv[1], 'zip', sys.argv[2])" "$ZIPBASE" "$SRCDIR"
ssh h200 'rm -rf /tmp/pvis && mkdir -p /tmp/pvis'
scp -q -r "$B"/* h200:/tmp/pvis/
ssh h200 'cd /tmp/pvis && /mnt/data/yd/t2icomparison/data/tools/tectonic -X compile --keep-logs main.tex 2>&1 | grep -iE "error|warning: .*(undefined|overfull)|^note: writing" | head -40; python3 -c "import re;s=open(\"main.log\").read();print(\"pages:\",re.findall(r\"Output written on main.pdf \((\d+) page\",s))"'
scp -q h200:/tmp/pvis/main.pdf "$HERE/../pvis_overleaf_test.pdf"
rm -rf "$B"
