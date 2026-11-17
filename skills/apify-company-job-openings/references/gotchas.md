# Company job openings: input rules, fields by system, cost guardrails

## How a company is matched

- A job board URL is read as given. This is the most exact input.
- A domain or careers page URL is matched through the company's own website: the job board its pages link to is used. If the site carries job postings in its own page markup instead, those are returned with `source: "jsonld"`.
- A plain name is matched by the board's own company name. If more than one board with open jobs carries that name, the run returns one free `not_found` row that lists them with their URLs; send one of those URLs.
- Workday boards are found from their URL (such as `https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite`) or from a link on the company's careers page, never from a name.
- Greenhouse EU boards (`boards.eu.greenhouse.io`, `job-boards.eu.greenhouse.io`) are not supported and return an `unsupported` row.
- A page on another company's site, such as a directory profile, is not the company's own site. Send the company's own domain.
- At most 100 companies per run. The same board named twice is delivered once.

## Fields by hiring system

| System | Department | Country | Remote flag | Employment type | Posting date | Salary |
|---|---|---|---|---|---|---|
| Greenhouse | yes | no | only when the location says "remote" | no | yes | no |
| Lever | yes | yes | yes | yes | yes | when published |
| Ashby | yes | yes | yes | yes | yes | when published |
| Workable | yes | yes | yes | yes | yes | no |
| SmartRecruiters | yes | yes | yes | yes | yes | no |
| Recruitee | yes | yes | yes | yes | yes | when published |
| Personio | yes | no | only when the location says "remote" | yes | yes | when published |
| Workday | no | with descriptions only | no | with descriptions only | approximate | no |

Consequences for filters:

- `locations` with a country matches the job's country, or whole words of the location text when the system gives no country. A Greenhouse job located in "Berlin" is not matched by "Germany".
- `remoteOnly` leaves out jobs whose remote status is unknown.
- `postedWithinDays` leaves out jobs without a posting date.

## Cost guardrails

- Worst case for a run: `companies x maxJobsPerCompany x $0.0015` (x $0.0025 with `includeDescription`).
- `includeDescription` needs one extra request per job on SmartRecruiters and Workday, so it is slower there. Use it for a short list of jobs, not for a whole board.
- With `onlyNew`, the first run returns every open job up to the limit; later runs return only jobs not returned before. The Actor remembers returned job IDs in a key-value store named `company-jobs-scraper-seen` in the user's own Apify account.
- When the user's spending limit is reached, the run stops and adds a `limit_reached` row.

## What it never returns

No recruiter, hiring-manager, contact or applicant data. Descriptions are the posting's own text, with email addresses and clearly formatted phone numbers removed.
