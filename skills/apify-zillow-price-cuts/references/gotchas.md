# Cost guardrails and error recovery

## Live prices, not remembered ones

```bash
apify actors info "johnvc/zillow-api" --json \
  --user-agent apify-awesome-skills/apify-zillow-price-cuts \
  2>/dev/null
```

Read `pricingInfos` from the output. Billing is one `listing_returned` event per delivered listing row.

## Guardrails

- Always set `priceReduction: true`. Without it you pay for every for-sale listing, most of which were never reduced.
- Cap every exploratory run: `maxResults: 50` until you confirm `priceChange` is populated.
- Filters run before billing. Push `priceMax`, `bedsMin`, and `homeType` into the input rather than filtering downstream.
- A search bills a 10-listing minimum for the page it fetches, so a metro with only a few reduced homes still bills 10 for that page.
- `autoShard` is off by default. Turn it on only to exceed 820 results for one location, and always set `maxUpstreamCalls`, because each shard is its own billable page.

## Error recovery

- `priceChange` null on returned rows: `priceReduction: true` was not set.
- Zero rows, no error: the market has few reduced listings, or filters removed them. Widen `priceMax` or the location.
- `regionAmbiguous` on an error row: qualify the location or set `ambiguityPolicy: "all"`.
- Errors are in-band dataset rows with `resultType: "error"`; branch on `resultType`, not on run status.

## Freshness and honesty facts worth knowing

- The output is a snapshot per run. For a newly-reduced feed, schedule the run and diff outputs downstream; no field marks a row as new since your last run.
- `priceChange` and `priceChangeDate` describe the most recent reduction only. There is no per-listing price-history endpoint upstream.
- `daysOnZillow` resets on a relist, so it understates true time on market, worst on the stalest inventory, which is exactly what this skill surfaces.
- `zestimate` is Zillow's own estimate, not an appraisal or a recommended price.
