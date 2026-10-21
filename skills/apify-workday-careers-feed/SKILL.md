---
name: apify-workday-careers-feed
description: "Pull live open jobs from companies' own careers pages, including Workday sites (myworkdayjobs.com, myworkdaysite.com), and keep a daily feed of only new postings. Takes company names, websites or careers URLs, finds the right Workday site or Greenhouse, Lever, Ashby, Workable, SmartRecruiters or Recruitee board, and returns one row per job with title, department, locations, remote flag, posting date, apply link, salary when the description states one, seniority (intern, entry and up) and the full description. Routes Workday companies to heyitsgautham/workday-jobs-scraper and the rest to heyitsgautham/career-site-jobs-scraper, whose rows share one field set. Use when the user asks for jobs at named employers, a company's Workday careers page, internships or new grad roles at large companies, jobs with a stated salary, or a daily alert of new roles at a watch list of companies. Pay per job, no start fee, and companies with no jobs cost nothing."
author: Gautham Krishna (heyitsgautham)
author_url: https://github.com/heyitsgautham
metadata:
  category: data-extraction
  keywords: "workday, workday-jobs, myworkdayjobs, careers-page, company-jobs, greenhouse, lever, ashby, workable, internships, new-grad, salary, job-alerts, ats, recruiting, apify"
---

# Jobs from company careers pages, Workday included

Disclosure: the author of this skill built and owns both Actors it routes to (`heyitsgautham/workday-jobs-scraper` and `heyitsgautham/career-site-jobs-scraper`).
They are pay-per-result Actors on Apify Store.
No referral or tracking parameters are used in this skill.

Most large employers post jobs on Workday, and each company's Workday site is its own tenant, so a user cannot search them all at once.
This skill turns a list of employers into one table of their open jobs, picks the right Actor per company, and sets up a daily feed of new postings.

## Example prompts

Prompts this skill handles:

- "Get every open software engineering job at NVIDIA, Salesforce and Boeing, with salary where they list it."
- "Find internships and new grad roles posted in the last 30 days at these 20 companies." (a pasted list of names or websites)
- "Watch Stripe, Snap and Nike's careers pages and tell me only about new roles each morning."

Out of scope (the boundary):

- "Search all jobs on LinkedIn or Indeed for 'data analyst in Berlin'." That is a job-board search across employers, not a careers-page read. Use the `apify-job-boards` skill.
- Recruiter or hiring-manager contact details. Neither Actor has contact fields.

## Prerequisites

- Apify account ([sign up](https://apify.com)).
- Authentication through `apify login`, or an `APIFY_TOKEN` environment variable (Apify Console, Settings, Integrations).

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Companies on Workday, or any `myworkdayjobs.com` / `myworkdaysite.com` link | `heyitsgautham/workday-jobs-scraper` | community | Large employers. Finds the Workday site from a company name or website |
| Companies on Greenhouse, Lever, Ashby, Workable, SmartRecruiters or Recruitee | `heyitsgautham/career-site-jobs-scraper` | community | Startups and mid-size companies. Finds the board from a name or website |
| Not sure which system a company uses | Start with `heyitsgautham/career-site-jobs-scraper` | community | It answers with a free `unsupported_ats` row naming `workday` and the Workday link when the company uses Workday. Send that link to the Workday Actor |

Both Actors return the same fields per job, so their rows go in one table.
The Workday Actor adds `requisitionId`.

## Workflow

1. Collect the companies as names (`Boeing`), websites (`crowdstrike.com`) or careers URLs.
   Ask for filters the user cares about: keywords, locations, remote only, posted within N days, seniority, minimum salary.
2. If the user names companies you know are on Workday, or gives Workday links, call the Workday Actor with them.
   Otherwise call the career-site Actor first.
3. Read the rows by `status`.
   `ok` rows are jobs.
   On career-site output, an `unsupported_ats` row with `ats: "workday"` has a `boardUrl`.
   Pass every such `boardUrl` to the Workday Actor in one second call.
   `ats_not_detected` and `not_found` rows mean the company was not found on that system, and they cost nothing.
4. Merge the `ok` rows from both calls into one table, deduplicated on `url`.
   Report how many companies returned jobs, how many had none (`no_jobs`) and which were not found.
5. For a feed, run the same input with `onlyNewSinceLastRun: true` on a daily Apify schedule (Console, Schedules, or the [schedules API](https://docs.apify.com/api/v2/schedules)).
   The first run returns everything and remembers it.
   Later runs return only jobs not returned before for the same site and filters, and a site with nothing new is a free `no_jobs` row.

## Run it with the Apify CLI

Check the live input schema and price before a big batch:

```bash
apify actors info "heyitsgautham/workday-jobs-scraper" --input --json \
  --user-agent apify-awesome-skills/apify-workday-careers-feed \
  2>/dev/null
```

Engineering jobs in the US at three Workday employers, from names, URLs and a website:

```bash
apify actors call "heyitsgautham/workday-jobs-scraper" -i '{"companies":["https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite","Boeing","crowdstrike.com"],"keywords":["engineer"],"locations":["US"],"maxJobsPerCompany":200}' \
  --json \
  --user-agent apify-awesome-skills/apify-workday-careers-feed \
  2>/dev/null
```

Internships and entry-level roles posted in the last 30 days:

```bash
apify actors call "heyitsgautham/workday-jobs-scraper" -i '{"companies":["Boeing","Salesforce","Capital One"],"seniority":["intern","entry"],"postedWithinDays":30,"keywords":["software","data"]}' \
  --json \
  --user-agent apify-awesome-skills/apify-workday-careers-feed \
  2>/dev/null
```

Jobs whose description states at least $150,000 a year:

```bash
apify actors call "heyitsgautham/workday-jobs-scraper" -i '{"companies":["nvidia.wd5.myworkdayjobs.com"],"minSalary":150000,"salaryCurrency":"USD","salaryPeriod":"YEAR"}' \
  --json \
  --user-agent apify-awesome-skills/apify-workday-careers-feed \
  2>/dev/null
```

Startups on other systems, from websites and names:

```bash
apify actors call "heyitsgautham/career-site-jobs-scraper" -i '{"companies":["stripe.com","Scale AI","https://jobs.lever.co/outreach"],"remoteOnly":true}' \
  --json \
  --user-agent apify-awesome-skills/apify-workday-careers-feed \
  2>/dev/null
```

The daily feed shape, to save as a task and schedule:

```bash
apify actors call "heyitsgautham/workday-jobs-scraper" -i '{"companies":["Snap","Nike","Boeing"],"onlyNewSinceLastRun":true}' \
  --json \
  --user-agent apify-awesome-skills/apify-workday-careers-feed \
  2>/dev/null
```

Read the rows back from a finished run:

```bash
apify datasets get-items <DATASET_ID> --format json \
  --user-agent apify-awesome-skills/apify-workday-careers-feed \
  2>/dev/null
```

## What you get per job

`status`, `company`, `ats`, `title`, `department`, `location`, `locations`, `country`, `isRemote`, `workplaceType`, `employmentType`, `postedAt`, `url`, `applyUrl`, `salary` (`{min, max, currency, period, text}` or empty), `seniority`, `descriptionText`, `descriptionHtml`.
The Workday Actor adds `jobId` and `requisitionId`.
Resolved inputs also carry `boardUrl`, `resolvedBy` and `resolvedFrom`, so the user can see which site was used.

## Cost

| Actor | Price per 1,000 jobs | Lowest tier (Gold) | Always free |
|---|---|---|---|
| `heyitsgautham/workday-jobs-scraper` | $1.00 | $0.70 | Sites not found, empty or failed, jobs your filters drop, and the name or website lookup |
| `heyitsgautham/career-site-jobs-scraper` | $1.50 | $0.90 | Boards not found, empty or failed, jobs your filters drop, and the lookup |

Check live prices with `apify actors info` before quoting them.

Cost traps:

- A large employer can list tens of thousands of jobs. Set `maxJobsPerCompany` or `keywords` when the user wants a sample, and tell them the cap.
- A seniority or salary filter on a very large Workday site reads most job pages, so it is slow. Add `keywords` first.

## Troubleshooting

- `ats_not_detected` on the Workday Actor: the company may not use Workday. Try the career-site Actor, or ask the user for the careers URL.
- `unsupported_ats` on the career-site Actor with `ats: "workday"`: send its `boardUrl` to the Workday Actor.
- Fewer jobs than the careers page shows: a few very large Workday sites serve at most 2,000 jobs per query with no filter that splits them further. The run note and the summary row (`boardSummary: true`) say when a site was read only in part.
- `salary` is empty: Workday has no pay field, so pay comes from the description. Many non-US jobs state none.
- Seniority is empty when the title and description give no clear level, which was 22% of 41,383 Workday jobs in the author's test run. `keepJobsWithoutSeniority: true` keeps those jobs in a filtered run.
