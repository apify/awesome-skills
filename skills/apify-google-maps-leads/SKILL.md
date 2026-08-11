---
name: apify-google-maps-leads
description: Build a local-business lead database from Google Maps in one Apify pipeline: search by target audience + geography, enrich each place with company contacts from its website, leads enrichment (names, emails, phones, LinkedIn), Instagram + Facebook profiles, and optionally reviews for lead scoring. For places with no named contacts, escalate to apify/ai-web-scraper to pull owner / decision-maker names from the business website. Backfill missing phones via scalelist/phone-finder and missing emails via scalelist/email-finder. Use when the user asks to build a lead list from Google Maps, scrape local businesses, generate B2B leads by city/industry, find owner/decision-maker contacts for restaurants / dentists / gyms / hotels / any local vertical, score leads by review volume or rating, or says "Google Maps lead-gen pipeline", "leads from Maps", "prospect local businesses", "scrape Google Maps for outreach", "find companies in <city>", or mentions chaining Google Maps + AI web scraper + Scalelist Actors.
author: Fabian Maume
author_url: https://github.com/fmaume
---

# Google Maps Leads (with Scalelist backfill)

Build a lead CSV from Google Maps in one pipeline:

1. **Interview** — ask target audience, target geography, and whether to use reviews for lead scoring.
2. **Scrape** — one `compass/crawler-google-places` run with four add-ons pre-configured (leads enrichment, website contacts, Instagram + Facebook profiles, optional reviews).
3. **Filter & score** — apply a review-based score if scoring is on.
4. **Discover missing names** — for places that came back with zero (or unnamed) leads, call `apify/ai-web-scraper` on the business website to extract owner/decision-maker names. Scalelist can't work without a name.
5. **Backfill contacts** — call `scalelist/phone-finder` for leads with a missing phone, `scalelist/email-finder` for leads with a missing email.
6. **Deliver** — a deduplicated CSV plus a `run_metadata.json` sidecar.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Auth via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` env var
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

Either the Apify CLI (recommended for portability) or the Apify MCP connector works. Commands below use the CLI; the MCP path is a drop-in via the `call-actor` and `get-dataset-items` tools.

## Workflow

Track progress with this checklist:

```
Task Progress:
- [ ] Step 1: Interview — audience, geography, scoring choice
- [ ] Step 2: Build the Google Maps input
- [ ] Step 3: Run compass/crawler-google-places
- [ ] Step 4: Filter + score (if scoring enabled)
- [ ] Step 5: Discover missing names via apify/ai-web-scraper
- [ ] Step 6: Backfill missing phones and emails via scalelist Actors
- [ ] Step 7: Deduplicate and render the CSV
```

### Step 1: Interview

Ask three questions **as one block** — don't drip them one by one.

1. **Target audience** — the business type(s) to search for. Free text. Examples: `"dentists"`, `"vegan restaurants"`, `"boutique hotels"`, `"dog groomers, pet stores"` (comma-splittable → array).
2. **Target geography** — one location per run. City + country reads best (`"Berlin, Germany"`, `"Austin, TX"`). If the user gives a country only, warn that Maps runs perform best on city-scoped searches.
3. **Use reviews for lead scoring? (y/n)** — if yes, we pull reviews (`maxReviews`) and filter by review volume + star rating post-run. If no, we skip reviews to cut cost.

Follow-ups only if the user asks for more control:

- `maxCrawledPlacesPerSearch` — default `50`. Bigger runs = bigger cost.
- `maximumLeadsEnrichmentRecords` — default `3` per place (people to enrich per business). Never `0` — that disables leads enrichment, which is the point.
- `leadsEnrichmentDepartments` — default `[]` (any). Enum values are listed in [references/actor-inputs.md](references/actor-inputs.md).
- Minimum star rating pre-filter (`placeMinimumStars`) — cheaper than post-filtering when scoring is off.
- Review-scoring thresholds — default is `≥ 10 reviews AND ≥ 4.0 rating`.

**Cost warning threshold.** Compute `expected_leads = maxCrawledPlacesPerSearch × maximumLeadsEnrichmentRecords`. If it exceeds **200**, restate the number back to the user and confirm before running. Leads enrichment is the dominant cost line; a slip here is what surprises people.

### Step 2: Build the Google Maps input

Set every field below on **every** run. Full field reference in [references/actor-inputs.md](references/actor-inputs.md).

| Field | Value |
|---|---|
| `searchStringsArray` | audience as array (e.g. `["dentists"]`) |
| `locationQuery` | geography free text |
| `maxCrawledPlacesPerSearch` | user override or default `50` |
| `language` | `"en"` unless user specifies |
| `scrapePlaceDetailPage` | `true` — needed for phone + hours + address |
| `skipClosedPlaces` | `true` — permanent/temporary closures are dead leads |
| `scrapeContacts` | `true` — **Add-on: Company contacts enrichment (from website) ($)** |
| `scrapeSocialMediaProfiles` | `{"instagrams": true, "facebooks": true, "youtubes": false, "tiktoks": false, "twitters": false}` — Instagram + Facebook profile enrichment |
| `maximumLeadsEnrichmentRecords` | user override or default `3` — **Add-on: Business leads enrichment ($)** |
| `leadsEnrichmentDepartments` | user override or `[]` |
| `verifyLeadsEnrichmentEmails` | `true` — always, never `false` |
| `maxReviews` | `10` if scoring is on, `0` otherwise |
| `reviewsSort` | `"newest"` if scoring is on |

`scrapeSocialMediaProfiles` auto-enables `scrapeContacts`. Both are billed on top of the base scrape — see the Actor's pricing tab.

### Step 3: Run compass/crawler-google-places

```bash
apify actors call "compass/crawler-google-places" \
  --input '<JSON_FROM_STEP_2>' \
  --user-agent apify-awesome-skills/apify-google-maps-leads \
  --json 2>/dev/null
```

Capture `id` (runId) and `defaultDatasetId`. Pull the dataset:

```bash
apify datasets get-items <DATASET_ID> --format json \
  --user-agent apify-awesome-skills/apify-google-maps-leads 2>/dev/null > places.json
```

Leads enrichment adds 30–90 s per place — expect long runs. If a run times out, the dataset already holds partial results; pull by `datasetId`.

### Step 4: Filter and score

Applied to the raw `places.json` in order. Full logic in [references/scoring-and-backfill.md](references/scoring-and-backfill.md).

1. **Spurious-match filter (always on).** Drop leads whose `leadsEnrichment[].companyWebsite` hostname doesn't match the `place.website` hostname. Same failure mode as `apify-verified-email-finder` — a global-fallback lead attributed to unrelated places by substring. Count drops in `run_metadata.json`.
2. **Review-based score (only if scoring is on).**
   - Default keep-logic: `place.reviewsCount >= 10 AND place.totalScore >= 4.0`.
   - Emit a numeric `Lead Score` column: `round(place.totalScore * log10(place.reviewsCount + 1), 2)`. Higher = better local reputation.
   - If scoring is off, `Lead Score` is blank.
3. **Empty-lead surfacing.** If a place has zero enriched leads, keep one row for the place with blank person fields — the user sees the business but knows nobody was found. Never silently drop.

### Step 5: Discover missing names via apify/ai-web-scraper

Scalelist needs a person name (or LinkedIn URL) to look anything up. When a place has zero enriched leads — or leads with blank `firstName` / `lastName` — but has a working `website`, run `apify/ai-web-scraper` on that website to extract owner/decision-maker names.

**When to run this step per place** (all conditions must hold):

- `place.website` is non-empty (nothing to scrape otherwise)
- Either `leadsEnrichment[]` is empty, or every lead has a blank `firstName`
- The place survived Step 4's scoring filter (don't spend on places we're going to drop)

**Payload** — same input pattern as [the Apify AI Web Scraper "list of writers" example](https://apify.com/apify/ai-web-scraper/examples/get-a-list-of-writer-for-any-blog), retargeted from blog authors to local-business decision-makers:

```json
{
  "startUrls": [{"url": "<place.website>"}],
  "extractionMode": "agentic",
  "prompt": "Find the owner, founder, or key decision-makers of this business. For each person, include their full name and job title. Prioritize pages like /about, /team, /contact, or the site footer.",
  "maxPagesToVisit": 20,
  "maxCrawlDepth": 3
}
```

Defaults trimmed vs. the blog example (which uses `maxPagesToVisit: 100` / `maxCrawlDepth: 5`) — small-business sites are typically shallow, and this is one call per website.

```bash
apify actors call "apify/ai-web-scraper" \
  --input '{"startUrls":[{"url":"<place.website>"}],"extractionMode":"agentic","prompt":"...","maxPagesToVisit":20,"maxCrawlDepth":3}' \
  --user-agent apify-awesome-skills/apify-google-maps-leads \
  --json 2>/dev/null
```

**One place per call** — the Actor's crawl fans out from `startUrls`, so batching multiple business sites in one `startUrls` array would mix results. Run one call per place website. Parallelize across places if you have many.

**Merge results back onto the place:**

- The Actor returns rows with `url`, `data`, `markdown`. `data` holds the extracted people — expect `{ "people": [{ "name": "...", "jobTitle": "..." }] }` or an array of such objects (LLM output shape varies).
- For each extracted person, split `name` on the last space into `firstName` / `lastName`.
- Append a new lead into `place.leadsEnrichment[]` with `firstName`, `lastName`, `jobTitle`, `companyWebsite = place.website`, and mark `Backfill Source = "ai-web-scraper"`.
- Cap at 3 new leads per place — the Actor sometimes returns lots of tangential names (past employees, testimonial subjects).

**Skip conditions:**

- Skip entirely if the user opts out of name discovery up front (offer this as a follow-up when running large batches — this is the priciest step per place).
- Skip if `place.website` returns a redirect to a social profile (Facebook page, Instagram) — the AI scraper handles JS sites but Meta login walls will burn budget for nothing.

### Step 6: Backfill missing contacts

For every lead surviving Step 5, check what's missing.

**Phone backfill.** Collect leads with a non-blank name and a blank phone. Group into batches of 100. Payload for `scalelist/phone-finder`:

```json
{
  "leads": [
    {"first_name": "...", "last_name": "...", "company_domain": "...", "linkedin_profile_url": "..."}
  ]
}
```

`linkedin_profile_url` alone is sufficient; otherwise supply `first_name + last_name + company_domain` (preferred) or `company_name`.

```bash
apify actors call "scalelist/phone-finder" \
  --input '{"leads":[...]}' \
  --user-agent apify-awesome-skills/apify-google-maps-leads \
  --json 2>/dev/null
```

**Email backfill.** Collect leads with a non-blank name and a blank email. Payload for `scalelist/email-finder`:

```json
{
  "leads": [
    {"first_name": "...", "last_name": "...", "company_domain": "...", "company_name": "..."}
  ]
}
```

`first_name + last_name` are required; `company_domain` beats `company_name` for match rate.

```bash
apify actors call "scalelist/email-finder" \
  --input '{"leads":[...]}' \
  --user-agent apify-awesome-skills/apify-google-maps-leads \
  --json 2>/dev/null
```

Both Actors are pay-per-event: you're only charged for successful matches. Merge the returned phones/emails back onto the original leads by lowercased `first_name + last_name + company_domain`.

**Skip conditions.** Don't call scalelist if the lead has no first+last name AND no LinkedIn URL — nothing to look up. Don't call it if the user says "skip backfill" up front (surface this as an offer if the initial `maximumLeadsEnrichmentRecords` was high, since the cost stacks).

### Step 7: Deduplicate and render the CSV

Full column schema in [references/output-format.md](references/output-format.md). Twenty columns including `Lead Score`, `Instagram Followers`, `Facebook Followers`, `Backfill Source`.

- Dedupe by lowercased `email` where present; otherwise by lowercased `first_name + last_name + place_id`.
- Sort by `Lead Score` descending when scoring is on; otherwise by `Business` alphabetically.
- Deliverable header: state whether scoring was on, the review thresholds, and the spurious-match drop count. Offer to re-render without scoring if the kept-row count is low.
- Write a `run_metadata.json` sidecar next to the CSV with `runId`, `datasetId`, and stats (`placesScraped`, `rawLeads`, `spuriousDropped`, `phonesBackfilled`, `emailsBackfilled`, `keptRows`).

## Worked example

See [examples/example-dentists-berlin.md](examples/example-dentists-berlin.md) — full inputs + sample CSV rows for a "dentists in Berlin, Germany, scoring on" run.

## Quality rules (always enforce)

- **Guard rails:** `verifyLeadsEnrichmentEmails: true` and `skipClosedPlaces: true` on every run.
- **Provenance:** every row carries `Source Query`, `Business`, and `Place ID`. `run_metadata.json` carries the Apify `runId` + `datasetId`.
- **No fabrication:** missing fields stay blank. Never invent an email or phone.
- **Cost transparency:** if `expected_leads > 200`, restate and confirm before running Step 3.
- **Scoring is optional.** If the user said no to scoring, keep the `Lead Score` column but leave it blank — don't invent one.

## Troubleshooting

- **`Run TIMED-OUT`** — Lower `maxCrawledPlacesPerSearch` or `maximumLeadsEnrichmentRecords`. Enrichment is the slow part.
- **All leads dropped by spurious-match** — The enrichment service returned only global-fallback leads. Real fix: none. Surface the count.
- **Zero backfilled phones/emails** — Scalelist needs a person name **and** a company domain (or LinkedIn URL). If leads came back without domains, backfill has nothing to work with. Check `place.website` was populated. If names are also missing, Step 5 (ai-web-scraper) should have populated them — check its output.
- **`apify/ai-web-scraper` returned zero people** — Site is a single-page landing (no /about /team /contact), a JS-app that renders after the crawl budget, or a redirect to Facebook/Instagram. No fix; accept the miss and let scalelist skip that place.
- **Instagram / Facebook fields blank** — The place's website didn't link to those profiles, so nothing to enrich. Not an error.
- **`Actor not found: scalelist/phone-finder`** — The Actor is on the Apify Store but not pre-approved on your account. Open it once in the console to accept the terms.
- **Cost surprise** — Pull the breakdown from the console. Usual culprits: `maxReviews > 10` combined with high `maxCrawledPlacesPerSearch`, or forgetting to disable YouTube/TikTok/X social enrichment (they cost the same as IG/FB).

For error recovery patterns shared across Apify skills, see [references/gotchas.md](references/gotchas.md).
