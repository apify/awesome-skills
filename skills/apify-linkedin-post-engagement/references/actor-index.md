# Actor index: LinkedIn post engagement

The primary Actor for this skill, plus the LinkedIn Actors worth chaining when a task needs more than post engagement. The agent reads this after `SKILL.md` to pick the right Actor for a specific user intent.

| Platform | User intent | Actor ID | Tier | Notes |
|----------|-------------|----------|------|-------|
| LinkedIn | Measure reactions, comments, and shares across a profile's posts | `johnvc/linkedin-posts-api` | community | Pay per post. Ships an `engagement` dataset view: author, headline, followers, likes, comments, shares, date, URL. |

## Chain with the rest of the LinkedIn suite

| User intent | Actor ID | Notes |
|-------------|----------|-------|
| Profile data for a high-engagement author | `johnvc/linkedin-profile-api` | Feed `authorUrl` into it to profile who is winning. |
| Company firmographics behind an author | `johnvc/linkedin-company-api` | Segment engagement by company. |
| Open roles as a hiring signal | `johnvc/linkedin-jobs-api` | Pair engagement with hiring intent. |

## How to extend

1. Search candidates: `apify actors search "linkedin posts" --json --limit 20 2>/dev/null`
2. Fetch the input schema: `apify actors info "johnvc/linkedin-posts-api" --input --json 2>/dev/null`
3. Add a row above with the user intent that should trigger it.

Note: `Tier` here is `community` because these are third-party Actors published by John Cole on the Apify Store, not Apify-maintained Actors.
