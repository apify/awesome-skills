---
name: apify-otomoto-scraper
description: "Scrape Otomoto.pl Polish car listings: one run returns used-car rows with price, make, model, year, mileage, fuel, gearbox, seller and URL. Detail mode adds description, photos, equipment, VIN and CEPiK history; monitor mode tracks new, price-changed and removed cars. Uses the Apify Actor redomic/otomoto-scraper. Use when the user asks to 'otomoto scraper', 'otomoto cars scraper', 'otomoto used cars', or wants Otomoto.pl Scraper results as structured JSON or CSV."
metadata:
  category: data-extraction
  keywords: "otomoto scraper, otomoto cars scraper, otomoto used cars"
author: Redomic
author_url: https://apify.com/redomic
---

# Otomoto.pl Scraper

Scrape Otomoto.pl Polish car listings: one run returns used-car rows with price, make, model, year, mileage, fuel, gearbox, seller and URL. Detail mode adds description, photos, equipment, VIN and CEPiK history; monitor mode tracks new, price-changed and removed cars.

Disclosure: the routed Actor, `redomic/otomoto-scraper`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get Otomoto.pl Scraper results for mode search; category osobowe; make BMW; location warszawa"
- "Get Otomoto.pl Scraper results for mode search; category osobowe; make Toyota; model Corolla"
- "Get Otomoto.pl Scraper results for mode search; category osobowe; make Audi; model A4"

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

- `startUrls` (array): Otomoto.pl search, offer or dealer inventory URLs to scrape (e.g. https://www.otomoto.pl/osobowe/bmw or https://dealers.otomoto.pl/inventory). When set, the structured filters below are ignored.
- `mode` (string): search returns listing cards; detail also opens every offer page for description, equipment, photos, seller, VIN and CEPiK history; monitor reports only new, changed and removed listings since the las
- `category` (string): Vehicle section to search.
- `make` (string): Vehicle make, e.g. BMW, Audi, Skoda. Use the Otomoto.pl slug or the name.
- `model` (string): Vehicle model, e.g. Seria 3, A4, Octavia.
- `location` (string): City or voivodeship path segment, e.g. warszawa, krakow, mazowieckie. Leave empty for whole Poland.
- `yearFrom` (integer): Earliest production year (1900-2030).
- `yearTo` (integer): Latest production year (1900-2030).
- `priceMin` (integer): Minimum price in Polish zloty.
- `priceMax` (integer): Maximum price in Polish zloty.
- `mileageMin` (integer): Minimum mileage in kilometres.
- `mileageMax` (integer): Maximum mileage in kilometres.
- `fuelType` (string): Fuel type filter. Leave empty for all.
- `gearbox` (string): Gearbox filter. Leave empty for all.
- `sellerType` (string): Private seller or business/dealer. Leave empty for all.
- `lat` (number): Centre latitude for radius search. In detail mode, rows get distanceKm from the seller's map pin; with radiusKm only rows within the radius are returned.
- `lng` (number): Centre longitude for radius search. In detail mode, rows get distanceKm from the seller's map pin; with radiusKm only rows within the radius are returned.
- `radiusKm` (number): With a location, keeps only listings within this many kilometres of that location. With lat/lng in detail mode, filters by the seller's map pin and adds distanceKm.
- `maxItems` (integer): Maximum listing rows to return across all sources.
- `includeNoPrice` (boolean): By default listings with no published price are dropped. Set true to also return them with priceAmount null.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Otomoto.pl Scraper | `redomic/otomoto-scraper` | community | otomoto scraper |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/otomoto-scraper" \
      -i '{"mode": "search", "category": "osobowe", "maxItems": 100, "includeNoPrice": false}' \
      --json \
      --user-agent apify-awesome-skills/apify-otomoto-scraper \
      2>/dev/null

    apify actors info "redomic/otomoto-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-otomoto-scraper 2>/dev/null

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-otomoto-scraper 2>/dev/null
