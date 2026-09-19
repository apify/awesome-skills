---
name: apify-ai-overview-tracking
description: "Find the pages that rank but are never cited by Google's AI with the Apify AI Overview Rewrite Queue Actor (johnvc/ai-overview-rewrite-queue). This is ai overview tracking that uses your Search Console position data to expose the rank versus citation gap: the pages ranking 1 to 4 whose AI Overview cites competitors or shows no references, graded into a tiered queue instead of a plain yes or no citation check. Track citation_state on a monthly schedule to see where you win or lose AI Overview citations against your rankings over time. Use when the user wants ai overview tracking, to monitor AI Overview citations against rankings, or to find high-ranking pages that Google's AI ignores. Pass target_domains plus a Search Console CSV, inline rows, or a query list. Pay per scored query, MCP-ready for Claude and other AI agents."
author: John Cole
author_url: https://github.com/johnisanerd
license: MIT
metadata:
  version: "1.0"
  keywords: "ai overview tracking, ai overview citations, rank versus citation, generative engine optimization, ai visibility"
---

# AI Overview Tracking: The Rank Versus Citation Gap

Find the pages that rank but are never cited by Google's AI. This Actor grades each query by two signals at once, where you rank in Search Console and whether the AI Overview cites you, so the pages ranking 1 to 4 that the overview cites competitors on (or cites nobody on) surface as tier B. Track `citation_state` on a schedule and you can see, month over month, where you gain or lose an AI Overview citation while your ranking holds.

## When to use this skill

- The user wants "ai overview tracking" that is tied to rankings, not a standalone citation watchlist.
- They want to find high-ranking pages (position 1 to 4) that Google's AI Overview ignores or cites a competitor on instead.
- They want to monitor `citation_state` over time on a monthly schedule and see the rank versus citation gap move.
- They want a graded queue of where to act, not a yes or no answer for a fixed set of queries.

Not for: a plain citation yes or no check across a fixed watchlist with no ranking context (use the google-ai-overview-monitoring skill), organic rank tracking on its own, or building the rewrite content itself.

## Distinct from a plain citation monitor

A watchlist monitor answers one question per query: is the brand cited, yes or no. This skill needs your Search Console position data, so it can answer a sharper one: are you cited relative to how you rank. That is what makes a top-ranking page that the AI ignores visible. The output is a graded queue (tiers), not a boolean, and the tier depends on both rank and citation state together.

## What you get (one row per query)

Queue and identity: `result_type`, `query`, `query_normalized`, `tier` (A to D, or X), `tier_reason`, `join_status`.

Ranking signals from the join: `clicks`, `impressions`, `ctr`, `position`.

Citation signals to track over time: `check_status`, `ai_overview_present`, `citation_state` (cited, competitor_cited, no_overview, overview_no_references, or null), `cited_urls`, `cited_pages_count`, `reference_domains`, `reference_count`, `fetched_at`. Failures carry `error_message` and `error_type`.

A per-run summary is written to the key-value store.

### The tier that matters here

- Tier B is the rank versus citation gap: you rank position 1 to 4, yet a competitor is cited or the overview shows no references. You have the ranking; you are missing the citation.
- Tier A: a competitor is cited and you rank 5 to 20 (the deeper rewrite opportunity).
- Tier C: you are cited but your CTR sits below your own baseline for that query.
- Tier D: no AI Overview for the query.
- Tier X: the check failed, or the query did not match a Search Console row. Kept so the gap stays visible.

For tracking, the field to follow is `citation_state` per `query` over `fetched_at`.

## Prerequisites

- Apify account (sign up at https://apify.com?fpr=9n7kx3&fp_sid=awesomeskills).
- Authentication via `apify login`, or an `APIFY_TOKEN` environment variable (Apify Console, Settings, Integrations).
- Search Console position data, which is what makes this rank-aware. Export the Queries report as CSV and pass `search_console_csv_url`, or pass rows inline as `search_console_rows`.

## The Actor

- Store page: https://apify.com/johnvc/ai-overview-rewrite-queue?fpr=9n7kx3&fp_sid=awesomeskills
- Actor ID: `johnvc/ai-overview-rewrite-queue`
- Pricing: a per-run setup fee plus a per-scored-query fee. This is a composition Actor, so the citation half runs a second Actor that bills your own account separately. Read `references/gotchas.md` before scheduling.

## Run it with the Apify CLI

One tracking pass from a hosted Search Console CSV:

```bash
apify actors call "johnvc/ai-overview-rewrite-queue" -i '{"target_domains":["example.com"],"search_console_csv_url":"https://example.com/exports/search-console-queries.csv","min_impressions":25,"gl":"us","hl":"en"}' \
  --json \
  --user-agent apify-awesome-skills/apify-ai-overview-tracking \
  2>/dev/null
```

From inline rows, to track a fixed set of money queries:

```bash
apify actors call "johnvc/ai-overview-rewrite-queue" -i '{"target_domains":["example.com"],"search_console_rows":[{"query":"best crm for startups","clicks":40,"impressions":900,"ctr":0.044,"position":2.1},{"query":"crm free tier","clicks":22,"impressions":610,"ctr":0.036,"position":3.4}],"min_impressions":25}' \
  --json \
  --user-agent apify-awesome-skills/apify-ai-overview-tracking \
  2>/dev/null
```

Read a run's rows back later, for example from a scheduled run:

```bash
apify datasets get-items <DATASET_ID> --format json --user-agent apify-awesome-skills/apify-ai-overview-tracking 2>/dev/null
```

Every call carries the three flags this repo expects: `--json` (or `--format json`), `--user-agent apify-awesome-skills/apify-ai-overview-tracking`, and `2>/dev/null`.

## Run it from Claude or another AI agent (MCP)

The Actor is MCP-ready. Add the hosted server URL:

`https://mcp.apify.com/?tools=actors,docs,johnvc/ai-overview-rewrite-queue`

Then ask, for example: "Track example.com against my Search Console queries and list the tier B pages, where I rank top 4 but the AI Overview cites someone else." MCP setup docs: https://docs.apify.com/platform/integrations/mcp

## Workflow

1. Fix the query set. Export the Search Console Queries report as CSV, or keep a stable list of money queries as `search_console_rows`. A fixed set keeps the month-over-month history comparable.
2. Set `target_domains` to every property you own, so cited versus competitor_cited is classified correctly.
3. Set `min_impressions` (25 is a reasonable tracking floor) so you track queries with real traffic and hold the child citation cost down.
4. Estimate the cost for both Actors and set a run budget. See `references/gotchas.md`.
5. Run and read tier B first: high rank, missing citation. Then A, then C.
6. Schedule monthly. Save the input as an Apify task and attach a monthly schedule, or cron the CLI call. Each run stamps `fetched_at`; append rows to your own store keyed by `query` plus `fetched_at`.
7. Track the deltas. Report queries that moved between `citation_state` values since the last run, especially cited to competitor_cited (a loss) and competitor_cited to cited (a win after a rewrite).

## Inputs

- `target_domains` (array, required): your domains; used to classify cited versus competitor_cited.
- `search_console_csv_url` (string): URL to a Search Console Queries CSV. One of the three query sources.
- `search_console_rows` (array): inline rows of {query, clicks, impressions, ctr, position}; needed for rank-aware tiers.
- `queries` (array): a bare query list; without metrics these join as unmatched (tier X) but still get a citation check.
- `min_impressions` (int, default 10): impression floor; raise it for tracking to focus on traffic-carrying queries.
- `gl` (string, default us) and `hl` (string, default en): market targeting for the citation check. One market per run.
- `location` (string): optional named location for local-intent queries.

## Cost

Two Actors bill on one run. This Actor charges a per-run setup fee plus a per-scored-query fee; the citation half runs the sibling `johnvc/google-ai-overview-api`, whose run bills your own account separately (a setup fee plus a per-retrieval fee, one or two retrievals per query). A monthly schedule multiplies a single run's cost by twelve a year, so size the query set deliberately. Keep query counts modest, raise `min_impressions`, and set a run budget. Worked numbers and exact prices are in `references/gotchas.md`.

## Honest limits

- Join rate. Search Console anonymizes long-tail queries, so a long-tail export will not fully match; expect roughly 30 to 60 percent of a long-tail list to join. Unmatched queries are labelled tier X and kept, never dropped.
- AI Overviews are not deterministic. `citation_state` can flip between identical runs, so alert on a trend across two or three runs, not a single flip.
- There is no backfill: the history starts at your first run, so schedule before the period you want to measure.
- Rank-aware tiers need Search Console metrics; a bare `queries` list gives you citation state but no tier B, because there is no `position` to compare against.
- The queue shows where the gap is; closing it is a content rewrite, which is your call.

## Troubleshooting

- No tier B rows: either you do not rank 1 to 4 on the tracked queries (look at tier A) or your top pages are already cited (good). Confirm `search_console_rows` carries `position`.
- Everything lands in tier X: the join is not matching or metrics are missing. Confirm `query` values match, `target_domains` is set, and rows carry `position`.
- `citation_state` flapping month to month: normal AI Overview variance; trend it over several runs before acting.
- Whole run shows `ai_overview_present` false: keep `hl` at en, try `gl` at us, and check the queries trigger overviews.
- Monthly bill creeping up: the child citation checks scale with query count; trim the set or raise `min_impressions`, and set a run budget.

See `references/gotchas.md` for cost guardrails and error recovery, and `references/actor-index.md` for the Actor routing table.

## Related answer-engine Actors

- Google AI Overview API (the citation engine this Actor composes, and a standalone yes or no check): https://apify.com/johnvc/Google-AI-Overview-API?fpr=9n7kx3&fp_sid=awesomeskills
- Bing Copilot API: https://apify.com/johnvc/bing-copilot-api?fpr=9n7kx3&fp_sid=awesomeskills
- Naver AI Overview API: https://apify.com/johnvc/naver-ai-overview-api?fpr=9n7kx3&fp_sid=awesomeskills
