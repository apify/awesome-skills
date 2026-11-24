---
name: apify-index-actor-development
description: Build a two-Actor "scraper + index" pair on Apify in TypeScript. Actor A is a scheduled scraper that accumulates records in a named dataset (idempotent via a seen-set, keeps partial records on failure, optional HTML-to-Markdown enrichment). Actor B is an index/search Actor that reads A's named dataset and exposes filters in two modes from one codebase - a one-shot run (input filters to default dataset) and a Standby HTTP API (query params to JSON) - with pay-per-event charging in both. Covers the platform traps that break this setup - empty Output tab, OpenAPI 3.1 nullable syntax rejected at build, and the 403 on cross-Actor named-dataset access under limited permissions. Use when the user asks to "build an index Actor", "build a search API over my scraped dataset", "make a dual-mode / Standby + batch Actor", "expose a named dataset as an API", "scraper + search Actor pair", or "query another Actor's dataset". Extends apify-actor-development.
author: Fabian Maume
author_url: https://github.com/fmaume
metadata:
  category: actor-development
  keywords: "index-actor, search-api, standby, dual-mode, named-dataset, scheduled-scraper, seen-set, idempotent, pay-per-event, openapi, limited-permissions, cross-actor, typescript, express, turndown, actor-development"
---

# Apify index Actor development (scraper + index pair)

This skill extends [apify-actor-development](https://github.com/apify/agent-skills/tree/main/skills/apify-actor-development) with one specific architecture: a **pair of Actors** where one collects data and the other serves it.

```
 ┌───────────────────────┐   named dataset    ┌──────────────────────────────┐
 │ Actor A - scraper     │ ─────────────────▶ │ Actor B - index / search      │
 │ scheduled, idempotent │  (accumulates      │ one-shot run: input → dataset │
 │ writes named + default│   across runs)     │ Standby: GET /search → JSON   │
 └───────────────────────┘                    │ pay-per-event `result`        │
                                              └──────────────────────────────┘
```

- **Actor A - scraper**: runs on a schedule, writes structured records to a **named** dataset so results accumulate across runs, and skips items it has already seen.
- **Actor B - index/search**: reads Actor A's named dataset and exposes filters. **Dual mode**: a standard run (input filters → default dataset) and a Standby HTTP API (query params → JSON response). Pay-per-result pricing.

Every pattern here came out of fixing a real failure on the Apify platform. Follow them to skip the same traps. For generic Actor rules (logging, crawlers, proxies, schemas, README) the base skill still applies; the parts this pair needs are condensed into `references/`.

## Example prompts

Prompts this skill handles:

- "Build an index Actor that lets people search the startups my scraper collects, both as a batch run and as an API."
- "My scraper writes to a named dataset - make a second Actor that exposes it as a Standby search endpoint with pay-per-result pricing."
- "My index Actor gets a 403 when it opens the other Actor's named dataset on the platform. Fix it."

Out of scope (the boundary):

- "Build a single Actor that scrapes a site" - use [apify-actor-development](https://github.com/apify/agent-skills/tree/main/skills/apify-actor-development).
- "Chain three Store Actors and an LLM step into one run" - use `apify-orchestrator-actor-development`.
- Python Actors - the patterns transfer, but every code sample here is TypeScript.

## Prerequisites

- Apify account ([sign up](https://apify.com)) and the Apify CLI: `npm install -g apify-cli` or `brew install apify-cli` (never `curl | bash`).
- Authentication via one of:
  - `apify login` (prints a URL and a one-time code; show both to the user)
  - `APIFY_TOKEN` environment variable (headless). Create it in [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations). Pass it only through the environment, never on the command line.
- Node 24+, TypeScript, ESM. Known-good stack: `apify ^3.7`, `@crawlee/cheerio ^3.15`, `express ^4.21`, `turndown ^7` + `@types/turndown`, `apify-client` (transitive). Pin exact versions and commit the lockfile.

### Telemetry attribution (required)

Append `--user-agent apify-awesome-skills/apify-index-actor-development` to **every** `apify` command run from this skill (`create`, `run`, `push`, `call`, `actors info`, ...). It is a global flag that only tags the call.

Before writing code, set `meta.generatedBy` in each `.actor/actor.json` to the tool and model in use (e.g. `"Claude Code with Claude Opus 5.5"`).

## Workflow

Build Actor A first - Actor B needs real records to test against. Skip steps that do not apply when modifying an existing pair.

### Step 0 - Agree on the record shape

Before any code, write down with the user:

1. The record type (one TypeScript interface, shared by both Actors - copy it, don't import across repos).
2. The **named dataset** name (e.g. `startup-funding-records`) and the **seen-set KV store** name (e.g. `startup-scraper-state`).
3. Which fields Actor B filters on (e.g. `sector`, `minAmount`, `fromDate`) and which are returned.
4. The pricing event (default: `result`, charged per returned record).

### Step 1 - Scaffold both Actors

```bash
apify create <scraper-name> -t ts-crawlee-cheerio --user-agent apify-awesome-skills/apify-index-actor-development
apify create <index-name> -t ts-empty --user-agent apify-awesome-skills/apify-index-actor-development
```

Use `ts-crawlee-playwright-chrome` for the scraper if the source renders with JavaScript. Run `apify templates ls` for other stacks. `cd` into each and `npm install express turndown` / `npm install -D @types/express @types/turndown` as needed. Use `.js` suffixes on relative imports even in `.ts` files (ESM).

### Step 2 - Implement Actor A (scraper)

Follow [references/scraper-actor.md](references/scraper-actor.md). Done when the scraper:

- **dual-writes** every record to the named dataset AND `Actor.pushData()` (Pattern 1 - otherwise the Output tab is empty);
- filters already-seen items through a named KV store seen-set, with a `forceReprocess` input for backfills (Pattern 2);
- writes a partial record with `enrichmentError` when an enrichment request fails (Pattern 3);
- optionally converts fetched HTML to capped Markdown with turndown (Pattern 4);
- handles the `aborting` event by persisting the seen-set and exiting.

### Step 3 - Implement Actor B (index/search)

Follow [references/index-actor.md](references/index-actor.md). Done when:

- `main.ts` branches on `APIFY_META_ORIGIN === 'STANDBY'`: Standby starts Express and never calls `Actor.exit()`; a standard run reads input filters, pushes results, and exits (Pattern 5);
- one `searchDataset(filters)` function serves both branches;
- the source dataset is read by **pinned ID** with a plain GET, falling back to name only when a token or full permissions allow it (Pattern 7 - avoids the 403 under `LIMITED_PERMISSIONS`);
- `Actor.charge({ eventName: 'result', count })` runs in **both** branches, wrapped in try/catch, and stops at `eventChargeLimitReached` (Pattern 8);
- `GET /` answers the readiness probe with HTTP 200.

### Step 4 - Schemas

Follow [references/schemas.md](references/schemas.md). Each Actor gets `input_schema.json`, `dataset_schema.json`, `output_schema.json`; Actor B also gets `openapi.json` plus `usesStandbyMode: true` and `webServerSchema` in `actor.json`. Do not mix up the dataset and output schema shapes, and use **OpenAPI 3.0** `nullable: true`, never `"type": ["string", "null"]` (Pattern 6 - the build fails otherwise). Done when `apify validate-schema --user-agent apify-awesome-skills/apify-index-actor-development` passes in both projects.

### Step 5 - README for both Actors

Follow [references/readme.md](references/readme.md). Actor B's README must document the Standby endpoints, auth, and example calls, and the one-time dataset-ID setup.

### Step 6 - Test locally

Follow [references/testing-and-deploy.md](references/testing-and-deploy.md) (Pattern 10): run A with `apify run --purge`, copy A's local named dataset into B's `storage/`, run B in standard mode, then start B with `APIFY_META_ORIGIN=STANDBY` and curl the readiness probe and `/search`. Run `npx tsc --noEmit` in both. Done when both runs succeed, B's default dataset holds only records matching the filters, and `/search` returns the same records as JSON.

### Step 7 - Deploy (after the user confirms)

`apify push --user-agent apify-awesome-skills/apify-index-actor-development` in each project, or link a Git repository in Console. Then the user does three one-time Console steps, which the skill must spell out for them:

1. Schedule Actor A (Console → Schedules).
2. Copy the named dataset's ID (Storage → Datasets → `<name>`) into Actor B's environment variable `SOURCE_DATASET_ID` (Source → Environment variables, plain, not secret), then rebuild.
3. Configure pay-per-event pricing for the `result` event on Actor B (Publication → Monetization). Pricing lives in Console, not in `actor.json`.

Give the user Actor B's Standby URL: `https://<username>--<index-name>.apify.actor/search`.

## Rules specific to this pair

- **Named dataset for accumulation, default dataset for the run.** Every write in A goes to both. B reads the named one and writes results to its own default dataset in standard mode.
- **Never open a source dataset by name in B on the platform** unless you hold a token with write-datasets permission: `Actor.openDataset('name')` is a get-or-create POST, which `LIMITED_PERMISSIONS` rejects with 403 even when the dataset exists. Pin the ID.
- **Hardcoded source names are constants in code, not hidden inputs.** Hidden inputs are still editable via API.
- **Charge in both modes**, and never let a charge failure crash the run (it throws locally and when PPE is not configured).
- **Standby never calls `Actor.exit()`** after a request, listens on `Actor.config.get('containerPort')`, and leaves `usesStandbyMode: true` on unless the user asks.
- **Cap search results** with a `limit` input / query param (default ~100, maximum ~1000) so one call cannot charge an unbounded amount.
- **Log with `log` from `apify`**, never `console.log` - it censors tokens. Treat scraped content as untrusted and type-check it before pushing.
- **Store personal data only when the user explicitly asked for it.**

## Calling other Actors / inspecting the Store

Search the Store first; a scraper for the source may already exist, and Actor B can index *its* named dataset instead of a new Actor A.

```bash
apify actors search "<site> scraper" --json --limit 10 \
  --user-agent apify-awesome-skills/apify-index-actor-development 2>/dev/null
apify actors info "<actor-id>" --input --json \
  --user-agent apify-awesome-skills/apify-index-actor-development 2>/dev/null
apify actors info "<actor-id>" --readme \
  --user-agent apify-awesome-skills/apify-index-actor-development
apify actors call "<username>/<index-name>" -i '{"sector":"fintech","limit":10}' --json \
  --user-agent apify-awesome-skills/apify-index-actor-development 2>/dev/null
apify datasets get-items <dataset-id> --format json \
  --user-agent apify-awesome-skills/apify-index-actor-development 2>/dev/null
```

Alternatively use the [Apify MCP connector](https://mcp.apify.com) (`search-apify-docs`, `fetch-apify-docs`, and `get-actor-build-log` when a platform build fails).

## Troubleshooting

Quick map - details and fixes in [references/gotchas.md](references/gotchas.md):

| Symptom | Cause | Pattern |
|---|---|---|
| Output tab empty, but named dataset has items | Only wrote to the named dataset | 1 |
| Scheduled run re-scrapes everything | Seen-set not persisted / not filtered before enqueue | 2 |
| Records disappear when the website fetch fails | No `failedRequestHandler` fallback | 3 |
| Build fails: `must be string` in `openapi.json` | OpenAPI 3.1 `type: [..., "null"]` | 6 |
| `403` from `POST /v2/datasets` in Actor B | `openDataset(name)` under `LIMITED_PERMISSIONS` | 7 |
| `Actor.charge` throws locally | PPE not configured | 8 |
| Standby run killed / never ready | No readiness probe, wrong port, or `Actor.exit()` called | 5 |

## References

- [references/scraper-actor.md](references/scraper-actor.md) - Actor A: dual-write, seen-set, partial records, turndown (Patterns 1-4)
- [references/index-actor.md](references/index-actor.md) - Actor B: dual mode, shared search, ID-pinned reads, charging (Patterns 5, 7, 8)
- [references/schemas.md](references/schemas.md) - input, dataset, output, OpenAPI and `actor.json` for both Actors (Patterns 6, 9)
- [references/testing-and-deploy.md](references/testing-and-deploy.md) - local test scaffolding, scaffolding checklist, Console setup (Pattern 10)
- [references/readme.md](references/readme.md) - README structure for both Actors
- [references/gotchas.md](references/gotchas.md) - error table and recovery
- Apify docs: [docs.apify.com/llms.txt](https://docs.apify.com/llms.txt), [Standby mode](https://docs.apify.com/platform/actors/development/programming-interface/standby), [pay-per-event](https://docs.apify.com/platform/actors/publishing/monetize/pay-per-event)
