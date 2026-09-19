# Actor index: AI Overview tracking (rank versus citation)

The primary Actor for this skill, the sibling it composes, and the answer-engine Actors worth chaining when tracking covers more than Google. The agent reads this after `SKILL.md` to pick the right Actor for a specific user intent.

| Platform | User intent | Actor ID | Tier | Notes |
|----------|-------------|----------|------|-------|
| Google (Search Console + AI Overview) | Track the rank versus citation gap over time and surface high-ranking pages the AI ignores | `johnvc/ai-overview-rewrite-queue` | community | Composition Actor. Grades each query by rank and citation state together, so top-ranked pages missing a citation land in tier B. Inputs: `target_domains` (required), one of `search_console_csv_url` / `search_console_rows` / `queries`, `min_impressions`, `gl`, `hl`, `location`. Track `citation_state` per `query` over `fetched_at`. Bills the caller for this Actor and the child citation Actor. |

## The sibling Actor this one composes

| User intent | Actor ID | Notes |
|-------------|----------|-------|
| A plain yes or no AI Overview citation check on a fixed watchlist, no ranking context | `johnvc/Google-AI-Overview-API` | The Actor the tracker runs for the citation half. Use it directly when there is no Search Console data and no need for rank-aware tiers. Its run bills the caller's own account separately. |

## Chain with other answer-engine Actors

| User intent | Actor ID | Notes |
|-------------|----------|-------|
| Track the same pages on Microsoft's answer engine | `johnvc/bing-copilot-api` | Bing Copilot answers and cited sources. |
| Brave Search AI answers | `johnvc/brave-ai-mode-api` | Privacy-focused search visibility. |
| Korean-market AI answers | `johnvc/naver-ai-overview-api` | Naver's AI overview equivalent. |

## How to extend

1. Search candidates: `apify actors search "ai overview tracking" --json --limit 20 --user-agent apify-awesome-skills/apify-ai-overview-tracking 2>/dev/null`
2. Fetch the input schema: `apify actors info "johnvc/ai-overview-rewrite-queue" --input --json --user-agent apify-awesome-skills/apify-ai-overview-tracking 2>/dev/null`
3. Add a row above with the user intent that should trigger it.

Note: `Tier` here is `community` because these are third-party Actors published by John Cole on the Apify Store, not Apify-maintained Actors.
