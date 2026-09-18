# Actor index: hotel points value

The primary Actor for this skill and the travel-data Actors worth chaining. Read this after `SKILL.md` to route a need to the right Actor.

| Platform | User intent | Actor ID | Tier | Notes |
|----------|-------------|----------|------|-------|
| Google Hotels | Live cash rate for a property and date, to divide by the award points cost | `johnvc/google-hotels-search-scraper` | community | Pay per page. Returns per property `rate_per_night`/`total_rate` with numeric `extracted_lowest`, `overall_rating`, `link`, `property_token`. The skill computes cents per point on the cash rate; the Actor does not return points or award pricing. |

## Chain with other travel-data Actors

| User intent | Actor ID | Notes |
|-------------|----------|-------|
| Watch a redemption over time and alert on a good deal | `johnvc/google-hotels-search-scraper` | Same Actor on an Apify schedule. See the `apify-hotel-points-deal-tracker` skill. |
| Price the whole trip, flights and lodging | `johnvc/Google-Flights-Data-Scraper-Flight-and-Price-Search` and `johnvc/google-hotels-search-scraper` | See the `apify-plan-a-trip` skill. |

## How to extend

1. Search candidates: `apify actors search "google hotels" --json --limit 20 2>/dev/null`
2. Fetch the input schema: `apify actors info "johnvc/google-hotels-search-scraper" --input --json 2>/dev/null`
3. Add a row above with the user intent that should trigger it.

Note: `Tier` here is `community` because these are third-party Actors published by John Cole on the Apify Store, not Apify-maintained Actors.
