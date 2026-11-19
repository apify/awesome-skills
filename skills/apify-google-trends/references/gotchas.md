# Gotchas - apify-google-trends

## Cost guardrails

`granola2/google-trends-scraper` is `PAY_PER_EVENT`: one `result` event per dataset row, about $0.005 on the free plan ($0.003-0.004 on paid plans), plus a negligible start fee. Rows per run = keywords x reports, plus one row per trending search.

| Run | Rows | Rough cost |
|-----|------|------------|
| 10 keywords, interest over time | 10 | ~$0.05 |
| 50 keywords, interest over time | 50 | ~$0.25 |
| 10 keywords x 3 reports | 30 | ~$0.15 |
| Trending now, 3 countries | ~30 | ~$0.15 |

- Keywords Google has no data for are not charged and appear in the `SUMMARY` record, not the dataset.
- Set `maxResults` to cap a run's spend.
- Suggested thresholds: warn above $5, require explicit confirmation above $20.

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| Input error about `geo` | Not a 2-letter code or sub-region | Use `US`, `GB`, `US-NY`; empty for worldwide |
| Input error about `timeRange` | Free text like "last year" | Use a preset (`today 12-m`) or `YYYY-MM-DD YYYY-MM-DD` |
| `relatedTopics` rejected | Google returns related topics empty to automated tools | Use `relatedQueries`, or `resolveTopics: true` |
| Run ends early with partial results | `maxRunSeconds` reached | Raise `maxRunSeconds` (up to 3600) for very large lists; everything fetched is kept |
| Values look small for every keyword | One very large keyword in the set peaks at 100 | Expected on a shared scale; drop the giant or report `shareOfTotalPct` |
