---
name: apify-allabolag-company-scraper
description: "Scrape allabolag.se for Swedish company financials, industry, status and board role titles by search, org number or URL. Monitor mode reports new and changed companies. $3/1k rows. Uses the Apify Actor redomic/allabolag-company-scraper. Use when the user asks to 'allabolag scraper', 'allabolag', 'swedish company data', or wants Allabolag Scraper - Swedish Company Data results as structured JSON or CSV."
metadata:
  category: data-extraction
  keywords: "allabolag scraper, allabolag, swedish company data, allabolag company scraper"
author: Redomic
author_url: https://apify.com/redomic
---

# Allabolag Scraper - Swedish Company Data

Scrape allabolag.se for Swedish company financials, industry, status and board role titles by search, org number or URL. Monitor mode reports new and changed companies. $3/1k rows.

Disclosure: the routed Actor, `redomic/allabolag-company-scraper`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get Allabolag Scraper - Swedish Company Data results for query volvo; mode search; maxItems 10"
- "Get Allabolag Scraper - Swedish Company Data results for query ericsson; mode search; maxItems 10"
- "Get Allabolag Scraper - Swedish Company Data results for query spotify; mode search; maxItems 10"

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

- `query` (string): Company name or keyword to search (uses /what/<query>). You can also pass an organisation number or allabolag.se URL here.
- `queries` (array): Multiple search keywords, organisation numbers or allabolag URLs to process.
- `orgNumbers` (array): Swedish organisation numbers (10 digits, with or without dash) to fetch directly.
- `startUrls` (array): Direct allabolag.se company URLs.
- `mode` (string): search = find companies by query; detail = fetch by org number/URL; monitor = report new/changed/removed companies since last run (uses a named key-value store).
- `maxItems` (integer): Maximum company rows to return.
- `county` (string): Optional: keep only companies whose county contains this text (best-effort).
- `municipality` (string): Optional: keep only companies whose municipality contains this text (best-effort).

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Allabolag Scraper - Swedish Company Data | `redomic/allabolag-company-scraper` | community | allabolag scraper |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/allabolag-company-scraper" \
      -i '{"query": "volvo", "mode": "search", "maxItems": 50}' \
      --json \
      --user-agent apify-awesome-skills/apify-allabolag-company-scraper \
      2>/dev/null

    apify actors info "redomic/allabolag-company-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-allabolag-company-scraper 2>/dev/null

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-allabolag-company-scraper 2>/dev/null
