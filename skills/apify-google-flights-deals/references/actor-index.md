# Actor index: Google Flights Deals API

The primary Actor for this skill, plus the Actors worth chaining for adjacent intents. The agent reads this after `SKILL.md` to pick the right Actor for a specific user intent.

| Platform | User intent | Actor ID | Tier | Notes |
|----------|-------------|----------|------|-------|
| Google Flights Deals API | google flights deals | `johnvc/google-flights-deals-api` | community | Pay per event: `deal_returned` about $0.0025 per destination, `actor_start` about $0.001 per run. |

## Chain with adjacent Actors

| User intent | Actor ID | Notes |
|-------------|----------|-------|
| Price a chosen route | `johnvc/Google-Flights-Data-Scraper-Flight-and-Price-Search` | Point to point search when the destination is known. |
| Destination ideas with hotels | `johnvc/google-travel-explore-api` | Inspiration including nightly hotel prices. |
| Hotels at the destination | `johnvc/google-hotels-search-scraper` | Hotel search, photos, and reviews. |
| Imagery of where you land | `johnvc/google-maps-photos-api` | Real photos for places at the destination. |

## How to extend

1. Fetch the input schema: `apify actors info "johnvc/google-flights-deals-api" --input --json --user-agent apify-awesome-skills/apify-google-flights-deals 2>/dev/null`
2. Add a row above with the user intent that should trigger it.

Note: `Tier` here is `community` because these are third-party Actors published by John Cole on the Apify Store, not Apify-maintained Actors.
