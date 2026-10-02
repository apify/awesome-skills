# Actor index — apify-etsy-market-research

Comprehensive Actor routing table. The agent reads this after `SKILL.md` to
pick the right Actor for a specific user intent.

Input field names below were read from each Actor's published default-build
input schema on **2026-10-02**, not guessed — but schemas change, so confirm
before a large run:

    apify actors info "ACTOR_ID" --input \
      --user-agent apify-awesome-skills/apify-etsy-market-research \
      2>/dev/null

Pass `--input` **without** `--json`: on Apify CLI 1.10.0 `--input --json` prints
the whole Actor record and buries the schema.

Both Actors are public, community-tier, `PAY_PER_EVENT`, under the
`publicrecords` Store account, and **built by this skill's author**.
Disclosure: I maintain these Actors on Apify Store (publicrecords).

## Etsy — live listing rows (search / market / category)

| User intent | Actor ID | Tier | Key input fields | Cap & price | Notes |
|-------------|----------|------|------------------|-------------|-------|
| Keyword search listing rows | `publicrecords/etsy-search-scraper` | community | `queries` (array of keywords), `maxPages` (default 5, 1–20), `maxItems` (default 0 = no cap), badge filters `is_best_seller`, `is_star_seller`, `free_shipping`, `is_discounted`, `instant_download`, `ship_to`, `proxyConfiguration` (RESIDENTIAL default) | $0.005 actor-start + $0.006 per `listing-row`; blocked pages charge nothing | Lands on Etsy's `/market` page per keyword, then pages results. Start with `maxPages: 1`. **Built by this skill's author.** |
| Market-phrase listing rows | `publicrecords/etsy-search-scraper` | community | `marketPhrases` (array), same caps/filters as above | same | Phrases for Etsy's `/market/` pages (any phrase resolves). |
| Category-page listing rows | `publicrecords/etsy-search-scraper` | community | `categoryUrls` (array of `https://www.etsy.com/c/...` URLs, no query string), same caps/filters | same | Category pages, not keyword search. |

Output fields (live SUCCEEDED sample): `query`, `page`, `position`, `surface`, `listing_id`, `url`, `title`, `price`, `currency`, `rating_value`, `review_count`, `review_count_approx`, `bestseller`, `popular_now`, `star_seller`, `etsys_pick`, `free_shipping`, `is_ad`, `shop_name`, `shop_id`, `shop_url`. Do not invent fields.

## Etsy — shop sales counters and velocity

| User intent | Actor ID | Tier | Key input fields | Cap & price | Notes |
|-------------|----------|------|------------------|-------------|-------|
| Sales counters / deltas for named shops | `publicrecords/etsy-shop-velocity` | community | `shops` (array of shop names — the part after `etsy.com/shop/`), `maxShops` (default 200) | $0.005 actor-start + $0.003 per `shop-row`; optional `shop-history-record` ($0.05) and `velocity-record` ($0.10) lookup-shaped events — confirm live `pricingInfos` before promising those shapes | One row per shop from a hosted daily panel snapshot (does not scrape Etsy from the user's machine for the default shop-row path). **Built by this skill's author.** |
| Filter panel for breakouts / category / rate | `publicrecords/etsy-shop-velocity` | community | `keywords`, `category`, `minSales`, `minRate`, `since`, `breakoutOnly`, `maxShops` | same | Leave `shops` empty to use keyword/category filters. `breakoutOnly` needs ~7 days of history. |

Output fields (live SUCCEEDED sample): `shop`, `shop_url`, `as_of`, `read_interval_days`, `title`, `headline`, `category`, `sales_count`, `sales_precision`, `reviews_count`, `rating`, `admirers`, `listings_active`, `first_seen`, `last_changed`, `history_days`, `delta_last`, `sales_per_day`, `delta_7d`, `delta_28d`, `units_day`, `units_lo`, `units_hi`, `lift_7d`, `breakout`, `breakout_p`, `vintage_event`, `snapshot_date`, `snapshot_stale`, `source`. Nulls mean insufficient history — do not invent values.

## Suggested chain

1. Search: `publicrecords/etsy-search-scraper` with `maxPages: 1` → collect distinct `shop_name` values from page-1 rows.
2. Velocity: `publicrecords/etsy-shop-velocity` with those names in `shops` → report `sales_count`, `delta_7d`, `delta_28d`, `lift_7d`, `breakout` exactly as returned.

## How to extend

1. Search for candidates: `apify actors search "etsy" --json --limit 20 --user-agent apify-awesome-skills/apify-etsy-market-research 2>/dev/null`
2. Fetch input schema: `apify actors info "ACTOR_ID" --input --user-agent apify-awesome-skills/apify-etsy-market-research 2>/dev/null`
3. Add a row above with the user intent that should trigger it — and the input field names you read, not the ones you expect.
