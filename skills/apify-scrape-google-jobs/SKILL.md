---
name: apify-scrape-google-jobs
description: Scrape Google Jobs listings into structured JSON with the Apify Google Jobs Scraper Actor (johnvc/Google-Jobs-Scraper). Give a job title or search query plus an optional location, and get one row per listing with title, company_name, location, source platform, full description, job_highlights, posted_at, schedule_type, and direct apply_options links. Use when the user wants to scrape google jobs, export Google Jobs results to JSON or CSV, build a job listings dataset, pull openings for a role or city, or asks for a Google Jobs scraper, job scraper, or job scraping workflow. Pay-per-page billing, MCP-ready for Claude and other AI agents.
author: John Cole
author_url: https://github.com/johnisanerd
license: MIT
metadata:
  version: "1.0"
---

# Scrape Google Jobs: Listings to Structured JSON

Scrape Google Jobs into clean JSON with the Apify Google Jobs Scraper. Give it a job title and an optional location, and get one flat row per listing: title, company, source platform, full description, highlights, posting age, and direct apply links.

## When to use this skill

- The user wants to scrape Google Jobs results (to JSON, CSV, a sheet, or a database).
- They want openings for a role, company, city, or country as a dataset.
- They want job listings for research, recruiting pipelines, or market scans.
- They ask for a "Google Jobs scraper", "job scraper", or "job scraping".

Not for: salary analytics (no numeric salary field), LinkedIn-only listings (use the LinkedIn Jobs API), or employer reviews (use the Glassdoor Reviews API).

## What you get (one row per listing)

`title`, `company_name`, `location`, `via` (source platform), `description`, `job_highlights` (Qualifications, Responsibilities, Benefits), `extensions` (raw tags such as "Full-time", "3 days ago"), `detected_extensions` (`posted_at`, `schedule_type`, plus benefit flags such as `health_insurance` only when a listing advertises them), `apply_options` (per-platform title plus direct link), `job_id`, `share_link`. Run metadata includes `total_jobs_found` and `pages_processed`.

## Prerequisites

- Apify account (sign up at https://apify.com?fpr=9n7kx3&fp_sid=awesomeskills).
- Authentication via `apify login`, or an `APIFY_TOKEN` environment variable (Apify Console, Settings, Integrations).

## The Actor

- Store page: https://apify.com/johnvc/Google-Jobs-Scraper?fpr=9n7kx3&fp_sid=awesomeskills
- Actor ID: `johnvc/Google-Jobs-Scraper`
- Pricing: pay per page of results processed (see `references/gotchas.md`).

## Run it with the Apify CLI

Scrape a role in a city:

```bash
apify actors call "johnvc/Google-Jobs-Scraper" -i '{"query":"software engineer","location":"Austin, TX","num_results":50}' \
  --json \
  --user-agent apify-awesome-skills/apify-scrape-google-jobs \
  2>/dev/null
```

Scrape a country-wide search on a local Google domain:

```bash
apify actors call "johnvc/Google-Jobs-Scraper" -i '{"query":"data analyst","location":"United Kingdom","google_domain":"google.co.uk","num_results":100}' \
  --json \
  --user-agent apify-awesome-skills/apify-scrape-google-jobs \
  2>/dev/null
```

Every call carries the three flags this repo expects: `--json`, `--user-agent apify-awesome-skills/apify-scrape-google-jobs`, and `2>/dev/null`.

## Run it from Claude or another AI agent (MCP)

The Actor is MCP-ready. Add the hosted server URL:

`https://mcp.apify.com/?tools=actors,docs,johnvc/Google-Jobs-Scraper`

Then ask, for example: "Scrape Google Jobs for remote customer service roles and export the listings as JSON." MCP setup docs: https://docs.apify.com/platform/integrations/mcp

## Workflow

1. Build the query. `query` is the only required field: a job title, skill, or company. Add `location` (city, state, or country) to narrow it.
2. Bound the volume. Set `num_results` (default 100, about 10 listings per page) and, to hard-cap pages, `max_pagination`. Start small: 30 to 50 results is one to five pages.
3. Localize when needed. Pick `google_domain` and `language` for non-US markets; add `include_lrad` plus `lrad_value` for a radius search around the location.
4. Estimate cost, then confirm with the user if the run is large. See `references/gotchas.md`.
5. Run the Actor and read the dataset. Deliver rows as JSON or CSV, or hand back the dataset link. Dedupe across runs on `job_id`.

## Inputs

- `query` (string, required): job title, skill, or company
- `location` (string): city, state, or country
- `country` (enum, 11 values) and `language` (enum, 100 plus values)
- `google_domain` (enum, default `google.com`)
- `num_results` (integer, default 100): cap on listings returned
- `max_pagination` (integer, default 0 = fetch all available up to `num_results`)
- `include_lrad` (boolean) plus `lrad_value` (string, km): radius search
- `max_delay` (integer, default 1): seconds between page requests

## Cost

Billing is per page of results processed, roughly 10 listings per page. A 50-result run is about five pages. Estimate first and confirm large runs; live prices and thresholds are in `references/gotchas.md`.

## Honest limits

- No numeric salary field and no experience-level field; do not promise salary or seniority filters.
- `posted_at` is a relative string such as "3 days ago", so freshness filtering happens on your side after the run.
- Google Jobs inventory varies by region and query; `num_results` is a cap, not a guarantee.

## Troubleshooting

- No results: broaden the query, or drop the location. For some non-US cities the Actor already retries with the location merged into the query.
- Fewer results than `num_results`: normal; Google had fewer listings for that query.
- Budget warning at startup: raise the run's budget limit, or lower `num_results` / set `max_pagination`.

See `references/gotchas.md` for cost guardrails and error recovery, and `references/actor-index.md` for the Actor routing table.

## Related job-data Actors

- Google Jobs Scraper API, pay per result edition: https://apify.com/johnvc/google-jobs-scraper---pay-per-result?fpr=9n7kx3&fp_sid=awesomeskills
- LinkedIn Jobs API: https://apify.com/johnvc/linkedin-jobs-api?fpr=9n7kx3&fp_sid=awesomeskills
- Glassdoor Reviews API: https://apify.com/johnvc/glassdoor-reviews-api?fpr=9n7kx3&fp_sid=awesomeskills
