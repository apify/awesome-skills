# Gotchas, apify-website-performance-audit

Cost guardrails, error recovery and known traps. Read on demand when building inputs or when a run returns less than expected.

## Cost guardrails

Both routed `datatoolsforall` Actors are `PAY_PER_EVENT`. Estimate before running:

| Actor | Upper-bound estimate |
|-------|----------------------|
| `datatoolsforall/website-sitemap-extractor` | sites x `maxUrlsPerSite` x $0.0002, plus x $0.0005 per URL with `checkUrlStatus`, plus $0.00005 start |
| `datatoolsforall/bulk-lighthouse-pagespeed-audit` | (URLs in `urls` + `maxUrls` if `sitemapUrl` is set) x devices x $0.02, plus $0.0001 start at 2 GB |
| `apify/sitemap-extractor` | URLs found x $0.0005 on the Free plan (less on paid plans), with no input cap |

The traps:

- **Defaults are large.** `maxUrlsPerSite` defaults to 10,000 ($2.00 per site) and `maxUrls` to 50 ($1.00 per device). Set both explicitly on every call.
- **`maxUrls` does not limit `urls`.** Every pasted URL is audited. The length of the list you pass is the cap.
- **Devices multiply.** `["mobile","desktop"]` doubles the audit count.
- **No CLI cost cap.** `apify actors call` has no flag for a maximum cost per run, so the input caps are the only guard on the CLI route. A user who wants a hard dollar cap can set the run's maximum cost in Apify Console or via the API.
- **Status checks are rarely worth it before auditing.** Lighthouse does not charge 404, 5xx, blocked or timed-out pages, so `checkUrlStatus` ($0.0005 per URL) only pays off when the sitemap is known to be full of redirects. Redirected URLs are audited at their target (`finalUrl`) and charged.
- **Template sampling beats full coverage.** Most Lighthouse findings come from the page template. 3 pages per first path segment usually tell more per dollar than every page of a 2,000-page blog.

### Confirmation thresholds (this skill)

- Always state the estimate as "around $X, at most $Y" before running.
- Above about $1 in total, get an explicit yes from the user first.
- Above about $20, suggest a sample per template or a smaller section before a full run.

## Run time

- Audits run one at a time. The author measured about 10 s per light page and about 60 s per script-heavy page locally; platform times depend on run memory.
- The Console default run timeout is 3,600 s. Rule of thumb: allow about 75 s per audit. Above about 40 audits, pass `--timeout <seconds>` on `apify actors call`, or split the URL list into several runs that can run in parallel.
- A run that times out keeps the audits it finished, and they are charged. Do not rerun the whole list: compare the dataset's `url` and `strategy` pairs with the plan and rerun only the missing ones.

## Common errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Extractor: one row with `errorCode` `NO_SITEMAP_FOUND` (billed $0.0002) | The site has no sitemap at robots.txt or the common locations | Ask the user for URLs and pass them to the Lighthouse Actor in `urls` |
| Extractor: `SITEMAP_NOT_FOUND` (free) | A direct sitemap link from the input does not work | Pass the website root so robots.txt discovery runs |
| Extractor: `BLOCKED` (free) | The site answered 401, 403 or a bot challenge; nothing is bypassed | If the user owns the site, allow-list the request. For a list only, `apify/sitemap-extractor` uses Apify Proxy. Lighthouse will likely be blocked too |
| Extractor: `INDEX_NOT_FOLLOWED` (free) | `followSitemapIndexes` was false | Leave it at the default (true) |
| Extractor: `outcome` `PARTIAL` in `SUMMARY` | A sitemap download failed or was cut off part-way; the rows that arrived are kept | Run again later; `sitemapErrors` names the file |
| Extractor: fewer URLs than expected | `maxUrlsPerSite`, the regex filters (case-sensitive), or `lastmodAfter` dropping pages without a date | Read `truncatedBy` and `filteredOut` in `SUMMARY` |
| Extractor: "newest N pages" are not the newest | The cap keeps the first matches in sitemap order | Narrow with `lastmodAfter`, keep the cap above the expected match count, then sort by `lastmod` |
| Error rows passed to Lighthouse | Error rows carry the site root or the sitemap file in `url` | Keep only rows with `errorCode` null before building `urls` |
| Lighthouse run `FAILED`: "No page URLs could be read from the sitemap" | Wrong or unreadable `sitemapUrl` | Use the extractor route with the website root |
| Lighthouse run `FAILED`: "Every audit failed" | All rows have an `errorCode`; nothing was charged | Read the `errorCode` values below |
| Lighthouse run `TIMED-OUT` (CLI `exitCode` 2) | Too many audits for the run timeout | See Run time above |
| `BLOCKED` (free) | HTTP 401, 403 or 429 | Report it. Do not retry; test a site the user controls or allow-lists |
| `HTTP_ERROR` (free) | 404, 5xx or another error status | Report as a broken sitemap entry |
| `TIMEOUT` (free) | The audit did not finish within `timeoutSecs` (default 120) | Raise `timeoutSecs` up to 300 for slow pages |
| `NOT_HTML` (free) | PDF, image or another non-HTML file | Exclude it in the extractor, for example `\.pdf$` in `excludePatterns` |
| `INCOMPLETE_AUDIT` (free) | DevTools throttling on a page that never stops loading | Use `throttlingMethod` `simulate` (the default) |
| `PSI_QUOTA`, `PSI_ERROR` (free) | The user's own PageSpeed Insights key ran out of quota or failed | The user fixes the key in Apify Console, or removes it to run Lighthouse in the Actor ($0.02 per audit) |
| `warnings` says the page loaded too slowly | The page never went idle (ads, analytics, chat widgets) | Scores are still computed with `simulate`; mention the warning next to that row |
| Scores differ by a few points between runs | Normal lab variance | Compare the median of several runs before calling a change a regression |

## Actor-specific notes

### `datatoolsforall/website-sitemap-extractor`

- `startUrls` accepts plain strings (`"https://example.com"`) or `{"url": ...}` objects. A page address is reduced to its website; http and https on one host count as one site, so it is not extracted or charged twice.
- Filters run before the cap: rows dropped by `includePatterns`, `excludePatterns` or `lastmodAfter` are neither stored nor charged.
- `lastmod` values with a time but no time zone are kept as written (no `Z`) and compared as UTC by `lastmodAfter`.
- `compareWithPreviousRun` with a schedule marks each row `new` or `unchanged` and adds `removed` rows (billed, counted against the cap). Useful for "audit only pages added since last week".
- Run summary: `apify key-value-stores get-value <KEY_VALUE_STORE_ID> SUMMARY --user-agent apify-awesome-skills/apify-website-performance-audit 2>/dev/null` (the store ID is `storage.defaultKeyValueStoreId` in the call output). This command returns the stored JSON as-is and has no `--json` flag.

### `datatoolsforall/bulk-lighthouse-pagespeed-audit`

- Lighthouse 13 runs inside the Actor in a fresh headless Chrome for each audit; no Google API key is needed.
- `url` in each row is the address exactly as passed, so rows match the input list; `finalUrl` is where the page ended after redirects.
- `categories` without `performance` gives no lab metrics and no opportunities.
- `psiApiKey` is a secret input. The skill never handles it; the user sets it in Apify Console. With it, `engine` is `pagespeed-insights` and `fieldData` carries CrUX p75 values where Google has data.
- `saveFullReport` stores the complete HTML report per page in the run's key-value store and links it in `reportUrl`.

### `apify/sitemap-extractor`

- Apify-maintained. Status checks (`checkPageStatus`) are on by default and send a HEAD request to every URL, which is slow on large sites; switch them off when only the list is needed.
- `lastmod` falls back to the page's `Last-Modified` header when the sitemap has none and status checks are on.
- No URL cap or filters in the input. Filter the rows after the run, and cap spend with the run's maximum cost or maximum items.
