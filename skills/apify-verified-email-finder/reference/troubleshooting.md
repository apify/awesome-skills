# Troubleshooting

## Auth / setup

- **`APIFY_TOKEN not found`** (script path only) — Create `.env` with `APIFY_TOKEN=...`; get the token from `https://console.apify.com/account/integrations`. Not needed on the MCP path.
- **`Actor not found`** — Confirm the ID is one of `compass/crawler-google-places`, `apify/google-search-scraper`, `vdrmota/contact-info-scraper`. The script converts `/` to `~` when calling the API; expected.

## Run-time

- **`Run FAILED`** — Open the console URL printed by the runner and read the Actor log. Most common cause: malformed input JSON.
- **Timeout** — Leads enrichment adds 30–90 s per domain on top of the base scrape. Raise the timeout (try 1500–1800 s). If the run is still progressing, the dataset already has partial results — pull by datasetId.
- **`Run TIMED-OUT` from Apify** — Lower source breadth (`maxCrawledPlacesPerSearch`, `maxRequestsPerStartUrl`, fewer queries).

## Empty / weak results

- **No verified rows after filter** — Re-render under `verified-plus-catchall` or `all-emails` scope. Catch-all SMTP servers can't be proven but often deliver.
- **No leads at all** — Try in order: bump `maximumLeadsEnrichmentRecords`; widen `leadsEnrichmentDepartments` to `[]`; confirm sources have reachable websites (Maps places without a `website` can't be enriched).
- **All leads dropped by spurious-match filter** — The enrichment service returned only global-fallback leads. There's no real fix — the source domain has no recognizable LinkedIn footprint. Surface the count and move on.
- **Empty SERP queries** — Confirm the keyword is non-empty and ≤ 32 words. Strip stray quotes.

## URL-list route

- **Blocked domain** — Set `useBrowser: true` in `vdrmota/contact-info-scraper` input. Raises cost but unblocks most anti-bot sites.
- **Invalid URL** — Pre-validate in Step 3; emit a `skipped — invalid URL` row. Never submit a bad URL to the Actor.

## Routing ambiguity

Ask one follow-up. Common patterns: SERP+URL-list pasted together → pick one or both; industry + no source → Maps or SERP?; industry + city without "Maps" → confirm route.

## Cost surprises

Pull the breakdown from the run console. Usual causes: `maximumLeadsEnrichmentRecords` too high, source breadth uncapped, `useBrowser: true` left on. Live rates are in the Apify console under the Actor's pricing tab; the 200-lead pre-submit warning rule lives in SKILL.md Step 3.
