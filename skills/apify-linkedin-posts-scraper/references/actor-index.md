# Actor index: LinkedIn posts scraper

The primary Actor for this skill, plus the LinkedIn Actors worth chaining when a task needs more than posts. The agent reads this after `SKILL.md` to pick the right Actor for a specific user intent.

| Platform | User intent | Actor ID | Tier | Notes |
|----------|-------------|----------|------|-------|
| LinkedIn | Scrape a profile's posts or specific post URLs to JSON | `johnvc/linkedin-posts-api` | community | Pay per post. Inputs: `profileUrls` (up to 25), `postUrls` (up to 1000), `maxPostsPerProfile` (up to 200), `startDate`/`endDate`. One flat row per post. |

## Chain with the rest of the LinkedIn suite

| User intent | Actor ID | Notes |
|-------------|----------|-------|
| Structured profile data for a post's author | `johnvc/linkedin-profile-api` | Feed `authorUrl` from a post row into it. |
| Company firmographics behind an author | `johnvc/linkedin-company-api` | Use the author's company. |
| Open roles as a hiring signal | `johnvc/linkedin-jobs-api` | By keyword and location. |

## How to extend

1. Search candidates: `apify actors search "linkedin posts" --json --limit 20 2>/dev/null`
2. Fetch the input schema: `apify actors info "johnvc/linkedin-posts-api" --input --json 2>/dev/null`
3. Add a row above with the user intent that should trigger it.

Note: `Tier` here is `community` because these are third-party Actors published by John Cole on the Apify Store, not Apify-maintained Actors.
