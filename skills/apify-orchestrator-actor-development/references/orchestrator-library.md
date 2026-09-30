# apify-orchestrator library reference

The [`apify-orchestrator`](https://github.com/apify-projects/apify-orchestrator) library is an opinionated TypeScript wrapper around `apify` + `apify-client` for coordinating **many external Actor Runs from within a single parent Run**. Unlike rigid parallel-runner patterns, it lets you spawn Runs from anywhere in your code at any time.

> **Alpha release** — the library is at `0.x`. Pin the exact version in `package.json` and expect breaking changes on minor bumps.

## Installation

```bash
npm install apify-orchestrator apify apify-client
```

`apify` and `apify-client` are peer dependencies. Install a matching version of each.

## Core concepts

### `Orchestrator`
The singleton that owns the run scheduler, KVS persistence, log stream, and kill-switch behaviour.

```typescript
import { Orchestrator } from 'apify-orchestrator';

const orchestrator = new Orchestrator({
    enableLogs: true,                       // structured logs + periodic stats reports
    persistenceSupport: 'kvs',              // 'kvs' | 'none' — enables Run resurrection
    persistencePrefix: 'ORCH-',             // KVS record prefix
    abortAllRunsOnGracefulAbort: true,      // parent gracefully aborts → all child Runs aborted
    retryOnInsufficientResources: true,     // wait for memory/slots before launching
    // fixedInput: { ... },                 // deep-merged into every child Run's input
    // persistenceEncryptionKey: '...',     // optional at-rest encryption for persisted state
    // hideSensitiveInformation: true,      // scrubs secrets from stats reports
});
```

### `ExtendedApifyClient`
An extended `ApifyClient` returned by `orchestrator.apifyClient()`. Same API surface as the standard client plus orchestrator-aware verbs.

```typescript
const client = await orchestrator.apifyClient({
    name: 'MAIN',                           // clientName — persistence-critical (see gotchas)
    token: process.env.APIFY_TOKEN,         // optional — SDK picks it up automatically on Apify
});
```

## Verbs cheat sheet

| Verb | Behaviour |
|---|---|
| `client.actor(id).enqueue(...)` | Register Run(s) in scheduler; start later when resources allow. Returns names. |
| `client.actor(id).start(name, input?)` | Begin one Run; return `ActorRun` immediately (no wait). |
| `client.actor(id).call(name, input?)` | Begin one Run and **await** finish. This is the default for sequential pipelines. |
| `client.actor(id).callRuns(...requests)` | Begin multiple Runs in parallel, await all. Requests are `{ runName, input, options? }`. |
| `client.actor(id).callBatch(prefix, sources, inputGen, splitRules?)` | Auto-shard `sources` into multiple Runs when input exceeds Apify's 9 MiB payload cap. **Slow** — prefer `callRuns` when you already know the shape. |
| `client.dataset(id).iterate({ pageSize })` | Async generator over dataset items. **Required for large datasets** — plain `.listItems()` hits the V8 string cap. |
| `orchestrator.mergeDatasets(...datasets)` | Combine child-Run datasets; call `.iterate()` on the result. Iteration is sequential (A drained fully before B). |
| `client.abortAllRuns()` | Abort every tracked Run for this client. |

## Canonical orchestrator pattern

```typescript
import { Actor, log } from 'apify';
import { Orchestrator } from 'apify-orchestrator';

await Actor.init();

const orchestrator = new Orchestrator({
    enableLogs: true,
    persistenceSupport: 'kvs',
    persistencePrefix: 'ORCH-',
    abortAllRunsOnGracefulAbort: true,
});
const client = await orchestrator.apifyClient({ name: 'MAIN' });

// Sequential: run A, then run B with A's output
log.info('Starting step 1');
const runA = await client.actor('apify/website-content-crawler').call('step-1', {
    startUrls: [{ url: 'https://example.com' }],
});

log.info('Starting step 2');
const items = await client.dataset(runA.defaultDatasetId).listItems({ skipEmpty: true });
const runB = await client.actor('apify/rag-web-browser').call('step-2', {
    query: items.items.map(i => i.text).join('\n').slice(0, 4000),
});

// Emit combined output
for await (const item of client.dataset(runB.defaultDatasetId).iterate({ pageSize: 100 })) {
    await Actor.pushData(item);
}

await Actor.exit();
```

## Parallel fan-out

```typescript
const record = await client.actor('apify/website-content-crawler').callRuns(
    { runName: 'crawl-a', input: { startUrls: [{ url: 'https://a.com' }] } },
    { runName: 'crawl-b', input: { startUrls: [{ url: 'https://b.com' }] } },
);
// record === { 'crawl-a': ActorRun, 'crawl-b': ActorRun }

const merged = orchestrator.mergeDatasets(
    ...Object.values(record).map(r => client.dataset(r.defaultDatasetId)),
);
for await (const item of merged.iterate({ pageSize: 100 })) {
    await Actor.pushData(item);
}
```

## Kill-switch across accounts (Children Run Killer)

When you also control the child Actors' code, propagate the parent Run ID so a hard crash of the parent can still stop them:

```typescript
new Orchestrator({
    fixedInput: {
        __watched: {
            parentRunId: Actor.getEnv().actorRunId,
            apifyUserId: Actor.getEnv().userId,
        },
    },
});
```

`abortAllRunsOnGracefulAbort` only fires on graceful abort. Hard timeouts and crashes orphan child Runs — the `fixedInput` pattern above is your only durable guarantee.

## Gotchas

1. **Alpha version** — pin the exact version, expect breakage on minor bumps.
2. **`callBatch` is slow.** Its auto-split walks the input generator and probes sizes. If you already know a good shard shape, use `callRuns` with hand-authored `ActorRunRequest[]`.
3. **Client name is persistence-critical.** The KVS record key is `${persistencePrefix}${clientName}-RUNS`. Change the name and resurrection reattaches to nothing.
4. **`callBatch` name collision.** `namePrefix` is suffixed with `-1`, `-2`, etc. Don't reuse a prefix that also appears as a single-Run name in a `call`.
5. **`abortAllRunsOnGracefulAbort` only fires on graceful abort.** Hard crashes leak child Runs.
6. **`mergeDatasets` iterates sequentially.** Dataset A is drained fully before B begins. Not interleaved.
7. **`iterate({ pageSize })` is required for large datasets.** Plain `listItems()` returns everything in one string and hits the V8 `0x1fffffe8`-char cap.

## Sources

- Repo: <https://github.com/apify-projects/apify-orchestrator>
- Types: <https://raw.githubusercontent.com/apify-projects/apify-orchestrator/main/src/types.ts>
