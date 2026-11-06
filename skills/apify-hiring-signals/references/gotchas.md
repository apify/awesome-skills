# Gotchas — apify-hiring-signals

Cost guardrails, error recovery, and common pitfalls. The agent reads this
on demand when building inputs or when a run fails.

## Cost guardrails

Both routed Actors use `PAY_PER_EVENT`. Before running, confirm live prices:

    apify actors info "goldenrod_serrano/ats-hiring-signals" --json \
      --user-agent apify-awesome-skills/apify-hiring-signals 2>/dev/null

    apify actors info "goldenrod_serrano/workday-hiring-signals" --json \
      --user-agent apify-awesome-skills/apify-hiring-signals 2>/dev/null

| Model | What to watch for |
|-------|-------------------|
| `PAY_PER_EVENT` | Charged events: `job`, `company-summary`, plus a small Actor-start event. Free-tier list prices on the Store pages are about $0.001 / job and $0.005 / company-summary (tier discounts may apply). |

### Confirmation thresholds (suggested)

- Estimated cost **>$5** → warn the user.
- Estimated cost **>$20** → require explicit user confirmation before running.
- Always present cost as a **rough estimate** ("around $X"), not a guarantee.
- Prefer `outputJobs: false` when the user only needs company rankings.
- `includeDescription` (ATS) / `includeDetails` (Workday) increase payload and Workday per-job detail calls — leave off for signal-only runs.
- Set Apify max charge per run so output stops cleanly at the budget.

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| `type: "error"` / board not found | Bad slug, private board, or non-supported ATS | Use board URL or `ats:slug`; bare slugs can collide across ATS |
| Workday list stuck at ~2,000 | Site larger than Workday list view | Add `locations` and/or `searchText` for server-side facets |
| No `closed_jobs_*` on later run | Incomplete scan or first baseline | Keep filters/`stateKey` stable; only trust closures when scan is complete |
| Empty dataset on change-tracking follow-up | No changes since last run | Expected; report zero new/changed/closed rather than re-running with a new `stateKey` |
| Auth / 401 from CLI | Missing `APIFY_TOKEN` or login | `apify login` or set `APIFY_TOKEN`; never put the token in a URL |

## Actor-specific notes

### `goldenrod_serrano/ats-hiring-signals`

- Supports Greenhouse, Lever, Ashby, Workable, SmartRecruiters, Recruitee only — not Workday (use the sister Actor).
- SmartRecruiters list endpoint does not return descriptions; `includeDescription` stays empty there.
- With `changeTracking` on, `maxJobsPerCompany` limits **output**, not what is remembered as seen.

### `goldenrod_serrano/workday-hiring-signals`

- Paste job links, search links, or locale paths; company careers pages that redirect to Workday also work.
- `posted_date` precision improves when `includeDetails` is on.
- Location shortcuts such as `GCC`, `UAE`, `KSA`, `SEA`, `LATAM`, `UK`, `US` map to the site's own facets when present.
