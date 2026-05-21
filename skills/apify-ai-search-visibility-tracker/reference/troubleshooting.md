# Troubleshooting

## Setup / first run

**`APIFY_TOKEN not found`**
Put the token in a `.env` file in the same directory as `config.json` (`echo 'APIFY_TOKEN=...' > .env && chmod 600 .env`). The runner auto-loads it on every fire -- whether invoked manually, from launchd, or from cron. Rotate the token by overwriting the same `.env` file -- no schedule reinstall needed.

**`config.json not found`**
Run Step 3 of `SKILL.md` -- copy `reference/scripts/config.example.json` to `./config.json` and fill in the seven required fields. The runner refuses to start without it; this is deliberate (no interactive fallback, because launchd / cron has no stdin).

**`ModuleNotFoundError: No module named 'requests'`**
The runner needs `requests`. Install with `pip3 install requests`. Optional but recommended: `pip3 install tldextract` for accurate registrable-domain matching on multi-part TLDs.

## Actor runs

**Actor run status: `FAILED`**
The runner prints the console URL -- open it. Common causes:
- Invalid `countryCode` / `languageCode` (use ISO 3166-1 alpha-2 / ISO 639-1).
- Apify account out of credits.
- Actor build temporarily broken -- retry in 5 minutes or pin to an older build (`--build`).

**Dataset not appearing in console**
Named datasets are scoped to the token's account. Verify by hitting `https://api.apify.com/v2/datasets?token=$APIFY_TOKEN&unnamed=false`. If the runner's first call to "get-or-create dataset by name" fails, it falls back to writing items to the run's default dataset and prints the run-default dataset URL; the next run will retry the named dataset.

## Citation and mention matching

**Brand looks uncited but I see it in the answer text**
Two checks:
1. Is the URL on the same registrable domain? `github.com/apify/...` is a citation for **GitHub**, not Apify.
2. Did the surface form match? `\bApify\b` will not match `Apify's` if your form is `Apify's` (the trailing `s` is a word character). Add `Apify's` as a separate surface form, or rely on `Apify` (which matches the `Apify` part of `Apify's` via `\b...\b`).

**Brand showing as mentioned in unrelated text**
The brand surface form is too generic (e.g., `Apify` as a verb in some other context). Use a more specific form (`apify.com`, or the brand plus a qualifier).

## Schedule (launchd / cron) issues

**macOS `launchctl list | grep ai-visibility` shows the label but the dataset has no new rows**
- Machine was asleep at the scheduled hour. launchd skips fires while asleep and does NOT catch up. Open the lid before the next scheduled hour, or host the runner on an always-on machine.
- The runner errored. Tail `~/Library/Logs/ai-visibility-tracker.log` and look for the last `Error:` line.

**Linux `crontab -l` shows the line but no log lines appear**
- cron daemon disabled. On Debian/Ubuntu: `systemctl status cron` (or `cronie`/`crond` on RHEL/Fedora). Container / WSL environments often have no daemon at all.
- Permissions on `~/.ai-visibility-tracker.log`: if the file is root-owned from an earlier test, `rm` it and let cron recreate it.

**`APIFY_TOKEN not found` in the log**
- `.env` missing or unreadable. Verify: `cat $CONFIG_DIR/.env` should show the `APIFY_TOKEN=` line.
- Permissions: should be `chmod 600 .env`.
- Token rotated: `echo 'APIFY_TOKEN=new_value' > .env` -- no reinstall needed.

**`python3: command not found` in the log**
- The plist / crontab captured an absolute path at install time. If you've reinstalled Homebrew or moved Python since, the path is stale. Re-run `install_cron.sh` -- it re-resolves `python3`.

**Reports land in `$HOME/reports/` instead of the project folder**
- The launchd plist uses `WorkingDirectory`; cron lines start with `cd $CONFIG_DIR &&`. If you've edited the crontab by hand and dropped the `cd`, reports go to whatever cron's default `pwd` is (`$HOME`). Reinstall via `install_cron.sh` to fix.


## Diff and reports

**Report says `_First run -- no diff available._` but I know it's not the first run**
The runner finds the previous run by querying the dataset for rows with a different `run_timestamp` for the same prompt. If the dataset name was changed in `config.json`, the diff has nothing to compare to -- it's looking at an empty dataset. Either restore the old dataset name, or accept the missing diff for this transition run.

**Share-of-voice deltas look bigger than expected**
SoV is sensitive to the citation count. A query with 4 citations vs. one with 14 -- the same brand cited once swings SoV from 25% to 7%. Always look at `Delta Cited` (raw count) alongside `Delta SoV`. Both are in the per-source scorecard.

## Config corruption

**Runner exits with `json.JSONDecodeError` on config.json**
Restore from the example: `cp reference/scripts/config.example.json ./config.json.new`, copy your values over by hand. Schema lives in `output-schema.md` for the dataset; config schema is in `config.example.json` itself.
