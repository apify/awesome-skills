# Actor index — apify-app-store-intelligence

Routing table for Apple App Store data. Input field names below were read from each Actor's
published input schema, not guessed — but schemas change, so confirm before a large run:

    apify actors info "ACTOR_ID" --input --json \
      --user-agent apify-awesome-skills/apify-app-store-intelligence \
      2>/dev/null

## Metadata — one row per app

| User intent | Actor ID | Tier | Key input fields | Notes |
|-------------|----------|------|------------------|-------|
| App record; watch price/rating/version for changes | `praise-most-high/app-store-intelligence` | community | `appIds`, `bundleIds`, `searchTerms`, `country`, `changesOnly`, `watchFields` | `changesOnly: true` emits only apps whose `watchFields` moved since the previous run (default `["price","rating","version"]`). Reads Apple's public lookup API; no reviews. **Built by this skill's author.** |
| App data, charts and in-app purchases | `sourabhbgp/apple-app-store-scraper` | community | see schema | Carries chart position and IAP fields the pure-metadata Actors omit. |
| Broad app metadata / ASO fields | `logiover/app-store-data-api` | community | see schema | Smaller, newer; check output shape before depending on a field. |

## Reviews — many rows per app

| User intent | Actor ID | Tier | Key input fields | Notes |
|-------------|----------|------|------------------|-------|
| High-volume review corpus | `thewolves/appstore-reviews-scraper` | community | `appIds`, `country`, `startUrls`, `maxItems`, `customMapFunction` | The most-used Actor in this category. Set `maxItems` — review counts run to five figures per app. |
| Reviews as clean JSON, iOS + macOS | `johnvc/apple-app-store-reviews-api` | community | see schema | Wraps Apple's own public feed. |
| Reviews across every storefront, translated | `fatihtahta/app-store-global-reviews-scraper` | community | see schema | Multi-country sweeps; cost scales with country count. |
| Fast review pulls | `theagents/appstore-reviews` | community | see schema | |
| Reviews across Apple **and** Google Play | `brilliant_gum/google-play-app-store-scraper` | community | see schema | Use when the user did not say which store they meant. |

## Keyword rank / ASO — neither metadata nor reviews

| User intent | Actor ID | Tier | Notes |
|-------------|----------|------|-------|
| Track keyword rank over time | `slothtechlabs/aso-keyword-rank-tracker` | community | App Store and Google Play. |
| Keyword discovery + search popularity | `petersutarik/aso-keyword-intel` | community | |

Ranking questions ("where do I rank for X") cannot be answered from metadata or reviews. If the
user asks one, route here rather than approximating it from a category listing.

## How to extend

1. Search for candidates: `apify actors search "KEYWORDS" --json --limit 20 --user-agent apify-awesome-skills/apify-app-store-intelligence 2>/dev/null`
2. Fetch the input schema: `apify actors info "ACTOR_ID" --input --json --user-agent apify-awesome-skills/apify-app-store-intelligence 2>/dev/null`
3. Add a row with the user intent that should trigger it — and the input field names you read,
   not the ones you expect.
