---
name: apify-hotel-price-research
description: Research hotel prices with live Google Hotels data. Compare hotels in a city by all-in nightly price (taxes and fees included), rating and star class; find the cheapest dates or weekend over the coming weeks; compare several cities for the same dates; or track the price of one stay over time and flag drops. Use when the user asks "how much are hotels in X", "cheapest weekend to visit Y", "compare hotel prices in A and B", "track the price of my hotel stay", "hotel prices for an event weekend", "rate shopping against competing hotels", or wants hotel prices as CSV or JSON. Prices only; it never books.
author: Ralf IJsbrandij — routes to an Actor built by the author; no affiliate or referral parameters
author_url: https://github.com/RalfIJ
metadata:
  category: data-extraction
  keywords: "hotels, hotel-prices, google-hotels, travel, rate-shopping, price-tracking, cheapest-dates, city-comparison, hotel-rates, revenue-management, apify"
---

# Hotel Price Research

Turn "what do hotels cost there, and when is it cheapest?" into a sourced answer from live Google Hotels prices. Google Hotels compares booking sites and the hotels' own websites, so one search shows the going rate for a city, dates and number of guests.

**Disclosure:** `ralfij/google-hotels-scraper` is built and published by the author of this skill. No affiliate or referral parameters are used on any link.

**Never invent a price, a rating or a hotel.** Every number comes from the Actor's dataset for the dates and guests the user asked for. Missing values stay blank.

## Example prompts

Prompts this skill handles:

- "What does a 4-star hotel in Lisbon cost for 2 adults on the weekend of 13 to 15 November?"
- "Which of the next 8 weekends is cheapest for a hotel in Amsterdam?"
- "Compare median hotel prices in Paris, Rome, Barcelona and Prague for the same dates, taxes included."

Out of scope (the boundary):

- "Find me flights and a hotel for a trip to Tokyo." Flights and whole-trip planning belong to the `apify-plan-travel` skill. This skill covers hotel prices only, and it never books anything.

## Prerequisites

- An Apify account ([sign up](https://apify.com)).
- **MCP path:** with the Apify MCP server connected, use the `call-actor` and `get-dataset-items` tools. No extra setup.
- **CLI path:** the [Apify CLI](https://docs.apify.com/cli), authenticated with `apify login` or an `APIFY_TOKEN` environment variable ([get a token](https://console.apify.com/settings/integrations)). Every call below carries `--json`, `--user-agent apify-awesome-skills/apify-hotel-price-research` and `2>/dev/null`.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Hotel prices for any city, dates and guests | `ralfij/google-hotels-scraper` | community | About 20 hotels per search with nightly price, total with taxes, rating, stars, amenities and coordinates |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Workflow

```
Task Progress:
- [ ] Step 1: Collect the anchors (one block)
- [ ] Step 2: Pick the mode
- [ ] Step 3: Fetch the input schema, build the input, estimate the cost
- [ ] Step 4: Run and pull the dataset
- [ ] Step 5: Compute all-in prices and answer
```

### Step 1: Collect the anchors

Ask these as one block before any Actor call, with the defaults shown:

1. **Destination**, as a Google Hotels search: `hotels in Lisbon`, `hotels near Times Square`, `Paris`. Required. One search per city or area.
2. **Dates**: check-in and check-out as `YYYY-MM-DD`, or relative (`30 days`, `32 days`). The default is 14 days from today, for 1 night. Stays can be up to 30 nights.
3. **Guests**: adults (default 2, 1 to 10) and children's ages (`["8", "11"]`).
4. **Currency** (default `USD`) and **market** (`country`, Google's `gl`, default `us`).
5. **Filters** to apply after the run: minimum rating, star class, maximum price.

If the destination or dates are missing, ask one clarifying question. Don't run on a guess.

### Step 2: Pick the mode

| Mode | Runs | How |
|---|---|---|
| One search | 1 | One query, one date range |
| Compare cities | 1 | Several `queries` in one run, same dates |
| Cheapest dates or weekend | 1 per date range | One run per check-in date, run one after the other; compare medians |
| Track one stay | 1 per day | Fixed dates, scheduled daily; match rows across runs by `hotelId` |

### Step 3: Fetch the schema, build the input, estimate the cost

```bash
apify actors info "ralfij/google-hotels-scraper" --input \
  --user-agent apify-awesome-skills/apify-hotel-price-research 2>/dev/null
```

Example input for comparing cities:

```json
{
  "queries": ["hotels in Lisbon", "hotels in Porto"],
  "checkInDate": "2026-11-13",
  "checkOutDate": "2026-11-15",
  "adults": 2,
  "currency": "EUR",
  "maxHotelsPerSearch": 20
}
```

**Cost:** about 20 hotels per search, times searches, times date ranges. The price is per hotel result (about $0.0035 on Apify's free plan, less on paid plans; check the Actor's Pricing tab before quoting it). A search that returns nothing costs only the tiny start fee. Confirm with the user before runs above about 500 hotels. `maxHotelsPerSearch` lowers the cost.

### Step 4: Run and pull the dataset

```bash
apify actors call "ralfij/google-hotels-scraper" \
  -i '{"queries": ["hotels in Lisbon"], "checkInDate": "30 days", "checkOutDate": "32 days", "currency": "EUR"}' \
  --json --user-agent apify-awesome-skills/apify-hotel-price-research 2>/dev/null

apify datasets get-items DATASET_ID --format json \
  --user-agent apify-awesome-skills/apify-hotel-price-research 2>/dev/null
```

Take `DATASET_ID` from `storage.defaultDatasetId` in the JSON the call prints.

### Step 5: Compute all-in prices and answer

Fields per hotel: `name`, `hotelId`, `pricePerNight`, `pricePerNightText`, `totalPrice`, `totalPriceBeforeTaxes`, `taxesAndFees`, `currency`, `dealText`, `rating`, `reviewCount`, `hotelClass`, `propertyType`, `amenities`, `latitude`, `longitude`, `checkInDate`, `checkOutDate`, `nights`, `googleHotelsUrl`, `googleMapsUrl`, `query`, `searchLocation`.

- **Compare on `totalPrice / nights`.** `pricePerNight` is exactly what Google shows: before taxes for the US market, but with taxes in most other markets. `totalPrice` always includes taxes and fees.
- Use medians per city or date range; single cheap listings (hostel beds, apartments) skew averages.
- Report the deal note (`dealText`, such as "23% less than usual") when it is there.
- Deliver a short table (hotel, stars, rating, all-in price per night, link) and state the dates, guests, currency and market the prices are for.

## Gotchas and failure modes

- **About 20 hotels per search.** That is Google's first page, not the whole city. For more coverage, add area searches (`hotels in Lisbon Alfama`, `hotels near Lisbon Oriente`).
- **A search came back empty.** Read the `RUN_SUMMARY` record in the run's key-value store: each search has a status (`ok`, `no-results`, `skipped`, `failed`, `not-run`) and a note. Retry with different wording or dates. A hotel's name on its own opens that hotel's page and is `skipped`.
- **Prices differ from the user's browser.** Google adapts prices to the market, currency and logged-in deals. Match `country` and `currency` to compare.
- **Scheduled runs:** relative dates (`30 days` to `32 days`) keep a schedule pointing at the future. For tracking one stay, keep the dates fixed.
- **Events move prices a lot.** A weekend that is twice the price of the others usually has a festival, fair or match; say so instead of averaging it away.
- **Data scope:** business data only. Guest reviews and reviewer names are not collected.
