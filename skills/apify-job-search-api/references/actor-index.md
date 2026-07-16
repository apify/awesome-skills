# Actor index: job search API feed

The primary Actor for this skill, plus the job-data Actors worth chaining when a feed needs more than Google Jobs. The agent reads this after `SKILL.md` to pick the right Actor for a specific user intent.

| Platform | User intent | Actor ID | Tier | Notes |
|----------|-------------|----------|------|-------|
| Google Jobs | A polled job search API or feed by role and location | `johnvc/Google-Jobs-Scraper` | community | Pay per page (about 10 listings per page). Feed pattern: small `num_results`, hard `max_pagination` cap, dedupe on `job_id`, parse `posted_at` client-side. |

## Chain with other job-data Actors

| User intent | Actor ID | Notes |
|-------------|----------|-------|
| Bulk exports billed per result instead of per page | `johnvc/google-jobs-scraper---pay-per-result` | Same Google Jobs source, per-result billing. |
| LinkedIn-hosted listings and salary ranges in the feed | `johnvc/linkedin-jobs-api` | By keyword and location. |
| Employer reviews enrichment per listing | `johnvc/glassdoor-reviews-api` | Feed `company_name` from a listing row into it. |

## How to extend

1. Search candidates: `apify actors search "jobs api" --json --limit 20 2>/dev/null`
2. Fetch the input schema: `apify actors info "johnvc/Google-Jobs-Scraper" --input --json 2>/dev/null`
3. Add a row above with the user intent that should trigger it.

Note: `Tier` here is `community` because these are third-party Actors published by John Cole on the Apify Store, not Apify-maintained Actors.
