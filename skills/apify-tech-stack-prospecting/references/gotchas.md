# Gotchas — apify-tech-stack-prospecting

Cost guardrails, error recovery, and Actor-specific pitfalls for the three-stage pipeline.

## Cost guardrails

All three Actors use `PAY_PER_EVENT` pricing. Confirm before running any stage that involves more than ~50 inputs.

| Stage | Actor | Unit billed | Typical run | Warn threshold |
|-------|-------|-------------|-------------|----------------|
| Discovery | `apify/google-search-scraper` | per result page | 5 queries × 50 results = ~3 pages each ≈ 15 page-loads | >50 queries |
| Contact | `vdrmota/contact-info-scraper` | per page crawled | 100 domains × 20 pages/domain = 2 000 pages | >100 domains |
| Enrichment | `apify/linkedin-companies-scraper` | per company scraped | 1 unit per company URL | >100 companies |

Check live rates before quoting: `apify actors info "ACTOR_ID" --json 2>/dev/null` → `pricingInfo` field.

### Confirmation thresholds

- Estimated cost **>$5** → warn the user and show the estimate.
- Estimated cost **>$20** → require explicit confirmation before running.
- Present all estimates as rough ("around $X"), never as guarantees.
- Enrichment on >100 companies scales linearly and can become expensive quickly — always call this out explicitly.

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| `APIFY_TOKEN not found` | Missing env var or `.env` file | Run `apify login` or set `APIFY_TOKEN=<token>` in the environment |
| Google Search scraper returns 0 results | Queries too narrow (`site:` restrictions + long phrases) | Remove `site:` filters; broaden the query; try alternate signal types from the query table |
| Contact scraper returns 0 emails for a domain | Company uses contact forms, Cloudflare, or auth-gated pages | Use the `linkedin_url` from the same run for manual or MCP-based outreach |
| LinkedIn scraper rate-limited or returns 429 | Too many company URLs in one batch; LinkedIn session throttle | Reduce batch to 20–30 companies; wait 10–15 min between batches |
| `Actor not found` error | Actor ID typo or the community actor was removed | IDs are case-sensitive; verify with `apify actors search` before retrying |
| Dataset missing after run | Run did not reach `SUCCEEDED` status | Check run status: `apify runs info RUN_ID --json 2>/dev/null`; inspect logs in console |

## Actor-specific notes

### `apify/google-search-scraper`

- Keep `resultsPerPage` ≤ 50 for the discovery stage; 100 is allowed but rarely improves domain quality for this use case.
- Set `maxPagesPerQuery: 1` on the first pass; bump to 2 only if the first page yielded fewer than 10 unique root domains.
- Deduplicate results by root domain immediately — the same company often appears on multiple SERP positions.
- Discard known noise domains: job boards (`linkedin.com`, `indeed.com`, `glassdoor.com`), news aggregators, Wikipedia, and developer docs sites.

### `vdrmota/contact-info-scraper`

- **Always cap `maxDepth: 2` and `maxPagesPerCrawl: 20`** — without these limits a single domain can crawl thousands of pages.
- Pages behind login walls, Cloudflare JS challenges, or requiring cookies are silently skipped; expect partial results on enterprise sites.
- The scraper extracts emails from `mailto:` links and plain-text patterns. Obfuscated emails (e.g. `name [at] company [dot] com`) are not extracted.
- Social profiles (`linkedin_url`) are extracted from `<a href="https://linkedin.com/company/...">` links; these are the input for the enrichment stage.

### `apify/linkedin-companies-scraper`

- Input must be **company page URLs** (`linkedin.com/company/...`), not person profile URLs (`linkedin.com/in/...`). Passing profile URLs silently returns no data.
- LinkedIn blocks scrapers aggressively. If >5 consecutive companies return empty results, stop and retry after 15–30 minutes.
- `employee_count` is a LinkedIn-reported estimate and often rounded (e.g., "51–200"). Treat as a firmographic signal, not an exact headcount.
- The scraper does not return individual contact names or emails — it provides company-level firmographics only.
