# Actor B - the index / search Actor

Actor B reads Actor A's named dataset and returns the records that match a set of filters. One codebase, two entry points:

| Mode | Triggered by | Input | Output | Lifetime |
|---|---|---|---|---|
| Standard (one-shot) | Console, API, schedule, `apify actors call` | `INPUT` (input schema) | Default dataset | Pushes results, then `Actor.exit()` |
| Standby (HTTP API) | Request to `https://<user>--<actor>.apify.actor` | Query params | JSON response | Stays alive, serves many requests |

Suggested layout:

```
src/
  main.ts      # mode detection, runOneShot(), runStandby()
  source.ts    # openSourceDatasetReader() (Pattern 7)
  search.ts    # Filters, parseFilters(), searchDataset()
  charge.ts    # chargeResults() (Pattern 8)
  record.ts    # the shared IndexRecord interface (copied from Actor A)
```

## Pattern 5 - Standard + Standby dual-mode Actor

Detect the mode from the environment and branch early.

```json
// .actor/actor.json (excerpt)
{ "usesStandbyMode": true, "webServerSchema": "./openapi.json" }
```

```ts
// src/main.ts
import { Actor, log } from 'apify';
import express from 'express';
import { openSourceDatasetReader } from './source.js';
import { FilterError, parseFilters, searchDataset, type Filters } from './search.js';
import { chargeResults } from './charge.js';

await Actor.init();
const isStandby = process.env.APIFY_META_ORIGIN === 'STANDBY';
const reader = await openSourceDatasetReader();

if (isStandby) {
    await runStandby(); // starts Express, never calls Actor.exit()
} else {
    await runOneShot();
    await Actor.exit();
}

async function runOneShot() {
    const input = (await Actor.getInput<Partial<Filters>>()) ?? {};
    const filters = parseFilters(input);
    const results = await searchDataset(reader, filters);
    const { allowed } = await chargeResults(results.length);
    await Actor.pushData(results.slice(0, allowed));
    log.info(`Returned ${allowed} of ${results.length} matching records`);
}

async function runStandby() {
    const app = express();
    const port = Number(Actor.config.get('containerPort') ?? 4321);

    app.get('/', (req, res) => {
        // Readiness probe - must answer 200 quickly
        if (req.headers['x-apify-container-server-readiness-probe']) {
            res.status(200).type('text/plain').send('OK\n');
            return;
        }
        res.status(200).type('text/plain').send('API ready - see /search\n');
    });

    app.get('/search', async (req, res) => {
        try {
            const filters = parseFilters(req.query as Record<string, unknown>);
            const results = await searchDataset(reader, filters);
            const { allowed } = await chargeResults(results.length);
            res.json({ count: allowed, total: results.length, items: results.slice(0, allowed) });
        } catch (err) {
            if (err instanceof FilterError) {
                res.status(400).json({ error: err.message });
                return;
            }
            log.exception(err as Error, 'Search failed');
            res.status(500).json({ error: 'Internal error' });
        }
    });

    app.listen(port, () => log.info(`Standby server listening on ${port}`));
}
```

Rules:

- **Never** call `Actor.exit()` in the Standby branch, not even after an error - the platform kills the container and the next request cold-starts.
- Listen on `Actor.config.get('containerPort')` (env `ACTOR_WEB_SERVER_PORT`), never a hardcoded port in production.
- `GET /` must return 200 for the `x-apify-container-server-readiness-probe` header.
- Both branches call the **same** `searchDataset()` and `chargeResults()` so the API and the batch run cannot drift apart.
- Return 400 with a message for invalid filters; never echo raw stack traces to callers.

## Shared search logic

Inputs come from two places with different types (input JSON gives numbers and booleans, query strings give strings). Normalise once:

```ts
// src/search.ts
import type { DatasetReader } from './source.js';
import type { IndexRecord } from './record.js';

export class FilterError extends Error {}

export interface Filters {
    sector?: string;
    minAmount?: number;
    fromDate?: string; // YYYY-MM-DD
    query?: string;
    limit: number;
}

const DEFAULT_LIMIT = 100;
const MAX_LIMIT = 1000;

function num(v: unknown, name: string): number | undefined {
    if (v === undefined || v === null || v === '') return undefined;
    const n = Number(v);
    if (!Number.isFinite(n)) throw new FilterError(`${name} must be a number`);
    return n;
}

export function parseFilters(raw: Record<string, unknown>): Filters {
    const fromDate = raw.fromDate ? String(raw.fromDate) : undefined;
    if (fromDate && !/^\d{4}-\d{2}-\d{2}$/.test(fromDate)) throw new FilterError('fromDate must be YYYY-MM-DD');
    const limit = Math.min(num(raw.limit, 'limit') ?? DEFAULT_LIMIT, MAX_LIMIT);
    if (limit < 1) throw new FilterError('limit must be at least 1');
    return {
        sector: raw.sector ? String(raw.sector).toLowerCase() : undefined,
        minAmount: num(raw.minAmount, 'minAmount'),
        fromDate,
        query: raw.query ? String(raw.query).toLowerCase() : undefined,
        limit,
    };
}

function matches(r: IndexRecord, f: Filters): boolean {
    if (f.sector && r.sector?.toLowerCase() !== f.sector) return false;
    if (f.minAmount !== undefined && (r.amount ?? -Infinity) < f.minAmount) return false;
    if (f.fromDate && (r.date ?? '') < f.fromDate) return false;
    if (f.query && !`${r.name ?? ''} ${r.description ?? ''}`.toLowerCase().includes(f.query)) return false;
    return true;
}

const PAGE_SIZE = 1000;

export async function searchDataset(reader: DatasetReader, f: Filters): Promise<IndexRecord[]> {
    const out: IndexRecord[] = [];
    const seenIds = new Set<string>();
    const { total } = await reader.getData({ offset: 0, limit: 1 });
    // Walk pages from the end with ascending offsets: newest records first,
    // and the loop always terminates at offset 0.
    for (let end = total; end > 0 && out.length < f.limit; end -= PAGE_SIZE) {
        const offset = Math.max(end - PAGE_SIZE, 0);
        const { items } = await reader.getData({ offset, limit: end - offset });
        for (const r of items.reverse()) {
            if (seenIds.has(r.id)) continue; // named dataset is append-only: dedupe by key
            seenIds.add(r.id);
            if (matches(r, f)) out.push(r);
            if (out.length >= f.limit) break;
        }
    }
    return out;
}
```

Notes:

- **Don't page with `desc: true` + `offset`.** Local storage ignores `offset` when `desc` is set and returns the whole dataset on every call, so a "loop until an empty page" scan never ends and the request hangs whenever fewer records match than `limit`. Reading ascending pages from `total` backwards behaves the same locally and on the platform.
- A dataset is append-only, so the same item can appear twice (e.g. after a `forceReprocess` backfill). Dedupe by a stable key, reading newest first.
- For datasets up to a few hundred thousand items a paged scan per request is fine. Beyond that, in Standby, cache an in-memory index built at startup and refresh it on an interval (e.g. every 10 minutes) instead of scanning per request; in standard mode keep the scan.
- Keep every filter in one `Filters` type, and mirror it in both `input_schema.json` and `openapi.json` (see [schemas.md](schemas.md)).

## Pattern 7 - Cross-Actor named dataset access under LIMITED_PERMISSIONS

**The trap**: `Actor.openDataset('some-name')` calls `POST /v2/datasets` (get-or-create) under the hood. Actors run with `LIMITED_PERMISSIONS` by default, and that POST returns **403** even when the dataset exists and the same user owns it. Adding a secret token alone is not enough - the POST itself is what's denied.

**Fix - pin the dataset ID** and do a plain GET:

```ts
// src/source.ts
import { Actor } from 'apify';
import type { IndexRecord } from './record.js';

const SOURCE_DATASET_NAME = 'my-named-dataset'; // constant, same as Actor A
const DATASET_ID_ENV = 'SOURCE_DATASET_ID';      // plain env var, set in Console
const OWNER_TOKEN_ENV = 'SOURCE_OWNER_TOKEN';    // optional secret env var

export interface DatasetReader {
    // Ascending pages only; `total` is the dataset's item count
    getData(opts: { offset: number; limit: number }): Promise<{ items: IndexRecord[]; total: number }>;
}

export async function openSourceDatasetReader(): Promise<DatasetReader> {
    const datasetId = process.env[DATASET_ID_ENV];
    const token = process.env[OWNER_TOKEN_ENV];

    if (datasetId) {
        // Preferred: a GET by ID works under LIMITED_PERMISSIONS
        const client = token ? Actor.newClient({ token }) : Actor.apifyClient;
        const dsc = client.dataset(datasetId);
        return {
            getData: async (opts) => {
                const { items, total } = await dsc.listItems(opts);
                return { items: items as unknown as IndexRecord[], total };
            },
        };
    }

    if (token) {
        // Fallback by name - needs a token allowed to write datasets
        const client = Actor.newClient({ token });
        const info = await client.datasets().getOrCreate(SOURCE_DATASET_NAME);
        const dsc = client.dataset(info.id);
        return {
            getData: async (opts) => {
                const { items, total } = await dsc.listItems(opts);
                return { items: items as unknown as IndexRecord[], total };
            },
        };
    }

    // Local dev (storage/datasets/<name>/) or FULL_PERMISSIONS runs
    const ds = await Actor.openDataset<IndexRecord>(SOURCE_DATASET_NAME);
    return {
        getData: async (opts) => {
            const { items, total } = await ds.getData(opts);
            return { items, total };
        },
    };
}
```

Log which branch was taken at startup (without the token) - it is the first thing to check when B returns nothing.

**One-time setup the user does**: Apify Console → **Storage → Datasets → `<name>`** → copy the 17-character ID → Actor B → **Source → Environment variables** → add `SOURCE_DATASET_ID = <id>` (plain, not secret) → rebuild. If the owner token is used, add it with the **Secret** toggle on, or locally with `apify secrets add` and reference it as `"@name"` in `actor.json` `environmentVariables`.

If Actor B is public, every user reads the **owner's** dataset by ID - that is the point. Make sure the dataset holds nothing you would not sell, and never expose the owner token through responses or logs.

## Pattern 8 - Pay-per-event charging

```ts
// src/charge.ts
import { Actor, log } from 'apify';

const EVENT_NAME = 'result';

export async function chargeResults(count: number): Promise<{ allowed: number }> {
    if (count === 0) return { allowed: 0 };
    try {
        const res = await Actor.charge({ eventName: EVENT_NAME, count });
        // When the user's spending limit is hit, only part of the count is charged
        if (res.eventChargeLimitReached) {
            log.warning('Charge limit reached - truncating results');
            return { allowed: res.chargedCount ?? 0 };
        }
        return { allowed: count };
    } catch (err) {
        // Older SDKs and misconfigured events can throw - never crash the run over billing
        log.warning(`Actor.charge failed (safe to ignore locally): ${(err as Error).message}`);
        return { allowed: count };
    }
}
```

- Charge from **both** the standard and the Standby branch so pricing works in either mode.
- Locally (and on the platform before PPE pricing is set up) `apify ^3.8` does not throw: it logs `Ignored attempt to charge for an event - the Actor does not use the pay-per-event pricing` and the charge is a no-op. Keep the try/catch anyway.
- Charge only for records actually returned; never for an empty search.
- The `result` event and its per-unit price are configured in **Apify Console → Actor → Publication → Monetization → Pay-per-event** after the first push - not in `actor.json`. The event name in code must match Console exactly.
- Check the exact shape of the object `Actor.charge()` returns in your SDK version (`apify ^3.7`) and adjust the `chargedCount` read if needed; the stop-on-`eventChargeLimitReached` behaviour is what matters.

## Done checklist (Actor B)

- [ ] `APIFY_META_ORIGIN === 'STANDBY'` branch never exits; standard branch exits.
- [ ] Readiness probe answers 200 on `GET /`.
- [ ] One `searchDataset()` and one `chargeResults()` used by both branches.
- [ ] Source dataset read by pinned ID when `SOURCE_DATASET_ID` is set; startup log says which branch.
- [ ] `limit` capped; invalid filters return 400 in Standby and fail the run with a clear message in standard mode.
- [ ] Every filter appears in `input_schema.json` and `openapi.json` with the same name.
