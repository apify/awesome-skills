# Gotchas — apify-etsy-market-research

Cost guardrails, error recovery, and common pitfalls. The agent reads this
on demand when building inputs or when a run fails.

Both routed Actors are built by this skill's author.
Disclosure: I maintain these Actors on Apify Store (publicrecords).

## Cost guardrails

Apify Actors use one of three pricing models. Before running, check the
model via:

    apify actors info "ACTOR_ID" --json \
      --user-agent apify-awesome-skills/apify-etsy-market-research \
      2>/dev/null

(look at `pricingInfo` / `pricingInfos`).

| Model | What to watch for |
|-------|-------------------|
| `FREE` | No cost — safe to run. |
| `PAY_PER_EVENT` | Cost scales with results. Estimate before running. Both Actors here use this. |
| `FLAT_PRICE_PER_MONTH` | Subscription — runs are unlimited once paid. |

### Live prices (FREE tier, read 2026-10-02 — re-read before a large run)

| Actor | Events |
|-------|--------|
| `publicrecords/etsy-search-scraper` | `actor-start` $0.005 once; `listing-row` $0.006 per delivered listing row. Blocked pages charge nothing for rows. |
| `publicrecords/etsy-shop-velocity` | `actor-start` $0.005 once; `shop-row` $0.003 per shop row; `shop-history-record` $0.05; `velocity-record` $0.10. Default shop-list lookups are `shop-row` shaped — do not assume the higher events fire unless the run log / receipt shows them. |

Residential proxy usage on the search Actor is billed separately by Apify Proxy when `proxyConfiguration.useApifyProxy` is true (the schema default).

### Confirmation thresholds (suggested)

- Estimated cost **>$5** → warn the user.
- Estimated cost **>$20** → require explicit user confirmation before running.
- Always present cost as a **rough estimate** ("around $X"), not a guarantee.
- Prefer `maxPages: 1` and an explicit `shops` list for first runs.

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| Empty search dataset | Filters too tight, or pages blocked | Relax badge filters; lower ambition on `maxPages`; read the run log for blocked-page notes. |
| Empty velocity dataset | `breakoutOnly` / filters with too little history, or unknown shop names | Drop `breakoutOnly`, widen `minSales`/`category`, or pass exact shop names from `etsy.com/shop/<name>`. |
| Invented fields in the summary | Agent hallucinated sales volume on listing rows | Only use the field tables in `SKILL.md`; pair search with velocity for shop counters. |
| Large unexpected bill | Open `maxPages` (default 5) or `maxShops` (default 200) without a cap conversation | Confirm page/shop bounds with the user; set `maxItems` on search when needed. |
| Wrong country results | `ship_to` unset / wrong | Pass a two-letter `ship_to` (e.g. `"US"`) when shipping destination matters. |

## Actor-specific notes

### `publicrecords/etsy-search-scraper`

- Etsy caps a query at 20 pages; `maxPages` accepts 1–20.
- Default `proxyConfiguration` uses Apify Proxy RESIDENTIAL — datacenter IPs are commonly blocked.
- `review_count_approx: true` means Etsy rounded the displayed review count; do not treat it as exact.
- `is_ad` may be `null` when sponsorship is unknown — do not coerce to false.
- Results reflect what Etsy shows a logged-out visitor from the run's proxy region.
- Do not claim listing-level sales volume from search rows alone.

### `publicrecords/etsy-shop-velocity`

- Default path reads a hosted daily panel snapshot; it is not a live scrape of each shop page from the user's machine for ordinary `shop-row` results.
- `snapshot_stale: true` means the panel date may lag — report `as_of` / `snapshot_date` with the numbers.
- Null `delta_*`, `sales_per_day`, `lift_7d`, etc. mean insufficient history — say so; do not invent rates.
- `breakoutOnly: true` needs about 7 days of history; an empty result until then is expected and explained in the run log.
- `sales_precision` (e.g. `"exact"`) describes the counter quality — preserve it when summarizing.
