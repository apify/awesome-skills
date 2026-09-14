---
name: apify-zillow-price-cuts
description: "Find and monitor homes with a recent price cut on Zillow through the Zillow API Actor (johnvc/zillow-api), and get structured JSON rows for each reduced listing: the price change amount, the price change date, days on Zillow, current price, beds, baths, square feet, full address with latitude and longitude, Zestimate, and the listing URL. Pass a plain city or ZIP, set statusType to sale and priceReduction to true, and run it on a schedule to build a week-over-week feed of price-reduced homes for motivated-seller, investor, and agent workflows. Use when someone wants price reduced homes, zillow price cuts, homes with recent price drops, motivated seller leads, or stale-inventory data by city or ZIP. Billed per listing returned, and MCP-ready for Claude and other AI agents."
author: John Cole
author_url: https://github.com/johnisanerd
license: MIT
metadata:
  version: "1.0"
---

# Homes With a Recent Price Cut, as Rows You Can Query

A city or ZIP in, price-reduced homes out as structured rows, each carrying how much the price dropped, when it dropped, and how long the home has been listed.

## When to use this skill

- You want price-reduced homes, the classic signal of a motivated seller or stale inventory.
- You are building a lead feed for agents or investors and want the price cut as numbers, not a badge to read off a page.
- You want a week-over-week feed of new price drops in a market, not a one-time snapshot to eyeball.
- You track a metro to spot where a buyer can negotiate, and need the change amount and days on market on every row.

Not for: a general search of everything for sale, rent, or sold. Use the companion `apify-zillow-api` skill, built on the same Actor for broad listing pulls. See `references/actor-index.md`.

## What you get

One dataset row per reduced listing. `resultType` is `forSale`; branch on it and on the presence of `priceChange`.

Core fields:

- `zpid`, `url`, `title`, `status`
- `price`, `priceValue`, `priceChange` (the drop amount), `priceChangeDate` (when it dropped)
- `daysOnZillow`
- `beds`, `baths`, `squareFeet`, `homeType`
- `street`, `city`, `state`, `zipcode`, `latitude`, `longitude`
- `brokerName`, `zestimate`, `taxAssessedValue`, `scrapedAt`

Plus the resolution provenance on every row: `searchLocation`, `regionId`, `regionName`, `regionType`, `regionAmbiguous`.

The Actor ships a dataset view built for exactly this job: `priceCuts`, which surfaces the change amount, the change date, and days on market together.

## Prerequisites

- Apify account (sign up at https://apify.com?fpr=9n7kx3&fp_sid=awesomeskills).
- Authentication via `apify login`, or an `APIFY_TOKEN` environment variable (Apify Console, Settings, Integrations).

## The Actor

- Store page: https://apify.com/johnvc/zillow-api?fpr=9n7kx3&fp_sid=awesomeskills
- Actor ID: `johnvc/zillow-api`
- Pricing: pay per event, billed per listing returned. See the cost section below and `references/gotchas.md` for the live-price command.

## Run it with the Apify CLI

Price-reduced homes in a metro, capped while you look at the shape:

```bash
apify actors call "johnvc/zillow-api" -i '{"locations":["Phoenix, AZ"],"statusType":"sale","priceReduction":true,"maxResults":50}' \
  --json \
  --user-agent apify-awesome-skills/apify-zillow-price-cuts \
  2>/dev/null
```

Price cuts by ZIP with a price ceiling, the shape for a buyer's lead list:

```bash
apify actors call "johnvc/zillow-api" -i '{"locations":["85008"],"statusType":"sale","priceReduction":true,"priceMax":600000,"maxResults":100}' \
  --json \
  --user-agent apify-awesome-skills/apify-zillow-price-cuts \
  2>/dev/null
```

A wider sweep across a whole metro for a weekly feed:

```bash
apify actors call "johnvc/zillow-api" -i '{"locations":["Dallas, TX"],"statusType":"sale","priceReduction":true,"autoShard":true,"maxUpstreamCalls":40,"maxResults":1000}' \
  --json \
  --user-agent apify-awesome-skills/apify-zillow-price-cuts \
  2>/dev/null
```

Confirm the live schema and prices before a large batch:

```bash
apify actors info "johnvc/zillow-api" --json \
  --user-agent apify-awesome-skills/apify-zillow-price-cuts \
  2>/dev/null
```

Read the rows back from a finished run:

```bash
apify datasets get-items <DATASET_ID> --format json \
  --user-agent apify-awesome-skills/apify-zillow-price-cuts \
  2>/dev/null
```

Every call carries the three flags this repo expects: `--json` (or `--format json`), `--user-agent apify-awesome-skills/apify-zillow-price-cuts`, and `2>/dev/null`.

## Run it from Claude or another AI agent (MCP)

The Actor is MCP-ready. Add the hosted server URL:

`https://mcp.apify.com/?tools=actors,docs,johnvc/zillow-api`

Then ask, for example: "Find homes in Phoenix with a recent price cut under 600000, and rank them by the size of the price drop." MCP setup docs: https://docs.apify.com/platform/integrations/mcp

## Workflow

1. Set `statusType: "sale"` and `priceReduction: true`. That is the whole trick; every returned row is a listing whose price was reduced.
2. Start with one metro and `maxResults: 50`. Confirm `priceChange` and `priceChangeDate` are populated before you widen.
3. Add `priceMax`, `bedsMin`, or `homeType` to shape the lead list, all applied before billing.
4. Sort your results by `priceChange` for the biggest drops, or by `priceChangeDate` for the freshest ones.
5. To build a week-over-week feed, save this input as an Apify task and attach a schedule. Each run is the current set of reduced listings; diff runs downstream to see what is newly reduced.
6. Turn on `autoShard` for a whole-metro pull past 820 results, and cap it with `maxUpstreamCalls`.
7. Read `daysOnZillow` with care; it resets on a relist, so a low value can hide a long true time on market.

## Inputs

- `locations` (array): plain city, ZIP, county, neighborhood, or state names, resolved automatically to the correct Zillow region.
- `statusType` (enum, required): use `sale` for price cuts.
- `priceReduction` (boolean): set `true` to return only reduced listings.
- `priceMin`, `priceMax`, `bedsMin`, `bedsMax`, `bathsMin`, `sqftMin`, `homeType` (filters, applied before billing).
- `timeOnZillow` (string): narrow by how long listings have been up.
- `maxResults` (integer, default 200): the primary spend cap.
- `autoShard` (boolean, default false), `maxUpstreamCalls` (integer, default 40): whole-metro sweeping and its ceiling.
- `ambiguityPolicy` (enum `largest`, `error`, `all`, default `largest`).

## Cost

Billing is pay per event: one `listing_returned` event per delivered listing row. Confirm live prices with the info command above rather than trusting a number copied here.

A search is billed for at least 10 listings, so a metro with only a handful of reduced homes still bills the 10-listing minimum for the page it fetched. Filtered-out listings that never reach the dataset are not billed. Price cuts are a genuine subset of for-sale inventory, so counts per metro are moderate; keep `maxResults` sized to the market.

Suggested confirmation thresholds: mention the estimate under about $5, warn the user over about $5, get explicit confirmation over about $20. Present cost as "around $X", never as a guarantee.

## Honest limits

- `priceChange` and `priceChangeDate` are present because the listing was reduced. They describe the most recent change, not the full price history; the source exposes no per-listing price-history endpoint.
- **This is a snapshot per run, not a delta between runs.** To see what is newly reduced week over week, schedule the run and diff the outputs yourself. A row does not tell you it is new since your last run.
- `daysOnZillow` resets when a home is relisted, so it understates true marketing time, and it does that most on the stalest inventory, which is exactly the inventory this skill surfaces. Never present it as listing age.
- `zestimate` is Zillow's own estimate, not an appraisal. It is context next to the reduced price, not a valuation.
- Public listing data only. No seller contact details; the motivation is inferred from the price cut, not from any private field.

## Troubleshooting

- Rows returned but `priceChange` is null: confirm `priceReduction: true` is set. Without it the search returns all for-sale listings, most of which were never reduced.
- Zero rows, no error: this market has few reduced listings right now, or your filters removed them. Widen `priceMax` or the location.
- `regionAmbiguous` on an error row: the location matched several regions. Set `ambiguityPolicy: "all"` or qualify the name.
- Errors are in-band dataset rows with `resultType: "error"`; branch on `resultType`, not on run status.

See `references/gotchas.md` for cost guardrails and error recovery, and `references/actor-index.md` for the Actor routing table.

## Related Actors

- Zoopla Property API: https://apify.com/johnvc/zoopla-property-api?fpr=9n7kx3&fp_sid=awesomeskills
- Realestate.com.au Property API: https://apify.com/johnvc/realestate-au-property-api?fpr=9n7kx3&fp_sid=awesomeskills
- Google Maps Places API: https://apify.com/johnvc/google-maps-places-api?fpr=9n7kx3&fp_sid=awesomeskills
