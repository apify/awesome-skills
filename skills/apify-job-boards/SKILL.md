---
name: apify-job-boards
description: Pull job postings from many boards in one run and prepare one validated, deduplicated table. Routes "find jobs / scrape job postings / build a job list / monitor new jobs / track a company's careers page" requests to a multi-board job scraper (LinkedIn, Indeed, Glassdoor, The Muse plus keyless boards) or a remote-only aggregator (RemoteOK, We Work Remotely, Remotive, Jobicy, Himalayas, HN Who is hiring), with output-locality checks, per-board raw/qualified/deduplicated counts, only-new-jobs monitoring, per-board caps and honest cost estimates. Use when the user asks to scrape jobs across job boards, get Indeed or Glassdoor postings without an API key, collect remote developer jobs, watch a company's Greenhouse/Lever/Ashby careers page, or set up a daily new-jobs alert.
author: Zakariae (Flash Scrape)
author_url: https://github.com/ZAKRIAZ
metadata:
  category: data-extraction
  keywords: "jobs, job-postings, job-boards, indeed, glassdoor, linkedin-jobs, remote-jobs, job-aggregator, job-alerts, careers-page, greenhouse, lever, ashby, recruiting, salary-data, apify"
---

# Job boards to one table

Disclosure: the author of this skill owns both Actors it routes to (`flash_scraper/multi-jobboard-scraper` and `flash_scraper/remote-job-aggregator`). They are pay-per-result Actors on the Apify Store; no referral or tracking parameters are used anywhere in this skill.

Turn "I need job postings" into one validated, deduplicated dataset by routing the request to the right multi-board Actor, sizing the run so the user knows the cost before it starts, checking the returned locations and vacancy identities, and returning the rows with the board each job was found on. Treat the Actor output as raw input to these checks, not as proof that its location filtering or deduplication succeeded.

## Example prompts

Prompts this skill handles:

- "Scrape software engineer jobs in Austin from LinkedIn, Indeed and Glassdoor into one spreadsheet, no duplicates."
- "Give me remote Python developer jobs posted this week across the remote job boards, with salary where listed."
- "Watch Stripe's and OpenAI's careers pages and only tell me about new roles."

For the Austin request, try all three requested boards, then validate each returned location and vacancy identity before delivery. If Glassdoor returns only wrong-city or unverifiable rows, deliver the qualified LinkedIn and Indeed rows as a partial result and report Glassdoor's raw, qualified and deduplicated counts as a board failure. Do not claim three-board coverage merely because Glassdoor returned rows.

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
4. **How many** — a per-board cap. Default to 20 per board for a first run; ask before going above 100.

Optional follow-ups, only if the user raises them: posted-within window, salary required, job type, exclude staffing agencies, company watch list, Slack/Discord webhook for alerts.

### Step 2: Route to the Actor

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Jobs by role + location across the big boards | `flash_scraper/multi-jobboard-scraper` | community | LinkedIn, Indeed, Glassdoor, The Muse by default; 8 more keyless boards optional; returns raw candidates that still require locality and vacancy-identity validation |
| Remote-only jobs from the remote boards | `flash_scraper/remote-job-aggregator` | community | RemoteOK, We Work Remotely, Working Nomads, DevITjobs, The Muse, Remotive, Jobicy, Himalayas, HN "Who is hiring", Arbeitnow (opt-in); cheapest per row |
| Watch named companies' careers pages | `flash_scraper/multi-jobboard-scraper` with `atsCompanies` | community | Greenhouse, Lever, Ashby and other ATS boards read directly; combine with `onlyNewJobs` for a daily alert |

Rule of thumb: a city or country in the request → multi-board scraper. "Remote" and nothing else → remote aggregator. Both Actors run without an API key, login or cookies.

Check the live input schema before building input (fields change; the schema wins over this file):

    apify actors info "flash_scraper/multi-jobboard-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-job-boards 2>/dev/null

    apify actors info "flash_scraper/remote-job-aggregator" --input --json \
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

- `sites` accepts: `linkedin`, `indeed`, `glassdoor`, `muse`, `remotive`, `jobicy`, `himalayas`, `hn_hiring`, `devitjobs_us`, `devitjobs_uk`, `remoteok`, `weworkremotely`, `working_nomads`. Leave out `google`, `zip_recruiter`, `bayt`, `bdjobs`, `naukri`: they are in the enum for backwards compatibility but blocked at the source, and the run report will say so.
- `maxResults` is **per board**, so 4 boards × 20 = up to 80 rows before deduplication.
- `strictKeywordMatch: true` drops rows whose title and description never mention the search term (LinkedIn in particular returns loosely related postings). Filtered rows are not billed.
- `isRemote: true` restricts to remote postings and auto-adds the remote boards.
- Several roles or cities: use `searchTerms` / `locations` arrays instead of the singular fields.
- Company watch: `"atsCompanies": ["stripe", "openai"]` reads their Greenhouse/Lever/Ashby boards directly; add `"onlyNewJobs": true` on a schedule so each run delivers only postings it has not sent before (the Actor remembers what it delivered for 90 days).
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

**Cost, stated before the run.** Both Actors bill per delivered row; filtered and deduplicated rows are not billed. Read the current price from the Store Pricing tab (the schema fetch in Step 2 also returns the pricing block). At the time of writing the free-plan rate is $0.005 per job on the multi-board scraper and $0.002 per job on the remote aggregator; paid plans pay less. So a first multi-board run of 4 boards × 20 rows costs at most about $0.40 and usually less after deduplication; a 100-row remote run about $0.20. If the user asks for more than 500 rows, say the number and confirm before running.

### Step 4: Run and wait

    apify actors call "flash_scraper/multi-jobboard-scraper" -i '{"searchTerm":"data analyst","location":"Chicago, IL","sites":["linkedin","indeed","glassdoor","muse"],"maxResults":20,"strictKeywordMatch":true}' \
      --json \
      --user-agent apify-awesome-skills/apify-job-boards \
      2>/dev/null

    apify actors call "flash_scraper/remote-job-aggregator" -i '{"searchTerms":["python"],"maxItems":100,"matchDescriptions":true,"postedWithinDays":7}' \
      --json \
      --user-agent apify-awesome-skills/apify-job-boards \
      2>/dev/null

Typical durations: a 4-board, 20-per-board multi-board run finishes in about a minute; the remote aggregator answers a 100-row query in under a minute, and a 20-row query on the four single-request boards in a few seconds. The JSON output contains `defaultDatasetId`; fetch the rows with:

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
3. The columns the user asked for. Verified column names on the multi-board scraper include `title`, `company`, `location`, `site`, `date_posted`, `job_url`, `found_on_sites`, `duplicate_count`; the dataset has 54 stable columns, all listed in the Actor README under "Output fields". Do not invent columns: if a field the user wants is not in the dataset, say so.
4. A link to the dataset or the Console run, and the run's HTML report URL (both Actors write one to the run's key-value store, printed in the log as `Report saved:`).

Salary is present only where a board publishes it (roughly a third of postings on the big boards); set `requireSalary: true` on the multi-board scraper if the user needs salary on every row, and warn that the row count will drop.

## Troubleshooting

- **A board shows 0 rows or "blocked" in the log** → the run still succeeds; the report names the board. LinkedIn, Indeed and Glassdoor are fetched through Apify's datacenter proxy by default and occasionally throttle a single search; rerun with a narrower term or fewer boards rather than raising `maxResults`.
- **Rows that do not match the role** → set `strictKeywordMatch: true` (multi-board) or `strictFilters: true` (remote); both filter before billing.
- **Same job appears twice** → inspect stable job or requisition IDs first, then compare URLs after removing only confirmed tracking parameters. The Actor can leave duplicates even when rows report `duplicate_count`; merge confirmed matching identities across or within a board, but do not merge on company + normalized title alone because separate requisitions can share both.
- **A board returns jobs outside the requested city** → classify those rows as wrong-location and exclude them from the qualified table; separate missing or ambiguous locations as unverifiable. Report the board's raw, qualified and deduplicated counts and deliver an honest partial result from the boards that did satisfy the locality check.
- **`countryIndeed` errors** → Indeed and Glassdoor need a country code (`usa`, `uk`, `canada`, ...); the location string alone does not set it.
- **Monitoring run delivers nothing** → with `onlyNewJobs: true` an empty run means no new postings since the last delivery, which is the expected result, not a failure. The run's status message says so.
- **Cost higher than expected** → `maxResults` is per board and `sites` may include boards the user did not mean; list the boards and the cap back to the user before the next run.
