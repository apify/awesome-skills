# Actor A - the scheduled scraper

Actor A runs on a schedule, produces structured records, and accumulates them in a **named** dataset that Actor B reads. Named storages are kept until deleted; unnamed (default) ones expire with the run's data retention.

Suggested layout:

```
src/
  main.ts      # init, input, storages, crawler, aborting handler
  routes.ts    # router handlers, writeRecord(), pushEnrichmentFailure()
  record.ts    # the shared IndexRecord interface + buildRecord()
  markdown.ts  # htmlToMarkdown() (optional, Pattern 4)
```

The record type is the contract between the two Actors. Copy the same file into Actor B; every field is nullable because sources drop values without warning:

```ts
// record.ts (example - adapt fields in Step 0)
export interface IndexRecord {
    id: string;                     // stable key: canonical URL or source ID
    name: string | null;
    description: string | null;
    sector: string | null;
    amount: number | null;
    date: string | null;            // YYYY-MM-DD, sortable as a string
    url: string | null;
    websiteMarkdown: string | null; // Pattern 4
    enrichmentError: string | null; // Pattern 3
    scrapedAt: string;              // ISO timestamp
}

export function buildRecord(p: Partial<IndexRecord> & { id: string }): IndexRecord {
    return {
        name: null, description: null, sector: null, amount: null, date: null, url: null,
        websiteMarkdown: null, enrichmentError: null,
        ...p,
        scrapedAt: new Date().toISOString(),
    };
}
```

## Pattern 1 - Dual-write so the Output tab is not empty

A named dataset is right for cross-run accumulation, but Apify Console's **Output tab** templates against `links.apiDefaultDatasetUrl`. Write only to the named dataset and the Output tab shows nothing. Write every record to both:

```ts
// routes.ts
import { Actor, Dataset } from 'apify';
import type { IndexRecord } from './record.js';

export interface RouterContext {
    namedDataset: Dataset<IndexRecord>;
    seen: Set<string>;
}

export async function writeRecord(ctx: RouterContext, record: IndexRecord) {
    await Promise.all([
        ctx.namedDataset.pushData(record), // cross-run accumulation, read by Actor B
        Actor.pushData(record),            // this run's default dataset → Output tab
    ]);
}
```

```ts
// main.ts
const DEFAULT_DATASET_NAME = 'my-named-dataset'; // constant, not a hidden input
const namedDataset = await Actor.openDataset<IndexRecord>(input.datasetName ?? DEFAULT_DATASET_NAME);
```

Actor A owns the dataset, so opening it by name (get-or-create) is fine here. Actor B must not do that - see [index-actor.md](index-actor.md) Pattern 7.

Named dataset names: lowercase letters, digits and `-`, unique per account. Decide the name once in Step 0 and reuse it everywhere.

## Pattern 2 - Idempotent scheduled scraper via a seen-set KV store

A named KV store survives across runs. Load the seen-set at start, filter listings against it **before** enqueuing detail pages, and persist it as you go:

```ts
const STATE_STORE_NAME = 'my-scraper-state';
const SEEN_KEY = 'seen-items';

const seenStore = await Actor.openKeyValueStore(STATE_STORE_NAME);
const seen = new Set<string>(input.forceReprocess ? [] : ((await seenStore.getValue<string[]>(SEEN_KEY)) ?? []));

async function persistSeen() {
    await seenStore.setValue(SEEN_KEY, [...seen]);
}

// listing handler: only enqueue unseen items
const fresh = urls.filter((u) => !seen.has(u));
await enqueueLinks({ urls: fresh, label: 'DETAIL' });

// detail handler, after writeRecord():
seen.add(request.url);
```

Persist on a cadence and on shutdown, not after every item (each `setValue` rewrites the whole array):

```ts
setInterval(() => void persistSeen(), 60_000);
Actor.on('aborting', async () => {
    await persistSeen();
    await Actor.exit();
});
// after crawler.run():
await persistSeen();
```

Expose `forceReprocess` (boolean, default `false`) in the input schema for backfills. Use a stable key per item (canonical URL or source ID), not a URL with tracking parameters. If the set grows past a few hundred thousand entries, shard it (`seen-items-0`, `seen-items-1`, ...) - a KV record is capped at 9 MB.

## Pattern 3 - Persist partial records on fetch failure

When enrichment (visiting a company website, downloading a document) fails after retries, you still have the record from the upstream handler in `request.userData`. Don't lose it:

```ts
// routes.ts
export async function pushEnrichmentFailure(ctx: RouterContext, userData: Partial<IndexRecord>, reason: string) {
    await writeRecord(ctx, buildRecord({ ...userData, id: userData.id as string, enrichmentError: reason }));
}

// main.ts
const crawler = new CheerioCrawler({
    proxyConfiguration: await Actor.createProxyConfiguration(input.proxyConfiguration),
    requestHandler: router,
    failedRequestHandler: async ({ request }, error) => {
        if (request.label === 'ENRICH') {
            await pushEnrichmentFailure(ctx, request.userData, (error as Error).message);
            ctx.seen.add(request.userData.id as string);
        }
    },
});
```

Pass everything the record needs through `userData` when enqueuing the enrichment request. Add `enrichmentError: string | null` to the record type and to `dataset_schema.json`. On success set it to `null` explicitly, so the column is always present.

Decide with the user whether a failed item is marked seen. Marking it avoids hammering a dead site every run; not marking it retries next run. Default: mark seen, and let `forceReprocess` cover backfills.

## Pattern 4 - HTML → Markdown enrichment via turndown

```ts
// markdown.ts
import TurndownService from 'turndown';

const turndown = new TurndownService({ headingStyle: 'atx', codeBlockStyle: 'fenced', bulletListMarker: '-' });
turndown.remove(['script', 'style', 'noscript', 'iframe']);
turndown.addRule('drop-svg', { filter: 'svg' as never, replacement: () => '' });

const MARKDOWN_MAX_CHARS = 200_000;

export function htmlToMarkdown(html: string): string {
    const md = turndown.turndown(html).trim();
    return md.length <= MARKDOWN_MAX_CHARS ? md : `${md.slice(0, MARKDOWN_MAX_CHARS)}\n\n[...truncated]`;
}
```

Only convert when the response is HTML:

```ts
const contentType = String(response?.headers?.['content-type'] ?? '');
const websiteMarkdown = contentType.includes('html') ? htmlToMarkdown(body.toString()) : null;
```

Keep the cap: dataset items are limited to 9 MB each, and huge Markdown blobs make Actor B's scans slow and expensive. Make `MARKDOWN_MAX_CHARS` an input field if users need to tune it.

## Input fields Actor A typically needs

| Field | Type / editor | Default | Notes |
|---|---|---|---|
| `startUrls` or source filters | array / `requestListSources` | prefill only | |
| `maxItems` | integer / `number` | `100` | Stop enqueuing past it |
| `forceReprocess` | boolean / `checkbox` | `false` | Pattern 2 |
| `fromDate` | string / `datepicker` | - | Stores `YYYY-MM-DD` |
| `proxyConfiguration` | object / `proxy` | `{ "useApifyProxy": true }` | Confirm paid proxy use with the user |
| `datasetName` | string / `textfield` | the constant | Only if users really need to redirect output; otherwise a constant |

## Done checklist (Actor A)

- [ ] Every write goes through `writeRecord()` (named + default).
- [ ] Seen-set loads at start, filters before enqueue, persists on interval, on `aborting`, and at the end.
- [ ] `failedRequestHandler` writes partial records with `enrichmentError`.
- [ ] IndexRecord type, `buildRecord()` and `dataset_schema.json` list the same fields.
- [ ] Results counted with your own tally, not `Dataset.getInfo()` (it lags on the platform).
