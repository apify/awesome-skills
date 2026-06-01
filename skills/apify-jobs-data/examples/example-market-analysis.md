# Example — Market & salary analysis

User: *"What's the hiring demand and salary range for senior backend engineers in
Berlin right now, and what skills are they asking for?"*

## Step 0 — Mode

Analysis ("demand / salary / skills"). No résumé needed.

## Step 1 — Anchors

| # | Anchor | Value |
|---|---|---|
| 1 | Role | `senior backend engineer` |
| 2 | Location / country | `Berlin` / `Germany` (full country name, per the schema) |
| 3 | Boards | `auto` → aggregator (broad sample) |
| 4 | Result cap | `50` **per board** ≈ 300 rows across ~6 boards — a bigger sample makes the stats meaningful |
| 5 | Recency | `1 month` |
| 6 | Filters | none (open market scan) |

## Steps 2–4 — Run

`agentx/all-jobs-scraper`, `country: "Germany"`, `posted_since: "1 month"`,
`max_results: 50` (per board). Returns 312 raw rows across 6 boards — cost ≈ $0.01 +
312 × $0.0023 ≈ **$0.73**.

## Step 5 — De-noise + normalize

| Funnel | Count |
|---|---|
| Raw | 312 |
| After hard filters | 312 (none set) |
| After dedupe | 247 (65 cross-board duplicates/reposts merged) |
| Flagged | 9 possible ghosts (re-stamped / pipeline language) |

247 clean, normalized rows. De-noise matters here: the raw 312 would have inflated
demand by ~26%.

## Step 6 — Analysis ([analysis.md](../reference/analysis.md))

> **Hiring demand:** 247 distinct senior-backend postings, last 30 days.
> Top employers: Example Cloud (11), Beispiel AG (8), Muster Tech (6), … (top-15 in CSV).
> 71% full-time, 18% contract; 54% remote-eligible, 22% hybrid, 24% on-site (coverage 100%).
>
> **In-demand skills** (share of 247 postings that name each):
> | Skill | Share |
> |---|---|
> | Go | 58% (143) |
> | Kubernetes | 49% (121) |
> | PostgreSQL | 44% (109) |
> | AWS | 41% (101) |
> | gRPC | 22% (54) |
>
> **Salary distribution** — **only 6% (15/247) of these Berlin postings disclosed a
> figure, and several had inconsistent currency/period** (a known pattern — a live
> test of this market found ~2% disclosure). That is **too thin for a reliable posted
> distribution**, so the posted numbers are shown only as a directional range
> (≈ €78k–€115k for the 15 that disclosed, after currency/period normalization), and
> the salary read leans on the Glassdoor benchmark instead:
> Glassdoor estimate for senior backend in Berlin ≈ **€95k median** (`memo23/glassdoor-scraper-ppr`).
> *Never present a posted-salary median from 15 points as the market rate — coverage
> is the headline here, not the number.*

## Step 7 — Deliver

Header with the funnel + coverage; the report above inline; the 247 clean rows written
to `2026-06-01_jobs_senior-backend-berlin.csv` + the Apify `datasetId` so the user can
re-aggregate or load it into a dashboard. `run_metadata.json` records the run, funnel,
and `salaryDisclosedPct: 6`.
