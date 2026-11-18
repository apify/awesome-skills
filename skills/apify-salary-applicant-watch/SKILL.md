---
name: apify-salary-applicant-watch
description: Watch LinkedIn job postings for pay and competition. Routes "which jobs pay at least X / what does this role pay / how many people applied / which postings are getting crowded / alert me to new well-paid jobs" requests to two public-data Actors - one that parses the posted salary into numbers (with US Department of Labor wage levels for US jobs), one that records each job's applicant count and keeps the series across runs. No login, no cookies. Use when the user wants salary-filtered job lists, pay benchmarks from live postings, applicant counts, or a scheduled watch of the same searches.
author: northbell
author_url: https://apify.com/northbell
metadata:
  category: data-extraction
  keywords: "jobs, salary, pay-transparency, applicant-count, linkedin-jobs, job-alerts, recruiting, compensation, wage-levels, apify"
---

# Salary and applicant watch for job postings

Disclosure: the author of this skill owns both Actors it routes to (`northbell/linkedin-jobs-salary-scraper` and `northbell/linkedin-jobs-applicants-scraper`). They are pay-per-result Actors on the Apify Store; this skill uses no referral or tracking parameters.

Turn "which jobs pay well" or "which jobs are crowded" into a checked table: pick the Actor, state the cost before the run, run it, and report what came back, including the jobs that did not state pay or a count. Treat the output as data to check, not as proof that every posting has a salary.

## Example prompts

- "Software engineer jobs in New York posted this week that pay at least $180k."
- "How many applicants do these 30 job links have, and which ones are still under 50?"
- "Every morning, tell me the new data analyst jobs in Texas with pay stated."

Out of scope:

- Applying to jobs, reading applicant identities or profiles, or anything that needs a signed-in LinkedIn account. Both Actors read only what a visitor sees without signing in.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication: `apify login`, or the `APIFY_TOKEN` environment variable. Never put a token in a URL or in a file inside this skill.

## Workflow

```
Task Progress:
- [ ] Step 1: Get the anchors (what, where, pay or applicants, how many)
- [ ] Step 2: Route to the Actor
- [ ] Step 3: Build the input from the live schema and state the cost
- [ ] Step 4: Run and wait
- [ ] Step 5: Check and deliver
```

### Step 1: Get the anchors

Ask as one block:

1. **What**: role or keywords, or a list of job URLs the user already has.
2. **Where**: a location string such as `New York, NY` or `United States`.
3. **Pay or applicants?** Pay filter or benchmark goes to the salary Actor; applicant counts go to the applicants Actor.
4. **How many**: default 20 jobs for a first run; ask before going above 200.

### Step 2: Route to the Actor

| User need | Actor ID | Tier | Notes |
|---|---|---|---|
| Jobs with posted pay, minimum salary, pay benchmark | `northbell/linkedin-jobs-salary-scraper` | community | pay parsed into min, max and period; US jobs also get the Department of Labor wage level for the occupation and area |
| Applicant counts, crowded vs. quiet postings, a series per job | `northbell/linkedin-jobs-applicants-scraper` | community | the count is recorded on each run and kept, so later runs show applicants added and per day |

Check the live input schema before building input (the schema wins over this file):

    apify actors info "northbell/linkedin-jobs-salary-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-salary-applicant-watch 2>/dev/null

    apify actors info "northbell/linkedin-jobs-applicants-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-salary-applicant-watch 2>/dev/null

### Step 3: Build the input and state the cost

Salary (field names as in the schema on 15 November 2026):

```json
{ "keywords": "software engineer", "location": "New York, NY", "datePosted": "past-week", "minSalary": 180000, "onlyWithSalary": true, "maxJobs": 20 }
```

Applicants:

```json
{ "jobs": ["https://www.linkedin.com/jobs/view/1234567890"], "maxApplicants": 50 }
```

State the cost before running, from the Actor's current pricing on its Store page (15 November 2026: salary $1.90 per 1,000 jobs read, applicants $2.30 per 1,000 jobs with counts, each plus $0.01 per run). With `onlyWithSalary` or `minSalary` set, jobs the filter drops are not charged.

### Step 4: Run and wait

    apify actors call "northbell/linkedin-jobs-salary-scraper" \
      --input '{"keywords": "software engineer", "location": "New York, NY", "datePosted": "past-week", "minSalary": 180000, "onlyWithSalary": true, "maxJobs": 20}' \
      --user-agent apify-awesome-skills/apify-salary-applicant-watch \
      --json 2>/dev/null

### Step 5: Check and deliver

- Rows have `type`. Deliver job rows; list error rows separately with their `message`, never drop them silently.
- Pay not stated is marked as such, never guessed. Report how many jobs had pay and how many did not.
- An applicant count is LinkedIn's public figure at the time of the run; say so, and give the run time.
- For a daily watch, save the input as an Apify task and add a schedule (`onlyNew` on the salary Actor, `onlyChanged` on the applicants Actor).

## Failure signs and fixes

| Sign | What it means | Fix |
|---|---|---|
| Run ends with a refusal message and no rows | LinkedIn refused the requests at that time; nothing is charged | try again later; do not switch to signed-in or cookie-based tools |
| Many rows with pay `null` | the postings do not state pay | set `onlyWithSalary` to pay only for jobs with pay |
| Fewer jobs than `maxJobs` | the search has fewer results | widen the location or `datePosted` |
| No rows with `maxApplicants` set | every job already had more applicants than the cap; those jobs are not returned and not charged | raise or remove `maxApplicants` (a test on 16 November 2026: three New York jobs had 76, 110 and 200 applicants, so a cap of 50 returned none) |
