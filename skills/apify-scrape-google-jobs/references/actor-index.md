# Actor index: scrape Google Jobs

The primary Actor for this skill, plus the job-data Actors worth chaining when a task needs more than listings. The agent reads this after `SKILL.md` to pick the right Actor for a specific user intent.

| Platform | User intent | Actor ID | Tier | Notes |
|----------|-------------|----------|------|-------|
| Google Jobs | Scrape listings for a query and location to JSON | `johnvc/Google-Jobs-Scraper` | community | Pay per page (about 10 listings per page). Inputs: `query` (required), `location`, `country`, `language`, `google_domain`, `num_results`, `max_pagination`, radius via `include_lrad` plus `lrad_value`. One flat row per listing. |

## Chain with other job-data Actors

| User intent | Actor ID | Notes |
|-------------|----------|-------|
| Bulk exports billed per result instead of per page | `johnvc/google-jobs-scraper---pay-per-result` | Same Google Jobs source, per-result billing. |
| LinkedIn-hosted listings and salary ranges | `johnvc/linkedin-jobs-api` | By keyword and location. |
| Employer reviews behind a listing | `johnvc/glassdoor-reviews-api` | Feed `company_name` from a listing row into it. |

## How to extend

1. Search candidates: `apify actors search "google jobs" --json --limit 20 2>/dev/null`
2. Fetch the input schema: `apify actors info "johnvc/Google-Jobs-Scraper" --input --json 2>/dev/null`
3. Add a row above with the user intent that should trigger it.

Note: `Tier` here is `community` because these are third-party Actors published by John Cole on the Apify Store, not Apify-maintained Actors.
