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

If CLI is unavailable and Apify MCP server is connected, use MCP `call-actor` / `fetch-actor-details` directly. If neither is available, install and authenticate the CLI first.

## Authentication

If a CLI command fails with an auth error, authenticate using one of these methods:

1. **OAuth (interactive):** `apify login` (opens browser)
2. **Environment variable:** `export APIFY_TOKEN=your_token_here`
3. **From .env file:** `source .env` (if the file contains `APIFY_TOKEN=...`)

Generate token: https://console.apify.com/settings/integrations

## Actor Registry

Run `apify actors info "ACTOR_ID" --user-agent apify-agent-skills/apify-easy-competitive-intelligence --input --json 2>/dev/null` to verify input schema before calling any actor for the first time in a session. Full input/output schemas with sample data: `reference/actor-schemas.md`.

| Data Need | Actor | Verified Input | Notes |
|---|---|---|---|
| **Google SERP** | `apify/google-search-scraper` | `{ "queries": "...", "maxPagesPerQuery": 1 }` | Supports country/language. SERP snippets contain ratings & review counts |
| **Page scrape** | `apify/website-content-crawler` | `{ "startUrls": [{"url": "..."}], "proxyConfiguration": {"useApifyProxy": true} }` | **proxyConfiguration REQUIRED**. Returns markdown |
| **RAG browse** | `apify/rag-web-browser` | `{ "query": "..." }` | Search + scrape in one call. Good fallback |
| **LinkedIn company** | `dev_fusion/Linkedin-Company-Scraper` | `{ "profileUrls": ["..."] }` | ⚠️ `profileUrls` not `urls`. Output in KV store |
| **LinkedIn jobs** | `curious_coder/linkedin-jobs-scraper` | `{ "urls": ["https://www.linkedin.com/jobs/search/?keywords=COMPANY&position=1&pageNum=0"], "count": 10, "scrapeCompany": true }` | **Requires LinkedIn search URL, NOT keywords.** `count` min = 10 |
| **Crunchbase** | `pratikdani/crunchbase-companies-scraper` | `{ "url": "..." }` | ⚠️ `url` (string), NOT `urls` (array) |
| **Amazon product** | `junglee/Amazon-crawler` | `{ "categoryOrProductUrls": [{"url": "..."}] }` | ⚠️ `categoryOrProductUrls`, NOT `productUrls` |
| **Amazon reviews** | `web_wanderer/amazon-reviews-extractor` | `{ "products": ["..."] }` | ⚠️ `products`, NOT `productUrls` |
| **Walmart product** | `e-commerce/walmart-product-detail-scraper` | `{ "productUrls": ["..."] }` | May return empty |
| **Google Maps reviews** | `compass/Google-Maps-Reviews-Scraper` | `{ "startUrls": [{"url": "..."}], "maxReviews": 30 }` | Use full Google Maps place URL |
| **G2 reviews** | `automation-lab/g2-scraper` | `{ "startUrls": [{"url": "..."}], "maxReviews": 10 }` | NPS, ratings, switching data. $0.04/run |
| **Capterra reviews** | `zen-studio/capterra-reviews-scraper` | `{ "productUrl": "...", "maxReviews": 10 }` | ⚠️ `productUrl` (string), NOT `startUrls`. $1.99/1K |
| **Gartner Peer Insights** | — | No working actor | All tested actors return empty. Use SERP snippet mining as fallback |
| **Glassdoor** | `memo23/glassdoor-scraper-ppr` | `{ "startUrls": [{"url": "..."}] }` | Reviews, salaries, culture, ratings |
| **Reddit** | `harshmaur/reddit-scraper` | `{ "startUrls": [{"url": "..."}], "maxItems": 10 }` | Posts + full comment threads |
| **Google Play reviews** | `neatrat/google-play-store-reviews-scraper` | `{ "appIdOrUrl": "com.company.app" }` | ⚠️ `appIdOrUrl`, NOT `appId` |
| **App Store** | `jdtpnjtp/apple-app-store-scraper` | `fetch-actor-details` first | ⚠️ Requires SHADER proxy — may not be available on all plans |
| **SimilarWeb** | `pro100chok/similarweb-scraper` | `{ "searchType": "similarweb", "domains": ["example.com"] }` | **searchType REQUIRED**. Empty for small sites |
| **Google News** | `data_xplorer/google-news-scraper-fast` | `{ "keywords": ["..."], "maxArticles": 10, "timeframe": "7d", "region_language": "US:en", "decodeUrls": true, "extractDescriptions": true, "extractImages": false }` | $1/1K. Multi-keyword, full text, resolved URLs |
| **Wayback Machine** | `andok/wayback-machine-scraper` | `{ "url": "..." }` | No `maxSnapshots` param |

## Core Workflow

### Step 0: Understand the User (once, at start)

Clarify before gathering data:
- **Role** — Analyzed company, competitor, investor, consultant?
- **Decision** — Entering market, defending position, choosing vendor, building battlecard?
- **Autonomy** — Checkpoints after initial findings, or autopilot?

### Steps 1–7

1. **Clarify scope** — Identify competitors. Select module(s). Default geography: US.
2. **Fetch actor schemas** — Run `fetch-actor-details` for each actor planned for use. Skip re-fetching within the same session.
3. **Read module reference** — Load `reference/modules/<module>.md` for gathering + analysis instructions.
4. **Gather live data** — Parallelize independent `call-actor` calls.
5. **Checkpoint** (if not autopilot) — Present first findings, confirm direction.
6. **Analyze** — Select framework, lead with narrative, support with tables.
7. **Verify & deliver** — Run pre-delivery verification (`reference/verification-checklist.md`). End with strategic recommendations framed for the user's role.

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
- **Failures** — Report failures, try fallback (`rag-web-browser`). Never hallucinate data.
- **Cite everything** — Include source URLs for every data point.
- **Async for long runs** — Set `async: true` for actors >30s, poll with `get-actor-run`.
- **Protected platforms** — Do NOT use `website-content-crawler` or `rag-web-browser` for: g2.com, capterra.com, gartner.com, glassdoor.com, reddit.com, linkedin.com. Use dedicated actors.

### Apify vs. WebSearch

**Apify required**: review sites (G2, Capterra, Gartner, Glassdoor), LinkedIn, Reddit, Amazon, Walmart, app stores, SimilarWeb, Crunchbase, Wayback Machine, Google Maps reviews, news (Google News actor).

**WebSearch/WebFetch sufficient** (Claude Code built-in tools): competitor discovery, general company info, blog posts, publicly accessible pricing pages.

## Data Validation & Grounding

- **Every factual claim needs a source URL.** No link = not a fact.
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

## Pre-delivery Verification

Every report undergoes mandatory verification before delivery. Full checklist: `reference/verification-checklist.md`. Core principle: **every factual claim must have a source URL. No exceptions. No inferences presented as facts.**
