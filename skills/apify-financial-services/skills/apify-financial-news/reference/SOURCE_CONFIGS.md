# Source Configurations — 33 Verified Financial News Sources + Macro Briefing

Each source includes verified MCPC commands, curl commands, input schemas, run IDs, and output samples.
All configs tested 2026-03-19 with real Apify API runs. New sources (21-33) tested 2026-03-20.

## Post-Processing: readability-lxml Cleanup

**ALL `rag-web-browser` commands below use `outputFormats: ["html"]`**. The raw HTML MUST be cleaned via `readability-lxml` before use — see Step 4c in SKILL.md for the `clean_article()` function.

This strips navigation, menus, language pickers, sidebars, and footers (30-70% noise reduction). Exceptions: Bloomberg scraper, workhard3000 extractor, and EC Press Corner API return already-clean output — no cleanup needed.

---

## 1. Bloomberg (bloomberg.com)

### Discovery

**Guidance:**
- Hard paywall — Google News + RSS are the only discovery methods
- ALWAYS set `decodeUrls: true` — Bloomberg extractors fail on encoded Google News redirect URLs
- Use `"InPost SA"` not `"InPost"` to avoid false positives

**Google News:**
```bash
curl -X POST "https://api.apify.com/v2/acts/data_xplorer~google-news-scraper-fast/runs?waitForFinish=120" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"keywords":["site:bloomberg.com \"InPost SA\" OR \"INPST\""],"maxArticles":10,"timeframe":"7d","region_language":"US:en","decodeUrls":true,"extractImages":true,"proxyConfiguration":{"useApifyProxy":true,"apifyProxyGroups":["RESIDENTIAL"]}}'
```

- Verified: run `TGlLVnklOTKiU4Ert` — 30 articles ([console](https://console.apify.com/actors/runs/TGlLVnklOTKiU4Ert))
- GNews verified: run `4GxdXYWLAFTbc9H3j` — 1 article ([console](https://console.apify.com/actors/runs/4GxdXYWLAFTbc9H3j))

### Extraction

**Primary: `jamie_tran/bloomberg-article-scraper`** — $0.02/article, 80 fields, structured body, terminal tickers

**Command:**
```bash
curl -X POST "https://api.apify.com/v2/acts/jamie_tran~bloomberg-article-scraper/runs?waitForFinish=120" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"start_urls":[{"url":"https://www.bloomberg.com/news/articles/2026-03-19/jpmorgan-goldman-offer-hedge-funds-way-to-short-private-credit"}]}'
```

- Verified: run `qQbwWxgm0Ircjfm8h` — 7,577 chars, 80 fields ([console](https://console.apify.com/actors/runs/qQbwWxgm0Ircjfm8h))
- Key fields: headline, authors, publishedAt, terminalTickers, body, byline, contentTags, aiSummary, url

**Output sample:**
```json
{
  "headline": "JPMorgan, Goldman Offer Hedge Funds Way to Short Private Credit",
  "byline": "Silas Brown and Nishant Kumar",
  "publishedAt": "2026-03-19T14:17:09.116Z",
  "terminalTickers": [{"id": "GS:US"}, {"id": "CS:FP"}],
  "contentTags": [{"id": "private-credit", "name": "private credit", "type": "Topic"}]
}
```

**Fallback 1: `romy/bloomberg-news-scraper`** — $0.03/result, ~50% success rate, 38 fields
- Verified: run `KMZxdgHg0YBi45hV4` — 7,040 chars ([console](https://console.apify.com/actors/runs/KMZxdgHg0YBi45hV4))

**Fallback 2: `workhard3000/news-intelligence-rag-extractor`** — $0.025, 14 fields, last resort
- Verified: run `o8GkLCESzmlW5380e` — 2,996 chars ([console](https://console.apify.com/actors/runs/o8GkLCESzmlW5380e))

---

## 2. Reuters (reuters.com)

### Discovery

**Guidance:**
- Reuters deprecated ALL public RSS feeds — Google News is the only discovery method
- `dadhalfdev/reuters-scraper-per-event` IGNORES keyword param — do not use
- headline-news-scraper returns 0 for Reuters

**Google News:**
```bash
curl -X POST "https://api.apify.com/v2/acts/data_xplorer~google-news-scraper-fast/runs?waitForFinish=120" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"keywords":["site:reuters.com \"InPost SA\" OR \"INPST\""],"maxArticles":10,"timeframe":"7d","region_language":"US:en","decodeUrls":true,"extractImages":true,"proxyConfiguration":{"useApifyProxy":true,"apifyProxyGroups":["RESIDENTIAL"]}}'
```

### Extraction

**WARNING (updated 2026-03-24):** Reuters blocks `rag-web-browser` completely — returns 0 chars on ALL URLs, even with RESIDENTIAL proxy. Use `workhard3000` as primary extractor.

**Primary: `workhard3000/news-intelligence-rag-extractor` with RESIDENTIAL proxy** — $0.025

```bash
curl -X POST "https://api.apify.com/v2/acts/workhard3000~news-intelligence-rag-extractor/runs?waitForFinish=120" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"articleUrls":["https://www.reuters.com/..."],"autoArchive":true,"maxRetries":3,"requestIntervalMs":2000,"proxyConfiguration":{"useApifyProxy":true,"apifyProxyGroups":["RESIDENTIAL"]}}'
```

- Verified: 2026-03-24 — 2,632 chars with RESIDENTIAL proxy
- `rag-web-browser` returns 0 chars on ALL Reuters URLs (tested 5 URLs, standard + RESIDENTIAL proxy) — do NOT use
- Previous `workhard3000` test without RESIDENTIAL (2026-03-19) returned only 386 chars — RESIDENTIAL proxy is critical

---

## 3. Financial Times (ft.com)

### Discovery

**Guidance:**
- RSS (13 articles) + Google News
- headline-news-scraper returns articles but no keyword filtering — general FT front page

- RSS verified: run `TGlLVnklOTKiU4Ert` — 13 articles ([console](https://console.apify.com/actors/runs/TGlLVnklOTKiU4Ert))

### Extraction

**Primary: `workhard3000/news-intelligence-rag-extractor`** — $0.025/success (ONLY working extractor for FT)

**Command:**
```bash
curl -X POST "https://api.apify.com/v2/acts/workhard3000~news-intelligence-rag-extractor/runs?waitForFinish=120" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"articleUrls":["https://www.ft.com/content/..."],"autoArchive":true,"maxRetries":3,"requestIntervalMs":2000,"proxyConfiguration":{"useApifyProxy":true,"apifyProxyGroups":["RESIDENTIAL"]}}'
```

- Verified: run `AlP9aKovUBRxhdJwc` — 6,960 chars ([console](https://console.apify.com/actors/runs/AlP9aKovUBRxhdJwc))
- rag-web-browser returns 16 chars ("Client Challenge") — FT blocks it

**Output sample:**
```json
{
  "title": "ECB holds interest rates at 2% as energy prices soar",
  "byline": "Olaf Storbeck and Ian Smith",
  "publishedDate": "2026-03-19T13:15:18.282Z",
  "domain": "ft.com",
  "text": "The European Central Bank has kept its benchmark interest rate on hold at 2 per cent..."
}
```

---

## 4. WSJ (wsj.com)

### Discovery

- RSS verified: run `TGlLVnklOTKiU4Ert` — 20 articles ([console](https://console.apify.com/actors/runs/TGlLVnklOTKiU4Ert))

### Extraction

**Primary: `workhard3000/news-intelligence-rag-extractor`** — $0.025/success (ONLY working extractor for WSJ)

- Verified: run `2zXshJwxycAKgN7yK` — 4,748 chars ([console](https://console.apify.com/actors/runs/2zXshJwxycAKgN7yK))
- WARNING: byline and publishedDate are null — get from Google News/RSS discovery metadata
- WARNING: `wsj.com/livecoverage/` URLs FAIL — skip them

---

## 5. Economist (economist.com)

### Discovery

**Guidance:**
- Economist has EXCELLENT RSS — 300 articles! Best coverage of all 33 sources
- RSS should be primary, supplemented by Google News for targeted search

- RSS verified: run `TGlLVnklOTKiU4Ert` — 300 articles ([console](https://console.apify.com/actors/runs/TGlLVnklOTKiU4Ert))

### Extraction

**Primary: `workhard3000/news-intelligence-rag-extractor`** — $0.025/success (ONLY working extractor)

- Verified: run `ckhijvIQcwvwaOdaw` — 14,256 chars ([console](https://console.apify.com/actors/runs/ckhijvIQcwvwaOdaw))
- Byline always "The Economist" — no individual authors
- rag-web-browser returns 0 chars for Economist

---

## 6. CNBC (cnbc.com)

### Discovery

3 working methods: RSS (30), Headlines (19), Google News.

- RSS verified: run `TGlLVnklOTKiU4Ert` — 30 articles
- Headlines verified: run `a6JHWQ6LCv8DCum13` — 19 articles ([console](https://console.apify.com/actors/runs/a6JHWQ6LCv8DCum13))

### Extraction

**Primary: `apify/rag-web-browser`** — ~$0.005/query

- Verified: run `2QKQRPjZRyJxfggJt` — 4,865 chars ([console](https://console.apify.com/actors/runs/2QKQRPjZRyJxfggJt))
- Optional: workhard3000 for metadata (byline, date, image) — run `5WBPe82sgy5rUsigG`, 2,837 chars

---

## 7. Forbes (forbes.com)

### Discovery

RSS (25 articles) + Google News.

- RSS verified: run `TGlLVnklOTKiU4Ert` — 25 articles

### Extraction

**Primary: `apify/rag-web-browser`** — ~$0.005/query

- Verified: run `naBDjdL8RHZK4MEKM` — 4,969 chars ([console](https://console.apify.com/actors/runs/naBDjdL8RHZK4MEKM))
- workhard3000 returns 0 chars for Forbes — do NOT use
- `natasha.lekh` Forbes actor is UNDER MAINTENANCE — do not use

---

## 8. Morningstar (morningstar.com)

### Discovery

RSS (.co.uk, 20 articles) + Google News (.com).

**IMPORTANT**: morningstar.co.uk URLs fail with workhard3000 — use morningstar.com URLs for extraction.

- RSS verified: run `TGlLVnklOTKiU4Ert` — 20 articles

### Extraction

**Primary: `workhard3000/news-intelligence-rag-extractor`** — $0.025/success

- Verified: run `uVI3NxwXu9rULA5zY` — 35,256 chars ([console](https://console.apify.com/actors/runs/uVI3NxwXu9rULA5zY))
- `janbruinier` Morningstar actor is for fund ratings, NOT news — do not use

---

## 9. Barron's (barrons.com)

### Discovery

ONLY Google News — RSS returns 403, headline-scraper returns 0.

### Extraction

**Primary: `stanvanrooy6/universal-ai-web-scraper`** — ~$0.25/page (USE SELECTIVELY)

**Command:**
```bash
curl -X POST "https://api.apify.com/v2/acts/stanvanrooy6~universal-ai-web-scraper/runs?waitForFinish=120" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"startUrls":[{"url":"https://www.barrons.com/articles/..."}],"instructions":"Extract the full article text, title, author name, publication date, and any tags or categories.","proxyConfiguration":{"useApifyProxy":true,"apifyProxyGroups":["RESIDENTIAL"]},"useWebSearch":true}'
```

- Verified: run `tKoc6e4qWFGhHYG2x` — 3,387 chars ([console](https://console.apify.com/actors/runs/tKoc6e4qWFGhHYG2x))
- Output fields: author, categories, fullArticleText, publicationDate, tags, title

**Output sample:**
```json
{
  "title": "3 Reasons This Drone Stock Soared 520%...",
  "author": "Al Root",
  "publicationDate": "2026-03-18T10:38:00Z",
  "categories": ["daily", "feature"],
  "tags": ["Aerospace and Defense", "Drones", "IPO"]
}
```

---

## 10. MarketWatch (marketwatch.com)

### Discovery

Google News (primary) + RSS (10 articles, small volume).

- RSS verified: run `TGlLVnklOTKiU4Ert` — 10 articles

### Extraction

**Primary: `stanvanrooy6/universal-ai-web-scraper`** — ~$0.25/page (USE SELECTIVELY)

- Verified: run `E41lckeBGwYoFQMMl` — fullArticleText present ([console](https://console.apify.com/actors/runs/E41lckeBGwYoFQMMl))
- rag-web-browser returns HTTP 500 — completely blocked

**Cheap fallback (excerpts only):** workhard3000 — $0.025, returns 448-878 chars
- Verified: run `FdKa2X4C8IyQYTTck` — 559 chars ([console](https://console.apify.com/actors/runs/FdKa2X4C8IyQYTTck))

---

## 11. IBD / Investor's Business Daily (investors.com)

### Discovery

Google News only (very limited for non-US companies). RSS returns 403.

### Extraction

**Primary: `apify/rag-web-browser`** — ~$0.005/query

- Verified: run `a9dwfryRba07Eb0Nh` — 6,722 chars ([console](https://console.apify.com/actors/runs/a9dwfryRba07Eb0Nh))
- Optional metadata: workhard3000 run `PHQtaoYk0xa1f2QjH` — 958 chars (byline, date, image)

---

## 12. Les Echos (lesechos.fr)

### Discovery

ONLY Google News — RSS returns 403. Use French queries with `region_language: "FR:fr"`.

### Extraction

**Primary: `apify/rag-web-browser`** — ~$0.005/query

- Verified: run `K4sLa7tbZ720xwAkq` — 2,832 chars ([console](https://console.apify.com/actors/runs/K4sLa7tbZ720xwAkq))
- Paywall tightened: was 9,257 chars in audit, now 2,832
- Content in French
- Optional metadata: workhard3000 run `PHQtaoYk0xa1f2QjH` — 716 chars (byline, date)

---

## 13. AFR / Australian Financial Review (afr.com)

### Discovery

RSS (20 articles) + Google News. AFR focuses on APAC — limited European coverage.

- RSS verified: run `C8Q7CeLmLwEKbGLLS` — 20 articles ([console](https://console.apify.com/actors/runs/C8Q7CeLmLwEKbGLLS))

### Extraction

**Primary: `apify/rag-web-browser`** — ~$0.005/query

- Verified: run `Mod5b0kwyjdpR7Nea` — 1,231 chars ([console](https://console.apify.com/actors/runs/Mod5b0kwyjdpR7Nea))
- WARNING: Paywall tightened — was 4,399 chars, now only 1,231

---

## 14. SCMP / South China Morning Post (scmp.com)

### Discovery

Excellent discovery: RSS (50) + Headlines (39) + Google News.

- RSS verified: run `C8Q7CeLmLwEKbGLLS` — 50 articles
- Headlines verified: run `a6JHWQ6LCv8DCum13` — 39 articles

### Extraction

**Primary: `apify/rag-web-browser`** — ~$0.005/query

- Verified: run `LYVVUSk197JTJu81z` — 1,819 chars ([console](https://console.apify.com/actors/runs/LYVVUSk197JTJu81z))
- WARNING: Paywall tightened — was 3,014 chars, now 1,819

---

## 15. Nikkei Asia (asia.nikkei.com)

### Discovery

Best headline coverage (60!) + RSS (50, no description) + Google News.

- Headlines verified: run `a6JHWQ6LCv8DCum13` — 60 articles (highest!)
- RSS verified: run `C8Q7CeLmLwEKbGLLS` — 50 articles (title + link only, no description)

### Extraction

**Primary: `workhard3000/news-intelligence-rag-extractor`** — $0.025/success (outperforms rag-web-browser for Nikkei)

- Verified: run `XK7gMVH4Ddzk0B7YF` — 5,723 chars ([console](https://console.apify.com/actors/runs/XK7gMVH4Ddzk0B7YF))
- Full metadata: byline ("EISAKU NITTA"), publishedDate, image

---

## 16. Caixin Global (caixinglobal.com)

### Discovery

Google News + Headlines (7, very low volume). No RSS.

- Headlines verified: run `a6JHWQ6LCv8DCum13` — 7 articles

### Extraction

**Primary: `workhard3000/news-intelligence-rag-extractor`** — $0.025/success

- Verified: run `2oYfpd4YhrSQc50Lg` — 4,166 chars ([console](https://console.apify.com/actors/runs/2oYfpd4YhrSQc50Lg))
- Free/commentary = full text; paywalled news = ~885 chars
- IMPORTANT: Use complete URLs — truncated URLs fail
- rag-web-browser fetches wrong page for Caixin — do NOT use

---

## 17. Zawya (zawya.com)

### Discovery

Google News is recommended. Headlines (50 articles) exist but return tag pages, not articles.

**WARNING**: Headline scraper returns category/tag page URLs (e.g. `/primarykeyword/OIL`), NOT article URLs. Filter these out or avoid.

### Extraction

**Primary: `workhard3000/news-intelligence-rag-extractor`** — $0.025/success

- Verified: run `RzRvX08Xg29SsrXV5` — 12,681 chars ([console](https://console.apify.com/actors/runs/RzRvX08Xg29SsrXV5))
- rag-web-browser returns HTTP 500 for Zawya — do NOT use
- Full metadata: byline, publishedDate, image

---

## 18. Euronews (euronews.com)

### Discovery

RSS (50 articles, business theme) + Google News. NOT paywalled.

- RSS verified: run `C8Q7CeLmLwEKbGLLS` — 50 articles

### Extraction

**Primary: `apify/rag-web-browser`** — ~$0.005/query

- Verified: run `fREgpuCzO6DulRH8w` — 10,917 chars ([console](https://console.apify.com/actors/runs/fREgpuCzO6DulRH8w))
- Optional metadata: workhard3000 run `5WBPe82sgy5rUsigG` — 8,670 chars (byline: "Denis Loctier", date, image)

---

## 19. IntelliNews (intellinews.com)

### Discovery

RSS (variable volume) + Google News. Niche source, excellent for CEE coverage.

- RSS verified: run `C8Q7CeLmLwEKbGLLS` — volume varies ([console](https://console.apify.com/actors/runs/C8Q7CeLmLwEKbGLLS))

### Extraction

**Primary: `apify/rag-web-browser`** — ~$0.005/query

- Verified: run `eAiUialgv1waTvJNP` — 10,744 chars ([console](https://console.apify.com/actors/runs/eAiUialgv1waTvJNP))
- Optional metadata: workhard3000 run `5WBPe82sgy5rUsigG` — 6,496 chars
- NOTE: publishedDate is null in workhard3000 — get from RSS/GNews discovery

---

## 20. Handelsblatt (handelsblatt.com)

### Discovery

Excellent: Headlines (60) + RSS (50, full metadata) + Google News. German language.

- Headlines verified: run `a6JHWQ6LCv8DCum13` — 60 articles
- RSS verified: run `C8Q7CeLmLwEKbGLLS` — 50 articles with author + date

**Google News — MCPC (German):**
```bash
curl -s -X POST "https://api.apify.com/v2/acts/data_xplorer~google-news-scraper-fast/runs?waitForFinish=120" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"keywords":["site:handelsblatt.com \"InPost SA\" OR \"INPST\" OR \"Paketautomaten\""],"maxArticles":10,"timeframe":"7d","region_language":"DE:de","decodeUrls":true,"extractImages":true,"proxyConfiguration":{"useApifyProxy":true,"apifyProxyGroups":["RESIDENTIAL"]}}'
```

### Extraction

**Primary: `apify/rag-web-browser`** — ~$0.005/query

- Verified: run `Y79uVeyDxC0dD6ncY` — 10,435 chars ([console](https://console.apify.com/actors/runs/Y79uVeyDxC0dD6ncY))
- Content in German
- Optional metadata: workhard3000 run `PHQtaoYk0xa1f2QjH` — 7,737 chars (byline: "Laura de la Motte", date, image)

---

# Pan-European Sources — Added 2026-03-20

---

## 21. POLITICO Europe (politico.eu)

### Discovery

- Verified: 2026-03-20, 5 articles — strong EU policy/energy coverage

### Extraction

**Primary: `apify/rag-web-browser`** — ~$0.005/query

```bash
curl -s -X POST "https://api.apify.com/v2/acts/apify~rag-web-browser/runs?waitForFinish=120" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"<POLITICO_ARTICLE_URL>","maxResults":1,"outputFormats":["html"],"requestTimeoutSecs":40,"proxyConfiguration":{"useApifyProxy":true,"apifyProxyGroups":["RESIDENTIAL"]},"removeCookieWarnings":true}'
```

- Verified: 2026-03-20 — 7,677 chars, full article text for free articles
- Premium/paywalled articles may return partial content — still useful for headline + lead

---

## 22. EUobserver (euobserver.com)

### Discovery

- Verified: 2026-03-20, 5 articles — investigative/transparency focus

### Extraction

**Primary: `workhard3000/news-intelligence-rag-extractor`** (with autoArchive) — $0.025

```bash
curl -s -X POST "https://api.apify.com/v2/acts/workhard3000~news-intelligence-rag-extractor/runs?waitForFinish=120" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"articleUrls":["<EUOBSERVER_URL>"],"autoArchive":true,"maxRetries":3,"requestIntervalMs":2000,"proxyConfiguration":{"useApifyProxy":true,"apifyProxyGroups":["RESIDENTIAL"]}}'
```

- Verified: 2026-03-20 — 3,001 chars via archive bypass
- `rag-web-browser` hits "Unlock article" paywall — do NOT use as primary

---

## 23. EUbusiness (eubusiness.com)

### Discovery

### Extraction

**Primary: `apify/rag-web-browser`** — ~$0.005/query

- Verified: 2026-03-20 — 4,828 chars, open access, clean extraction

---

## 24. EU Reporter (eureporter.co)

### Discovery

### Extraction

**Primary: `apify/rag-web-browser`** — ~$0.005/query

- Verified: 2026-03-20 — 5,921 chars, open access, full article text

---

# Institutional Sources — Added 2026-03-20

---

## 25. EC Press Corner (ec.europa.eu)

### Discovery

### Extraction

**DO NOT use rag-web-browser** — EC Press Corner is an Angular SPA, JS-only render returns 0 chars.

**Use REST API directly:**
```bash
curl -s "https://ec.europa.eu/commission/presscorner/api/documents?reference=IP/26/614&language=en" | python3 -c "
import sys,json
d=json.load(sys.stdin)
html=d.get('docuLanguageResource',{}).get('htmlContent','')
print(f'Chars: {len(html)}')
# Strip HTML tags for plain text
import re
text=re.sub('<[^<]+?>','',html)
print(text[:500])
"
```

- Verified: 2026-03-20 — REST API returns 9K+ chars clean HTML per press release
- Parse `IP_XX_NNN` reference IDs from Google News titles to construct API calls
- Subdomain pages (energy.ec.europa.eu, research.ec.europa.eu) extract fine with `rag-web-browser` (1,936 chars)

---

## 26. ECB (ecb.europa.eu)

### Discovery

- Verified: 2026-03-20, 5 articles — projections, rate decisions, digital euro

### Extraction

**Primary: `apify/rag-web-browser`** — ~$0.005/query

- Verified: 2026-03-20 — press releases: 6,950 chars; projection reports: 85,009 chars
- First ~400 chars are nav boilerplate — strip or ignore
- Excellent institutional source for SK and BG (eurozone members)

---

# CEE Local Sources — Added 2026-03-20

---

## 27. ČTK / České noviny (ceskenoviny.cz)

### Discovery

- GNews verified: 2026-03-20 — 5 articles (CZ:cs region)
- RSS verified: 2026-03-20 — 50 articles per feed (ekonomika.php, cr.php)
- Search on ceskenoviny.cz does NOT work (JS rendered, returns shell only)

### Extraction

**Primary: `apify/rag-web-browser`** — ~$0.005/query

- Verified: 2026-03-20 — 4,596 chars, full article text in Czech

---

## 28. PAP — Polska Agencja Prasowa (pap.pl)

### Discovery

- Verified: 2026-03-20 — 5 articles
- PAP web search returns false positives (3-letter string match)
- PAP RSS is blocked by WAF (Incapsula)
- Only Google News `site:pap.pl` works reliably

### Extraction

**Primary: `apify/rag-web-browser`** — ~$0.005/query

- Verified: 2026-03-20 — 9,232 chars, full article text in Polish

---

## 29. BTA — Bulgarska Telegrafna Agentsia (bta.bg)

### Discovery

- Verified: 2026-03-20 — 5 articles
- BTA web search is JS rendered — returns empty results
- BTA has no RSS feeds
- Only Google News `site:bta.bg` works

### Extraction

**Primary: `apify/rag-web-browser`** — ~$0.005/query

- Verified: 2026-03-20 — 10,851 chars, full article text in Bulgarian

---

## 30. TASR — Tlačová agentúra Slovenskej republiky (tasr.sk)

### Discovery

- Verified: 2026-03-20 — 5 articles
- **WARNING**: Google News returns generic titles ("Tlačová agentúra Slovenskej republiky") — extraction needed to determine article content
- TASR web search redirects to homepage (SPA)
- TASR has no RSS feeds

### Extraction

**Primary: `apify/rag-web-browser`** — ~$0.005/query

- Verified: 2026-03-20 — 3,956 chars, article text in Slovak

---

## 31. Telex.hu (telex.hu) — Hungary

### Discovery

- Verified: 2026-03-20 — 2 articles for portfolio-related queries
- Independent outlet, launched by ex-index.hu journalists — high editorial credibility
- **Best Hungarian extraction quality** among tested sources

### Extraction

**Primary: `apify/rag-web-browser`** — ~$0.005/query

- Verified: 2026-03-20 — 8,216 chars, excellent clean article body in Hungarian

---

## 32. HVG.hu (hvg.hu) — Hungary

### Discovery

- Verified: 2026-03-20 — 3 articles
- Respected independent weekly (since 1968), strong digital presence

### Extraction

**Primary: `apify/rag-web-browser`** — ~$0.005/query

- Verified: 2026-03-20 — 4,883 chars, clean article body in Hungarian

---

## 33. Világgazdaság (vg.hu) — Hungary

### Discovery

- Verified: 2026-03-20 — 4 articles (strongest GNews presence among HU sources)
- Hungarian business daily — focuses on economics and finance

### Extraction

**Primary: `apify/rag-web-browser`** — ~$0.005/query

- Verified: 2026-03-20 — 9,906 chars, article body in Hungarian
- First ~900 chars contain navigation/ticker noise — article body starts after

---

# Macro Briefing Sources (not Tier 1, but used for market context)

---

## ING Think (think.ing.com)

### Discovery

```bash
curl -s -X POST "https://api.apify.com/v2/acts/data_xplorer~google-news-scraper-fast/runs?waitForFinish=120" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"keywords":["site:think.ing.com Czech OR Poland OR Hungary OR CEE"],"maxArticles":10,"timeframe":"7d","region_language":"US:en","decodeUrls":true,"proxyConfiguration":{"useApifyProxy":true,"apifyProxyGroups":["RESIDENTIAL"]}}'
```

### Extraction

**Primary: `apify/rag-web-browser`** — ~$0.005/query

- Verified: 2026-03-20 — 11,319 chars, excellent quality
- Best free open-access source for daily CEE FX, rates, and macro commentary
- Covers CZ, PL, HU, SK, BG + broader EU

---

## IMF Country Pages (imf.org)

### Extraction

```bash
curl -s -X POST "https://api.apify.com/v2/acts/apify~rag-web-browser/runs?waitForFinish=120" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"https://www.imf.org/en/Countries/CZE","maxResults":1,"outputFormats":["html"],"requestTimeoutSecs":40,"proxyConfiguration":{"useApifyProxy":true,"apifyProxyGroups":["RESIDENTIAL"]},"removeCookieWarnings":true}'
```

- Verified: 2026-03-20 — 22,250 chars for Article IV concluding statements
- Annual cadence (Article IV) + quarterly (WEO data)
- Country codes: CZE (CZ), POL (PL), HUN (HU), BGR (BG), SVK (SK)

---

## ČNB — Czech National Bank (cnb.cz)

### Direct URL Extraction

```bash
curl -s -X POST "https://api.apify.com/v2/acts/apify~rag-web-browser/runs?waitForFinish=120" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"https://www.cnb.cz/en/monetary-policy/","maxResults":1,"outputFormats":["html"],"requestTimeoutSecs":40,"proxyConfiguration":{"useApifyProxy":true,"apifyProxyGroups":["RESIDENTIAL"]},"removeCookieWarnings":true}'
```

- Verified: 2026-03-20 — 35,367 chars (full bank board decisions listing)
- **WARNING**: Google News `site:cnb.cz` is blocked by Cloudflare — use direct URL extraction only
- Use keyword query "ČNB" or "Czech National Bank" in broad GNews search instead
