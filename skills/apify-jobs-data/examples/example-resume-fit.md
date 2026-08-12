# Example — Résumé-fit ranking + ATS gap

User: *"Rank senior backend roles in Berlin against my résumé and tell me which ATS
keywords I'm missing. Résumé: Python, Go, Postgres, Kubernetes, 7 yrs, led a team of 4."*

## Step 0 — Mode

Résumé-fit (a résumé is supplied → full Path-A scoring).

## Step 1 — Anchors

| # | Anchor | Value |
|---|---|---|
| 1 | Role | `senior backend engineer` |
| 2 | Location / country | `Berlin` / `Germany` |
| 3 | Boards | `auto` → aggregator |
| 4 | Result cap | `15` **per board** (≈90 across ~6 boards; fewer after some boards return less) |
| 5 | Recency | `2 weeks` |
| 6 | Filters | `salary_floor: 85000 EUR`, `job_type: fulltime` |
| 7 | Résumé | Python, Go, Postgres, Kubernetes; 7 yrs; team lead |

## Steps 2–5 — Run + de-noise

`agentx/all-jobs-scraper`, `country: "Germany"`, `job_type: "fulltime"`. 71 raw rows
returned across the boards — cost ≈ **$0.18** (71 × $0.0023 + start). Funnel:
`71 raw → 67 after dropping 4 below the €85k floor → 38 after merging 29 duplicates`;
3 ghost-flagged. 38 clean rows.

## Step 6 — Résumé-fit ([fit-scoring.md](../reference/fit-scoring.md))

38 sub-agents (batched), each reads the full JD against the résumé and returns the
contract (fit, matched skills, gaps, `ats_keywords_missing`, hook). Ranked top:

| Fit | Band | Title | Company | Salary | Matched | ATS to add |
|---:|---|---|---|---|---|---|
| 92 | 🟢 | Senior Backend Engineer (Go) | Example Cloud GmbH | €90–110k | Go, Postgres, Kubernetes, team lead | Kubernetes, gRPC |
| 84 | 🟢 | Senior SWE, Platform | Beispiel AG | €88–105k | Python, Kubernetes | (none — résumé covers it) |
| 71 | 🟡 | Backend Engineer | Muster Tech | undisclosed | Python, Postgres | — |
| 58 | 🟠 | Staff Engineer | Probe Labs | €120k+ | Go, Kubernetes | Terraform (real gap) |

ATS note for row 1: the résumé says "container orchestration" — the JD says
**Kubernetes**, an exact ATS keyword the screen looks for, so name it explicitly;
**gRPC** is listed under the Acme project but not surfaced. Both `honest_to_add: true`.
Row 4's `Terraform` is `honest_to_add: false` — a genuine gap, don't fake it.

## Step 7 — Deliver

Header (funnel, full fit score), the ranked table inline with apply-ready briefs for
the 🟢/🟡 rows (opener + ATS keywords to add + gaps), and the full ranked set written to
`2026-06-01_jobs_resume-fit.csv` + `run_metadata.json`.
