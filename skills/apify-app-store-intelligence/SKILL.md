---
name: apify-app-store-intelligence
description: App-store intelligence and ASO research across the Apple App Store, Google Play, and the Shopify App Store. Pull app details, exact ratings and ratings histograms, customer reviews, and keyword/category rankings, then compare an app against its competitors. Use when the user asks to scrape App Store or Google Play data, track app reviews or ratings over time, do ASO / app-store keyword rank research, monitor competitor apps, mine app reviews for sentiment or feature requests, or research the Shopify app ecosystem. Requires the Apify CLI or the Apify MCP server.
author: FreshActors
author_url: https://github.com/Freshactors
---

# App Store Intelligence (Apple App Store · Google Play · Shopify App Store)

Pull structured data — app details, ratings, customer reviews, and keyword/category rankings — from the three major app marketplaces, and turn it into ASO research, review mining, and competitor monitoring. Backed by FreshActors' pure-HTTP/JSON Apify Actors (no API key, no headless browser, daily-monitored for reliability).

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. **Clarify the goal and platform.** Which marketplace — Apple App Store, Google Play, or Shopify App Store — and which task: app details, reviews, keyword/ASO search, or a competitor comparison? Collect the app identifier(s): an App Store numeric ID, a Google Play package name, or a Shopify app handle (these are NOT interchangeable — see Troubleshooting).
2. **Fetch the input schema and build a valid input.** Use `apify actors info` to confirm the exact fields, then assemble the JSON input (`mode`, IDs, country, and a cap such as `maxReviewsPerApp`). Caps control cost.
3. **Run the Actor.** Call it with the input. For large pulls (thousands of reviews, or many apps via `search`/`discover`), estimate the cost first (see [references/gotchas.md](references/gotchas.md)) and confirm with the user before running.
4. **Deliver results.** Report the row count, summarize the key fields (ratings, sentiment themes, ranking positions), and give the dataset link. For competitor work, build a small comparison table (rating, review count, price, category) across the apps.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Apple App Store — app details, keyword search, reviews | `freshactors/app-store-scraper` | community | iOS app metadata, ASO keyword rankings, and customer reviews |
| Google Play — app details, reviews, keyword search | `freshactors/google-play-scraper` | community | Android app metadata + ratings histogram, reviews, and keyword search |
| Shopify App Store — app details, reviews, catalog discovery | `freshactors/shopify-app-store-scraper` | community | Shopify app details, reviews, and keyword-based catalog discovery |

`Tier` = `apify` (Apify-maintained) or `community` (third-party). These are community Actors maintained with a daily "always-fresh" canary check.

## Calling Actors — choose your interface

### Option A: Apify CLI (recommended for portability)

Every call carries three flags: `--json` (stable machine-readable output), `--user-agent apify-awesome-skills/apify-app-store-intelligence` (telemetry attribution), and `2>/dev/null` (suppress progress lines that break JSON).

Always confirm the current input fields first:

```bash
apify actors info "freshactors/app-store-scraper" --input --json \
  --user-agent apify-awesome-skills/apify-app-store-intelligence 2>/dev/null
```

**Apple App Store** — app details, keyword search (ASO), and reviews:

```bash
# details — numeric App Store ID(s) (389801252 = Instagram)
apify actors call "freshactors/app-store-scraper" \
  -i '{"mode":"details","appIds":["389801252"],"country":"us"}' \
  --json --user-agent apify-awesome-skills/apify-app-store-intelligence 2>/dev/null

# search — keyword rankings for ASO research
apify actors call "freshactors/app-store-scraper" \
  -i '{"mode":"search","searchTerms":["habit tracker"],"country":"us","maxSearchResults":25}' \
  --json --user-agent apify-awesome-skills/apify-app-store-intelligence 2>/dev/null

# reviews — capped per app, newest first
apify actors call "freshactors/app-store-scraper" \
  -i '{"mode":"reviews","appIds":["389801252"],"maxReviewsPerApp":200,"reviewsSort":"mostRecent","country":"us"}' \
  --json --user-agent apify-awesome-skills/apify-app-store-intelligence 2>/dev/null
```

**Google Play** — details (with the 1–5★ ratings histogram), reviews, and search:

```bash
# details — Google Play package name (the id= part of the URL)
apify actors call "freshactors/google-play-scraper" \
  -i '{"mode":"details","appIds":["com.spotify.music"],"country":"us","lang":"en"}' \
  --json --user-agent apify-awesome-skills/apify-app-store-intelligence 2>/dev/null

# reviews — capped per app
apify actors call "freshactors/google-play-scraper" \
  -i '{"mode":"reviews","appIds":["com.spotify.music"],"maxReviewsPerApp":200,"reviewsSort":"newest"}' \
  --json --user-agent apify-awesome-skills/apify-app-store-intelligence 2>/dev/null
```

**Shopify App Store** — app details and catalog discovery by keyword:

```bash
# details — Shopify app handle (the slug in the apps.shopify.com URL)
apify actors call "freshactors/shopify-app-store-scraper" \
  -i '{"mode":"details","appHandles":["klaviyo-email-marketing"]}' \
  --json --user-agent apify-awesome-skills/apify-app-store-intelligence 2>/dev/null

# discover — find apps across the catalog by keyword
apify actors call "freshactors/shopify-app-store-scraper" \
  -i '{"mode":"discover","query":"email marketing","maxApps":25}' \
  --json --user-agent apify-awesome-skills/apify-app-store-intelligence 2>/dev/null
```

Fetch results from a run's dataset when needed:

```bash
apify datasets get-items DATASET_ID --format json \
  --user-agent apify-awesome-skills/apify-app-store-intelligence 2>/dev/null
```

### Option B: Apify MCP connector

Hosted MCP server at <https://mcp.apify.com> (docs: <https://docs.apify.com/platform/integrations/mcp>). Add the server, then call `freshactors/app-store-scraper`, `freshactors/google-play-scraper`, or `freshactors/shopify-app-store-scraper` by name with the same JSON input shown above.

### Option C: MCP client of your choice (e.g. `mcpc`)

Standalone CLI client. See <https://github.com/apify/mcpc>.

## Common recipes

- **Track my app + 3 competitors' ratings over time** → run `details` for all four IDs on a schedule; store `averageUserRating`/`rating`, `userRatingCount`/`ratingCount`, and `version` per run; chart the deltas.
- **ASO keyword rank check** → run `search` for each target keyword (Apple) and read the ranked result order; the position of a given app is its rank for that term and storefront.
- **Review sentiment / feature-request mining** → pull `reviews` (cap with `maxReviewsPerApp`), then classify `body` text by `rating` and `appVersion` to catch a post-release sentiment drop.
- **Cross-platform comparison** → fetch the same app on Apple (`details`) and Android (`details`) and compare rating, rating count, and price side by side.
- **Shopify ecosystem map** → `discover` a category keyword, then enrich each result's `rating`/`reviewCount`/`pricingSummary` for a market snapshot.

## Troubleshooting

- **Empty result / "0 reviews" when reviews clearly exist** → the source was rate-limited. These Actors retry through Apple's empty-`200` throttle and Google's missing-RPC-marker block, but on a heavy run, lower the cap or re-run. A genuinely empty set means that app/storefront has no reviews.
- **Wrong identifier type** → Apple uses the numeric ID from the URL (`389801252`); Google Play uses the package name (`com.spotify.music`); Shopify uses the URL handle (`klaviyo-email-marketing`). Passing the wrong kind returns nothing.
- **"App not found" / a removed app** → dead or removed apps are skipped and logged; the rest of the run continues. Verify the identifier.
- **Run costs more than expected** → cost scales with rows returned (per app for `details`/`search`, per review for `reviews`). Cap with `maxReviewsPerApp`, `maxSearchResults`, or `maxApps`, and estimate before large pulls.
- For detailed cost guardrails and recovery, see [references/gotchas.md](references/gotchas.md).
