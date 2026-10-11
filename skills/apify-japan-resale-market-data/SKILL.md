---
name: apify-japan-resale-market-data
description: "Pull structured second-hand and resale prices from Japanese marketplaces — anime figures and hobby goods (Suruga-ya, Mandarake), used cameras (Kitamura), used watches (Jackroad), and pre-owned luxury brands (Komehyo). Use when the user asks about Japan resale prices, Japanese second-hand market data, anime figure resale values, used camera or watch prices in Japan, pre-owned luxury brand pricing in Japan, Japanese hobby shop price monitoring, or wants to build a Japan resale price dataset. Covers Mandarake auction bids, Suruga-ya stock prices, normalized anime-figure price history, and brand watch/camera resale listings."
author: atushi1841
author_url: https://github.com/atushi1841
metadata:
  category: data-extraction
  keywords: "japan resale prices, japanese second-hand market, anime figure prices, suruga-ya, mandarake, used camera japan, used watch japan, pre-owned luxury japan, komehyo, kitamura, hobby shop prices, japan market data"
---

# Japan Resale & Hobby Market Data

Retrieve structured pricing from Japan's second-hand and resale marketplaces: hobby and
collectible shops, used-camera chains, pre-owned watch dealers, and luxury-brand resellers.
Every Actor returns one row per listing with an explicit JPY price field, so results can be
compared, trended, or joined without HTML parsing.

**Disclosure:** all Actors routed by this skill are built and maintained by the author
(Apify user `fruitful_quintessence`). No affiliate or referral parameters are used; the
Apify Store links are plain.

## Example prompts

Prompts this skill handles:

- "What are used anime figures going for in Japan right now?"
- "Pull the current Mandarake auction listings for Vocaloid cosplay items."
- "Compare used camera prices at Kitamura against the resale market."
- "Get me Japanese pre-owned luxury handbag listings with prices."
- "Build a dataset of Japanese used-watch prices for Rolex models."

Out of scope (the boundary — route these elsewhere):

- Live purchase, checkout, or bidding on any marketplace → this skill is read-only data extraction.
- Non-Japanese marketplaces (eBay, Chrono24) → use a store-wide Actor for those sites instead.
- Scraping a site that is NOT one of the Actors below → search the Apify Store for a dedicated Actor first.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. Map the user's request to a marketplace in the routing table below.
2. Build the Actor input with the documented fields (see `references/actor-index.md`).
3. Confirm before a large run: these Actors are **pay-per-result**, so the charge cap
   (`maxItems` on the REST API, `maxResults` in the Actor input) directly controls cost.
   Start with a small cap, then scale. **A PPE Actor run is rejected outright if you do not
   set the charge cap** — see the REST example below for the exact parameter placement.
4. Run the Actor and report back the item count, the price field, and the dataset link.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Hobby/collectible auction listings (Mandarake) | `fruitful_quintessence/mandarake-auction-scraper` | community | Auction current price, bid count, watch count |
| Used hobby/collectible stock (Suruga-ya) | `fruitful_quintessence/surugaya-japan-hobby-prices` | community | In-stock retail prices for used goods |
| Anime figure price history (normalized) | `fruitful_quintessence/japan-anime-figure-price-data` | community | Multi-shop normalized figure prices |
| Used cameras (Kitamura) | `fruitful_quintessence/kitamura-japan-used-camera-scraper` | community | Used camera bodies/lenses with maker + JAN |
| Used watches (Jackroad) | `fruitful_quintessence/jackroad-used-watch-scraper` | community | Pre-owned luxury watch listings |
| Pre-owned luxury brands (Komehyo) | `fruitful_quintessence/komehyo-japan-brand-scraper` | community | Brand, rank, size, reference price |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party). All rows above are
community Actors authored by this skill's author.

## Calling Actors — choose your interface

Skills in this repo can call Actors via any of these interfaces. Pick the one
that fits your runtime; cross-tool compatibility is your responsibility.

### Option A: Apify CLI (recommended for portability)

Three flags on every call:

```bash
apify actors call "fruitful_quintessence/mandarake-auction-scraper" \
  -i '{"mode": "category", "category": "toys", "keyword": "", "maxPages": 2, "maxResults": 50, "language": "ja"}' \
  --json \
  --user-agent apify-awesome-skills/apify-japan-resale-market-data \
  2>/dev/null
```

| Flag | Why |
|------|-----|
| `--json` | Stable machine-readable output |
| `--user-agent` | Apify telemetry attribution |
| `2>/dev/null` | Suppress progress messages that break JSON |

Search the Store before assuming an Actor exists:

```bash
apify actors search "japan resale" --json --limit 10 \
  --user-agent apify-awesome-skills/apify-japan-resale-market-data 2>/dev/null
```

Fetch the run history to inspect the exact input a previous run used:

```bash
apify runs ls "fruitful_quintessence/mandarake-auction-scraper" --json --limit 1 \
  --user-agent apify-awesome-skills/apify-japan-resale-market-data 2>/dev/null
```

### Option B: Apify MCP connector

Use the hosted connector at `https://mcp.apify.com` and call the same Actor IDs. Response
shapes match Option A; only the transport differs.

### Option C: REST API (verified end-to-end)

For a scripted pipeline, call the run endpoint directly. **The charge cap is a query
parameter, not an input field** — omitting it fails with
`max-items-must-be-greater-than-zero`:

    curl -s -X POST \
      -H "Authorization: Bearer $APIFY_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"mode":"category","category":"toys","maxPages":1,"maxResults":10,"language":"ja"}' \
      "https://api.apify.com/v2/acts/fruitful_quintessence~mandarake-auction-scraper/runs?maxItems=10&waitForFinish=120"

A verified run of exactly that command returned `status: SUCCEEDED`,
`statusMessage: "Returned 10 items for category mode"`. Read the rows back with:

    curl -s -H "Authorization: Bearer $APIFY_TOKEN" \
      "https://api.apify.com/v2/datasets/$DATASET_ID/items?limit=10&clean=true"

Never put the token in the URL — always the `Authorization` header.

## Input reference

Every Actor accepts a small JSON input. Verified shapes (2026-10):

| Actor | Verified input example |
|-------|------------------------|
| mandarake-auction-scraper | `{"mode":"category","category":"toys","keyword":"","maxPages":2,"maxResults":50,"language":"ja","proxyConfiguration":{"useApifyProxy":true,"apifyProxyCountry":"JP"}}` |
| surugaya-japan-hobby-prices | `{"searchKeyword":"トイザラス","maxPages":3,"inStockOnly":false,"maxResults":50,"proxyConfiguration":{"useApifyProxy":true,"apifyProxyCountry":"JP"}}` |
| kitamura-japan-used-camera-scraper | `{"keyword":"","sort":"default","maxItems":100}` |
| jackroad-used-watch-scraper | `{"keyword":"ROLEX","classification":"2","maxItems":100}` |
| komehyo-japan-brand-scraper | `{"keyword":"ルイヴィトン","maxItems":100}` |

Keyword fields accept Japanese text directly (e.g. `トイザラス`, `ルイヴィトン`) — pass UTF-8,
do not romanize.

## Output reference

Representative item fields, verified from real runs:

- `mandarake-auction-scraper` → `item_no`, `name`, `current_price_jpy`, `start_price_jpy`,
  `bid_count`, `watch_count`, `shop_name`, `image_url`, `item_url`, `auction_type`, `scraped_at`
- `kitamura-japan-used-camera-scraper` → `productId`, `title`, `price`, `maker`, `shop`,
  `category`, `description`, `imageUrl`, `productUrl`, `janCode`, `salesStatus`, `scrapedAt`
- `komehyo-japan-brand-scraper` → `productId`, `title`, `brand`, `price`, `referencePrice`,
  `rank`, `size`, `material`, `store`, `imageUrl`, `productUrl`, `scrapedAt`

Note the mixed naming: Mandarake uses `*_jpy` suffixes, the other Actors use a bare `price`
(JPY, integer, no currency symbol) plus a `*At` timestamp. Always read the field name from the
item, not from an assumed schema.

## Cost guardrails

- All six Actors are **pay-per-result (PAY_PER_EVENT)**. There is no free tier inside the Actor;
  you pay per delivered listing. See `references/gotchas.md` for the traps.
- Set `maxResults` (Mandarake, Suruga-ya) or `maxItems` (Kitamura, Jackroad, Komehyo) on every run.
  Omitting it can let a category crawl run long.
- `maxPages` compounds cost on the two paginated Actors — 2 pages at 50 results is up to 100 rows.
- Apify's own monthly free credit applies to your account, not to the Actor.

## Failure modes

- **Zero items**: the keyword found nothing, or the marketplace changed markup. Retry with an
  empty keyword on a known-populated category (e.g. `toys` on Mandarake) to separate "no match"
  from "broken scrape".
- **HTTP 403 / challenge page**: the marketplace rate-limited the run. Wait and retry; do not
  fan out many concurrent runs against the same domain.
- **Prices look like strings**: some listings land as text; cast before arithmetic and drop rows
  whose price is missing rather than defaulting to 0.
- **Japanese text garbled**: responses are UTF-8. If the Agent's transport mangles it, write the
  dataset to a file and read it back rather than piping through a lossy console.

## Validation rule for any claim

Never state a price, a trend, or a "market average" without a run behind it. Report the row count
and the dataset ID alongside any number, so the user can re-verify.
