---
name: apify-google-jobs-feed
description: "Pull job postings from Google Jobs (the jobs panel in Google Search) as flat, structured rows with the Google Jobs Scraper Actor (redomic/google-jobs): title, company, location, posting date and age, salary range parsed into min/max/period, job type, benefits, full description, and every apply link (Indeed, LinkedIn, company careers sites and more) in one row per job. Takes a plain search query plus optional location, country edition, date-posted window and job type. Use when the user asks to scrape Google Jobs, search jobs across job boards at once, collect job postings with salaries, build a jobs feed or hiring-signal list for a role and city, track new postings since yesterday, compare salaries for a role across cities or countries, or export job listings to CSV/JSON. Billed per job row delivered; status and empty rows are never charged."
metadata:
  category: data-extraction
  keywords: "google jobs, google jobs api, job postings, job scraper, jobs feed, salary data, hiring signals, job board aggregator, recruiting data, labor market"
author: Redomic
author_url: https://apify.com/redomic
---

# Google Jobs feed

Turn a job search ("data engineer", "Berlin") into structured job rows from Google Jobs, which aggregates postings from Indeed, LinkedIn, Glassdoor, ZipRecruiter, company career sites and many smaller boards.

Disclosure: the routed Actor, `redomic/google-jobs`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get the 50 newest software engineer jobs in New York with salaries"
- "Which companies posted data analyst roles in London since yesterday? Give me a CSV"
- "Compare nurse salaries in Toronto and Vancouver from current job postings"

Out of scope (the boundary):

- "Scrape LinkedIn profiles of the recruiters" — no personal profiles or contact data; recruiter names are off by default.
- EU/EEA job searches: Google has turned the jobs panel off there, so the Actor cannot return EU results. Use a board-specific Actor instead.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via `apify login`, or the `APIFY_TOKEN` environment variable, or a token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. Turn the request into one query per role (`query`), plus `location` (city, region or `remote`) and `country` (two-letter Google edition, default `US`). Use `datePosted` for "new since" requests and `jobType` for full-time/part-time/contract.
2. Set `maxJobs` to what the user needs (default 50, maximum 200). Cost is per job row, so `maxJobs` is also the spending cap.
3. Run the Actor (command below) and read the dataset. Rows with a `_status` field are per-query status rows (`ok`, `partial`, `empty` with a reason), not jobs.
4. Deliver: number of jobs, a short table (title, company, location, salary, posted), and the dataset link or a CSV export.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Job postings across boards for a role and place | `redomic/google-jobs` | community | Many boards in one search, parsed salary, apply links |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/google-jobs" \
      -i '{"query": "data engineer", "location": "Austin", "country": "US", "datePosted": "week", "maxJobs": 50}' \
      --json \
      --user-agent apify-awesome-skills/apify-google-jobs-feed \
      2>/dev/null

Fetch the current input schema before building unusual inputs:

    apify actors info "redomic/google-jobs" --input --json \
      --user-agent apify-awesome-skills/apify-google-jobs-feed 2>/dev/null

Read results:

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-google-jobs-feed 2>/dev/null

## Output fields (one row per job)

`jobId`, `title`, `company`, `location`, `via` (board that published it), `postedAt` (ISO date), `ageDays`, `postedText`, `salaryText`, `salaryMin`, `salaryMax`, `salaryCurrency`, `salaryPeriod` (`year`, `month`, `hour`...), `jobType`, `qualification`, `benefits`, `description` (full text), `highlights`, `applyLinks` (every source with its URL), `sourceSites`, `googleUrl`, `query`, `searchLocation`, `country`, `scrapedAt`.

See [references/gotchas.md](references/gotchas.md) for cost guardrails and known limits.
