# Actor index: what each Actor is for in this chain

This file says which Actor plays which role in the chain. For inputs, defaults, prices and output fields, read each Actor's live README and input schema before calling it; they change, and they win over this file.

## Lane A, aggregators

- **`johnvc/Google-Jobs-Scraper`:** breadth.
  - Call it once per title variant, bounded to a single page. Its default pages without limit.
  - Rows carry the posting's own `location`, the run's `search_location`, `apply_options`, and a base64 `job_id`.
- **`johnvc/linkedin-job-search-scraper`:** the exemplar and the seeds.
  - In job mode, a LinkedIn URL returns the full posting plus `similarJobs` and `peopleAlsoViewed`.
  - In search mode it returns listings for a variant.
  - Records can come from a cache of up to 7 days (`fromCache`), and apply URLs are usually empty, so LinkedIn rows are never proof a job is open.

## Lane B, employers' own boards

- **`johnvc/ashby-job-board-scraper`:**
  - `companies` accepts employer names, board slugs, or a single job URL. Use it to check the LinkedIn seed employers.
  - With `companies` empty, it sweeps the largest boards. Pass `titleKeywords`, location keywords and `maxJobsPerCompany`.
- **`johnvc/greenhouse-job-board-api`:**
  - `companies` accepts board tokens or URLs (a single job URL works). Take the token from a real Greenhouse link; never derive it from a company name.
  - With `companies` empty, it sweeps the largest boards. Use the same filters as Ashby; a 200-board sweep took about 4 minutes in testing.
- **`johnvc/jazzhr-jobs-api`:** with no company given, it searches every employer on the platform by title keywords. Useful for small-business, hourly and clinical roles.
- **`johnvc/workday-career-sites-api`:** a company name or domain in, that company's Workday career site out.
- **`johnvc/workday-careers-api`:** a site URL plus `searchText` and a small `maxJobsPerSite`. A single job URL expands to the whole site, so always filter.
- **`johnvc/oracle-taleo-jobs-api`:** a company name or domain resolves to its Oracle boards, then `searchText` and `maxJobsPerSite` narrow the pull.
- **`johnvc/icims-careers-api`:** a company name or a careers-site URL, plus `keywords`.

## Not routed, and why

- **No Actor here covers** Lever, SmartRecruiters, Workable or Jobvite. Rows on those systems stay "aggregator only".
- **Indeed apply links** redirect through Indeed and never reach the employer, so Indeed rows can't be confirmed.
- **Paylocity:** its discovery sweep did not finish inside a 900-second run in testing, which is too slow for this chain.
- **Retired Actors:** isolved and SAP SuccessFactors jobs, both retired on 2026-10-23.

## Calling them

Every run goes through the runs endpoint with `maxTotalChargeUsd`, using the call shape in SKILL.md. Keep at most 4 runs in flight on a free plan; the limit is 5 concurrent runs.
