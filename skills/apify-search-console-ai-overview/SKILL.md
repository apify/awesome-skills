---
name: apify-search-console-ai-overview
description: "Build a prioritized page rewrite queue from your Google Search Console data with the Apify AI Overview Rewrite Queue Actor (johnvc/ai-overview-rewrite-queue). It joins your Search Console query positions and CTR against the live Google AI Overview citation state, then returns a tiered queue that puts the highest-leverage rewrites first, the pages where a competitor is cited in the AI Overview while you rank 5 to 20. Use when the user asks about google search console ai overview, search console ai overview, which pages to rewrite for AI Overviews, or wants to turn a Search Console export into an action list. Pass target_domains plus a Search Console CSV, inline rows, or a query list. Pay per scored query, MCP-ready for Claude and other AI agents."
author: John Cole
author_url: https://github.com/johnisanerd
license: MIT
metadata:
  version: "1.0"
  keywords: "google search console ai overview, search console ai overview, ai overview rewrite queue, ai overview tracking, seo content refresh"
---

# Search Console AI Overview: A Prioritized Rewrite Queue
**Disclosure:** the Apify links on this page carry the author's affiliate code (`fpr=9n7kx3`), so the author earns from sign-ups made through them, and the Actors this skill routes to are published by `johnvc`, whose Store listing credits this skill's author.


Build a prioritized rewrite queue from your Google Search Console data. This Actor joins each query's Search Console position and CTR against the live AI Overview citation state, then returns a tiered queue so you rewrite the highest-leverage pages first: the ones where a competitor is cited in the AI Overview while you still rank 5 to 20.

## When to use this skill

- The user wants to know which pages to rewrite because of Google AI Overviews, starting from their own Search Console data.
- They ask about "google search console ai overview" or "search console ai overview" and want an action list, not a dashboard.
- They have a Search Console Queries export (CSV) and a domain, and want it turned into a ranked to-do queue.
- They want the join that nothing else does: Search Console rank and CTR on one side, live AI Overview citation state on the other.

Not for: a plain yes or no citation check across a fixed watchlist (run `johnvc/Google-AI-Overview-API` directly), organic rank tracking on its own, or content rewriting itself (this tells you which pages to rewrite, not what to write).

## What you get (one row per query)

Queue and identity: `result_type` (labels the record), `query`, `query_normalized`, `tier` (A to D, or X), `tier_reason` (why it landed there), `join_status` (whether the query matched a Search Console row).

Search Console metrics carried through the join: `clicks`, `impressions`, `ctr`, `position`.

Live citation check: `check_status`, `ai_overview_present`, `citation_state` (one of cited, competitor_cited, no_overview, overview_no_references, or null), `cited_urls`, `cited_pages_count`, `reference_domains`, `reference_count`, `fetched_at`. A citation check that does not complete is **not** an error row: it comes back as `result_type: scored_query` with `check_status: retrieval_failed` or `blocked`, `citation_state: null` and tier X, and it still bills a scored query. `error_message` and `error_type` appear only on a `result_type: error` row, which describes a run that could not proceed at all.

A run summary is written to the key-value store.

### How tiers rank the queue

- Tier A: a competitor is cited in the AI Overview and you rank position 5 to 20. Highest-leverage rewrites; do these first.
- Tier B: a competitor is cited or the overview has no references, and you rank 1 to 4. You are close; a rewrite can win the citation.
- Tier C: you are already cited but your CTR is below your own baseline — the baseline being your CTR on queries in *this same export* that have no AI Overview at a comparable position, not that query's own history. A small export often has too few of those for the baseline to exist, and then tier C cannot fire at all.
- Tier D: no AI Overview for the query.
- Tier X: the citation check failed, or the query did not match a Search Console row. Kept, never dropped, so you can see the gap.

## Example prompts

Prompts this skill handles:

- "Here is my Search Console Queries export for example.com — which pages should I rewrite first because of AI Overviews?"
- "Turn this Search Console CSV into a ranked rewrite queue and show me the tier A rows."
- "For these 20 queries, where does the AI Overview cite a competitor while I rank on page one or two?"

Out of scope (the boundary):

- "Is my brand cited in the AI Overview for these 10 queries?" — a plain citation check with no Search Console data behind it. Run `johnvc/Google-AI-Overview-API` directly; this skill needs rank and CTR to tier anything.
- "Rewrite the page for me." — this skill tells you which pages to rewrite, not what to write.

## Prerequisites

- Apify account (sign up at https://apify.com?fpr=9n7kx3&fp_sid=awesomeskills).
- Authentication via `apify login`, or an `APIFY_TOKEN` environment variable (Apify Console, Settings, Integrations).
- Your Search Console Queries report. Export it from the Performance report as CSV, host it at a URL and pass `search_console_csv_url`, or pass the rows inline as `search_console_rows`.

## The Actor

- Store page: https://apify.com/johnvc/ai-overview-rewrite-queue?fpr=9n7kx3&fp_sid=awesomeskills
- Actor ID: `johnvc/ai-overview-rewrite-queue`
- Pricing: a small per-run setup fee plus a scored-query fee. This is a composition Actor, so the citation half runs a second Actor that bills your own account separately. Read `references/gotchas.md` before scheduling.

## Run it with the Apify CLI

From a hosted Search Console CSV:

```bash
apify actors call "johnvc/ai-overview-rewrite-queue" -i '{"target_domains":["example.com"],"search_console_csv_url":"https://example.com/exports/search-console-queries.csv","min_impressions":10,"gl":"us","hl":"en"}' \
  --json \
  --user-agent apify-awesome-skills/apify-search-console-ai-overview \
  2>/dev/null
```

From inline rows, when you already have the Queries report in hand:

```bash
apify actors call "johnvc/ai-overview-rewrite-queue" -i '{"target_domains":["example.com"],"search_console_rows":[{"query":"best crm for startups","clicks":12,"impressions":540,"ctr":0.022,"position":7.3},{"query":"crm with free tier","clicks":4,"impressions":210,"ctr":0.019,"position":11.4}],"min_impressions":10}' \
  --json \
  --user-agent apify-awesome-skills/apify-search-console-ai-overview \
  2>/dev/null
```

Read the rows back later, for example from a scheduled run:

```bash
apify datasets get-items <DATASET_ID> --format json --user-agent apify-awesome-skills/apify-search-console-ai-overview 2>/dev/null
```

Every call carries the three flags this repo expects: `--json` (or `--format json`), `--user-agent apify-awesome-skills/apify-search-console-ai-overview`, and `2>/dev/null`.

## Run it from Claude or another AI agent (MCP)

The Actor is MCP-ready. Add the hosted server URL:

`https://mcp.apify.com/?tools=actors,docs,johnvc/ai-overview-rewrite-queue`

Then ask, for example: "Here is my Search Console CSV for example.com. Build the rewrite queue and show me the tier A pages first." MCP setup docs: https://docs.apify.com/platform/integrations/mcp

## Workflow

1. Export the Queries report. In Search Console, open Performance, set the date range and property, and export the Queries table as CSV (query, clicks, impressions, ctr, position). Host it and pass `search_console_csv_url`, or paste the rows into `search_console_rows`.
2. Set `target_domains`. List every property you count as "yours" (apex plus subdomains you own). The Actor compares these against the AI Overview's cited domains to decide cited versus competitor_cited.
3. Set `min_impressions` to trim noise. The default is 10; raise it on a long export so you score the queries that actually carry traffic and keep the child citation cost down.
4. Estimate the cost for both Actors and confirm. Query count drives the bill on both sides. See `references/gotchas.md` and set a run budget.
5. Run, then work the queue top down. Start with tier A (competitor cited, you rank 5 to 20), then tier B (you rank 1 to 4). Use `tier_reason`, `position`, and `reference_domains` to brief the rewrite.
6. Re-run after you ship rewrites to confirm the tier moved (A to B to cited).

## Inputs

- `target_domains` (array, required): the domains you own; used to classify cited versus competitor_cited.
- `search_console_csv_url` (string): URL to a Search Console Queries CSV. The three query sources are **additive, not exclusive** — send the CSV, the inline rows and the extra `queries` together if you want, and a query appearing in more than one is checked and billed once.
- `search_console_rows` (array): inline rows of {query, clicks, impressions, ctr, position}. Preserves the join fields.
- `queries` (array): a bare query list when you have no Search Console metrics; those rows come back `join_status: check_only` and land in tier X, but still get a citation check — and still bill. `join_status` is one of `matched` (the query is in your Search Console export and was checked), `check_only` (checked but not present in the export) or `gsc_only`. There is no `unmatched` value; a filter on one would return nothing.
- `min_impressions` (int, default 10): drop queries below this impression floor before scoring.
- `gl` (string, default us) and `hl` (string, default en): market targeting for the citation check.
- `location` (string): optional named location for local-intent queries.

## Cost

Two Actors bill on one run. This Actor charges a per-run setup fee plus a per-scored-query fee; the citation half runs the sibling `johnvc/google-ai-overview-api`, whose run bills your own account separately (a setup fee plus a per-retrieval fee, one or two retrievals per query). So the query count drives the bill on both sides. Keep query counts modest, raise `min_impressions`, and set a run budget. Worked numbers and the exact per-event prices are in `references/gotchas.md`.

## Honest limits

- Join rate. Search Console anonymizes long-tail queries, so a long-tail export will not fully match; expect roughly 30 to 60 percent of a long-tail list to join. Queries that do not join are labelled `check_only`, land in tier X and are kept, never dropped, so the gap is visible.
- AI Overviews are not deterministic. The cited set can shift between identical runs, so treat a single tier A as a candidate and confirm over a couple of runs before a big rewrite.
- The CTR baseline in tier C is computed from your own rows in the same export — queries with no AI Overview at a comparable position — not from that query's history and not from an industry number. The Actor says so in `tier_reason` when the baseline is missing.
- The queue tells you which pages to rewrite and why; the rewrite itself is your call.
- Point-in-time, not a live feed: `fetched_at` timestamps each row.

## Troubleshooting

- Everything lands in tier X: the join is not matching. Check that `query` values in your CSV match live queries, that `target_domains` is set, and that `min_impressions` is not filtering everything out.
- Few or no tier A rows: either you already rank 1 to 4 (look at tier B) or few overviews cite competitors in your space; lower `min_impressions` to widen the set, or confirm `gl` matches your market.
- Whole run shows `ai_overview_present` false: keep `hl` at en, try `gl` at us, and check the queries actually trigger overviews.
- Cost higher than expected: the child citation checks dominate; cut the query count or raise `min_impressions`, and set a run budget.

See `references/gotchas.md` for cost guardrails and error recovery, and `references/actor-index.md` for the Actor routing table.

## Related answer-engine Actors

- Google AI Overview API (the citation engine this Actor composes, and a standalone check): https://apify.com/johnvc/Google-AI-Overview-API?fpr=9n7kx3&fp_sid=awesomeskills
- Bing Copilot API: https://apify.com/johnvc/bing-copilot-api?fpr=9n7kx3&fp_sid=awesomeskills
- Brave AI Mode API: https://apify.com/johnvc/brave-ai-mode-api?fpr=9n7kx3&fp_sid=awesomeskills
