#!/bin/sh
# Download the whole interior-models library (12 repos, ~7.9 GB) into DEST (default ./interior-models-local)
set -e; DEST=${1:-./interior-models-local}; mkdir -p "$DEST"; cd "$DEST"
for r in interior-models interior-models-ikea interior-models-ikea-2 interior-models-ikea-3 interior-models-extra interior-models-objaverse interior-models-objaverse-2 interior-models-objaverse-3 interior-models-materials interior-models-layouts interior-models-layouts-2 interior-models-stores; do
  curl -L -o "$r.zip" "https://github.com/iandamai720-cmyk/$r/archive/refs/heads/main.zip"
  rm -rf "$r"; unzip -q "$r.zip"; mv "$r-main" "$r"; rm "$r.zip"
done
echo "Done -> $DEST"
