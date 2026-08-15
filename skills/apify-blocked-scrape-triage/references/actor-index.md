# Actor index: what to reach for at each rung

All Actor IDs below were resolved against the public Apify Store API and are public at the time of writing. Always confirm the input schema before building an input:

    apify actors info "ACTOR_ID" --input --json \
      --user-agent apify-awesome-skills/apify-blocked-scrape-triage \
      2>/dev/null

## Routing

| Need | Actor ID | Tier | Notes |
|---|---|---|---|
| Static HTML, cheapest per page | `apify/cheerio-scraper` | apify | Start here. No browser, no JS execution. If the data is in the HTML, nothing else is cheaper. |
| Browser, Chrome, page function | `apify/web-scraper` | apify | Client-side rendering. One to two orders of magnitude more per page than Cheerio. |
| Browser, Playwright control | `apify/playwright-scraper` | apify | Multi-engine, complex interaction flows. |
| Browser, Puppeteer control | `apify/puppeteer-scraper` | apify | When existing Puppeteer logic is being ported. |
| Whole-site text for AI pipelines | `apify/website-content-crawler` | apify | Content harvesting, not field-level extraction. Wrong tool for structured records. |

## The inputs that matter when you are blocked

These fields exist on `apify/cheerio-scraper`, `apify/web-scraper`, `apify/playwright-scraper` and `apify/puppeteer-scraper` (checked against each Actor's published input schema).

| Field | Type | Why it matters here |
|---|---|---|
| `proxyConfiguration` | object | `{"useApifyProxy": true, "apifyProxyGroups": ["RESIDENTIAL"], "apifyProxyCountry": "US"}`. Groups and country are the two knobs; residential is a cost decision, not a default. |
| `proxyRotation` | string | `RECOMMENDED`, `PER_REQUEST`, `UNTIL_FAILURE`. See the table in `SKILL.md`; stateful flows need `UNTIL_FAILURE`. |
| `sessionPoolName` | string | Keeps sessions separate between runs that must not share cookies or IP affinity. |
| `initialCookies` | array | Carry cookies the site issues before the target page. |
| `preNavigationHooks` | string | Where request headers and their order are set. |
| `maxConcurrency` | integer | The first thing to lower. Most "detection" is rate. |
| `maxRequestRetries` | integer | Raise with backoff rather than hammering. |
| `pageLoadTimeoutSecs` | integer | A slow challenge page and a genuine timeout look the same in logs; separate them. |
| `ignoreSslErrors` | boolean | Diagnostic only. If this changes the outcome, an interception layer sits in the path. |
| `respectRobotsTxtFile` | boolean | Defaults to **false**. Turning it on is the right default for a crawl, and it also means a URL can vanish from your results for a reason that is not a block. |

Browser Actors additionally expose `headless`, `useChrome` and `waitUntil`; an incoherent combination of these with the proxy country is the classic self-inflicted block.

**Two things to know before the first browser run.** A browser Actor asks for full account access and refuses to start until that is approved in the Console, which stops an unattended flow dead. And its `pageFunction` context is not the raw Puppeteer or Playwright API: the `response` it hands you is a plain object with `status` and `headers`, the same shape `apify/cheerio-scraper` uses, so `response.status()` throws.

## Calling these from the CLI

`SKILL.md` describes the MCP path, which is how an agent normally runs these. If you have the CLI instead, the same diagnostic input goes in a file, and three flags belong on every call: `--json` for stable output, `--user-agent` for attribution, `2>/dev/null` so progress messages do not break JSON parsing.

```bash
apify actors call "apify/cheerio-scraper" --input-file diagnose.json \
  --json \
  --user-agent apify-awesome-skills/apify-blocked-scrape-triage \
  2>/dev/null
```

```bash
apify datasets get-items DATASET_ID --format json \
  --user-agent apify-awesome-skills/apify-blocked-scrape-triage \
  2>/dev/null
```

**The field names differ between the two paths**, which is a quiet way to lose an hour: the CLI reply carries `storage.defaultDatasetId` and `storage.defaultKeyValueStoreId`, while the MCP reply carries `storages.datasets.default.id`. Neither is `defaultDatasetId` on its own.

## What is deliberately not in this list

- Antidetect browsers and account-warming services. Out of scope for this skill.
- CAPTCHA-solving services. If a challenge is still the wall after the ladder, the answer is the "How this ends" section of `SKILL.md` (stop and reconsider the source), not automated solving.
- TLS-level impersonation libraries (uTLS, curl-impersonate). Named in `SKILL.md` as the correct tool class when the evidence points below the header layer, but they are not Apify Actors and are not routed here.
