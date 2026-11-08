---
name: apify-otodom-scraper
description: "Scrape Otodom.pl property listings in Poland. Returns price, area, rooms, location, advertiser and URLs from any search. Monitor mode tracks new and price-changed listings. Uses the Apify Actor redomic/otodom-scraper. Use when the user asks to 'otodom scraper', 'otodom', 'otodom api', or wants Otodom Scraper: Poland Property Listings & Price Monitor results as structured JSON or CSV."
metadata:
  category: data-extraction
  keywords: "otodom scraper, otodom, otodom api"
author: Redomic
author_url: https://apify.com/redomic
---

# Otodom Scraper: Poland Property Listings & Price Monitor

Scrape Otodom.pl property listings in Poland. Returns price, area, rooms, location, advertiser and URLs from any search. Monitor mode tracks new and price-changed listings.

Disclosure: the routed Actor, `redomic/otodom-scraper`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get Otodom Scraper: Poland Property Listings & Price Monitor results for location mazowieckie/warszawa/warszawa; dealType sale; propertyType flat; priceMax 900000"
- "Get Otodom Scraper: Poland Property Listings & Price Monitor results for location malopolskie/krakow/krakow; dealType rent; propertyType flat; maxItems 15"
- "Get Otodom Scraper: Poland Property Listings & Price Monitor results for location cala-polska; dealType sale; propertyType house; priceMax 1500000"

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

- `startUrls` (array): Otodom.pl search result URLs to scrape (e.g. https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/warszawa/warszawa/warszawa). If provided, structured filters below are ignored for URL building.
- `location` (string): Location path segment for Otodom search when not using startUrls (e.g. 'cala-polska', 'mazowieckie/warszawa/warszawa', 'malopolskie/krakow/krakow').
- `dealType` (string): Sale or rent.
- `propertyType` (string): Type of property to search.
- `priceMin` (integer): Minimum total price in PLN.
- `priceMax` (integer): Maximum total price in PLN.
- `areaMin` (integer): Minimum area in square meters.
- `areaMax` (integer): Maximum area in square meters.
- `roomsMin` (integer): Minimum number of rooms.
- `roomsMax` (integer): Maximum number of rooms.
- `market` (string): Primary (new) or secondary (resale) market. Leave empty for all.
- `mode` (string): search returns matching listings; monitor reports only new, changed and removed listings since the last run (state kept per source URL).
- `maxItems` (integer): Maximum listing rows to return across all sources.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Otodom Scraper: Poland Property Listings & Price Monitor | `redomic/otodom-scraper` | community | otodom scraper |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/otodom-scraper" \
      -i '{"location": "cala-polska", "dealType": "sale", "propertyType": "flat", "mode": "search", "maxItems": 100}' \
      --json \
      --user-agent apify-awesome-skills/apify-otodom-scraper \
      2>/dev/null

    apify actors info "redomic/otodom-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-otodom-scraper 2>/dev/null

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-otodom-scraper 2>/dev/null
