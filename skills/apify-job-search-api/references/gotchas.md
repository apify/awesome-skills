# Gotchas: job search API feed (johnvc/Google-Jobs-Scraper)

Cost guardrails, error recovery, and feed-specific quirks. The agent reads this on demand when building inputs or when a poll fails.

## Cost guardrails

Pricing model: pay per event, dominated by a per-page fee. At the time of writing: about $0.15 per page of results processed on the free tier (volume discounts bring it to about $0.10), plus negligible per-run start and per-result fees. Confirm the live price on the Store card or with `apify actors info "johnvc/Google-Jobs-Scraper" --json --user-agent apify-awesome-skills/apify-job-search-api 2>/dev/null` (look at `pricingInfo`).

Feed math: one page is roughly 10 listings. Always set `max_pagination` on a recurring feed; it is the hard per-poll cost cap.

- One poll at `max_pagination` 3: about $0.45.
- Daily polls at 3 pages: about 90 pages, about $13.50 per month per feed.
- Hourly polls at 2 pages: about 1,440 pages, about $216 per month; confirm explicitly before scheduling anything hourly.

Suggested confirmation thresholds:

- Estimated monthly cost over $5: state the monthly number before scheduling.
- Estimated monthly cost over $20: get explicit confirmation.
- Always present cost as "around $X", not a guarantee.

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| Duplicates across polls | Same listings still live | Expected; dedupe on `job_id` against your store. |
| Nothing new in a poll | Narrow query, slow market | Normal; widen the query or lengthen the poll interval. |
| Empty dataset | No inventory for query plus location | Broaden the query; drop or widen the location. |
| Budget warning at startup | Run budget below estimated page cost | Raise the run budget, or lower `num_results` / `max_pagination`. |

## Feed-specific notes

- `posted_at` is a relative age string ("3 days ago", "just posted"). Convert to a timestamp at ingest time (poll time minus the stated age) and filter client-side; there is no server-side date parameter.
- Freshness equals your poll interval; this is a polled feed, not a webhook.
- `apply_options` gives one direct link per hosting platform; prefer the company-site link when present.
- For recurring feeds, create one Apify Schedule per feed input rather than one big multi-query run; per-feed datasets keep dedupe simple.
- No numeric salary field and no experience-level field in the output.
