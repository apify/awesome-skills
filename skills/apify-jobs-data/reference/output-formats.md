# Output Formats — apify-jobs-data

The normalized row schema (the cleaned data, shared by every mode), the export
formats, and the résumé-fit output. Analysis output is in
[analysis.md](analysis.md).

## Normalized row schema (the cleaned data)

Step 5 maps each surviving posting onto this consistent schema, regardless of which
board it came from. This is what the export mode writes and what every other mode
reads. Field coverage varies by board — **missing fields stay blank, never inferred.**
The `Raw field` column maps from the verified `agentx/all-jobs-scraper` output; other
Actors use their own names (fetch the live schema).

| Normalized field | Raw field (agentx) | Notes |
|---|---|---|
| `title` | `title` | |
| `company` | `company_name` | normalize (strip Inc/GmbH/Ltd suffixes) for grouping |
| `location` | `location` | city / region |
| `remote` | `is_remote` / `work_from_home` | → `remote` / `onsite` / blank |
| `salary_min`, `salary_max`, `salary_currency`, `salary_period` | `salary_minimum`, `salary_maximum`, `salary_currency`, `salary_period` | as published; blank if undisclosed (often is). Currency/period can be inconsistent — normalize before any stat |
| `seniority` | `job_level` / `experience_range` | mark when inferred from title |
| `job_type` | `job_type` | |
| `skills` | `skills` (list) | else parse from `description` |
| `posted` | `posted_date` | `re_stamped: true` if ghost-flagged (skip-pass rule 3) |
| `source` | `platform` | board the row came from |
| `apply_url` | `official_url` / `platform_url` | primary link |
| `other_sources` | — | apply links merged from de-duplicated rows |
| `flags` | — | `ghost?` / `agency?` (skip-pass flags), blank if clean |

(The raw output also includes `applicant_count`, `easy_apply`, `company_rating`,
`emails`, `phones`, and more — pass through to the export if the user wants them.)

## Export mode

- **CSV** — UTF-8, header row, quoted fields. One file of the clean rows, named
  `YYYY-MM-DD_jobs_<role-slug>.csv`, plus the `run_metadata.json` sidecar.
- **JSON** — `{ "rows": [...], "skipped": [...], "meta": {...} }`.
- **Raw Apify dataset** — surface the `datasetId` from Step 4 so the user can ingest it
  directly into a dashboard/BI tool via the Apify API
  (`https://api.apify.com/v2/datasets/<id>/items?format=csv`) without re-running.
- **Skipped rows** travel in a separate `skipped` array / file section, each with a
  `skip_reason` (hard-filter violation, off-target). De-duplicated rows are **not**
  here — they're merged into the surviving row's `other_sources` as a count. Ghost /
  agency *flagged* rows stay in the main set with a `flags` value.

Never paste a 100-row table into chat — write the file, show a short sample.

## Résumé-fit mode output

One row per surviving posting, ranked by fit. Extends the normalized schema with the
sub-agent fields (contract in [fit-scoring.md](fit-scoring.md)):

| Column | Source |
|---|---|
| `fit` | 0–100 (`Fit (partial)` if no résumé) |
| `band` | 🟢 strong / 🟡 worth-a-look / 🟠 stretch / 🔴 low |
| `matched_skills` | grounded in JD + résumé |
| `gaps` | prep targets, not necessarily disqualifiers |
| `ats_keywords_missing` | JD-required terms the résumé lacks (honest-to-add flagged) |
| `hook` | one-line tailored opener |

For the top 🟢/🟡 rows, render a short **apply-ready brief** inline (grounded — no
fabrication):

```
🟢 92 · Senior Backend Engineer (Go) · Example Cloud GmbH · €90–110k
  Opener: "~7 years building Go + Kubernetes services on Postgres, led a team of four —
           the multi-region work in your JD lines up closely."
  ATS keywords to add (honest): "Kubernetes" (résumé says "container orchestration"),
           "gRPC" (listed under the Acme project — name it explicitly).
  Gap to prep: distributed tracing at scale (not on your résumé).
  → Apply: <url>
```

The full ranked set goes to the file.

## Header summary (always, Step 7)

Lead with it, above any mode output:

- Role + location queried; boards searched (and any that returned 0 / were blocked).
- **Funnel:** `raw → after hard filters → after dedupe → clean` (+ `N ghost-flagged`,
  `M agency-flagged`).
- Date window; run cost.
- For analysis: coverage notes (e.g. salary disclosed by only ~6% of postings (varies sharply by region)). For
  résumé-fit: whether the score is **full** (sub-agent read the JDs) or **partial**.

Example:

> **126 senior backend postings in Berlin** across LinkedIn, Indeed, Glassdoor, Google
> Jobs. 154 raw → 150 after filters → 126 after merging 24 duplicate/repost rows; 5
> flagged as possible ghosts (re-stamped). Window: last 2 weeks. Run cost ≈ $0.30.
> Salary disclosed by 6% (8/126). Analysis below; clean rows in the CSV + dataset `<id>`.

## `run_metadata.json` sidecar

Written next to every deliverable for traceability and re-runs:

```json
{
  "generatedAt": "YYYY-MM-DDTHH:MM:SSZ",
  "modes": ["analysis", "export"],
  "anchors": { "role": "...", "location": "...", "boards": "auto", "resultCap": 100, "postedSince": "2 weeks" },
  "actors": [{ "actorId": "agentx/all-jobs-scraper", "runId": "...", "datasetId": "..." }],
  "funnel": { "raw": 154, "afterHardFilters": 150, "afterDedupe": 126, "ghostFlagged": 5, "agencyFlagged": 0 },
  "coverage": { "salaryDisclosedPct": 6 },
  "estimatedCostUsd": 0.30
}
```

Never fabricate values. Missing dataset fields stay blank everywhere.
