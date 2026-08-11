# Example — dentists in Berlin, Germany (scoring on)

Full walk-through of a real invocation. Numbers here are illustrative — actual counts depend on the day.

## Step 1 — Interview

| Question | Answer |
|---|---|
| Target audience | `dentists` |
| Target geography | `Berlin, Germany` |
| Reviews for lead scoring? | `yes` (min 10 reviews, min 4.0 stars — default) |

Follow-up defaults: `maxCrawledPlacesPerSearch=50`, `maximumLeadsEnrichmentRecords=3`, `leadsEnrichmentDepartments=[]`.

Expected leads = `50 × 3 = 150` — under the 200 threshold, no confirmation needed.

## Step 2 — Actor input

```json
{
  "searchStringsArray": ["dentists"],
  "locationQuery": "Berlin, Germany",
  "maxCrawledPlacesPerSearch": 50,
  "language": "en",
  "scrapePlaceDetailPage": true,
  "skipClosedPlaces": true,
  "scrapeContacts": true,
  "scrapeSocialMediaProfiles": {
    "facebooks": true,
    "instagrams": true,
    "youtubes": false,
    "tiktoks": false,
    "twitters": false
  },
  "maximumLeadsEnrichmentRecords": 3,
  "leadsEnrichmentDepartments": [],
  "verifyLeadsEnrichmentEmails": true,
  "maxReviews": 10,
  "reviewsSort": "newest",
  "reviewsOrigin": "all"
}
```

## Step 3 — Run

```bash
apify actors call "compass/crawler-google-places" \
  --input @input.json \
  --user-agent apify-awesome-skills/apify-google-maps-leads \
  --json 2>/dev/null
```

Returned: `id=abc123`, `defaultDatasetId=def456`. Pull items:

```bash
apify datasets get-items def456 --format json \
  --user-agent apify-awesome-skills/apify-google-maps-leads 2>/dev/null > places.json
```

## Step 4 — Filter + score

- Places scraped: `47` (three deduped by Google)
- Spurious matches dropped: `3`
- Places passing `reviewsCount >= 10 AND totalScore >= 4.0`: `32`
- Raw surviving leads: `88`

## Step 5 — Name discovery

- Places with 0 named leads after Google Maps enrichment: `14`
- `apify/ai-web-scraper` called once per place (14 calls)
- Names discovered: `9` places yielded at least one owner/manager name (mostly from `/about` or `/team` pages)
- Placeholder input:

```json
{
  "startUrls": [{"url": "https://example-dental-c.de/"}],
  "extractionMode": "agentic",
  "prompt": "Find the owner, founder, or key decision-makers of this business. For each person, include their full name and job title. Prioritize pages like /about, /team, /contact, or the site footer.",
  "maxPagesToVisit": 20,
  "maxCrawlDepth": 3
}
```

## Step 6 — Contact backfill

- Leads missing phone: `36` (27 from Google Maps + 9 new from ai-web-scraper) → `scalelist/phone-finder` returned `15` matches
- Leads missing email (or `emailVerification.result == "invalid"`): `28` → `scalelist/email-finder` returned `11` matches

## Step 7 — Deliverable

`leads.csv` — 118 rows total after empty-lead surfacing (some places kept a `no-leads-found` row). Top 3 rows by `Lead Score`:

| Business | Reviews | Rating | Lead Score | Full Name | Job Title | Email | Phone | Backfill |
|---|---|---|---|---|---|---|---|---|
| Example Dental A | 412 | 4.8 | 12.53 | Anna Schmidt | Owner | anna@example-dental-a.de | +49 30 5550001 | |
| Example Dental A | 412 | 4.8 | 12.53 | Marco Weber | Practice Manager | marco@example-dental-a.de | +49 30 5550002 | scalelist-phone |
| Example Dental B | 287 | 4.7 | 11.55 | Julia König | CEO | julia@example-dental-b.de | +49 30 5550010 | |
| Example Dental C | 156 | 4.5 | 9.87 | Peter Müller | Practice Owner | peter@example-dental-c.de | +49 30 5550020 | ai-web-scraper+scalelist-phone+scalelist-email |

Header preamble:

```
# Google Maps Leads — Berlin, Germany | audience: dentists
# Scoring: ON (min_reviews=10, min_rating=4.0) | spurious drops: 3 | phones backfilled: 12 | emails backfilled: 8
# runId: abc123 | datasetId: def456 | scraped: 2026-08-10T14:32:00Z
```

Sidecar `run_metadata.json` written alongside the CSV.
