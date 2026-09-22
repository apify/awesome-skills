# Gotchas

Cost, safety, and recovery notes specific to this pipeline. Read once per new deployment; keep the ones you hit as institutional memory.

## Cost

- **`maximumLeadsEnrichmentRecords` is a multiplier.** `50 places × 5 leads = 250 lead attempts`, priced per successful lead. Anything over `200` expected leads should be restated to the user before running.
- **Social enrichment is per-profile flat-rate.** Enabling YouTube/TikTok/X on top of IG+FB doesn't change the per-profile price — but if the place links to all five, you'll pay for all five. Add them only when the user asks.
- **Reviews are cheap but not free.** `maxReviews: 10` is the sweet spot for scoring — enough signal, low cost. `maxReviews: 100+` only pays off if the user asked for review-content analysis.
- **Scalelist is pay-per-event.** No match = no charge. Safe to over-batch.
- **`apify/ai-web-scraper` is the priciest per-place step.** It runs an agentic crawl + LLM extraction per business website. On a 50-place run where 40% of places need name discovery, that's 20 additional Actor calls at 5–20 pages each. Keep `maxPagesToVisit ≤ 20` unless you have evidence a vertical needs deeper crawls. Offer users the option to skip name discovery entirely for large batches.

## Data quality

- **Places without websites can't be lead-enriched.** The Actor skips them. If a place is on Maps as "Marco's Bakery" with a phone but no site, `leadsEnrichment[]` will be empty and you get a `no-leads-found` row.
- **Big chains are excluded server-side** for both `scrapeContacts` and leads enrichment: McDonald's, Starbucks, Domino's, Pizza Hut, Burger King, KFC, Subway, Wendy's, Dunkin', Taco Bell. Not a bug.
- **Spurious matches are real.** Always run the hostname-equality check. Don't trust the enrichment blindly for places without a strong web footprint.
- **Backfill match rates vary by geography.** Scalelist coverage is strongest in the US/UK/EU; expect lower hit rates for e.g. Southeast Asia SMBs.

## Legal / policy

- **Personal data in `leadsEnrichment[]`** — names, work emails, phone numbers. GDPR and equivalents apply. The Actor emits a GDPR notice in its own docs; carry it forward when handing the CSV to a user with an EU audience.
- **Don't scrape reviewers' personal data** — leave `scrapeReviewsPersonalData: false` (the default). The review text is fine; the reviewer identity is not.

## Recovery

- **Run FAILED mid-way** — the dataset already has partial results. Pull it (`apify datasets get-items <id>`) and run Steps 4–6 on what's there. Note the shortfall in `run_metadata.json`.
- **Actor not authorized** — scalelist Actors sometimes need one manual acceptance in the Apify Console before the API accepts a run. Open the Actor page once in a browser; retry.
- **Rate-limited on scalelist** — batch size ≤ 100 usually avoids this. If you still hit it, sleep 30 s between batches.
