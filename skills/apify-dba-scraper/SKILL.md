---
name: apify-dba-scraper
description: "A dba scraper for Danish classifieds: one run returns DBA.dk listings with title, price in DKK, condition, category, image and seller. Detail mode adds location, attributes and contact fields. Monitor mode reports new, changed and removed ads. Uses the Apify Actor redomic/dba-scraper. Use when the user asks to 'dba scraper', 'dba dk scraper', or wants DBA.dk Scraper results as structured JSON or CSV."
metadata:
  category: data-extraction
  keywords: "dba scraper, dba dk scraper"
author: Redomic
author_url: https://apify.com/redomic
---

# DBA.dk Scraper

A dba scraper for Danish classifieds: one run returns DBA.dk listings with title, price in DKK, condition, category, image and seller. Detail mode adds location, attributes and contact fields. Monitor mode reports new, changed and removed ads.

Disclosure: the routed Actor, `redomic/dba-scraper`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get DBA.dk Scraper results for mode search; query cykel; maxItems 10"
- "Get DBA.dk Scraper results for mode search; query iphone; maxItems 10"
- "Get DBA.dk Scraper results for mode search; query ps5; maxItems 8"

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

- `mode` (string): search = listings, detail = single listings, monitor = new/changed/removed since last run.
- `query` (string): Keyword to search on DBA.dk (used when queries is empty).
- `queries` (array): Multiple keywords to search. Each becomes its own input with a status row.
- `startUrls` (array): DBA.dk search page URLs to scrape.
- `listingUrls` (array): Specific DBA.dk listing URLs to fetch in detail.
- `listingIds` (array): DBA.dk listing IDs (the number in a listing URL).
- `priceMin` (number): Keep listings priced at or above this value.
- `priceMax` (number): Keep listings priced at or below this value.
- `condition` (string): Filter by condition text contained in the listing (e.g. Ny, Brugt).
- `maxItems` (integer): Upper limit on rows returned.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| DBA.dk Scraper | `redomic/dba-scraper` | community | dba scraper |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/dba-scraper" \
      -i '{"mode": "search", "query": "cykel", "maxItems": 100}' \
      --json \
      --user-agent apify-awesome-skills/apify-dba-scraper \
      2>/dev/null

    apify actors info "redomic/dba-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-dba-scraper 2>/dev/null

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-dba-scraper 2>/dev/null
