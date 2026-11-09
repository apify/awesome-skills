---
name: apify-job-postings-dataset
description: "328,000 open jobs from 11,000 company career sites (Greenhouse, Lever, Ashby), updated daily with first-seen and closed dates. Bulk export or daily new/closed delta. $0.002/job. Uses the Apify Actor redomic/job-postings-dataset. Use when the user asks to 'job postings dataset', 'job postings data', 'jobs dataset', or wants Job Postings Dataset: 328k Open Jobs, Updated Daily results as structured JSON or CSV."
metadata:
  category: data-extraction
  keywords: "job postings dataset, job postings data, jobs dataset"
author: Redomic
author_url: https://apify.com/redomic
---

# Job Postings Dataset: 328k Open Jobs, Updated Daily

328,000 open jobs from 11,000 company career sites (Greenhouse, Lever, Ashby), updated daily with first-seen and closed dates. Bulk export or daily new/closed delta. $0.002/job.

Disclosure: the routed Actor, `redomic/job-postings-dataset`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get Job Postings Dataset: 328k Open Jobs, Updated Daily results for mode snapshot; countries Germany; roleFamilies Engineering; remoteOnly True"
- "Get Job Postings Dataset: 328k Open Jobs, Updated Daily results for mode new; newWithinDays 3; companies anthropic; maxItems 10"
- "Get Job Postings Dataset: 328k Open Jobs, Updated Daily results for mode changes; companies spotify; maxItems 20"

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

- `mode` (string): snapshot = every open job matching filters. new = jobs first seen within newWithinDays. changes = stateful monitor: returns jobs new and jobs closed since the previous run with the same filters (first
- `newWithinDays` (integer): For mode 'new': jobs first seen in the last N days. Default 1. Ignored in other modes.
- `companies` (array): Limit to these companies (board token or company name). Empty = all.
- `ats` (array): Limit to Greenhouse, Lever or Ashby. Empty = all three.
- `countries` (array): Keep jobs whose location mentions any of these countries (e.g. Germany, United States, UK). Matched as words in the location text.
- `locations` (array): Keep jobs whose location contains any of these (city/region text, e.g. Berlin, EMEA).
- `roleFamilies` (array): Job function (e.g. Engineering, Sales, Data/Analytics). 'Engineering' covers engineering families. Empty = all.
- `seniority` (array): e.g. Junior, Mid, Senior, Lead/Principal, Intern. Empty = all.
- `remoteOnly` (boolean): Only remote jobs.
- `hasSalary` (boolean): Only jobs that publish a pay range.
- `postedWithinDays` (integer): Only jobs posted in the last N days. 0 = any date.
- `includeAggregators` (boolean): Aggregator/staffing boards re-post other companies' jobs and are left out by default. Turn on to include them.
- `maxItems` (integer): Maximum job rows returned (and billed). 0 = no cap (returns every matching job; can be large).

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Job Postings Dataset: 328k Open Jobs, Updated Daily | `redomic/job-postings-dataset` | community | job postings dataset |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/job-postings-dataset" \
      -i '{"mode": "snapshot", "newWithinDays": 1, "remoteOnly": false, "hasSalary": false, "postedWithinDays": 0, "includeAggregators": false, "maxItems": 1000}' \
      --json \
      --user-agent apify-awesome-skills/apify-job-postings-dataset \
      2>/dev/null

    apify actors info "redomic/job-postings-dataset" --input --json \
      --user-agent apify-awesome-skills/apify-job-postings-dataset 2>/dev/null

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-job-postings-dataset 2>/dev/null
