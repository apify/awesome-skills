# Gotchas

- **Dates make travel prices comparable.** Without `checkIn`/`checkOut`, Airbnb shows flexible stays and each listing may be priced for different dates. Booking.com and Expedia accept a relative stay (`checkInDaysFromNow` + `nights`) for schedules.
- **Booking.com destination.** If a text destination is ambiguous, give `destId` (the `dest_id` of a Booking.com search URL) or paste the search URL in `startUrls`.
- **Currency.** Every row carries its currency; ask for one currency per run and never sum across currencies.
- **Cost guardrail.** Paid per result: start with `maxResults` 20–50, then scale. In tracking mode with `onlyChanges` / `onlyPriceDrops`, unchanged products are not charged.
- **Tracking needs the same input.** The monitor compares runs of the same search (same keywords or URL, country, currency, filters). Change the input and a new reference is created.
- **No personal data.** Host, seller or reviewer identities are never returned; do not promise them to the user.
