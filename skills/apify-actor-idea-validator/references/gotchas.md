# Gotchas, cost guardrails and recovery

## Cost

| Call | Typical cost | Guardrail |
|---|---|---|
| `steadyfetch/keyword-search-volume-scraper` | USD 0.19 per fresh run + USD 0.004–0.012 per keyword with data | Send the whole list (≤ 15) in **one** run. Keywords with no data are free. Rerunning keywords from the last 30 days is free. Set the run's max total charge to at least USD 0.25. |
| `tri_angle/similarweb-scraper` | about USD 0.014 per domain | One run per idea. Pass every named domain in one input. |
| `advantageous_subcontra/n8n-template-scraper` | a few cents | `maxResultsPerKeyword: 20`, at most 15 keywords |
| `apify/google-search-scraper` (API check fallback) | a few cents | One page per query |
| Store, Actor stats, issues and n8n template APIs | free | Public endpoints, no token |

Tell the user before a run would clearly exceed about USD 1. For example, a 100-domain traffic check.

## Recovery

| Symptom | Cause | Fix |
|---|---|---|
| `plan_limit_reached` rows from the volume Actor | The free plan allows one fresh lookup per day | Continue on traffic data only, or rerun after 00:00 UTC (`retryAfter` on the row) |
| Questions return no volume | The volume Actor only scores short phrases | Use the 2–4 word core the row suggests |
| Every Actor shows 0 issues | Read `body.list` instead of `body.json.list` | Re-parse, and sanity-check against `compass/crawler-google-places` |
| Run stats missing for some Actors | Parallel requests throttled | Retry one at a time, or mark them "no stats" (usually ~1 MAU Actors) |
| Store count is absurd (thousands of hits) | The search term is a substring of other words, or matches README text | Keep only Actors whose name or title contains the brand, and drop false matches by hand |
| `apify actors search` stops at 10 | CLI / MCP cap | Use `curl "https://api.apify.com/v2/store?search=<kw>&limit=100"` |
| n8n results unrelated to the niche | Competitor-name keywords | Apply the relevance filter in [n8n-scout.md](n8n-scout.md) |
| Input schemas come back empty | Read from `/v2/actor-builds/` | Use `apify actors info --input` or the search field lists ([market-research.md](market-research.md)) |
| Prices like `TrustMRR.19` show up in text written by a skill | A dollar sign followed by a digit was substituted as a skill argument | Write money as `USD x` in skill files |

## Judgment calls

- **Segment the competition.** A site can have a saturated segment next to an empty one (XING jobs vs. members and companies). Bucket the segment the idea targets, and say so.
- **Demand on the job, not the brand.** For ideas like "rank top writers in a topic", the brand keywords may be near zero while use-case keywords ("expert finder", "influencer discovery") carry the volume and the CPC. Report both.
- **Run status isn't data quality.** An Actor can show 0% failures while returning empty datasets. Cross-check against "no results" issues.
- **Personal data.** Profile and member scraping in the EU needs a GDPR-defensible design. Flag it under "Risks to check before building".
