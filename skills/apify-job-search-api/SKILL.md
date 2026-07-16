---
name: apify-job-search-api
description: Turn Google Jobs into a job search API for your app, AI agent, or alerts pipeline with the Apify Google Jobs Scraper Actor (johnvc/Google-Jobs-Scraper). Query by role and location with country, language, and radius filters, and get fresh structured listings back, including title, company_name, source platform, posted_at, schedule_type, and direct apply_options links, ready to dedupe by job_id and serve as a feed. Use when the user wants a job search api, a job postings API or job listings feed for an application or AI agent, wants to refresh a job board or job alerts programmatically, or asks which job search sites have an API. Pay-per-page billing, MCP-ready for Claude and other AI agents.
author: John Cole
author_url: https://github.com/johnisanerd
license: MIT
metadata:
  version: "1.0"
---

# Job Search API: A Live Job Feed From Google Jobs

Use Google Jobs as a job search API. One call takes a role and location and returns fresh, structured listings with direct apply links, ready to serve to an app, an AI agent, a job board, or an alerts pipeline.

## When to use this skill

- The user wants a job search API or a job postings feed for an application, bot, or AI agent.
- They want to refresh a job board, careers digest, or alerts pipeline on a schedule.
- They want fresh openings for a role filtered to a location, language, or radius.
- They ask "which job search sites have an API" or "how do I search job listings by API".

Not for: one-off bulk exports of a single search (use the scrape-google-jobs skill), salary analytics (no numeric salary field), or LinkedIn-only listings (use the LinkedIn Jobs API).

## What the feed returns (one row per listing)

`title`, `company_name`, `location`, `via` (source platform), `description`, `job_highlights`, `extensions`, `detected_extensions` (`posted_at`, `schedule_type`, plus benefit flags such as `health_insurance` only when a listing advertises them), `apply_options` (per-platform direct apply links), `job_id`, `share_link`. `job_id` is the dedupe key; `posted_at` ("3 days ago") is the freshness signal.

## Prerequisites

- Apify account (sign up at https://apify.com?fpr=9n7kx3&fp_sid=awesomeskills).
- Authentication via `apify login`, or an `APIFY_TOKEN` environment variable (Apify Console, Settings, Integrations).

## The Actor

- Store page: https://apify.com/johnvc/Google-Jobs-Scraper?fpr=9n7kx3&fp_sid=awesomeskills
- Actor ID: `johnvc/Google-Jobs-Scraper`
- Pricing: pay per page of results processed (see `references/gotchas.md`).

## Run it with the Apify CLI

One feed call, bounded to about three pages:

```bash
apify actors call "johnvc/Google-Jobs-Scraper" -i '{"query":"registered nurse","location":"Dallas, TX","num_results":30,"max_pagination":3}' \
  --json \
  --user-agent apify-awesome-skills/apify-job-search-api \
  2>/dev/null
```

Read the newest run's items later, for example from a scheduled run:

```bash
apify datasets get-items <DATASET_ID> --format json --user-agent apify-awesome-skills/apify-job-search-api 2>/dev/null
```

Every call carries the three flags this repo expects: `--json` (or `--format json`), `--user-agent apify-awesome-skills/apify-job-search-api`, and `2>/dev/null`.

## Run it from Claude or another AI agent (MCP)

The Actor is MCP-ready. Add the hosted server URL:

`https://mcp.apify.com/?tools=actors,docs,johnvc/Google-Jobs-Scraper`

Then ask, for example: "Search jobs for senior accountant roles in Chicago posted this week and give me the apply links." MCP setup docs: https://docs.apify.com/platform/integrations/mcp

## Workflow

1. Define the feed. One Actor input per feed: `query` (role or skill), `location`, and localization (`google_domain`, `language`) for non-US markets. A radius feed adds `include_lrad` and `lrad_value`.
2. Bound each poll. For a feed you refresh often, keep `num_results` at 20 to 50 and set `max_pagination` (2 to 5) as the hard cost cap per call.
3. Estimate cost per poll and per month, then confirm with the user. See `references/gotchas.md`.
4. Call the Actor, read the dataset, and post-process: dedupe against your store on `job_id`, parse `posted_at` relative ages ("3 days ago") to timestamps, and keep only rows newer than your last poll.
5. Serve the result. Hand rows to the app or agent, write them to your database, or deliver a digest. For recurring feeds, wrap the same input in an Apify Schedule or a cron job.

## Inputs

- `query` (string, required): role, skill, or company
- `location` (string): city, state, or country
- `country`, `language`, `google_domain` (enums): localization
- `num_results` (integer, default 100): cap per call, keep small for feeds
- `max_pagination` (integer): hard page cap per call, the cost bound
- `include_lrad` (boolean) plus `lrad_value` (string, km): radius feeds

## Cost

Billing is per page processed, roughly 10 listings per page, so a bounded feed poll of 30 results is about three pages. A daily 3-page poll is roughly 90 pages per month; estimate with the live per-page price in `references/gotchas.md` before scheduling.

## Honest limits

- This is a polled feed, not a push API: freshness is your poll interval.
- `posted_at` is a relative string; the workflow converts it client-side. There is no server-side date filter.
- No numeric salary field and no experience-level field.
- Inventory varies by region and query; some polls legitimately return nothing new.

## Troubleshooting

- Duplicate listings across polls: expected; dedupe on `job_id` before serving.
- Nothing new in a poll: normal for narrow queries; widen the query or slow the poll.
- Budget warning at startup: raise the run budget or lower `num_results` / `max_pagination`.

See `references/gotchas.md` for cost guardrails and error recovery, and `references/actor-index.md` for the Actor routing table.

## Related job-data Actors

- Google Jobs Scraper API, pay per result edition: https://apify.com/johnvc/google-jobs-scraper---pay-per-result?fpr=9n7kx3&fp_sid=awesomeskills
- LinkedIn Jobs API: https://apify.com/johnvc/linkedin-jobs-api?fpr=9n7kx3&fp_sid=awesomeskills
- Glassdoor Reviews API: https://apify.com/johnvc/glassdoor-reviews-api?fpr=9n7kx3&fp_sid=awesomeskills
