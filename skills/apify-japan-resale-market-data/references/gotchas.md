# Gotchas — cost traps and error recovery

## Cost traps

1. **Pay-per-result.** All six Actors bill per delivered listing (PAY_PER_EVENT). A "cheap test"
   that omits `maxItems`/`maxResults` can return thousands of rows and bill accordingly.
   Always cap explicitly.
2. **Pagination compounds.** `maxPages` multiplies your result ceiling on the Mandarake and
   Suruga-ya Actors. 3 pages x 50 results = up to 150 billed rows from one call.
3. **Category crawls are open-ended.** `mode: "category"` without a keyword can walk a whole
   category. Set `maxPages` and `maxResults` together.
4. **Repeat runs for "freshness".** Re-running the same input within minutes re-bills the same
   rows. Cache the dataset ID and re-read it instead of re-running.
5. **Concurrency is not free.** Fanning out 10 concurrent runs against one marketplace raises
   both cost and block risk. Run sequentially, or space runs out.

## The charge cap is mandatory (verified 2026-10)

These are PPE (pay-per-event) Actors. A run **without a charge cap is rejected** before it
starts:

```
{"error": {"type": "max-items-must-be-greater-than-zero",
           "message": "Maximum charged results must be greater than zero"}}
```

- **REST API**: pass `?maxItems=N` as a **query parameter** on `POST .../runs`. Putting
  `maxItems` in the JSON body does NOT work — the cap is a run option, not Actor input.
  Verified working: `.../runs?maxItems=10&waitForFinish=120` → `SUCCEEDED`, 10 items.
- **Actor input**: `maxResults` (Mandarake, Suruga-ya) / `maxItems` (others) still bounds how
  many rows the Actor collects. Set both — the cap bounds billing, the input bounds collection.
- `maxTotalChargeUsd` alone is not a substitute; without `maxItems` the run still fails.

## Cheapest safe first call

```bash
apify actors call "fruitful_quintessence/mandarake-auction-scraper" \
  -i '{"mode": "category", "category": "toys", "maxPages": 1, "maxResults": 10, "language": "ja"}' \
  --json \
  --user-agent apify-awesome-skills/apify-japan-resale-market-data \
  2>/dev/null
```

One page, ten rows, keyword-free on a known-populated category — enough to prove the pipeline
works before scaling.

## Error recovery

| Symptom | Likely cause | Recovery |
|---------|--------------|----------|
| 0 items | keyword matched nothing | retry with empty keyword on a known-populated category |
| 0 items, keyword-free too | marketplace markup changed | check the Actor's last successful run date; report as a data-source issue rather than retrying blindly |
| 403 / challenge page | rate limiting | wait, then retry sequentially; do not increase concurrency |
| partial rows | listings missing a price | drop rows without a price; never default to 0 |
| mojibake in Japanese text | lossy console/transport | write items to a file and read back; the API payload is UTF-8 |
| run never finishes | open-ended pagination | kill the run, re-issue with `maxPages` + `maxResults` |

## Data-quality note

Field names are not uniform across the Actors: Mandarake uses `current_price_jpy` /
`start_price_jpy`, while Kitamura, Jackroad and Komehyo use a bare `price`. Read the field name
from the returned item; do not assume one schema across all six.
