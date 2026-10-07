#!/bin/zsh
# Renders tools/share-card.html to site/assets/share.jpg (the link-preview image).
cd "${0:A:h}/.."
tmp=$(mktemp -d)
perl -e "alarm 60; exec @ARGV" "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --no-first-run --disable-extensions --disable-gpu --hide-scrollbars \
  --allow-file-access-from-files --window-size=1200,630 --virtual-time-budget=4000 \
  --user-data-dir="$tmp" --screenshot="$tmp/share.png" "file://$PWD/tools/share-card.html" 2>/dev/null
sips -s format jpeg -s formatOptions 88 "$tmp/share.png" --out site/assets/share.jpg >/dev/null
rm -rf "$tmp"
echo "site/assets/share.jpg written"
