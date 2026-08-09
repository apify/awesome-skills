# Gotchas: Google Flights Deals API (`johnvc/google-flights-deals-api`)

Cost guardrails, error recovery, and input quirks. The agent reads this on demand when building inputs or when a run fails.

## Cost guardrails

Pricing model: pay per event, plus a platform fee of about $0.00001 per dataset row. Charge events:

- `deal_returned`: about $0.0025 per destination returned (BRONZE tier at the time of writing).
- `actor_start`: about $0.001 per run.

Confirm the live price before a large batch:

```bash
apify actors info "johnvc/google-flights-deals-api" --json \
  --user-agent apify-awesome-skills/apify-google-flights-tracking \
  2>/dev/null
```

Worked estimates for this skill:

- One airport at thirty deals is about $0.08 per reading.
- Daily for a month, one airport, is roughly $2.30.
- Daily for a month, three airports, is roughly $7. Always quote the monthly figure for a schedule, not the per-run one.

Suggested confirmation thresholds:

- Rough estimate over $5: warn the user.
- Rough estimate over $20: get explicit confirmation before running.
- Always present cost as "around $X", not a guarantee.

## Actor-specific notes

- The Actor keeps no history and sends no alerts. Storing the readings and writing the notify rule are the caller's job, and copy must not imply otherwise.
- `average_price` is what makes the record useful: each observation arrives with its own reference price, so a rule can be 'below typical' rather than a guessed threshold.
- The destination set changes between runs because it is the cheapest thirty, not a fixed watchlist. A route can drop out because it got expensive; treat absence as missing data, never as a zero.
- With dates blank the itinerary floats between runs, so you track the cheapest available trip rather than one fixed departure. Pin `outboundDate` if you need a fixed one.
- Never set `maxDurationMinutes` on a tracking schedule: it removes the baseline and with it the whole point of the record.
- Keep the input shape fixed across runs, cabin and stops included, or readings stop being comparable.
- Key stored rows on departure, arrival, and travel date, and stamp the run time yourself; the Actor does not add one.

## Error recovery

- An `error` row explains the failure in plain terms; deals that never arrived are not charged.
- A gap in the series is usually the route leaving the cheapest thirty, not a failed run. Check the run status before backfilling.
- Baseline fields missing: `maxDurationMinutes` is set on the task. Remove it and re-run.
- Transient upstream failures: retry once. A scheduled run that fails is not charged for undelivered rows.
- Costs climbing faster than expected: count airports times deals times runs per month before widening a schedule.
