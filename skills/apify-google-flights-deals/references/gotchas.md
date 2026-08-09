# Gotchas: Google Flights Deals API (`johnvc/google-flights-deals-api`)

Cost guardrails, error recovery, and input quirks. The agent reads this on demand when building inputs or when a run fails.

## Cost guardrails

Pricing model: pay per event, plus a platform fee of about $0.00001 per dataset row. Charge events:

- `deal_returned`: about $0.0025 per destination returned (BRONZE tier at the time of writing).
- `actor_start`: about $0.001 per run.

Confirm the live price before a large batch:

```bash
apify actors info "johnvc/google-flights-deals-api" --json \
  --user-agent apify-awesome-skills/apify-google-flights-deals \
  2>/dev/null
```

Worked estimates for this skill:

- A full thirty-destination sweep from one airport is about $0.08.
- Three home airports at thirty each is about $0.23.
- Twenty airports in one run is about $1.50.

Suggested confirmation thresholds:

- Rough estimate over $5: warn the user.
- Rough estimate over $20: get explicit confirmation before running.
- Always present cost as "around $X", not a guarantee.

## Actor-specific notes

- There is no arrival airport. The feed answers where to go, not what a chosen route costs.
- `maxDealsPerAirport` caps at 30, which is the source ceiling rather than a setting you can raise.
- `maxDurationMinutes` makes the source stop returning the baseline, which switches off `savings`, `savings_percent`, and `is_below_typical`. The Actor logs a warning when you set it. Every other filter keeps the baseline.
- `includeAirlines` and `excludeAirlines` are mutually exclusive and validated in code.
- Leaving `outboundDate` blank lets the feed pick cheap dates and report the ones it found, which is the opposite of a normal flight search.
- Negative `savings` is real data: that route is currently priced above its own norm. Those rows tell you what to skip.
- Measured across three hubs during the build, between 6 and 30 percent of a feed clears its own baseline on a given day. A run with no bargains is a normal outcome.

## Error recovery

- An `error` row explains the failure in plain terms; deals that never arrived are not charged.
- Empty feed: thin-coverage airport. Try a larger hub nearby.
- Baseline fields missing across every row: `maxDurationMinutes` is set. Remove it.
- Transient upstream failures: retry once before changing inputs.
- If a run stops early at your budget limit, rows already delivered are kept and billed; lower `maxDealsPerAirport` or drop an airport.
