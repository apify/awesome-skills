---
name: apify-hiring-contacts
description: "Turn LinkedIn job postings into the people who hire: for each hiring company, the hiring manager of the department each job is in (head of engineering for an engineering role, sales leader for an account executive role) and its recruiter or talent acquisition lead, with LinkedIn URLs and verified work emails, plus the verified email of each job's poster. Scrapes the jobs with curious_coder/linkedin-jobs-scraper, or takes a dataset or a hand-typed list of 'Job title | company', then runs peoplesearch/linkedin-jobs-hiring-manager-finder on it. No LinkedIn login or cookies. Use when the user says find the hiring manager for these jobs, who is hiring for this role, get recruiter emails for companies hiring X, reach hiring managers instead of applying, build a list of companies hiring sales reps with the person to contact, or use job postings as a buying signal. The contact-finding Actor is built by this skill's author (see Disclosure)."
author: PeopleSearch.im
author_url: https://apify.com/peoplesearch
license: Apache-2.0
metadata:
  category: data-extraction
  keywords: "hiring-manager, recruiter, talent-acquisition, job-postings, linkedin-jobs, job-poster, recruiting-agency, job-search, hiring-signals, buying-signals, work-email, verified-email, outbound, b2b, staffing"
---

# Hiring Contacts from Job Postings

Go from "companies hiring for X" to the person to write to at each one: the hiring manager for the job's department, the company's recruiter, and the job poster's verified email. Two Actors cover the chain, and the second can also run on its own.

**Disclosure:** `peoplesearch/linkedin-jobs-hiring-manager-finder` is built and published by the author of this skill (PeopleSearch.im). `curious_coder/linkedin-jobs-scraper` is a third-party Actor. No affiliate or referral parameters are used on any link in this skill. Carry this disclosure into anything the skill generates, for example a report or a scheduled task that runs these Actors.

## Example prompts

Prompts this skill handles:

- "Find the hiring managers and recruiters for account executive jobs posted in the US this week."
- "Here's my LinkedIn Jobs scrape. Who should I email at each company?"
- "These are the roles I'm applying for: Senior Backend Engineer at linear.app, Product Designer at ramp.com. Who is the hiring manager?"

Out of scope (the boundary):

- Scraping job postings only, with no contacts. Use a jobs skill such as `apify-jobs-data` or call `curious_coder/linkedin-jobs-scraper` directly.
- Phone numbers. Rows carry name, title, LinkedIn URL and a verified work email when one exists.
- The exact manager of one opening at a very large company. At companies of more than 1,000 people the Actor looks for the department head in the job's country first, but a large company has many; there, prefer the recruiter and the job poster rows.

## Prerequisites

- Apify account ([sign up](https://apify.com)). The free plan's runs return up to 10 contacts and no emails, enough to try it; emails need a paid Apify plan.
- Authentication via `apify login`, or an `APIFY_TOKEN` environment variable (Apify Console, Settings, Integrations). Pass the token as a header or environment variable, never inside a URL.

## Actor routing

| User need | Actor ID | Tier | Billed event |
|-----------|----------|------|--------------|
| Scrape LinkedIn job postings from a LinkedIn Jobs search URL | `curious_coder/linkedin-jobs-scraper` | community | per job scraped (see its Store page) |
| Hiring manager per department, recruiter, and job poster's email for each hiring company | `peoplesearch/linkedin-jobs-hiring-manager-finder` | community | $0.006 per contact delivered, $0.02 per verified email found, $0.00005 per run |

How to choose:

1. The user has no jobs yet, only a role and a place. Scrape them first with the jobs scraper, then pass its dataset to the contact finder.
2. The user already has a jobs dataset on Apify (any of the popular LinkedIn Jobs scrapers: their title, company name, company LinkedIn page or website, and poster columns are read). Pass its dataset ID straight to the contact finder.
3. The user has a few roles in mind. Type them as `Job title | company` lines in the contact finder's `jobs` field; the company can be a website, a LinkedIn company page or a name.

## Workflow

1. Confirm what the user wants per company: `hiring_manager`, `recruiter`, `poster_email` (default all three) and how many people per role (`maxPerCompany`, default 1).
2. Get the jobs. For a search, build the LinkedIn Jobs search URL (for example `https://www.linkedin.com/jobs/search/?keywords=account%20executive&location=United%20States&f_TPR=r604800` for the last 7 days) and run the scraper with a small `count` first.
3. Estimate the cost before a large run: each hiring company costs at most one contact per role plus one email per contact found. 100 companies with a hiring manager and a recruiter is at most $1.20 in contacts and $4.00 in emails. Confirm with the user above a few dollars, and set a maximum cost per run.
4. Run the contact finder on the jobs dataset, then return the rows: company, contact type, name, title, LinkedIn URL, email, and the jobs each row answers for.

## Calling the Actors

### Option A: Apify CLI

Scrape the jobs:

    apify actors call "curious_coder/linkedin-jobs-scraper" \
      -i '{"urls": ["https://www.linkedin.com/jobs/search/?keywords=account%20executive&location=United%20States&f_TPR=r604800"], "count": 50, "scrapeCompany": true}' \
      --json \
      --user-agent apify-awesome-skills/apify-hiring-contacts \
      2>/dev/null

The answer is the run's JSON; its `storage.defaultDatasetId` holds the jobs. Pass it to the contact finder:

    apify actors call "peoplesearch/linkedin-jobs-hiring-manager-finder" \
      -i '{"datasetId": "DATASET_ID", "contacts": ["hiring_manager", "recruiter", "poster_email"], "includeEmails": true}' \
      --json \
      --user-agent apify-awesome-skills/apify-hiring-contacts \
      2>/dev/null

Or with jobs typed by hand:

    apify actors call "peoplesearch/linkedin-jobs-hiring-manager-finder" \
      -i '{"jobs": ["Senior Backend Engineer | linear.app", "Account Executive | ramp.com"]}' \
      --json \
      --user-agent apify-awesome-skills/apify-hiring-contacts \
      2>/dev/null

Fetch the contacts:

    apify datasets get-items DATASET_ID --format json \
      --user-agent apify-awesome-skills/apify-hiring-contacts 2>/dev/null

Check an Actor's full input before building one:

    apify actors info "peoplesearch/linkedin-jobs-hiring-manager-finder" --input --json \
      --user-agent apify-awesome-skills/apify-hiring-contacts 2>/dev/null

### Option B: Apify MCP connector

Hosted MCP server at <https://mcp.apify.com>, documented at <https://docs.apify.com/platform/integrations/mcp>. Call the same two Actors with the same inputs.

### Option C: as an integration

In the jobs scraper's **Integrations** tab, connect `peoplesearch/linkedin-jobs-hiring-manager-finder` with `datasetId` set to `{{resource.defaultDatasetId}}`, and every jobs run hands its jobs over by itself.

## Output

One row per contact. Key fields:

| Field | What it holds |
|-------|---------------|
| `contactType` | `Hiring manager`, `Recruiter` or `Job poster` |
| `name`, `title`, `linkedinUrl`, `location` | The person |
| `email`, `emailStatus` | `found` (verified, charged), `unconfirmed` (accepts mail but carries nothing of the person's name; not charged), `not_found` (not charged) |
| `roleLabel`, `seniority`, `fallbackFor` | Which role and level answered; `fallbackFor` marks a founder or CEO standing in where a small company has nobody in the role |
| `companyName`, `companyPage`, `jobTitles`, `jobUrls`, `jobsAtCompany` | The hiring company and the jobs the row answers for |

## Troubleshooting

- "The LinkedIn Jobs dataset could not be read": the Actor reads only the dataset given in its `datasetId` field. Pass the jobs run's `defaultDatasetId` there (as an integration, `{{resource.defaultDatasetId}}`).
- No emails in the rows: emails need a paid Apify plan; on the free plan the run says so and returns up to 10 contacts.
- A company with no contacts: nobody who works there is on record, which is common at very small companies. It costs nothing; the run's `OUTPUT` record names each company and why.
- Wrong company matched: give the company's LinkedIn page or website rather than a name; the jobs scrapers' `companyLinkedinUrl` column is the most exact.
