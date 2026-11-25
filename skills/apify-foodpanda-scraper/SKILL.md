---
name: apify-foodpanda-scraper
description: "Foodpanda vendor listings and dish-level menus with dated price history and new/changed/removed monitoring across SG, MY, PH, HK, TW, PK and BD. Uses the Apify Actor redomic/foodpanda-scraper. Use when the user asks to 'foodpanda scraper', 'foodpanda restaurant scraper', 'foodpanda menu scraper', or wants Foodpanda Scraper: Dated Menu Price Drops & Watchlist results as structured JSON or CSV."
metadata:
  category: data-extraction
  keywords: "foodpanda scraper, foodpanda restaurant scraper, foodpanda menu scraper"
author: Redomic
author_url: https://apify.com/redomic
---

# Foodpanda Scraper: Dated Menu Price Drops & Watchlist

Foodpanda vendor listings and dish-level menus with dated price history and new/changed/removed monitoring across SG, MY, PH, HK, TW, PK and BD.

Disclosure: the routed Actor, `redomic/foodpanda-scraper`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get Foodpanda Scraper: Dated Menu Price Drops & Watchlist results for mode search; latitude 1.3521; longitude 103.8198; country sg"
- "Get Foodpanda Scraper: Dated Menu Price Drops & Watchlist results for mode search; latitude 22.3193; longitude 114.1694; country hk"
- "Get Foodpanda Scraper: Dated Menu Price Drops & Watchlist results for mode search; latitude 3.139; longitude 101.6869; country my"

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

- `mode` (string): search: list vendors near a location. detail: fetch menus (dish rows) for vendor codes. monitor: only new/changed/removed vendors since the last run.
- `latitude` (number): Centre of the area to list vendors for.
- `longitude` (number): Centre of the area to list vendors for.
- `country` (string): Foodpanda market.
- `maxItems` (integer): Upper limit on rows returned.
- `vendors` (array): Vendor codes (or full restaurant URLs) for detail mode, e.g. rso3.
- `language` (string): auto, en, local, or both (paired bilingual fields).

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Foodpanda Scraper: Dated Menu Price Drops & Watchlist | `redomic/foodpanda-scraper` | community | foodpanda scraper |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/foodpanda-scraper" \
      -i '{"mode": "search", "latitude": 1.3521, "longitude": 103.8198, "country": "sg", "maxItems": 20, "language": "auto"}' \
      --json \
      --user-agent apify-awesome-skills/apify-foodpanda-scraper \
      2>/dev/null

    apify actors info "redomic/foodpanda-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-foodpanda-scraper 2>/dev/null

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-foodpanda-scraper 2>/dev/null
