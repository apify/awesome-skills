# Board notes

What each board returned in test runs on 2026-11-21, all with `openclawai/job-board-scraper` unless noted. Boards change; re-check against a small run when something here looks wrong.

## Test runs

| Search | Boards | Rows | Time | Notes |
|--------|--------|------|------|-------|
| `data engineer`, Austin, TX, `maxResults` 5 | linkedin, indeed, glassdoor, zip_recruiter | 20 (5 per board) | 101 s | ZipRecruiter needed a second warm-up attempt; platform usage was larger than the job fees |
| `devops engineer`, Bangalore, `countryIndeed` india, `maxResults` 5 | naukri, bayt, linkedin | 15 (5 per board) | 47 s | Naukri and Bayt ignored the location (below) |
| `registered nurse`, Chicago, IL, `maxResults` 10, `hoursOld` 24 | linkedin, indeed | 20 (10 per board) | 33 s | Platform usage about a tenth of the 4-board run |
| `accountant`, Denver, CO, `maxResults` 20, run cap $0.05 | linkedin, indeed | 7 | under 5 s of scraping | Cap reached after Indeed finished; LinkedIn rows were never saved |
| `product manager`, London, `maxResults` 10, `linkedinFetchDescription` (LinkedIn Jobs Scraper) | LinkedIn | 10 | 31 s | Every row had a description, `job_level` and `company_industry` |
| Paychex with domain, `hoursOld` 48, `maxJobsPerCompany` 5 (Indeed & ZipRecruiter Scraper, companies mode) | indeed, zip_recruiter | 1 company row + 5 job rows | 125 s | ZipRecruiter failed its anti-bot warm-up twice and was reported in `sites_with_errors` |

## Per board

| Board | Location applied | Fields present | Missing or unreliable |
|-------|------------------|----------------|-----------------------|
| LinkedIn | yes | `id`, `title`, `company`, `location`, `job_url`, `company_url`, usually `date_posted` | `description` and `job_url_direct` only with `linkedinFetchDescription`; `date_posted` empty on some rows; salary rare |
| Indeed | yes, within `distance` (default 50 miles) | `id`, `description`, `date_posted`, `job_url_direct`, company details, salary on about half the rows | none seen |
| Glassdoor | yes, needs `countryIndeed` outside the US | `description`, `date_posted`, salary on every test row, `company_rating` | without `hoursOld`, postings up to nine months old |
| ZipRecruiter (US and Canada only) | yes | `title`, `company`, `location`, `job_url` | no `id`, `date_posted`, salary or description; one of five titles was off-target |
| Naukri (India) | **no**: returned jobs across India for a Bangalore search | `date_posted`, `skills`, `experience_range`, `work_from_home_type`, `company_rating`, `vacancy_count`; salary amount and currency on some rows | `salary_interval` empty; `description` empty |
| Bayt (Gulf and Middle East) | **no**: `location` is empty; the country is in the URL path (`bayt.com/en/<country>/jobs/...`) | `id`, `title`, `company`, `date_posted`, `job_url` | returned jobs in the UAE, Saudi Arabia, Qatar and Germany for one search; some titles off-target |
| Google Jobs, BDJobs | n/a | n/a | return no rows at the moment; leave them out of `sites` |

## Cost notes

- `openclawai/job-board-scraper` bills platform usage (compute and residential proxy traffic) to the user on top of the per-job price. Most of that usage comes from the browser boards (Glassdoor, ZipRecruiter, Naukri, Bayt).
- `openclawai/linkedin-jobs-scraper` and `openclawai/indeed-ziprecruiter-scraper` include platform usage in their prices. The Indeed & ZipRecruiter Scraper's start event is charged per GB of memory, so batch companies into one run.
- Read prices on each Actor's Store page (Pricing tab) at run time. After a run, `chargedEventCounts` and `usageTotalUsd` from `apify runs info` give the real cost.
