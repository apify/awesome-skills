---
name: apify-personio-jobs
description: "Scrape open jobs from Personio company career pages (jobs.personio.de/.com XML feeds). Returns clean rows with title, department, office, employment, seniority, dates, URLs and descriptions. Supports monitor mode for new/changed/removed jobs. Uses the Apify Actor redomic/personio-jobs. Use when the user asks to 'personio jobs', 'personio scraper', 'personio jobs api', or wants Personio Jobs Scraper results as structured JSON or CSV."
metadata:
  category: data-extraction
  keywords: "personio jobs, personio scraper, personio jobs api"
author: Redomic
author_url: https://apify.com/redomic
---

# Personio Jobs Scraper

Scrape open jobs from Personio company career pages (jobs.personio.de/.com XML feeds). Returns clean rows with title, department, office, employment, seniority, dates, URLs and descriptions. Supports monitor mode for new/changed/removed jobs.

Disclosure: the routed Actor, `redomic/personio-jobs`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get Personio Jobs Scraper results for companies personio-gmbh; mode jobs; maxItems 10; includeDescription True"
- "Get Personio Jobs Scraper results for companies https://join.jobs.personio.de; mode jobs; maxItems 10; includeDescription True"
- "Get Personio Jobs Scraper results for companies xempus; mode jobs; search Product; maxItems 10"

Out of scope (the boundary):

- Personal contact data or logged-in content: this Actor reads public pages only.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via `apify login`, the `APIFY_TOKEN` environment variable, or a token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. Map the request onto the input fields below; fetch the live schema for anything unusual.
2. Run the Actor and read its dataset. Rows with a `_status` field are per-input status rows, not data.
3. Deliver a count, a short table of the key fields, and the dataset link or an export.

## Input

- `companies` (array): Personio company subdomains or career-page URLs. The part before .jobs.personio.de/.com (for example personio-gmbh, join). You can also paste full board URLs or a single job URL; the subdomain (and jo
- `mode` (string): jobs lists every open job; monitor reports only new, changed and removed jobs since the last run (stateful). Unchanged monitor rows are not charged.
- `search` (string): Keep only jobs whose title, location, office, department or description contains this text (case-insensitive). Leave empty for every open job.
- `postedSinceDays` (integer): Keep only jobs created within the last N days (by createdAt). Leave empty for every open job.
- `locations` (array): Keep only jobs whose office/location/additional offices contain one of these values (case-insensitive, OR). Leave empty for every location.
- `departments` (array): Keep only jobs whose department or recruiting category contains one of these values (case-insensitive, OR). Leave empty for every department.
- `employmentTypes` (array): Keep only jobs with one of these Personio employment types (permanent, working_student, intern, freelance, temporary; case-insensitive, OR). Leave empty for every type.
- `schedules` (array): Keep only jobs with one of these schedules (full-time, part-time; case-insensitive, OR). Leave empty for every schedule.
- `seniorities` (array): Keep only jobs with one of these Personio seniority values (entry-level, experienced, student, executive, ...; case-insensitive, OR). Leave empty for every seniority.
- `includeDescription` (boolean): Add the full job description as HTML and plain text (plus per-section HTML) to every row. On by default.
- `maxItems` (integer): Upper limit on job rows per company (and on what you pay). Default 100, maximum 5000.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Personio Jobs Scraper | `redomic/personio-jobs` | community | personio jobs |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/personio-jobs" \
      -i '{"companies": ["personio-gmbh"], "mode": "jobs", "includeDescription": true, "maxItems": 100}' \
      --json \
      --user-agent apify-awesome-skills/apify-personio-jobs \
      2>/dev/null

    apify actors info "redomic/personio-jobs" --input --json \
      --user-agent apify-awesome-skills/apify-personio-jobs 2>/dev/null

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-personio-jobs 2>/dev/null
