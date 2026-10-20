# Actor index — travel & e-commerce prices

All Actors: pay per result, no login, no personal data, one flat row per result with stable columns. Built by the skill's author.

| Actor | Main input | Typical output columns |
|-------|------------|------------------------|
| `myth84/airbnb-listings-scraper` | `location` or `locations` (list), `checkIn`, `checkOut`, `adults`, `currency`, `maxResults` (per destination) | title, url, pricePerNight, priceTotal, currency, rating, reviewCount, roomType, coordinates |
| `myth84/airbnb-listing-details-scraper` | `listingUrls`, `includeCalendar`, `calendarMonths` | description, amenities, house rules, six category ratings, review count, availability calendar |
| `myth84/booking-hotels-scraper` | `location` (or `destId`) or `startUrls` (search URLs), `checkIn`/`checkOut` or `checkInDaysFromNow` + `nights`, `adults`, `rooms`, `currency`, `filters` | name, url, total price for the stay, taxes, review score, review count, stars, type, coordinates |
| `myth84/expedia-hotels-scraper` | `location`, `checkIn`/`checkOut` or `checkInDaysFromNow` + `nights`, `adults`, `currency`, `sortBy` | name, url, pricePerNight, priceTotal, guest rating, review count, neighbourhood |
| `myth84/aliexpress-search-scraper` | `searchQueries`, `country`, `currency`, `sortBy`, `priceMin`/`priceMax`, `minSold`, `minRating` | title, url, price, original price, discount, units sold, rating, ship-from, free shipping |
| `myth84/ebay-search-scraper` | `searchQueries`, `marketplace` (US, UK, DE, FR, IT, ES, NL, CA, AU), `condition`, `buyingFormat`, `sortBy` | title, url, price, shipping, condition, sold count, rating |
| `myth84/etsy-search-scraper` | `searchQueries`, `locale` (USD, EUR, GBP), `priceMin`/`priceMax`, `freeShippingOnly` | title, url, price, sale price, discount, rating, review count |
