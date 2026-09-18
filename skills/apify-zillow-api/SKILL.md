---
name: apify-zillow-api
description: "Search US real estate listings on Zillow through the Zillow API Actor (johnvc/zillow-api) and get structured JSON rows: zpid, price, beds, baths, square feet, home type, full address with latitude and longitude, broker, Zestimate, rent Zestimate, tax-assessed value, days on Zillow, and the listing URL. Takes plain city, ZIP, county, neighborhood, or state names and resolves each to the correct Zillow region for you, so a bare ZIP never silently returns the wrong city. Choose for sale, for rent, or recently sold; filter by price, beds, baths, square feet, and home type before billing; and sweep a whole metro past the 820-result cap with map-bounds sharding. Use when someone wants a zillow api, zillow data by city or ZIP, a Zillow API alternative to the gated official developer program, or to fill a CRM, dashboard, or model with for-sale, rental, or sold listings. Billed per listing returned, and MCP-ready for Claude and other AI agents."
author: John Cole
author_url: https://github.com/johnisanerd
license: MIT
metadata:
  version: "1.0"
---

# Zillow Listings, as Rows You Can Query

Plain locations in, live Zillow listings out as structured rows, with the region resolved correctly for you so a ZIP never lands on the wrong town.

## When to use this skill

- Someone wants a Zillow API and found only the official developer program, which is invite-only, unpriced, and gated behind a partner review.
- You are filling a CRM, a market dashboard, a valuation model, or a lead tool with for-sale, rental, or recently sold listings.
- You have a list of cities or ZIP codes and want listings back as JSON, not a page of search results to read by hand.
- You need latitude and longitude on every row so listings can be joined to a map or a geo dataset.

Not for: tracking homes whose price just dropped. Use the companion `apify-zillow-price-cuts` skill, built on the same Actor but shaped for price-drop monitoring. See `references/actor-index.md`.

## What you get

One dataset row per listing. `resultType` separates `forSale`, `rental`, `sold`, and `error` rows, so a sale search that returns a sold row is still labeled honestly.

Core fields (for sale and sold):

- `zpid`, `url`, `title`, `status`, `statusType`
- `price`, `priceValue`, `priceChange`, `priceChangeDate`
- `beds`, `baths`, `squareFeet`, `homeType`
- `street`, `city`, `state`, `zipcode`, `latitude`, `longitude`
- `brokerName`, `zestimate`, `rentZestimate`, `taxAssessedValue`, `soldDate`, `daysOnZillow`
- `thumbnail`, `images` (URLs only, opt-in), `scrapedAt`

Rental rows are building-level, so they carry `buildingName`, `minBaseRent`, `maxBaseRent`, `availableUnits`, `phone`, `amenityHighlight`, and per-floorplan `units`, with `lotId` and `providerListingId` as identity in place of `zpid`.

Every row also carries the resolution provenance: `searchLocation`, `regionId`, `regionName`, `regionType`, `regionAmbiguous`, and `regionAlternatives`, so you can see exactly which Zillow region answered.

The Actor ships dataset views for the console: `overview`, `priceCuts`, `rentals`, `sold`, and `map`.

## Prerequisites

- Apify account (sign up at https://apify.com?fpr=9n7kx3&fp_sid=awesomeskills).
- Authentication via `apify login`, or an `APIFY_TOKEN` environment variable (Apify Console, Settings, Integrations).

## The Actor

- Store page: https://apify.com/johnvc/zillow-api?fpr=9n7kx3&fp_sid=awesomeskills
- Actor ID: `johnvc/zillow-api`
- Pricing: pay per event, billed per listing returned. See the cost section below and `references/gotchas.md` for the live-price command.

## Run it with the Apify CLI

Homes for sale in a city, capped at 10 while you look at the shape:

```bash
apify actors call "johnvc/zillow-api" -i '{"locations":["Austin, TX"],"statusType":"sale","maxResults":10}' \
  --json \
  --user-agent apify-awesome-skills/apify-zillow-api \
  2>/dev/null
```

Rentals by ZIP, with the building-level rental fields:

```bash
apify actors call "johnvc/zillow-api" -i '{"locations":["78704"],"statusType":"rent","maxResults":50}' \
  --json \
  --user-agent apify-awesome-skills/apify-zillow-api \
  2>/dev/null
```

Recently sold homes for comping (sold date, Zestimate, and assessed value, never a sale price):

```bash
apify actors call "johnvc/zillow-api" -i '{"locations":["Phoenix, AZ"],"statusType":"sold","maxResults":100}' \
  --json \
  --user-agent apify-awesome-skills/apify-zillow-api \
  2>/dev/null
```

Sweep a whole metro past the 820-result cap:

```bash
apify actors call "johnvc/zillow-api" -i '{"locations":["Dallas, TX"],"statusType":"sale","autoShard":true,"maxUpstreamCalls":40,"maxResults":2000}' \
  --json \
  --user-agent apify-awesome-skills/apify-zillow-api \
  2>/dev/null
```

Confirm the live schema and prices before a large batch:

```bash
apify actors info "johnvc/zillow-api" --json \
  --user-agent apify-awesome-skills/apify-zillow-api \
  2>/dev/null
```

Read the rows back from a finished run:

```bash
apify datasets get-items <DATASET_ID> --format json \
  --user-agent apify-awesome-skills/apify-zillow-api \
  2>/dev/null
```

Every call carries the three flags this repo expects: `--json` (or `--format json`), `--user-agent apify-awesome-skills/apify-zillow-api`, and `2>/dev/null`.

## Run it from Claude or another AI agent (MCP)

The Actor is MCP-ready. Add the hosted server URL:

`https://mcp.apify.com/?tools=actors,docs,johnvc/zillow-api`

Then ask, for example: "Get homes for sale in Austin under 500000 with at least 3 beds, and return address, price, and the listing URL." MCP setup docs: https://docs.apify.com/platform/integrations/mcp

## Workflow

1. Start with one location and `maxResults: 10`. Look at the row shape before you pay for a wide pull.
2. Pass plain locations. "Austin, TX", "78704", "Travis County, TX", and "Texas" all resolve; a bare five-digit string resolves as a ZIP to the correct region, never as a pass-through that would return the wrong town.
3. Pick `statusType`: `sale`, `rent`, or `sold`. The row shape follows the listing, not the input, so branch on `resultType`.
4. Filter at the source. `priceMin`, `priceMax`, `bedsMin`, `bathsMin`, `sqftMin`, `homeType`, and the rest drop listings before they are billed.
5. Turn on `autoShard` only when you need more than 820 results for one location, and cap it with `maxUpstreamCalls`. Off by default so a run never surprises you with a large bill.
6. Dedupe on `zpid` for sale and sold rows; use `lotId` or `providerListingId` for rentals, which are building-level and often carry no `zpid`.
7. Keep `latitude` and `longitude` if you plan to map or join. They are on every row for that reason.

## Inputs

- `locations` (array): plain city, ZIP, county, neighborhood, or state names, resolved automatically. Prefix a value with `zip:`, `city:`, `county:`, `neighborhood:`, `msa:`, or `state:` to force a type.
- `statusType` (enum `sale`, `rent`, `sold`, required)
- `ambiguityPolicy` (enum `largest`, `error`, `all`, default `largest`): how to resolve a name that maps to more than one region.
- `regionId` (string), `mapBounds` (string): advanced overrides; prefer `locations`.
- `homeType`, `listingType`, `listingStatus` (arrays)
- `priceMin`, `priceMax`, `bedsMin`, `bedsMax`, `bathsMin`, `bathsMax`, `sqftMin`, `sqftMax`, `yearBuiltMin`, `yearBuiltMax` (integers)
- `priceReduction` (boolean), `tours` (array), `keywords` (string), and the rest of Zillow's filter set.
- `maxResults` (integer, default 200): the primary spend cap.
- `autoShard` (boolean, default false), `maxUpstreamCalls` (integer, default 40): whole-metro sweeping and its ceiling.
- `includeImages` (boolean, default false): image URLs add many values per row; off by default.

## Cost

Billing is pay per event: one `listing_returned` event per delivered listing row. Confirm live prices with the info command above rather than trusting a number copied here.

A search is billed for at least 10 listings, so a search that returns fewer, or none, still bills the 10-listing minimum for the page it fetched. Filtered-out listings that never reach the dataset are not billed. Keep `maxResults` low while exploring, and turn `autoShard` on deliberately, since each shard is its own page.

Suggested confirmation thresholds: mention the estimate under about $5, warn the user over about $5, get explicit confirmation over about $20. Present cost as "around $X", never as a guarantee.

## Honest limits

- **Sold rows carry no sale price.** The source exposes only the sold date, the Zestimate, and the tax-assessed value for sold listings, so treat sold data as recently-sold context with an estimate, never as closed sale prices.
- **Zestimate is an estimate.** The Zestimate and rent Zestimate are Zillow's own estimates, not appraisals, and no field is a recommended rent.
- **Images are URLs only.** Photo fields pass through the source URL and are never downloaded, cached, or re-hosted.
- `daysOnZillow` resets when a listing is relisted, so it can understate how long a home has truly been on the market. Do not present it as listing age.
- One search is capped at 820 results. `autoShard` splits the map to exceed that; a point with more listings than a single tile can hold is marked `truncated`.
- Public listing data only. No agent contact details beyond the broker name shown on the listing, and nothing behind a login.

## Troubleshooting

- Zero rows and no error row: your filters removed everything, or the location has little inventory for that `statusType`. Relax the filters or widen the location.
- An `error` row with `regionAmbiguous`: the name mapped to several regions. Set `ambiguityPolicy` to `all`, or qualify the location (add the state, or use a prefix).
- Wrong-city results: pass the town with its state, or use a `city:` or `zip:` prefix. The resolver never passes a raw ZIP straight through, so a mismatch is almost always an ambiguous name.
- A `truncated` row: the tile held more listings than one search returns. It is a completeness note, not an error.
- Errors are in-band dataset rows with `resultType: "error"`; pipelines should branch on `resultType`, not on run status.

See `references/gotchas.md` for cost guardrails and error recovery, and `references/actor-index.md` for the Actor routing table.

## Related Actors

- Zoopla Property API: https://apify.com/johnvc/zoopla-property-api?fpr=9n7kx3&fp_sid=awesomeskills
- Realestate.com.au Property API: https://apify.com/johnvc/realestate-au-property-api?fpr=9n7kx3&fp_sid=awesomeskills
- Google Maps Places API: https://apify.com/johnvc/google-maps-places-api?fpr=9n7kx3&fp_sid=awesomeskills
