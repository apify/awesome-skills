---
name: apify-financial-news
description: Discover and extract financial news for tracked portfolio companies across 33 verified Tier 1 sources (Bloomberg, Reuters, FT, WSJ, IntelliNews, ČTK, PAP, BTA, TASR, ING Think, ECB, EC Press Corner, ...) plus broad Google News fallback. Use when the user asks to find news about a company, get press coverage, monitor financial press, run a news scan, or check headlines for a portfolio company. Reads tracked companies from data/companies.json. Do NOT use for marketing/social-listening (use apify/awesome-skills) or for morning-briefing formatting (out of scope).
---

# Financial News Intelligence

Discover and extract financial news for portfolio companies via Apify Actors. Two modes:

- **Single company** — news scan for one company.
- **Portfolio scan** — same pipeline run across multiple companies.

33 Tier 1 sources organized in 4 categories (Global / Pan-European / Institutional / CEE Local). Tier 2 = broad Google News fallback for unverified domains.

**Estimated cost**: $0.10–0.50 per single company, $1–5 per full portfolio scan.

## Prerequisites

- Apify access — preferred: `apify` CLI (`npm install -g apify-cli && apify login`); fallback: Apify MCP connector (`call-actor` tool). CLI is faster and preferred when both are available.
- Python 3 + `pip install readability-lxml lxml` (for the `extract_and_clean.py` post-processor)
- Companies data at `${CLAUDE_PLUGIN_ROOT}/data/companies.json`

`${CLAUDE_PLUGIN_ROOT}` is the plugin's root directory (where `.claude-plugin/` lives). It is resolved automatically by Claude Code when the plugin is installed, or set to the `--plugin-dir` path during development.

## Workflow checklist

Copy this and tick boxes as you progress:

```
Task Progress:
- [ ] Step 0: Verify prerequisites — try `apify --version && apify info`; if unavailable, check for `call-actor` MCP tool; if neither, tell user to install apify CLI or Apify MCP connector. Also verify: `python3 -c "from readability import Document; print('OK')"` (install: `pip install readability-lxml lxml`)
- [ ] Step 1: Build queries (look up company in data/companies.json or construct manually)
- [ ] Step 2: Discovery — pick 8-12 sources by region, run 2-phase Google News
- [ ] Step 3: Dedup + route (Tier 1 = whitelisted domain → verified extractor; Tier 2 = broad → rag-web-browser)
- [ ] Step 4: Extract & clean (run extractor, then extract_and_clean.py)
- [ ] Step 5: Output Tier 1 + Tier 2 tables to user
```

## Constraints

### Allowed Apify Actors (exhaustive — do NOT use others)

| Actor | Purpose |
|-------|---------|
| `data_xplorer/google-news-scraper-fast` | Google News discovery |
| `louvre/rss-news-aggregator` | RSS discovery |
| `rodrigo_pacelli/headline-news-scraper` | Headline discovery |
| `jamie_tran/bloomberg-article-scraper` | Bloomberg extraction |
| `romy/bloomberg-news-scraper` | Bloomberg fallback |
| `workhard3000/news-intelligence-rag-extractor` | Paywall extraction |
| `apify/rag-web-browser` | Free/soft-paywall + Tier 2 |
| `stanvanrooy6/universal-ai-web-scraper` | Hard paywall (Barron's, MarketWatch) — $0.25/page |

Do NOT use any other actor. Do NOT use WebSearch, WebFetch, or browser tools.

### Extractor routing (mandatory — do NOT substitute)

| Extractor | Domains |
|-----------|---------|
| `jamie_tran/bloomberg-article-scraper` | bloomberg.com |
| `workhard3000/news-intelligence-rag-extractor` | ft.com, wsj.com, economist.com, morningstar.com, asia.nikkei.com, caixinglobal.com, zawya.com, euobserver.com, reuters.com |
| `apify/rag-web-browser` | cnbc.com, forbes.com, investors.com, lesechos.fr, afr.com, scmp.com, euronews.com, intellinews.com, handelsblatt.com, politico.eu, eubusiness.com, eureporter.co, ecb.europa.eu, + all 7 CEE Local |
| `stanvanrooy6/universal-ai-web-scraper` | barrons.com, marketwatch.com |
| REST API (presscorner) | ec.europa.eu |

Full per-source config: [reference/SOURCE_CONFIGS.md](reference/SOURCE_CONFIGS.md). Machine-readable: [data/sources.json](data/sources.json).

## Pipeline

### Step 1: Build queries

Look up company in `${CLAUDE_PLUGIN_ROOT}/data/companies.json`. Key fields under `queries`: `gnews_en`, `gnews_cz`, `bloomberg`.

For non-portfolio companies, construct manually: quoted full legal name + ticker OR variant + geographic qualifier.

**Query rules:**
- Use `"InPost SA"` not `InPost` (quoted full names avoid false positives — see [reference/EUROPEAN_COMPANIES_GUIDE.md](reference/EUROPEAN_COMPANIES_GUIDE.md))
- Per-source `site:` operator: `site:bloomberg.com "InPost SA" OR "INPST"`
- FT tip: use `site:ft.com/content/` (bare `ft.com` returns stock-data pages)
- Valid timeframes: `"1h"`, `"1d"`, `"7d"`, `"1y"`, `"all"` (NOT `"30d"`)
- Tickers < 4 chars: always pair with full company name
- ALWAYS set `decodeUrls: true` on Google News input

### Step 2: Discovery

Do NOT search all 33 sources. Pick 8–12 based on company region.

#### Regional priorities

| Region | Priority Sources |
|--------|------------------|
| **CZ** | ČTK, IntelliNews, Reuters, Bloomberg, POLITICO EU, FT, Handelsblatt |
| **PL** | PAP, IntelliNews, Reuters, Bloomberg, POLITICO EU, FT |
| **HU** | Telex.hu, HVG.hu, VG.hu, IntelliNews, Reuters, Bloomberg |
| **BG** | BTA, IntelliNews, Reuters, Bloomberg, Euronews |
| **SK** | TASR, IntelliNews, Reuters, Bloomberg, Handelsblatt |
| **Western Europe** | Bloomberg, Reuters, FT, Handelsblatt, Les Echos, POLITICO EU |
| **US / Global** | Bloomberg, Reuters, WSJ, FT, CNBC, Forbes, Barron's |
| **Asia / MENA** | Bloomberg, Reuters, SCMP, Nikkei, Caixin, Zawya |
| **EU Regulatory** | POLITICO EU, EUobserver, EUbusiness, EU Reporter, EC Press Corner, ECB |

#### Two-phase Google News strategy

**Phase 1 — Targeted** (per priority source, with `site:`):

```bash
apify call data_xplorer/google-news-scraper-fast \
  --input '{"keywords":["site:bloomberg.com \"InPost SA\" OR \"INPST\""],"maxArticles":10,"timeframe":"7d","region_language":"US:en","decodeUrls":true,"proxyConfiguration":{"useApifyProxy":true,"apifyProxyGroups":["RESIDENTIAL"]}}' \
  --output-dataset > discovery_bloomberg.json
```

**Phase 2 — Broad** (always run, no `site:` operator). Classify results by domain in Step 3 — whitelisted → Tier 1, others → Tier 2.

**CEE local-language discovery**: For CEE companies, run additional queries with `region_language` set to `CZ:cs`, `PL:pl`, `HU:hu`, `BG:bg`, `SK:sk`. See `region_language` field per source in [data/sources.json](data/sources.json).

#### EC Press Corner — direct REST API (no Actor)

```bash
curl -s "https://ec.europa.eu/commission/presscorner/api/documents?reference=IP/26/614&language=en"
```

Parse `IP_XX_NNN` reference IDs from Google News titles to construct API calls.

#### RSS / Headline discovery (optional)

For sources with RSS, you can supplement GNews with `louvre/rss-news-aggregator` (max 10 feeds per run; split into batches). For 6 sources, `rodrigo_pacelli/headline-news-scraper` works (CNBC, SCMP, Nikkei, Caixin, Zawya tag-pages-only, Handelsblatt). RSS/headline output is unfiltered — filter client-side by company name in title/description. Full feed list: [reference/PIPELINE_DETAIL.md](reference/PIPELINE_DETAIL.md).

### Step 3: Dedup & route

1. Collect URLs from all discovery runs.
2. Classify by domain: whitelist (33 Tier 1 sources) → Tier 1; other → Tier 2.
3. Filter non-article URLs: `/quote/`, `/stock/`, `/sitemap`, `/author/`, `/tag/`, `/key-metrics/`, `/newsletters/`, `/topic/`, `/profile/`, `redirectUrl=`.
4. Filter by company name/ticker in title.
5. Deduplicate (URL normalize).
6. Route Tier 1 URLs to verified extractor per routing table.
7. Route Tier 2 URLs to `apify/rag-web-browser`.

**Low-coverage fallback** (< 3 articles): broaden timeframe to `"1y"`, run Phase 2 if skipped, try local-language queries.

### Step 4: Extract & clean

Run the extractor per the routing table. For `rag-web-browser` calls, use `outputFormats: ["html"]`.

After extraction, run `extract_and_clean.py` on the dataset to strip nav/menus/footers via readability-lxml. The script auto-detects format: HTML cleaned via readability-lxml, already-clean output (Bloomberg scraper, workhard3000) passes through.

```bash
DATASET_ID=$(apify call apify/rag-web-browser \
  --input '{"query":"<ARTICLE_URL>","maxResults":1,"outputFormats":["html"],"requestTimeoutSecs":40,"proxyConfiguration":{"useApifyProxy":true,"apifyProxyGroups":["RESIDENTIAL"]},"removeCookieWarnings":true}' \
  --json | jq -r '.defaultDatasetId')

python3 ${CLAUDE_PLUGIN_ROOT}/skills/apify-financial-news/reference/scripts/extract_and_clean.py "$DATASET_ID"
```

The `--json` flag returns run metadata including `defaultDatasetId`. Errors produce non-zero exit code so the pipeline fails fast.

### Step 5: Output

Two tables to the user — **Tier 1 (verified)** and **Tier 2 (broad)**. Per article: source, title, author, date, char count, URL.

```markdown
## News Intelligence: InPost (INPST.AS) — Last 7 days

### Tier 1 — Verified Sources (2)
| Source | Title | Author | Date | Chars | URL |
|--------|-------|--------|------|-------|-----|
| bloomberg.com | InPost Readies AI Shopping Assistant | K. Krasuski | 2026-03-19 | 7,577 | … |

### Tier 2 — Broad Discovery (5)
| Source | Title | Date | Chars | URL |
|--------|-------|------|-------|-----|
| seekingalpha.com | InPost expands parcel locker network | 2026-03-18 | 1,200 | … |

*Sources: 6 verified queried | 5 broad | Cost: $0.15*
```

## Macro context

For country-level economic context, use these alongside news scans:

- **ING Think** (`think.ing.com`) — daily CEE FX/rates via `apify/rag-web-browser` (~11K chars). Best free open-access CEE macro source.
- **IMF** (`imf.org`) — Article IV concluding statements via `apify/rag-web-browser` (~22K chars).
- **ECB** (`ecb.europa.eu`) — already in Tier 1.
- Central banks (ČNB, NBP, MNB, BNB, NBS) — direct URL extraction; see [reference/MACRO_SOURCES.md](reference/MACRO_SOURCES.md).

## Critical gotchas

- **ALWAYS `decodeUrls: true`** in Google News (encoded redirects break ALL extractors).
- **"InPost" is ambiguous** — matches "post-Maduro". Use `"InPost SA"` for precision.
- **RSS max 10 feeds per run** — split into batches.
- **Zawya headline-scraper returns tag pages, NOT articles** — exclude from headline runs.
- **Reuters needs RESIDENTIAL proxy** — without it, returns 386 chars.
- **Reuters: rag-web-browser returns 0 chars on ~60% of URLs** — use workhard3000 only.
- **Morningstar `.co.uk` URLs fail** with workhard3000 — use `.com` URLs for extraction.
- **WSJ livecoverage pages fail** — skip URLs matching `wsj.com/livecoverage/`.
- **FT: rag-web-browser returns 16 chars ('Client Challenge')** — use workhard3000.
- **Forbes: workhard3000 returns 0 chars** — use rag-web-browser.
- **Barron's / MarketWatch cost $0.25/page** — use selectively for high-value articles.
- **Caixin URLs must be complete** — truncated URLs fail extraction.
- **EC Press Corner is an Angular SPA** — `rag-web-browser` returns 0 chars. Use REST API.

Full failure-mode catalog: [reference/PIPELINE_DETAIL.md](reference/PIPELINE_DETAIL.md), [reference/SOURCE_CONFIGS.md](reference/SOURCE_CONFIGS.md).

## Reference

- [data/sources.json](data/sources.json) — machine-readable: 33 sources × discovery × extractor × cost × gotchas
- [reference/SOURCE_CONFIGS.md](reference/SOURCE_CONFIGS.md) — per-source curl examples, run IDs, output samples
- [reference/PIPELINE_DETAIL.md](reference/PIPELINE_DETAIL.md) — RSS feeds, headline sources, warnings, failed paths, source quick-reference table
- [reference/MACRO_SOURCES.md](reference/MACRO_SOURCES.md) — ING Think, IMF, central banks
- [reference/EUROPEAN_COMPANIES_GUIDE.md](reference/EUROPEAN_COMPANIES_GUIDE.md) — European company handling tips
- [reference/MORNING_NOTE_DETAIL.md](reference/MORNING_NOTE_DETAIL.md) — HTML output spec (archived; out of scope for this skill)
- [reference/scripts/extract_and_clean.py](reference/scripts/extract_and_clean.py), [reference/scripts/clean_article.py](reference/scripts/clean_article.py) — readability-lxml post-processors
