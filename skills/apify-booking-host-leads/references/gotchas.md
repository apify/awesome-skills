# Gotchas & cost notes

## Coverage expectations
- `traderInfo.email` is present for roughly **80%** of independent apartments / guest houses / holiday homes. Big branded hotels often have **no** `traderInfo` (the brand, not a trader, owns the listing) - those are usually not the lead you want anyway.
- The Google Maps fallback adds only a small fraction of extra emails and often matches the wrong place. Enable it only when the user explicitly wants socials or maximum coverage.

## Cost control
- `voyager/booking-scraper` cost scales with `maxItems`. Start at 25-50 to validate, then scale.
- The Google Maps fallback is the expensive step (one place crawl per property). Skipping it cuts most of the cost while keeping ~80% email coverage.
- Set `onlyWithEmail` (or filter downstream) if you only want actionable rows.

## Data quality
- Drop OTA domains from `website` (booking.com, agoda, expedia, decolar, hotels.com, tripadvisor, airbnb, vrbo, trip.com). They are listing pages, not host sites.
- `managedProperties` from `hostInfo` is a strong operator-size signal - sort by it to prioritize professional property managers over one-off hosts.
- `traderInfo` emails are business-disclosure data. Respect GDPR / local rules and the recipient's lawful-basis / opt-out requirements before outreach.

## Matching
- Join Booking and Google Maps rows on a normalized `name + ", " + destination` string (lowercase, collapse whitespace). Google Maps echoes the input as `searchString`; also try matching its `title`.
