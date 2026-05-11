---
name: apify-easy-competitive-intelligence
description: >
  This skill should be used when the user asks to "analyze a competitor",
  "compare pricing", "competitive landscape", "market research",
  "what do customers think", "review intelligence", "hiring signals",
  "content strategy", "SEO battle", "build a battlecard", "competitive analysis",
  "who are the players", "who competes with", "market intelligence",
  "competitive positioning", "deep dive on a company", "board prep",
  "SWOT analysis", "how does [X] compare to [Y]",
  or mentions competitor analysis, pricing comparison, customer sentiment,
  or market landscape research. Requires Apify CLI or Apify MCP server.
---

# Competitive Intelligence

Real-time competitive intelligence powered by live web data via Apify actors. **Never answer competitive questions from training knowledge alone.** Always gather live data first, then analyze.

## Prerequisites

- Apify CLI v1.5.0+ (`npm install -g apify-cli`), or Apify MCP server
- Authenticated session (`apify login` or `APIFY_TOKEN` env var)

**CLI rules:** Always pass `--json`, `--user-agent apify-agent-skills/apify-easy-competitive-intelligence`, and `2>/dev/null`.
- **Run actor:** `apify actors call "ACTOR_ID" -i 'INPUT' --json 2>/dev/null` → returns run metadata with `defaultDatasetId`
- **Fetch results:** `apify datasets get-items DATASET_ID --format json > /tmp/results.json 2>/dev/null` — save locally, parse from file:
  - Quick extraction: `jq '.[] | "\(.field1) | \(.field2)"' /tmp/results.json`
  - Aggregation: `python3 -c "import json; d=json.load(open('/tmp/results.json')); ..."`
  - Tabular: `--format csv > /tmp/results.csv` + `python3` with `csv.DictReader`
  - Flags: `--limit N`, `--offset N`, `--format json|jsonl|csv|xlsx|xml`
  - Output fields: `apify datasets info DATASET_ID --json | jq .fields`
- **Fetch schema:** `apify actors info "ACTOR_ID" --input --json 2>/dev/null`

If CLI is unavailable and Apify MCP server is connected, use MCP `call-actor` / `fetch-actor-details` / `get-actor-output` directly.

## Authentication

If a CLI command fails with an auth error, authenticate using one of these methods:

1. **OAuth (interactive):** `apify login` (opens browser)
2. **Environment variable:** `export APIFY_TOKEN=your_token_here`
3. **From .env file:** `source .env` (if the file contains `APIFY_TOKEN=...`)

Generate token: https://console.apify.com/settings/integrations

## Actor Registry

Every actor call follows three steps:
1. **Read** — find the actor's section in `reference/actor-schemas.md`. Use the exact verified input and follow the "How to find" instructions for URLs/slugs.
2. **Discover** — verify platform URLs and slugs (e.g. via SERP) as described in the actor's schema section. Do not guess — wrong slugs silently return empty or wrong data.
3. **Run** — call the actor with verified input.

Alternatively, fetch the live schema: `apify actors info "ACTOR_ID" --user-agent apify-agent-skills/apify-easy-competitive-intelligence --input --json 2>/dev/null`

| Data Need | Actor | Notes |
|---|---|---|
| **Google SERP** | `apify/google-search-scraper` | Supports country/language. SERP snippets contain ratings & review counts |
| **Page scrape** | `apify/website-content-crawler` | proxyConfiguration REQUIRED. Returns markdown |
| **RAG browse** | `apify/rag-web-browser` | Search + scrape in one call. Good fallback |
| **LinkedIn company** | `dev_fusion/Linkedin-Company-Scraper` | Output in KV store, not dataset |
| **LinkedIn jobs** | `curious_coder/linkedin-jobs-scraper` | Requires LinkedIn search URL, NOT keywords |
| **Crunchbase** | `pratikdani/crunchbase-companies-scraper` | Single company URL per call |
| **Amazon product** | `junglee/Amazon-crawler` | Product or category URLs |
| **Amazon reviews** | `web_wanderer/amazon-reviews-extractor` | May return 0 for some products |
| **Walmart product** | `e-commerce/walmart-product-detail-scraper` | May return empty |
| **Google Maps reviews** | `compass/Google-Maps-Reviews-Scraper` | Use full Google Maps place URL |
| **G2 reviews** | `automation-lab/g2-scraper` | NPS, ratings, switching data. $0.04/run |
| **Capterra reviews** | `zen-studio/capterra-reviews-scraper` | $1.99/1K |
| **Gartner Peer Insights** | — | No working actor. Use SERP snippet mining as fallback |
| **Glassdoor** | `memo23/glassdoor-scraper-ppr` | Reviews, salaries, culture, ratings |
| **Reddit** | `harshmaur/reddit-scraper` | Posts + full comment threads |
| **Google Play reviews** | `neatrat/google-play-store-reviews-scraper` | App ID or Play Store URL |
| **App Store** | `jdtpnjtp/apple-app-store-scraper` | Requires SHADER proxy — may not be available on all plans |
| **SimilarWeb** | `pro100chok/similarweb-scraper` | Minimum 10 domains per call |
| **Google News** | `data_xplorer/google-news-scraper-fast` | No boolean operators in keywords |
| **Wayback Machine** | `andok/wayback-machine-scraper` | Full URL including path |

## Core Workflow

### Step 0: Understand the User (once, at start)

Clarify before gathering data:
- **Role** — Analyzed company, competitor, investor, consultant?
- **Decision** — Entering market, defending position, choosing vendor, building battlecard?
- **Autonomy** — Checkpoints after initial findings, or autopilot?

### Steps 1–7

1. **Clarify scope** — Identify competitors. Select module(s). Default geography: US.
2. **Read module reference** — Load `reference/modules/<module>.md` for gathering + analysis instructions.
3. **Gather live data** — For each actor call, follow the three-step pattern: **Read** (actor-schemas.md) → **Discover** (SERP for URLs) → **Run** (call actor). Use PRIMARILY actors from the Actor Registry above.
4. **Checkpoint** (if not autopilot) — Present first findings, confirm direction.
5. **Analyze** — Select framework, lead with narrative, support with tables.
6. **Verify** — Run pre-delivery verification (`reference/verification-checklist.md`). Check: every claim has a source URL, every major finding has a confidence label, inferences are labeled as such. Remove any ungrounded claims.
7. **Deliver** — End with strategic recommendations framed for the user's role.

### Framework Selection

| Situation | Framework |
|---|---|
| Profile one competitor | SWOT |
| Market dynamics & forces | Porter's Five Forces |
| Visual position comparison | Strategy Canvas (Blue Ocean) |
| Why customers switch | Jobs-to-be-Done |
| Find white space | Positioning Matrix (2x2) |
| Predict competitor reaction | Competitive Response Matrix |

## Data Collection Rules

- **Prefer structured actors** over `website-content-crawler` when a dedicated actor exists.
- **Cost budget** — 3-8 actor calls per snapshot. Track total, warn at 15+.
- **Parallelize** independent `call-actor` calls in a single response.
- **Failures** — Report every failure explicitly (actor, input, error). Retry with corrected input if the cause is obvious. If retry fails, try `rag-web-browser` as fallback. Never silently skip a failed data source.
- **Cite everything** — Include source URLs for every data point.
- **Async for long runs** — Set `async: true` for actors >30s, poll with `get-actor-run`.
- **Protected platforms** — Do NOT use `website-content-crawler` or `rag-web-browser` for: g2.com, capterra.com, gartner.com, glassdoor.com, reddit.com, linkedin.com. Use dedicated actors.

### Apify vs. WebSearch

**Apify required**: review sites (G2, Capterra, Gartner, Glassdoor), LinkedIn, Reddit, Amazon, Walmart, app stores, SimilarWeb, Crunchbase, Wayback Machine, Google Maps reviews, news (Google News actor).

**WebSearch/WebFetch sufficient** (Claude Code built-in tools): competitor discovery, general company info, blog posts, publicly accessible pricing pages.

## Data Validation & Grounding

- **Every factual claim needs a source URL.** No link = not a fact.
- **Confidence labels are mandatory.** Mark every major finding: **High** (primary source), **Medium** (2+ third-party sources), **Low** (single third-party source). Format: `[Confidence | Source]`. No report without labels.
- **Data tiers**: Verified (primary source) → Reported (third-party, attribute) → Inferred (label as "this suggests...") → Ungrounded (omit).
- **Numbers are dangerous** — employee counts, revenue, funding change fast. Always cite source and date.
- **Empty results ARE intelligence** — 0 jobs = not hiring, 0 SimilarWeb = small site, 12 reviews = low adoption.
- **Cross-reference** — Single-source claims are unverified. Multi-source (G2 + Capterra + Reddit) = pattern.

## Module Selection

| User says... | Module | Reference |
|---|---|---|
| "Analyze [competitor]", "Tell me about [company]" | Competitor Snapshot | `reference/modules/competitor-snapshot.md` |
| "Compare pricing", "How much does [X] cost" | Pricing Intelligence | `reference/modules/pricing-intelligence.md` |
| "Pricing details", "per-use-case costs", "tiers", "add-ons" | Pricing Deep Dive | `reference/modules/pricing-deep-dive.md` |
| "What do customers think", "Reviews", "Pain points" | Review Intelligence | `reference/modules/review-intelligence.md` |
| "What are they hiring for", "Job postings" | Hiring Signals | `reference/modules/hiring-signals.md` |
| "How do they rank", "Content strategy", "SEO" | Content & SEO | `reference/modules/content-seo.md` |
| "Who are the players", "Market landscape" | Market Landscape | `reference/modules/market-landscape.md` |
| "Full battlecard", "Deep analysis", "Board prep" | Multi-Module | `reference/multi-module-playbook.md` |