#!/bin/zsh
# Zip the labelling page and its images so an annotator can label on their own computer (no server needed).
# Usage: ./package.sh   ->  $T2IC_DATA/annotation_package.zip
set -e
D=${T2IC_DATA:-~/va4ext}
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$D/annotation_aspects"
cp "$HERE/ANNOTATOR_GUIDE.md" GUIDE_zh.md
rm -f "$D/annotation_package.zip"
zip -qr "$D/annotation_package.zip" label_aspects.html GUIDE_zh.md img
rm GUIDE_zh.md
echo "$D/annotation_package.zip ($(du -h "$D/annotation_package.zip" | cut -f1))"
