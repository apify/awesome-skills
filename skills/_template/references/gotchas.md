# Gotchas — REPLACE skill name

Cost guardrails, error recovery, and common pitfalls. The agent reads this
on demand when building inputs or when a run fails.

## Cost guardrails

Apify Actors use one of three pricing models. Before running, check the
model via `apify actors info "ACTOR_ID" --json 2>/dev/null` (look at
`pricingInfo`).

| Model | What to watch for |
|-------|-------------------|
| `FREE` | No cost — safe to run. |
| `PAY_PER_EVENT` | Cost scales with results. Estimate before running. |
| `FLAT_PRICE_PER_MONTH` | Subscription — runs are unlimited once paid. |

### Confirmation thresholds (suggested)

- Estimated cost **>$5** → warn the user.
- Estimated cost **>$20** → require explicit user confirmation before running.
- Always present cost as a **rough estimate** ("around $X"), not a guarantee.

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| REPLACE | REPLACE | REPLACE |
| REPLACE | REPLACE | REPLACE |

## Actor-specific notes

### `apify/REPLACE-actor-id`

- REPLACE: input quirk
- REPLACE: known limitation
- REPLACE: rate-limit behavior

For a polished gotchas example with detailed cost tables and error-recovery flows, see [apify/agent-skills ultimate-scraper gotchas](https://github.com/apify/agent-skills/blob/main/skills/apify-ultimate-scraper/references/gotchas.md).
