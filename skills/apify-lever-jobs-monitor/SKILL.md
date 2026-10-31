---
name: apify-lever-jobs-monitor
description: "Lever jobs scraper for any company's careers page (Palantir, Spotify, Zoox, Shield AI and thousands more): flat rows with title, team, location, workplace, commitment, apply link, salary as numbers and the full description merged. Monitor mode returns only new, changed and removed jobs. Uses the Apify Actor redomic/lever-jobs-monitor. Use when the user asks to 'lever jobs', 'lever', or wants Lever Jobs Scraper with Salaries results as structured JSON or CSV."
metadata:
  category: data-extraction
  keywords: "lever jobs, lever, lever jobs monitor"
author: Redomic
author_url: https://apify.com/redomic
---

# Lever Jobs Scraper with Salaries

Lever jobs scraper for any company's careers page (Palantir, Spotify, Zoox, Shield AI and thousands more): flat rows with title, team, location, workplace, commitment, apply link, salary as numbers and the full description merged. Monitor mode returns only new, changed and removed jobs.

Disclosure: the routed Actor, `redomic/lever-jobs-monitor`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get Lever Jobs Scraper with Salaries results for companies palantir; mode jobs; maxItems 15"
- "Get Lever Jobs Scraper with Salaries results for companies spotify; mode jobs; maxItems 15"
- "Get Lever Jobs Scraper with Salaries results for companies shieldai; mode jobs; maxItems 15; search engineer"

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

- `companies` (array): Lever company names: the part after jobs.lever.co/, for example palantir, spotify, zoox. You can also paste full careers or posting URLs; only the name is kept. EU-hosted companies (jobs.eu.lever.co) 
- `mode` (string): jobs lists every open job; monitor reports only new, changed (including a changed pay range) and removed jobs since the last run of the same company and keyword.
- `search` (string): Keep only jobs whose title, department, team, location, commitment, workplace type or description contains this text. Case-insensitive. Leave empty for every open job.
- `includeDescription` (boolean): Add the full description (opening, body, every section and closing, merged as plain text, plus the HTML) to each row. Off by default to keep rows small; the keyword filter searches descriptions either
- `maxItems` (integer): Upper limit on job rows per company (and so on what you pay): 3 companies x 100 = at most 300 rows. Default 100, maximum 1000.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Lever Jobs Scraper with Salaries | `redomic/lever-jobs-monitor` | community | lever jobs |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/lever-jobs-monitor" \
      -i '{"companies": ["palantir"], "mode": "jobs", "includeDescription": false, "maxItems": 100}' \
      --json \
      --user-agent apify-awesome-skills/apify-lever-jobs-monitor \
      2>/dev/null

    apify actors info "redomic/lever-jobs-monitor" --input --json \
      --user-agent apify-awesome-skills/apify-lever-jobs-monitor 2>/dev/null

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-lever-jobs-monitor 2>/dev/null
