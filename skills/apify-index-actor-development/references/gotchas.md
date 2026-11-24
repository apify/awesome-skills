# Gotchas - scraper + index pair

Read this when a run, build or request fails, or before estimating cost.

## Common errors

| Symptom | Cause | Fix |
|---|---|---|
| Output tab empty though the named dataset has items | Output tab templates against `links.apiDefaultDatasetUrl`; Actor A only wrote to the named dataset | Dual-write every record with `writeRecord()` (Pattern 1, [scraper-actor.md](scraper-actor.md)) |
| Output tab shows raw JSON or nothing; schema "invalid" | `dataset_schema.json` and `output_schema.json` shapes swapped | `dataset_schema.json` = `actorSpecification` + `fields` + `views`; `output_schema.json` = `actorOutputSchemaVersion` + `properties` with `template` ([schemas.md](schemas.md)) |
| Scheduled run re-scrapes everything | Seen-set never loaded, persisted only at the end and run aborted, or keys unstable (tracking params) | Load at start, filter before enqueue, persist on interval + `aborting` + end; canonicalize keys (Pattern 2) |
| Records vanish when the company website is down | No `failedRequestHandler` for the enrichment label | Write partial records with `enrichmentError` (Pattern 3) |
| Dataset item too large / slow index scans | Unbounded Markdown | Cap with `MARKDOWN_MAX_CHARS`, skip non-HTML responses (Pattern 4) |
| Build fails with `must be string` (or similar) in `openapi.json` | OpenAPI 3.1 syntax `"type": ["string", "null"]` | `"type": "string", "nullable": true`, `"openapi": "3.0.3"` (Pattern 6) |
| `403` on `POST /v2/datasets` in Actor B | `Actor.openDataset(name)` is get-or-create; `LIMITED_PERMISSIONS` denies the POST even for the owner | Pin `SOURCE_DATASET_ID` and read with `client.dataset(id).listItems()` (Pattern 7, [index-actor.md](index-actor.md)) |
| Actor B returns 0 results on the platform but works locally | Env var not set or set on another build; wrong dataset ID | Check the startup log line naming the reader branch; set the variable, **rebuild**, rerun |
| Actor B returns duplicates | Append-only named dataset after a backfill | Dedupe by `id`, newest first (`desc: true`) |
| Actor B request or run hangs when fewer records match than `limit` | Scan paged with `desc: true` + `offset`; local storage ignores `offset` with `desc`, so pages never run out | Page ascending from `total` backwards ([index-actor.md](index-actor.md), shared search logic) |
| A dead enrichment host is retried ~10 times despite `maxRequestRetries: 1` | Connection errors (e.g. `ECONNREFUSED`) count as session errors, governed by `maxSessionRotations` (default 10) | Expected; lower `maxSessionRotations` if dead hosts slow runs. The record still lands via `failedRequestHandler` |
| `Ignored attempt to charge for an event` or `Actor.charge failed` warning | Running locally, or PPE event not configured in Console | Safe locally; on the platform add the `result` event in Monetization (Pattern 8) |
| Results cut short with "charge limit reached" | User's max-charge limit hit | Expected - return only `chargedCount` records |
| Standby container restarts / never becomes ready | No 200 on `GET /` readiness probe, listening on wrong port, or `Actor.exit()` called after a request | Answer the probe, use `Actor.config.get('containerPort')`, never exit in Standby (Pattern 5) |
| Local `apify run` ignores Standby branch | `apify run` does not set `APIFY_META_ORIGIN` | Start with `APIFY_META_ORIGIN=STANDBY npx tsx src/main.ts` (Pattern 10) |
| `ERR_MODULE_NOT_FOUND` for `./search` | ESM needs explicit extensions | Import `./search.js` even from `.ts` files |
| Users can change the source dataset via API | Source name exposed as a hidden input | Make it a `const` in code (Pattern 9) |

## Cost guardrails

Check the pricing of any Store Actor before running it: `apify actors info "<actor-id>" --json --user-agent apify-awesome-skills/apify-index-actor-development 2>/dev/null` and read `pricingInfo`.

| Model | What to watch |
|---|---|
| `FREE` | No Actor fee; platform usage (compute, proxy) still applies |
| `PAY_PER_EVENT` | Cost scales with events - estimate count x price first |
| `FLAT_PRICE_PER_MONTH` | Subscription |

Own Actors cost compute units and proxy traffic while you test:

- Keep `maxItems` small (10-20) on the first platform runs of Actor A.
- Residential proxy is billed per GB - confirm with the user before enabling it or switching proxy groups.
- A Standby Actor bills compute while containers are alive; leave the default idle timeout unless the user asks otherwise.

Suggested confirmation thresholds: warn above about **$5** estimated, require explicit confirmation above about **$20**. Present costs as rough estimates.

## Before you push

- [ ] `npx tsc --noEmit` clean in both projects.
- [ ] `apify validate-schema` passes in both; `output_schema.json` and `openapi.json` checked by hand.
- [ ] Local seen-set, partial-record, batch and Standby tests from [testing-and-deploy.md](testing-and-deploy.md) all pass.
- [ ] No tokens, `.env` or `storage/` in the commit.
- [ ] The user confirmed the deploy.
