---
name: apify-buying-signal-detection
description: Set up a recurring buying-signal detection pipeline that finds companies showing buying intent across three signal types — job postings (hiring for the persona), fundraising events (recent raises), and LinkedIn content (pain-point posts, hiring announcements) — then aggregates results into a deduplicated leads.csv with the signal source, evidence URL, and detection timestamp per row. Split-schedule architecture — Apify Actor Tasks pull raw data on their own cadence, a Claude-side aggregation task normalizes, deduplicates against a blacklist, and appends new leads with a weekly-idempotent guard. Use when the user says "find companies with buying signals", "detect intent signals for outbound", "set up a weekly lead pipeline", "monitor hiring signals for lead gen", "track startup funding leads", "find LinkedIn buying signals", "schedule Apify Actors for prospecting", "build a signals-based lead list", or "set up buying-intent monitoring for my ICP".
author: Fabian Maume
author_url: https://github.com/fmaume
metadata:
  keywords: "buying-signals, intent-data, lead-generation, outbound, prospecting, hiring-signals, funding-signals, linkedin-signals, sales-triggers, icp, scheduled-pipeline, b2b"
---

# Buying-Signal Detection

Turn an ICP description into a recurring pipeline that surfaces companies showing buying intent across three signal types — job postings, fundraising events, and LinkedIn content — and appends them to a single deduplicated `leads.csv` you can pipe straight into your CRM.

## What this skill does (and what it deliberately does not)

This skill **sets up and runs** a scheduled workflow. It does not draft cold emails, score leads by fit, or push rows into a CRM. Its output is a clean, evidence-linked `leads.csv` — the *input* to whatever outreach process you already have. Cold outreach drafting for these leads is deliberately a separate concern (that's what `apify-link-prospecting-outreach` and similar skills exist for).

Three design commitments worth knowing before you start:

1. **The Apify side and the Claude side run on separate schedules.** Apify runs the Actors on its own cron; Claude runs the aggregation on its own cron. Claude Code doesn't need to be up when the Actors run. This decoupling is what makes the pipeline actually recurring, not just "you have to remember to trigger it."
2. **Weekly idempotency is enforced at aggregation time.** If the leads CSV already has an entry from the current ISO week, the aggregate script exits early with no HTTP calls made. The Claude-side schedule can fire more often than weekly (safety net) without cost impact.
3. **First-seen wins on dedup.** A lead surfaced by the jobs signal on Monday stays a jobs-signal lead even if the same company shows up in the funding feed on Wednesday. The signal that first surfaced a company is the more useful one.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)
- Python 3.10+ (for `scripts/aggregate.py` and `scripts/setup_apify_tasks.py`; only stdlib is required — `requests` is used when available but has a `urllib` fallback)
- Optional: a way to trigger the Claude-side aggregation on a schedule — the local `scheduled-tasks` MCP is the recommended path when you're on Claude Code; cron / Task Scheduler / GitHub Actions all work too if you'd rather run it headlessly

## Workflow

Copy this checklist and mark items done:

```
Task Progress:
- [ ] Step 1: Collect ICP inputs (block on these)
- [ ] Step 2: Write icp.json + blacklist.csv (if any)
- [ ] Step 3: Provision Apify Actor Tasks (setup_apify_tasks.py)
- [ ] Step 4: Verify Actor picks in the Apify Console
- [ ] Step 5: Register the Claude-side aggregation schedule
- [ ] Step 6: First manual run of aggregate.py — sanity check the output
```

### Step 1: Collect ICP inputs (block on these)

Ask the user for all of the following before writing any file. The setup script needs every field to route correctly, and reworking a scheduled task after it's provisioned means either editing it in the Apify Console or re-running setup — both worse than asking once.

1. **Campaign name** — a short slug (lowercase, dashes). Used as the prefix on every Apify Task name (e.g. `emea-saas-hiring-aes-bebity-linkedin-jobs-scraper`). If the user already runs multiple campaigns, prevent collisions upfront.
2. **Signals to track** — subset of `["jobs", "funding", "linkedin_content"]`. Rarely will a campaign want only one; the strength of the workflow is the intersection of signals per company. Recommend all three unless there's a specific cost concern.
3. **Geo (ISO country codes)** — uppercase two-letter codes. Drives regional Actor routing (Stepstone for DE/AT/BE, Seek for AU/NZ, France Travail for FR, Maddyness for FR-funding). Global campaigns should list every country the user actually sells into — passing `["US", "GB", "DE", "FR", "AU"]` will fan out to five regional job Actors, which is 5× the weekly cost. See [`references/gotchas.md`](references/gotchas.md#cost-guardrails).
4. **Industry keywords** — the category descriptor. Passed to funding trackers as `industry`, to LinkedIn as `keywords` when no explicit content search terms are provided, and to job scrapers as a fallback when no persona titles are given.
5. **Persona (if jobs signal enabled)** — job titles the ICP hires for. Concrete titles beat categories: `"Account Executive"`, `"SDR"`, `"BDR"` are hits; `"sales"` is noise. Optional seniority (`entry`, `mid`, `senior`, `manager`, `director`, `vp`, `cxo`) and company-size bands (`"11-50"`, etc.) get applied post-hoc in the aggregator.
6. **Funding config (if funding signal enabled)** — stages (`seed`, `series_a`, `series_b`, etc.) and `max_days_since_announcement` (default 90). Fresh cash → open budget → tighter window is better.
7. **LinkedIn content config (if linkedin_content signal enabled)** — search phrases. This is the biggest quality lever; broad terms (`"sales"`) waste budget. Specific pain-point phrases beat category names — see [`references/actors.md`](references/actors.md#linkedin-search-phrase-design). Plus `min_reactions` (default 5) and `posted_within_days` (default 14) for post-filtering.
8. **Where to store leads** — path to a CSV file. Default `./leads.csv` inside the campaign directory. This file is the pipeline's memory across runs; keep it under version control (or at least back it up) so the dedup guard survives disk resets.
9. **Blacklist CSV path** — optional. CSV with columns `domain,company,reason`. Rows matching either the exact domain or the normalized company name get dropped before append. If the user doesn't have one, ask if they want to start with obvious exclusions (existing customers, their own domain, top competitors).
10. **Schedule** — `apify_side_cron` (when Apify runs the Actors) and `claude_side_cron` (when Claude aggregates). Default: `0 6 * * 1` (Apify Monday 06:00 UTC) and `0 8 * * 1` (Claude Monday 08:00 UTC). Two hours of buffer between them absorbs slow Actor runs.

The full schema is documented in [`references/icp-config-schema.md`](references/icp-config-schema.md). A worked example lives at [`examples/icp.example.json`](examples/icp.example.json).

### Step 2: Write `icp.json` and `blacklist.csv`

Write the campaign directory contents:

```
<campaign-dir>/
  icp.json           ← the config from Step 1
  blacklist.csv      ← optional; columns: domain,company,reason
  leads.csv          ← created empty; the aggregator will populate it
```

Start `leads.csv` with just the header row (schema in [`references/csv-schema.md`](references/csv-schema.md)) so the aggregator doesn't have to handle a missing-file case on first run:

```
detected_at,company,domain,signal_type,signal_detail,signal_source_actor,signal_date,evidence_url,geo,notes
```

### Step 3: Provision Apify Actor Tasks

Run the setup script:

```bash
APIFY_TOKEN=$APIFY_TOKEN \
python ${CLAUDE_PLUGIN_ROOT}/scripts/setup_apify_tasks.py \
  --config ./icp.json
```

What this does:
- Reads `icp.json` and picks Actors per the routing tables in [`references/actors.md`](references/actors.md) — global Actors always, plus regional Actors matching the geo list.
- For each pick, upserts an Apify Actor Task named `<campaign>-<actor-slug>` with the input payload derived from the ICP. Re-running the script updates existing tasks in place; it does not create duplicates.
- Writes a sidecar `<campaign-dir>/.<campaign-name>.tasks.json` recording the task IDs. `aggregate.py` reads this to know which tasks to pull dataset items from.
- If `schedule.apify_side_cron` is set in the ICP (default is), creates or updates a single Apify Schedule that fires all the tasks on that cron.

Useful flags:
- `--dry-run` — print the pick list and payloads without making any API calls. Always do this once when authoring a new campaign.
- `--no-schedule` — provision tasks but skip Schedule creation (useful when you want to trigger runs manually while calibrating).

### Step 4: Verify Actor picks in the Apify Console

Open [console.apify.com/actors/tasks](https://console.apify.com/actors/tasks). Filter by the campaign prefix. Sanity-check three things:

1. **The right Actors were picked** — the regional ones (Stepstone / Seek / France Travail / Maddyness) fire only for the intended geos. If you see Seek but no ANZ country in the ICP, something's off.
2. **The input payload looks right** — click each task, view its input JSON. Keywords, titles, and stages should be populated from the ICP; nothing should be `null`.
3. **The Apify Schedule is enabled** — under Schedules, find `<campaign>-schedule`, confirm it's on and lists every task.

If anything looks wrong, edit `icp.json` and re-run `setup_apify_tasks.py` — it's idempotent.

### Step 5: Register the Claude-side aggregation schedule

Register a scheduled task that invokes the aggregator on the campaign's `claude_side_cron`. Pick whichever runner matches your environment:

**Option A — `scheduled-tasks` MCP inside Claude Code.** The MCP exposes `mcp__scheduled-tasks__create_scheduled_task`. The concrete call to make:

```json
{
  "name": "<campaign-name>-aggregate",
  "cron_expression": "<value of schedule.claude_side_cron from icp.json>",
  "timezone": "UTC",
  "prompt": "Run the buying-signal aggregator. Execute exactly: python ${CLAUDE_PLUGIN_ROOT}/scripts/aggregate.py --config /abs/path/to/icp.json. Requires APIFY_TOKEN env var. On non-zero exit, surface the stderr in the notification body — do not attempt to reinterpret the error."
}
```

Substitute the real values for `<campaign-name>` and `/abs/path/to/icp.json` before making the call. Verify the task landed with `mcp__scheduled-tasks__list_scheduled_tasks` and confirm the cron matches `icp.json`.

**Option B — headless cron / Task Scheduler / CI.** Add a plain OS-level scheduler entry:

```bash
# Linux crontab entry
0 8 * * 1 APIFY_TOKEN=$APIFY_TOKEN /path/to/python /path/to/aggregate.py --config /path/to/icp.json >> /path/to/aggregate.log 2>&1
```

Or a GitHub Actions workflow (`.github/workflows/aggregate.yml`):

```yaml
on:
  schedule:
    - cron: '0 8 * * 1'
jobs:
  aggregate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - env: { APIFY_TOKEN: '${{ secrets.APIFY_TOKEN }}' }
        run: python scripts/aggregate.py --config icp.json
```

Either runner is safe to invoke more often than weekly — the weekly-idempotency guard skips runs that already have this-week entries. Use `--force` only during calibration.

### Step 6: First manual run of `aggregate.py`

Before waiting for the schedule to fire, run once manually to confirm the wiring. This also seeds `leads.csv` so the week-guard has something to compare against next week:

```bash
APIFY_TOKEN=$APIFY_TOKEN \
python ${CLAUDE_PLUGIN_ROOT}/scripts/aggregate.py --config ./icp.json
```

Expected output shape:

```
{
  "summary": {
    "appended": 47,
    "fetched_by_signal": {"jobs": 320, "funding": 88, "linkedin_content": 210},
    "dropped": {"blacklist": 2, "dup_domain": 156, "dup_url": 401, "post_filter": 12, "unmappable": 0, "linkedin_no_domain": 8},
    "linkedin_profile_lookups": 142,
    "linkedin_profile_resolved": 134,
    "linkedin_company_lookups": 118,
    "linkedin_company_resolved": 112,
    "linkedin_domain_resolved": 128
  }
}
wrote 47 new rows to /abs/path/to/leads.csv
```

The `linkedin_*_lookups` / `linkedin_*_resolved` counters report each hop of
the LinkedIn author-domain enrichment chain (see below). `linkedin_domain_resolved`
is the count of LinkedIn rows whose `domain` column was successfully filled in.
`linkedin_no_domain` is the number of LinkedIn rows dropped because the chain
couldn't resolve a domain — those rows cannot be blacklisted or deduped safely.

If `fetched_by_signal` is all zeros, either the Apify tasks haven't run yet (check the Console) or the sidecar task registry is missing. Wait for the first Apify run to complete, then rerun.

Use `--dry-run` to see what would be appended without touching the CSV, and `--force` to bypass the weekly guard during calibration.

## Actor routing

The full catalog with per-signal PICK rules lives in [`references/actors.md`](references/actors.md). Condensed summary:

| Signal | Global default | Regional additions |
|---|---|---|
| Jobs | `bebity/linkedin-jobs-scraper`, `johnvc/google-jobs-scraper` | Indeed (US/GB/IN/CA), Stepstone (DE/AT/BE), Seek (AU/NZ), France Travail (FR) |
| Funding | `nexgendata/startup-funding-tracker`, `memo23/crunchbase-scraper`, `complex_intricate_networks/fundraising-and-startup-funding-scraper`, `signalbase/signalbase-api` | Maddyness (FR) |
| LinkedIn content | `harvestapi/linkedin-post-search` (no cookies, $2/1k posts) | Deep-scrape fallback: `curious_coder/linkedin-post-search-scraper` (cookie required) |
| LinkedIn author → company domain (enrichment, called on-demand from `aggregate.py`) | `harvestapi/linkedin-profile-scraper` ($4/1k profiles) **+** `harvestapi/linkedin-company` (per-lookup) — two hops | none — profile URL and company LinkedIn URL are the primary keys |

The routing logic in `setup_apify_tasks.py::pick_actors` mirrors this table — if you edit one, edit the other.

### Why the LinkedIn enrichment runs on-demand, not scheduled — and why it's a two-hop chain

`harvestapi/linkedin-post-search` returns the author's name and headline but not the employer's website. Without a domain, the aggregator cannot check the blacklist or dedup against previously seen companies for this signal — meaning blacklisted competitors could slip in via LinkedIn posts.

Resolving that domain takes **two additional Actor calls**, chained inside `aggregate.py::enrich_linkedin_domains`:

1. **`harvestapi/linkedin-profile-scraper`** on the deduplicated set of author profile URLs whose post rows came back without a domain. Returns `currentPosition[0].companyLinkedinUrl` and `companyName` — but *not* the company website. Input: `{profileScraperMode: "Profile details no email ($4 per 1k)", urls: [...]}`.
2. **`harvestapi/linkedin-company`** on the deduplicated set of company LinkedIn URLs returned by step 1. Returns `website`. Input: `{companies: [...]}`.

The chain is the aggregator's only synchronous Actor call path — all other data comes from pre-scheduled Task runs. It's the deliberate exception because both enrichment inputs (author profile URLs, then company URLs) can only be known *after* the previous hop's dataset is read.

**Cost.**
- Profile scraping: $4 per 1000 profiles (chose the "no email" tier — email lookup isn't needed for domain resolution)
- Company scraping: pay-per-event on `harvestapi/linkedin-company`
- Combined effect: for a campaign of 500 LinkedIn posts averaging 3 posts/author, expect ~170 profile lookups + ~150 company lookups (many authors work at the same company)

Three knobs bound the cost:
- Canonical profile URL dedup — N posts by the same author cost one profile lookup (`canonical_linkedin_profile_url` strips `?miniProfileUrn=…` so the same author across sample posts collapses to one key)
- Company-URL dedup at the company-scraper hop — N authors at the same company cost one company lookup
- The whole pass is skipped entirely when every LinkedIn row already has a domain

## Calling Actors — choose your interface

`setup_apify_tasks.py` uses the Apify REST API directly (no Actor call — it provisions Tasks and Schedules). `aggregate.py` uses the REST API to pull dataset items from the last successful run of each task. If you want to trigger an Actor manually during troubleshooting (e.g. Step 4 verification), use one of these:

### Option A: Apify CLI (recommended for portability)

Three flags on every call (`--json`, `--user-agent`, `2>/dev/null`):

    # Manually trigger one campaign task
    apify tasks run <task-id> --wait 300 \
      --json \
      --user-agent apify-awesome-skills/apify-buying-signal-detection \
      2>/dev/null

    # List tasks provisioned for this campaign
    apify tasks list --json 2>/dev/null | \
      jq '.[] | select(.name | startswith("<campaign-name>-"))'

    # Peek at the latest dataset for a task
    apify tasks last-run <task-id> --dataset --format json \
      --user-agent apify-awesome-skills/apify-buying-signal-detection 2>/dev/null

    # Fetch an Actor's input schema (when you're deciding whether to add it to the routing table)
    apify actors info "<actor-id>" --input --json \
      --user-agent apify-awesome-skills/apify-buying-signal-detection 2>/dev/null

### Option B: Apify MCP connector

Hosted MCP server at [mcp.apify.com](https://mcp.apify.com). Full docs at [docs.apify.com/platform/integrations/mcp](https://docs.apify.com/platform/integrations/mcp).

### Option C: MCP client of your choice (e.g. `mcpc`)

Standalone CLI client. See [github.com/apify/mcpc](https://github.com/apify/mcpc).

## Troubleshooting

| Error / symptom | What to do |
|---|---|
| `APIFY_TOKEN not found` | `export APIFY_TOKEN=$(cat ~/.apify_token)` or add to `.env`. Get one at [console.apify.com/account/integrations](https://console.apify.com/account/integrations). |
| `no task registry for campaign '<name>'` | You ran `aggregate.py` before `setup_apify_tasks.py`. Run setup first — it writes the sidecar the aggregator needs. |
| `skipped: already run this week` on a legitimate re-run | Pass `--force`. The guard preserves the week's entries and dedupes on top; it does not overwrite. |
| Task runs on Apify but `aggregate.py` reports `"fetched_by_signal": {"jobs": 0}` | The Actor ran but returned zero items. Check the Actor's run log for schema errors (wrong keyword format, unsupported country code). Post-fix, run the task manually via `apify tasks run` and re-aggregate. |
| Tasks provisioned but no data ever lands | The Apify Schedule may be disabled. In the Console, open Schedules → `<campaign>-schedule` and confirm it's enabled. Also check the schedule's cron matches your timezone assumption — schedules are in UTC unless you set `timezone`. |
| Costs higher than expected | See [`references/gotchas.md#cost-guardrails`](references/gotchas.md#cost-guardrails). Most common cause: broad LinkedIn search terms multiplying `harvestapi/linkedin-post-search` cost. Second-most-common: adding all regional job Actors when the ICP only really sells into two countries. |
| Reposts inflate LinkedIn signal counts | The aggregator strips `trackingId` and `utm_*` query params to canonicalize URLs before dedup, but LinkedIn's URL scheme changes periodically. If you see the same post appearing twice, check whether the URLs differ only in a param not in the strip list and add it to `strip_tracking()` in `aggregate.py`. |
| Duplicate leads after a company rebrand | Dedup is `domain`-first. If a company changes domains, the aggregator treats it as a new lead. Manual reconciliation only — no automatic fix. |
| Multiple machines writing the same `leads.csv` | Not supported. Single-writer assumption. Put the CSV behind a locking layer (Google Sheets export, `flock`, etc.) or partition per machine. |
