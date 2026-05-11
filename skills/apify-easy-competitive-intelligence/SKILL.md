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

**CLI rules:** Always pass `--json`, `--user-agent apify-agent-skills/apify-easy-competitive-intelligence`, and `2>/dev/null`. Module references use shorthand — translate to CLI:
- `call-actor: ACTOR_ID` → `apify actors call "ACTOR_ID" -i 'INPUT' ...`
- `fetch-actor-details` → `apify actors info "ACTOR_ID" --input ...`

If CLI is unavailable and Apify MCP server is connected, use MCP `call-actor` / `fetch-actor-details` directly. If neither is available, install and authenticate the CLI first.

## Authentication

If a CLI command fails with an auth error, authenticate using one of these methods:

1. **OAuth (interactive):** `apify login` (opens browser)
2. **Environment variable:** `export APIFY_TOKEN=your_token_here`
3. **From .env file:** `source .env` (if the file contains `APIFY_TOKEN=...`)

Generate token: https://console.apify.com/settings/integrations

## Actor Registry

The table below lists actor IDs and minimal verified inputs. **Before calling any actor, read its section in `reference/actor-schemas.md`** — it contains:
- **How to find/verify the URL** (most actors need a platform-specific URL that must be discovered via SERP first — do not guess slugs)
- **Full input parameters** with required fields, gotchas, and valid values
- **Output keys** for parsing results

Alternatively, fetch the live schema: `apify actors info "ACTOR_ID" --user-agent apify-agent-skills/apify-easy-competitive-intelligence --input --json 2>/dev/null`

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
| **SimilarWeb** | `pro100chok/similarweb-scraper` | `{ "searchType": "similarweb", "domains": ["dom1.com", ... ] }` | **searchType REQUIRED. Minimum 10 domains.** Batch all competitors in one call |
| **Google News** | `data_xplorer/google-news-scraper-fast` | `{ "keywords": ["..."], "maxArticles": 10, "timeframe": "7d", "region_language": "US:en", "decodeUrls": true, "extractDescriptions": true, "extractImages": false }` | $1/1K. **timeframe: only `1h`, `1d`, `7d`, `1y`, `all`**. No boolean operators in keywords |
| **Wayback Machine** | `andok/wayback-machine-scraper` | `{ "url": "..." }` | No `maxSnapshots` param |

## Core Workflow

### Step 0: Understand the User (once, at start)

Clarify before gathering data:
- **Role** — Analyzed company, competitor, investor, consultant?
- **Decision** — Entering market, defending position, choosing vendor, building battlecard?
- **Autonomy** — Checkpoints after initial findings, or autopilot?

### Steps 1–7

1. **Clarify scope** — Identify competitors. Select module(s). Default geography: US.
2. **Fetch actor schemas** — Read `reference/actor-schemas.md` for each actor planned for use. Verify URLs via SERP before calling (do not guess platform slugs). Optionally fetch live schema: `apify actors info "ACTOR_ID" --input --json`.
3. **Read module reference** — Load `reference/modules/<module>.md` for gathering + analysis instructions.
4. **Gather live data** — Parallelize independent `call-actor` calls. Use PRIMARILY actors from the Actor Registry above.
5. **Checkpoint** (if not autopilot) — Present first findings, confirm direction.
6. **Analyze** — Select framework, lead with narrative, support with tables.
7. **Verify** — Run pre-delivery verification (`reference/verification-checklist.md`). Check: every claim has a source URL, every major finding has a confidence label, inferences are labeled as such. Remove any ungrounded claims.
8. **Deliver** — End with strategic recommendations framed for the user's role.

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

## Pre-delivery Verification

Every report undergoes mandatory verification before delivery. Full checklist: `reference/verification-checklist.md`. Core principle: **every factual claim must have a source URL. No exceptions. No inferences presented as facts.**
