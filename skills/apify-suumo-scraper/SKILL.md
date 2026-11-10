---
name: apify-suumo-scraper
description: "Scrape SUUMO Japan property listings from search URLs for rentals and sales. Returns flat rows with JPY prices, area, layout, station access, monitor changes, and run status. Uses the Apify Actor redomic/suumo-scraper. Use when the user asks to 'suumo scraper', 'suumo property scraper', 'suumo rental scraper', 'suumo 賃貸', or wants SUUMO Scraper - Japan Property Listings results as structured JSON or CSV."
metadata:
  category: data-extraction
  keywords: "suumo scraper, suumo property scraper, suumo rental scraper, suumo 賃貸"
author: Redomic
author_url: https://apify.com/redomic
---

# SUUMO Scraper - Japan Property Listings

Scrape SUUMO Japan property listings from search URLs for rentals and sales. Returns flat rows with JPY prices, area, layout, station access, monitor changes, and run status.

Disclosure: the routed Actor, `redomic/suumo-scraper`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get SUUMO Scraper - Japan Property Listings results for startUrls {'url': 'https://suumo.jp/ms/chuko/tokyo/sc_shinjuku/'}; mode search; maxItems 10"
- "Get SUUMO Scraper - Japan Property Listings results for startUrls {'url': 'https://suumo.jp/ms/chuko/tokyo/sc_minato/'}; mode search; maxItems 15"
- "Get SUUMO Scraper - Japan Property Listings results for startUrls {'url': 'https://suumo.jp/ms/chuko/tokyo/sc_shibuya/'}; mode search; maxItems 10"

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

- `startUrls` (array): SUUMO search or listing URLs to scrape (rental, sale, used condo, etc.).
- `mode` (string): search/detail scrapes current listings; monitor reports new, changed, and removed listings versus the previous run state.
- `maxItems` (integer): Upper limit on listing rows returned per run (excluding status/summary rows).
- `monitorStateKey` (string): Optional key suffix for monitor state in the named key-value store. Use different keys for different URL sets.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| SUUMO Scraper - Japan Property Listings | `redomic/suumo-scraper` | community | suumo scraper |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/suumo-scraper" \
      -i '{"startUrls": [{"url": "https://suumo.jp/jj/bukken/ichiran/JJ010FJ001/?ar=030&bs=011&ta=13&sc=13104&kb=1&kt=9999999&mb=0&mt=9999999&ekTjCd=&ekTjNm=&tj=0&cnb=0&cn=9999999"}], "mode": "search", "maxItems": 100, "monitorStateKey": "default"}' \
      --json \
      --user-agent apify-awesome-skills/apify-suumo-scraper \
      2>/dev/null

    apify actors info "redomic/suumo-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-suumo-scraper 2>/dev/null

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-suumo-scraper 2>/dev/null
