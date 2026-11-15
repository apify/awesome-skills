---
name: apify-ulta-scraper
description: "Scrape Ulta Beauty products by search or category with prices, ratings, reviews, and availability. Monitor price and stock changes over time. $1.40 per 1,000 products. Uses the Apify Actor redomic/ulta-scraper. Use when the user asks to 'ulta scraper', 'ulta beauty scraper', or wants Ulta Scraper results as structured JSON or CSV."
metadata:
  category: data-extraction
  keywords: "ulta scraper, ulta beauty scraper"
author: Redomic
author_url: https://apify.com/redomic
---

# Ulta Scraper

Scrape Ulta Beauty products by search or category with prices, ratings, reviews, and availability. Monitor price and stock changes over time. $1.40 per 1,000 products.

Disclosure: the routed Actor, `redomic/ulta-scraper`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get Ulta Scraper results for query https://www.ulta.com/shop/makeup/face/foundation; mode discovery; maxItems 20"
- "Get Ulta Scraper results for query /shop/makeup/eyes/mascara; mode discovery; maxItems 15"
- "Get Ulta Scraper results for query /shop/makeup/lips/lipstick; mode discovery; maxItems 10"

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

- `query` (string): A product type or brand (e.g. "mascara", "dry shampoo"), which opens the matching Ulta category or brand page; or a category path (e.g. "/shop/makeup/face/foundation"), a brand page (e.g. "/brand/tart
- `mode` (string): discovery: list products from a search or category. detail: fetch full details for product URLs/IDs. monitor: report only new, changed, and removed products since the previous run for the same input.
- `maxItems` (integer): Maximum number of products to return.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Ulta Scraper | `redomic/ulta-scraper` | community | ulta scraper |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/ulta-scraper" \
      -i '{"query": "mascara", "mode": "discovery", "maxItems": 50}' \
      --json \
      --user-agent apify-awesome-skills/apify-ulta-scraper \
      2>/dev/null

    apify actors info "redomic/ulta-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-ulta-scraper 2>/dev/null

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-ulta-scraper 2>/dev/null
