# Gotchas: AI Overview tracking (johnvc/ai-overview-rewrite-queue)

Cost guardrails, the two-Actor billing model, and error recovery. The agent reads this on demand when setting up a schedule or when a run misbehaves.

## Two Actors bill on one run (read this first)

This is a composition Actor. Each run does two things:

1. It joins your Search Console rows and grades them into tiers. That work bills on THIS Actor: a per-run setup fee plus a per-scored-query fee.
2. It runs the sibling `johnvc/google-ai-overview-api` to fetch the live AI Overview for each scored query. That child run bills YOUR OWN account separately, as its own Actor run.

So a single run charges you for BOTH Actors, and a monthly schedule repeats that charge every month. The query count is the cost driver on both sides. Keep query counts modest, raise `min_impressions` to score fewer low-traffic queries, and set a run budget (`maxTotalChargeUsd` on the run, or a plan-level limit) before scheduling.

## Cost guardrails

Per-event prices at the time of writing. Confirm the live numbers on each Store card, or with `apify actors info "johnvc/ai-overview-rewrite-queue" --json --user-agent apify-awesome-skills/apify-ai-overview-tracking 2>/dev/null` (look at `pricingInfo`).

This Actor (johnvc/ai-overview-rewrite-queue):

- Setup: about $0.005 per run.
- Scored query: about $0.002 per scored query (about $0.0022 on the free tier).

The child citation Actor (johnvc/google-ai-overview-api), billed to your account separately:

- Setup: about $0.01 per run.
- AI Overview retrieval: about $0.015 each, and Google defers some answers, so budget 1 to 2 retrievals per query.

Combined estimate per run, where N is the number of scored queries:

- This Actor: about $0.005 + (N x $0.002).
- Child Actor: about $0.01 + (N x $0.015 to N x $0.030).

Worked numbers, and the monthly cost of a monthly schedule:

- 25 queries: about $0.44 to $0.82 per run, about $5.30 to $9.90 a year monthly.
- 50 queries: about $0.87 to $1.62 per run, about $10.40 to $19.40 a year monthly.
- 100 queries: about $1.72 to $3.22 per run, about $20.60 to $38.60 a year monthly.

The child retrievals dominate, so a shorter tracked list (a higher `min_impressions`, fewer queries) is the main lever.

Suggested confirmation thresholds:

- Per-run estimate over $5, or an annual estimate over $20: get explicit confirmation and set a run budget before scheduling.
- Always present cost as "around $X", not a guarantee, because deferred answers add retrievals.

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| Run fails at startup | `target_domains` missing, or none of `search_console_csv_url` / `search_console_rows` / `queries` provided | Supply `target_domains` plus one query source. |
| No tier B rows | You do not rank 1 to 4 on the tracked queries, or rows lack `position` | Confirm `search_console_rows` carries `position`; otherwise look at tier A. |
| Everything lands in tier X | The join is not matching, or metrics are missing | Confirm `query` values match live queries, `target_domains` is set, and rows carry `position`. |
| Whole run shows `ai_overview_present` false | Non-English `hl`, unsupported country, or head terms that never trigger overviews | Keep `hl=en`, try `gl=us`, rephrase head terms as questions. Checks are still billed. |
| Monthly bill creeping up | Child citation checks scale with query count | Raise `min_impressions`, shorten the tracked list, set a run budget. |

## Tracking notes

- The field to follow over time is `citation_state` per `query`, keyed by `fetched_at`. Cited to competitor_cited is a loss; competitor_cited to cited is a win after a rewrite.
- Tier B is the rank versus citation gap: position 1 to 4 with a competitor cited or no references. This is what a plain citation monitor cannot show, because it has no `position`.
- Rank-aware tiers require Search Console metrics. A bare `queries` list yields `citation_state` but no tier B; those rows read as unmatched (tier X).
- Join rate: Search Console anonymizes long-tail queries, so a long-tail export will not fully match. Expect roughly 30 to 60 percent of a long-tail list to join; unmatched queries are kept in tier X.
- Fix the query set. Adding or removing queries mid-history changes what you are comparing; version the list when it must change.
- AI Overviews vary between identical runs; trend `citation_state` over two or three runs before acting on a flip.
- There is no backfill: history starts at your first run. Schedule before the period you want to measure.
- The per-run summary in the key-value store gives tier counts at a glance before you page through the dataset.
