# Gotchas — cost guardrails & data caveats

## Cost scaling

- Indeed cost scales with `maxResultsPerQuery` × number of `searchQueries`. For a salary benchmark, 100 listings per role usually gives a stable median; go higher only if the role is sparse.
- `includeDescription: true` adds payload per listing. Turn it off for a pure salary/company snapshot; turn it on when the user needs to read role requirements.
- A cheap calibration run: one role, depth 25, `includeDescription: false` — confirm the market is dense enough, then scale.

## Salary data caveats

- **Not every listing discloses pay.** Treat missing salary as "not disclosed," never as zero. Report the salary sample size separately from the total listing count.
- **Normalize the period.** Listings mix `salaryPeriod` (hourly, yearly). Convert to one basis before computing a median, or you'll average $35/hr with $90,000/yr and get nonsense.
- **Ranges, not points.** A listing's `salaryMin`/`salaryMax` is the employer's posted band, not what they actually pay. Always present a range with the sample size.

## Indeed fragility

- Indeed throttles aggressive scraping. A run that returns fewer results than `maxResultsPerQuery` usually hit pagination limits or regional gating, not a bug — note the actual `n`.
- `country` must match the location (e.g. `country: "us"` with `location: "Austin, TX"`). A mismatch returns thin or empty results.

## Glassdoor module

- `glassdoor-reviews` needs the **Glassdoor company URL** (`/Reviews/<Company>-Reviews-E<id>.htm`), not just a name — resolve it first. Skip the module if you can't resolve the URL for a given employer rather than guessing.
- Reviews are self-selected and skew negative/positive at the extremes; use them as a directional reputation signal, not a verdict.

## Empty results

Zero listings usually means the role title or location was too specific. Broaden ("nurse in Texas" vs "pediatric ICU nurse in Austin TX 78701") and retry.
