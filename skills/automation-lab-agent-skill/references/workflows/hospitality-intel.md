# Hospitality intelligence workflow

Use when the user asks for hotel, short-term rental, Booking.com, Airbnb, property review, availability, pricing, or guest-experience intelligence.

## Trigger phrases

- "scrape Booking.com listings"
- "get Booking.com reviews"
- "compare Airbnb properties"
- "summarize guest complaints"
- "hotel/rental market analysis"

## Actor routing

| Need | Actor ID |
|---|---|
| Booking.com listing search/details | `automation-lab/booking-scraper` |
| Booking.com guest reviews | `automation-lab/booking-reviews-scraper` |
| Airbnb listings/search/details | `automation-lab/airbnb-listing` |
| Airbnb reviews | `automation-lab/airbnb-reviews` |

## Input schema hints

Fetch schema. Hospitality Actors usually need one of:

- destination/search query
- check-in/check-out dates and guests when availability/pricing matters
- `startUrls`/`urls` for specific properties
- `maxItems`/`maxResults`
- currency, locale, room/property filters when supported

Ask for dates, destination, and result count if the user requests live pricing or availability.

## Example payloads

```bash
apify actors call "automation-lab/booking-scraper" -i '{"query":"Prague hotels","checkIn":"2026-06-15","checkOut":"2026-06-18","maxItems":50}' --user-agent automation-lab-agent-skill --json 2>/dev/null
```

```bash
apify actors call "automation-lab/booking-reviews-scraper" -i '{"startUrls":[{"url":"https://www.booking.com/hotel/example.html"}],"maxItems":200}' --user-agent automation-lab-agent-skill --json 2>/dev/null
```

```bash
apify actors call "automation-lab/airbnb-listing" -i '{"query":"Austin, TX","checkIn":"2026-06-15","checkOut":"2026-06-18","maxItems":50}' --user-agent automation-lab-agent-skill --json 2>/dev/null
```

## Output normalization

Normalize to:

- `sourcePlatform`: `booking` or `airbnb`
- `sourceActor`
- `propertyName`
- `propertyUrl`
- `location`
- `price`
- `currency`
- `rating`
- `reviewCount`
- `amenities`
- `reviewText`, `reviewDate`, `reviewRating` for review Actors

Summaries should separate pricing/availability facts from review sentiment.
