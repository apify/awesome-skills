---
name: apify-govdeals-scraper
description: "Search and monitor GovDeals government surplus auctions. Get flat rows with lot ID, title, seller, location, current bid, end time, category, and direct asset URLs. Monitor runs report new, changed, and removed lots. Uses the Apify Actor redomic/govdeals-scraper. Use when the user asks to 'govdeals scraper', 'govdeals auction scraper', 'government surplus auction scraper', or wants GovDeals Scraper results as structured JSON or CSV."
metadata:
  category: data-extraction
  keywords: "govdeals scraper, govdeals auction scraper, government surplus auction scraper"
author: Redomic
author_url: https://apify.com/redomic
---

# GovDeals Scraper

Search and monitor GovDeals government surplus auctions. Get flat rows with lot ID, title, seller, location, current bid, end time, category, and direct asset URLs. Monitor runs report new, changed, and removed lots.

Disclosure: the routed Actor, `redomic/govdeals-scraper`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get GovDeals Scraper results for query truck; mode search; maxItems 10"
- "Get GovDeals Scraper results for query generator; mode search; maxItems 5"
- "Get GovDeals Scraper results for query excavator; mode search; maxItems 15"

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

- `query` (string): Keyword to search on GovDeals (for example truck, generator, excavator). Used in search and monitor modes.
- `mode` (string): search lists matching lots; monitor reports only new, changed and removed lots since the last run for the same query/filters.
- `maxItems` (integer): Upper limit on lot rows returned per run (and on what you pay). Default 50, maximum 500.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| GovDeals Scraper | `redomic/govdeals-scraper` | community | govdeals scraper |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/govdeals-scraper" \
      -i '{"query": "truck", "mode": "search", "maxItems": 50}' \
      --json \
      --user-agent apify-awesome-skills/apify-govdeals-scraper \
      2>/dev/null

    apify actors info "redomic/govdeals-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-govdeals-scraper 2>/dev/null

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-govdeals-scraper 2>/dev/null
