#!/bin/bash
# Regenera fondos, sprites y unlock.png del tema a partir de los SVG generados por gen-backgrounds.py.
# Uso: tools/build.sh   (necesita python3 y rsvg-convert)
set -euo pipefail
cd "$(dirname "$0")/.."
TMP=$(mktemp -d)
python3 tools/gen-backgrounds.py "$TMP"
for f in 01-claude-ember 02-claude-parade 03-claude-terracotta-bloom; do
  rsvg-convert -w 3840 -h 2400 "$TMP/$f.svg" -o "backgrounds/$f.png"
done
rsvg-convert -w 3840 -h 2400 "$TMP/04-claude-cream-bloom.svg" -o "light/backgrounds/01-claude-cream-bloom.png"
# Claude Light reutiliza dos fondos del tema oscuro; install.sh los enlaza.
for s in glow-terra glow-cream star-terra star-cream spark; do
  rsvg-convert "$TMP/sprite-$s.svg" -o "aura/assets/$s.png"
done
for f in "$TMP"/clawd-*.svg; do
  rsvg-convert -w 400 -h 280 "$f" -o "aura/assets/$(basename "${f%.svg}").png"
done
rsvg-convert "$TMP/unlock-dark.svg" -o unlock.png
rsvg-convert "$TMP/unlock-light.svg" -o light/unlock.png
magick backgrounds/01-claude-ember.png -resize 1280x800 preview.png
magick light/backgrounds/01-claude-cream-bloom.png -resize 1280x800 light/preview.png
rm -rf "$TMP"
echo "OK"
