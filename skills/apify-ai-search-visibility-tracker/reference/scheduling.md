# Scheduling -- via OS-level cron / launchd

## TL;DR

Recurrence is driven by **the operating system's own scheduler**. The skill ships an installer that detects the OS and writes the right schedule entry:

- **macOS** -> `~/Library/LaunchAgents/com.apify.ai-visibility-tracker.plist`
- **Linux** -> a crontab line tagged `# ai-visibility-tracker`
- **Windows** -> the installer prints a `schtasks` command for the user to run

At fire time, the scheduler invokes `python3 run_snapshot.py --config <abs path>` with the working directory set next to `config.json`. The runner reads `APIFY_TOKEN` from a `.env` file at that location, so no credential ever lands in the schedule entry itself.

## Installation

From the user's working directory (containing `config.json` and `.env`):

```bash
bash ${CLAUDE_PLUGIN_ROOT}/reference/scripts/install_cron.sh --cadence daily --hour 9
```

The installer:

1. Validates that `config.json` exists.
2. Validates that `.env` next to `config.json` contains an `APIFY_TOKEN=...` line.
3. Resolves absolute paths for `python3`, `run_snapshot.py`, `config.json`.
4. Detects the OS via `uname -s` and branches:
   - **macOS** -> writes the plist, `chmod 600`, then `launchctl bootstrap gui/$(id -u) <plist>` (falls back to `launchctl load` on older macOS).
   - **Linux** -> appends a single crontab line `0 H * * * cd <config-dir> && python3 <runner> --config <config> >> ~/.ai-visibility-tracker.log 2>&1 # ai-visibility-tracker`. Any prior tagged line is removed first so re-installing is idempotent.
   - **Windows** -> prints a `schtasks /Create` command.
5. Shows the user the exact entry it will write, then asks for confirmation (skip with `--yes`).

## Cron expressions by cadence

| Cadence | Cron expression | When |
|---------|-----------------|------|
| daily   | `0 H * * *`     | every day at H:00 local |
| weekly  | `0 H * * 1`     | every Monday at H:00 local |
| monthly | `0 H 1 * *`     | the 1st of every month at H:00 local |

`H` is the user's chosen hour (0-23, default 9). On macOS, the same cadence maps to `StartCalendarInterval` keys (`Hour`/`Minute` + optional `Weekday`/`Day`).

## Credential handling

The schedule entry contains **no token**. The runner script's `load_dotenv_into_env()` helper reads `.env` from the config's directory at run-start and merges it into `os.environ` before any Apify call. Rotating the token is just `echo 'APIFY_TOKEN=new_value' > .env` -- no reinstall needed.

## Changing cadence

Re-run the installer with the new `--cadence` / `--hour`. It removes the previous entry (by Label on macOS, by the marker comment on Linux) and writes a new one.

## Verifying the schedule

| OS | Verify it's loaded | Tail its log |
|----|---|---|
| macOS | `launchctl list \| grep ai-visibility` | `tail -f ~/Library/Logs/ai-visibility-tracker.log` |
| Linux | `crontab -l` | `tail -f ~/.ai-visibility-tracker.log` |
| Windows | `schtasks /Query /TN "AI Visibility Tracker"` | check Task Scheduler History |

To fire it once now without waiting for the schedule, on macOS:

```bash
launchctl kickstart "gui/$(id -u)/com.apify.ai-visibility-tracker"
```

On Linux there's no direct kickstart -- just run the command from the cron line manually, or invoke `python3 run_snapshot.py --config ./config.json` from the config dir.

## Caveats

- **Machine must be on at fire time.** Both launchd and cron skip a fire if the machine is asleep / off; missed runs are NOT caught up. For a laptop, expect occasional missed mornings.
- **DST.** Cron and `StartCalendarInterval` interpret the hour in local time, so they auto-track DST.
- **No retries.** If the actor run fails (Apify outage, network blip), the runner exits non-zero and the next fire is the recovery point. To add retry-on-failure semantics, wrap the runner call in a small bash loop with a sleep between attempts.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `crontab -l` shows the entry but no log lines | cron daemon disabled | `systemctl status cron` (or `cronie`/`crond`); start it |
| `launchctl list` shows the label but no fires | machine was asleep at the scheduled hour | Open the lid + power before 09:00, or move to an always-on host |
| Log says `APIFY_TOKEN not found` | `.env` missing or not readable | Verify `cat $CONFIG_DIR/.env` and check `chmod 600` permissions |
| Log says `python3: command not found` | macOS reinstalled Homebrew, Python path drifted | Re-run `install_cron.sh` -- it re-resolves `python3` |
| Reports written to `$HOME/reports/` not project folder | cron line missing the leading `cd <config-dir>` | Reinstall via `install_cron.sh` (it always injects the `cd`) |
