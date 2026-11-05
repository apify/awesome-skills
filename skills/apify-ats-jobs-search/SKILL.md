---
name: apify-ats-jobs-search
description: "Search 328,000+ open jobs from 11,000+ companies on Greenhouse, Lever and Ashby in one run. Filter by keyword, location, remote, salary, seniority and posting date. Flat rows with annual salary, days open and company hiring velocity. Lead-list mode and daily new-jobs monitor. Uses the Apify Actor redomic/ats-jobs-search. Use when the user asks to 'greenhouse jobs', 'lever jobs', 'ats jobs', or wants ATS Jobs Search: Greenhouse, Lever & Ashby Jobs API results as structured JSON or CSV."
metadata:
  category: data-extraction
  keywords: "greenhouse jobs, lever jobs, ats jobs, ats jobs search"
author: Redomic
author_url: https://apify.com/redomic
---

# ATS Jobs Search: Greenhouse, Lever & Ashby Jobs API

Search 328,000+ open jobs from 11,000+ companies on Greenhouse, Lever and Ashby in one run. Filter by keyword, location, remote, salary, seniority and posting date. Flat rows with annual salary, days open and company hiring velocity. Lead-list mode and daily new-jobs monitor.

Disclosure: the routed Actor, `redomic/ats-jobs-search`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get ATS Jobs Search: Greenhouse, Lever & Ashby Jobs API results for keywords python, backend; remoteOnly True; hasSalary True; salaryCurrency USD"
- "Get ATS Jobs Search: Greenhouse, Lever & Ashby Jobs API results for keywords data engineer; locations Berlin; maxItems 10"
- "Get ATS Jobs Search: Greenhouse, Lever & Ashby Jobs API results for locations London; firstSeenWithinDays 1; maxItems 10"

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

- `keywords` (array): Return jobs whose title contains ANY of these words (whole words, case-insensitive). Empty = every job.
- `excludeKeywords` (array): Drop jobs whose title contains any of these words, e.g. intern, senior, manager.
- `keywordsInDepartment` (boolean): Match keywords against the department/team as well as the title (e.g. 'Sales' finds every role in a Sales team).
- `locations` (array): Keep jobs whose location contains ANY of these (city, country or region text, e.g. Berlin, United States, London, EMEA).
- `excludeLocations` (array): Drop jobs whose location contains any of these, e.g. India, Philippines.
- `remoteOnly` (boolean): Only remote jobs (workplace type Remote, or 'remote' in the location).
- `workplaceTypes` (array): Remote, Hybrid or Onsite. Empty = all.
- `employmentTypes` (array): Empty = all.
- `roleFamilies` (array): Job function. 'Engineering' covers every engineering family. Empty = all.
- `seniority` (array): Empty = all.
- `ats` (array): Limit to Greenhouse, Lever or Ashby companies. Empty = all three.
- `companies` (array): Limit to these companies: board token (as in boards.greenhouse.io/<token>) or company name. Empty = all 11,000+.
- `excludeCompanies` (array): Drop these companies (board token or name), e.g. job aggregators such as jobgether.
- `hasSalary` (boolean): Only jobs that publish a pay range.
- `minSalary` (integer): Keep jobs whose top of range, annualised (hourly x 2080, monthly x 12), is at least this. 0 = no minimum. Combine with salary currency.
- `salaryCurrency` (string): ISO currency code to keep, e.g. USD, EUR, GBP. Empty = any currency.
- `postedWithinDays` (integer): Only jobs the company posted in the last N days. 0 = any date.
- `firstSeenWithinDays` (integer): Only jobs that first appeared in our daily crawl in the last N days: genuinely new openings, even when the posted date is old or missing. 0 = any.
- `output` (string): 'companies' rolls the matching jobs up into one row per company: matching roles, new this week, pay range, top departments. Built for sales and recruiting lead lists.
- `groupSameTitle` (boolean): When a company posts the same title in many cities or countries, return it once with locationCount and otherLocations, and bill it once.
- `onlyNewSinceLastRun` (boolean): Schedule this daily: the first run saves a baseline, every later run returns only matching jobs that were not there last time. A quiet day returns just the free summary row. Jobs output only.
- `maxItems` (integer): Maximum rows returned (and billed).
- `sort` (string): Order of job rows.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| ATS Jobs Search: Greenhouse, Lever & Ashby Jobs API | `redomic/ats-jobs-search` | community | greenhouse jobs |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/ats-jobs-search" \
      -i '{"keywordsInDepartment": false, "remoteOnly": false, "hasSalary": false, "minSalary": 0, "postedWithinDays": 0, "firstSeenWithinDays": 0, "output": "jobs", "groupSameTitle": true, "onlyNewSinceLastRun": false, "maxItems": 100, "sort": "newest"}' \
      --json \
      --user-agent apify-awesome-skills/apify-ats-jobs-search \
      2>/dev/null

    apify actors info "redomic/ats-jobs-search" --input --json \
      --user-agent apify-awesome-skills/apify-ats-jobs-search 2>/dev/null

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-ats-jobs-search 2>/dev/null
