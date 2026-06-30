# Gotchas — apify-linkedin-intelligence

Cost guardrails, error recovery, and LinkedIn-specific pitfalls. The agent reads
this on demand when building inputs or when a run fails.

## Cost guardrails

LinkedIn Actors are almost always `PAY_PER_EVENT` — you pay per profile,
company, or job returned. Cost = (rows requested) × (per-result price). Check the
model first:

    apify actors info "ACTOR_ID" --json 2>/dev/null   # look at pricingInfo

| Model | What to watch for |
|-------|-------------------|
| `FREE` | No cost — safe to run. |
| `PAY_PER_EVENT` | **The common case here.** Cost scales linearly with `maxItems`/`count`. Estimate before running. |
| `FLAT_PRICE_PER_MONTH` | Subscription — runs unlimited once paid. |

### Confirmation thresholds (suggested)

- Estimated cost **>$5** → warn the user.
- Estimated cost **>$20** → require explicit confirmation before running.
- Always present cost as a **rough estimate** ("around $X"), not a guarantee.

### Sample-then-scale (do this on every large list)

1. Run with `maxItems`/`count` set to ~10 to confirm the schema and output shape.
2. Inspect the columns and that rows are non-empty.
3. Only then raise the cap to the full list. This avoids paying for a 5,000-row
   run that returns 0 usable rows because of a wrong field name.

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| Run finishes, 0 dataset rows | Wrong slug/name/URL, or `dev_fusion/Linkedin-Company-Scraper` wrote to the **KV store** | Re-resolve the slug via SERP; read the KV store keys, not the dataset. |
| `count` rejected / too low | `curious_coder/linkedin-jobs-scraper` `count` minimum is 10 | Set `count: 10` or higher. |
| Jobs Actor returns unrelated jobs | Passed keywords instead of a jobs search URL, or unencoded spaces | Use a full `linkedin.com/jobs/search/?...` URL; URL-encode (`Bright Data` → `Bright%20Data`). |
| Wrong input field name | LinkedIn Actor inputs vary (`profileUrls` vs `companyUrls` vs `identifier`) | Always `apify actors info "ACTOR_ID" --input --json` before building input. |
| Headcount disagrees with reality | LinkedIn counts are modeled estimates | Label as directional; cross-check vs company site or jobs Actor `companyEmployeesCount`. |

## Identifier resolution (the #1 silent failure)

Company **names are not slugs**: `Oxylabs` → `oxylabs-io`, `Bright Data` →
`bright-data-ltd`. A wrong slug returns 0 rows with no error. Resolve first:

    apify actors call "apify/google-search-scraper" \
      -i '{"queries":"<company> site:linkedin.com/company","maxPagesPerQuery":1,"resultsPerPage":5}' \
      --json --user-agent apify-awesome-skills/apify-linkedin-intelligence 2>/dev/null

Take the first `organicResults[].url` matching `linkedin.com/company/<slug>`.
For people, query `"<title> <company> site:linkedin.com/in"`.

## Actor-specific notes

### `dev_fusion/Linkedin-Company-Scraper`

- Input field is `profileUrls`, **not** `urls`.
- Output lands in the **key-value store**, not the dataset — read KV store keys.

### `curious_coder/linkedin-jobs-scraper`

- Input `urls` must be LinkedIn jobs **search URLs**, not keyword strings.
- `count` minimum is 10. `scrapeCompany: true` enriches each job with firmographics.

### `harvestapi/linkedin-profile-search`

- The discovery/prospecting engine — use it when you do NOT yet have profile URLs.
- Confirm the exact filter field names and the `maxItems` cap in the schema before
  scaling; cap it to control `PAY_PER_EVENT` cost.

## Compliance / data-handling note

LinkedIn profile data about identifiable people is personal data. Use it for
legitimate B2B outreach, respect rate limits, and honor opt-outs / data-subject
requests. Surface this to the user when building large people lists.

For a polished gotchas example with detailed cost tables, see [apify/agent-skills ultimate-scraper gotchas](https://github.com/apify/agent-skills/blob/main/skills/apify-ultimate-scraper/references/gotchas.md).
