---
name: apify-ats-jobs-hiring-signals
description: "Pull every open job of a list of companies straight from their public ATS boards (Greenhouse, Lever, Ashby, Workday, SAP SuccessFactors, iCIMS, Oracle Recruiting Cloud, Eightfold, Phenom, Recruitee, Personio, Teamtailor, BambooHR and more) with the cleanyield/ats-jobs-scraper Actor, and turn them into hiring signals. Takes company names, websites or board URLs; returns one row per job with title, department, location, isRemote/workplaceType, postedAt, applyUrl, salary fields only when the posting publishes one, seniority, plus per-company companyOpenJobs, companyJobsPostedLast30Days and companyTrend. Use when the user asks for open jobs at specific companies, which companies are hiring for a role, hiring signals for outbound, a weekly new-jobs watch (monitor mode), job-board pipelines across several ATS, or salary ranges where companies publish them. Billed per delivered job; companies not found and jobs filtered out are free."
metadata:
  category: data-extraction
  keywords: "ats jobs, greenhouse jobs, lever jobs, ashby jobs, workday jobs, successfactors jobs, icims jobs, job postings api, hiring signals, open jobs by company, recruiting data, job monitor"
---

# ATS Jobs and Hiring Signals

Get every open job of the companies the user names, read live from their public applicant tracking system (ATS) boards, and summarize who is hiring, for what and how fast.

Author: [Clean Yield](https://apify.com/cleanyield). Disclosure: the routed Actor `cleanyield/ats-jobs-scraper` is built and maintained by the author of this skill and is a paid Actor (pay per delivered job). No affiliate or referral parameters are used.

## Example prompts

Prompts this skill handles:

- "List all open engineering jobs at Stripe, Ramp and Notion, remote or in the US."
- "Which of these 40 SaaS companies posted sales jobs in the last 14 days? Give me a table with the count per company."
- "Every Monday, tell me the new product-manager jobs at these 25 companies."

Out of scope (the boundary):

- "Search LinkedIn or Indeed for data analyst jobs in Berlin." This skill reads company ATS boards, not job aggregators; use an aggregator scraper from the Apify Store instead.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. **Collect the companies.** Accept company names (`Stripe`), websites (`figma.com`, the Actor follows the Careers link) or board URLs (`https://jobs.ashbyhq.com/ramp`). One company per array item.
2. **Fetch the live input schema** instead of guessing field names:

       apify actors info "cleanyield/ats-jobs-scraper" --input --json \
         --user-agent apify-awesome-skills/apify-ats-jobs-hiring-signals 2>/dev/null

3. **Build the input.** Main fields: `companies` (array), `keywords` (array, matched in the title by default), `locations` (array: city, US state code, country or `remote`), `postedWithinDays` (integer, 0 = any), `maxJobsPerCompany` (integer, 0 = all). Set `onlyWithSalary` to `false` unless the user only wants jobs that publish pay: many postings do not publish a salary, and the Console prefill turns this filter on.
4. **Estimate cost before big runs.** Cost scales with delivered jobs. Large employers can have 800+ open jobs, so set `maxJobsPerCompany` (for example 50) or `postedWithinDays` when the user wants a sample or a signal, not the full list. Check the current price per 1,000 jobs on the [Actor page](https://apify.com/cleanyield/ats-jobs-scraper) and confirm with the user when the estimate is significant.
5. **Run it:**

       apify actors call "cleanyield/ats-jobs-scraper" \
         -i '{"companies":["stripe","ramp.com","https://jobs.ashbyhq.com/notion"],"keywords":["engineer"],"locations":["United States","remote"],"onlyWithSalary":false,"maxJobsPerCompany":50}' \
         --json --user-agent apify-awesome-skills/apify-ats-jobs-hiring-signals 2>/dev/null

6. **Fetch and summarize results:**

       apify datasets get-items DATASET_ID --format json \
         --user-agent apify-awesome-skills/apify-ats-jobs-hiring-signals 2>/dev/null

   Useful output fields: `company`, `ats`, `title`, `department`, `location`, `countryCode`, `isRemote`, `workplaceType`, `postedAt`, `applyUrl`, `seniority`, `salaryAnnualMinUsd` / `salaryAnnualMaxUsd` (empty when the posting has no salary), `companyOpenJobs`, `companyJobsPostedLast30Days`, `companyTrend`. Group by `company` for hiring-signal tables; report how many companies returned no board.

7. **Recurring watch (optional).** For "tell me what is new every week", set `monitorMode: true` and a `monitorStateName`, then schedule the run in Apify Console. Later runs output only jobs with `changeType` `new` or `changed`. Billing in this mode: only new or changed jobs plus a small fee per company checked.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Open jobs of named companies across many ATS, hiring signals, weekly new-jobs watch | `cleanyield/ats-jobs-scraper` | community | Company-first job data straight from the employer's ATS board |
| Emails, phones, socials and tech stack of the hiring companies (next step for outbound) | `cleanyield/company-enrichment-from-website` | community | One row per company website |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling Actors via MCP instead of the CLI

The same Actors work through the [Apify MCP connector](https://mcp.apify.com) (`https://mcp.apify.com/?tools=cleanyield/ats-jobs-scraper`), documented at <https://docs.apify.com/platform/integrations/mcp>.

## Troubleshooting

- **A company returns 0 jobs:** check the COMPANIES record in the run's key-value store. "Not found" means the company uses an ATS that is not covered yet or blocks robots; pass the board URL directly if you have it. Not-found companies are not charged.
- **Far fewer jobs than expected:** `onlyWithSalary` is on (drops jobs without published pay), or `keywords`/`locations` are too narrow. Rerun with `onlyWithSalary: false` and fewer filters.
- **Wrong company with a common name** (for example "monday"): pass the website (`monday.com`) or the board URL instead of the bare name.
- **Run stops early:** the user's maximum charge per run was reached; the run ends cleanly and keeps the jobs delivered so far.
