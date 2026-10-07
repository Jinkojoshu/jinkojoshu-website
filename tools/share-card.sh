#!/bin/zsh
# Renders the promo images with headless Chrome:
#   zsh tools/share-card.sh         → site/assets/share.jpg  (link preview, 1200×630)
#   zsh tools/share-card.sh story   → Instagram story.jpg    (1080×1920, in the project folder, not published)
cd "${0:A:h}/.."
if [[ $1 == story ]]; then src=story-card; size=1080,1920; out="Instagram story.jpg"
else src=share-card; size=1200,630; out=site/assets/share.jpg; fi
tmp=$(mktemp -d)
perl -e "alarm 60; exec @ARGV" "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --no-first-run --disable-extensions --disable-gpu --hide-scrollbars \
  --allow-file-access-from-files --window-size=$size --virtual-time-budget=4000 \
  --user-data-dir="$tmp" --screenshot="$tmp/out.png" "file://$PWD/tools/$src.html" 2>/dev/null
sips -s format jpeg -s formatOptions 90 "$tmp/out.png" --out "$out" >/dev/null
rm -rf "$tmp"
echo "$out written"
