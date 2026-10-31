---
name: apify-greenhouse-jobs-monitor
description: "Greenhouse jobs scraper for any company's careers board (Airbnb, Stripe, Discord and thousands more), with published salary ranges as numbers: min, max, currency, period. Flat rows with title, location, posting date, apply link. Monitor mode returns only new, changed and removed jobs. Uses the Apify Actor redomic/greenhouse-jobs-monitor. Use when the user asks to 'greenhouse jobs', 'greenhouse', or wants Greenhouse Jobs Scraper with Salaries results as structured JSON or CSV."
metadata:
  category: data-extraction
  keywords: "greenhouse jobs, greenhouse, greenhouse jobs monitor"
author: Redomic
author_url: https://apify.com/redomic
---

# Greenhouse Jobs Scraper with Salaries

Greenhouse jobs scraper for any company's careers board (Airbnb, Stripe, Discord and thousands more), with published salary ranges as numbers: min, max, currency, period. Flat rows with title, location, posting date, apply link. Monitor mode returns only new, changed and removed jobs.

Disclosure: the routed Actor, `redomic/greenhouse-jobs-monitor`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get Greenhouse Jobs Scraper with Salaries results for boards airbnb; mode jobs; maxItems 15"
- "Get Greenhouse Jobs Scraper with Salaries results for boards stripe; mode jobs; search engineering; maxItems 20"
- "Get Greenhouse Jobs Scraper with Salaries results for boards figma; mode jobs; maxItems 10"

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

- `boards` (array): Company career-page slugs on Greenhouse. The part after boards.greenhouse.io/ — for example airbnb, stripe, greenhouse. You can also paste full board or job URLs; only the slug is kept.
- `mode` (string): jobs lists every open job; detail fetches full descriptions for specific jobIds; monitor reports only new, changed and removed jobs since the last run.
- `jobIds` (array): For mode 'detail': the Greenhouse job ids to fetch full detail for.
- `search` (string): Keep only jobs whose title, location or department (or description, when included) contains this text. Case-insensitive. Leave empty for every open job.
- `includeDescription` (boolean): Add the full job description (plain text and HTML), department and offices to every row, and read pay ranges written in the description when the company did not publish a structured one. Off by defaul
- `maxItems` (integer): Upper limit on job rows per board (and so on what you pay): 3 boards x 100 = at most 300 rows. Default 100, maximum 1000.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Greenhouse Jobs Scraper with Salaries | `redomic/greenhouse-jobs-monitor` | community | greenhouse jobs |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/greenhouse-jobs-monitor" \
      -i '{"boards": ["airbnb"], "mode": "jobs", "includeDescription": false, "maxItems": 100}' \
      --json \
      --user-agent apify-awesome-skills/apify-greenhouse-jobs-monitor \
      2>/dev/null

    apify actors info "redomic/greenhouse-jobs-monitor" --input --json \
      --user-agent apify-awesome-skills/apify-greenhouse-jobs-monitor 2>/dev/null

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-greenhouse-jobs-monitor 2>/dev/null
