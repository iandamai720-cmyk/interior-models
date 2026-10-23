#!/bin/sh
# Download the whole interior-models library (4 repos) into DEST (default ./interior-models-local)
set -e; DEST=${1:-./interior-models-local}; mkdir -p "$DEST"; cd "$DEST"
for r in interior-models interior-models-ikea interior-models-extra interior-models-layouts; do
  curl -L -o "$r.zip" "https://github.com/iandamai720-cmyk/$r/archive/refs/heads/main.zip"
  rm -rf "$r"; unzip -q "$r.zip"; mv "$r-main" "$r"; rm "$r.zip"
done
echo "Done -> $DEST"
