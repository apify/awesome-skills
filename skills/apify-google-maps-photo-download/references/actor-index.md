# Actor index: Google Maps Photos API

The primary Actor for this skill, plus the Actors worth chaining for adjacent intents. The agent reads this after `SKILL.md` to pick the right Actor for a specific user intent.

| Platform | User intent | Actor ID | Tier | Notes |
|----------|-------------|----------|------|-------|
| Google Maps Photos API | google maps photo download | `johnvc/google-maps-photos-api` | community | Pay per event: `photo_returned` about $0.0015 per photo, `place_search` about $0.012 per search term, `actor_start` about $0.001 per run. |

## Chain with adjacent Actors

| User intent | Actor ID | Notes |
|-------------|----------|-------|
| Find the places first | `johnvc/google-maps-places-api` | Names, ratings, hours, and the identifiers you can feed straight back in. |
| Reviews for a place | `johnvc/google-maps-contributor-reviews-api` | Review text and ratings by contributor. |
| Routes and drive times | `johnvc/google-maps-directions-api` | Point to point, with distance and duration. |
| Hotel imagery and reviews | `johnvc/google-hotels-search-scraper` | Hotel search including photos. |
| Same places, second source | `johnvc/apple-maps-api` | Apple Maps place data for cross-checking. |

## How to extend

1. Fetch the input schema: `apify actors info "johnvc/google-maps-photos-api" --input --json --user-agent apify-awesome-skills/apify-google-maps-photo-download 2>/dev/null`
2. Add a row above with the user intent that should trigger it.

Note: `Tier` here is `community` because these are third-party Actors published by John Cole on the Apify Store, not Apify-maintained Actors.
