# Gotchas: scrape Google Jobs (johnvc/Google-Jobs-Scraper)

Cost guardrails, error recovery, and input quirks. The agent reads this on demand when building inputs or when a run fails.

## Cost guardrails

Pricing model: pay per event, dominated by a per-page fee. At the time of writing: about $0.15 per page of results processed on the free tier (volume discounts bring it to about $0.10), plus negligible per-run start and per-result fees. Confirm the live price on the Store card or with `apify actors info "johnvc/Google-Jobs-Scraper" --json --user-agent apify-awesome-skills/apify-scrape-google-jobs 2>/dev/null` (look at `pricingInfo`).

Estimate before running: one page is roughly 10 listings, so cost is about (`num_results` / 10) times the per-page price.

- 50 results: about 5 pages, about $0.75.
- 100 results: about 10 pages, about $1.50.
- 1,000 results: about 100 pages, about $15.

Suggested confirmation thresholds:

- Rough estimate over $5: warn the user.
- Rough estimate over $20: get explicit confirmation before running.
- Always present cost as "around $X", not a guarantee.

`max_pagination` is the hard cost cap: it bounds pages fetched no matter what `num_results` asks for.

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| Empty dataset | Query too narrow, or no Google Jobs inventory for that location | Broaden the query; drop or widen the location. |
| Fewer rows than `num_results` | Google had fewer listings for the query | Expected; `num_results` is a cap, not a guarantee. |
| Budget warning at startup | Run budget below the estimated page cost | Raise the run budget, or lower `num_results` / set `max_pagination`. |
| Non-US city returns nothing on the first pass | Google location targeting missed | The Actor retries automatically with the location merged into the query. |

## Actor-specific notes

- `query` is the only required input.
- About 10 listings per page; `pages_processed` in the run metadata is the billing driver.
- `posted_at` is a relative string ("3 days ago"); filter freshness client-side.
- No numeric salary field and no experience-level field in the output.
- Dedupe across runs on `job_id`.
- `apply_options` carries one direct link per hosting platform (company site, LinkedIn, Indeed, and so on); it is the most valuable field for recruiting pipelines.
