---
name: apify-mercari-sold-comps
description: "Search Mercari Japan for live listings and sold prices. Each row carries the JPY price, item status, condition, timestamps, seller id and auction fields. Detail mode adds the description, category path and public seller rating; monitor mode reports new, changed and removed listings. Uses the Apify Actor redomic/mercari-sold-comps. Use when the user asks to 'mercari scraper', 'mercari japan scraper', 'mercari sold prices', or wants Mercari Scraper results as structured JSON or CSV."
metadata:
  category: data-extraction
  keywords: "mercari scraper, mercari japan scraper, mercari sold prices, mercari sold comps"
author: Redomic
author_url: https://apify.com/redomic
---

# Mercari Scraper

Search Mercari Japan for live listings and sold prices. Each row carries the JPY price, item status, condition, timestamps, seller id and auction fields. Detail mode adds the description, category path and public seller rating; monitor mode reports new, changed and removed listings.

Disclosure: the routed Actor, `redomic/mercari-sold-comps`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get Mercari Scraper results for mode search; query nike air max; maxItems 10"
- "Get Mercari Scraper results for mode search; query ルイヴィトン 財布; maxItems 10"
- "Get Mercari Scraper results for mode search; query sony wh-1000xm5; priceMin 15000; priceMax 40000"

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

- `mode` (string): search: listings for a keyword. detail: full item pages. monitor: only new, changed and removed listings since the last run.
- `query` (string): Japanese or English keyword to search on Mercari Japan. Used when queries is empty.
- `queries` (array): Several keywords, searched one after another. Items found twice are returned once and charged once.
- `keyword` (string): Alias for query, accepted from other scrapers' inputs.
- `itemUrls` (array): Mercari item pages or bare ids such as m95735345163. Used in detail mode.
- `startUrls` (array): Mercari item or search URLs pasted from another Actor. The keyword and the filters are read from them.
- `maxItems` (integer): Hard upper limit on result rows for the whole run. Never raised above 1000.
- `statusFilter` (string): Keep only items in this state. Public search lists items on sale; detail mode also returns sold and trading items.
- `priceMin` (integer): Drop rows priced below this value.
- `priceMax` (integer): Drop rows priced above this value. Zero means no upper limit.
- `fetchDetails` (boolean): Open each search result as well, adding description, category path, seller rating and shipping.
- `includeComments` (boolean): Reserved for future use. Comment count is always returned; comment text never is.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Mercari Scraper | `redomic/mercari-sold-comps` | community | mercari scraper |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/mercari-sold-comps" \
      -i '{"mode": "search", "query": "camera", "maxItems": 100, "statusFilter": "all", "priceMin": 0, "priceMax": 0, "fetchDetails": false, "includeComments": false}' \
      --json \
      --user-agent apify-awesome-skills/apify-mercari-sold-comps \
      2>/dev/null

    apify actors info "redomic/mercari-sold-comps" --input --json \
      --user-agent apify-awesome-skills/apify-mercari-sold-comps 2>/dev/null

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-mercari-sold-comps 2>/dev/null
