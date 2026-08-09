---
name: apify-google-flights-deals
description: Find genuine google flights deals from a home airport with the Apify Google Flights Deals API Actor (johnvc/google-flights-deals-api). Give one IATA code and get the thirty cheapest destinations back as rows, each carrying the fare, what that route typically costs, the saving between them, and an is_below_typical flag. That flag is the point, because a cheap fare and a good deal are different things, and most of a cheapest-first list is short-haul that is cheap because it is close, not because the price is unusual. There is no arrival airport, the feed answers where can I go cheaply rather than what does this route cost. Filter by stops, cabin, budget, or trip length. Use when the user wants flight deals, cheap flights from an airport, fare drop discovery, or destination inspiration priced against a baseline. Pay per deal returned, MCP-ready for Claude and other AI agents.
author: John Cole
author_url: https://github.com/johnisanerd
license: MIT
metadata:
  version: "1.0"
---

# Google Flights Deals, With Real Bargains Separated From Cheap Short-Hauls

One airport code in, thirty destinations out, each flagged for whether it actually beats what that route normally costs.

## When to use this skill

- The user wants "flight deals" or "cheap flights from" a specific airport.
- They know where they are leaving from but not where they are going.
- They want fare-drop discovery for a newsletter, affiliate site, or travel agent.
- They need the cheapest destinations filtered to nonstop, business class, or a weekend-length trip.

Not for: pricing a route you have already chosen (use `johnvc/Google-Flights-Data-Scraper-Flight-and-Price-Search` and the apify-google-flights-api skill) or building a fare history over time (use the companion apify-google-flights-tracking skill). See `references/actor-index.md`.

## Why the baseline matters

Sort any deals feed by price and the top is dominated by short-haul routes that are cheap because they are close. Every row here also carries `average_price`, what that specific route typically costs, so `is_below_typical` tells you which fares are genuinely unusual. Measured across three hubs during the build, between 6 and 30 percent of a feed clears its own baseline on a given day.

## What you get

One dataset row per destination. `result_type` separates `deal` rows from `error` rows:

- `price`, `average_price`, `savings`, `savings_percent`
- `is_below_typical`, true only when the fare beats that route's own norm
- `name`, `country`, `description`, `thumbnail` for the destination
- `route`, `departure_airport_code`, `arrival_airport_code`
- `outbound_date` and `return_date` for the exact itinerary
- `airline`, `stops`, `flight_duration` in minutes, and `flight_link`

## Prerequisites

- Apify account (sign up at https://apify.com?fpr=9n7kx3&fp_sid=awesomeskills).
- Authentication via `apify login`, or an `APIFY_TOKEN` environment variable (Apify Console, Settings, Integrations).

## The Actor

- Store page: https://apify.com/johnvc/google-flights-deals-api?fpr=9n7kx3&fp_sid=awesomeskills
- Actor ID: `johnvc/google-flights-deals-api`
- Pricing: pay per event; see the cost section below and `references/gotchas.md` for live-price commands.

## Run it with the Apify CLI

The thirty cheapest destinations from one airport:

```bash
apify actors call "johnvc/google-flights-deals-api" -i '{"departureId":"JFK","maxDealsPerAirport":30,"currency":"USD"}' \
  --json \
  --user-agent apify-awesome-skills/apify-google-flights-deals \
  2>/dev/null
```

Nonstop only, under a budget:

```bash
apify actors call "johnvc/google-flights-deals-api" -i '{"departureId":"LAX","maxStops":"nonstop","maxPrice":400}' \
  --json \
  --user-agent apify-awesome-skills/apify-google-flights-deals \
  2>/dev/null
```

Business class, weekend-length trips:

```bash
apify actors call "johnvc/google-flights-deals-api" -i '{"departureId":"ORD","travelClass":"business","travelDuration":"weekend"}' \
  --json \
  --user-agent apify-awesome-skills/apify-google-flights-deals \
  2>/dev/null
```

Confirm live pricing and the input schema before a large batch:

```bash
apify actors info "johnvc/google-flights-deals-api" --json \
  --user-agent apify-awesome-skills/apify-google-flights-deals \
  2>/dev/null
```

Every call carries the three flags this repo expects: `--json`, `--user-agent apify-awesome-skills/apify-google-flights-deals`, and `2>/dev/null`.

## Run it from Claude or another AI agent (MCP)

The Actor is MCP-ready. Add the hosted server URL:

`https://mcp.apify.com/?tools=actors,docs,johnvc/google-flights-deals-api`

Then ask, for example: "Where can I fly cheaply from Chicago next month, and which of those are actually below their normal price?" MCP setup docs: https://docs.apify.com/platform/integrations/mcp

## Workflow

1. Set `departureId` to one IATA code, or `departureIds` to several. There is no arrival field.
2. Leave `outboundDate` blank unless dates are fixed; the feed then picks cheap dates and reports the ones it found.
3. Apply at most one or two filters at a time so you can tell which one changed the result.
4. Filter rows on `is_below_typical` rather than sorting on `price`.
5. Rank the survivors by `savings_percent` and hand off `flight_link` for booking.

## Inputs

- `departureId` (string): one IATA code, for example `JFK`
- `departureIds` (array): several home airports in one run
- `tripType` (enum `round_trip`, `one_way`, default `round_trip`)
- `outboundDate` / `returnDate` (string): leave blank to let the feed choose
- `travelDuration` (enum `any`, `one_week`, `weekend`, `two_weeks`, default `any`)
- `travelClass` (enum `economy`, `premium_economy`, `business`, `first`, default `economy`)
- `maxStops` (enum `any`, `nonstop`, `one_stop`, `two_stops`, default `any`)
- `maxPrice` (integer): budget ceiling
- `includeAirlines` / `excludeAirlines` (string): mutually exclusive
- `maxDealsPerAirport` (integer, default 30, max 30)
- `adults`, `children`, `infants` (integer)
- `currency` (string, default `USD`), `hl` (default `en`), `gl` (string)

## Cost

Billing is pay per event, plus a negligible platform fee per dataset row. Prices below are the BRONZE tier at the time of writing; confirm live prices with the info command above.

- About $0.0025 per deal returned.
- About $0.001 to start a run.
- A full thirty-destination sweep from one airport is about $0.08.
- Three home airports at thirty each is about $0.23.

Suggested confirmation thresholds: warn the user over about $5; get explicit confirmation over about $20. Present cost as "around $X", never a guarantee.

## Honest limits

- No arrival airport. This answers where to go, not what a chosen route costs.
- Thirty destinations per airport is the ceiling, not a setting you can raise.
- `maxDurationMinutes` makes the source stop returning the baseline, which switches off `savings`, `savings_percent`, and `is_below_typical`. The Actor logs a warning when you set it. Every other filter keeps the baseline.
- This is a snapshot, not a tracker. It keeps no history and sends no alerts.
- Negative savings are real, not a bug: that route is currently priced above its own norm.

## Troubleshooting

- No bargains in the results: normal on a given day. Check whether any row has `is_below_typical` true before assuming the run failed.
- `savings` and `is_below_typical` are missing everywhere: `maxDurationMinutes` is set. Remove it.
- Empty feed: thin-coverage airport. Try a larger hub nearby.
- An `error` row: clean failure, stated plainly; retry once before investigating.

See `references/gotchas.md` for cost guardrails and error recovery, and `references/actor-index.md` for the Actor routing table.

## Related Actors

- Google Travel Explore API: https://apify.com/johnvc/google-travel-explore-api?fpr=9n7kx3&fp_sid=awesomeskills
- Google Flights Data Scraper: https://apify.com/johnvc/Google-Flights-Data-Scraper-Flight-and-Price-Search?fpr=9n7kx3&fp_sid=awesomeskills
- Google Hotels Search Scraper: https://apify.com/johnvc/google-hotels-search-scraper?fpr=9n7kx3&fp_sid=awesomeskills
- Google Maps Photos API: https://apify.com/johnvc/google-maps-photos-api?fpr=9n7kx3&fp_sid=awesomeskills
