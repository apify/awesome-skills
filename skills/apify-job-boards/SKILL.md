---
name: apify-job-boards
description: Pull job postings from many boards in one run and prepare one validated, deduplicated table. Routes "find jobs / scrape job postings / build a job list / monitor new jobs / track a company's careers page / scrape LinkedIn jobs" requests to a multi-board job scraper (LinkedIn, Indeed, Glassdoor, The Muse plus keyless boards), a remote-only aggregator (RemoteOK, We Work Remotely, Remotive, Jobicy, Himalayas, HN Who is hiring) or a LinkedIn-only scraper (several titles and up to 25 places per run, or pasted LinkedIn job-search URLs), with output-locality checks, per-board raw/qualified/deduplicated counts, only-new-jobs monitoring, per-board caps and honest cost estimates. Use when the user asks to scrape jobs across job boards, get Indeed or Glassdoor postings without an API key, scrape LinkedIn jobs only or from a pasted LinkedIn search URL, collect remote developer jobs, watch a company's Greenhouse/Lever/Ashby careers page, or set up a daily new-jobs alert.
author: Zakariae (Flash Scrape) — routes to Actors built by the author; no affiliate or referral parameters
author_url: https://github.com/ZAKRIAZ
metadata:
  category: data-extraction
  keywords: "jobs, job-postings, job-boards, indeed, glassdoor, linkedin-jobs, remote-jobs, job-aggregator, job-alerts, careers-page, greenhouse, lever, ashby, recruiting, salary-data, apify"
---

# Job boards to one table

Disclosure: the author of this skill owns all three Actors it routes to (`flash_scraper/multi-jobboard-scraper`, `flash_scraper/remote-job-aggregator` and `flash_scraper/linkedin-jobs-scraper`). They are pay-per-result Actors on the Apify Store; no referral or tracking parameters are used anywhere in this skill.

Turn "I need job postings" into one validated, deduplicated dataset by routing the request to the right Actor, sizing the run so the user knows the cost before it starts, checking the returned locations and vacancy identities, and returning the rows with the board each job was found on. Treat the Actor output as raw input to these checks, not as proof that its location filtering or deduplication succeeded.

## Example prompts

Prompts this skill handles:

- "Scrape software engineer jobs in Austin from LinkedIn, Indeed and Glassdoor into one spreadsheet, no duplicates."
- "Scrape LinkedIn only for 'product manager' and 'backend engineer' postings in London, mid-senior level, into a CSV."
- "Here is my LinkedIn job search, put those jobs in a CSV: https://www.linkedin.com/jobs/search/?keywords=data%20analyst&geoId=103644278&f_TPR=r86400"
- "Watch Stripe's and OpenAI's careers pages and only tell me about new roles."

For the Austin request, try all three requested boards, then validate each returned location and vacancy identity before delivery. If Glassdoor returns only wrong-city or unverifiable rows, deliver the qualified LinkedIn and Indeed rows as a partial result and report Glassdoor's raw, qualified and deduplicated counts as a board failure. Do not claim three-board coverage merely because Glassdoor returned rows.

For the London request, run the LinkedIn-only scraper with the LinkedIn input from Step 3: both titles in one run, and `"experienceLevel": ["4"]` (Mid-Senior level) checked on each job page.

For the pasted search, run the LinkedIn-only scraper with the URL in `searchUrls` (Step 3): its keywords, place and past-24-hours filter are kept, and the run names any URL filter it could not use.

For the Stripe and OpenAI watch, run the company-watch input from Step 4 and schedule the same input daily: `"sites": []` keeps the run to the two companies' own boards (Stripe answers on Greenhouse, OpenAI on Ashby; checked 2026-10-28), the first run is the baseline, and later runs deliver only postings not delivered before.

Out of scope (the boundary):

- "Apply to these jobs for me" or anything that needs a logged-in account, CAPTCHA solving, or personal data of applicants. This skill only reads public postings; for candidate profiles send the user to the LinkedIn workflows in [apify/agent-skills ultimate-scraper](https://github.com/apify/agent-skills/blob/main/skills/apify-ultimate-scraper/SKILL.md).

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

Never paste a token into a URL or into a file inside this skill; pass it as `Authorization: Bearer` (the CLI does this for you).

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Step 1: Get the four anchors (what, where, remote-only?, how many)
- [ ] Step 2: Route to the Actor
- [ ] Step 3: Build the input and state the cost
- [ ] Step 4: Run and wait
- [ ] Step 5: Validate and deliver: locality, vacancy identity, per-board counts and failures
```

### Step 1: Get the four anchors

Ask these as one block; do not start a run without them.

1. **What** — the role or keyword(s), e.g. `data analyst`, `registered nurse`. Several are fine.
2. **Where** — a city/region string like `Chicago, IL`, or "remote".
3. **Remote-only?** — yes/no. "Yes" with no city routes to the remote aggregator (Step 2).
4. **How many** — a per-board cap (a run total on the remote aggregator, per query and per place on the LinkedIn-only scraper). Default to 20 per board for a first run; ask before going above 100.

For a careers-page watch, ask only for the company names (a role keyword is optional); its cap is per company (Step 3).

Optional follow-ups, only if the user raises them: posted-within window, salary required, job type, exclude staffing agencies, company watch list, Slack/Discord webhook for alerts.

### Step 2: Route to the Actor

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Jobs by role + location across the big boards | `flash_scraper/multi-jobboard-scraper` | community | Store title "Job Board Scraper: LinkedIn, Indeed, Glassdoor Job Postings API"; LinkedIn, Indeed, Glassdoor, The Muse by default; 8 more keyless boards optional; returns raw candidates that still require locality and vacancy-identity validation |
| Remote-only jobs from the remote boards | `flash_scraper/remote-job-aggregator` | community | RemoteOK, We Work Remotely, Working Nomads, DevITjobs, The Muse, Remotive, Jobicy, Himalayas, HN "Who is hiring", Arbeitnow (opt-in); no LinkedIn, Indeed or Glassdoor |
| LinkedIn jobs only, several titles and up to 25 places per run | `flash_scraper/linkedin-jobs-scraper` | community | Seniority checked on each job page; `applicants`, `job_score` and the job page's base-pay range; cheapest per row |
| A LinkedIn job-search URL the user pasted | `flash_scraper/linkedin-jobs-scraper` with `searchUrls` | community | The URL's keywords, place, distance, date, company, Easy Apply and under-10-applicants filters are sent as-is; `f_PP` cities are searched one by one; filters LinkedIn's public search ignores are checked by the Actor or named in the run status |
| Watch named companies' careers pages | `flash_scraper/multi-jobboard-scraper` with `atsCompanies` and `"sites": []` | community | Greenhouse, Lever, Ashby, Recruitee, BambooHR and Workable boards read directly, up to 20 companies per run; combine with `onlyNewJobs` for a daily alert |

Rule of thumb, first match wins: named companies' careers pages → multi-board scraper with `atsCompanies` and `"sites": []`. A pasted LinkedIn job-search URL → LinkedIn-only scraper with `searchUrls`; a pasted Indeed or Glassdoor search URL → multi-board scraper with `searchUrls` (each URL searches only its own board). LinkedIn as the only board wanted → LinkedIn-only scraper. A city or country in the request → multi-board scraper. "Remote" and nothing else → remote aggregator, so "Give me remote Python developer jobs posted this week across the remote job boards, with salary where listed" takes the remote input in Step 3. All three Actors run without an API key, login or cookies.

Check the live input schema before building input (fields change; the schema wins over this file):

    apify actors info "flash_scraper/multi-jobboard-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-job-boards 2>/dev/null

    apify actors info "flash_scraper/remote-job-aggregator" --input --json \
      --user-agent apify-awesome-skills/apify-job-boards 2>/dev/null

    apify actors info "flash_scraper/linkedin-jobs-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-job-boards 2>/dev/null

### Step 3: Build the input and state the cost

**Multi-board (city/region search).** Field names as in the live schema:

```json
{
  "searchTerm": "data analyst",
  "location": "Chicago, IL",
  "sites": ["linkedin", "indeed", "glassdoor", "muse"],
  "maxResults": 20,
  "countryIndeed": "usa",
  "strictKeywordMatch": true
}
```

- `sites` accepts: `linkedin`, `indeed`, `glassdoor`, `muse`, `remotive`, `jobicy`, `himalayas`, `hn_hiring`, `devitjobs_us`, `remoteok`, `weworkremotely`, `working_nomads`, and `naukri` / `bdjobs` for a place in India / Bangladesh only (any other location bills nothing on that board). Leave out `google`, `zip_recruiter`, `bayt` (blocked at the source) and `devitjobs_uk` (discontinued upstream): they stay in the enum, return nothing, bill nothing, and the run status names them.
- `maxResults` is **per board** (1–500), so 4 boards × 20 = up to 80 rows before deduplication; each term × location pair and each `atsCompanies` company gets its own cap.
- `strictKeywordMatch: true` drops rows whose title and description never mention the search term (LinkedIn in particular returns loosely related postings). Filtered rows are not billed.
- `isRemote: true` restricts to remote postings and, when `sites` is the default four, auto-adds the seven remote-only boards.
- Several roles or cities: use `searchTerms` / `locations` arrays instead of the singular fields (up to 5 terms, 10 places and 50 term × place searches per run; extras are named in `RUN_SUMMARY`, not run).
- An empty `location` means no place: Indeed (and Glassdoor where supported) search the whole `countryIndeed` country (default `usa`), the other boards search anywhere. There is no hidden New York default (the Console form only pre-fills `New York, NY`), so pass the user's place; a location naming a country (`Berlin, Germany`) switches the Indeed search to that country by itself.
- Company watch: `"atsCompanies": ["stripe", "openai"]` with `"sites": []` reads only those companies' own Greenhouse, Lever, Ashby, Recruitee, BambooHR or Workable boards (tried in that order, up to 20 companies per run); without `"sites": []` the default boards also run a search and bill their rows. Leave `searchTerm` out to read each whole board: the platform then fills in the schema default `software engineer`, which a watch reads as no term, so every role is delivered while the status line and the `search_term` column still say `software engineer` (ignore the log's hint to set `strictKeywordMatch`, which would cut the watch to that term). A typed `software engineer` is read the same way; to watch some roles only, add `requireTitleKeywords` (e.g. `["engineer"]`: titles containing any of them, the rest dropped before billing). Any other term keeps only postings that mention every word of it (of every term, with several `searchTerms`), and an empty string stops the run. `maxResults` keeps each company's newest postings on every run, so set it above what a company can post between two runs: 50 for a daily watch of Stripe and OpenAI, which each published at most 17 new roles a day in the fortnight to 2026-10-28.
- Monitoring: `"onlyNewJobs": true` on a schedule delivers and bills only postings this exact search has not delivered before (the Actor remembers what it delivered for 90 days); the first run is the baseline. A posting re-listed under a new URL or on another board can bill again.
- Alerts: `"webhookUrl": "https://hooks.slack.com/..."` posts a digest of new rows to Slack, Discord or any webhook.

**Remote aggregator.** Field names as in the live schema:

```json
{
  "searchTerms": ["python"],
  "boards": ["remoteok", "weworkremotely", "remotive", "jobicy", "himalayas", "hn_hiring"],
  "maxItems": 100,
  "matchDescriptions": true,
  "postedWithinDays": 7
}
```

- `matchDescriptions: true` matches the keyword in descriptions as well as titles (the README's measured example: 28 rows title-only vs 194 with descriptions for `python`).
- `salaryMinAnnual`, `seniority`, `countries`, `excludeKeywords` are cheap filters that run before billing.
- `onlyNewJobs` and `webhookUrl` work the same way as above.

**LinkedIn only.** Field names as in the live schema; send titles in `searchQueries` or pasted LinkedIn job-search URLs in `searchUrls` (below):

```json
{
  "searchQueries": ["product manager", "backend engineer"],
  "location": "London",
  "experienceLevel": ["4"],
  "maxItems": 10
}
```

- `searchQueries` takes several titles or keywords; each is searched separately and duplicates are removed across them before the job pages are read.
- `maxItems` (1–1000, default 100) applies to **each** query, and with `locations` (up to 25 places, one search each, used instead of `location`) to each place: 2 queries × 10 = up to 20 rows here. LinkedIn's public search stops at 800 results per search; `locations` is the way past it.
- `experienceLevel` codes: `1` Internship, `2` Entry level, `3` Associate, `4` Mid-Senior level, `5` Director. LinkedIn's search no longer applies them, so the Actor checks each job page's seniority (or clear title words when the poster set none): a job at another level, or whose page could not be read, is left out and not billed; a job with no level anywhere is kept.
- `titleInclude` / `titleExclude`, `companyNames` and `excludeAgencies` are checked on the search cards before any job page is read; LinkedIn no longer filters on `remote` and `contractType` (the Actor turns them into search keywords), so check `isRemote` and `employmentType` on the rows.
- `onlyNewJobs` and `webhookUrl` work the same way as above.

**LinkedIn from a pasted search URL.** Copy the address of a LinkedIn job search (opened logged out at `linkedin.com/jobs/search`) into `searchUrls`:

```json
{
  "searchUrls": ["https://www.linkedin.com/jobs/search/?keywords=data%20analyst&geoId=103644278&f_TPR=r86400"],
  "maxItems": 50
}
```

- Up to 25 URLs per run, each its own search; they replace `searchQueries`, `location`, `locations` and `geoId`, and `maxItems` applies to each URL. A job found by two URLs is delivered and billed once.
- Sent to LinkedIn as-is: `keywords`, `geoId` (wins over `location`), `distance`, `f_TPR` (any `r<seconds>` window, e.g. `r3600` for the past hour), `f_C`, `f_AL` (Easy Apply) and `f_EA` (under 10 applicants). Checked by the Actor instead, because LinkedIn's public search ignores them: `f_E` on each job page, `f_JT` / `f_WT` as search keywords. `f_PP` cities are searched one by one as their own `geoId` (up to 10 per URL, sharing the URL's `maxItems`).
- Not used, and named in the status message and `RUN_SUMMARY.search_urls`: `sortBy` (results come in relevance order), salary `f_SB2` (use `minSalary`) and other `f_` filters. Page and tracking parameters such as `currentJobId` are dropped.
- A URL that is not a job search (a `/jobs/view/` posting, a `/jobs/collections/` page, a company page, an Indeed or Glassdoor URL, a `lnkd.in` link) is not run, is named with its reason and bills nothing; if no URL can run, the run stops without falling back to `searchQueries`. Indeed and Glassdoor search URLs go to the multi-board scraper's `searchUrls`.
- Card filters, `minSalary`, `onlyNewJobs` and `webhookUrl` still apply on top of every URL; with `onlyNewJobs` the memory follows each URL's search filters, not its tracking parameters, so a re-copied URL keeps its memory.

**Cost, stated before the run.** All three Actors bill per delivered row plus a $0.00005 start fee per run; filtered and deduplicated rows are not billed. Read the current price from the Store Pricing tab (the schema fetch in Step 2 also returns the `pricingInfos` records; the last one whose `startedAt` has passed is in force). At the time of writing (live records read 2026-11-02) the free-plan rate is $0.005 per job on the multi-board scraper, $0.003 on the remote aggregator and $0.002 on the LinkedIn-only scraper; paid plans pay the same or less. So a first multi-board run of 4 boards × 20 rows costs at most about $0.40 and usually less after deduplication; a 100-row remote run at most $0.30; the LinkedIn example (2 queries × 10) at most $0.04 and the pasted-URL example (1 URL × 50) at most $0.10; the Stripe and OpenAI watch's first run at most $0.50 (2 companies × 50), and each later run $0.005 per new posting. If the user asks for more than 500 rows, say the number and confirm before running.

### Step 4: Run and wait

    apify actors call "flash_scraper/multi-jobboard-scraper" -i '{"searchTerm":"data analyst","location":"Chicago, IL","sites":["linkedin","indeed","glassdoor","muse"],"maxResults":20,"strictKeywordMatch":true}' \
      --json \
      --user-agent apify-awesome-skills/apify-job-boards \
      2>/dev/null

    apify actors call "flash_scraper/remote-job-aggregator" -i '{"searchTerms":["python"],"maxItems":100,"matchDescriptions":true,"postedWithinDays":7}' \
      --json \
      --user-agent apify-awesome-skills/apify-job-boards \
      2>/dev/null

    apify actors call "flash_scraper/linkedin-jobs-scraper" -i '{"searchQueries":["product manager","backend engineer"],"location":"London","experienceLevel":["4"],"maxItems":10}' \
      --json \
      --user-agent apify-awesome-skills/apify-job-boards \
      2>/dev/null

    apify actors call "flash_scraper/linkedin-jobs-scraper" -i '{"searchUrls":["https://www.linkedin.com/jobs/search/?keywords=data%20analyst&geoId=103644278&f_TPR=r86400"],"maxItems":50}' \
      --json \
      --user-agent apify-awesome-skills/apify-job-boards \
      2>/dev/null

    apify actors call "flash_scraper/multi-jobboard-scraper" -i '{"atsCompanies":["stripe","openai"],"sites":[],"onlyNewJobs":true,"maxResults":50}' \
      --json \
      --user-agent apify-awesome-skills/apify-job-boards \
      2>/dev/null

The last command is the company watch's baseline run; run the same input daily with an Apify schedule to receive only new postings. Typical durations: a 4-board, 20-per-board multi-board run finishes in about a minute, and a one-company `atsCompanies` call with `"sites": []` returned rows in well under a minute; the remote aggregator answers a 20-row query on the four single-request boards in a few seconds and took 84 s across all ten boards; the LinkedIn-only scraper reads about one job page per second after the search (10 full rows in 9 s). The JSON output contains `defaultDatasetId`; fetch the rows with:

    apify datasets get-items DATASET_ID --format json \
      --user-agent apify-awesome-skills/apify-job-boards 2>/dev/null

### Step 5: Validate and deliver

Treat the downloaded dataset as raw output. Before delivery:

1. For a location-constrained request, inspect every returned `location` against the requested city, region and country. Keep matching rows as qualified; separate wrong-location and missing or unverifiable locations. A board answered only if it produced qualified rows, not merely raw rows.
2. Build a stable vacancy identity. Prefer an employer/ATS vacancy ID when available; otherwise use a board's stable job ID together with its board namespace, since unrelated boards can reuse IDs. Otherwise use the job URL after removing only parameters documented or clearly identified as tracking; preserve unknown parameters and every path or parameter that can distinguish requisitions. Use company, normalized title and location only to flag candidates for review, never as the sole basis for merging distinct vacancies.
3. Re-run the identity check across all raw rows even when `found_on_sites` or `duplicate_count` says the Actor already merged them. Merge rows only when their stable identity matches, combine their source boards, and retain genuinely distinct requisitions. Preserve the locality decision for each source row; a duplicate link must not turn an excluded location into qualified coverage.
4. Calculate raw, location-qualified and deduplicated counts for each requested board. Keep excluded rows available separately with the exclusion reason so the user can audit the partial result.

Report, in this order:

1. Total delivered rows and a per-board table of raw, qualified and deduplicated counts. Name wrong-location, unverifiable-location, empty and blocked boards as partial failures.
2. What the local identity check merged, which stable identifier supported each merge, and which possible duplicates remain unresolved. `found_on_sites` and `duplicate_count` are useful evidence but are not proof that deduplication is complete.
3. The columns the user asked for. Verified column names on the multi-board scraper include `title`, `company`, `location`, `site`, `date_posted`, `job_url`, `found_on_sites`, `duplicate_count`; the dataset has 65 stable columns, all listed in the Actor README under "Output fields". The LinkedIn-only scraper has 27 columns, including `jobTitle`, `companyName`, `location`, `jobUrl`, `jobId`, `postedDate`, `seniority`, `employmentType`, `applicants`, `salaryMin`, `salaryMax`, `descriptionText` and `job_score`; `applyUrl` is always `null`. Do not invent columns: if a field the user wants is not in the dataset, say so.
4. A link to the dataset or the Console run, and the run's HTML report URL (each Actor writes one to the run's key-value store when the run delivers rows, printed in the log as `Report saved:`).

Salary is present only where a board publishes it (49 of 80 rows on the multi-board scraper's default four-board run of 2026-10-01: Glassdoor 20 of 20, Indeed 19, LinkedIn 10, The Muse none; 35% of rows on the remote aggregator's default run; LinkedIn-only rows only when the job page shows a base-pay range); set `requireSalary: true` on the multi-board or LinkedIn-only scraper if the user needs salary on every row, and warn that the row count will drop.

## Troubleshooting

- **A board shows 0 rows or "blocked" in the log** → the run still succeeds; the report names the board. LinkedIn, Indeed and Glassdoor are fetched through Apify's datacenter proxy by default and occasionally throttle a single search; rerun with a narrower term or fewer boards rather than raising `maxResults`.
- **Rows that do not match the role** → set `strictKeywordMatch: true` (multi-board) or `titleInclude` / `titleExclude` (LinkedIn-only); on the remote aggregator send `matchDescriptions: false` for title-only matching and `excludeKeywords` for the terms to drop (its `strictFilters` only drops rows that lack a filter's data). All of these filter before billing.
- **Same job appears twice** → inspect stable job or requisition IDs first, then compare URLs after removing only confirmed tracking parameters. The Actor can leave duplicates even when rows report `duplicate_count`; merge confirmed matching identities across or within a board, but do not merge on company + normalized title alone because separate requisitions can share both.
- **A board returns jobs outside the requested city** → classify those rows as wrong-location and exclude them from the qualified table; separate missing or ambiguous locations as unverifiable. Report the board's raw, qualified and deduplicated counts and deliver an honest partial result from the boards that did satisfy the locality check.
- **Indeed or Glassdoor rows from the wrong country** → `countryIndeed` (default `usa`) picks the country site both boards search; set it (`uk`, `canada`, `india`, ...) when the location string does not name the country. An unrecognised value falls back to `usa` with a note in `RUN_SUMMARY` and never fails the run.
- **A watched company comes back "not found"** → it is not on Greenhouse, Lever, Ashby, Recruitee, BambooHR or Workable (Workday, SmartRecruiters, iCIMS and custom careers sites are not read), or its board slug differs from its name. Names are lowercased and stripped to letters and digits (`"Stripe Inc."` → `stripeinc`), so pass the slug from the careers URL (`jobs.lever.co/<slug>`, `jobs.ashbyhq.com/<slug>`). A not-found company is named in the log and `RUN_SUMMARY` and bills nothing; `ATS lookup incomplete` means a board refused or timed out, so rerun that company.
- **LinkedIn-only rows lack seniority, employment type or description** → LinkedIn blocked some job pages; the rows still ship with the search-card fields, the run still succeeds, and the status message says how many full records arrived and why. With `experienceLevel` set, jobs whose page could not be read are left out and not billed. If every request gets HTTP 999 or 403, set `proxyConfiguration` (Apify RESIDENTIAL).
- **A pasted LinkedIn URL was not run, or returned fewer rows than `maxItems`** → read the status message and `RUN_SUMMARY.search_urls`: a URL that is not a job search is named with its reason and bills nothing, a URL's `f_PP` cities share its `maxItems`, and a city LinkedIn rate-limited (HTTP 429) is named as not fetched; rerun it later.
- **Monitoring run delivers nothing** → with `onlyNewJobs: true` an empty run means no new postings since the last delivery, which is the expected result, not a failure. The run's status message says so.
- **Cost higher than expected** → `maxResults` is per board (and per `atsCompanies` company), `sites` may include boards the user did not mean, and `atsCompanies` without `"sites": []` also runs the default board search; on the LinkedIn-only scraper `maxItems` is per query and per place. List the boards, companies or queries and the cap back to the user before the next run.
