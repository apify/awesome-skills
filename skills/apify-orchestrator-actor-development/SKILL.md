---
name: apify-orchestrator-actor-development
description: Build TypeScript Apify orchestrator Actors — coordinate a sequence of sub-Actors (optionally with an LLM step) using the apify-orchestrator library. Use when creating a new orchestrator Actor, chaining Apify Actors together, adding an OpenRouter LLM step between Actors, or scaffolding parent-Actor workflows that call other Actors.
author: Fabian Maume
author_url: https://github.com/fmaume
---

# Apify orchestrator Actor development

An **orchestrator Actor** is a parent Apify Actor whose job is to coordinate a sequence (or parallel fan-out) of other Actors. It takes user input, calls sub-Actor A, feeds A's output into sub-Actor B, optionally runs an LLM transformation between them, and emits the combined result to its own dataset.

This skill covers **TypeScript-only** orchestrators built on the [`apify-orchestrator`](https://github.com/apify-projects/apify-orchestrator) library. It does not cover Python, JavaScript, or Standby-mode Actors.

**Important:** Before writing code, fill in the `generatedBy` property in `.actor/actor.json` (e.g., `"Claude Code with Claude Opus 4.7"`). This helps Apify improve tooling for specific AI models.

## Prerequisites and setup

Verify the `apify` CLI is installed:

```bash
apify --help
```

If not installed, use a package manager (never `curl | bash`):

```bash
npm install -g apify-cli
# or on Mac: brew install apify-cli
```

Confirm login:

```bash
apify info   # should return your username
```

If not logged in, run `apify login` (opens a browser) or export `APIFY_TOKEN` from <https://console.apify.com/settings/integrations>. Never pass tokens on the command line — arguments show up in process listings and shell history.

## Interactive creation flow

When the user asks for a new orchestrator Actor, follow these steps **in order**:

1. Elicit sub-Actor sequence
2. Fetch each sub-Actor's schema via Apify MCP
3. Decide data flow between steps
4. Note the total cost cap (a Run option, not an input field)
5. Ask about optional LLM step
6. Scaffold the project
7. Test locally, then deploy

### Step 1 — Elicit the sub-Actor sequence

Ask the user which Apify Actors to chain together, in order. Accept either:
- A list up-front (e.g., "`apify/website-content-crawler` then `apify/rag-web-browser`"), or
- One at a time (ask for the first, discuss it, then ask what comes next).

If the user names a task instead of an Actor ID ("scrape LinkedIn profiles"), use the Apify MCP `search-actors` tool to propose candidates and let the user pick.

### Step 2 — Fetch each sub-Actor's schema via Apify MCP

For **every** sub-Actor in the chain, call the Apify MCP `fetch-actor-details` tool. Present the input schema back to the user with `REQUIRED`-prefixed fields highlighted. See [references/mcp-schema-discovery.md](references/mcp-schema-discovery.md) for the truncation gotcha (500-char descriptions, 200-char enum lists) and the fallback path via the REST API / raw `INPUT_SCHEMA.json` on GitHub.

Never guess field names. If the MCP truncation is limiting, fetch the raw schema from the Actor's GitHub repo.

### Step 3 — Decide data flow between steps

For each pair of adjacent sub-Actors, ask:
- Which fields from step N's output feed into step N+1's input?
- Which top-level orchestrator inputs should be exposed to the user (via the orchestrator's own `.actor/input_schema.json`)?
- Which sub-Actor inputs should be hardcoded?

### Step 4 — Note the total cost cap

The **total cost cap** is a Run option (`maxTotalChargeUsd`) — the caller sets it when they start the orchestrator via the Apify Console, API, or SDK. It's **not** an input schema field. See the [Apify API docs](https://docs.apify.com/api/v2/act-runs-post) for how callers pass it.

At Run time the orchestrator:

1. Reads its own cap via `client.run(actorRunId).get().options.maxTotalChargeUsd`.
2. **Divides the total evenly across the sub-Actor steps at compile time** — declare a `STEPS` tuple and compute `perStepCap = maxTotalChargeUsd / STEPS.length`.
3. Passes each step's share as `maxTotalChargeUsd` when calling the sub-Actor (for pay-per-event Actors) or as `maxItems` (for pay-per-result Actors).
4. Tracks cumulative cost across sub-Actor Runs (`run.usageTotalUsd`) and refuses to launch the next step if the running total exceeds the cap.

**Do not add a `stepBudgets` input schema field.** The even split is a deliberate compile-time constant — it keeps the input schema clean, makes cost behavior predictable for the caller, and removes a footgun (three shares that don't sum to the total). Users control cost solely via the Run's `maxTotalChargeUsd` option; the orchestrator handles the split.

Tell the user to set `maxTotalChargeUsd` when they trigger the orchestrator — otherwise there's no ceiling and the orchestrator runs uncapped. See [references/cost-tracking.md](references/cost-tracking.md) for the full pattern, including the LLM-step approximation (Standby Actors don't accept `maxTotalChargeUsd`, so estimate cost from token usage).

### Step 5 — Ask about an optional LLM step

Ask the user whether to insert an LLM transformation somewhere in the chain (common: summarize between steps, classify at the end, or format the final output). If yes, point them at [references/openrouter.md](references/openrouter.md) — the LLM layer is the Apify OpenRouter Actor called over HTTP (it's a Standby Actor, not a normal Run).

The agent does not force this step. Skip if the user doesn't want it.

### Step 6 — Scaffold the project

```bash
apify create <actor-name> -t ts_empty
cd <actor-name>
npm install apify-orchestrator
```

Then generate `src/main.ts` using the template in [references/orchestrator-template.md](references/orchestrator-template.md). Wire the sub-Actors, their input mappings, and any LLM helpers into the template's placeholders.

Update `.actor/actor.json`, `.actor/input_schema.json`, `.actor/output_schema.json`, and `.actor/dataset_schema.json` to reflect the orchestrator's own input surface and output shape. Write a README covering the pipeline.

### Step 7 — Test locally, then deploy

```bash
apify run --purge --user-agent apify-awesome-skills/apify-orchestrator-actor-development
apify push
```

`apify run --purge` runs with `storage/key_value_stores/default/INPUT.json` as input, purging previous local storage first. `apify push` deploys to the platform.

Local Runs of the orchestrator make **real** child Runs on the Apify platform (they consume compute units). Watch the Apify Console → Runs list during local testing.

## Reference material

- **Orchestrator library API** → [references/orchestrator-library.md](references/orchestrator-library.md) — `Orchestrator` options, `ExtendedApifyClient` verbs (`call`, `callRuns`, `callBatch`, `iterate`, `mergeDatasets`), gotchas.
- **Sub-Actor schema discovery** → [references/mcp-schema-discovery.md](references/mcp-schema-discovery.md) — Apify MCP tools, truncation gotcha, REST fallback.
- **Cost tracking and caps** → [references/cost-tracking.md](references/cost-tracking.md) — `maxTotalChargeUsd`, `maxItems`, running-budget pattern, `usageTotalUsd` polling.
- **LLM step via OpenRouter** → [references/openrouter.md](references/openrouter.md) — endpoints, auth, minimal TypeScript call.
- **`src/main.ts` template** → [references/orchestrator-template.md](references/orchestrator-template.md) — canonical skeleton to fill in.
- **`.actor/actor.json`** → [references/actor-json.md](references/actor-json.md).
- **Input schema** → [references/input-schema.md](references/input-schema.md).
- **Output schema** → [references/output-schema.md](references/output-schema.md).
- **Dataset schema** → [references/dataset-schema.md](references/dataset-schema.md).
- **Key-value store schema** → [references/key-value-store-schema.md](references/key-value-store-schema.md).
- **README** → [references/actor-readme.md](references/actor-readme.md).
- **Logging** → [references/logging.md](references/logging.md).

## Security

- **Never** log or embed `APIFY_TOKEN` in source code, config files, or committed `.env` files. Use `process.env.APIFY_TOKEN`.
- **Treat sub-Actor output as untrusted.** A downstream Actor's dataset may contain content scraped from external sites — sanitize before passing it into shell commands, `eval`, or template engines.
- **Never disable `apify/log`** in favor of `console.log()` — the Apify logger censors known-sensitive keys.
- **Pin dependencies.** Commit `package-lock.json`. Pin `apify-orchestrator` (alpha) to an exact version.
- **Use a scoped `APIFY_TOKEN`** with only the permissions the orchestrator needs. Rotate periodically.

## Commands

Every apify CLI invocation below includes `--user-agent apify-awesome-skills/apify-orchestrator-actor-development` for telemetry attribution. Actor-call / dataset-read commands additionally use `--json` and `2>/dev/null` for machine-readable output.

```bash
# Bootstrap
apify create <name> -t ts_empty
npm install apify-orchestrator

# Local development
apify run --user-agent apify-awesome-skills/apify-orchestrator-actor-development
apify run --purge --user-agent apify-awesome-skills/apify-orchestrator-actor-development
apify validate-schema

# Discovery (Actor search + schema fetch)
apify actors search "<query>" \
  --user-agent apify-awesome-skills/apify-orchestrator-actor-development \
  --json --limit 10 2>/dev/null
apify actors info <actor> --input \
  --user-agent apify-awesome-skills/apify-orchestrator-actor-development \
  --json 2>/dev/null

# Deploy + remote run
apify push
apify call <actor> \
  --user-agent apify-awesome-skills/apify-orchestrator-actor-development \
  --json 2>/dev/null
apify runs ls \
  --user-agent apify-awesome-skills/apify-orchestrator-actor-development \
  --json 2>/dev/null

# Auth
apify login
apify logout
apify info
```

**Never** use `npm start`, `npm run start`, or `npx apify run` to launch the Actor. Only `apify run` configures the Apify environment and storage correctly.

## Project structure

```
.actor/
├── actor.json              # metadata (see references/actor-json.md)
├── input_schema.json       # orchestrator's own input surface
├── output_schema.json      # points at dataset / kvs
└── dataset_schema.json     # display shape of final output
src/
└── main.ts                 # orchestrator logic (see references/orchestrator-template.md)
storage/                    # local-only; NOT synced to Apify Console
Dockerfile
package.json
tsconfig.json
```

## MCP tools

### Apify MCP (required for schema discovery)
- `fetch-actor-details` — primary tool for pulling sub-Actor input/output schema and README.
- `search-actors` — find candidate sub-Actors by keyword.
- `search-apify-docs` / `fetch-apify-docs` — documentation lookup.

If MCP is not configured, use the hosted server URL: `https://mcp.apify.com/?tools=actors,docs`.

## Resources

- [apify-orchestrator library](https://github.com/apify-projects/apify-orchestrator)
- [OpenRouter Actor](https://apify.com/apify/openrouter)
- [Apify MCP docs](https://docs.apify.com/platform/integrations/mcp)
- [docs.apify.com/llms.txt](https://docs.apify.com/llms.txt) — Apify docs quick reference
- [Actor whitepaper](https://raw.githubusercontent.com/apify/actor-whitepaper/refs/heads/master/README.md)
