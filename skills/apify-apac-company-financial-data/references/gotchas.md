# Gotchas — cost guardrails, locale & error recovery

## Cost (these are pay-per-event Actors)
- Every Actor here bills **per result row** plus a tiny per-run start fee. **Start with small caps** (`max_disclosures` / `maxResults` / `limit` / `max_records` / `maxRecords` ≈ 10–25) and a **narrow date window**, confirm the data is what the user wants, then widen. Don't screen an entire exchange or pull a year of disclosures on the first run.
- Stock screeners with `enrich_*` flags (`enrich_sector`, `enrich_fundamentals`, `enrich_xbrl`) make **extra per-row fetches** — slower and more expensive. Leave enrichment **off** for a first pass; turn it on only for the final shortlist.
- For "how much will this cost?" — multiply expected rows by the Actor's per-row price on its Store page (`apify actors info "nexgendata/SLUG" --readme 2>/dev/null` includes pricing).

## Source API keys required (user must supply their own)
A few Actors call an official API that needs a **free key the user registers themselves** — we don't ship one:
- `japan-edinet-insider-filings` → `apiKey` (Japan FSA **EDINET** subscription key).
- `korea-ipo-pipeline-tracker` → `opendart_api_key` (Korea FSS **OpenDART** key).
- Optional (work without, better with a key): `japan-houjin-bangou-corporate-registry` (`nta_api_key`), `ogd-india-companies-registry` (`api_key`).
If the user hasn't got one, point them to the source's free developer portal; don't hard-code or share keys.

## Field names differ by country (don't assume)
APAC Actors were built per-source, so the same concept has different field names:
- Date windows: `date_from`/`date_to` (Japan TDnet, Taiwan MOPS, EDINET, Singapore MAS), `startDate`/`endDate` (HKEX insider, China A-share), `start_date`/`end_date` (SEBI), `decision_date_from`/`decision_date_to` (HK SFC), or `lookbackDays`/`lookaheadDays` (HKEX/SGX/IPO sweep).
- Ticker/code: `ticker_filter` (Japan/Taiwan, 4-digit), `issuer_ticker` (EDINET), `tickers[]` (HKEX/SGX announcements), `stockCode` (HKEX insider, single), `stockCodes[]` (China A-share, array).
- Result cap: `max_disclosures` / `maxResults` / `max_results` / `max_records` / `maxRecords` / `limit` — all different. **Always run `apify actors info … --input --json` first.**

## Locale, encoding & calendars
- Many APAC sources return **native-language fields** (한국어, 日本語, 繁體中文/简体中文). Preserve the original string and add an English gloss when presenting. Examples: 適時開示 (timely disclosure), 大量保有報告書 (large-shareholding report), 重大訊息 (material announcement), 高管增减持 (executive buy/sell), 證監會 (HK SFC).
- Use 4-digit securities codes, not Western tickers, for Japan (e.g. Toyota = `7203`) and Taiwan (e.g. TSMC = `2330`). China A-shares use 6-digit codes (e.g. `600519`); HK uses up to 5 digits (e.g. `00700`).
- Time zones matter for "today's" disclosures — Taiwan MOPS is TPE, TDnet is JST, etc. A UTC date window can miss the local trading day; widen by one day if a fresh filing seems missing.

## Volume & seasonality
- Registries (ACRA / 法人番号 / OGD India) are **lookup** Actors: give a specific company name/number, not an open-ended sweep, or you'll pay for noise.
- Insider / large-shareholder and enforcement feeds are **lower-volume**; an empty window usually means "nothing filed," not a failure — widen the dates before concluding zero.
- IPO calendars are bursty and seasonal; use `lookaheadDays` for upcoming listings and `lookbackDays` for recent ones, and don't expect a steady stream off-cycle.

## Error recovery
- Auth error (Apify) → `apify login` or `export APIFY_TOKEN=...`.
- `401/403` from inside the run → a **source** API key is missing/invalid (EDINET / OpenDART) — see above.
- `0 results` → widen the date window / raise the cap / drop the company/ticker filter; re-confirm the schema with `--input --json` (you may be using the wrong field name).
- Run `FAILED` → read `apify runs info RUN_ID --json 2>/dev/null` (`.statusMessage`); most failures are bad date formats, a wrong code format (Western ticker instead of numeric code), or an unsupported filter value.
- Always include each row's `source_url` when presenting results — it's the auditable link to the official exchange / registry / regulator.

## Compliance (non-negotiable)
This is **public company, exchange, and regulatory data for research**. Present it as facts with source links. **Do not** generate buy/sell recommendations, price targets, or anything framed as financial, legal, or investment advice. Not affiliated with any exchange, company registry, or financial regulator.
