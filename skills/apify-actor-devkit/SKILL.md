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
4. Read the **decision field**, not the prose. Each Actor exposes one stable routable field — `decision`, `decisionPosture`, or `releaseAction` (the field name is in the routing table and the Actor's own docs). Branch on that. Never branch on `verdictHuman`, `summary`, `oneLine`, or `explanation` — those are for display and their wording is not stable.

## Actor routing

| User need | Actor ID | Tier | Decision field | Best for |
|-----------|----------|------|----------------|----------|
| Validate Actor input before running | `ryanclinton/actor-input-tester` | community | `decision` | **Input Guard** — preflight an input against the target's schema before you spend a run; catches unknown/silently-dropped fields and schema drift |
| Validate a multi-Actor pipeline at design time | `ryanclinton/actor-pipeline-builder` | community | `decisionPosture` | **Pipeline Preflight** — catch broken field mappings, schema drift and cost blow-ups before runtime; returns a `reliabilityScore` (0-100) + ship/canary/monitor/block |
| Decide between two Actors for production | `ryanclinton/actor-ab-tester` | community | `decisionPosture` | **A/B Tester** — run both on identical input N times, get a fairness-checked switch verdict + a `safeToSwitch` boolean |
| Detect silent data failures after a run | `ryanclinton/actor-schema-validator` | community | `decision` | **Output Guard** — catch SUCCEEDED runs that produced broken or incomplete output before it reaches downstream systems |
| Gate a deploy / detect regressions across builds | `ryanclinton/actor-test-runner` | community | `releaseAction` | **Deploy Guard** — run a test suite against a candidate build vs a trusted baseline; deploy/halt/review/misconfigured verdict for a CI gate |
| Score and diagnose every Actor in your account | `ryanclinton/actor-quality-monitor` | community | `qualityGates` | **Quality Monitor** — fleet metadata audit: score across 8 dimensions, diagnose, sequence fixes (`fixSequence[]`) by expected impact |
| Pre-publish PII / GDPR / ToS risk triage | `ryanclinton/actor-compliance-scanner` | community | `decision` | **Compliance Scanner** — surface PII/GDPR/ToS risks before publishing; risk verdict + `gateResult.publish` (pass/warn/block) with reason codes and fixes (not legal advice) |
| Fleet profit and next-action analytics | `ryanclinton/actor-fleet-analytics` | community | `nextBestAction` | **Fleet Health Report** — per-run profit, revenue-cliff and quality-bleed detection, one prioritized next best action |

`Tier` = `apify` (Apify-maintained) or `community` (third-party developer). Every Actor in this table is a `community` Actor.

Each Actor also ships one-click example tasks at its `…/examples` page — preset, runnable configurations you can point a user to or fork. Fetch the Actor's live schema (workflow step 2) before adapting one, since fields can change between versions.

### Picking between siblings

Route on what the Actor inspects, not on a keyword in the request — these are the pairs most often confused:

- **Input Guard vs Output Guard** — Input Guard checks a payload *before* a run; Output Guard checks a dataset *after* one. "Will this input even run" → Input Guard. "Bad data came out of a successful run" → Output Guard.
- **Output Guard vs Deploy Guard** — Output Guard validates one completed run's dataset; Deploy Guard gates a whole *build* against a trusted baseline across many runs. A single dataset → Output Guard. "Is this build safe to release" → Deploy Guard.
- **Pipeline Preflight vs Deploy Guard** — Preflight validates a *multi-Actor chain* at design time; Deploy Guard validates a *single build* at release time.
- **Quality Monitor vs Fleet Health Report** — Quality Monitor scores and diagnoses each Actor's metadata (*fix this Actor*); Fleet Health Report ranks the whole portfolio by profit into one next best action (*fix the business first*). Per-Actor diagnosis → Quality Monitor; "what do I touch first across everything" → Fleet Health Report.

## Lifecycle order

The Actors compose into one build-to-production loop:

1. **Input Guard** (`actor-input-tester`) — *invocation*: is this input valid before I spend a run?
2. **Pipeline Preflight** (`actor-pipeline-builder`) — *composition*: does my multi-Actor chain compose before I deploy it?
3. **A/B Tester** (`actor-ab-tester`) — *migration*: which of two candidate Actors should ship?
4. **Deploy Guard** (`actor-test-runner`) — *release*: does this new build pass its tests against the trusted baseline, or did it regress? (pre-deploy)
5. **Output Guard** (`actor-schema-validator`) — *runtime*: did the run that SUCCEEDED actually produce good data? (post-deploy)
6. **Quality Monitor** (`actor-quality-monitor`) — *readiness*: across my whole account, what should I fix next?
7. **Compliance Scanner** (`actor-compliance-scanner`) — *publish / govern*: is anything I am about to publish a PII/ToS risk?
8. **Fleet Health Report** (`actor-fleet-analytics`) — *operations*: where is the revenue and what is the recommended next action?

The stage tag above is the routable ontology — a developer at the *release* stage wants Deploy Guard, one at *runtime* wants Output Guard. Match the user's stage to the tag, not a keyword in their wording.

## After a decision — route to the next stage

Don't stop at one verdict. A decision tells you which stage comes next. After reading the decision field, move the developer forward:

| You just ran | …and got | Run next | Why |
|--------------|----------|----------|-----|
| Input Guard | `act_now` | (fix the payload, re-run Input Guard) | the input is invalid — correct it before spending a run |
| Pipeline Preflight | `block` / `monitor` | (fix mappings, re-preflight) | the chain won't compose yet; fix the named breaking actor first |
| Output Guard | `act_now` | Deploy Guard | a SUCCEEDED run regressed — find which build or change broke it against the trusted baseline |
| Deploy Guard | `halt` | A/B Tester, or roll back | confirm a known-good build still wins, or revert the candidate |
| A/B Tester | `no_call` | (add runs, re-compare) | the evidence is insufficient or unfair — don't force a switch |
| Same actor flags `act_now` / `monitor` repeatedly | (recurring) | Quality Monitor → Fleet Health Report | stop firefighting single runs; score the fleet and pick the highest-ROI fix |

Opinionated defaults worth holding (state them when the developer skips a stage):

- Never spend a production run on an unvalidated payload — Input Guard first.
- A `SUCCEEDED` status is not a data guarantee. Never ship to production output without Output Guard on a real run.
- Gate every deploy on Deploy Guard against a trusted baseline, not on "the run passed".

## Composite requests — audit the whole Actor

When the developer asks a broad question ("audit my actor", "is this ready to ship", "what's wrong with it") instead of naming one stage, orchestrate the lifecycle and return one synthesized answer rather than a single Actor's output:

1. Inspect the Actor's metadata and input schema (workflow step 2).
2. Run **Quality Monitor** (score, `fixSequence[]`, `qualityGates.storeReady`/`schemaReady`, Store-SEO and missing-example checks) and **Compliance Scanner** (`decision` + `gateResult.publish`, PII/GDPR/ToS) — these already cover README quality, schema completeness and discoverability, so the audit maps to real fields, not guesswork.
3. If the Actor runs, add **Output Guard** (is live output healthy) and, for a release decision, **Deploy Guard** (does the candidate beat its baseline).
4. Branch on each decision field, then return one prioritized action plan ordered by `fixSequence` / expected impact.

Stop early to save spend: if Quality Monitor returns `qualityGates.storeReady: false`, or Compliance Scanner's `gateResult.publish` is `block`, surface those blockers and stop — don't spend runs on Output Guard or Deploy Guard until the publish-blocking issues are fixed.

Cost-aware: start with the single-target / smoke run; only fan out to a fleet-wide scan or A/B Tester (`runs: N` = 2N sub-Actor runs) once the cheap checks justify it, and state the expected sub-run count before any fan-out.

These Actors also accumulate their own cross-run memory when run on a schedule — Deploy Guard's `releaseMemory` and trusted baseline, Pipeline Preflight's pattern history, Fleet Health Report's `calibration`, and the Guard fleet's per-actor reliability history. Re-running compounds the value and is the only way drift gets caught; a one-off run can't see it. (The state lives in the Actors, not in this skill — so the moat is in re-running them, not in remembering IDs.)

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

For every other Actor in the table, fetch its schema first (step 2 of the workflow) — input fields differ per Actor — then build the input and branch on its documented decision field (`decision`, `decisionPosture`, or `releaseAction` — see the routing table).

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
