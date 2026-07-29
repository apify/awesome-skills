# Orchestrator Actor: canonical `src/main.ts` template

This is the shape the agent should generate for the orchestrator's entry point. Fill in the placeholders (`<...>`) based on the sub-Actor schemas fetched during the interactive flow.

## Template

```typescript
import { Actor, log } from 'apify';
import { Orchestrator } from 'apify-orchestrator';

// -------------------------------------------------------------------------
// Input & sub-Actor input types
// -------------------------------------------------------------------------

// List every sub-Actor step that spends money. The total cap is divided
// evenly across this tuple — see references/cost-tracking.md for the rationale.
const STEPS = ['step1', 'step2'] as const;
type Step = (typeof STEPS)[number];

interface OrchestratorInput {
    // Top-level fields exposed to the orchestrator's own input schema.
    // Derive these from the sub-Actors' REQUIRED fields that shouldn't be hardcoded.
    // Do NOT add a cost cap or stepBudgets field here — the TOTAL cap is the
    // Run's own maxTotalChargeUsd option, and the split is the compile-time
    // even distribution defined by STEPS above.
    startUrls: { url: string }[];
    maxItems?: number;
}

// One interface per sub-Actor, mirroring its input schema (from Apify MCP fetch-actor-details).
interface StepOneInput {
    startUrls: { url: string }[];
    maxCrawlDepth?: number;
}

interface StepTwoInput {
    query: string;
    maxResults?: number;
}

// -------------------------------------------------------------------------
// Actor entry
// -------------------------------------------------------------------------

await Actor.init();

const input = await Actor.getInput<OrchestratorInput>();
if (!input) throw new Error('Missing input');

const orchestrator = new Orchestrator({
    enableLogs: true,
    persistenceSupport: 'kvs',
    persistencePrefix: 'ORCH-',
    abortAllRunsOnGracefulAbort: true,
});

const client = await orchestrator.apifyClient({ name: 'MAIN' });

// -------------------------------------------------------------------------
// Cost budget bookkeeping — see references/cost-tracking.md
//   Total cap comes from THIS Run's own maxTotalChargeUsd option (set by
//   the caller via API / Console / SDK, not via input schema). The
//   orchestrator splits it evenly across STEPS at compile time — no
//   stepBudgets input, no per-step config for the caller.
// -------------------------------------------------------------------------

const env = Actor.getEnv();
let totalBudget = Number.POSITIVE_INFINITY;
if (env.actorRunId) {
    try {
        const selfRun = await client.run(env.actorRunId).get();
        const cap = selfRun?.options?.maxTotalChargeUsd;
        if (typeof cap === 'number' && cap > 0) totalBudget = cap;
    } catch (err) {
        // Local `apify run` uses a synthetic Run ID that doesn't exist on
        // the platform. Fall back to uncapped so local runs still work.
        log.debug(`Could not read self-Run options: ${(err as Error).message}`);
    }
}
const perStepCap = totalBudget / STEPS.length;   // Infinity / N = Infinity
let spent = 0;

log.info(
    `Total cost cap: ${Number.isFinite(totalBudget) ? '$' + totalBudget.toFixed(4) : 'unlimited (caller did not set maxTotalChargeUsd)'}. ` +
    `Per-step cap (even split across ${STEPS.length} steps): ${Number.isFinite(perStepCap) ? '$' + perStepCap.toFixed(4) : 'unlimited'}.`,
);

function planStepCap(step: Step): number | undefined {
    const remaining = totalBudget - spent;
    if (remaining <= 0) {
        throw new Error(`Cost cap of $${totalBudget} reached before step "${step}"; refusing to launch`);
    }
    if (!Number.isFinite(perStepCap)) return undefined;   // uncapped → don't pass maxTotalChargeUsd
    // Cap at whichever is smaller so an earlier overshoot can't leak into a later step.
    return Math.min(perStepCap, remaining);
}

function record(stepName: string, run: { usageTotalUsd?: number }) {
    const stepCost = run.usageTotalUsd ?? 0;
    spent += stepCost;
    log.info(`Step "${stepName}" spent $${stepCost.toFixed(4)}; cumulative $${spent.toFixed(4)}`);
}

// -------------------------------------------------------------------------
// Step 1: <sub-actor-1-id>
//   See: https://apify.com/<sub-actor-1-id>
// -------------------------------------------------------------------------

log.info('Step 1: launching <sub-actor-1-id>');
const step1Input: StepOneInput = {
    startUrls: input.startUrls,
    // maxCrawlDepth: 2,  // hardcoded example
};
const step1Cap = planStepCap('step1');
const run1 = await client
    .actor('<sub-actor-1-id>')
    .call('step-1', step1Input, step1Cap != null ? { maxTotalChargeUsd: step1Cap } : undefined);
// For compute-unit sub-Actors, drop maxTotalChargeUsd and pass { memory, timeout } instead.
record('step-1', run1);
const step1Items = await client.dataset(run1.defaultDatasetId).listItems({ skipEmpty: true });
log.info(`Step 1 finished: ${step1Items.items.length} items`);

// -------------------------------------------------------------------------
// (Optional) LLM transformation
//   See references/openrouter.md for the full pattern.
// -------------------------------------------------------------------------
//
// const summary = await callOpenRouter([
//     { role: 'system', content: '...' },
//     { role: 'user', content: JSON.stringify(step1Items.items).slice(0, 12000) },
// ]);

// -------------------------------------------------------------------------
// Step 2: <sub-actor-2-id>
//   Input derived from step-1 output.
//   See: https://apify.com/<sub-actor-2-id>
// -------------------------------------------------------------------------

log.info('Step 2: launching <sub-actor-2-id>');
const step2Input: StepTwoInput = {
    query: step1Items.items.map(i => i.text as string).join('\n').slice(0, 4000),
    maxResults: input.maxItems ?? 20,
};
const step2Cap = planStepCap('step2');
const run2 = await client
    .actor('<sub-actor-2-id>')
    .call('step-2', step2Input, step2Cap != null ? { maxTotalChargeUsd: step2Cap } : undefined);
record('step-2', run2);

// -------------------------------------------------------------------------
// Emit final dataset — iterate (not listItems) to survive large payloads
// -------------------------------------------------------------------------

log.info('Emitting final dataset');
for await (const item of client.dataset(run2.defaultDatasetId).iterate({ pageSize: 100 })) {
    await Actor.pushData(item);
}

// -------------------------------------------------------------------------
// Surface sub-Actor dataset links so users can inspect upstream data.
// Referenced from .actor/output_schema.json — see output-schema.md.
// -------------------------------------------------------------------------

const subDatasets = [
    {
        name: '<sub-actor-1-id>',
        resultUrl: `https://console.apify.com/storage/datasets/${run1.defaultDatasetId}`,
    },
    {
        name: '<sub-actor-2-id>',
        resultUrl: `https://console.apify.com/storage/datasets/${run2.defaultDatasetId}`,
    },
];
await Actor.setValue('SUB_DATASETS', subDatasets);

await Actor.exit();
```

## Companion files

`.actor/actor.json`:

```json
{
    "actorSpecification": 1,
    "defaultMemoryMbytes": 1000,
    "name": "my-orchestrator",
    "title": "My Orchestrator",
    "version": "0.0",
    "meta": {
        "templateId": "ts_empty",
        "generatedBy": "Claude Code with Claude Opus 4.7"
    },
    "input": "./input_schema.json",
    "output": "./output_schema.json",
    "storages": {
        "dataset": "./dataset_schema.json"
    },
    "dockerfile": "../Dockerfile"
}
```

`defaultMemoryMbytes: 1000` is a sane default for orchestrators — the parent Run spends most of its life awaiting child Runs, not doing heavy work. Bump it only if the workflow chains 200+ sub-Actors or streams very large datasets through in-memory transforms. See [actor-json.md](actor-json.md).

`package.json` dependencies section (versions are indicative — check npm for latest):

```json
{
    "dependencies": {
        "apify": "^3.4.0",
        "apify-client": "^2.10.0",
        "apify-orchestrator": "0.x"
    }
}
```

Pin the exact `apify-orchestrator` version (it's alpha, minor bumps break API).

## Surfacing sub-Actor dataset links

Orchestrator users often want to inspect the raw data each sub-Actor produced — for debugging, spot-checking, or downloading the upstream dataset directly. Emit an array of `{ name, resultUrl }` records to a KVS key (canonically `SUB_DATASETS`), then reference that key from `.actor/output_schema.json` so it appears on the Run's Output tab.

Construct URLs from each Run's `defaultDatasetId`:

```typescript
const subDatasets = [
    { name: 'Google Search Scraper', resultUrl: `https://console.apify.com/storage/datasets/${googleRun.defaultDatasetId}` },
    { name: 'Website Content Crawler', resultUrl: `https://console.apify.com/storage/datasets/${wccRun.defaultDatasetId}` },
];
await Actor.setValue('SUB_DATASETS', subDatasets);
```

Then in `.actor/output_schema.json` add a property pointing at the KVS record. See [output-schema.md](output-schema.md) for the exact template syntax.

## Variations

- **Parallel step**: replace `.call(name, input)` with `.callRuns(...requests)` and merge with `orchestrator.mergeDatasets(...)`. See `references/orchestrator-library.md`.
- **Batch step** (very large inputs that would exceed 9 MiB): use `.callBatch(prefix, sources, inputGen, { respectApifyMaxPayloadSize: true })`.
- **Kill-switch propagation**: pass `fixedInput.__watched` to the `Orchestrator` constructor (see `references/orchestrator-library.md`).
- **LLM step**: inline a `callOpenRouter(...)` helper (see `references/openrouter.md`) between steps.

## Testing locally

1. `apify run --purge` — runs the orchestrator with the local `storage/key_value_stores/default/INPUT.json` as input.
2. Local sub-Actor Runs execute **on the Apify platform** (they're real Runs, not simulated) — you need a valid `APIFY_TOKEN` in your environment. Watch the Apify Console → Runs list for the child Runs while the orchestrator runs locally.
3. Local storage under `storage/` receives only the orchestrator's own dataset output, not the child Runs' data.
