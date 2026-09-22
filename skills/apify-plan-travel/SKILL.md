---
name: apify-plan-travel
description: This skill should be used when the user asks to "find flights", "compare flights", "analyze flight search results", "plan a flight itinerary", "plan a complete trip", "plan an event trip", or create an itinerary and budget that combines flights with lodging. It turns supplied or live Apify travel results into a defensible recommendation while preserving unresolved fare scope. Do not use it for hotel-only or lodging-only requests. It prices and advises but never books.
author: John Cole
author_url: https://github.com/johnisanerd
license: MIT
metadata:
  version: "1.0"
  keywords: "flight search, compare flights, multi-city itinerary, open-jaw flights, trip planning, event trip, flights and hotels, travel budget, google flights, google hotels, apify"
---

# Plan flights or a complete trip with Apify

Turn travel data into a decision rather than a list of results. Preserve the requested scope, distinguish sourced prices from estimates, and keep unresolved price or itinerary coverage explicit.

Disclosure: The skill author also maintains the two paid Apify Actors used here.

## Route the request

- **Flights only:** read [references/flights.md](references/flights.md). This includes flight-only round-trip, multi-city, and open-jaw requests. Do not load the hotel or whole-trip references merely because the flight has several segments.
- **Whole trip:** when the requested output combines flights with lodging, an event plan, overnight bases, or a full trip budget, read [references/whole-trip.md](references/whole-trip.md), then [references/flights.md](references/flights.md) and [references/hotels.md](references/hotels.md).
- **Hotel or lodging only:** do not use this skill. Use the selected Actor's current documentation or a dedicated lodging skill.
- **Supplied results:** analyze usable supplied Actor output without rerunning the Actor unless fresher data is requested or required.

## Data sources and prerequisites

For live flight searches, use [Google Flights Data Scraper](https://apify.com/johnvc/google-flights-data-scraper-flight-and-price-search). For lodging within a whole-trip plan, use [Google Hotels Search Scraper](https://apify.com/johnvc/google-hotels-search-scraper). Access them through Apify MCP or another available Apify interface.

Before a live call, inspect the Actor's current README, input schema, pricing, and returned payload. Estimate the intended run before starting paid work. Keep optional billable features off unless the user needs them. Treat the Actor documentation as the source for current inputs and operation; use this skill for the judgment that the documentation does not provide.

## Shared decision rules

1. Use only prices whose currency, itinerary or stay coverage, and price basis are known. Keep incompatible or ambiguous amounts separate.
2. Do not turn missing data into zero or infer a favorable interpretation from plausibility.
3. Rank against the user's priorities. When priorities are unstated, expose the main trade-offs instead of inventing a universal score.
4. Keep ground transport, fuel, parking, meals, taxes, fees, and tickets outside the sourced subtotal unless a cited source priced them for this plan.
5. Do not infer award availability, points prices, program benefits, or alliance and brand membership from cash results. Verify current membership from a primary source when it affects the recommendation.
6. Never book or imply that an option is held. Warn that prices, schedules, and availability must be verified before booking.

## Deliverable

Lead with the recommended flight or trip shape and the evidence behind it. Follow with compact alternatives, meaningful trade-offs, evidence locators or returned booking URLs, price-basis caveats, and a verify-before-booking warning. For a whole trip, include a day-by-day outline, a sourced flight-and-lodging subtotal, and separately labelled estimates or unknowns.

## Example requests

Supported:

- "Compare these supplied flight-search results for Prague to Tokyo and explain the cheapest and best-convenience options."
- "Plan an event trip from Boston to Austin with flights, overnight bases, a day-by-day itinerary, and a clearly sourced budget."

Boundary:

- "Find me a hotel in Vienna for Friday night." This is lodging-only, so do not activate this skill.
