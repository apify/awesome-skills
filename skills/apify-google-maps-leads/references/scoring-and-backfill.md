# Scoring and backfill logic

Everything that happens between the raw Google Maps dataset and the final CSV.

## Data shape reminder

The `compass/crawler-google-places` dataset returns one object per place. Fields used by this skill:

| Path | Meaning |
|---|---|
| `title` | Business name |
| `placeId` | Google's stable ID for the place |
| `website` | Business website URL (source of truth for domain match) |
| `phone` | Place phone (may be missing) |
| `address`, `city`, `countryCode` | Location fields |
| `totalScore` | Average star rating (0–5) |
| `reviewsCount` | Total reviews on Google |
| `categories` | Category tags |
| `instagrams`, `facebooks` | Objects with `followerCount`, `verified`, etc. — populated when the social enrichment matched |
| `leadsEnrichment[]` | Array of people at the place |

Each `leadsEnrichment[]` item has:

| Path | Meaning |
|---|---|
| `firstName`, `lastName`, `fullName` | Person name |
| `jobTitle`, `seniority`, `departments[]` | Role fields |
| `email` | Business email (may be blank) |
| `emailVerification.result` | `ok` / `invalid` / `disposable` / `catch_all` / `unknown` / `error` |
| `emailVerification.quality` | `good` / `risky` / `bad` |
| `phoneNumber` or `companyPhoneNumber` | Person phone or company phone (may be blank) |
| `linkedinProfile` | Full LinkedIn URL |
| `companyWebsite` | The domain the enrichment service matched — cross-check against `place.website` |
| `companyName` | Company name as the enrichment service knows it |

## Pipeline order — do not reorder

```
1. Spurious-match filter (always on)
2. Review-based score + threshold (only if scoring enabled)
3. Name discovery via apify/ai-web-scraper (only for places with no named leads)
4. Phone backfill via scalelist/phone-finder
5. Email backfill via scalelist/email-finder
6. Empty-lead surfacing (still empty after all discovery → keep one row per place)
7. Dedupe + sort + render CSV
```

Filtering **before** any discovery/backfill saves paid calls — you don't want to spend on places that will be dropped by the score. Name discovery **before** contact backfill is mandatory: scalelist needs names to look anything up.

## 1. Spurious-match filter (mandatory)

Same failure mode documented in `apify-verified-email-finder`. When a place has no real LinkedIn footprint, the enrichment service sometimes returns global-fallback leads that share a substring with the place's category (e.g., a US zoo CFO attached to unrelated Polish zoos).

**Row-keep logic:** for each `leadsEnrichment[]` item, extract hostnames from `place.website` and `leadsEnrichment[].companyWebsite`:

- Strip `https?://` and leading `www.`.
- Strip anything after the first `/`.
- Lowercase.

Keep the lead only if **both** hostnames are non-empty **and** equal. Drop otherwise. Count drops in `run_metadata.json.stats.spuriousDropped`.

## 2. Review-based score

Only runs when the user said "yes" to lead scoring in Step 1.

**Default threshold** (Step 4 keep-logic):

```
place.reviewsCount >= 10  AND  place.totalScore >= 4.0
```

Drop places that don't meet both. Ask the user before running if they want tighter/looser thresholds.

**Score formula** — emitted in the `Lead Score` column:

```
Lead Score = round(place.totalScore * log10(place.reviewsCount + 1), 2)
```

Rationale: pure `totalScore` ignores popularity — a 5.0 with 3 reviews shouldn't outrank a 4.6 with 400. `log10(reviewsCount + 1)` compresses the review-count difference so a 500-review vs. 5000-review gap doesn't dominate the score. `+1` protects against `log(0)`.

Interpretation cheat sheet:

| reviewsCount | totalScore | Lead Score |
|---|---|---|
| 3 | 5.0 | 3.01 |
| 25 | 4.4 | 6.24 |
| 100 | 4.6 | 9.29 |
| 500 | 4.6 | 12.45 |
| 5000 | 4.6 | 17.05 |

Higher = better local reputation. Sort the final CSV by this column descending.

If scoring is off, leave the `Lead Score` column blank on every row (keep the column so the schema is stable across runs).

## 3. Name discovery — apify/ai-web-scraper

Scalelist requires a first + last name (or LinkedIn URL) — there's no way to look up contacts for an anonymous business. If Google Maps enrichment gave us a place but no named lead, run `apify/ai-web-scraper` on the business website before touching scalelist.

**Trigger per place** (all must hold):

- `place.website` is non-empty
- Either `leadsEnrichment[]` is empty **or** every existing lead has blank `firstName`
- The place survived Steps 1–2 (spurious-match + score)

**Call shape** (see [actor-inputs.md](actor-inputs.md#2-apifyai-web-scraper-name-discovery-fallback) for the full payload):

```json
{
  "startUrls": [{"url": "<place.website>"}],
  "extractionMode": "agentic",
  "prompt": "Find the owner, founder, or key decision-makers of this business. For each person, include their full name and job title. Prioritize pages like /about, /team, /contact, or the site footer.",
  "maxPagesToVisit": 20,
  "maxCrawlDepth": 3
}
```

**One call per place website.** The Actor crawls from `startUrls`; batching multiple business sites in one call would mix their outputs. Parallelize across places to speed things up.

**Merge results back:**

- Read the dataset. Each row has `data` — the LLM's structured extraction. Expect one of these shapes:
  - `[{"name": "...", "jobTitle": "..."}, ...]`
  - `{"people": [{"name": "...", "jobTitle": "..."}, ...]}`
  - `{"owner": "...", "role": "..."}` (single-person sites)
  - Handle all three; wrap single-object outputs in a one-element array.
- Split `name` on the last space → `firstName` = everything before, `lastName` = last token. Handle single-name entries (e.g., mononym-only Instagram-style names) by leaving `firstName` blank and using the token as `lastName`.
- Append new leads to `place.leadsEnrichment[]` with:
  - `firstName`, `lastName`, `jobTitle` from the LLM output
  - `companyWebsite = place.website`
  - `companyName = place.title`
  - `email`, `phoneNumber`, `linkedinProfile` all blank — subsequent scalelist steps will try to fill them
- Cap at 3 new leads per place. LLM extractions occasionally return past employees, testimonial subjects, or blog-post authors; the cap keeps noise bounded.
- Set `Backfill Source = "ai-web-scraper"` for these leads (subsequent scalelist backfills will append `+scalelist-phone` / `+scalelist-email` as those fire).

**Skip conditions:**

- User opted out of name discovery in Step 1 (offer this as a cost-saver on large runs — this is the priciest step per place).
- `place.website` redirects to a social network (Facebook / Instagram) — those need auth walls that the scraper can't cross; the call would burn budget for nothing.
- The Actor previously returned zero people for this domain in the current session — cache the miss and skip retries within one run.

## 4. Phone backfill — scalelist/phone-finder

Collect every surviving lead where:

- `phoneNumber` is blank **AND** `companyPhoneNumber` is blank
- **AND** the lead has a usable identifier: `linkedinProfile` OR (`firstName` + `lastName`)

Map each to a scalelist input object:

```javascript
{
  linkedin_profile_url: lead.linkedinProfile || undefined,
  first_name: lead.firstName || undefined,
  last_name: lead.lastName || undefined,
  company_domain: hostname(place.website) || undefined,
  company_name: place.title || undefined
}
```

Batch into groups of 100. Call `scalelist/phone-finder` per batch. Merge results back onto the original lead by (case-insensitive) `first_name + last_name + company_domain`, or by `linkedin_profile_url` when that's what you sent.

Fill the lead's `phoneNumber` from the scalelist response. Set the `Backfill Source` column to `"scalelist-phone"` for any row that got its phone this way.

## 5. Email backfill — scalelist/email-finder

Collect every surviving lead where:

- `email` is blank **OR** `emailVerification.result == "invalid"`
- **AND** the lead has `firstName` + `lastName` (both required)

Map each to a scalelist input object:

```javascript
{
  first_name: lead.firstName,
  last_name: lead.lastName,
  company_domain: hostname(place.website) || undefined,
  company_name: place.title
}
```

Batch (≤ 100), call `scalelist/email-finder`, merge back. The Actor returns verification data — carry it into the `Email Verification Status` and `Email Verification Quality` columns. If the row already had an `emailVerification` from Google Maps enrichment, prefer the newer scalelist verification only when the old one was `invalid` or blank.

Set `Backfill Source` to `"scalelist-email"` (or `"scalelist-phone+email"` if both fired for the same row). If the lead was created by `ai-web-scraper` in Step 3, use `"ai-web-scraper+scalelist-email"`, etc.

## 6. Empty-lead surfacing

Only reached after all three enrichment sources (Google Maps → AI web scraper → scalelist) failed to attach a person. Keep **one** row for the place with:

- Business fields populated
- Person fields blank
- `Lead Status` column set to `"no-leads-found"`

Never silently drop a place — the user needs to see which businesses had no reachable contacts.

## 7. Dedupe and sort

**Dedupe key:**
- If the lead has an `email`, lowercase it → dedupe key is the email.
- Otherwise, dedupe by `lowercase(first_name) + "|" + lowercase(last_name) + "|" + place_id`.

**Sort:**
- Scoring on → sort by `Lead Score` descending, then `Business` ascending.
- Scoring off → sort by `Business` ascending, then `Full Name` ascending.

**Deliverable header** (first non-header line in the CSV, wrapped in a leading `# ` comment or output as a preamble in a wrapping tool):

```
# Google Maps Leads — Berlin, Germany | audience: dentists
# Scoring: ON (min_reviews=10, min_rating=4.0) | spurious drops: 3 | phones backfilled: 12 | emails backfilled: 8
# runId: <id> | datasetId: <id> | scraped: <ISO 8601>
```

If the deliverable format can't carry comments, put the same lines in the `run_metadata.json` sidecar.
