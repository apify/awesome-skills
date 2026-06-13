---
name: apify-job-market-intelligence
description: Map a job market from live listings — who is hiring, what they pay, where the roles are, remote vs onsite, and how employers are rated. Routes a role + location to an Indeed scraper that returns salaries, companies, job types and descriptions, aggregates them into a market snapshot (salary range, top hirers, remote share, demand by location), and optionally pulls employer reviews for reputation. Use when a user asks to research a job market, benchmark salaries for a role, find companies hiring for a position, scope hiring demand in a city, build a recruiting target list, analyze a competitor's hiring, or check what a role pays.
author: Renzo Madueno
author_url: https://github.com/renzomacar
---

# Job Market Intelligence

Turn a `role + location` into a labor-market snapshot: salary range, the companies hiring, remote vs onsite split, demand by location, and (optionally) how those employers are rated. Built for recruiters, staffing agencies, compensation/HR teams, job seekers benchmarking an offer, and sales teams using hiring as a growth/budget signal.

Unlike a generic SaaS competitive-intelligence workflow, this skill is **labor-market-first**: it reasons over live job listings (salaries, employers, role types) rather than product/pricing pages.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

Two execution paths, same Actors:

- **MCP path (default in Claude sessions).** If the [Apify MCP server](https://mcp.apify.com) is connected, no setup is needed. Use the `call-actor` and `get-dataset-items` tools.
- **CLI path (portable / scheduled / non-Claude).** Apify CLI + token. Every CLI call uses three flags: `--json`, `--user-agent apify-awesome-skills/apify-job-market-intelligence`, and `2>/dev/null`.

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Step 1: Collect the market brief (role(s), location, country, depth, lens)
- [ ] Step 2: Run the Indeed scraper for listings + salaries
- [ ] Step 3: (optional) Pull employer reviews for the top hirers
- [ ] Step 4: Aggregate into a market snapshot
- [ ] Step 5: Deliver the report for the user's lens
```

### Step 1: Collect the market brief

Ask as one block before any Actor call:

1. **Role(s)** — the job title(s) to research, e.g. `"registered nurse"`, `"data engineer"`. Accept several.
2. **Location + country** — city/state and the two-letter `country` (default `us`). Leave location empty for a country-wide view.
3. **Depth** — listings per query (`maxResultsPerQuery`, default `100`). More = better salary statistics.
4. **Filters** (optional) — `datePosted` (recency), `jobType` (full-time, contract…), surfaced as follow-ups, not in the first block.
5. **Lens** — who is asking, which shapes the report (Step 5): `recruiter` (target list of hirers), `comp/HR` (salary benchmark), `job-seeker` (offer benchmark), or `sales` (companies hiring = growth signal).
6. **Employer reputation?** — pull Glassdoor reviews for the top hirers? (`yes`/`no`, default `no` — it needs Glassdoor company URLs and adds cost).

### Step 2: Run the Indeed scraper

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Listings + **salaries + companies + role data** | `renzomacar/indeed-jobs` | community | the core market data: salary min/max, company, location, jobType, remote, companyRating |
| **Employer reputation** for named companies | `renzomacar/glassdoor-reviews` | community | optional reputation layer (needs Glassdoor company URLs) |

`Tier` = `apify` (Apify-maintained) or `community` (third-party). Both are public on the [Apify Store](https://apify.com/store).

```bash
apify actors call "renzomacar/indeed-jobs" \
  -i '{"searchQueries": ["registered nurse"], "location": "Austin, TX", "country": "us", "maxResultsPerQuery": 100, "includeDescription": true}' \
  --user-agent apify-awesome-skills/apify-job-market-intelligence \
  --json 2>/dev/null
```

Each listing returns `jobTitle`, `company`, `location`, `salary`, `salaryMin`, `salaryMax`, `salaryPeriod`, `jobType`, `isRemote`, `companyRating`, `benefits`, `datePosted`, `jobUrl`.

**MCP path equivalent:** `call-actor` with the same id + input, then `get-dataset-items`.

### Step 3: (optional) Employer reputation

If the user wants reputation on the top hirers, take the company names from Step 2, resolve their Glassdoor company URLs, and run:

```bash
apify actors call "renzomacar/glassdoor-reviews" \
  -i '{"companyUrls": ["https://www.glassdoor.com/Reviews/Google-Reviews-E9079.htm"], "maxReviewsPerCompany": 50}' \
  --user-agent apify-awesome-skills/apify-job-market-intelligence \
  --json 2>/dev/null
```

### Step 4: Aggregate into a market snapshot

From the listings, compute:

- **Salary range** — min / median / max from `salaryMin`/`salaryMax`, normalized to a common `salaryPeriod` (convert hourly↔annual before comparing; flag listings with no salary separately — don't treat missing as zero).
- **Top hirers** — companies by listing count; note their `companyRating` if present.
- **Remote share** — % of listings with `isRemote = true`.
- **Demand by location** — listing counts per location (when querying multiple cities).
- **Role-type mix** — full-time vs contract vs part-time from `jobType`.
- **Recency** — distribution by `datePosted` (is this market hot or stale?).

State your `n` (how many listings the stats are based on) and that salary stats only cover listings that disclosed pay.

### Step 5: Deliver the report for the lens

Lead with what the user's lens needs:

- **recruiter** → ranked **target list of companies hiring** for the role, with listing counts and contact-worthiness.
- **comp / HR** → **salary benchmark**: range + median by location/role, remote premium, top payers.
- **job-seeker** → "is my offer fair?" — the salary band and which employers pay above it.
- **sales** → **companies actively hiring = growth/budget signal**, ranked, as a prospect list.

End with the headline stats (median salary, top hirer, remote %, `n`) and the Apify dataset/console link for the full export.

## Responsible use

Only public job-listing and employer-review data is collected. Salary figures are listing-disclosed estimates, not guarantees — present them as ranges with the sample size, and don't present scraped pay data as an individual's actual compensation.
