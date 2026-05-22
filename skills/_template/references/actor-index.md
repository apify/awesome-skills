# Actor index — REPLACE skill name

Comprehensive Actor routing table. The agent reads this after `SKILL.md` to
pick the right Actor for a specific user intent.

| Platform | User intent | Actor ID | Tier | Notes |
|----------|-------------|----------|------|-------|
| REPLACE | REPLACE | `apify/REPLACE` | apify | REPLACE pricing model, key flags |
| REPLACE | REPLACE | `community/REPLACE` | community | REPLACE |

## How to extend

1. Search for candidates: `apify actors search "KEYWORDS" --json --limit 20 2>/dev/null`
2. Fetch input schema: `apify actors info "ACTOR_ID" --input --json 2>/dev/null`
3. Add a row above with the user intent that should trigger it.

For a polished example covering 130+ Actors across 15+ platforms, see [apify/agent-skills ultimate-scraper actor-index](https://github.com/apify/agent-skills/blob/main/skills/apify-ultimate-scraper/references/actor-index.md).
