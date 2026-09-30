# Lodging judgment inside a whole trip

Read this reference only for the lodging subworkflow of a whole-trip request. Do not use this skill as the entry point for hotel-only or lodging-only work.

## Establish comparable quotes

Use [Google Hotels Search Scraper](https://apify.com/johnvc/google-hotels-search-scraper). Inspect the current README, schema, pricing, and actual payload before a live call or interpretation.

Search the requested dates, occupancy, filters, currency, and location intent. The reviewed schema has no `rooms` input. If the requested room configuration cannot be expressed faithfully, keep it unresolved or use separately labelled searches where that would answer the question.

For every quoted option, retain the stay dates, searched occupancy and room assumptions, currency, nightly or stay-total basis, and whether returned fees are included. Compare only compatible stay scopes. Do not compare a rental stay total directly with a hotel nightly rate. Preserve materially different quote variants; never let name- or property-level deduplication erase a different date, occupancy, room assumption, or price basis.

Reviewed live output used `rate_per_night.extracted_lowest` and `total_rate.extracted_lowest` where the README examples used different paths. Treat this only as observed drift: verify the current payload before choosing numeric fields.

## Interpret missing rates cautiously

A null or absent rate is not zero. It means no rate was returned for the exact request; it does not by itself prove that the property or market is sold out.

Before treating widespread missing rates as a constrained-market signal, verify that the run succeeded, the returned coverage was adequate for the question, dates and occupancy match, and filters were not unreasonably narrow. Then:

1. separate priced properties from `no rate returned`;
2. describe the market only as likely constrained for that searched stay;
3. offer a clearly labelled nearby re-base and explain its transfer trade-off;
4. re-price only when it remains within scope.

## Rank and explain

Recommend a shortlist using total stay cost, location, rating confidence, review volume, relevant amenities, cancellation terms when sourced, and availability. Treat star class as a label rather than a ranking signal. Public cash rates do not establish points availability or program benefits.
