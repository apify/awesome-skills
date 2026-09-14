# Cost guardrails and error recovery

## Live prices, not remembered ones

```bash
apify actors info "johnvc/zillow-api" --json \
  --user-agent apify-awesome-skills/apify-zillow-api \
  2>/dev/null
```

Read `pricingInfos` from the output. Billing is one `listing_returned` event per delivered listing row.

## Guardrails

- Cap every exploratory run: `maxResults: 10` until the row shape is confirmed.
- Filters run before billing. Push `priceMin`, `priceMax`, `bedsMin`, `homeType`, and the rest into the input rather than filtering downstream.
- A search bills a 10-listing minimum for the page it fetches, so a search that returns fewer than 10 still bills 10. Do not fan out one location into many tiny narrow searches when one broader search would do.
- `autoShard` is off by default. Turn it on only to exceed 820 results for one location, and always set `maxUpstreamCalls`, because each shard is its own billable page.
- `includeImages` adds many image-URL values per row. Keep it off unless the images are the point.

## Error recovery

- `regionAmbiguous` on an error row: the location matched several regions. Set `ambiguityPolicy: "all"`, or qualify the name (add the state, or use a `city:` or `zip:` prefix).
- Wrong-city results: qualify the location. A bare ZIP is always resolved to its region, never passed through, so a mismatch points at an ambiguous plain name.
- `truncated: true` on a row: the tile held more listings than one search returns; a completeness note, not a failure.
- Zero rows, no error: filters removed everything, or the location has thin inventory for that `statusType`. Relax filters or widen the location.
- Errors are in-band dataset rows with `resultType: "error"`; pipelines should branch on `resultType`, not on run status.

## Freshness and honesty facts worth knowing

- Sold rows carry no sale price. Only `soldDate`, `zestimate`, and `taxAssessedValue` are present for sold listings.
- `zestimate` and `rentZestimate` are Zillow's own estimates, not appraisals or recommended rents.
- Photo fields are URLs only, never downloaded or re-hosted.
- `daysOnZillow` resets on a relist, so it can understate true time on market.
