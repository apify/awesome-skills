---
name: apify-seek-jobs
description: "Search SEEK, the main job board in Australia and New Zealand, and get job listings as JSON with no SEEK account or cookies, using the Apify Actor krammer/seek-jobs-scraper. Returns title, company, location, salary text and parsed salary range, work type, work arrangement (on-site, hybrid, remote), classification, posting date and, optionally, the full job description and apply link. Filters: keywords, one or more locations, country (AU or NZ), days since posting, work type, work arrangement, classification and salary bracket. $0.0016 per delivered job, no start fee. Use when the user says find jobs in Sydney, Melbourne, Brisbane, Perth or Auckland, search SEEK, Australian job market, NZ job listings, compare salaries for a role across Australian cities, export SEEK jobs to CSV, or watch SEEK for new postings. The routed Actor is built by this skill's author (see Disclosure)."
author: krammer0
author_url: https://github.com/krammer0
license: MIT
metadata:
  category: data-extraction
  keywords: "seek, seek-jobs, australia-jobs, new-zealand-jobs, job-listings, job-search, salary-data, job-market, recruiting, job-board, no-login, sydney, melbourne, auckland"
---

# SEEK Job Listings (Australia and New Zealand)

Get SEEK job listings as structured rows: one row per job, with salary, work type and the full description. No SEEK account, cookies or API key. SEEK shows at most 500 jobs per search, so a broad search returns a sample of the market, not every job.

**Disclosure:** the routed Actor `krammer/seek-jobs-scraper` is built and published by the author of this skill. No affiliate or referral parameters are used on any link in this skill.

## Example prompts

Prompts this skill handles:

- "Find data engineer jobs in Sydney posted in the last 7 days, with salary."
- "Compare how many nurse jobs there are in Sydney, Melbourne and Brisbane."
- "List remote data analyst jobs in New Zealand, newest first, as CSV."

Out of scope (the boundary):

- Jobs outside Australia and New Zealand. Use a Google Jobs or LinkedIn Actor instead.
- Applicant counts, recruiter emails or anything behind a SEEK login. The Actor reads public job pages only.
- Applying to jobs. The Actor only reads.

## Prerequisites

- Apify account ([sign up](https://apify.com)). Free Apify plans can use up to $1.00 of this Actor each month, about 600 jobs.
- Authentication via `apify login`, or an `APIFY_TOKEN` environment variable (Apify Console, Settings, Integrations).

## Actor routing

| User need | Actor ID | Tier | Billed event |
|-----------|----------|------|--------------|
| SEEK job listings in AU or NZ, with or without the full description | `krammer/seek-jobs-scraper` | community | `job` $0.0016 per delivered job, no start fee |

## Workflow

1. Get the search: keywords, city or region (`Sydney NSW`, `Melbourne VIC`), country (`AU` default, or `NZ`), and how recent.
2. Check the live input schema before you build the input:

        apify actors info "krammer/seek-jobs-scraper" --input --json \
          --user-agent apify-awesome-skills/apify-seek-jobs 2>/dev/null

3. Estimate the cost: `maxResults` × $0.0016. Start small (`maxResults` 20–50). Ask the user before a run above about $1.
4. Run the Actor and read the dataset:

        apify actors call "krammer/seek-jobs-scraper" \
          -i '{"keywords": "data engineer", "location": "Sydney NSW", "dateRange": "7", "maxResults": 50}' \
          --json --user-agent apify-awesome-skills/apify-seek-jobs 2>/dev/null

    `DATASET_ID` is `storage.defaultDatasetId` in the JSON that `actors call` prints; `run.status` must be `SUCCEEDED`.

        apify datasets get-items DATASET_ID --format json \
          --user-agent apify-awesome-skills/apify-seek-jobs 2>/dev/null

5. Deliver: number of jobs, a table (title, company, location, salary text), and the dataset ID.

## Input fields

| Field | Default | Notes |
|---|---|---|
| `keywords` | — | Search words. |
| `location` | — | City, state or region. A JSON list such as `["Sydney NSW", "Melbourne VIC"]` runs one search per location. Empty = whole country. |
| `country` | `AU` | `AU` (seek.com.au) or `NZ` (seek.co.nz). |
| `dateRange` | `""` | `""`, `1`, `3`, `7`, `14` or `31` days. |
| `workType` | `""` | `242` full time, `243` part time, `244` contract/temp, `245` casual/vacation. |
| `workArrangement` | `""` | `1` on-site, `2` hybrid, `3` remote. |
| `sortMode` | `relevance` | `relevance` or `date`. |
| `maxResults` | `100` | `0` = all, up to SEEK's 500 per search. |
| `includeDetails` | `true` | Full description and apply link. Set `false` for a faster list. |

## Output fields

`jobId`, `title`, `canonicalUrl`, `company`, `location`, `salaryText`, `salaryMin`, `salaryMax`, `salaryCurrency`, `salaryType` (`year`, `hour`…), `employmentType`, `workArrangement`, `category`, `subCategory`, `postedDate`, `applyUrl`, `description`, `detailFetched`.

A value SEEK does not publish is `null`. `detailFetched: false` means the description page could not be read; the listing fields are still delivered and charged.

## Calling Actors — other interfaces

- Apify MCP connector: `https://mcp.apify.com/?tools=krammer/seek-jobs-scraper` ([docs](https://docs.apify.com/platform/integrations/mcp)).
- [mcpc](https://github.com/apify/mcpc) or any MCP client.

## Troubleshooting

- **0 jobs:** the keyword and location are too narrow, or `dateRange` is too short. Clear `dateRange` or widen the location.
- **Exactly 500 jobs:** SEEK's limit per search. Split by location, `workType` or `dateRange`.
- **Many `detailFetched: false`:** the description pages were busy. Run again later, or set `includeDetails` to `false` if the list is enough.
- **Salary is `null`:** the employer did not publish one. `salaryText` may still have free text.
