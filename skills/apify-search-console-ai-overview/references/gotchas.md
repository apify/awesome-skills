# Gotchas: Search Console AI Overview rewrite queue (johnvc/ai-overview-rewrite-queue)

Cost guardrails, the two-Actor billing model, and error recovery. The agent reads this on demand when scoping a run or when a run misbehaves.

## Two Actors bill on one run (read this first)

This is a composition Actor. It does two things per run:

1. It joins your Search Console rows and grades them into tiers. That work bills on THIS Actor: a per-run setup fee plus a per-scored-query fee.
2. It runs the sibling `johnvc/google-ai-overview-api` to fetch the live AI Overview for each scored query. That child run bills YOUR OWN account separately, as its own Actor run.

So a single run charges you for BOTH Actors. The query count is the cost driver on both sides. Keep query counts modest, raise `min_impressions` to score fewer low-traffic queries, and set a run budget (`maxTotalChargeUsd` on the run, or a plan-level limit) before you launch a large export.

## Cost guardrails

Per-event prices at the time of writing. Confirm the live numbers on each Store card, or with `apify actors info "johnvc/ai-overview-rewrite-queue" --json --user-agent apify-awesome-skills/apify-search-console-ai-overview 2>/dev/null` (look at `pricingInfo`).

This Actor (johnvc/ai-overview-rewrite-queue):

- Setup: about $0.005 per run.
- Scored query: about $0.002 per scored query (about $0.0022 on the free tier).

The child citation Actor (johnvc/google-ai-overview-api), billed to your account separately:

- Setup: about $0.01 per run.
- AI Overview retrieval: about $0.015 each, and Google defers some answers, so budget 1 to 2 retrievals per query.

Combined estimate per run, where N is the number of scored queries:

- This Actor: about $0.005 + (N x $0.002).
- Child Actor: about $0.01 + (N x $0.015 to N x $0.030).

Worked numbers:

- 25 queries: this Actor about $0.055; child about $0.39 to $0.76; total about $0.44 to $0.82.
- 50 queries: this Actor about $0.105; child about $0.76 to $1.51; total about $0.87 to $1.62.
- 100 queries: this Actor about $0.205; child about $1.51 to $3.01; total about $1.72 to $3.22.

The child retrievals dominate, so trimming the query list (a higher `min_impressions`, a shorter export) is the main lever.

Suggested confirmation thresholds:

- Combined estimate over $5: warn the user.
- Combined estimate over $20: get explicit confirmation and set a run budget before launching.
- Always present cost as "around $X", not a guarantee, because deferred answers add retrievals.

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| Run fails at startup | `target_domains` missing, or none of `search_console_csv_url` / `search_console_rows` / `queries` provided | Supply `target_domains` plus one query source. |
| Everything lands in tier X | The join is not matching, or the citation check failed | Confirm `query` values match live queries, `target_domains` is set, and `min_impressions` is not filtering the whole list. |
| Whole run shows `ai_overview_present` false | Non-English `hl`, unsupported country, or head terms that never trigger overviews | Keep `hl=en`, try `gl=us`, rephrase head terms as questions. Checks are still billed. |
| Domain always reads competitor_cited | `target_domains` is too narrow to match a subdomain or apex variant | List every property you own; the Actor compares registered domains. |
| Cost higher than expected | The child citation checks scale with query count | Raise `min_impressions`, shorten the export, and set a run budget. |

## Scoring and join notes

- Join rate: Search Console anonymizes long-tail queries, so a long-tail export will not fully match. Expect roughly 30 to 60 percent of a long-tail list to join. Unmatched queries get `join_status` unmatched, land in tier X, and are kept, never dropped.
- Tier A is the highest-leverage bucket: a competitor is cited and you rank position 5 to 20. Work these first.
- Tier C uses your own historical CTR for the query as the baseline, not an industry benchmark.
- `citation_state` values: cited, competitor_cited, no_overview, overview_no_references, or null. Read it together with `reference_domains` and `cited_urls` to brief a rewrite.
- AI Overviews vary between identical runs; confirm a tier A over a couple of runs before committing a large rewrite.
- History key: `query` plus `fetched_at`. Re-run after shipping rewrites to confirm the tier moved.
- The per-run summary in the key-value store is a quick read for tier counts before you page through the dataset.
