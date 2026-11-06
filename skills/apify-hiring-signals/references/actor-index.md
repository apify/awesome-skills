# Actor index — apify-hiring-signals

Comprehensive Actor routing table. The agent reads this after `SKILL.md` to
pick the right Actor for a specific user intent.

| Platform | User intent | Actor ID | Tier | Notes |
|----------|-------------|----------|------|-------|
| Greenhouse / Lever / Ashby / Workable / SmartRecruiters / Recruitee | Company hiring summary, change tracking, signal score | `goldenrod_serrano/ats-hiring-signals` | community | PAY_PER_EVENT: job + company-summary; no login/proxy; optional `changeTracking`, `signalScoring`, `addTickers` |
| Workday career sites | Same signals with country/city server-side filter | `goldenrod_serrano/workday-hiring-signals` | community | PAY_PER_EVENT; location shortcuts e.g. `GCC`, `UAE`, `SEA`; past ~2,000 list cap via facets |

## How to extend

1. Search for candidates: `apify actors search "KEYWORDS" --json --limit 20 --user-agent apify-awesome-skills/apify-hiring-signals 2>/dev/null`
2. Fetch input schema: `apify actors info "ACTOR_ID" --input --json --user-agent apify-awesome-skills/apify-hiring-signals 2>/dev/null`
3. Add a row above only for Actors that stay on the company-hiring-signal path (not LinkedIn/Indeed aggregators).
