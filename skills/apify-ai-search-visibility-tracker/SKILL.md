---
name: apify-ai-search-visibility-tracker
description: Track whether a brand and its competitors get cited or mentioned across Google AI Overviews, Google AI Mode, ChatGPT Search, Perplexity, Microsoft Copilot, and Google Gemini for a defined set of prompts, on a recurring schedule. Use when user asks to track AI visibility, monitor brand mentions in AI search, track ChatGPT citations, do AI search SEO tracking, GEO tracking (Generative Engine Optimization), AEO tracking (Answer Engine Optimization), monitor Perplexity citations, track AI Overviews mentions, or see if their brand shows up in AI search.
author: Daniela Ryplová
author_url: https://github.com/danielarypl
---

# AI Search Visibility Tracker

Snapshots brand citations and mentions across six AI search surfaces (Google AI Overviews, Google AI Mode, ChatGPT Search, Perplexity, Microsoft Copilot, Google Gemini) on a recurring schedule. Every run appends to a named Apify Dataset, writes the raw item to a named Apify Key-Value Store, and produces a Markdown report comparing today's snapshot to every prior run. Recurrence is driven by the **operating system's own scheduler** -- launchd on macOS, cron on Linux, Task Scheduler on Windows. See `reference/scheduling.md`.

## Prerequisites
(No need to check upfront)

- `APIFY_TOKEN` saved in a `.env` file next to `config.json` (the runner auto-loads it).
- Python 3.9+ on PATH. `pip3 install requests` (only third-party dependency); `pip3 install tldextract` recommended for accurate registrable-domain matching on multi-part TLDs.
- For automated daily runs: macOS / Linux with launchd or cron available (the installer handles both). Windows users get printed `schtasks` instructions.

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Step 1: Load or collect the seven required inputs
- [ ] Step 2: Confirm AI sources and cadence
- [ ] Step 3: Write config.json + .env, then install the OS schedule
- [ ] Step 4: Run a snapshot now so the user sees the first report
- [ ] Step 5: Deliver the history report (diff vs. all prior runs)
```

### Step 1: Load or Collect the Seven Required Inputs

If `config.json` exists in the user's working directory, load it and skip to Step 4 unless the user asks to reconfigure. On first run, ask all seven anchors **before** any Actor call:

| # | Input | Why it matters |
|---|-------|----------------|
| 1 | **Brand URL** | Primary domain. Drives registrable-domain citation matching (`blog.apify.com` -> `apify.com`). |
| 2 | **Brand name(s)** | Surface forms for text-mention matching (e.g., `Apify`, `apify.com`, `@apify`). URL-only matching misses mentions without links. |
| 3 | **Competitor brands** | Ask explicitly: *"Which competitors do you want tracked alongside your brand?"* Accept `name + domain` pairs. Zero is allowed; the question must still be asked on first run. |
| 4 | **Prompts to monitor** | One or more search queries. Each runs through every enabled AI source. |
| 5 | **Cadence** | `daily` / `weekly` / `monthly`. Drives the schedule entry that `install_cron.sh` writes. |
| 6 | **Which AI sources** | Present the six (AI Overviews, AI Mode, ChatGPT, Perplexity, Copilot, Gemini), all enabled by default. Each adds per-result cost -- current pricing on the Actor page (https://apify.com/apify/google-search-scraper). |
| 7 | **Apify Dataset name** | The named dataset to append to. If absent, created on first run; the name is recorded in `config.json`. |

After those seven, ask optional follow-ups: `countryCode`, `languageCode`, `location` (UULE), preferred run hour (default `09:00` local).

Then one verbosity question -- save as `config.json:include_full_answers`:

- **`on_demand`** (default): report shows short quoted snippets around each surface-form match. Full LLM answers live in the named KV store; user can ask later.
- **`always`**: report embeds the full LLM answer verbatim whenever any entity is mentioned. Useful for one prompt; gets unwieldy at 5+ prompts.

### Step 2: Confirm AI Sources and Cadence

Echo back the user's seven choices in a single paragraph for confirmation. If the user toggles sources, update the in-memory config before writing.

### Step 3: Write `config.json` + `.env`, Then Install the OS Schedule

Create the working directory layout next to where the user wants reports to land:

```
working-dir/
  config.json     # copied from the skill's config.example.json, edited with collected values
  .env            # APIFY_TOKEN=apify_api_xxx   (chmod 600)
```

```bash
cp ${CLAUDE_PLUGIN_ROOT}/reference/scripts/config.example.json ./config.json
# then edit with the collected values, save

echo 'APIFY_TOKEN=your_token_here' > ./.env
chmod 600 ./.env
```

Then install the OS schedule. The installer detects macOS / Linux / Windows and writes the right entry. It validates that `config.json` and `.env` both exist before doing anything, and shows the user the exact schedule entry before applying it:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/reference/scripts/install_cron.sh --cadence daily --hour 9
```

Cron expression mapping (the installer fills these in):

| Cadence | Cron expression | When |
|---------|-----------------|------|
| daily   | `0 H * * *`     | every day at H:00 local |
| weekly  | `0 H * * 1`     | every Monday at H:00 |
| monthly | `0 H 1 * *`     | the 1st of every month at H:00 |

`H` is the user's chosen hour (0-23, default 9).

The schedule entry contains **no credentials**. The runner reads `APIFY_TOKEN` from `.env` at fire time. Rotating the token is `echo 'APIFY_TOKEN=new_value' > .env` -- no reinstall needed. Full mechanics in `reference/scheduling.md`.

### Step 4: Run a Snapshot Now

Fire one snapshot immediately so the user sees the first report without waiting for tomorrow's schedule:

**macOS:**

```bash
launchctl kickstart "gui/$(id -u)/com.apify.ai-visibility-tracker"
tail -f ~/Library/Logs/ai-visibility-tracker.log
```

**Linux / generic:**

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_snapshot.py --config ./config.json
```

Both paths:

1. Call `apify/google-search-scraper` with the configured prompts + AI-source toggles.
2. Parse each (prompt x source) cell for citations and brand/competitor mentions.
3. Append rows to the named Apify Dataset (schema in `reference/output-schema.md`).
4. Write the raw item to the named KV store (long-term archive).
5. Compute the history vs. all prior runs.
6. Write `reports/snapshot-<ISO-date>.md` next to `config.json`.

The runner reads its input only from `--config` and env vars. **It never prompts on stdin** -- the scheduler has no stdin to give it.

### Output format

Snapshot summaries are **entity-major**: one Markdown table per tracked entity (brand, then competitors), one row per AI source, columns `Source | Cited | Mentioned | SoV% | Matched URLs | History`. Each table is followed by a one-line interpretive note quoting the surface-form context where the entity was mentioned. The runner emits this format; chat summaries should mirror it. Full template in `reference/output-schema.md`.

### Step 5: Deliver the History Report

Open `reports/snapshot-<ISO-date>.md` and surface the top findings in chat. From the second run onwards the report compares today's snapshot to **every prior run** (unless the user asks for last-run-only). Lead with:

- **First-ever citations / mentions today** -- entity x source combinations crossing the threshold for the first time.
- **Drops** -- entity was cited in the latest prior run but isn't today.
- For every cited entity, the **exact matched URL(s)**.

Don't restate the full report -- point the user at the file. Per-source scorecards + per-prompt detail + top-10 most-cited URLs are already in there.

## Actor

The skill uses a single Actor -- `apify/google-search-scraper` -- for all six AI surfaces. AI Overviews ride alongside the organic SERP automatically; do **not** set `disableGoogleSearchResults: true`. Input schema and field-name mapping in `reference/apify-actor-usage.md`. Pricing changes; check the Actor's [pricing tab](https://apify.com/apify/google-search-scraper) before quoting numbers.

## Quality Rules

- **Non-interactive.** No stdin reads in `run_snapshot.py` -- launchd / cron has no stdin.
- **Word-boundary brand matching** (`\bbrand\b`, case-insensitive) so `Apify` doesn't match `Apifying`. See `reference/citation-matching.md`.
- **Registrable-domain citation matching** (`blog.apify.com` counts as `apify.com`). See `reference/citation-matching.md`.
- **Never skip a row.** If an AI source returns nothing, write a row with `cited: false, mentioned: false, answer_text: "[no answer returned]"`. Continuity is required for the history diff.
- **Every row carries the Apify run ID** so any finding can be reverified.

## Error Handling

`APIFY_TOKEN not found` -- Tell the user to put it in `.env` next to `config.json` (`echo 'APIFY_TOKEN=...' > .env && chmod 600 .env`). Token at https://console.apify.com/account/integrations.
`config.json not found` -- Run Step 3 first to create it from the template.
`Dataset name not set` -- Ask the user for a name; the runner will create the dataset on first append.
`Actor run FAILED` -- Print the console link from the runner output and ask the user to inspect it.
`AI source returned no answer` -- The row is still written with `[no answer returned]`. Not an error.
`Schedule not firing` -- See `reference/scheduling.md` troubleshooting section: macOS `launchctl list | grep ai-visibility`, Linux `crontab -l`, check the log file at `~/Library/Logs/ai-visibility-tracker.log` (macOS) or `~/.ai-visibility-tracker.log` (Linux).
`No previous run to diff against` -- First run only. The report renders the snapshot without a history section.
