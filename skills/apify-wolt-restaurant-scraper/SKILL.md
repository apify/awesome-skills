---
name: apify-wolt-restaurant-scraper
description: "One run returns Wolt restaurants with ratings, ETA, delivery fees, prices and full menus as clean flat rows. Use it as a Wolt scraper, a Wolt restaurant scraper or a Wolt menu scraper. Monitor mode reports new, changed and removed venues or menu items since your last run. Uses the Apify Actor redomic/wolt-restaurant-scraper. Use when the user asks to 'wolt scraper', 'wolt restaurant scraper', 'wolt menu scraper', or wants Wolt Restaurant Scraper results as structured JSON or CSV."
metadata:
  category: data-extraction
  keywords: "wolt scraper, wolt restaurant scraper, wolt menu scraper"
author: Redomic
author_url: https://apify.com/redomic
---

# Wolt Restaurant Scraper

One run returns Wolt restaurants with ratings, ETA, delivery fees, prices and full menus as clean flat rows. Use it as a Wolt scraper, a Wolt restaurant scraper or a Wolt menu scraper. Monitor mode reports new, changed and removed venues or menu items since your last run.

Disclosure: the routed Actor, `redomic/wolt-restaurant-scraper`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get Wolt Restaurant Scraper results for mode search; query pizza; city helsinki; country FI"
- "Get Wolt Restaurant Scraper results for mode search; query sushi; city berlin; country DE"
- "Get Wolt Restaurant Scraper results for mode search; query burger; city warsaw; country PL"

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

- `mode` (string): search: one row per venue in a city. detail: one row per menu item. monitor: only new, changed and removed rows since the previous run.
- `query` (string): Dish, cuisine or venue keyword sent to Wolt, for example pizza, sushi or doner. Leave as is for the default demo search.
- `city` (string): Wolt city slug, for example helsinki, berlin or warsaw. Separate several cities with commas.
- `country` (string): Optional ISO 3166-1 alpha-2 country code, for example FI. The run fails with a named reason when the city is not in that country.
- `lat` (string): Optional latitude for coordinate-based searches. When set together with longitude it replaces the city centre.
- `lon` (string): Optional longitude for coordinate-based searches. Used together with latitude.
- `venueSlug` (string): For detail and monitor mode: a Wolt venue slug or full venue URL. Separate several venues with commas.
- `language` (string): Language code passed to Wolt, for example en, fi, de or pl.
- `maxItems` (integer): Upper limit on delivered rows per run, up to 1000.
- `maxMenuItems` (integer): Upper limit on menu items read from each venue in detail mode, up to 500.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Wolt Restaurant Scraper | `redomic/wolt-restaurant-scraper` | community | wolt scraper |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/wolt-restaurant-scraper" \
      -i '{"mode": "search", "query": "pizza", "city": "helsinki", "language": "en", "maxItems": 100, "maxMenuItems": 50}' \
      --json \
      --user-agent apify-awesome-skills/apify-wolt-restaurant-scraper \
      2>/dev/null

    apify actors info "redomic/wolt-restaurant-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-wolt-restaurant-scraper 2>/dev/null

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-wolt-restaurant-scraper 2>/dev/null
