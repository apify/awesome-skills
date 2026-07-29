# Cost tracking and per-run cost caps

An orchestrator Actor's total cost is the parent Run's compute cost **plus** the sum of every child Run's cost. Without a cap, one badly-configured sub-Actor can burn through a user's Apify credits. The orchestrator is the right place to enforce a cost ceiling because it's the only actor that has visibility into all the child Runs.

## The two Apify cost-cap primitives

| Sub-Actor pricing model | Option to pass to `.call(name, input, options)` | What it does |
|---|---|---|
| **Pay-per-event** (most Apify Store Actors) | `maxTotalChargeUsd: <number>` | Hard USD cap. Apify aborts the Run when the charge would exceed this. |
| **Pay-per-result** | `maxItems: <integer>` | Cap on the number of dataset items charged. |
| **Rental / compute-unit** | *(neither)* — control cost via `memory` and `timeout` | No dollar cap available; use the Run's own timeout + memory instead. |

Check each sub-Actor's pricing model on its Apify Store page (or via the MCP `fetch-actor-details` output — `pricingInfo` field) before picking which cap to pass.

Type reference (from `apify-client`):

```typescript
interface ActorStartOptions {
    memory?: number;
    timeout?: number;
    build?: string;
    maxItems?: number;            // pay-per-result cap
    maxTotalChargeUsd?: number;   // pay-per-event cap
    // ...
}
```

## Reading the orchestrator's own cap

**`maxTotalChargeUsd` is a Run option, not an input schema field.** The caller sets it when starting the orchestrator — via the `maxTotalChargeUsd` query parameter on [`POST /v2/acts/{actorId}/runs`](https://docs.apify.com/api/v2/act-runs-post) (or the equivalent option in `apify-client`, Apify Console → Advanced → *Max total charge*, or a scheduled task). Do **not** duplicate it as a top-level input schema field.

The orchestrator reads its own cap from its Run's `options`:

```typescript
import { Actor } from 'apify';

const env = Actor.getEnv();
let totalBudget = Number.POSITIVE_INFINITY;
if (env.actorRunId) {
    try {
        const selfRun = await client.run(env.actorRunId).get();
        const cap = selfRun?.options?.maxTotalChargeUsd;
        if (typeof cap === 'number' && cap > 0) totalBudget = cap;
    } catch (err) {
        // Local `apify run` uses a synthetic Run ID that doesn't exist on the
        // platform. Swallow the error and run uncapped.
        log.debug(`Could not read self-Run options: ${(err as Error).message}`);
    }
}
```

`ActorRunOptions.maxTotalChargeUsd?: number` — the cap that was applied to this Run (may be undefined if the caller didn't set one, in which case the orchestrator has no dollar ceiling).

## Splitting the cap: hard-code an even distribution

The orchestrator divides `maxTotalChargeUsd` **evenly** across its sub-Actor steps at compile time. **Do not** expose a per-step budget field (`stepBudgets` or similar) in the input schema. The even split is the recommended default because:

- It keeps the orchestrator input schema focused on the pipeline's real inputs, not on cost knobs the caller can already set via the Run option.
- It removes a common footgun — a `stepBudgets` object whose three shares don't sum to the total, or that exceeds it.
- It makes cost behavior predictable from the caller's perspective: "each step gets `maxTotalChargeUsd / n`," full stop.
- If one step reliably dominates cost for a specific caller, they raise the Run-level cap so its slice is large enough; the surplus on cheaper steps is accepted overhead.

Declare a `STEPS` tuple listing every step that spends money, and derive the share:

```typescript
const STEPS = ['crawl', 'summarize', 'classify'] as const;
type Step = (typeof STEPS)[number];

const perStepCap = totalBudget / STEPS.length;  // Infinity / N = Infinity, fine.
```

## Querying the current cost of any run

Every Run object carries a running total:

```typescript
interface ActorRun {
    id: string;
    // ...
    options: ActorRunOptions;         // includes maxTotalChargeUsd
    usageTotalUsd?: number;           // running total charge in USD
    usageUsd?: ActorRunUsage;         // per-resource breakdown (compute, storage, network)
    chargedEventCounts?: Record<string, number>;  // pay-per-event only
}
```

- After a sub-Actor call finishes, read `run.usageTotalUsd` from the returned object.
- To poll a still-running child Run, use `client.run(runId).get()`.

## The running-budget pattern

Wrap each `client.actor(id).call(...)` with a helper that computes the step cap and updates the cumulative tally afterwards:

```typescript
let spent = 0;
const remaining = (): number => totalBudget - spent;

function planStepCap(step: Step): number | undefined {
    const rem = remaining();
    if (rem <= 0) {
        throw new Error(`Cost cap $${totalBudget} reached before step "${step}"`);
    }
    // Uncapped run: return undefined so the caller doesn't pass maxTotalChargeUsd.
    if (!Number.isFinite(perStepCap)) return undefined;
    // Never ask a sub-Actor to spend more than we have left, even if the even
    // share is larger (e.g. a prior step overshot its share).
    return Math.min(perStepCap, rem);
}

function recordSpend(step: string, cost: number): void {
    spent += cost;
    log.info(`Step "${step}" spent $${cost.toFixed(4)}; cumulative $${spent.toFixed(4)}`);
}

// Usage:
const cap = planStepCap('crawl');
const run = await client
    .actor('apify/website-content-crawler')
    .call('crawl', input, cap != null ? { maxTotalChargeUsd: cap } : undefined);
recordSpend('crawl', run.usageTotalUsd ?? 0);
```

The wrapper hands the sub-Actor a cap that never exceeds the remaining budget and updates the running tally. If cumulative spend ever exceeds `totalBudget`, the next `planStepCap` call throws before making the next Run — preventing runaway spend even if a sub-Actor overshot its individual cap.

## LLM (Standby Actor) steps

The Apify OpenRouter Actor and other Standby-mode Actors are called over HTTP, not via `.call()`, so **you can't hand them a `maxTotalChargeUsd`**. Their cost accrues to the parent Run's `usageTotalUsd` asynchronously and lags by seconds.

Two practical mitigations:

1. **Refuse to start the LLM step if the budget is already exhausted.** Call `planStepCap('llm')` up-front; if it throws, emit each candidate with `score: null` and a reasoning like `"Cost cap exhausted before LLM scoring"` rather than crashing the whole Run.
2. **Estimate LLM cost per call and short-circuit mid-batch.** The OpenRouter response includes `json.usage.total_tokens`. Multiply by a rough per-token rate (e.g. `LLM_USD_PER_1K_TOKENS = 0.001` biased slightly high for `openai/gpt-4o-mini`) and track a running estimated cost. When the estimate crosses the LLM step's share, flip a `llmBudgetExhausted` flag; concurrent workers check it on entry and return null-scored placeholders. Add the final estimate to `spent` at the end of the step so downstream steps see the LLM cost too.

Expect ±20% accuracy on the estimator — good enough for orchestration control flow, not for billing reconciliation.

## Prompt the user for the budget

During the interactive scaffolding flow, **do not ask** for per-step budgets. Instead, tell the user:

- The total cap is `maxTotalChargeUsd`, set at Run start time (Apify Console → Advanced → *Max total charge*, or the API/SDK option).
- The orchestrator splits that total evenly across all pay-spending steps.
- If they want a specific step to have more budget, they should raise the Run cap enough that that step's slice is sufficient.

If the caller expects to run the orchestrator uncapped for exploratory use, that's fine — just tell them scheduled Runs should always have a positive cap set.

## Where to also declare the cap

- **On the orchestrator Run itself** — the caller sets `maxTotalChargeUsd` when triggering the Run. This is the only surface for adjusting cost per Run.
- **Not in the input schema** — do not add `maxCostUsd`, `stepBudgets`, or similar. Duplicating the cap creates two sources of truth that will diverge; the Run option is authoritative.

## Gotchas

1. **`maxTotalChargeUsd` only works on pay-per-event Actors.** Silently ignored on compute-unit Actors. Read the sub-Actor's pricing model before assuming the cap will bind.
2. **`usageTotalUsd` lags slightly.** Apify updates it as the Run charges accumulate — it may be up to a few seconds stale. For orchestration control flow, that's fine; don't build sub-second cost logic on top of it.
3. **Aborted-by-cap Runs still produce partial data.** When a sub-Actor is stopped mid-Run by hitting `maxTotalChargeUsd`, its dataset contains whatever it managed to write. Handle partial results (skip empty, retry, or degrade gracefully).
4. **Compute unit runs need timeout + memory caps instead.** Set `timeout: 3600` (seconds) and `memory: 1024` on the `.call()` options — the product roughly bounds the compute-unit cost.
5. **Don't double-count.** `usageTotalUsd` on the parent already excludes child Runs. Sum child Runs separately; add both totals to compute the true orchestrator cost.
6. **Local `apify run` has no self-Run.** `env.actorRunId` points at a synthetic ID; `client.run(id).get()` returns an error. Catch it and fall back to `Infinity` (uncapped) so local runs still work.
