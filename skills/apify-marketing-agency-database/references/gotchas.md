# Cost guardrails and error recovery: Clutch marketing agency database

## Confirm live prices before a sweep

Prices can change. Read them from the live Actor rather than trusting a copied number:

```bash
apify actors info "johnvc/clutch-agency-api" --json \
  --user-agent apify-awesome-skills/apify-marketing-agency-database \
  2>/dev/null
```

If this metadata JSON cannot be parsed, use `apify api` to GET `/v2/actors/johnvc~clutch-agency-api`, with the same skill user-agent in the `User-Agent` header. Parse the complete pricing records; keep authentication in the CLI or an Authorization header, never in the URL.

## Cost model

- Pay per event, no start fee. A run that delivers nothing costs almost nothing.
- Include the `apify-default-dataset-item` charge for each stored row in addition to the applicable listing, profile, or review event. Read current event prices before estimating the run.
- `listing-scraped`: one per agency row delivered. Listings are priced as a loss leader, so a whole category is cheap.
- A company that repeats across pages (sponsored and featured cards) is de-duplicated and billed once.
- `maxPagesPerDirectory` caps the pages fetched; `maxItems` caps the whole run. Each page is a separate request, so page depth is the main cost lever.

Rule of thumb for confirmation: mention cost under about $5, warn over about $5, get explicit sign-off over about $20. Always phrase as "around $X".

## Guardrails

1. Start with `maxPagesPerDirectory:1` and a small `maxItems`. Confirm the category and row shape before a deep sweep.
2. Cap page depth before the run, never after. Trimming rows after the fact still pays for every page already fetched.
3. One directory page is roughly 70 to 90 companies. Size `maxItems` with that in mind.
4. To enrich, do not re-crawl. Take the `profile_url` values and run the `apify-company-data-api` workflow on just your shortlist.

## Error recovery

- `result_type: "error"` rows carry `error_message` and `error_type`.
- Zero rows and no error row: the input was not a valid Clutch directory URL (a profile URL or a non-Clutch host normalizes away). Paste a category page URL such as `https://clutch.co/agencies/digital-marketing`.
- Later pages returning nothing is the natural end of pagination, not a failure.
- A sparse row is a thin Clutch card, not a parse error. Enrich its `profile_url` for the full record.
- Before retrying, check the original run ID and status. If the start response was lost, recover the existing run first so an uncertain response does not trigger a second paid run.
