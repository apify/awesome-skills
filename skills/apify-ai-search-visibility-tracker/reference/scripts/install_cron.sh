#!/usr/bin/env bash
# install_cron.sh -- install a recurring schedule for run_snapshot.py.
#
# Detects OS and installs the appropriate scheduler entry:
#   macOS  -> ~/Library/LaunchAgents/com.apify.ai-visibility-tracker.plist
#   Linux  -> crontab line tagged "# ai-visibility-tracker"
#   Windows -> prints schtasks instructions (no auto-install)
#
# The runner reads APIFY_TOKEN from a `.env` file next to `config.json`,
# so this script does NOT embed any credentials in the schedule entry.
#
# Usage:
#   bash install_cron.sh [--cadence daily|weekly|monthly] \
#                        [--hour 0-23] \
#                        [--config /path/to/config.json] \
#                        [--yes]

set -euo pipefail

CADENCE="daily"
HOUR="9"
CONFIG=""
YES="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cadence)  CADENCE="$2"; shift 2 ;;
    --hour)     HOUR="$2";    shift 2 ;;
    --config)   CONFIG="$2";  shift 2 ;;
    --yes|-y)   YES="1";      shift ;;
    -h|--help)
      echo "Usage: $0 [--cadence daily|weekly|monthly] [--hour 0-23] [--config /path/to/config.json] [--yes]"
      exit 0 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

case "$CADENCE" in
  daily|weekly|monthly) ;;
  *) echo "Error: --cadence must be daily, weekly, or monthly" >&2; exit 2 ;;
esac

if ! [[ "$HOUR" =~ ^[0-9]+$ ]] || (( HOUR < 0 || HOUR > 23 )); then
  echo "Error: --hour must be 0-23" >&2; exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNNER="$SCRIPT_DIR/run_snapshot.py"
if [[ ! -f "$RUNNER" ]]; then
  echo "Error: run_snapshot.py not found at $RUNNER" >&2; exit 2
fi

# Resolve config.json path (default: $PWD/config.json).
if [[ -z "$CONFIG" ]]; then
  CONFIG="$PWD/config.json"
fi
if [[ ! -f "$CONFIG" ]]; then
  echo "Error: config.json not found at $CONFIG. Create it first (see SKILL.md Step 3)." >&2
  exit 2
fi
CONFIG="$(cd "$(dirname "$CONFIG")" && pwd)/$(basename "$CONFIG")"
CONFIG_DIR="$(dirname "$CONFIG")"

# Sanity-check that .env with APIFY_TOKEN exists alongside config.json.
if [[ ! -f "$CONFIG_DIR/.env" ]]; then
  cat >&2 <<EOF
Error: $CONFIG_DIR/.env not found.

The runner reads APIFY_TOKEN from a .env file next to config.json. Create it:
  echo 'APIFY_TOKEN=your_token_here' > $CONFIG_DIR/.env
  chmod 600 $CONFIG_DIR/.env
EOF
  exit 2
fi
if ! grep -q '^APIFY_TOKEN=' "$CONFIG_DIR/.env"; then
  echo "Error: $CONFIG_DIR/.env exists but has no APIFY_TOKEN line." >&2
  exit 2
fi

PYTHON_BIN="$(command -v python3 || true)"
if [[ -z "$PYTHON_BIN" ]]; then
  echo "Error: python3 not on PATH" >&2; exit 2
fi

OS="$(uname -s)"
LABEL="com.apify.ai-visibility-tracker"

confirm() {
  if [[ "$YES" == "1" ]]; then return 0; fi
  read -r -p "$1 [y/N] " ans
  [[ "$ans" =~ ^[Yy]$ ]]
}

# ---- macOS: launchd ----
install_macos() {
  local plist="$HOME/Library/LaunchAgents/$LABEL.plist"
  local logdir="$HOME/Library/Logs"
  mkdir -p "$logdir" "$HOME/Library/LaunchAgents"

  local cal_block
  case "$CADENCE" in
    daily)
      cal_block="<dict><key>Hour</key><integer>$HOUR</integer><key>Minute</key><integer>0</integer></dict>"
      ;;
    weekly)
      cal_block="<dict><key>Hour</key><integer>$HOUR</integer><key>Minute</key><integer>0</integer><key>Weekday</key><integer>1</integer></dict>"
      ;;
    monthly)
      cal_block="<dict><key>Hour</key><integer>$HOUR</integer><key>Minute</key><integer>0</integer><key>Day</key><integer>1</integer></dict>"
      ;;
  esac

  cat <<EOF
Will write the following launchd plist to:
  $plist

Schedule:        $CADENCE at ${HOUR}:00 local time
Runner:          $PYTHON_BIN $RUNNER --config $CONFIG
Working dir:     $CONFIG_DIR
APIFY_TOKEN src: $CONFIG_DIR/.env  (read by the runner; NOT embedded in plist)
Logs:            $logdir/ai-visibility-tracker.log
EOF

  if ! confirm "Proceed with install?"; then echo "Aborted."; exit 1; fi

  cat > "$plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>$PYTHON_BIN</string>
    <string>$RUNNER</string>
    <string>--config</string>
    <string>$CONFIG</string>
  </array>
  <key>WorkingDirectory</key><string>$CONFIG_DIR</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key><string>/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin</string>
  </dict>
  <key>StartCalendarInterval</key>
  $cal_block
  <key>StandardOutPath</key><string>$logdir/ai-visibility-tracker.log</string>
  <key>StandardErrorPath</key><string>$logdir/ai-visibility-tracker.log</string>
  <key>RunAtLoad</key><false/>
</dict>
</plist>
EOF
  chmod 600 "$plist"

  # Unload any previous version first; then bootstrap (modern) or fall back to load.
  launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
  if ! launchctl bootstrap "gui/$(id -u)" "$plist" 2>/dev/null; then
    launchctl load "$plist"
  fi

  cat <<EOF

Installed. Verify with:
  launchctl list | grep ai-visibility
  tail -f $logdir/ai-visibility-tracker.log

To fire it once now (burns one actor run):
  launchctl kickstart "gui/\$(id -u)/$LABEL"
EOF
}

# ---- Linux: crontab ----
install_linux() {
  local schedule
  case "$CADENCE" in
    daily)   schedule="0 $HOUR * * *" ;;
    weekly)  schedule="0 $HOUR * * 1" ;;
    monthly) schedule="0 $HOUR 1 * *" ;;
  esac

  local logfile="$HOME/.ai-visibility-tracker.log"
  local line="$schedule cd $CONFIG_DIR && $PYTHON_BIN $RUNNER --config $CONFIG >> $logfile 2>&1 # ai-visibility-tracker"

  cat <<EOF
Will append the following line to your crontab:

$line

The runner reads APIFY_TOKEN from $CONFIG_DIR/.env -- NOT embedded in the cron line.
Logs: $logfile
EOF

  if ! confirm "Proceed with install?"; then echo "Aborted."; exit 1; fi

  # Remove any previous tagged line, then append the new one.
  ( crontab -l 2>/dev/null | grep -v '# ai-visibility-tracker'; echo "$line" ) | crontab -

  cat <<EOF

Installed. Verify with:
  crontab -l
  tail -f $logfile
EOF
}

# ---- Windows: print instructions only ----
install_windows() {
  cat <<EOF
Windows automated install is not supported by this script.
Run the following in an elevated PowerShell prompt:

  schtasks /Create /SC DAILY /ST ${HOUR}:00 /TN "AI Visibility Tracker" ^
    /TR "$PYTHON_BIN $RUNNER --config $CONFIG"

For weekly: /SC WEEKLY /D MON
For monthly: /SC MONTHLY /D 1

The runner reads APIFY_TOKEN from $CONFIG_DIR\\.env -- you do NOT need to set
it via setx.
EOF
}

case "$OS" in
  Darwin) install_macos ;;
  Linux)  install_linux ;;
  CYGWIN*|MINGW*|MSYS*) install_windows ;;
  *) echo "Unsupported OS: $OS" >&2; exit 2 ;;
esac
