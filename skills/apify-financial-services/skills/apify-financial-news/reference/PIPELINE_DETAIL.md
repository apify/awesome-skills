# Pipeline Detail — Reference

Detailed pipeline instructions, RSS feeds, headline sources, warnings, and failed paths.
Referenced from SKILL.md — load when executing the pipeline.

## RSS Discovery

**Actor**: `louvre/rss-news-aggregator`

**Actor**: `louvre/rss-news-aggregator`

**Max 10 feeds per run** — split into batches if needed.

14 sources with working RSS feeds:

| Source | RSS URL | Typical Volume |
|--------|---------|----------------|
| Bloomberg | `https://feeds.bloomberg.com/markets/news.rss` | 30 |
| FT | `https://www.ft.com/rss/home` | 13 |
| WSJ | `https://feeds.a.dj.com/rss/RSSMarketsMain.xml` | 20 |
| Economist | `https://www.economist.com/finance-and-economics/rss.xml` | 300 |
| CNBC | `https://www.cnbc.com/id/100003114/device/rss/rss.html` | 30 |
| Forbes | `https://www.forbes.com/business/feed2` | 25 |
| Morningstar | `https://www.morningstar.co.uk/uk/news/rss.aspx` | 20 |
| MarketWatch | `https://www.marketwatch.com/rss/topstories` | 10 |
| AFR | `https://www.afr.com/rss/feed.xml` | 20 |
| SCMP | `https://www.scmp.com/rss/91/feed` | 50 |
| Nikkei | `https://asia.nikkei.com/rss/feed/nar` | 50 |
| Euronews | `https://www.euronews.com/rss?level=theme&name=business` | 50 |
| IntelliNews | `https://www.intellinews.com/rss/` | varies |
| Handelsblatt | `https://www.handelsblatt.com/contentexport/feed/schlagzeilen` | 50 |
| ČTK (ČR) | `https://www.ceskenoviny.cz/sluzby/rss/cr.php` | 50 |
| ČTK (ekonomika) | `https://www.ceskenoviny.cz/sluzby/rss/ekonomika.php` | 50 |

**No RSS**: Reuters, Barron's, IBD, Les Echos, Caixin, Zawya, PAP (WAF), BTA, TASR, MTI (paywall).

```
curl -s -X POST "https://api.apify.com/v2/acts/louvre~rss-news-aggregator/runs?waitForFinish=120" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"rss_feeds":[{"url":"https://feeds.bloomberg.com/markets/news.rss"},{"url":"https://www.ft.com/rss/home"},{"url":"https://feeds.a.dj.com/rss/RSSMarketsMain.xml"},{"url":"https://www.economist.com/finance-and-economics/rss.xml"},{"url":"https://www.cnbc.com/id/100003114/device/rss/rss.html"},{"url":"https://www.forbes.com/business/feed2"},{"url":"https://www.morningstar.co.uk/uk/news/rss.aspx"},{"url":"https://www.marketwatch.com/rss/topstories"},{"url":"https://www.afr.com/rss/feed.xml"},{"url":"https://www.scmp.com/rss/91/feed"}],"raw_data":false}'
```

Batch 2 (remaining 4):
```
curl -s -X POST "https://api.apify.com/v2/acts/louvre~rss-news-aggregator/runs?waitForFinish=120" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"rss_feeds":[{"url":"https://asia.nikkei.com/rss/feed/nar"},{"url":"https://www.euronews.com/rss?level=theme&name=business"},{"url":"https://www.intellinews.com/rss/"},{"url":"https://www.handelsblatt.com/contentexport/feed/schlagzeilen"}],"raw_data":false}'
```

RSS returns general articles — **filter client-side** by company name/ticker match in title/description.


## Headline Discovery

**Actor**: `rodrigo_pacelli/headline-news-scraper`

**Actor**: `rodrigo_pacelli/headline-news-scraper`

Only 6 sources work (others return 0):

| Source | URL | Volume |
|--------|-----|--------|
| CNBC | `https://www.cnbc.com` | 19 |
| SCMP | `https://www.scmp.com` | 39 |
| Nikkei | `https://asia.nikkei.com` | 60 |
| Caixin | `https://www.caixinglobal.com` | 7 |
| Zawya | `https://www.zawya.com` | 50 (tag pages!) |
| Handelsblatt | `https://www.handelsblatt.com` | 60 |

```
curl -s -X POST "https://api.apify.com/v2/acts/rodrigo_pacelli~headline-news-scraper/runs?waitForFinish=120" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"urls":["https://www.cnbc.com","https://www.scmp.com","https://asia.nikkei.com","https://www.caixinglobal.com","https://www.handelsblatt.com"],"includeImages":false,"classifyWithAI":false}'
```

**WARNING**: Exclude Zawya from headline runs — returns category/tag pages, not article URLs.

No keyword filtering — filter results client-side by company name match.


## Non-Article URL Filter Patterns

3. **Non-article URL filter** (apply to BOTH tiers): Discard URLs matching any of these patterns — they are NOT articles:
   - Stock/quote pages: `/markets/companies/`, `/quote/`, `/key-metrics/`, `/stock/`
   - Sitemaps & feeds: `/sitemap`, `/rss/`, `/feed/`
   - Newsletters & redirects: `/newsletters/`, `redirectUrl=`
   - Author/profile pages: `/author/`, `/journalist/`, `/profile/`
   - Tag/category listing pages: `/primarykeyword/`, `/topic/`, `/tag/` (except when part of article slug)
   - Data pages with no article content: URL contains only ticker symbol and no article slug


## Source Quick Reference Table


| # | Source | Discovery Methods | Extractor | Cost/Article | Chars Verified | Language |
|---|--------|-------------------|-----------|--------------|----------------|----------|
| 1 | Bloomberg | GNews + RSS(30) | jamie_tran | $0.02 | 7,577 (80 fields) | EN |
| 2 | Reuters | GNews only | workhard3000 (RESIDENTIAL proxy!) | $0.025 | 2,632 | EN |
| 3 | Financial Times | GNews + RSS(13) | workhard3000 | $0.025 | 6,960 | EN |
| 4 | WSJ | GNews + RSS(20) | workhard3000 | $0.025 | 4,748 | EN |
| 5 | Economist | RSS(300!) + GNews | workhard3000 | $0.025 | 14,256 | EN |
| 6 | CNBC | RSS(30) + Headlines(19) + GNews | rag-web-browser | $0.005 | 4,865 | EN |
| 7 | Forbes | RSS(25) + GNews | rag-web-browser | $0.005 | 4,969 | EN |
| 8 | Morningstar | RSS(20) + GNews | workhard3000 | $0.025 | 35,256 | EN |
| 9 | Barron's | GNews only | universal-ai | $0.25 | 3,387 | EN |
| 10 | MarketWatch | GNews + RSS(10) | universal-ai | $0.25 | present | EN |
| 11 | IBD | GNews (limited) | rag-web-browser | $0.005 | 6,722 | EN |
| 12 | Les Echos | GNews only | rag-web-browser | $0.005 | 2,832 | FR |
| 13 | AFR | RSS(20) + GNews | rag-web-browser | $0.005 | 1,231 | EN |
| 14 | SCMP | RSS(50) + Headlines(39) + GNews | rag-web-browser | $0.005 | 1,819 | EN |
| 15 | Nikkei | Headlines(60) + RSS(50) + GNews | workhard3000 | $0.025 | 5,723 | EN |
| 16 | Caixin | GNews + Headlines(7) | workhard3000 | $0.025 | 4,166 | EN |
| 17 | Zawya | GNews (headlines=tag pages!) | workhard3000 | $0.025 | 12,681 | EN |
| 18 | Euronews | RSS(50) + GNews | rag-web-browser | $0.005 | 10,917 | EN |
| 19 | IntelliNews | RSS + GNews | rag-web-browser | $0.005 | 10,744 | EN |
| 20 | Handelsblatt | Headlines(60) + RSS(50) + GNews | rag-web-browser | $0.005 | 10,435 | DE |
| | **Pan-European** | | | | | |
| 21 | POLITICO Europe | GNews | rag-web-browser | $0.005 | 7,677 | EN |
| 22 | EUobserver | GNews | workhard3000 (autoArchive) | $0.025 | 3,001 | EN |
| 23 | EUbusiness | GNews | rag-web-browser | $0.005 | 4,828 | EN |
| 24 | EU Reporter | GNews | rag-web-browser | $0.005 | 5,921 | EN |
| | **Institutional** | | | | | |
| 25 | EC Press Corner | GNews | REST API (presscorner) | free | 9,000+ | EN |
| 26 | ECB | GNews | rag-web-browser | $0.005 | 6,950–85,009 | EN |
| | **CEE Local** | | | | | |
| 27 | ČTK / České noviny | RSS(50) + GNews (CZ:cs) | rag-web-browser | $0.005 | 4,596 | CZ |
| 28 | PAP | GNews (PL:pl) | rag-web-browser | $0.005 | 9,232 | PL |
| 29 | BTA | GNews (BG:bg) | rag-web-browser | $0.005 | 10,851 | BG |
| 30 | TASR | GNews (SK:sk) | rag-web-browser | $0.005 | 3,956 | SK |
| 31 | Telex.hu | GNews (HU:hu) | rag-web-browser | $0.005 | 8,216 | HU |
| 32 | HVG.hu | GNews (HU:hu) | rag-web-browser | $0.005 | 4,883 | HU |
| 33 | Világgazdaság | GNews (HU:hu) | rag-web-browser | $0.005 | 9,906 | HU |


## Critical Warnings


1. **ALWAYS `decodeUrls: true`** in Google News — encoded redirect URLs break ALL extractors
2. **"InPost" is ambiguous** — matches "post-Maduro", "post-ESG". Use `"InPost SA"` for precision
3. **RSS max 10 feeds per run** — must split into batches
4. **Zawya headline-scraper** returns category/tag pages (`/primarykeyword/OIL`), NOT article URLs — use Google News for Zawya discovery
5. **Morningstar domain matters** — `.co.uk` URLs fail with workhard3000. Use `.com` URLs only
6. **WSJ livecoverage pages** fail extraction — skip URLs matching `wsj.com/livecoverage/`
7. **Barron's/MarketWatch cost $0.25/page** — use selectively for high-value articles only
8. **Les Echos**: Use `region_language: "FR:fr"` for French queries
9. **Handelsblatt**: Use `region_language: "DE:de"` for German queries
10. **Caixin URLs must be complete** — truncated URLs fail extraction
11. **Paywall tightening observed** — AFR (1,231 chars), SCMP (1,819 chars), Les Echos (2,832 chars) return less than earlier audits


## Failed Paths (Do Not Use)


| What | Why |
|------|-----|
| `dadhalfdev/reuters-scraper-per-event` | Ignores keyword param, returns random latest news |
| `rag-web-browser` for FT | Returns 16 chars ("Client Challenge") |
| `rag-web-browser` for Economist | Returns 0 chars |
| `rag-web-browser` for Zawya | Returns HTTP 500 |
| `rag-web-browser` for MarketWatch | Returns HTTP 500 |
| `workhard3000` for Reuters WITHOUT residential proxy | Returns 386 chars — MUST use RESIDENTIAL proxy group (2,632 chars with it) |
| `rag-web-browser` for Reuters WITHOUT residential proxy | Returns 0 chars on ~60% of URLs — MUST use RESIDENTIAL proxy group |
| `workhard3000` for Forbes | Returns 0 chars |
| `natasha.lekh` Forbes actor | Under maintenance |
| `janbruinier` Morningstar actor | For fund ratings, not news articles |
| `mscraper` IBD actor | $20/mo, US tickers only |
| RSS for Reuters, Barron's, IBD, Les Echos | 403/404/deprecated |
| Headline scraper for 14/33 sources | Returns 0 results |


## Output Format Detail


Structure extracted articles as JSON with **separate tiers**:

```json
{
  "company": "InPost",
  "ticker": "INPST.AS",
  "query_date": "2026-03-19",
  "timeframe": "7d",
  "tier1": {
    "sources_queried": 6,
    "articles_found": 2,
    "articles": [
      {
        "tier": "verified",
        "title": "InPost Readies AI Shopping Assistant",
        "source": "bloomberg.com",
        "author": "Konrad Krasuski",
        "published_date": "2026-03-19T14:17:09Z",
        "url": "https://www.bloomberg.com/news/articles/...",
        "text_chars": 7577,
        "text_preview": "First 200 chars...",
        "discovery_method": "google_news_site",
        "extraction_actor": "jamie_tran/bloomberg-article-scraper",
        "extraction_cost": 0.02
      }
    ]
  },
  "tier2": {
    "articles_found": 5,
    "articles": [
      {
        "tier": "broad",
        "title": "InPost expands parcel locker network in France",
        "source": "seekingalpha.com",
        "url": "https://seekingalpha.com/news/...",
        "text_chars": 1200,
        "text_preview": "First 200 chars...",
        "discovery_method": "google_news_broad",
        "extraction_actor": "apify/rag-web-browser",
        "extraction_cost": 0.005,
        "quality_warning": null
      }
    ]
  },
  "total_extraction_cost": 0.15,
  "warnings": [],
  "failed_extractions": []
}
```

Present TWO separate tables to the user:

```markdown

## News Intelligence: InPost (INPST.AS) — Last 7 days

