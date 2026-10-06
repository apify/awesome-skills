# Cost guardrails and error recovery: tennis data

## Confirm live prices before a batch

Prices can change. Read them from the live Actor rather than trusting a copied number:

```bash
apify actors info "crawlplant/tennis-match-dataset" --json \
  --user-agent apify-awesome-skills/apify-tennis-data \
  2>/dev/null
```

The last entry of `pricingInfos` is the current plan. Each event in `pricingPerEvent.actorChargeEvents` has a price per
Apify plan in `eventTieredPricingUsd` (`FREE`, `BRONZE`, `SILVER`, `GOLD`...); use the user's plan, or `FREE` when
unknown.

## Cost model

- One match row per match delivered (`match-row`), whatever the mode that produced it.
- flashscore-tennis adds, per match: `match-odds` (only matches that have odds), `match-h2h` (only when head-to-head
  and form exist), `point-by-point` (only with `includePointByPoint` and only when the match has it).
- Other rows: `ranking-row`, `elo-row`, `player-row`, `stats-row`, `h2h-row`, each one per row.
- `apify-actor-start`: once per run.
- `maxItems` caps the rows after filters. Set it on every run; it is the spend cap.

Rule of thumb: mention cost under about $5, warn over about $5, get explicit sign-off over about $20. Always phrase as
"around $X".

## Guardrails

1. Run with `maxItems` 5-20 first and check the rows before a full day, season or career.
2. In `matches` mode, odds and head-to-head are on by default and are billed per match. A results-only dataset should
   pass `"includeOdds": false, "includeH2H": false`.
3. A multi-day or multi-season request multiplies fast: a busy day has 300-450 singles matches across all tours, an ATP
   season about 4,300 and a WTA season about 3,800. Use `tours` to keep only the levels the user asked for.
4. For a dataset kept up to date, schedule a weekly run of the last 7 days and upsert on `matchId` / `match_id` instead
   of re-reading whole seasons.

## Error recovery

- The run finished but returned fewer rows than expected: filters combine (all must match), `matchType` defaults to
  `singles`, and days are UTC. Check the run's `OUTPUT` record in Console (run, Storage): `warnings` names filters that
  matched nothing and player names it could not resolve.
- A name resolved to the wrong player: `warnings` lists the other candidates; rerun with the Flashscore player URL.
- A match missing odds, Elo, form or point-by-point keeps every other field with that part null, and the missing part
  is not charged.
- Before retrying a failed or interrupted call, check whether the run exists and finished (the run id is in the call
  output, or in Console under the Actor's runs), so a lost response does not start a second paid run.
