#!/bin/sh
# Refresh oil.json from live sources and push to rajagull/market-data.
# Runs every 5 minutes via launchd (com.rajagull.oilfeed) on the Mac mini.
cd "$HOME/market-data" || exit 1
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
python3 scripts/fetch_oil.py >> "$HOME/market-data/update.log" 2>&1 || exit 1
git pull --rebase -q origin main >> "$HOME/market-data/update.log" 2>&1 || exit 1
git add oil.json
if git diff --cached --quiet; then
  echo "$(date -u +%FT%TZ) no change" >> "$HOME/market-data/update.log"
else
  git commit -q -m "Update oil prices"
  git push -q origin main >> "$HOME/market-data/update.log" 2>&1
  echo "$(date -u +%FT%TZ) pushed" >> "$HOME/market-data/update.log"
fi
