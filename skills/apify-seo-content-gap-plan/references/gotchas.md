# Gotchas — apify-seo-content-gap-plan

Cost guardrails, plan limits and failure modes. Read when building inputs or when a run
returns something unexpected.

## Cost guardrails

Both Actors are `PAY_PER_EVENT`. Prices sit in the last entry of `pricingInfos` from
the Actor details fetched in step 2 of SKILL.md, per plan tier (`FREE`, `BRONZE`, `SILVER`, `GOLD` …).

| Actor | Event | Estimate |
|---|---|---|
| Competitor Keywords | `keyword` | competitors x `maxKeywords` x price. Upper bound: you pay for delivered rows only, and filters (`minVolume`, `maxKeywordDifficulty`, `intentFilter`, `positionTo`) cut rows before billing |
| AI Keyword Clustering | `batch_1k_keywords` | one event per run of up to 1,000 keywords. 10 keywords cost the same as 1,000 |

- Above $5: warn. Above $20: the user must confirm the amount. Always call it a rough estimate.
- Cheapest useful run: 1 competitor, `maxKeywords` 50-100, `minVolume` 100, then one
  clustering batch. On a paid plan most of the cost is the clustering batch, so cluster once
  with the full filtered list rather than several small runs.
- Gap-mode rows with `gap_type` `stronger` or `tied` are billed but not used. `positionTo: 20`
  and `minVolume` reduce them; there is no input to exclude them.

## Free Apify plan

- Competitor Keywords trims silently: only the first domain in `targets` and at most 100 rows.
  Run one call per competitor and tell the user the result is a preview.
- AI Keyword Clustering refuses more than 200 input keywords (run `SUCCEEDED`, 0 items, status
  "Nothing was charged: the free plan supports up to 200 keywords per run"). Cap the list
  at 200 by volume before calling.
- On the free plan one clustering batch uses most of the monthly free credit. Say so in the
  estimate; if the user declines, deliver the filtered gap list grouped by `competitor_url`
  (pages that rank for several gap keywords are natural topics) and mark it "not clustered".

## Common errors

| Error | Cause | Fix |
|---|---|---|
| Gap run `SUCCEEDED`, 0 rows, "Gap mode needs `compareToDomain`" | Missing user domain | Add `compareToDomain` |
| Gap run 0 rows, no error | Filters too strict, or the competitor has no rankings in that market | Lower `minVolume`, widen `positionTo`, check `location` |
| Clustering run 0 items, "cannot bill one keyword batch within its maximum charge" | The run's maximum total charge is below one batch price | Raise the run's charge limit to at least one batch, or run without a limit |
| Clustering run 0 items, timeout message | Backend hard limit (about 12 minutes) | Retry with fewer keywords or SERP validation off; nothing was charged |
| `location`/`language` rejected | CK expects full names, CL expects ISO codes | `"United Kingdom"`/`"English"` for CK, `gb`/`en` for CL |
| 402 | No credit left | Stop; offer the smaller run |
| 403 `public-actor-disabled` | Account cannot run public Actors | Stop; the user must change account settings |
| CLI `call` returns before the run ends | Long clustering run | Look the run up in Console, then `apify datasets get-items` with its dataset ID |

## Data quirks

- `keyword_difficulty` is sparse outside major English markets and comes back as `0`. Treat
  0 as unknown, not easy (see prioritization).
- Domain-wide competitors (big SaaS blogs, marketplaces) rank for glossary terms far from
  their product. Expect a large share of off-topic rows; the relevance filter is not optional.
- The clustering Actor expands inputs under 200 keywords with related keywords. Those are
  useful as supporting ideas but carry no gap evidence.
- The clustering Actor returns its own `google_search_volume`; for scoring use the gap Actor's
  `search_volume` so both numbers come from one source.
- Same keyword from several competitors: one row per competitor. Deduplicate before
  clustering, keep the list of competitors that rank.
