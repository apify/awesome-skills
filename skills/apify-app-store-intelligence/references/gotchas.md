# Gotchas & cost guardrails

Detailed notes for the `apify-app-store-intelligence` skill. Read this before large pulls.

## Cost model

All three Actors are **pay-per-event** — you pay only for rows actually returned, and there is **no per-run start fee**. Cost scales with the unit each mode emits:

| Mode | Charged per | Cost driver |
|------|-------------|-------------|
| `details` | app whose details are returned | number of apps |
| `search` (Apple) / `discover` (Shopify) | app returned from the query | result cap |
| `reviews` | individual review returned | reviews cap × apps |

Exact per-event prices are shown on each Actor's store page (they can change, so read them live rather than hardcoding):

- Apple App Store — <https://apify.com/freshactors/app-store-scraper>
- Google Play — <https://apify.com/freshactors/google-play-scraper>
- Shopify App Store — <https://apify.com/freshactors/shopify-app-store-scraper>

Reviews are by far the cheapest unit and the highest-volume one, so a large review pull is usually inexpensive — but it is still **cap × number of apps**, which multiplies fast across many apps.

## Estimate before you run

1. Multiply the relevant cap by the number of apps:
   - `details`: `len(appIds)` apps.
   - `search`/`discover`: `maxSearchResults`/`maxApps` per term/query.
   - `reviews`: `maxReviewsPerApp` × `len(appIds)`.
2. If the estimated row count is large (e.g. tens of thousands of reviews), tell the user the rough magnitude and confirm before running.
3. Apify platform compute is billed separately by Apify at its standard rates, as with any Actor.

## Keeping runs cheap and clean

- Start with a **small cap** (e.g. `maxReviewsPerApp: 100`) to validate the shape, then scale up.
- For competitor monitoring, prefer `details` (one row per app) over pulling full review sets unless you actually need review text.
- Schedule recurring pulls (Apify Schedules) rather than re-scraping everything each time.

## Reliability notes

- Empty-but-`200` throttle responses (Apple's legacy review feed) and missing-RPC-marker blocks (Google Play) are detected and retried with backoff — a returned empty set means genuinely no data, not a silent failure.
- Every record carries a `_schemaVersion` and `_scrapedAt`; if an upstream field is reshaped, the affected field degrades to `null` rather than crashing the run.
- The Actors are verified by a daily canary; check the "Last verified working" date on each store page.

## Identifier cheat-sheet

| Marketplace | Identifier field | Example | Where to find it |
|-------------|------------------|---------|------------------|
| Apple App Store | `appIds` (numeric) or `bundleIds` | `389801252` | the `id…` number in the App Store URL |
| Google Play | `appIds` (package name) | `com.spotify.music` | the `id=` part of the Play URL |
| Shopify App Store | `appHandles` (slug) or `appUrls` | `klaviyo-email-marketing` | the slug at the end of the `apps.shopify.com` URL |
