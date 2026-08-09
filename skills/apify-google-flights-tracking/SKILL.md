---
name: apify-google-flights-tracking
description: Build your own fare history for google flights tracking with the Apify Google Flights Deals API Actor (johnvc/google-flights-deals-api). Run it on a schedule against one or several home airports and every row arrives with the fare, what that route typically costs, the gap between them, exact dates, airline and a booking link, so successive runs accumulate into a price record you own and can query. This is the data layer under a price-alert product, not the alerting itself. The Actor takes a snapshot and keeps no history and sends no notifications, so the repeated observation is yours to store and the notify rule is yours to write, and a baseline in every row means that rule can be below typical instead of a threshold you guessed. Use when the user wants flight price tracking, airfare monitoring, fare data with a reference price, or the source feed behind flight price alerts. Pay per deal returned, MCP-ready for Claude and other AI agents.
author: John Cole
author_url: https://github.com/johnisanerd
license: MIT
metadata:
  version: "1.0"
---

# Google Flights Tracking: Your Own Fare History, With a Baseline in Every Row

Schedule the deals feed, store the rows, and you own a fare record where every observation already knows what that route normally costs.

## When to use this skill

- The user wants "flight price tracking" or airfare monitoring from their own data.
- They are building a price-alert product and need a source feed to sit under it.
- They want fare data where each row carries a reference price, not just a number.
- They want to watch several home airports on one schedule.

Not for: a one-shot look at today's bargains (use the companion apify-google-flights-deals skill) or pricing a specific route you have already picked (`johnvc/Google-Flights-Data-Scraper-Flight-and-Price-Search`). See `references/actor-index.md`.

## What this does and does not do

An alert is two pieces: a repeated observation, and a rule about when to notify. This Actor is the observation half. It returns a snapshot each run, keeps no history, and sends nothing. You schedule it, you store the rows, and you write the rule. Any copy or agent response that implies this Actor notifies the user is wrong.

The payoff for doing it this way is `average_price`. Because every observation arrives with what that route typically costs, your notify rule can be "below typical" rather than a fixed threshold you guessed at.

## What you get

One dataset row per destination, per run. `result_type` separates `deal` rows from `error` rows:

- `price` and `average_price`, the observation and its reference
- `savings`, `savings_percent`, `is_below_typical`
- `route`, `departure_airport_code`, `arrival_airport_code`
- `outbound_date` and `return_date` for the exact itinerary priced
- `airline`, `stops`, `flight_duration` in minutes, `flight_link`
- `name`, `country`, `description`, `thumbnail` for the destination

Key your storage on departure, arrival, and travel date, and add the run timestamp yourself.

## Prerequisites

- Apify account (sign up at https://apify.com?fpr=9n7kx3&fp_sid=awesomeskills).
- Authentication via `apify login`, or an `APIFY_TOKEN` environment variable (Apify Console, Settings, Integrations).

## The Actor

- Store page: https://apify.com/johnvc/google-flights-deals-api?fpr=9n7kx3&fp_sid=awesomeskills
- Actor ID: `johnvc/google-flights-deals-api`
- Pricing: pay per event; see the cost section below and `references/gotchas.md` for live-price commands.

## Run it with the Apify CLI

One observation across three home airports:

```bash
apify actors call "johnvc/google-flights-deals-api" -i '{"departureIds":["JFK","EWR","LGA"],"maxDealsPerAirport":30,"currency":"USD"}' \
  --json \
  --user-agent apify-awesome-skills/apify-google-flights-tracking \
  2>/dev/null
```

Pin the shape you want to track so successive runs stay comparable:

```bash
apify actors call "johnvc/google-flights-deals-api" -i '{"departureId":"SFO","maxStops":"nonstop","travelClass":"economy","maxDealsPerAirport":30}' \
  --json \
  --user-agent apify-awesome-skills/apify-google-flights-tracking \
  2>/dev/null
```

Confirm live pricing and the input schema before scheduling a sweep:

```bash
apify actors info "johnvc/google-flights-deals-api" --json \
  --user-agent apify-awesome-skills/apify-google-flights-tracking \
  2>/dev/null
```

Every call carries the three flags this repo expects: `--json`, `--user-agent apify-awesome-skills/apify-google-flights-tracking`, and `2>/dev/null`.

## Run it from Claude or another AI agent (MCP)

The Actor is MCP-ready. Add the hosted server URL:

`https://mcp.apify.com/?tools=actors,docs,johnvc/google-flights-deals-api`

Then ask, for example: "Take today's reading for my three New York airports and tell me which routes are below their typical price." MCP setup docs: https://docs.apify.com/platform/integrations/mcp

## Workflow

1. Decide the shape you are tracking: airports, cabin, and stops. Keep it fixed so readings stay comparable.
2. Save it as an Apify task, then attach a schedule. Daily is enough for most fare movement.
3. Append each run's rows to your own store, keyed on departure, arrival, and travel date, stamped with the run time.
4. Write the notify rule against `is_below_typical` or a `savings_percent` floor you choose.
5. Watch `average_price` too, not just `price`. A baseline that drifts down means the route repriced, which is different from a sale.

## Inputs

- `departureId` (string) or `departureIds` (array): the airports you watch
- `maxDealsPerAirport` (integer, default 30, max 30)
- `travelClass` (enum `economy`, `premium_economy`, `business`, `first`, default `economy`)
- `maxStops` (enum `any`, `nonstop`, `one_stop`, `two_stops`, default `any`)
- `travelDuration` (enum `any`, `one_week`, `weekend`, `two_weeks`, default `any`)
- `tripType` (enum `round_trip`, `one_way`, default `round_trip`)
- `outboundDate` / `returnDate` (string): leave blank so the feed keeps finding cheap dates
- `maxPrice` (integer), `includeAirlines` / `excludeAirlines` (string)
- `currency` (default `USD`), `hl` (default `en`), `gl` (string)

## Cost

Billing is pay per event, plus a negligible platform fee per dataset row. Prices below are the BRONZE tier at the time of writing; confirm live prices with the info command above.

- About $0.0025 per deal returned.
- About $0.001 to start a run.
- One airport at thirty deals is about $0.08 per reading, so roughly $2.30 a month daily.
- Three airports daily is roughly $7 a month.

Suggested confirmation thresholds: warn the user over about $5; get explicit confirmation over about $20. Present cost as "around $X", never a guarantee. Scheduled tracking is recurring spend, so state the monthly figure, not just the per-run one.

## Honest limits

- No history and no alerts inside the Actor. Both are yours to build, and copy must not claim otherwise.
- The destination set can change between runs, since it is the cheapest thirty rather than a fixed watchlist. A route can drop out because it got expensive.
- With dates left blank the itinerary moves between runs, so you are tracking the cheapest available trip, not one fixed departure.
- `maxDurationMinutes` switches off the baseline and with it `savings` and `is_below_typical`. Never set it on a tracking schedule.
- Thirty destinations per airport is a hard ceiling.

## Troubleshooting

- A route vanished between runs: it left the cheapest thirty. Treat absence as missing data, not a price of zero.
- The baseline disappeared: `maxDurationMinutes` is set. Remove it and re-run.
- Readings look noisy: the itinerary is floating because dates are blank. Pin `outboundDate` if you need one fixed departure.
- Costs climbing faster than expected: count airports times deals times runs per month before widening a schedule.

See `references/gotchas.md` for cost guardrails and error recovery, and `references/actor-index.md` for the Actor routing table.

## Related Actors

- Google Flights Data Scraper: https://apify.com/johnvc/Google-Flights-Data-Scraper-Flight-and-Price-Search?fpr=9n7kx3&fp_sid=awesomeskills
- Google Travel Explore API: https://apify.com/johnvc/google-travel-explore-api?fpr=9n7kx3&fp_sid=awesomeskills
- Google Hotels Search Scraper: https://apify.com/johnvc/google-hotels-search-scraper?fpr=9n7kx3&fp_sid=awesomeskills
- Google Maps Photos API: https://apify.com/johnvc/google-maps-photos-api?fpr=9n7kx3&fp_sid=awesomeskills
