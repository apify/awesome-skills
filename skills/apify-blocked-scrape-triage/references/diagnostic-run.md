# The diagnostic run: input, output, and the fields that answer Step 2

`SKILL.md` says what to look at. This file is the ready-made run that produces it, plus the places the platform hides something you will need.

## Start with the small input, not the big one

Through the MCP server this whole object is the `input` argument to `call-actor` with `actor: "apify/cheerio-scraper"`; through the CLI it is `diagnose.json`. Either way, **start here**: this object validates as it stands, measured on the first attempt, escaped `pageFunction` and hook included. Start from it and add one field at a time, because when a larger input is rejected the message is `Validation errors: must be object`, it names no field, and its wording points at the wrong thing entirely, see the note under the full input:

```json
{
  "startUrls": [{ "url": "https://example.com/" }],
  "proxyConfiguration": { "useApifyProxy": true },
  "maxRequestRetries": 0,
  "maxConcurrency": 1,
  "preNavigationHooks": "[async ({ session }) => { if (session) { const retire = session.retireOnBlockedStatusCodes.bind(session); session.retireOnBlockedStatusCodes = (code, extra) => { retire(code, extra); return false; }; } }]",
  "pageFunction": "async function pageFunction(context) { const r = context.response || {}; const h = r.headers || {}; const body = String(context.body || ''); return { url: context.request.url, loadedUrl: context.request.loadedUrl, status: r.status, cfMitigated: h['cf-mitigated'], bytes: body.length, title: context.$('title').text().trim().slice(0, 80) }; }"
}
```

Six fields answer the first two rows of Step 2, which is where most investigations end. Grow to the full version below only when the answer is a `200` and you have to tell a shell from a brochure.

**If your target serves JSON rather than HTML**, the field that fixes it is `"additionalMimeTypes": ["application/json", "text/plain"]`, because without it the Actor skips the response and the endpoint looks broken when it is not. **Through MCP that field is rejected in every encoding measured**: an array gives `Validation errors: must be object`, the array as a JSON string gives the same, an object gives `must be array`, and the build schema declares it an array. Everything else here validates alongside it, so when a run is rejected, this is the field to pull first. Workarounds are in Rung 4 of `SKILL.md`: ask the service for an HTML representation, or fetch the endpoint with your own code.

## The full input

The `preNavigationHooks` line is the one from `SKILL.md`, and without it every refusal arrives as an empty item.

```json
{
  "startUrls": [{ "url": "https://example.com/" }],
  "proxyConfiguration": { "useApifyProxy": true },
  "maxRequestRetries": 0,
  "maxConcurrency": 1,
  "preNavigationHooks": "[async ({ session }) => { if (session) { const retire = session.retireOnBlockedStatusCodes.bind(session); session.retireOnBlockedStatusCodes = (code, extra) => { retire(code, extra); return false; }; } }]",
  "pageFunction": "async function pageFunction(context) { const $ = context.$; const r = context.response || {}; const h = r.headers || {}; const host = new URL(context.request.url).hostname; const links = $('a[href^=\"http\"]').map((i, el) => { try { return new URL($(el).attr('href')).hostname; } catch (e) { return null; } }).get().filter(Boolean); const offHost = links.filter(x => x !== host); const tally = {}; offHost.forEach(x => { tally[x] = (tally[x] || 0) + 1; }); const topOffHost = Object.entries(tally).sort((a, b) => b[1] - a[1]).slice(0, 5); return { url: context.request.url, loadedUrl: context.request.loadedUrl, status: r.status, cfMitigated: h['cf-mitigated'], etag: h.etag, server: h.server, via: h.via, cfRay: h['cf-ray'], xCache: h['x-cache'], retryAfter: h['retry-after'], setCookie: h['set-cookie'] ? String(h['set-cookie']).slice(0, 200) : null, contentType: h['content-type'], bytes: context.body ? context.body.length : 0, title: $('title').text().trim().slice(0, 80), mountPoints: $('#root, #app, #vue-app, [id^=\"__next\"]').length, scripts: $('script[src]').length, offHostLinks: offHost.length, topOffHost: topOffHost, bodyHead: String(context.body || '').replace(/\\s+/g, ' ').slice(0, 300) }; }"
}
```

Which field decides what:

- `status` and `cfMitigated` separate a hard block from a managed challenge, the first two rows of Step 2.
- `etag` and `bytes` run the shell test: an SPA shell returns the same bytes and the same `ETag` for two different record ids.
- `offHostLinks` and `topOffHost` separate a shell from a brochure.
- `bodyHead` catches meta-refresh stubs, stock server pages and soft 404s without a second request.
- `loadedUrl` catches the site that moved. Compare it with `url` every time.

**To measure a rate rather than an outcome**, repeat one URL in `startUrls` with distinct `uniqueKey` values. Six entries, one run, six independent proxy draws, sub-cent.

## The response object is not the raw client's

In `apify/cheerio-scraper` the `response` handed to a `pageFunction` carries exactly two keys, `status` and `headers`. There is no `statusCode`; asking for one returns undefined rather than throwing, which is how it goes silently missing from a diagnostic. The browser Actors hand you the same shape, so `response.status()` throws there instead of returning a number.

The platform also writes its own view into every dataset item: `#debug.statusCode`, `#debug.retryCount`, `#debug.errorMessages` and `#debug.loadedUrl`. When an item arrives with `#error: true` and nothing else, `#debug.errorMessages` is the only thing that says what happened.

## Reading the reply, whichever interface you are on

| What you want | MCP | CLI |
|---|---|---|
| the dataset to read | `storages.datasets.default.id` | `storage.defaultDatasetId` |
| the store holding run counters | `storages.keyValueStores.default.id` | `storage.defaultKeyValueStoreId` |
| the items | `get-dataset-items` with that id | `apify datasets get-items <id> --format json` |

**The item count in that reply undercounts**, because it is read while the run is still flushing. Measured three times in one afternoon: a reply reporting one item belonged to a dataset holding six, and another reporting four belonged to one holding six. Read the dataset before concluding anything about how many items a run produced.

## Getting the input schema, which is not where you would expect

`apify actors info <actor> --input --json` returns the Actor record, with the schema nested inside it as an escaped string under `taggedBuilds.<tag>.build.inputSchema`, so grepping that output for a field name finds nothing. The direct route works from either interface and returns it as JSON:

```bash
curl -s "https://api.apify.com/v2/acts/apify~cheerio-scraper/builds/default" \
  | python -c "import json,sys; print(sorted(json.load(sys.stdin)['data']['actorDefinition']['input']['properties']))"
```

## Where the request counters actually live

They are not in the call reply and not in `apify runs info`, whose `stats` holds duration, compute units and memory only. Take the key-value store id (see the table above) and read:

```bash
curl -s "https://api.apify.com/v2/key-value-stores/KV_STORE_ID/records/SDK_CRAWLER_STATISTICS_0"
```

`requestsFinished`, `requestsFailed` and `requestsRetries` are in there, and so is `requestsWithStatusCode`, a histogram naming the status codes the run actually received. A run can finish `SUCCEEDED` with `exitCode 0` while some requests failed, so read this before concluding anything from a short dataset. Once the hook above is in place the dataset itself answers most of these questions, and the counters are the cross-check rather than the source.

## What the un-blinding hook is worth, measured

Six identical requests to one challenged vendor platform, one run each, same proxy pool, `PER_REQUEST` rotation:

| Hook | Items carrying fields | Refusals classified | Requests that got through |
|---|---|---|---|
| none | 3 of 6 | 0, three empty error items | 3 |
| `gotOptions.throwHttpErrors = false` only | 1 of 6 | 0, five empty error items | 1 |
| retire and return false | **6 of 6** | **2, both `cf-mitigated: challenge`** | 4 |
| never retire | 6 of 6 | 6 | **0** |

`throwHttpErrors` is the flag people reach for, and on this failure it changes nothing: Crawlee is not throwing because got threw, it is throwing because the session pool treats 401, 403 and 429 as blocking. Dropping the retire call unblinds the run and costs every request that would have succeeded, because the pool stops rotating away from addresses the site has already refused.

**Take the hook out once the refusal is classified.** Left in, a crawl writes challenge pages into the dataset as if they were records.
