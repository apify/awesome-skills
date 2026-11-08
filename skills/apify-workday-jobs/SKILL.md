---
name: apify-workday-jobs
description: "Search and monitor public Workday (myworkdayjobs.com) job postings. Returns flat rows with requisition IDs, source URLs, locations and salary fields. Uses the Apify Actor redomic/workday-jobs. Use when the user asks to 'workday jobs', 'workday scraper', 'myworkdayjobs', or wants Workday Jobs Scraper results as structured JSON or CSV."
metadata:
  category: data-extraction
  keywords: "workday jobs, workday scraper, myworkdayjobs"
author: Redomic
author_url: https://apify.com/redomic
---

# Workday Jobs Scraper

Search and monitor public Workday (myworkdayjobs.com) job postings. Returns flat rows with requisition IDs, source URLs, locations and salary fields.

Disclosure: the routed Actor, `redomic/workday-jobs`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get Workday Jobs Scraper results for startUrls https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite; mode search; maxItems 10; includeDetails False"
- "Get Workday Jobs Scraper results for startUrls https://salesforce.wd12.myworkdayjobs.com/External_Career_Site; mode search; locations Brazil; maxItems 10"
- "Get Workday Jobs Scraper results for startUrls https://mastercard.wd1.myworkdayjobs.com/CorporateCareers; mode search; searchText engineer; maxItems 10"

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

- `startUrls` (array): Workday career site URLs to scrape (myworkdayjobs.com, including wd1-wd5/wd10x/wd12 hosts) or direct wday/cxs jobs URLs. Tenant and site are detected automatically. The legacy companies field is merge
- `companies` (array): Legacy alias merged into startUrls. Prefer startUrls for new runs.
- `mode` (string): search returns matching jobs; monitor reports only new, changed and removed jobs since the previous run (state stored in a named key-value store).
- `searchText` (string): Text passed to Workday searchText. Leave empty to list jobs.
- `locations` (array): Keep only jobs whose locations match any of these values (case-insensitive). Country names and cities can match; matching is applied to location text.
- `postedWithinDays` (integer): Keep only jobs posted within the last N days when Workday provides a parseable posting age/date. Leave empty for every open job.
- `includeDetails` (boolean): Fetch each job's detail endpoint for full description, locations, requisition fields and source URLs. Slower but more complete.
- `maxItems` (integer): Upper limit on job rows returned per site (and what you pay for in search mode). Default 100, maximum 1000.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Workday Jobs Scraper | `redomic/workday-jobs` | community | workday jobs |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/workday-jobs" \
      -i '{"startUrls": ["https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite"], "mode": "search", "includeDetails": true, "maxItems": 100}' \
      --json \
      --user-agent apify-awesome-skills/apify-workday-jobs \
      2>/dev/null

    apify actors info "redomic/workday-jobs" --input --json \
      --user-agent apify-awesome-skills/apify-workday-jobs 2>/dev/null

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-workday-jobs 2>/dev/null
