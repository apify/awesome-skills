# Gotchas — cost guardrails & error recovery

## Cost (these are pay-per-event Actors)
- Every Actor here bills **per result row** plus a tiny per-run start fee. **Start with small caps** (`maxFilings` / `maxResults` / `maxReleases` ≈ 10–25) and a **narrow date window**, confirm the data is what the user wants, then widen. Don't pull a year of Form 4 across all tickers on the first run.
- If the user sets a spend cap, the platform stops the run when it's reached — so a tight `maxFilings` is the cheapest way to preview.
- For "how much will this cost?" — multiply expected rows by the Actor's per-row price shown on its Store page (`apify actors info "nexgendata/SLUG" --readme 2>/dev/null` includes pricing).

## Date windows
- US SEC Actors generally take `dateFrom`/`dateTo` (`YYYY-MM-DD`). Several require them (Form 4, 8-K, 13F, 13D/G). Default to a **recent window** (last 7–30 days) unless the user asks for history.
- `sec-form-nt-late-filing-tracker` uses `days_back` (default 90) — **Form NT is genuinely rare/low-volume**, so a short window can return zero rows. Widen `days_back` before concluding "nothing filed."
- `sec-form-13f-tracker-pro` data is **seasonal** — 13F is filed within 45 days of quarter-end, so off-cycle windows return little. Tie windows to quarter-ends (mid-Feb / mid-May / mid-Aug / mid-Nov).

## Tickers vs CIK
- EDGAR identifies filers by **CIK**, and many filings don't expose a ticker. Ticker filters work for large issuers; for precise filer targeting use CIK where the schema accepts it (`filerCik`, etc.). If a ticker returns nothing, the filer may simply not tag it.

## Global Actors
- The non-US regulators (FINMA/MAS/SFC/SEBI/ASIC/EDINET/HKEX/A-share/RNS) are **lower-volume and language-localized** (several return native-language fields, e.g. 證監會, 大量保有報告書, 高管增减持). Empty results often mean "no enforcement in that window," not a failure.

## Error recovery
- Auth error → `apify login` or `export APIFY_TOKEN=...`.
- `0 results` → widen the date window / raise the cap / drop the ticker filter; re-confirm the schema with `--input --json`.
- Run `FAILED` → read `apify runs info RUN_ID --json 2>/dev/null` (`.statusMessage`); most failures are bad date formats or an unsupported filter value.
- Always include each row's `source_url` when presenting results — it's the auditable link to the official filing.

## Compliance (non-negotiable)
This is **public regulatory filing data for research**. Present it as facts with source links. **Do not** generate buy/sell recommendations, price targets, or anything framed as financial, legal, or investment advice. Not affiliated with the SEC, FINRA, or any regulator.
