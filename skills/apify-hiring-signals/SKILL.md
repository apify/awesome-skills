---
name: apify-hiring-signals
description: "Turn a list of target companies into company-level hiring signals from their own ATS and Workday career sites: open-job counts, posts in the last 7/30 days, new/changed/closed jobs since the last run, long-open and repost flags, and an optional explainable 0–100 signal score with plain-English reasons. Routes Greenhouse, Lever, Ashby, Workable, SmartRecruiters and Recruitee boards to goldenrod_serrano/ats-hiring-signals, and *.myworkdayjobs.com / *.myworkdaysite.com sites to goldenrod_serrano/workday-hiring-signals (with server-side country/city filters past Workday's 2,000-job list cap). Use when the user asks for hiring signals, recruiting BD watchlists, sales trigger lists from job openings, company hiring momentum, monitor new and closed roles, Workday jobs by country (GCC, UAE, India…), or ATS + Workday in one workflow. Not for LinkedIn/Indeed/Glassdoor scrapes or applying to jobs."
author: Paopao Studio
author_url: https://github.com/paopao-studio-ai
metadata:
  category: data-extraction
  keywords: "hiring-signals, ats, workday, greenhouse, lever, ashby, workable, smartrecruiters, recruitee, recruiting-bd, sales-triggers, job-change-tracking, company-summary, careers-page, alternative-data, apify"
---

# Company hiring signals (ATS + Workday)

Disclosure: the author of this skill owns both Actors it routes to (`goldenrod_serrano/ats-hiring-signals` and `goldenrod_serrano/workday-hiring-signals`). They are pay-per-event Actors on the Apify Store; no referral or tracking parameters are used anywhere in this skill.

Focus: **company-level hiring signals** from employers' own public job boards — not a multi-board job search across LinkedIn/Indeed/Glassdoor.

How this differs from nearby skills:

| Skill | What it optimizes for | This skill instead |
|-------|----------------------|--------------------|
| `apify-job-boards` | Role + location scrapes across LinkedIn/Indeed/Glassdoor/remote boards | Named companies' **ATS / Workday** boards → per-company summaries |
| `apify-jobs-data` | Broad job-market pulls and analysis across many job sites | Hiring **momentum / change / score** on a watch list you already have |
| `apify-ashby-jobs-scraper` | Ashby-only jobs or Ashby customer discovery | Six ATS **plus** Workday, with shared change-tracking and signal-score fields |

## Example prompts

Prompts this skill handles:

- "Watch these 40 SaaS companies on Greenhouse/Lever/Ashby and give me a hiring-signal score for sales outreach."
- "Pull NVIDIA and Mastercard Workday jobs in GCC only, then show new and closed roles since last week."
- "For this account list, summarize open jobs, posts in the last 30 days, and long-open roles — one row per company."

Out of scope (the boundary):

- "Scrape software engineer jobs in Austin from LinkedIn and Indeed" → use `apify-job-boards` / `apify-jobs-data`.
- Applying to jobs, scraping candidate profiles, or anything that needs a login, CAPTCHA, or personal applicant data. These Actors read public employer boards only; no login, no cookies, no proxy.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

Never paste a token into a URL or into a file inside this skill; pass it as `Authorization: Bearer` (the CLI does this for you).

## Workflow

```
Task Progress:
- [ ] Step 1: Collect the watch list and goal
- [ ] Step 2: Route ATS vs Workday
- [ ] Step 3: Fetch live schemas, build input, state cost
- [ ] Step 4: Run (cap spend), deliver summaries + optional jobs
```

### Step 1: Collect the watch list and goal

Ask as one block before any paid run:

1. **Companies / sites** — ATS board URLs or slugs (e.g. `greenhouse:stripe`, `https://jobs.ashbyhq.com/ramp`) and/or Workday career URLs (e.g. `https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite`).
2. **Goal** — company summaries only, job rows, change tracking (new/changed/closed), and/or explainable signal score.
3. **Filters** — keywords, countries/cities (Workday), seniority, remote-only, posted-within days.
4. **Budget** — max companies this run and whether to include descriptions (extra payload / Workday detail calls).

### Step 2: Route ATS vs Workday

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Greenhouse, Lever, Ashby, Workable, SmartRecruiters, Recruitee boards | `goldenrod_serrano/ats-hiring-signals` | community | Paste board URL, `ats:slug`, bare slug (tries all six), or a careers page URL |
| Workday (`*.myworkdayjobs.com`, `*.myworkdaysite.com`) | `goldenrod_serrano/workday-hiring-signals` | community | Server-side country/city filters (incl. shortcuts like `GCC`, `UAE`, `SEA`); works past Workday's ~2,000-job list cap |

Split a mixed list: ATS entries → first Actor; Workday URLs → second. Both expose the same signal ideas (`company_summary`, optional `changeTracking`, optional `signalScoring`).

Live schema always wins over examples in this file:

    apify actors info "goldenrod_serrano/ats-hiring-signals" --input --json \
      --user-agent apify-awesome-skills/apify-hiring-signals 2>/dev/null

    apify actors info "goldenrod_serrano/workday-hiring-signals" --input --json \
      --user-agent apify-awesome-skills/apify-hiring-signals 2>/dev/null

### Step 3: Build input and state the cost

Both Actors are **PAY_PER_EVENT** (Store free-tier list prices as of the Actor pages; confirm with `apify actors info`):

| Event | Free-tier list price (USD) |
|-------|----------------------------|
| `job` row | ~$0.001 |
| `company-summary` row | ~$0.005 |
| Actor start | small per-GB start event |

Rough estimate before run: `(companies × $0.005) + (expected job rows × $0.001)`. Warn above ~$5; require explicit confirmation above ~$20. Present as a rough estimate, not a guarantee. Set Apify **max charge per run** so the Actor stops cleanly.

**ATS example** (summaries + optional score; keep job volume capped on first runs):

```json
{
  "companies": ["greenhouse:stripe", "https://jobs.ashbyhq.com/ramp", "lever:palantir"],
  "outputJobs": false,
  "outputCompanySummary": true,
  "signalScoring": true,
  "scoreFunctions": ["sales"],
  "changeTracking": false,
  "maxJobsPerCompany": 0
}
```

**Workday example** (country filter + change tracking on a named state key):

```json
{
  "careerSites": [
    "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite",
    "https://mastercard.wd1.myworkdayjobs.com/CorporateCareers"
  ],
  "locations": ["GCC"],
  "outputJobs": true,
  "outputCompanySummary": true,
  "changeTracking": true,
  "stateKey": "gcc-weekly",
  "signalScoring": true,
  "scoreFunctions": ["sales"],
  "maxJobsPerCompany": 50,
  "includeDetails": false
}
```

Useful shared flags (names match the live schemas):

- `changeTracking` + `stateKey` — first run is baseline; later runs emit new / changed jobs and free `job_closed` rows when the scan is complete.
- `signalScoring` — adds `signal_score` (0–100), `signal_tier` (hot/warm/cool/cold), and `score_reasons`.
- `onlyNewSinceLastRun` — older monitor mode (new jobs only); when `changeTracking` is on it replaces this mode for that run.
- `addTickers` — optional SEC ticker / CIK on summaries via public `company_tickers.json` (conservative exact-name match; unmatched stay null).

### Step 4: Run and deliver

```bash
apify actors call "goldenrod_serrano/ats-hiring-signals" \
  --input '{"companies":["greenhouse:anthropic"],"outputJobs":false,"outputCompanySummary":true,"signalScoring":true}' \
  --user-agent apify-awesome-skills/apify-hiring-signals \
  --json 2>/dev/null
```

```bash
apify actors call "goldenrod_serrano/workday-hiring-signals" \
  --input '{"careerSites":["https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite"],"locations":["GCC"],"outputCompanySummary":true,"maxJobsPerCompany":20}' \
  --user-agent apify-awesome-skills/apify-hiring-signals \
  --json 2>/dev/null
```

After the run finishes, fetch items:

```bash
apify datasets get-items DATASET_ID --format json \
  --user-agent apify-awesome-skills/apify-hiring-signals 2>/dev/null
```

Deliver:

1. Count of `company_summary` / `job` / `job_closed` / `error` rows.
2. Top companies by `signal_score` or `hiring_signal_score` when scoring was on.
3. Dataset / Console link.
4. Any `type: "error"` inputs (board not found) — never charged.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Multi-ATS hiring signals | `goldenrod_serrano/ats-hiring-signals` | community | Greenhouse, Lever, Ashby, Workable, SmartRecruiters, Recruitee |
| Workday hiring signals + country filter | `goldenrod_serrano/workday-hiring-signals` | community | myworkdayjobs / myworkdaysite with server-side location facets |

Full routing notes: [references/actor-index.md](references/actor-index.md). Cost traps and recovery: [references/gotchas.md](references/gotchas.md).

## Calling Actors — choose your interface

### Option A: Apify CLI (recommended)

Every `apify` CLI call in this skill uses:

- `--user-agent apify-awesome-skills/apify-hiring-signals`
- `--json` (or `--format json` for `datasets get-items`)
- `2>/dev/null`

### Option B: Apify MCP connector

Hosted MCP: <https://mcp.apify.com>. Docs: <https://docs.apify.com/platform/integrations/mcp>.

### Option C: MCP client of your choice (e.g. `mcpc`)

See <https://github.com/apify/mcpc>.

## Troubleshooting

- Empty board / `error` row → wrong slug or private board; prefer `ats:slug` or the full board URL over a bare company name.
- Huge Workday site truncated at ~2,000 → add `locations` or `searchText` so Workday filters server-side.
- No closed jobs on a tracked run → scan may be incomplete (`scan_complete` false / Workday capped); Actors refuse to guess closures.
- Cost surprise → turn `outputJobs` off for summary-only runs; set `maxJobsPerCompany`; leave `includeDescription` / `includeDetails` off unless needed.
