---
name: apify-myntra-scraper
description: "Myntra scraper for product prices, MRP, discounts, ratings and stock. One run returns flat rows from a search term, category or style ID with brand, images and INR prices. Detail mode adds manufacturer, description and review counts. Monitor mode returns only new, changed and removed products. Uses the Apify Actor redomic/myntra-scraper. Use when the user asks to 'myntra scraper', 'myntra product scraper', or wants Myntra Product Scraper results as structured JSON or CSV."
metadata:
  category: data-extraction
  keywords: "myntra scraper, myntra product scraper"
author: Redomic
author_url: https://apify.com/redomic
---

# Myntra Product Scraper

Myntra scraper for product prices, MRP, discounts, ratings and stock. One run returns flat rows from a search term, category or style ID with brand, images and INR prices. Detail mode adds manufacturer, description and review counts. Monitor mode returns only new, changed and removed products.

Disclosure: the routed Actor, `redomic/myntra-scraper`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get Myntra Product Scraper results for mode search; query kurti; maxItems 10"
- "Get Myntra Product Scraper results for mode search; query men-casual-shoes; sort price_asc; maxItems 5"
- "Get Myntra Product Scraper results for mode search; query women-kurtis; sort Customer Rating; maxItems 8"

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

- `mode` (string): search: products for a term or category; detail: full product pages by ID or URL; monitor: only new, changed and removed products since the last run.
- `query` (string): A search term such as kurti, a category slug such as men-casual-shoes, or a full Myntra listing URL.
- `styleIds` (array): Myntra style IDs for detail mode. A reviews URL or a product URL also works here; the ID is resolved from it.
- `productUrls` (array): Full Myntra product or reviews URLs for detail mode. Both /<slug>/<id>/buy and /reviews/<id> are accepted.
- `sort` (string): Sort order Myntra applies to the search. Leave empty for the site default.
- `minPrice` (number): Keep only products priced at or above this amount. Leave empty for no lower bound.
- `maxPrice` (number): Keep only products priced at or below this amount. Leave empty for no upper bound.
- `pincode` (string): Six-digit Indian pincode sent with the page request so delivery information matches the area.
- `maxItems` (integer): Upper limit on result rows for one run.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Myntra Product Scraper | `redomic/myntra-scraper` | community | myntra scraper |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/myntra-scraper" \
      -i '{"mode": "search", "query": "kurti", "styleIds": ["47331372"], "productUrls": ["https://www.myntra.com/kurtis/sangria/sangria-shirt-collar-kurti/47331372/buy"], "maxItems": 100}' \
      --json \
      --user-agent apify-awesome-skills/apify-myntra-scraper \
      2>/dev/null

    apify actors info "redomic/myntra-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-myntra-scraper 2>/dev/null

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-myntra-scraper 2>/dev/null
