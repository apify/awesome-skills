---
name: apify-job-market-intelligence
description: Build job-market intelligence from public job boards using Apify Actors. Use when the user asks to analyze hiring demand, find companies hiring for a role, compare job-market trends, scrape LinkedIn Jobs, Google Jobs, Indeed, or Glassdoor, extract required skills from postings, rank target companies, benchmark salaries, or create a focused job-search pipeline.
author: Samyak Jain
author_url: https://github.com/Samyak-jain7
---

# Job Market Intelligence

Turn public job postings into a ranked job-market report: companies hiring, skills in demand, salary signals, remote/hybrid mix, recency, application URLs, and a focused target list.

## Prerequisites

- Apify account: https://apify.com
- Authentication through one of:
  - `apify login`
  - `APIFY_TOKEN` environment variable
  - Apify MCP connector at https://mcp.apify.com

Do not check credentials upfront unless the user asks you to run the Actors. For planning-only work, produce the query plan and stop before spending credits.

## Workflow

Copy this checklist and track progress:

```text
Task Progress:
- [ ] Step 1: Collect the job-search anchors
- [ ] Step 2: Pick the right Actor route
- [ ] Step 3: Fetch the Actor input schema
- [ ] Step 4: Run the Actor with a capped result limit
- [ ] Step 5: Normalize, dedupe, and score the jobs
- [ ] Step 6: Deliver the report and export file
```

### Step 1: Collect the Job-Search Anchors

Ask for missing anchors in one short block before running any Actor:

| Anchor | Examples | Default |
|---|---|---|
| Role or keywords | `backend engineer`, `SDE2 Java`, `AI agent engineer` | Required |
| Location | `Bangalore`, `India`, `Remote`, `United States` | Required |
| Experience level | `entry`, `mid`, `senior`, `staff`, `internship` | `mid` |
| Recency | `24h`, `week`, `month`, `any` | `week` |
| Work mode | `remote`, `hybrid`, `onsite`, `any` | `any` |
| Max results | `50`, `100`, `250` | `100` |
| Output format | `markdown`, `csv`, `json` | `markdown + csv` |

If the user gives a company list, treat it as a company-focused search. If the user gives only a broad role, run a market scan.

### Step 2: Pick the Right Actor Route

Prefer the narrowest route that answers the question with the lowest waste.

| User need | Primary Actor | Secondary Actor | Best for |
|---|---|---|---|
| LinkedIn-heavy sourcing or company-focused roles | `scrapeengine/linkedin-jobs-scraper` | `automly/linkedin-jobs-scraper` | Fresh LinkedIn postings, company jobs, work-mode filters |
| Broad market scan across Google Jobs | `epctex/google-jobs-scraper` | `apify/google-search-scraper` | Coverage across multiple job boards and direct employer pages |
| Salary, rating, and employer-review context | `crawlerbros/glassdoor-jobs-scraper` | `simpleapi/glassdoor-jobs-scraper` | Salary ranges, company rating, Glassdoor-specific metadata |
| Indeed-specific job board analysis | `misceres/indeed-scraper` | Actor Store search for `indeed jobs scraper` | Indeed listings and regional job-market checks |

Routing rules:

- Use one Actor for a normal request. Do not run all boards unless the user asks for cross-board coverage.
- For "find me target companies", start with Google Jobs or LinkedIn Jobs, then dedupe by company.
- For "is this role in demand", run a broader Google Jobs scan and summarize skills, locations, and company clusters.
- For salary benchmarking, prefer Glassdoor first, then fill gaps from Google Jobs or LinkedIn salary fields if available.
- If a chosen Actor fails or has a schema mismatch, search the Apify Store for a replacement and tell the user which route changed.

### Step 3: Fetch the Actor Input Schema

Always fetch the current Actor schema before constructing input. Job Actors change field names often.

```bash
apify actors info "scrapeengine/linkedin-jobs-scraper" --input \
  --json \
  --user-agent apify-awesome-skills/apify-job-market-intelligence \
  2>/dev/null
```

If the schema field names differ from this skill's examples, trust the live schema.

Useful discovery command:

```bash
apify actors search "linkedin jobs scraper" \
  --json \
  --user-agent apify-awesome-skills/apify-job-market-intelligence \
  2>/dev/null
```

### Step 4: Run the Actor

Keep early runs small. A 50-100 item run is enough to validate quality before scaling.

Example LinkedIn Jobs run:

```bash
apify actors call "scrapeengine/linkedin-jobs-scraper" \
  --input '{"keywords":"SDE2 Java backend engineer","location":"Bangalore, India","publishedAt":"week","workType":"hybrid","maxJobs":100}' \
  --json \
  --user-agent apify-awesome-skills/apify-job-market-intelligence \
  2>/dev/null
```

Example Google Jobs run:

```bash
apify actors call "epctex/google-jobs-scraper" \
  --input '{"queries":["backend engineer Java Bangalore"],"maxItems":100}' \
  --json \
  --user-agent apify-awesome-skills/apify-job-market-intelligence \
  2>/dev/null
```

Example Glassdoor run:

```bash
apify actors call "crawlerbros/glassdoor-jobs-scraper" \
  --input '{"keyword":"backend engineer","location":"Bangalore, India","maxItems":100}' \
  --json \
  --user-agent apify-awesome-skills/apify-job-market-intelligence \
  2>/dev/null
```

Fetch results from the returned dataset:

```bash
apify datasets get-items DATASET_ID \
  --format json \
  --user-agent apify-awesome-skills/apify-job-market-intelligence \
  2>/dev/null
```

### Step 5: Normalize, Dedupe, and Score

Normalize each job into this common shape:

| Field | Notes |
|---|---|
| `title` | Original title, unchanged |
| `company` | Hiring company |
| `location` | Raw location plus parsed country/city if available |
| `work_mode` | `remote`, `hybrid`, `onsite`, or `unknown` |
| `posted_at` | Raw date plus parsed age in days when available |
| `salary` | Raw salary text or structured min/max if available |
| `skills` | Extracted from title and description |
| `seniority` | `entry`, `mid`, `senior`, `staff`, or `unknown` |
| `apply_url` | Direct apply URL if present, else job URL |
| `source` | Actor ID and source board |

Dedupe in this order:

1. Exact `apply_url`.
2. Exact `job_url`.
3. Lowercased `(company, title, location)` within the same source.
4. Fuzzy duplicate if company and title are almost identical and posted date is within 3 days.

Score each job from 0-100:

| Signal | Points |
|---|---:|
| Role keyword match in title | 25 |
| Required skills match user's target stack | 20 |
| Experience level match | 15 |
| Location/work-mode match | 15 |
| Posted within requested recency | 10 |
| Direct apply URL present | 5 |
| Salary present | 5 |
| Company quality signal present (rating, known brand, or clear domain) | 5 |

Never fabricate missing salaries, ratings, or skills. Use `unknown` and explain the gap.

### Step 6: Deliver the Report

For Markdown output, use this structure:

```text
## Job Market Snapshot

- Query:
- Source Actor:
- Jobs fetched:
- Jobs after dedupe:
- Date range:
- Location/work mode:

## Top Targets

| Rank | Score | Company | Role | Location | Posted | Salary | Why it matches | Apply |

## Market Signals

- Top skills:
- Hiring clusters:
- Remote/hybrid mix:
- Salary signal:
- Companies hiring multiple roles:

## Next Actions

- Apply now:
- Research first:
- Skip:
```

For CSV output, include:

```text
rank,score,company,title,location,work_mode,posted_at,salary,skills,seniority,source,apply_url,why_it_matches
```

## Cost Guardrails

- Start with `maxItems` or `maxJobs` <= 100 unless the user explicitly asks for a larger scrape.
- Tell the user before running multiple boards for the same query.
- Do not scrape full job descriptions from multiple boards if title/company/location is enough.
- If the first 20 results are low quality, stop and adjust query terms instead of increasing volume.

## Error Handling

- `Actor input is invalid`: fetch the live input schema again and rebuild the payload.
- `No results`: broaden location, relax recency, or switch from LinkedIn-only to Google Jobs.
- `Too many irrelevant jobs`: add exact title terms, seniority, and negative keywords.
- `Blocked or timed out`: reduce max results and enable the Actor's proxy settings if the schema supports them.
- `Dataset too large`: fetch only needed fields first, then pull full descriptions only for top-ranked jobs.
