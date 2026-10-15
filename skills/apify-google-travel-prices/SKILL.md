---
name: apify-google-travel-prices
description: Pull live hotel and vacation rental prices from Google Travel - OTA rates per night, per-room offers, daily price calendars, and Vrbo/Airbnb/Booking.com strike-through deals. Use when the user says things like "scrape Google Hotels prices", "find hotel rates in Paris", "compare OTA prices for a hotel", "track daily hotel prices", "monthly hotel price calendar", "Vrbo prices by date", or "vacation rental price history". Three Actors cover the Google Travel surface: Hotels (one row per hotel with current nightly rates + per-room offers from 50+ OTAs), Price Calendar (full daily/monthly matrix for one hotel), and Vacation Rentals (Airbnb/Vrbo/Booking.com rentals indexed by Google). Reaches tens of thousands of properties worldwide.
author: Huynh Tan An
author_url: https://github.com/huynhtanan
metadata:
  category: data-extraction
  keywords: "google-hotels, hotel-prices, hotel-rates, ota-prices, booking.com, expedia, agoda, vrbo, airbnb, vacation-rentals, price-calendar, price-tracking, rate-parity, travel, hospitality, hotel-api"
---

# Google Travel prices (hotels + rentals + price calendar)

Three Apify Actors that split the Google Travel surface so an agent can answer three different pricing questions without over-paying:

| User question | Actor | Rough shape of output |
|--------------|-------|-----------------------|
| "What's the price of hotels in Paris Oct 20-23?" | `zet46/google-hotels-scraper` | one row per hotel: nightly rate, per-room offers from Booking.com / Expedia / Agoda / Hotels.com (up to 20+ OTAs), amenities, star rating, class, review count |
| "How does one hotel's price change day-by-day across the next 60 days?" | `zet46/google-hotels-price-calendar` | one row per date: nightly price (nullable when sold out), currency, link back to Google |
| "What vacation rentals (Vrbo/Airbnb) are available in Lake Tahoe Dec 1-7?" | `zet46/google-vacation-rentals-scraper` | one row per rental: provider (Vrbo/Airbnb/Booking.com), nightly rate, total, beds/baths, rating |

Author discloses: the three routed Actors above are built by the author (zet46 on Apify Store). No affiliate parameters are used in this skill's links.

## Example prompts

Prompts this skill handles:

- "Scrape Google Hotels prices in Rome for Oct 20-23, two adults, show the top 50 with Booking.com and Expedia rates per room."
- "Build me a 60-day daily price calendar for this hotel URL `https://www.google.com/travel/hotels/entity/...`, EUR."
- "List Vrbo and Airbnb rentals in Lake Tahoe for a week in December, 4 guests, with nightly price."

Out of scope (the boundary):

- "Book this hotel for me / check me in." — these Actors read public Google Travel data; they do not transact. Hand that off to the hotel's or OTA's own site.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. **Pick the right Actor by the user's question** (see table above). If the user cares about *which hotels and at what rate right now*, that's `google-hotels-scraper`. If they already know *the one hotel* and want *dates*, that's `google-hotels-price-calendar`. If they ask for Vrbo/Airbnb/rentals, that's `google-vacation-rentals-scraper`.
2. **Collect inputs.** For hotels/rentals: destination (city, neighborhood), check-in and check-out dates, number of adults/children/rooms, currency. For the price calendar: a hotel URL from Google Travel (`/travel/hotels/entity/<token>`), start date, number of months, currency.
3. **Build the Actor input** following the JSON schema. All three Actors accept either natural-language `queries` (e.g. `"Paris"`) or `hotelUrls` for pin-point targeting. Set `includeProviderPrices: true` on the hotels Actor to get the per-room per-OTA breakdown — this is the data most price-comparison use cases need.
4. **Run the Actor, confirm cost if large.** Pricing is published on the Store page: hotels/rentals are `$0.002/record`, the price calendar is `$0.0015/date`. Warn the user before any run that would scan more than ~1,000 records.
5. **Deliver results.** Return the dataset ID + a short summary (rows, destination, cheapest result). For comparison tables, group by `providers[].name` and show nightly rate + currency.

For a worked 4-step workflow in a similar skill, see [apify/agent-skills ultimate-scraper](https://github.com/apify/agent-skills/blob/main/skills/apify-ultimate-scraper/SKILL.md).

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Live hotel search by destination + dates, with OTA rates per room | `zet46/google-hotels-scraper` | community | "Hotels in Paris Oct 20-23, nightly rates, Booking.com + Expedia offers per room" |
| Daily/monthly price matrix for one specific hotel | `zet46/google-hotels-price-calendar` | community | "60-day price history for this hotel URL, EUR" |
| Vacation rentals indexed by Google (Vrbo/Airbnb/Booking.com) | `zet46/google-vacation-rentals-scraper` | community | "Vrbo + Airbnb rentals in Lake Tahoe for Dec 1-7, 4 guests, nightly price" |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling Actors — choose your interface

### Option A: Apify CLI (recommended for portability)

    # Search Google Hotels in Paris, two adults, 2 nights, with OTA per-room prices
    apify actors call "zet46/google-hotels-scraper" -i '{
      "queries": ["Paris"],
      "checkIn": "2026-10-20",
      "checkOut": "2026-10-22",
      "adults": 2,
      "currency": "EUR",
      "maxResults": 30,
      "includeProviderPrices": true,
      "minRating": 4.0
    }' --json \
      --user-agent apify-awesome-skills/apify-google-travel-prices \
      2>/dev/null

    # 60-day daily price calendar for one hotel URL
    apify actors call "zet46/google-hotels-price-calendar" -i '{
      "hotelUrls": ["https://www.google.com/travel/hotels/entity/CgsIg..."],
      "startDate": "2026-10-16",
      "months": 2,
      "adults": 2,
      "currency": "EUR"
    }' --json \
      --user-agent apify-awesome-skills/apify-google-travel-prices \
      2>/dev/null

    # Vrbo/Airbnb rentals in Lake Tahoe
    apify actors call "zet46/google-vacation-rentals-scraper" -i '{
      "queries": ["Lake Tahoe"],
      "checkIn": "2026-12-01",
      "checkOut": "2026-12-07",
      "adults": 4,
      "currency": "USD",
      "maxResults": 50,
      "includeProviderPrices": true
    }' --json \
      --user-agent apify-awesome-skills/apify-google-travel-prices \
      2>/dev/null

| Flag | Why |
|------|-----|
| `--json` | Stable machine-readable output |
| `--user-agent` | Apify telemetry attribution |
| `2>/dev/null` | Suppress progress messages that break JSON |

Other useful commands:

    # Fetch the Actor's input schema before building a complex input
    apify actors info "zet46/google-hotels-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-google-travel-prices 2>/dev/null

    # Pull results from a finished run's dataset
    apify datasets get-items DATASET_ID --format json \
      --user-agent apify-awesome-skills/apify-google-travel-prices 2>/dev/null

### Option B: Apify MCP connector

Hosted MCP server at <https://mcp.apify.com>. Documented at
<https://docs.apify.com/platform/integrations/mcp>. Add `zet46/google-hotels-scraper`,
`zet46/google-hotels-price-calendar`, and `zet46/google-vacation-rentals-scraper` to
the tools list and the three Actors become callable as MCP tools.

### Option C: MCP client of your choice (e.g. `mcpc`)

Standalone CLI client. See <https://github.com/apify/mcpc>.

## Troubleshooting

- **Empty `providers[]` on a hotel row** → `includeProviderPrices` was off, or Google did not surface rate offers for that hotel at those dates. Re-run with `includeProviderPrices: true`; if still empty the hotel is genuinely unlisted by OTAs for that window.
- **`hotelUrls` row returns null price** → the URL was malformed (not `/travel/hotels/entity/<token>`) or the hotel has no availability for the requested party size. The Actor skips malformed URLs and only charges for valid ones.
- **Price calendar returns fewer dates than `months * 30`** → Google only publishes a calendar out ~11 months and drops dates fully sold out. This is expected and not a bug.
- **Currency mismatch between query and output** → set `currency` explicitly in the input. If unset the Actor follows Google's default for the Accept-Language locale.
