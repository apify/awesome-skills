#!/usr/bin/env bash
# uninstall_cron.sh -- remove the schedule installed by install_cron.sh.
#
# Usage: bash uninstall_cron.sh

set -euo pipefail

OS="$(uname -s)"
LABEL="com.apify.ai-visibility-tracker"

case "$OS" in
  Darwin)
    plist="$HOME/Library/LaunchAgents/$LABEL.plist"
    launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null \
      || launchctl unload "$plist" 2>/dev/null \
      || true
    if [[ -f "$plist" ]]; then
      rm "$plist"
      echo "Removed: $plist"
    else
      echo "No plist found at $plist"
    fi
    ;;
  Linux)
    if crontab -l 2>/dev/null | grep -q '# ai-visibility-tracker'; then
      crontab -l 2>/dev/null | grep -v '# ai-visibility-tracker' | crontab -
      echo "Removed crontab entry tagged '# ai-visibility-tracker'."
    else
      echo "No matching crontab entry found."
    fi
    ;;
  CYGWIN*|MINGW*|MSYS*)
    echo "On Windows, remove via Task Scheduler:"
    echo "  schtasks /Delete /TN \"AI Visibility Tracker\" /F"
    ;;
  *)
    echo "Unsupported OS: $OS" >&2; exit 2 ;;
esac
