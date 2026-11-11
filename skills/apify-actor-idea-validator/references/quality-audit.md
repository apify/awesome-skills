# Module: Quality audit (issues + run health)

Run from Step 7 of [SKILL.md](../SKILL.md). It answers three questions:

1. **Which competitors are weakest?** Bug density, slow fixes, high failure rates.
2. **What do users ask for that nobody has built?** Recurring feature requests, clustered as potential powerups.
3. **What breaks across the market?** Recurring bugs, clustered as market pain points. Fixing one is a differentiator.

Output: `~/apify-reports/apify-actor-quality-audit-<slug>-<YYYY-MM-DD>.md`. Use the template in [report-templates.md](report-templates.md#quality-audit).

## A1 — Scope

Use the relevant Actors from Step 6 of SKILL.md. When there are **20 or fewer**, audit all of them. Above that, audit the top 15 by MAU plus any Actor whose title matches the idea's segment. In young niches, many small Actors carry the only issue history.

## A2 — Resolve IDs and run health (free, public)

```bash
curl -s "https://api.apify.com/v2/acts/OWNER~ACTOR"
```

From `data`, take:
- `id`: the 17-character actorId, needed for issues
- `stats.totalUsers30Days` (MAU)
- `stats.publicActorRunStats30Days`: `TOTAL`, `SUCCEEDED`, `FAILED`, `TIMED-OUT`, `ABORTED` (missing keys = 0)
- `modifiedAt`, `isDeprecated`

Then compute:
- `failureRate` = (`FAILED` + `TIMED-OUT`) / `TOTAL`. This is the quality signal: ⚠ at 10% or more, 🔴 at 25% or more.
- `abortRate` = `ABORTED` / `TOTAL`. This is a secondary signal: users killing slow or runaway runs, or limits that aren't clear.
- `lowSample` = `TOTAL` < 50. About 30 SUCCEEDED runs a month is usually just Apify's daily automated test, so don't call such an Actor "healthy".

Caveat: a run that SUCCEEDED with **0 items** counts as healthy here. If issues mention "no results", say that run status understates breakage.

Query sequentially or in small batches. Large parallel bursts get throttled and return empty `data`. Mark those Actors as "no stats", and don't drop them.

## A3 — Fetch open AND closed issues

```bash
curl -s "https://apify.com/api/actor-issues/data?actorId=ACTOR_ID&statusOrName=open"
curl -s "https://apify.com/api/actor-issues/data?actorId=ACTOR_ID&statusOrName=closed"
```

**The list is nested at `body.json.list`, not `body.list`.** Reading `body.list` silently returns nothing, and every Actor looks issue-free. If every Actor comes back at 0, sanity-check against a known Actor with issues (e.g. `compass/crawler-google-places`).

Each entry has `_id`, `title`, `status`, `source`, `createdAt` and `lastCommentedAt`. Keep up to the 30 most recent per status per Actor, and note any cap in Methodology.

Why fetch both statuses: in low-MAU niches the open queue is often empty. Closed issues still show what broke, and `closedAt - createdAt` measures how responsive the maintainer is.

## A4 — Issue bodies (optional, for ambiguous titles)

Slug = lowercase title, runs of non-alphanumerics replaced with `-`, trimmed, plus `-<_id>`:

```bash
curl -s "https://apify.com/api/actor-issues/data?actorId=ACTOR_ID&statusOrName=SLUG"
```

Read `body.json.detail.issueDetail` (with `closedAt`) and the length of `issueComments`. If `detail` is null, classify on the title only.

## A5 — Classify

Use the regex rules in [issue-taxonomy.md](issue-taxonomy.md): **feature-request**, **bug**, **support** or **other**. If both bug and feature patterns match, treat it as ambiguous, and send ambiguous and `other` issues to the model in batches of 10 to get `{ id, label, rationale }`. Titles that start with "Feature request:" are always feature requests.

## A6 — Aggregate and cluster

Per Actor, record:
- open, closed, bug, feature and support counts
- average age of open issues and the oldest one
- median resolution time in hours
- `runs30d`, `failureRate`, `abortRate`, `lowSample`, deprecated

Cluster feature-request titles into **potential powerups** and bug titles into **market pain points**:
- Use an LLM pass over titles only.
- Minimum cluster size: 2 issues.
- A cluster must span 2+ Actors to count as a *market* pain point. Otherwise list it as context.

If no cluster clears the threshold, say so and name the clearest singleton.

**Lowest-quality Actor:** decide on open bugs first, then failure rate (ignoring low-sample Actors). If no Actor has open bugs, use the highest failure rate among Actors with 50+ runs, and name which signal decided it.
