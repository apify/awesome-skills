# Actor index: Search Console AI Overview rewrite queue

The primary Actor for this skill, the sibling it composes, and the answer-engine Actors worth chaining when a program covers more than Google. The agent reads this after `SKILL.md` to pick the right Actor for a specific user intent.

| Platform | User intent | Actor ID | Tier | Notes |
|----------|-------------|----------|------|-------|
| Google (Search Console + AI Overview) | Turn a Search Console export into a tiered page rewrite queue | `johnvc/ai-overview-rewrite-queue` | community | Composition Actor. Joins Search Console position and CTR with the live AI Overview citation state. Inputs: `target_domains` (required), one of `search_console_csv_url` / `search_console_rows` / `queries`, `min_impressions`, `gl`, `hl`, `location`. One row per query with `tier`, `tier_reason`, `citation_state`, and the joined Search Console metrics. Bills the caller for this Actor and for the child citation Actor. |

## The sibling Actor this one composes

| User intent | Actor ID | Notes |
|-------------|----------|-------|
| The live AI Overview citation check itself, standalone | `johnvc/Google-AI-Overview-API` | This is the Actor the rewrite queue runs for the citation half. Use it directly for a plain watchlist citation check with no Search Console join. Its run bills the caller's own account separately. |

## Chain with other answer-engine Actors

| User intent | Actor ID | Notes |
|-------------|----------|-------|
| The same page audit on Microsoft's answer engine | `johnvc/bing-copilot-api` | Bing Copilot answers and cited sources. |
| Brave Search AI answers | `johnvc/brave-ai-mode-api` | Privacy-focused search visibility. |
| Korean-market AI answers | `johnvc/naver-ai-overview-api` | Naver's AI overview equivalent. |

## How to extend

1. Search candidates: `apify actors search "ai overview" --json --limit 20 --user-agent apify-awesome-skills/apify-search-console-ai-overview 2>/dev/null`
2. Fetch the input schema: `apify actors info "johnvc/ai-overview-rewrite-queue" --input --json --user-agent apify-awesome-skills/apify-search-console-ai-overview 2>/dev/null`
3. Add a row above with the user intent that should trigger it.

Note: `Tier` here is `community` because these are third-party Actors published by John Cole on the Apify Store, not Apify-maintained Actors.
