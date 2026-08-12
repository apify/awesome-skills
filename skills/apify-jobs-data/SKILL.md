---
name: apify-jobs-data
description: Extract clean, de-noised job-posting data from LinkedIn, Indeed, Glassdoor, Google Jobs, and 20+ boards in one Apify run — deduplicated across boards with ghost jobs and reposts removed and fields normalized — then analyze it (deduped hiring demand, in-demand skills, coverage-labeled salary distribution), export it (CSV / JSON / Apify dataset) for dashboards and BI, or rank it against a résumé. Use when the user asks to scrape job postings, build a job dataset, analyze hiring demand or in-demand skills or salary ranges for a role or market, export job data for a dashboard or spreadsheet, dedupe job listings across boards, filter out ghost or fake jobs, or rank jobs by fit to a résumé. Triggers - "scrape job postings for X", "what skills are in demand for Y", "salary range for Z in [location]", "export job data to CSV", "filter out the ghost jobs", "which of these jobs fit my résumé".
author: Oleg Martinez
author_url: https://github.com/ezumyn-aliegm
---

# Jobs Data

Extract clean, structured job-posting data from 20+ boards in one Apify run, then put
it to use. The pipeline is the same regardless of purpose:

**acquire → de-noise → normalize → { analyze | export | rank by résumé }**

The reusable value is the cleaned dataset: postings deduplicated across boards, with
ghost jobs and reposts removed and fields normalized to a consistent schema. Ghost-job
and repost pollution corrupts demand counts, salary statistics, and dashboards just as
much as it wastes a job seeker's time — so de-noise is the shared core, and every
output mode runs on top of it.

**Never invent a posting, a salary, a count, or a keyword.** Everything is scraped
live from a named Apify Actor and carries its source; missing fields stay blank, and
every statistic reports the share of postings it is computed from — see
[Quality rules](#quality-rules).

Ghost-job and repost detection is the part that depends on scraping rather than the
LLM: it compares the same job description across boards and tracks re-stamped posting
dates. The Actors do the data work; the agent routes, de-noises, aggregates, and grounds:

| Step | Apify Actor | Agent |
|---|---|---|
| Acquire across 20+ boards | `agentx/all-jobs-scraper` | routes the query |
| De-noise ghost jobs / reposts | cross-board scraped fields — first-seen date, re-stamp history, JD-body match across "company" names | applies the rule |
| Salary benchmark (optional) | `memo23/glassdoor-scraper-ppr` | aggregates, labels coverage |

## Note on overlap with analysis-first job skills

A more analysis-first skill may also answer "hiring demand / in-demand skills /
salary" questions. This skill's center of gravity is the **cleaned dataset** — ghost
jobs, reposts, and cross-board duplicates removed and fields normalized — which every
mode then runs on. If you only need a quick market read, an analysis-only skill is
lighter. Reach for this one when **data quality matters** (deduped demand counts,
coverage-labeled salary stats), when you need the **raw rows exported** to CSV / an
Apify dataset for a dashboard, or when you need a **résumé ranked** against live
postings — none of which an analysis-only skill produces.

## Output modes — pick one or more

The shared core (Steps 1–5) is identical; Step 6 produces whichever mode(s) the user
wants. Default to whatever the request implies; if unclear, ask.

| Mode | Produces | Reference |
|---|---|---|
| **Market & salary analysis** | hiring demand on **deduped** counts (by company / location / seniority), in-demand skills, remote-hybrid mix, and **coverage-labeled** salary distribution | [reference/analysis.md](reference/analysis.md) |
| **Structured export** | the normalized rows as CSV / JSON, or the raw Apify dataset ID for direct BI / dashboard ingestion | [reference/output-formats.md](reference/output-formats.md) |
| **Résumé-fit** | postings ranked against a résumé, with ATS-keyword gaps and apply-ready briefs | [reference/fit-scoring.md](reference/fit-scoring.md) |

## Cost discipline (best quality for the lowest cost)

This is a design goal, not an afterthought — keep every run as cheap as it can be
while still answering the question:

- **One cheap actor, no subscriptions.** Default to the pay-per-result aggregator
  (~$0.0023/job). A typical run is **cents** (a live 60-job test billed $0.18).
- **Smallest sample that answers it.** `max_results` is *per board* (×~6 boards), so
  start small — a quick scan needs ~10–15/board; a market analysis ~25–50/board — and
  scale only if the result is too thin. Always estimate, and confirm before a big run.
- **One run feeds every mode.** Analysis, export, and résumé-fit all read the *same*
  scrape — never re-scrape to add a second mode.
- **De-noise so you never pay for junk.** Removing ghost jobs / reposts / duplicates
  keeps the billed sample honest and the counts real.
- **For salary, prefer the Glassdoor benchmark over a mega-scrape.** Salary disclosure
  is low (~2–6% in many markets), so scraping thousands of postings to harvest a few
  disclosed figures is wasteful — one cheap `memo23/glassdoor-scraper-ppr` call per
  company gives a better signal for less.

## Prerequisites
(No need to check this upfront.)

Two execution paths — pick the one that matches your environment.

**MCP path (default in an agent session with MCP, recommended).** If the Apify MCP
server is connected, no setup is needed — auth runs through the user's Apify account.
Use the `call-actor`, `get-actor-run`, and `get-dataset-items` MCP tools.

**CLI path (scripted / non-interactive execution).** Requires the
[Apify CLI](https://docs.apify.com/cli) v1.5.0+ and auth via `apify login` or an
`APIFY_TOKEN` env var ([get a token](https://console.apify.com/settings/integrations)).
Every CLI call in this skill carries three flags — `--json`,
`--user-agent apify-awesome-skills/apify-jobs-data`, and `2>/dev/null`.

**Responsible use.** These Actors scrape third-party boards (LinkedIn, Glassdoor,
Indeed, Google Jobs) against those sites' Terms of Service — the user's call to make.
All routes run on Apify's infrastructure (no user login), so they never put the
user's own board accounts at risk.

## Workflow

Copy this checklist and track progress.

```
Task Progress:
- [ ] Step 0: Pick the output mode(s)
- [ ] Step 1: Collect the query anchors (one block)
- [ ] Step 2: Route to the right board Actor(s) (primary + fallback)
- [ ] Step 3: Build the input, estimate cost, confirm if over threshold
- [ ] Step 4: Run, wait, pull the dataset
- [ ] Step 5: De-noise + normalize into clean rows
- [ ] Step 6: Produce the selected mode(s) — analysis / export / résumé-fit
- [ ] Step 7: Deliver, with provenance and coverage
```

### Step 0: Pick the output mode(s)

Decide what the user wants *done with the data* — it changes only Step 6, not the
shared core. Infer from the request; confirm if ambiguous:

- "what skills/salary/demand for X", "job-market for Y" → **Market & salary analysis**.
- "scrape / export / give me a dataset / CSV for a dashboard" → **Structured export**.
- "which of these fit my résumé", "rank these for me" → **Résumé-fit** (needs a résumé; anchor #7).
- Multiple are fine — e.g. analysis + export of the same run.

### Step 1: Collect the query anchors

Ask these as **one block** before any Actor call. Defaults shown — always surface
them so the user can override. (Anchor-block pattern from `apify-verified-email-finder`.)

1. **Role / keywords** — e.g. `senior backend engineer`. Required.
2. **Location** — city, country, or `remote`. Required. `remote` flips the remote-only filter on.
3. **Boards** — `auto` (default → aggregator, all major boards) or a named subset (`linkedin`, `indeed`, `glassdoor`, `google`). Drives Step 2.
4. **Result cap** — for the aggregator this is **per board** (`max_results: 25` ≈ 150 rows across ~6 boards), **minimum 10**. Start small (`10–15` for a quick scan, `25–50` for analysis) and scale only if the sample is too thin — it's the main cost lever, so budget `max_results × boards` ([Cost discipline](#cost-discipline-best-quality-for-the-lowest-cost), Step 3). Maps to each Actor's own field (`max_results` / `maxItems` / `rows` — actor-index.md).
5. **Recency window** — default `2 weeks`. The aggregator takes this as a natural-language string (`"2 weeks"`, `"1 month"`), not a day count.
6. **Filters** — optional constraints that *drop* a posting: `salary_floor`, `remote_only`, `job_type` (full-time / contract / internship). Collect what the user volunteers.
7. **Résumé / profile** — *only for résumé-fit mode*: résumé text or a must-have + nice-to-have skill list. Without it, résumé-fit falls back to a mechanical score labeled `Fit (partial)`.

**Ambiguity rule:** if role or location is missing or vague, ask **one** clarifying
question before running. Never burn Actor compute on a guessed query.

### Step 2: Route to the right Actor(s)

Default to the **aggregator** — one run, 20+ boards (LinkedIn, Indeed, Glassdoor,
Google Jobs, and more), country-aware routing, cheapest per-result. **Every Actor here
is pay-per-result — no subscriptions.** The aggregator already covers LinkedIn and
Google cheaply, so there is no need for a per-board LinkedIn or Google subscription
Actor.

| User wants | Actor | Notes |
|---|---|---|
| All boards (default) | `agentx/all-jobs-scraper` | One query → LinkedIn, Indeed, Glassdoor, Google Jobs, ZipRecruiter +15. **Pay-per-result** (~$0.0023/job). |
| Indeed only (cheap, focused) | `misceres/indeed-scraper` | **Apify-maintained**, pay-per-result (~$3/1,000). |
| Glassdoor salary benchmark | `memo23/glassdoor-scraper-ppr` | Pay-per-result; analysis mode only, to cross-check posted salaries (analysis.md). |

Pin to the aggregator unless the user explicitly wants a single board. If the
aggregator's coverage of one board is thin on a given run (boards block scrapers),
note it in the header rather than reaching for a paid per-board Actor. Full schemas
and field mappings: [reference/actor-index.md](reference/actor-index.md).

**Cross-board parallel runs.** If the user names two+ boards, run their primaries in
parallel (background each `call-actor` / CLI invocation), tag every row with its
`Source` board, and dedupe in Step 5.

### Step 3: Build the input, estimate cost, confirm

Map anchors → the chosen Actor's field names (per-Actor table in
[reference/actor-index.md](reference/actor-index.md)). Aggregator example:

```json
{ "keyword": "senior backend engineer", "location": "Berlin",
  "country": "Germany", "max_results": 50, "posted_since": "2 weeks", "remote_only": false }
```

Verified-from-live-schema notes for the aggregator: `country` is a **full country
name** (`Germany`, `United States`), not an ISO-2 code; `posted_since` is a
**natural-language string** (`"2 weeks"`), not a number of days; `job_type` is
`fulltime` / `parttime` / `contract` / `internship` / `all` (no hyphen); and
**`max_results` is per board** — the actor fans out to ~6 boards, so `max_results:
50` returns ≈ 300 rows. Other Actors use their own field names (actor-index.md).

**Estimate before running.** Formula and live rates in
[reference/gotchas.md](reference/gotchas.md). Guardrails:

- Estimated cost **> $5** → warn with a rough number ("around $X").
- Estimated cost **> $20** → require explicit confirmation before running.
- All routes are pay-per-result — cost scales with `max_results × boards`. Keep
  `max_results` modest to keep runs in the cents.

### Step 4: Run, wait, pull the dataset

**MCP path:** `call-actor` with `actor`, `input`, `callOptions`
`{"timeout": 900, "memory": 2048}`. It returns `runId` + `datasetId`. If `status` is
`RUNNING`, poll `get-actor-run` (waitSecs ≤ 45) until `SUCCEEDED`. Capture both IDs for
the `run_metadata.json` sidecar (and surface `datasetId` in export mode).

**CLI path:**

```bash
apify actors call "agentx/all-jobs-scraper" \
  --input '{"keyword":"senior backend engineer","location":"Berlin","country":"Germany","max_results":50,"posted_since":"2 weeks"}' \
  --json --user-agent apify-awesome-skills/apify-jobs-data 2>/dev/null
# then, using the returned defaultDatasetId:
apify datasets get-items DATASET_ID --format json \
  --user-agent apify-awesome-skills/apify-jobs-data 2>/dev/null > /tmp/jobs.json
```

On the MCP path, pull with `get-dataset-items` (`clean: true` + a `fields` list). If
the dataset exceeds the response cap, fetch directly:
`curl 'https://api.apify.com/v2/datasets/<id>/items?clean=true&fields=...' | jq`.

**Report every failure explicitly** (Actor, input, error) — never silently drop a
board. If the primary returns 0, switch to the fallback (Step 2) before concluding "no
data". A board returning 0 while others return results is usually a block, not an empty
market.

### Step 5: De-noise + normalize into clean rows

The shared core. Two parts:

1. **De-noise** — walk every row and remove the noise: duplicates/reposts across
   boards, hard-filter violations, off-target roles; flag (don't drop) ghost jobs and
   staffing-agency reposts. Skipped rows are **kept** in a separate `Skipped` section
   with a one-line reason — never silently dropped. Apply hard filters first, then
   dedupe, so the funnel reads `raw → after hard filters → after dedupe → clean`. Full
   detection logic: [reference/skip-pass.md](reference/skip-pass.md).
2. **Normalize** — map each surviving row onto the consistent schema in
   [reference/output-formats.md](reference/output-formats.md) (title, company,
   location, remote flag, salary min/max/currency, seniority, skills, posted date,
   source board, apply URL). Field coverage varies by board — leave missing fields
   blank, never inferred.

**Empty results are signal, not failure** (from `apify-easy-competitive-intelligence`):
0 postings for a niche role in a small market is real information — report it, suggest
widening recency or location, don't fabricate filler rows.

### Step 6: Produce the selected mode(s)

Run on the clean, normalized rows from Step 5.

- **Market & salary analysis** → compute the aggregations (demand, skills, salary
  distribution, remote mix) with coverage labels. Full method:
  [reference/analysis.md](reference/analysis.md).
- **Structured export** → write the normalized rows to CSV / JSON, and surface the raw
  Apify `datasetId` for direct ingestion. Schema and formats:
  [reference/output-formats.md](reference/output-formats.md).
- **Résumé-fit** → a per-posting sub-agent reads each full JD against the résumé and
  returns fit, matched skills, gaps, the **ATS keywords the résumé is missing**, and a
  one-line hook — not keyword counting. Contract and rubric:
  [reference/fit-scoring.md](reference/fit-scoring.md).

If the user picked more than one mode, produce each from the same run — no re-scrape.

### Step 7: Deliver, with provenance and coverage

Lead with a one-paragraph header: boards searched, the funnel
(`raw → after hard filters → after dedupe → clean`, plus flagged ghost/agency counts),
date window, and the run cost. Then the mode output(s).

- **Every statistic carries its coverage** — e.g. "median salary €95k, from the 41% of
  postings that disclosed a figure". A number without coverage is misleading.
- **Provenance** — `Source` board(s) + apply URL per row; `runId` + `datasetId` in a
  `run_metadata.json` sidecar so any figure is re-verifiable.
- Synthesize for analysis/résumé-fit; write the full row set to the file. For export,
  the file (and dataset ID) *is* the deliverable.

## Worked examples

- Market & salary analysis: [examples/example-market-analysis.md](examples/example-market-analysis.md)
- Résumé-fit ranking + ATS gap: [examples/example-resume-fit.md](examples/example-resume-fit.md)

## Quality rules

- **No fabrication, ever.** Never invent a posting, salary, count, or keyword. Missing
  fields stay blank. (From `apify-verified-email-finder` / `apify-link-prospecting-outreach`.)
- **Every statistic reports coverage.** State the share of postings a figure is
  computed from; salary stats especially, since many postings don't disclose.
- **Provenance.** `Source` board(s) + apply URL per row; `runId` + `datasetId` in
  `run_metadata.json` so any row or figure is re-verifiable.
- **Surface, don't suppress.** Skipped / ghost / duplicate rows stay in the output with
  a reason. Empty results are reported as signal, not hidden.
- **ATS suggestions stay honest** (résumé-fit mode): only surface missing keywords the
  user can truthfully claim; never coach them to lie on a résumé.
- **Don't be condescending about gaps.** When a field is missing, state the fact and
  stop. (From `apify-link-prospecting-outreach`.)
- **Lowest cost for the quality needed.** Cheapest actor, smallest sufficient sample,
  one run for all modes, estimate before scaling — see [Cost discipline](#cost-discipline-best-quality-for-the-lowest-cost).

## Cost & pricing

Every Actor here is **pay-per-result** — no subscriptions. A run costs cents (a live
60-job test billed $0.18). Cost scales with `max_results × boards`, so keep
`max_results` modest. The optional Glassdoor salary benchmark adds a small per-company
cost. Live rates and the estimate formula are in [reference/gotchas.md](reference/gotchas.md)
— always check the Apify console before a large run.

## Error handling & gotchas

See [reference/gotchas.md](reference/gotchas.md) — board blocks, empty results,
location-format quirks, per-board cost math, and recovery flows.
