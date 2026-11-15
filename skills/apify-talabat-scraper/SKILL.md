---
name: apify-talabat-scraper
description: "Talabat menus, prices and delivery fees as flat rows in 8 MENA markets. Area mode lists every branch delivering to an area with fee, ETA, minimum order and menu URL; menu mode returns each dish with section, price and currency. Search, detail and monitor modes too. Uses the Apify Actor redomic/talabat-scraper. Use when the user asks to 'talabat scraper', 'talabat restaurant scraper', 'talabat menu scraper', or wants Talabat Scraper — Menus, Prices & Delivery Fees results as structured JSON or CSV."
metadata:
  category: data-extraction
  keywords: "talabat scraper, talabat restaurant scraper, talabat menu scraper"
author: Redomic
author_url: https://apify.com/redomic
---

# Talabat Scraper — Menus, Prices & Delivery Fees

Talabat menus, prices and delivery fees as flat rows in 8 MENA markets. Area mode lists every branch delivering to an area with fee, ETA, minimum order and menu URL; menu mode returns each dish with section, price and currency. Search, detail and monitor modes too.

Disclosure: the routed Actor, `redomic/talabat-scraper`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get Talabat Scraper — Menus, Prices & Delivery Fees results for mode search; query pizza; country uae; maxItems 5"
- "Get Talabat Scraper — Menus, Prices & Delivery Fees results for mode search; query burger; country uae; maxItems 10"
- "Get Talabat Scraper — Menus, Prices & Delivery Fees results for mode search; query sushi; country uae; maxItems 8"

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

- `mode` (string): search lists the restaurants of a market (optionally filtered by a search term); detail fetches the full restaurant page for each entry in restaurants; monitor reports only restaurants that are new, c
- `query` (string): Talabat's own restaurant search for this market: a restaurant name, a dish or a cuisine (for example pizza, burger, sushi). Leave empty to browse every restaurant of the country. Used in search and mo
- `country` (string): The talabat.com market to read: uae, ksa, kuwait, qatar, bahrain, oman, egypt or jordan. Also the default country for bare slugs in detail mode.
- `restaurants` (array): For mode 'detail': restaurant pages (https://www.talabat.com/uae/johnny-rockets, /uae/johnny-rockets or johnny-rockets). For mode 'menu': branch menu URLs with their delivery area, like https://www.ta
- `areas` (array): For mode 'area': Talabat area pages, like https://www.talabat.com/uae/restaurants/1169/abu-hail (open talabat.com, pick a delivery area, copy the URL). Every branch delivering there is returned, paged
- `includeMenus` (boolean): For mode 'area': also read the full menu of every branch returned and add one row per menu item (same rows as menu mode). Max items still caps the branches; each branch menu is one 'menu' charge, howe
- `includeChoices` (boolean): For menu rows (menu mode, or area mode with menus): open the choices of every item that has them (size, combo, extras) and add fromPrice (item price plus the cheapest required choices; Talabat shows 0
- `maxItems` (integer): Upper limit on restaurant rows returned (and so on what you pay). Search pages 30 restaurants per request and stops at this cap; detail stops after this many restaurants.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Talabat Scraper — Menus, Prices & Delivery Fees | `redomic/talabat-scraper` | community | talabat scraper |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/talabat-scraper" \
      -i '{"mode": "search", "query": "pizza", "country": "uae", "restaurants": ["https://www.talabat.com/uae/restaurant/609078/papa-johns?aid=9553"], "areas": ["https://www.talabat.com/uae/restaurants/1169/abu-hail"], "includeMenus": true, "includeChoices": false, "maxItems": 100}' \
      --json \
      --user-agent apify-awesome-skills/apify-talabat-scraper \
      2>/dev/null

    apify actors info "redomic/talabat-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-talabat-scraper 2>/dev/null

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-talabat-scraper 2>/dev/null
