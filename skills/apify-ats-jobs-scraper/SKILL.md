---
name: apify-ats-jobs-scraper
description: Get open jobs from named companies' own career sites on Greenhouse, Lever, Ashby, Workday, SmartRecruiters, Workable, Personio and Recruitee, as one normalised record per job (country, remote, salary when posted). Use when the user says "get all open jobs at <company>", "which of these companies are hiring <role>", "jobs posted this week at my target accounts", "new jobs at these companies since last run", "Personio jobs", "export a Greenhouse/Lever/Ashby/Workday board".
author: career-site-jobs author (7bshiup)
author_url: https://github.com/7bshiup
metadata:
  category: data-extraction
  keywords: "greenhouse jobs, lever jobs, ashby jobs, workday jobs, smartrecruiters jobs, workable jobs, personio jobs, recruitee jobs, ats scraper, hiring signals, job postings, career site"
---

# ATS Jobs Scraper (Greenhouse, Lever, Ashby, Workday and more)

Reads the current open jobs of named companies from their own career-site feeds and returns one clean record per job.

Disclosure: routes to `improved_gravity_qb7/greenhouse-lever-ashby-personio-jobs-scraper`, a paid Actor built by the author of this skill.

## Example prompts

Prompts this skill handles:

- "Which of Stripe, Ramp and Linear posted engineering jobs in the last 14 days?"
- "Export all open roles at tado and bunq to CSV."
- "Tell me only the new jobs at these 20 companies since my last run."

Out of scope (the boundary):

- "Find every data engineer job in Berlin": no company list, so this skill does not apply (use a job-search Actor).
- LinkedIn or Indeed data, and historical postings: not covered.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via `apify login` or the `APIFY_TOKEN` environment variable

## Workflow

1. Turn each company into a board: a career-page URL, or `system:board` (for example `greenhouse:stripe`, `lever:spotify`, `ashby:ramp`, `workday:nvidia/wd5/NVIDIAExternalCareerSite`). A bare name is tried on the other systems and is slower.
2. Check the live input schema:
   `apify actors info "improved_gravity_qb7/greenhouse-lever-ashby-personio-jobs-scraper" --input --user-agent apify-awesome-skills/apify-ats-jobs-scraper 2>/dev/null`
3. Run with a cap, confirming cost with the user when it may be large:
   `apify actors call improved_gravity_qb7/greenhouse-lever-ashby-personio-jobs-scraper --input '{"companies":["greenhouse:stripe","https://jobs.lever.co/spotify"],"postedWithinDays":7,"maxJobs":200}' --user-agent apify-awesome-skills/apify-ats-jobs-scraper --json 2>/dev/null`
4. Read the items from the run's default dataset. Read `RUN_SUMMARY` from its key-value store to tell the user which boards were missing, throttled or failed.

For scheduled monitoring, save the call as an Apify task with `"newJobsOnly": true`: each run then returns, and charges, only jobs not returned before.

## Output fields

id, system, board, company, title, location, country, countries[], remote, department, employment_type, posted_at, url, description, salary_min, salary_max, salary_currency, salary_period, fetched_at.

## Cost and traps

From $0.0015 to $0.003 per job returned depending on the Apify plan; jobs removed by filters and failed boards are free. Always set `maxJobs`: a large employer board can hold thousands of jobs. Use `includeDescription:false` for smaller records (SmartRecruiters and Workday need one extra request per job for descriptions and pay).

## Failure modes

- Board `missing` in RUN_SUMMARY: wrong slug; open the company's careers page and copy the URL.
- Board `throttled`: the site refused requests (Workable, Recruitee); rerun later.
- Board `failed`: timed out; rerun later.
- The `country` filter drops jobs whose location names no country ("Europe").
