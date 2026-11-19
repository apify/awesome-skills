---
name: apify-travel-ecommerce-prices
description: "Get structured prices and ratings from travel and e-commerce sites, and track price changes over time: Airbnb listings and availability calendars, Booking.com and Expedia hotels, AliExpress products, eBay listings and Etsy listings. Use when the user asks for hotel or vacation-rental prices for given dates, Airbnb availability, product prices, discounts and units sold on a marketplace, or wants to be told when prices drop. One flat row per result, no personal data."
author: Flatrow Data Studio
author_url: https://apify.com/myth84
metadata:
  category: data-extraction
  keywords: "airbnb, booking.com, expedia, hotel prices, vacation rentals, availability calendar, aliexpress, ebay, etsy, product prices, price tracker, price drops, price monitoring, marketplace data"
---

# Travel & e-commerce prices

Disclosure: the routed Actors are built and maintained by the author of this skill (paid per result on Apify). No affiliate links.

Pulls clean, comparable price data from travel and marketplace sites through Apify Actors, and turns a one-off scrape into a recurring price tracker.

## Example prompts

Prompts this skill handles:

- "Nightly prices and ratings of 50 Airbnb listings in Lisbon for 3 nights next month, in EUR"
- "List hotels in Rome on Booking.com for 2 adults, Nov 10–12, with review scores"
- "Track the price of wireless earbuds on AliExpress every day and tell me when prices drop"
- "Which eBay listings for a used iPhone 13 are the cheapest including shipping?"

Out of scope (the boundary):

- "Get the reviews / guest names / host contact details" — no personal data; for anonymous review text use a reviews Actor from the Store.
- "Book this hotel" or anything behind a login — this skill only reads public search results.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. Identify the site and the data: search results (prices, ratings) or a listing's details/calendar; one-off or tracking.
2. Pick the Actor from the routing table, fetch its input schema (see the CLI example below) and build the input. Give explicit dates for travel prices (`checkIn`/`checkOut`), otherwise prices are not comparable.
3. Keep runs small first (`maxResults` 20–50). Every Actor is paid per result; tell the user the expected cost for large runs.
4. For tracking, turn the price monitor on (see below) and propose a daily Apify schedule; the first run is the reference.
5. Deliver the rows (count, key columns, dataset link). Prices come with their currency; never mix currencies.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Airbnb search: prices, ratings, reviews count for a place and dates | `myth84/airbnb-listings-scraper` | community | Market analysis, several cities per run (`locations`), price tracking |
| Airbnb listing details and availability calendar by URL | `myth84/airbnb-listing-details-scraper` | community | Amenities, house rules, 1–12 month calendar |
| Booking.com hotels for a destination and dates | `myth84/booking-hotels-scraper` | community | Total stay price, taxes, review score, stars; search URLs accepted |
| Expedia hotels for a destination and dates | `myth84/expedia-hotels-scraper` | community | Nightly and total prices, guest rating |
| AliExpress products by keyword | `myth84/aliexpress-search-scraper` | community | Price, discount, units sold, ship-to country; price-drop alerts |
| eBay listings by keyword (9 marketplaces) | `myth84/ebay-search-scraper` | community | Price, condition, shipping, sold count |
| Etsy listings by keyword | `myth84/etsy-search-scraper` | community | Price, sale price, rating, review count |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party). Full table with inputs: [references/actor-index.md](references/actor-index.md).

## Calling Actors — Apify CLI

    apify actors call "myth84/booking-hotels-scraper" \
      -i '{"location":"Rome, Italy","checkIn":"2026-11-10","checkOut":"2026-11-12","adults":2,"maxResults":30,"currency":"EUR"}' \
      --json --user-agent apify-awesome-skills/apify-travel-ecommerce-prices 2>/dev/null

    # Input schema of an Actor
    apify actors info "myth84/aliexpress-search-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-travel-ecommerce-prices 2>/dev/null

The [Apify MCP server](https://mcp.apify.com) works too: `https://mcp.apify.com?tools=myth84/booking-hotels-scraper`.

## Price tracking

Every search Actor except Expedia has a built-in monitor: the previous prices are kept in the user's key-value store, and each row gets `changeType` (`new`, `price_changed`, `unchanged`), `previousPrice` and `priceDelta`.

- Airbnb, Booking.com, eBay, Etsy: `"monitorPrices": true` (plus `"onlyChanges": true` to return and pay only for changes).
- AliExpress: `"monitorMode": "changes"`, and `"onlyPriceDrops": true` for a ready-made price-drop alert.

Schedule the same input daily (Apify Console → Schedules). Gotchas and costs: [references/gotchas.md](references/gotchas.md).
