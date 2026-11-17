---
name: apify-company-job-openings
description: "Get the current open jobs for a list of companies, read live from each company's own hiring system (Greenhouse, Lever, Ashby, Workday, SmartRecruiters, Workable, Recruitee, Personio), with the Apify Actor extractlyspace/company-jobs-scraper. Takes website domains, careers page URLs, job board URLs or company names, so you do not need to know which system a company uses. Returns one row per job: company, title, department, location, country, remote flag, employment type, posting date, apply URL, salary when published, and the description on request. Use for: what is this company hiring for, open roles at a list of target accounts, hiring signals for sales prospecting, which of these companies are hiring engineers, new jobs since the last check, careers page jobs as JSON, monitoring competitors' job openings. Not for searching job boards such as LinkedIn or Indeed by keyword. Pay per job returned, no start fee."
author: extractlyspace
author_url: https://apify.com/extractlyspace
license: MIT
metadata:
  version: "1.0"
  category: data-extraction
  keywords: "jobs, job-openings, careers-page, hiring-signals, ats, greenhouse, lever, ashby, workday, company-jobs, sales-prospecting"
---

# Open jobs for a list of companies

Give a list of companies; get their open jobs as rows, read live from the hiring system each company uses.

Disclosure: this skill routes to a paid Actor built by the author (extractlyspace).

## Example prompts

Prompts this skill handles:

- "Which engineering jobs are open at stripe.com, figma.com and notion.com right now?"
- "Here are 30 target accounts. Which of them posted sales roles in the last 14 days?"
- "Check these ten competitors every morning and tell me only the jobs that are new."

Out of scope (the boundary):

- "Find remote Python jobs anywhere." That is a search across job boards, not a list of companies. Use a job-board skill such as `apify-job-boards` or `apify-jobs-data`.
- Recruiter, hiring-manager or applicant data. The Actor never returns people.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable

## Workflow

1. Collect the companies. Prefer website domains (`stripe.com`) or job board URLs. A plain name works when exactly one board carries it; see [references/gotchas.md](references/gotchas.md).
2. Fetch the input schema once and build the input from it. Do not guess field names.
3. Estimate the cost before a large run: at most `companies x maxJobsPerCompany x $0.0015`. Ask the user before a run that can exceed about $1.
4. Run the Actor, then read the dataset.
5. Separate the rows by `recordType`: `job` rows are the result; `status` rows explain what could not be returned and are free. Tell the user about every `status` row that is not `no_results`.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Open jobs for named companies, any of eight hiring systems | `extractlyspace/company-jobs-scraper` | community | Lists of 1 to 100 companies given as domains, URLs or names |

## Run it with the Apify CLI

Fetch the input schema:

```bash
apify actors info "extractlyspace/company-jobs-scraper" --input --json \
  --user-agent apify-awesome-skills/apify-company-job-openings \
  2>/dev/null
```

Engineering jobs at three companies, at most 20 each:

```bash
apify actors call "extractlyspace/company-jobs-scraper" \
  -i '{"companies":["stripe.com","figma.com","notion.com"],"keywords":["engineer"],"maxJobsPerCompany":20}' \
  --json \
  --user-agent apify-awesome-skills/apify-company-job-openings \
  2>/dev/null
```

Sales roles posted in the last 14 days, the shape for a hiring-signal check:

```bash
apify actors call "extractlyspace/company-jobs-scraper" \
  -i '{"companies":["ramp.com","https://jobs.lever.co/spotify"],"keywords":["sales","account executive"],"postedWithinDays":14,"maxJobsPerCompany":10}' \
  --json \
  --user-agent apify-awesome-skills/apify-company-job-openings \
  2>/dev/null
```

Only jobs not returned before, the shape for a daily schedule:

```bash
apify actors call "extractlyspace/company-jobs-scraper" \
  -i '{"companies":["stripe.com","figma.com"],"onlyNew":true,"maxJobsPerCompany":50}' \
  --json \
  --user-agent apify-awesome-skills/apify-company-job-openings \
  2>/dev/null
```

The call prints the run as JSON. Read the rows from its `defaultDatasetId`:

```bash
apify datasets get-items <DATASET_ID> --format json \
  --user-agent apify-awesome-skills/apify-company-job-openings \
  2>/dev/null
```

## What you get

One row per job, always with the same fields:

- `recordType` (`job`), `company`, `companyDomain`, `title`, `department`, `location`, `country`, `isRemote`, `employmentType`
- `postedAt`, `applyUrl`, `jobId`, `source` (the hiring system, or `jsonld` for a company's own website), `scrapedAt`
- `salaryMin`, `salaryMax`, `salaryCurrency`, `salaryPeriod` (only when the company publishes pay)
- `description` (plain text, only with `includeDescription`)

A value the hiring system does not provide is `null`. Which system provides which field is listed in [references/gotchas.md](references/gotchas.md).

Rows with `recordType: "status"` carry `status`, `message` and `subject` (the company the row is about). The `status` is one of `no_results`, `not_found`, `unsupported`, `partial`, `invalid_input`, `limit_reached`.

## Cost

- $0.0015 for each job returned. `status` rows are free. No start fee.
- $0.001 more for each job that has a description, only with `includeDescription`.
- Filters (`keywords`, `locations`, `remoteOnly`, `postedWithinDays`) apply before `maxJobsPerCompany`, so a filtered run pays only for matching jobs.
- The default `maxJobsPerCompany` is 50. Set it lower for a first look.

## Troubleshooting

- A `not_found` row for a domain: the company's site does not link a supported job board. Send the job board URL itself, for example `https://boards.greenhouse.io/acme`.
- A `not_found` row that lists several boards: a plain name matched more than one company. Send one of the listed URLs.
- Workday is not found from a name. Send the Workday job board URL or the company's domain.
- A `partial` row: a board stopped answering or ran out of time. The jobs read so far are in the dataset; run the same company again later.
- The run fails only when nothing could be read at all. Retry once; if it fails again, report the run ID to the Actor's issue page on Apify.
- More in [references/gotchas.md](references/gotchas.md).
