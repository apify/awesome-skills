---
name: apify-ashby-jobs-monitor
description: "Ashby jobs scraper for any startup careers board (OpenAI, Ramp, Notion and thousands more), with salary ranges as numbers: min, max, currency, period, plus equity and bonus flags. Flat rows with title, team, location, remote, apply link. Monitor mode returns only new, changed and removed jobs. Uses the Apify Actor redomic/ashby-jobs-monitor. Use when the user asks to 'ashby jobs', 'ashby', or wants Ashby Jobs Scraper with Salaries results as structured JSON or CSV."
metadata:
  category: data-extraction
  keywords: "ashby jobs, ashby, ashby jobs monitor"
author: Redomic
author_url: https://apify.com/redomic
---

# Ashby Jobs Scraper with Salaries

Ashby jobs scraper for any startup careers board (OpenAI, Ramp, Notion and thousands more), with salary ranges as numbers: min, max, currency, period, plus equity and bonus flags. Flat rows with title, team, location, remote, apply link. Monitor mode returns only new, changed and removed jobs.

Disclosure: the routed Actor, `redomic/ashby-jobs-monitor`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get Ashby Jobs Scraper with Salaries results for boards ramp; mode jobs; maxItems 15"
- "Get Ashby Jobs Scraper with Salaries results for boards openai; mode jobs; maxItems 15; search engineer"
- "Get Ashby Jobs Scraper with Salaries results for boards notion; mode jobs; maxItems 15"

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

- `boards` (array): Ashby job board names: the part after jobs.ashbyhq.com/, for example ramp, openai, notion. You can also paste full board or job URLs; only the name is kept.
- `mode` (string): jobs lists every open job; monitor reports only new, changed (including a changed pay range) and removed jobs since the last run of the same board and keyword.
- `search` (string): Keep only jobs whose title, department, team, location, workplace type or description contains this text. Case-insensitive. Leave empty for every open job.
- `includeDescription` (boolean): Add the full job description (plain text and HTML) to every row. Off by default to keep rows small; the keyword filter searches descriptions either way. No extra request: the board comes in one respon
- `maxItems` (integer): Upper limit on job rows per board (and so on what you pay): 3 boards x 100 = at most 300 rows. Default 100, maximum 1000.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Ashby Jobs Scraper with Salaries | `redomic/ashby-jobs-monitor` | community | ashby jobs |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/ashby-jobs-monitor" \
      -i '{"boards": ["ramp"], "mode": "jobs", "includeDescription": false, "maxItems": 100}' \
      --json \
      --user-agent apify-awesome-skills/apify-ashby-jobs-monitor \
      2>/dev/null

    apify actors info "redomic/ashby-jobs-monitor" --input --json \
      --user-agent apify-awesome-skills/apify-ashby-jobs-monitor 2>/dev/null

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-ashby-jobs-monitor 2>/dev/null
