# Testing and deploying the pair

## Pattern 10 - Local test scaffolding

Always run Actors locally with `apify run` (it sets up the Apify environment and `storage/`), never `npm start` or `node`. The one exception is Standby mode detection, below.

### Actor A

```bash
# Input for the local run
mkdir -p storage/key_value_stores/default
echo '{"maxItems": 20, "forceReprocess": true}' > storage/key_value_stores/default/INPUT.json

apify run --purge --user-agent apify-awesome-skills/apify-index-actor-development
```

`--purge` clears the **default** storages only; named storages (`storage/datasets/<name>/`, `storage/key_value_stores/<name>/`) persist between local runs, which is how you test the seen-set:

1. Run once with `forceReprocess: true` → items appear in `storage/datasets/default/` **and** `storage/datasets/<name>/`.
2. Run again with `forceReprocess: false` → no new items; `storage/key_value_stores/<state-store>/seen-items.json` unchanged.
3. Point one enrichment URL at a dead host → a record with `enrichmentError` set still lands in both datasets.

### Actor B

Copy Actor A's named dataset into B's project so B reads it like on the platform:

```bash
mkdir -p storage/datasets/my-named-dataset
cp ../scraper-actor/storage/datasets/my-named-dataset/*.json storage/datasets/my-named-dataset/
```

Locally `SOURCE_DATASET_ID` is unset, so `openSourceDatasetReader()` falls through to `Actor.openDataset(name)`, which reads that folder.

Standard mode:

```bash
echo '{"sector": "fintech", "limit": 5}' > storage/key_value_stores/default/INPUT.json
apify run --purge --user-agent apify-awesome-skills/apify-index-actor-development
# check storage/datasets/default/ holds only matching records, at most 5
```

Standby mode - `apify run` does not set `APIFY_META_ORIGIN`, so the Actor would take the one-shot branch. Start it directly with the env vars set:

```bash
APIFY_META_ORIGIN=STANDBY ACTOR_WEB_SERVER_PORT=4321 APIFY_CONTAINER_PORT=4321 npx tsx src/main.ts
```

(`ACTOR_WEB_SERVER_PORT` is the current name, `APIFY_CONTAINER_PORT` the legacy one; setting both is harmless.) In another shell:

```bash
curl -i -H "x-apify-container-server-readiness-probe: true" http://localhost:4321/   # 200 OK
curl "http://localhost:4321/search?sector=fintech&limit=5"                            # JSON, same records as the batch run
curl -i "http://localhost:4321/search?minAmount=abc"                                  # 400
```

On Windows PowerShell set the variables with `$env:APIFY_META_ORIGIN='STANDBY'` etc. before `npx tsx src/main.ts`.

Expect `Actor.charge failed (safe to ignore locally)` warnings - PPE is not configured locally (Pattern 8).

### Type check

```bash
npx tsc --noEmit
```

in both projects before every push.

## Scaffolding checklist (both Actors)

```bash
apify create <name> -t ts-empty --user-agent apify-awesome-skills/apify-index-actor-development
cd <name>
npm install
# Fill in .actor/actor.json meta.generatedBy
# Write .actor/input_schema.json, .actor/dataset_schema.json, .actor/output_schema.json
# Index Actor only: write .actor/openapi.json, set usesStandbyMode + webServerSchema in actor.json
# Write src/main.ts (+ src/routes.ts for the crawler Actor)
# Write README.md (see readme.md)
apify validate-schema --user-agent apify-awesome-skills/apify-index-actor-development
npx tsc --noEmit
apify run --purge --user-agent apify-awesome-skills/apify-index-actor-development
# Verify storage/datasets/* and storage/key_value_stores/*
```

Use `ts-crawlee-cheerio` (or `ts-crawlee-playwright-chrome`) for Actor A, `ts-empty` or `ts-standby` for Actor B.

## Deploy (only after the user confirms)

Two options per Actor:

- **CLI**: `apify push --user-agent apify-awesome-skills/apify-index-actor-development`
- **Git**: `git init -b main && git add -A && git commit -m "..."`, create a **private** repo (`gh repo create <name> --private --source . --push`), then Apify Console → Actor → **Source → Link Git Repository**. Later deploys go through `git push`. Never commit `storage/`, `.env` or tokens - check `.gitignore` first.

If a platform build fails, read its build log (Console → Builds, or the MCP `get-actor-build-log` tool). The usual suspect for Actor B is Pattern 6 (OpenAPI 3.1 syntax).

## One-time Console setup

Walk the user through these; the skill cannot do them from code:

1. **Actor A → Schedules** - create a schedule (e.g. daily) with the production input.
2. Run Actor A once on the platform so the named dataset exists.
3. **Storage → Datasets → `<name>`** - copy the 17-character dataset ID.
4. **Actor B → Source → Environment variables** - add `SOURCE_DATASET_ID = <id>` (plain, not secret). Rebuild.
5. **Actor B → Publication → Monetization → Pay-per-event** - add the `result` event (name must match the code) and its price.
6. Call Actor B once in each mode:
   - batch: `apify actors call "<username>/<index-name>" -i '{"limit":3}' --json --user-agent apify-awesome-skills/apify-index-actor-development 2>/dev/null`
   - Standby: `curl -H "Authorization: Bearer $APIFY_TOKEN" "https://<username>--<index-name>.apify.actor/search?limit=3"`
7. Hand the user the Standby URL and the Console link of each Actor.
