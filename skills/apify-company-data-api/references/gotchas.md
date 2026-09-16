# Cost guardrails and error recovery: Clutch company data

## Confirm live prices before a batch

Prices can change. Read them from the live Actor rather than trusting a copied number:

```bash
apify actors info "johnvc/clutch-agency-api" --json \
  --user-agent apify-awesome-skills/apify-company-data-api \
  2>/dev/null
```

If this metadata JSON cannot be parsed, use `apify api` to GET `/v2/actors/johnvc~clutch-agency-api`, with the same skill user-agent in the `User-Agent` header. Parse the complete pricing records; keep authentication in the CLI or an Authorization header, never in the URL.

## Cost model

- Pay per event, no start fee. A run that delivers nothing costs almost nothing.
- Include the `apify-default-dataset-item` charge for each stored row in addition to the applicable listing, profile, or review event. Read current event prices before estimating the run.
- `profile-scraped`: one per company record delivered.
- `review-scraped`: one per verified review row, only when `includeReviews` is true.
- Markdown output is free; `html` output costs a second request per profile.
- `maxItems` caps the whole run (profiles plus reviews). Set it before a wide batch.

Rule of thumb for confirmation: mention cost under about $5, warn over about $5, get explicit sign-off over about $20. Always phrase as "around $X".

## Guardrails

1. Start with one or two profiles and `includeReviews:false`. Inspect the shape before paying for a wide batch.
2. Reviews multiply rows fast. A company with 175 reviews and no cap is 175 review rows plus one profile row. Set `maxReviewsPerProfile`.
3. Normalize profile URLs to slugs and de-duplicate the input before starting; repeated profiles can produce repeated charges.
4. Keep `html` off unless you truly need the raw page. It doubles the per-profile request cost for data you usually already have as fields.

## Error recovery

- `result_type: "error"` rows carry `error_message` and `error_type`. A bad slug or a removed profile lands here rather than aborting the run.
- Zero rows: check for error rows first. If there are none and you asked for profiles, your `profileUrls` list was empty after normalization (for example a non-Clutch URL).
- A short profile is not an error. Many Clutch pages are genuinely thin.
- Before retrying, check the original run ID and status. If the start response was lost, recover the existing run first so an uncertain response does not trigger a second paid run. Keep persistent failures in the report rather than assuming the profile no longer exists.
