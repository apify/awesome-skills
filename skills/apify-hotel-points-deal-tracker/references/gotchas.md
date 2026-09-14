# Gotchas: hotel points value and tracking (johnvc/google-hotels-search-scraper)

Cost, scheduling, the parse routine, and the points-cost caveat. Read on demand when building inputs or when a run fails.

## Cost guardrails

Pay per event: about $0.018 per page of results processed (BRONZE tier) plus a $0.02 setup fee per run. A one-page check lands around $0.04. `max_pages` is the hard cost cap; keep it at 1 for a value check or a scheduled watch. For the tracker, a weekly check on a handful of properties is a few cents a month. Confirm live pricing with `apify actors info "johnvc/google-hotels-search-scraper" --json 2>/dev/null`.

## Scheduling (for the tracker)

Apify runs an Actor on a schedule and stores each run's dataset, which gives both the alert trigger and the rate history. Set the schedule in the Apify Console (Schedules), or via the API, on the cadence the traveler wants (weekly is typical). Keep the input tight (one property or a small city query, `max_pages: 1`) so the recurring cost stays negligible. Compare each run's cents per point to the threshold to decide whether to alert.

## The points cost is not in the data

The Actor returns cash rates only. Award points cost comes from the Hyatt fixed chart (see `references/award-values.md`) or from the number the traveler reads in the app for a dynamic program. Never invent a points cost; if you estimate one, say so and tell the traveler to confirm in the app.

## Award availability is separate

A good cents-per-point value does not mean an award room is open. Google Hotels shows cash inventory, not award inventory. Always tell the traveler to confirm the award is bookable in their program.

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| Empty `properties` array | Query too narrow or dates invalid | Broaden the query, check the dates are in the future. |
| Prices look wrong for the market | Currency defaulted from country | Set `currency` explicitly (ISO 4217). |
| Brand filter returns nothing | `hotel_class` combined with `vacation_rentals: true` | Drop the class filter; these points programs are hotels, not rentals. |
| Cents per point looks absurd | Wrong points cost passed | Recheck the points number, or the Hyatt category and season. |

## Parse large results in a subagent

A single search can be 50 to 85 KB of minified JSON in a tool-results file. Hand the saved path to one subagent that returns compact rows (`name`, `extracted_lowest` cash rate, `overall_rating`, `link`, `property_token`), then feed those to `scripts/points_value.py`. `properties` is an array, so request `fields="properties"` (not dot-notation on subfields).

## Actor-specific notes

- Compute on the numeric `rate_per_night.extracted_lowest`, not the display string.
- Dedupe across scheduled runs on `property_token`.
- Baselines in `scripts/points_value.py` are rough defaults; edit them for the traveler's own valuations.
