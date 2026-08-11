# Output format

One row per lead (person) in the final CSV, plus place-only rows for businesses where no lead was found (see `Lead Status`).

## Column schema (20 columns)

| # | Column | Source |
|---|---|---|
| 1 | `Source Query` | The `searchStringsArray` entry that produced this place |
| 2 | `Business` | `place.title` |
| 3 | `Categories` | `place.categories` joined with `\|` |
| 4 | `Place ID` | `place.placeId` |
| 5 | `Business Website` | `place.website` |
| 6 | `Business Phone` | `place.phone` (blank if missing) |
| 7 | `Business Address` | `place.address` |
| 8 | `City` | `place.city` |
| 9 | `Country` | `place.countryCode` |
| 10 | `Reviews Count` | `place.reviewsCount` |
| 11 | `Rating` | `place.totalScore` |
| 12 | `Lead Score` | Computed (see scoring-and-backfill.md); blank if scoring off |
| 13 | `Full Name` | `leadsEnrichment[].fullName` |
| 14 | `Job Title` | `leadsEnrichment[].jobTitle` |
| 15 | `Departments` | `leadsEnrichment[].departments` joined with `\|` |
| 16 | `Email` | `leadsEnrichment[].email` (or scalelist backfill) |
| 17 | `Email Verification Status` | `leadsEnrichment[].emailVerification.result` (or scalelist status) |
| 18 | `Phone` | `leadsEnrichment[].phoneNumber` \|\| `.companyPhoneNumber` (or scalelist backfill) |
| 19 | `LinkedIn` | `leadsEnrichment[].linkedinProfile` |
| 20 | `Instagram Followers` | `place.instagrams.followerCount` (blank if not enriched) |
| 21 | `Facebook Followers` | `place.facebooks.followerCount` (blank if not enriched) |
| 22 | `Lead Status` | `"ok"`, `"no-leads-found"`, `"spurious-dropped"` |
| 23 | `Backfill Source` | Blank, or a `+`-joined combination of `"ai-web-scraper"`, `"scalelist-phone"`, `"scalelist-email"` (e.g. `"ai-web-scraper+scalelist-phone+scalelist-email"` for a lead whose name came from the AI scraper and whose phone and email were then filled by scalelist) |
| 24 | `Date Scraped` | Run finish time (ISO 8601) |

(Yes — the count is 24 despite the "20 columns" header; the last four are always-present status/provenance columns that don't come from the raw source. Keep them so downstream consumers get a stable schema.)

## Missing values

Blank string. Never `null`, `"N/A"`, or `"-"`. Never invent a value.

## Metadata sidecar

Always write `run_metadata.json` next to the CSV.

```json
{
  "runId": "abc123",
  "datasetId": "def456",
  "consoleUrl": "https://console.apify.com/actors/runs/abc123",
  "scrapedAt": "2026-08-10T14:32:00Z",
  "input": { "audience": "dentists", "geography": "Berlin, Germany", "scoring": true, "reviewThresholds": {"minReviews": 10, "minRating": 4.0} },
  "stats": {
    "placesScraped": 47,
    "placesKept": 32,
    "rawLeads": 138,
    "spuriousDropped": 3,
    "namesDiscoveredByAiScraper": 9,
    "placesQueriedForNameDiscovery": 14,
    "phonesBackfilled": 12,
    "emailsBackfilled": 8,
    "keptRows": 118
  },
  "actors": {
    "primary": "compass/crawler-google-places",
    "nameDiscovery": "apify/ai-web-scraper",
    "phoneBackfill": "scalelist/phone-finder",
    "emailBackfill": "scalelist/email-finder"
  }
}
```

## Header preamble (CSV only)

Put three `# `-prefixed lines above the header row (some spreadsheet importers skip them automatically; others show them as data — that's fine, it's a legitimate provenance trail):

```
# Google Maps Leads — Berlin, Germany | audience: dentists
# Scoring: ON (min_reviews=10, min_rating=4.0) | spurious drops: 3 | phones backfilled: 12 | emails backfilled: 8
# runId: abc123 | datasetId: def456 | scraped: 2026-08-10T14:32:00Z
Source Query,Business,Categories,...
```

If the tool writing the CSV can't handle preamble lines, put the same information in the header row of a first "notes" row and mark it clearly.
