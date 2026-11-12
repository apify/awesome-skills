---
name: apify-actor-idea-validator
description: >
  Check whether a planned Apify Actor is worth building before writing code.
  The user describes the Actor; the skill measures demand (Google Ads search
  volume and CPC for "<site> scraper / api / mcp / data" keywords, plus the
  target site's Similarweb traffic), checks for an official API, counts
  competing Actors on the Apify Store, then digs into competitors in
  proportion to how crowded the niche is: input-schema powerup coverage and
  pricing, issue-queue and run-failure quality audit, and n8n template
  demand. Ends with a Markdown report answering: is there demand, is there
  room against competition, and which value-added features would make the
  Actor stand out. Use when the user asks to "check the potential of an
  Actor idea", "validate an Actor idea", "should I build an Actor for
  <site>", "is there demand for a <site> scraper", "is it worth building a
  <site> API or MCP on Apify", or describes a planned Actor and asks whether
  it makes sense. Requires Apify CLI or Apify MCP server.
author: Fabian Maume
author_url: https://github.com/fmaume
metadata:
  category: market-research
  keywords: "actor-idea, validation, market-research, demand, search-volume, similarweb, competition, apify-store, powerups, quality-audit, n8n, go-no-go, actor-development"
---

# Apify Actor Idea Validator

Turn a description of a planned Actor into a go / no-go recommendation backed by three answers:

1. **Is there demand?** Search volume for the keywords people use to find this kind of tool, plus traffic on the target site.
2. **Is there room against competition?** An official API check, how many Actors already cover it, how big they are, and how reliable they are.
3. **What should we build to stand out?** Value-added features backed by evidence: uncovered powerups, recurring issues and run failures, n8n workflows, keyword intent.

The skill is standalone. The three research modules it calls live in `references/` and are run inline, not as separate skills.

## Example prompts

Prompts this skill handles:

- "Is there potential for a Quora scraper?"
- "I want to build an Actor that scrapes XING profiles, companies and jobs for DACH lead gen. Does it make sense?"
- "Check the potential of an Actor that ranks the top writers in a Quora topic."

Out of scope (the boundary):

- "Audit the issues on my existing Actor" or "scrape these 500 URLs for me". This skill evaluates an idea; it doesn't run production scrapes or review a single published Actor in depth.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)
- Apify CLI v1.5.0+ (`npm install -g apify-cli`), or the Apify MCP server
- `curl` for the public, unauthenticated Apify Store, issues and n8n endpoints

**Typical cost per run:** about USD 0.30–0.40 in Actor charges. That covers the keyword lookup (USD 0.19 fixed fee + about USD 0.01 per keyword with data), Similarweb (about USD 0.014) and, when run, the n8n template scraper (a few cents). Store, issue and run-health lookups are free public endpoints.

## Output

All reports go to `~/apify-reports/` (flat folder, created if missing), never into the working directory or the skill folder:

| File | When |
|---|---|
| `apify-actor-idea-<slug>-<YYYY-MM-DD>.md` | Always: the verdict report |
| `apify-market-research-<slug>.md` | When market research runs |
| `apify-actor-quality-audit-<slug>-<YYYY-MM-DD>.md` | When the quality audit runs |
| `<top-competitor-slug>-n8n-scout.md` | When the n8n scout runs |

Templates for all four are in [references/report-templates.md](references/report-templates.md). In chat, give the verdict, the three one-line answers and the paths. Don't paste the report.

## Workflow

### Step 1 — Understand the idea

The user must describe the planned Actor. If there's no description, ask for one in one line and stop. Extract:

| Field | Example |
|---|---|
| `domain`: target site(s) | `zillow.com` |
| `brand`: how people name the site in search | `zillow` |
| `data_types`: what is extracted | listings, agents, price history |
| `actor_type`: scraper / API wrapper / MCP server / enrichment / automation | scraper |
| `audience` | real-estate investors, proptech |
| `market`: country / language of the site's users | US/en (default); DE/de for xing.com |

If no site is named ("an Actor that finds podcast guests"), use the core noun phrase as `brand` and skip Step 4.

### Step 2 — Build the keyword set

Start from `<brand> scraper`, `<brand> api`, `<brand> mcp`, `<brand> data`. Add 4–11 variants from [references/keyword-patterns.md](references/keyword-patterns.md) that fit `data_types`, `actor_type` and `audience`. Cap at 15 short phrases of 2–4 words (full questions return no volume). For a job-to-be-done idea (e.g. "top writers in a topic"), include a few use-case terms ("expert finder", "influencer discovery"), because demand often sits there rather than on the site name.

Show the list and the proposed market to the user and let them edit it before the paid call.

### Step 3 — Demand: search volume

```bash
apify actors call steadyfetch/keyword-search-volume-scraper \
  --input '{"keywords": ["zillow scraper", "zillow api", "zillow mcp", "zillow data"], "country": "US", "language": "en", "mode": "metrics-only"}' \
  --user-agent apify-awesome-skills/apify-actor-idea-validator \
  --json 2>/dev/null
```

Read the run's `defaultDatasetId`, then:

```bash
apify datasets get-items DATASET_ID --format json \
  --user-agent apify-awesome-skills/apify-actor-idea-validator 2>/dev/null
```

Per row:
- Use rows with `status: "delivered"` (`avgMonthlySearches`, `cpcUsd`, `competition`, `competitionIndex`, `lowTopOfPageBidUsd`, `highTopOfPageBidUsd`, `trendDirection`).
- `nothing_found` counts as **0 volume**. That's a real signal, not an error.
- `plan_limit_reached` or `try_again` means "no data". Tell the user, and don't count it as 0.
- Skip the `_summary` / `run_summary` row except to note cost.

**Keyword difficulty** = Google Ads `competitionIndex` + CPC. Label it **paid-search competition** in the report, not SEO difficulty. High CPC on `<brand> api` / `<brand> data`, or on use-case terms, means buyers with budget.

Compute `total_volume` and note the dominant intent bucket: scraper, API, MCP, data, or use case.

### Step 4 — Demand: site traffic (run in parallel with Step 3)

```bash
apify actors call tri_angle/similarweb-scraper \
  --input '{"websites": ["zillow.com"]}' \
  --user-agent apify-awesome-skills/apify-actor-idea-validator \
  --json 2>/dev/null
```

From the dataset item, record `totalVisits`, `globalRank`, `topCountries`, `trafficSources` and `snapshotDate`. If there's no data (small site), record that and gate on search volume only.

### Step 5 — Demand gate

Demand is **promising** if `total_volume` ≥ 500/month **or** monthly visits ≥ 10,000. If it's below both, show the numbers and ask whether to stop (verdict **Don't build: weak demand**, demand section only) or continue (the verdict must still mention the weak demand).

### Step 5b — Official API check

An official API is a competitor in its own right.

1. Search for `"<brand> api"`, `"<brand> api pricing"` and `"<brand> developer api"`. Use the agent's own web search tool if it has one; otherwise:
   ```bash
   apify actors call apify/google-search-scraper \
     --input '{"queries": "zillow api\nzillow api pricing\nzillow developer api", "maxPagesPerQuery": 1}' \
     --user-agent apify-awesome-skills/apify-actor-idea-validator \
     --json 2>/dev/null
   ```
2. Keep only results on the site's own domain or developer portal. Ignore third-party scrapers, "unofficial API" wrappers and RapidAPI listings.
3. Read the official docs and pricing page (web fetch tool, or `apify/rag-web-browser`).
4. Classify `api_status` and act on it:

| `api_status` | Meaning | Effect |
|---|---|---|
| `none` | No official data API (login / share plugins or ads APIs don't count) | Normal buckets |
| `free-unlimited` | Free, no meaningful quota, covers the planned data | Ask: stop (**Don't build: free official API**) or continue |
| `free-rate-limited` | Free with quota or rate limit | Halve the buckets |
| `paid` | Paid plan or per-call fee | Halve the buckets |
| `partner-only` | Approval or partnership needed, or it covers only a small part of the planned data | Halve the buckets |

Halved buckets: `<1 / 1–2 / 3–5 / >5` instead of `<2 / 2–5 / 6–10 / >10`.

### Step 6 — Count competing Actors

```bash
apify actors search "zillow" --json --limit 10 \
  --user-agent apify-awesome-skills/apify-actor-idea-validator 2>/dev/null
```

`actors search` caps at 10 results. When it returns 10, list the full set from the public Store API (no token needed):

```bash
curl -s "https://api.apify.com/v2/store?search=zillow&limit=100"
```

Dedupe on `username/name`. **Keep only Actors that actually target the domain.** Their title or name must mention the brand. Watch for substring false matches (e.g. "xing" also matches "Douyin Xingtu"). Store search also matches README text, so raw counts overstate competition.

If the site hosts several distinct products (e.g. XING jobs vs. members and companies), split the count by segment. A crowded jobs segment can sit next to an empty lead-gen segment.

Record per Actor: MAU (`stats.totalUsers30Days`), total users, rating, pricing and last modified. Compute `competitor_count`, leader share (top MAU ÷ total MAU), Apify-owned Actors (`apify`, `clockworks`, `compass`) and stale Actors (> 6 months).

### Step 7 — Route by competition

| Normal buckets | Halved buckets | Run |
|---|---|---|
| **< 2** | **0** | Nothing extra. Good candidate; derive features from the description and keyword intent. |
| **2–5** | **1–2** | [Market research](references/market-research.md) |
| **6–10** | **3–5** | [Market research](references/market-research.md) + [quality audit](references/quality-audit.md) + [n8n scout](references/n8n-scout.md) |
| **> 10** | **> 5** | [Quality audit](references/quality-audit.md) first, then ask whether to also run market research and/or the n8n scout |

Run the modules one after another and extract:

- **Market research:**
  - Powerups covered by 0–1 Actors (gaps), and high-MAU powerups covered by few Actors.
  - **Pricing:** normalise each competitor to USD per 1,000 results. If **every** priced competitor is above **USD 10 per 1k**, add "Undercut on price" as a differentiation item.
- **Quality audit:**
  - Recurring bug clusters ("market pain points") and recurring feature requests ("potential powerups").
  - Run health: failure and abort rates. A high-MAU Actor with a high failure rate is an opening for a reliable alternative.
- **n8n scout:**
  - The LLM steps users bolt onto scrapers (power-ups), high-view templates built on competitor scrapers (replica angles), and empty niches.

If the user has already validated a related idea today (same domain), reuse its traffic, API and competitor data rather than paying for it again. Say so in Methodology.

### Step 8 — Verdict and report

- **Build:** demand is promising and `competitor_count` is below the first bucket, or competitors are weak (stale, low-rated, buggy) with no clear leader.
- **Build with differentiation:** demand is promising, competition exists, and there are concrete gaps (uncovered powerups, pain points, an unserved intent such as API or MCP with real volume, an empty segment).
- **Don't build:** weak demand (user stopped at Step 5), a free unlimited official API (user stopped at Step 5b), or a crowded niche with a strong, well-maintained leader and no gap with evidence.

**Differentiation ranking:**
- Rank value-added features above price. List "Undercut on price" (only when triggered) **last**, with this note: *price differentiation is less effective than value-added differentiation. Competitors can match a price cut in minutes, while a missing capability takes them a build cycle.*
- Suggest a pricing unit that matches the value (per company lead, per ranked writer) when the value is in aggregation.

Write the report using [references/report-templates.md](references/report-templates.md).

### Step 9 — Chat close-out

> **Verdict: …**
> - **Demand:** one line
> - **Official API:** one line
> - **Competition:** one line
> - **Differentiate with:** top 2–3 features
>
> Reports: absolute paths

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Keyword search volume, CPC, Ads competition | `steadyfetch/keyword-search-volume-scraper` | community | Step 3 demand |
| Site traffic, rank, countries, sources | `tri_angle/similarweb-scraper` | community | Step 4 demand |
| Official API discovery | `apify/google-search-scraper` | apify | Step 5b (when the agent has no web search) |
| Read API docs / pricing pages | `apify/rag-web-browser` | apify | Step 5b (when the agent has no web fetch) |
| n8n template library search | `advantageous_subcontra/n8n-template-scraper` | community | n8n scout module |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling Actors — choose your interface

**Option A: Apify CLI (recommended).** Every call carries `--user-agent apify-awesome-skills/apify-actor-idea-validator`, `--json` (or `--format json` for `datasets get-items`) and `2>/dev/null`, as in the examples above. Fetch an input schema before building any input not shown here:

```bash
apify actors info "steadyfetch/keyword-search-volume-scraper" --input --json \
  --user-agent apify-awesome-skills/apify-actor-idea-validator 2>/dev/null
```

**Option B: Apify MCP server** ([mcp.apify.com](https://mcp.apify.com)). Use `search-actors`, `fetch-actor-details` (parameter `actor:`, not `actorId:`), `call-actor` and `get-dataset-items` with the same inputs.

Public read-only endpoints used with plain `curl` (no token, no auth header):
- Store listing: `https://api.apify.com/v2/store?search=<kw>&limit=100`
- Actor stats: `https://api.apify.com/v2/acts/<username>~<name>`
- Actor issues: `https://apify.com/api/actor-issues/data?actorId=<id>&statusOrName=open|closed`
- n8n template details: `https://api.n8n.io/api/templates/workflows/<id>`

Never put an Apify token in a URL query string. If an authenticated REST call is ever needed, use the `Authorization: Bearer` header.

## Troubleshooting

- **`plan_limit_reached` on the volume Actor:** the free Apify plan allows one fresh keyword lookup per day. Continue on Similarweb data only, or rerun after 00:00 UTC. Rerunning keywords already fetched in the last 30 days is free.
- **All Actors show 0 issues:** you read `body.list` instead of `body.json.list`. See [references/quality-audit.md](references/quality-audit.md).
- **Store API returns stats for only some Actors:** parallel bursts get throttled. Retry sequentially, or mark tiny Actors as "no stats".
- **n8n results full of unrelated templates:** competitor-name keywords pull in off-topic hits. Apply the relevance filter in [references/n8n-scout.md](references/n8n-scout.md).
- For cost guardrails and more recovery steps, see [references/gotchas.md](references/gotchas.md).
