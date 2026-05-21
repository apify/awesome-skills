# Example setup -- Acme, two competitors, five prompts, weekly cadence

A worked walkthrough of a first-run setup, starting from an empty working directory.

## 1. The seven anchors + optional follow-ups

```
> /skills load ai-search-visibility-tracker

Claude: Before the first snapshot I need seven things:

  1. Brand URL?                                              > acme.com
  2. Surface forms to match in answer text (comma-sep)?      > Acme, acme.com, @acme
  3. Competitors (name + domain pairs, or "none")?           > Northwind northwind.com; Contoso contoso.com
  4. Prompts to monitor (blank line ends list)?
     > best web scraping tool
     > how to scrape marketplace prices
     > Acme vs Fabrikam
     > no-code web scraping
     > scraping API for developers
     >
  5. Cadence (daily / weekly / monthly)?                     > weekly
  6. AI sources (default: all 6 on)?                         > keep all
  7. Apify Dataset name?                                     > ai-visibility-acme

Claude: Optional:
  countryCode (us) / languageCode (en) / hour (9)?           > defaults
  Verbosity (on_demand keeps full answers in KV store)?      > on_demand
```

## 2. Confirmation

```
Claude: Setup:
  Brand: Acme (acme.com)  |  Competitors: Northwind, Contoso
  Prompts: 5  |  Cadence: weekly Mondays 09:00 local (0 9 * * 1)
  Sources: all 6  |  Dataset: ai-visibility-acme  |  KV: ai-visibility-acme-raw
  Cost: ~$0.18/run, ~$9.40/year (52 runs)

Proceed? > y
```

## 3. Files written

```
./config.json    # the seven anchors + acme section
./.env           # APIFY_TOKEN=...    (chmod 600)
./reports/       # created on first snapshot
```

## 4. Install the OS schedule

```
Claude: macOS detected -> writing ~/Library/LaunchAgents/com.acme.ai-visibility-tracker.plist
  Schedule:    weekly Mondays 09:00 local
  Runner:      /usr/bin/python3 .../run_snapshot.py --config /abs/path/config.json
  Token:       read from ./.env at fire time (NOT embedded in the plist)
  Logs:        ~/Library/Logs/ai-visibility-tracker.log

Proceed? > y

Installed. Verify:  launchctl list | grep ai-visibility
Fire now:           launchctl kickstart "gui/$(id -u)/com.acme.ai-visibility-tracker"
```

On Linux the installer writes a `crontab` line tagged `# ai-visibility-tracker` (log: `~/.ai-visibility-tracker.log`). On Windows it prints a `schtasks /Create` command.

## 5. Immediate first snapshot

Kickstarting the launchd job streams these lines to the log:

```
[09:00:12Z] Loaded config / Dataset ID: a1B2c3D4e5F6g7H8
[09:00:13Z] Starting actor: apify/google-search-scraper  (Run ID: a1B2c3D4)
[09:01:45Z] Run status: SUCCEEDED
[09:01:46Z] Parsed 90 snapshot rows  (5 prompts x 6 sources x 3 entities)
[09:01:47Z] Appended 90 rows to 'ai-visibility-acme'
[09:01:48Z] Wrote 5 raw records to 'ai-visibility-acme-raw'
[09:01:48Z] Wrote report: ./reports/snapshot-2026-05-20.md
```

## 6. Subsequent weekly runs

Every Monday at 09:00 local, launchd (or cron on Linux) invokes the runner. No interaction needed.

## Caveats

- **Machine must be on at fire time.** launchd and cron skip fires when asleep / off; missed runs aren't caught up. For laptops with closed lids overnight, expect occasional misses -- or host the runner on an always-on machine.
- **DST is handled.** launchd `StartCalendarInterval` and cron both use local time and follow DST.
