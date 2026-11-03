# Actor index: apify-company-careers-jobs

Routing table for the two Actors this skill uses. Both are community Actors built and priced by the skill's author (Jordan Belfort). Source: the Actors' READMEs, input schemas and code.

| Platform | User intent | Actor ID | Tier | Notes |
|----------|-------------|----------|------|-------|
| Workday, Greenhouse, Lever (US and EU), Ashby, Workable, SmartRecruiters, Recruitee, Personio, Teamtailor | Jobs at named companies, from the company's own ATS feed | `jordan-belfort/ats-jobs-api` | community | $0.001 per job returned (event `job`). Name, domain or careers URL in. `atsSystems` limits name/domain detection. |
| Workday (`*.myworkdayjobs.com`, `myworkdaysite.com`) | Jobs at large employers on Workday | `jordan-belfort/workday-jobs-scraper` | community | $0.001 per job returned. 1,447 companies by name, others by careers URL. |

## Input fields (both Actors)

| Field | What it does |
|-------|--------------|
| `companies` | Careers page URLs, domains or company names (required unless `searchKeywords` is given) |
| `searchKeywords` | `ats-jobs-api` only: search mode over the daily index, no company list; every word of a keyword must be a word of the title |
| `maxResults` | Search mode: newest matches up to this many (default 100) |
| `maxPerCompany` | Search mode: at most this many per company board (default 10, 0 = no limit) |
| `titleKeywords` | Keep jobs whose title contains any of these (case-insensitive) |
| `locationKeywords` | Keep jobs whose location or country contains any of these |
| `workplaceType` | Only these workplace types: `remote`, `hybrid`, `onsite`. Every job carries a normalised `workplaceType` (the ATS's own field, else a Remote/Hybrid/On-site word in location or title); jobs with none are dropped when set |
| `maxExperienceYears` | Only jobs whose description asks for at most this many years of experience (e.g. `2` for junior roles); every job carries `experienceYears`, jobs that name no number are dropped when set |
| `countries` | Only jobs in these countries (ISO codes like `US`, `DE`, or names), from the ATS field or the location text; every job carries `countryCodes` |
| `excludeKeywords` | Drop jobs whose title matches any of these, whole words (e.g. `senior`, `manager`) |
| `departments` | Keep jobs whose department or team contains any of these (e.g. `Engineering`, `Marketing`) |
| `employmentTypes` | Only `full-time`, `part-time`, `contract`, `internship`, `temporary` (normalised from the ATS field or the title); every job carries `employmentTypes`, jobs with neither are dropped when set |
| `minSalary` | Only jobs whose posted pay range reaches this yearly amount (top of range; hourly x 2080, monthly x 12). Not converted between currencies, so pair it with `salaryCurrencies`; jobs with no posted salary are dropped when set |
| `salaryCurrencies` | Only jobs paid in these ISO currencies, e.g. `["USD"]` |
| `remoteOnly` | Only remote jobs (same as `workplaceType: ["remote"]`) |
| `seniority` | Only these levels: `intern`, `entry`, `mid`, `senior`, `lead`, `manager`, `director`, `executive` (read from the title) |
| `postedWithinDays` | Only jobs published in the last N days (0 = all; jobs without a date are kept, except Workday jobs known to be 30+ days old) |
| `onlyNewJobs` | Monitor mode: skip job ids returned by earlier runs |
| `monitorName` | Separate memory per watch list (default `default`) |
| `includeDescription` | Full description as HTML and text (default on) |
| `maxJobsPerCompany` | Cap per company after filters (0 = no cap) |
| `atsSystems` | `ats-jobs-api` only: restrict detection to some of greenhouse, lever, ashby, workable, smartrecruiters, recruitee, personio, teamtailor |

## Output (one row per job)

`company`, `ats`, `boardSlug`, `jobId`, `title`, `department`, `team`, `location`, `allLocations`, `country`, `remote`, `workplaceType`, `employmentType`, `salaryMin`, `salaryMax`, `salaryCurrency`, `salaryInterval`, `salaryText`, `salarySource`, `experienceYears`, `url`, `applyUrl`, `publishedAt`, `updatedAt`, `descriptionText`, `descriptionHtml`, `input`, `scrapedAt`. Fields an ATS does not publish are `null`. A company that cannot be found gives one row with `input` and `error`. Run statistics are in the `STATS` record of the run's key-value store.

## Picking between the two

- Mixed list, or unsure which ATS a company uses: `ats-jobs-api`.
- Only Workday employers: either works. `workday-jobs-scraper` adds "did you mean" suggestions for unknown names, and its monitor memory is a separate store (`workday-jobs-seen`, versus `ats-jobs-seen`).
