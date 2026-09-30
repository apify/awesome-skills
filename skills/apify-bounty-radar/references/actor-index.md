# Optional Apify discovery and terms capture

GitHub API evidence must establish issue/PR state and discussion coverage. These public Apify-maintained Actors add web discovery or one off-GitHub terms page; neither replaces that verification.

| Need | Actor | Inspect in output |
|---|---|---|
| Supplementary search for candidate URLs or public project terms | [apify/google-search-scraper](https://apify.com/apify/google-search-scraper) | `organicResults[]`: `title`, `url`, `description`; not live issue status |
| Read one public static terms page | [apify/website-content-crawler](https://apify.com/apify/website-content-crawler) | `url`, `markdown`, `text`, crawl status; empty text is a failed evidence fetch |

## Inspect before a paid call

Use the current Actor schema and pricing, not fields inferred from another Actor with a similar name. The public, read-only build endpoints provide `data.inputSchema` (a JSON string):

- [Google default-build schema](https://api.apify.com/v2/acts/apify~google-search-scraper/builds/default)
- [Crawler default-build schema](https://api.apify.com/v2/acts/apify~website-content-crawler/builds/default)

At validation on 2026-09-30, Google build `0.0.451` accepts `queries`, `maxPagesPerQuery`, lowercase `countryCode: "us"`, and `languageCode: "en"`; it has no `resultsPerPage`. Crawler build `0.3.97` requires both `startUrls` and `proxyConfiguration`. Recheck before running because schemas and pricing can change. Pin the inspected build number with the run `build` parameter.

Confirm the user's available budget before any optional paid execution. The default $1 ceiling permits at most the two $0.50 runs below; it is a maximum, not a target. If the remaining budget is below the Actor's minimum supported cap, skip the run. Do not silently increase the ceiling. Disable search add-ons; do not multiply enrichment by result domains.

The $1 default is not spending authorization. If the user's remaining budget is below $0.50 (for example, $0.30), do not copy either $0.50 example unchanged: lower `maxTotalChargeUsd` to the remaining budget only if the Actor supports that cap; otherwise skip the paid run and continue with the free GitHub API.

## Bounded Google input

Save as `search-input.json`, replacing the phrase with one narrow public search. GitHub `is:`/`label:` operators belong in GitHub Search, not this string.

```json
{
  "queries": "site:github.com \"bounty\" \"Python\"",
  "maxPagesPerQuery": 1,
  "countryCode": "us",
  "languageCode": "en",
  "focusOnPaidAds": false,
  "maximumLeadsEnrichmentRecords": 0,
  "aiOverview": {"scrapeFullAiOverview": false},
  "aiModeSearch": {"enableAiMode": false},
  "websiteContentScraper": {"enable": false}
}
```

Other optional AI/prospecting add-ons must remain disabled in the inspected schema/default input. Google returns SERP records containing `organicResults`, so an item limit is not the number of organic links. Filter/deduplicate URLs before API inspection.

## Bounded static-page input

Save as `crawl-input.json`, replacing the example with one already-verified public terms URL. Do not point this at a GitHub issue, PR, directory, dashboard, login, or payment page.

```json
{
  "startUrls": [{"url": "https://example.com/terms"}],
  "proxyConfiguration": {"useApifyProxy": false},
  "crawlerType": "cheerio",
  "maxCrawlPages": 1,
  "maxCrawlDepth": 0,
  "maxConcurrency": 1,
  "initialConcurrency": 1,
  "maxRequestRetries": 0,
  "maxSessionRotations": 0,
  "requestTimeoutSecs": 30,
  "useSitemaps": false,
  "useLlmsTxt": false,
  "saveFiles": false,
  "saveScreenshots": false,
  "saveMarkdown": true
}
```

No proxy/browser fallback is automatic. Treat missing content, blocked requests, or JavaScript-only terms as unverified.

## Run-level dollar and time backstops

`maxTotalChargeUsd` and `timeout` are **run query parameters**, not Actor input fields. The [Run Actor API](https://docs.apify.com/api/v2/actors-runs-post) documents the dollar limit for all pricing models. `maxItems` only limits charged items for pay-per-result Actors; it is not a general cost cap. `waitForFinish` only limits how long the request waits, so it cannot replace the run timeout.

Example after confirming the schema, build, and budget; the environment variable is sent only in the Authorization header:

```bash
curl --fail-with-body --silent --show-error --max-time 30 \
  -X POST 'https://api.apify.com/v2/acts/apify~google-search-scraper/runs?build=0.0.451&maxTotalChargeUsd=0.50&timeout=120&restartOnError=false' \
  -H "Authorization: Bearer ${APIFY_TOKEN}" \
  -H 'Content-Type: application/json' \
  -H 'User-Agent: apify-awesome-skills/apify-bounty-radar' \
  --data-binary @search-input.json
```

For the one allowed crawl, after checking the remaining budget:

```bash
curl --fail-with-body --silent --show-error --max-time 30 \
  -X POST 'https://api.apify.com/v2/acts/apify~website-content-crawler/runs?build=0.3.97&maxTotalChargeUsd=0.50&timeout=120&restartOnError=false' \
  -H "Authorization: Bearer ${APIFY_TOKEN}" \
  -H 'Content-Type: application/json' \
  -H 'User-Agent: apify-awesome-skills/apify-bounty-radar' \
  --data-binary @crawl-input.json
```

Never omit either the dollar limit or run timeout for a retry. A timed-out HTTP request may already have started a billed run: inspect existing runs before retrying the POST.

Store `data.id` and `data.defaultDatasetId` from the response. Poll `GET /v2/actor-runs/{runId}` with the same Authorization and User-Agent headers until terminal status. If returned options do not reflect the requested cap/timeout, abort through `POST /v2/actor-runs/{runId}/abort` and stop. Do not start another run to compensate.

After `SUCCEEDED`, read `GET /v2/datasets/{datasetId}/items?format=json&clean=true&limit=100`. Verify the dataset actually contains the requested evidence. Record `usageTotalUsd` and any pricing-model-specific charge totals returned by the run; unknown cost stays unknown and prevents a second run until the remaining budget is known. Recheck run details after costs settle (the API documents a short delay), rather than reporting a preliminary zero as the final cost. On failure/timeout/budget stop, preserve partial results and report the failure without automatic retries.
