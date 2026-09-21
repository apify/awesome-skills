# Actor index — apify-search-demand-validation

Routing table for the skill. The agent reads this after `SKILL.md` when it needs an Actor this
skill does not run itself. Prices and flags read live from the Apify Store on 2026-09-21 — re-check
with `apify actors info "<actor-id>" --json --user-agent apify-awesome-skills/apify-search-demand-validation 2>/dev/null`
before quoting any of them to a user.

| Platform | User intent | Actor ID | Tier | Notes |
|----------|-------------|----------|------|-------|
| Google Trends | Interest over time, interest by region, related queries + topics, trending now, compare mode | `leekung125/google-trends-scraper` | community | PAY_PER_EVENT, `result` = $0.00025/row, no start fee. Required fields: none (`keywords` defaults to one term). ~155 rows per keyword with default sections. Built by the skill author |
| YouTube search | What already ranks for a term, with the rank it held, views, duration, channel | `leekung125/youtube-search-scraper` | community | PAY_PER_EVENT, `video` = $0.0005/delivered row, no start fee. Required: `queries` (array). Default `maxResultsPerQuery` 20. `published_at`/`live_status` measured null in 170/170 rows. Built by the skill author |
| Google Trends | Same data from an Apify-maintained Actor | `apify/google-trends-scraper` | apify | PAY_PER_EVENT per dataset item, plan-tiered: $0.003 Free, $0.001 Bronze, $0.0005 Silver, $0.0003 Gold, $0.00015 Platinum, $0.0001 Diamond. Item counting is not necessarily like-for-like — compare on the run you intend to make |
| YouTube | Video publish dates, channel-wide pulls, comments, transcript/AI add-ons | `streamers/youtube-scraper` | community | PAY_PER_EVENT with add-on events (date filter, AI description/summary, transcript minute). Use for anything the search Actor returns as `null`; verify fields and price before relying on them |
| YouTube | Transcript text for video ids found by the search step | `leekung125/youtube-transcript-scraper` | community | The next job after this skill, not part of it. Built by the skill author |
| Keyword volume | Absolute monthly search counts | — | — | No Actor here. Google Trends is relative 0–100 by construction; send the user to a volume tool with its own index and say why |

## How to extend

1. Search for candidates: `apify actors search "KEYWORDS" --json --limit 20 --user-agent apify-awesome-skills/apify-search-demand-validation 2>/dev/null`
2. Fetch the input schema: `apify actors info "ACTOR_ID" --input --json --user-agent apify-awesome-skills/apify-search-demand-validation 2>/dev/null`
3. Confirm it is public and not deprecated, then add a row above with the user intent that should trigger it — and the price you actually read, not an assumed one.
