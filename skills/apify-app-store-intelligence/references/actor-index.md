# Actor index — apify-app-store-intelligence

Routing table for Apple App Store and Google Play data. Input field names below were read from
each Actor's published input schema, not guessed — but schemas change, so confirm before a large
run:

    apify actors info "ACTOR_ID" --input \
      --user-agent apify-awesome-skills/apify-app-store-intelligence \
      2>/dev/null

Pass `--input` **without** `--json`: on Apify CLI 1.10.0 `--input --json` prints the whole Actor
record (pricing, stats, build) and the schema is buried inside it.

Every Actor listed here was checked on **2026-09-18** against the public Actor API
(`GET https://api.apify.com/v2/acts/<owner>~<name>`): all are public, not deprecated, run with
`LIMITED_PERMISSIONS`, and are priced `PAY_PER_EVENT` — none is a rental (`FLAT_PRICE_PER_MONTH`)
Actor. Prices below are the FREE-tier per-event prices from that same read. Re-read them before a
large run.

## Apple App Store — metadata, one row per app

| User intent | Actor ID | Tier | Key input fields | Cap & price | Notes |
|-------------|----------|------|------------------|-------------|-------|
| App record; watch price/rating/version for changes | `praise-most-high/app-store-intelligence` | community | `appIds`, `bundleIds`, `searchTerms`, `country`, `changesOnly`, `watchFields`, `includeRatings`, `limit`, `maxConcurrency` | `limit` default 20, max 200 — **per search term only; ignored for `appIds`/`bundleIds`** (one record per ID, so the ID list is the cap); $0.0011 per app record + $0.004 per detected change + $0.00001 per run | `changesOnly: true` emits only apps whose `watchFields` moved since the previous run (default `["price","rating","version"]`). `includeRatings` (default `true`) populates `rating` and `ratingsCount` — leave it on, or `watchFields: rating` has nothing to compare; `rating` is stored and compared at 5 decimals (see `gotchas.md`). Reads Apple's public lookup API; no reviews. See the change-detection section of [`gotchas.md`](gotchas.md) before scheduling it. **Built by this skill's author.** |
| App record from an unaffiliated Actor | `freshactors/app-store-scraper` | community | `mode` (`details`/`reviews`/`search`, required), `appIds`, `country`, `maxSearchResults`, `maxReviewsPerApp` | `maxSearchResults` default 50, max 200; `maxReviewsPerApp` default 200, max 500 (`reviews` mode); $0.002 per app detail, $0.001 per search result, $0.0001 per review | Returns `price`, `formattedPrice`, `version`, `averageUserRating`, `userRatingCount`, `currentVersionReleaseDate`. Use as the second opinion on metadata. |
| 1–5★ ratings histogram, charts, in-app purchases | `sourabhbgp/apple-app-store-scraper` | community | `mode` (required, **no default** — the Console prefills `search`), `countries` (default `["us"]`), `appDetailsConfig` (free-form JSON: `appIds`, optional `includePrivacyLabels`, `includeVersionHistory`, `includeFileSizeByDevice`, `includeSellerInfo`) | $0.002 per result. `mode: "app-details"` has no cap field: cost = apps × `countries` (default `["us"]`). The caps for the other modes live inside `searchConfig` / `reviewsConfig` / `chartsConfig` as free-form JSON, so a cap typo is not rejected by the schema; `reviewsConfig.maxReviewsPerApp` defaults to **500** at $0.002 per review — 20× `thewolves`, do not use this Actor for review corpora | `mode: "app-details"` returns `ratingsHistogram` by default (no flag needed); its star counts sum to `userRatingCount`. This is the measured way to get an Apple star breakdown — do not tell the user Apple histograms are unavailable. Separate `charts` and `iap-catalogue` modes exist. `appDetailsConfig.includeVersionHistory: true` costs nothing extra (measured 2026-09-19: $0.004 with and without) and returns the last 25 releases with dates. |
| Broad app metadata / ASO fields | `logiover/app-store-data-api` | community | see schema | $0.001 per dataset item + $0.00005 per run | Smaller, newer; check output shape before depending on a field. |

## Apple App Store — reviews, many rows per app

| User intent | Actor ID | Tier | Key input fields | Cap & price | Notes |
|-------------|----------|------|------------------|-------------|-------|
| High-volume review corpus | `thewolves/appstore-reviews-scraper` | community | `appIds`, `country`, `startUrls`, `maxItems`, `customMapFunction` | `maxItems` has **no schema default** (the Console prefills 1000); $0.0001 per review | The most-used Actor in this category; rows carry a `date`. Always set `maxItems` explicitly — review counts run to five figures per app. `customMapFunction` is a JavaScript hook for reshaping rows — leave it unset; its own schema warns that using it to filter gets the account banned. |
| Reviews as clean JSON, iOS + macOS | `johnvc/apple-app-store-reviews-api` | community | see schema | $0.001736 per review + $0.0175 setup + $0.00005 per run + $0.00001 per dataset item | Wraps Apple's own public feed. ~17× the per-review price of `thewolves` — use only if you need its exact output shape. |
| Reviews across every storefront, translated | `fatihtahta/app-store-global-reviews-scraper` | community | `startUrls` (what to scrape), `limit` (**default 50 000, per app**), `countries` (**default `["__all__"]`**, 160 storefronts), `translation` (default `false`) | $0.0004 per output record + $0.003 per translated word; minimum charge $0.10 per run | **Both defaults are fail-open.** `limit` is per app, not per storefront: left alone that is 50 000 × $0.0004 = $20 per app, and `countries: ["__all__"]` widens where those records come from rather than multiplying the bill. Set `limit` and name the countries. Translation is charged per word on top. |
| Fast review pulls | `theagents/appstore-reviews` | community | `maxItems` (**no default**), `country` (enum includes `all`) | $0.0001 per dataset item | `country: "all"` sweeps every storefront; with no `maxItems` that is ≈ $8.75 per app. Set both. |

## Google Play — metadata, one row per app

| User intent | Actor ID | Tier | Key input fields | Cap & price | Notes |
|-------------|----------|------|------------------|-------------|-------|
| App record incl. 1–5★ histogram | `freshactors/google-play-scraper` | community | `mode` (`details`/`reviews`/`search`, default `details`), `appIds` (package names), `country`, `lang`, `maxSearchResults`, `maxReviewsPerApp` | `maxSearchResults` default 30, max 100; `maxReviewsPerApp` default 200, max 4000 (`reviews` mode); $0.002 per app detail, $0.0001 per review | `details` returns `rating`, `ratingCount`, `installs`, `ratingHistogram`. **No `version` field.** The schema has no search event: `mode: "search"` results are charged as app details, $0.002 each. |
| App record incl. `version` and IAP range | `brilliant_gum/google-play-app-store-scraper` | community | `platform` (default `googlePlay`), `mode` (default `search`), `maxAppsPerQuery` (default 50), `maxAppsPerChart` (default 100), `fetchFullDetails` (default true) | $0.01 per app detail, $0.004 per search result, $0.001 per run; charges compute on top (`PPE user pays compute`) | Use only for the fields `freshactors` omits. `version` is a real string for some apps (`8.32.1`) and the literal `"VARY"` for apps Play lists as "Varies with device" (measured 2026-09-18) — report it as "varies with device", do not infer a number. `mode` defaults to `search`, so an unset `mode` plus a query can fan out to 50 paid details. |

## Google Play — reviews, many rows per app

| User intent | Actor ID | Tier | Key input fields | Cap & price | Notes |
|-------------|----------|------|------------------|-------------|-------|
| Cheapest chronological corpus | `thewolves/google-play-reviews-scraper` | community | `appIds`, `sort` (`NEWEST`/`RATING`/`HELPFULNESS`, default `NEWEST`), `maxItems` (**no default**) | $0.0001 per review | Rows carry a `date`. Set `maxItems`. |
| Reviews inside a hard date window | `neatrat/google-play-store-reviews-scraper` | community | `appIdOrUrl` (required, one app per run), `sortBy` (default `mostRelevant`; `newest` exists), `recentDays` (default 0 = off), `appVersion`, `maxReviews` (default 10 000, `-1` = unlimited), `pagesToScrape` (default 5, **`-1` = every page, fail-open**), `reviewsPerPage` (default 100), `uniqueOnly` (default `true`) | $0.00015 per review. Free Apify accounts get 5 runs and 500 reviews **in total** on this Actor, and a zero-result run still counts | `recentDays: N` filters to the last N days server-side. `pagesToScrape` × `reviewsPerPage` most likely forms a second ceiling of ~500 rows at the defaults — not confirmed by a run — so when you raise `maxReviews` above 500, raise `pagesToScrape` too, and never set it to `-1` without `maxReviews`. `sortBy: "newest"` and `appVersion` are real fields even though the Actor's README does not document them. |
| Reviews across Apple **and** Google Play | `brilliant_gum/google-play-app-store-scraper` | community | `maxReviewsPerApp` (default 100, max 3000) | **$0.006 per review** | 60× the per-review price of `thewolves`. Use it for the metadata fields above, not for a review corpus. |

## Keyword rank / ASO — neither metadata nor reviews

| User intent | Actor ID | Tier | Price | Notes |
|-------------|----------|------|-------|-------|
| Track keyword rank over time | `slothtechlabs/aso-keyword-rank-tracker` | community | $0.001 per dataset item | App Store and Google Play. |
| Keyword discovery + search popularity | `petersutarik/aso-keyword-intel` | community | $0.02 per metrics row, $0.002 per ranking row, $0.001 per suggestion row; charges compute on top | `keywords` is required. `includePopularity` defaults to `true`, which turns the $0.02 metrics row on for every keyword (up to 100 per run = $2 before compute) — set it to `false` unless you need popularity for a shortlist. A metrics row is 20× a ranking row — pull metrics for a shortlist, not a keyword dump. |

Ranking questions ("where do I rank for X") cannot be answered from metadata or reviews. If the
user asks one, route here rather than approximating it from a category listing — this skill's
workflow does not run these Actors for them.

## How to extend

1. Search for candidates: `apify actors search "KEYWORDS" --json --limit 20 --user-agent apify-awesome-skills/apify-app-store-intelligence 2>/dev/null`
2. Fetch the input schema: `apify actors info "ACTOR_ID" --input --user-agent apify-awesome-skills/apify-app-store-intelligence 2>/dev/null`
3. Add a row with the user intent that should trigger it — and the input field names you read,
   not the ones you expect. Record the cap field and its default: several Actors here default to
   unlimited.
