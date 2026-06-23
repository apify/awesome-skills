---
name: apify-actor-devkit
description: Validate, test, compare, and monitor your own Apify Actors across the full build-to-production lifecycle. Covers preflight input validation, multi-Actor pipeline validation, A/B comparison of two Actors for a production switch, post-run output validation (silent data failures), deploy-gate regression detection, fleet-wide quality scoring, PII/GDPR/ToS pre-publish risk triage, and fleet profit and next-action analytics. Most of these Actors return a stable decision enum (act_now / monitor / ignore, or switch_now / canary / no_call) that CI gates and AI agents can branch on without parsing prose; the fleet-wide Actors return a scorecard or prioritized action queue. Use when the user wants to test an Actor before publishing, validate an input or pipeline, decide between two Actors, catch broken output, gate a deploy, audit Actor quality, check compliance risk, or analyse fleet revenue.
author: apifyforge
author_url: https://github.com/apifyforge
license: MIT
metadata:
  version: "1.0"
---

# Actor DevKit — validate, test and monitor your own Apify Actors

A toolkit for Apify Actor developers. Each Actor maps to one stage of the build-to-production lifecycle. Most are designed to expose a stable, routable decision enum so CI pipelines, webhooks, and AI agents can branch on a single field instead of parsing prose; the fleet-wide Actors (Quality Monitor, Fleet Health Report) return a scorecard or prioritized action queue instead.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)
- These Actors orchestrate or inspect other Actors on your account. Sub-Actor runs (for example in A/B Tester) bill against your own credits.

## Workflow

1. Identify which lifecycle stage the user is at (validate input, validate a pipeline, choose between two Actors, check output, gate a deploy, audit quality, check compliance, analyse the fleet) and pick the Actor from the routing table.
2. Fetch the Actor's input schema so you build a valid input:
   `apify actors info "ACTOR_ID" --input --json --user-agent apify-awesome-skills/apify-actor-devkit 2>/dev/null`
3. Run the Actor.
4. Read the **decision field**, not the prose. Branch on `decision` / `decisionPosture` (stable enums). Never branch on `verdictHuman`, `summary`, or `explanation` — those are for display and their wording is not stable.

## Actor routing

| User need | Actor ID | Tier | Decision field | Best for |
|-----------|----------|------|----------------|----------|
| Validate Actor input before running | `ryanclinton/actor-input-tester` | community | `decision` | Preflight an input against a schema before you spend a run on it |
| Validate a multi-Actor pipeline at design time | `ryanclinton/actor-pipeline-builder` | community | `decision` | Catch input/dataset-schema and field-mapping breaks before runtime |
| Decide between two Actors for production | `ryanclinton/actor-ab-tester` | community | `decisionPosture` | Run both on identical input N times, get a fairness-checked production verdict |
| Detect silent data failures after a run | `ryanclinton/actor-schema-validator` | community | `decision` | Catch SUCCEEDED runs that produced broken or incomplete output |
| Gate a deploy / detect regressions across builds | `ryanclinton/actor-test-runner` | community | `decision` | Run a test suite against a candidate build, get a release verdict for a CI gate |
| Score and diagnose every Actor in your account | `ryanclinton/actor-quality-monitor` | community | scorecard | Fleet metadata audit: score, diagnose, sequence fixes by expected impact |
| Pre-publish PII / GDPR / ToS risk triage | `ryanclinton/actor-compliance-scanner` | community | `decision` | Surface common PII/GDPR/ToS risks before publishing — risk verdict with reason codes and fixes (not legal advice) |
| Fleet profit and next-action analytics | `ryanclinton/actor-fleet-analytics` | community | action queue | Per-run profit, revenue-cliff and quality-bleed detection, a recommended next action |

`Tier` = `apify` (Apify-maintained) or `community` (third-party developer). Every Actor in this table is a `community` Actor published by the skill author.

## Lifecycle order

The Actors compose into one build-to-production loop:

1. **Input Guard** (`actor-input-tester`) — is this input valid before I spend a run?
2. **Pipeline Preflight** (`actor-pipeline-builder`) — does my multi-Actor chain compose?
3. **A/B Tester** (`actor-ab-tester`) — which of two candidate Actors should ship?
4. **Output Guard** (`actor-schema-validator`) — did the run that SUCCEEDED actually produce good data?
5. **Deploy Guard** (`actor-test-runner`) — does this new build pass its tests, or did it regress?
6. **Quality Monitor** (`actor-quality-monitor`) — across my whole account, what should I fix next?
7. **Compliance Scanner** (`actor-compliance-scanner`) — is anything I am about to publish a PII/ToS risk?
8. **Fleet Health Report** (`actor-fleet-analytics`) — where is the revenue and what is the recommended next action?

## Calling Actors — choose your interface

### Option A: Apify CLI (recommended for portability)

Three flags on every call: `--json` (stable output), `--user-agent apify-awesome-skills/apify-actor-devkit` (attribution), `2>/dev/null` (suppress progress noise that breaks JSON).

The example input below is illustrative. Field names vary by Actor and can change between versions, so always inspect the Actor's input schema (workflow step 2) before building input rather than copying it verbatim.

Worked example — compare two Actors and get a production switch decision (A/B Tester):

```
apify actors call "ryanclinton/actor-ab-tester" \
  -i '{"actorA":"apify/web-scraper","actorB":"apify/cheerio-scraper","testInput":{"startUrls":[{"url":"https://example.com"}]},"mode":"decision"}' \
  --json \
  --user-agent apify-awesome-skills/apify-actor-devkit \
  2>/dev/null
```

Then branch on the decision field, never the prose:

```
# decisionPosture is the canonical control signal
# switch_now        → commit to the winner
# canary_recommended → partial rollout, then monitor
# monitor_only      → directional only, do not auto-switch
# no_call           → insufficient evidence, keep current
```

For every other Actor in the table, fetch its schema first (step 2 of the workflow) — input fields differ per Actor — then build the input and branch on its documented `decision` enum.

Other useful commands:

```
# Fetch an Actor's input schema before building input
apify actors info "ACTOR_ID" --input --json --user-agent apify-awesome-skills/apify-actor-devkit 2>/dev/null

# Fetch results
apify datasets get-items DATASET_ID --format json --user-agent apify-awesome-skills/apify-actor-devkit 2>/dev/null
```

### Option B: Apify MCP connector

Hosted MCP server at <https://mcp.apify.com>. Documented at <https://docs.apify.com/platform/integrations/mcp>.

### Option C: MCP client of your choice

Standalone CLI client. See <https://github.com/apify/mcpc>.

## Do not use this skill when

- The user wants to extract data from a website — this skill tests and monitors Actors, it does not scrape. Use a data-extraction skill.
- The user is not an Apify Actor developer or operator — these Actors inspect, compare, and monitor Actors on an account.
- The task is a one-off "does this run" check with no production decision attached — a manual run is enough.

## Troubleshooting

- Auth failure → run `apify login` or set `APIFY_TOKEN`.
- A/B Tester returns `no_call` → the test was inconclusive or unfair (incompatible input shapes, too few runs). Raise `mode` to `decision`/`high_stakes` or check both Actors accept the same `testInput`.
- A decision looks wrong → confirm you are reading the documented `decision`/`decisionPosture` enum and not the human-readable sentence. Read `warnings[]` before acting; any `blocking` warning forbids an actionable verdict.
- A/B Tester cost → `runs: N` means 2N sub-Actor runs, each billed at that Actor's own rate on your account, on top of the orchestration fee.
