# Actor inputs

Exact input parameters for the three Actors used by this skill.

## 1. compass/crawler-google-places

The one run that does 90% of the work. Set every field in the table below on every run — omitting the add-ons defeats the purpose of the pipeline.

### Search and geography

| Field | Type | Required | Notes |
|---|---|---|---|
| `searchStringsArray` | string[] | yes | Business type(s), e.g. `["dentists"]`. Multiple entries multiply cost — one per audience. |
| `locationQuery` | string | yes | Free text, one location per run. City + country reads best. |
| `maxCrawledPlacesPerSearch` | int | default 50 | Cap per search string. Bigger = more cost. |
| `language` | string | default `"en"` | Result-detail language. |
| `countryCode` | string | optional | ISO 3166 alpha-2, only if you need to override the query. |

### Base scrape flags (always on)

| Field | Value | Why |
|---|---|---|
| `scrapePlaceDetailPage` | `true` | Needed for `phone`, `address`, `openingHours`, `website`. |
| `skipClosedPlaces` | `true` | Permanent/temporary closures are dead leads. |

### Add-on: Company contacts enrichment

| Field | Value | Notes |
|---|---|---|
| `scrapeContacts` | `true` | **⏩ Add-on: Company contacts enrichment (from website) ($)** — scrapes the business website for emails, phones, social links. |

### Add-on: Social media profile enrichment

| Field | Value | Notes |
|---|---|---|
| `scrapeSocialMediaProfiles` | object below | **🔍 Add-on: Social media profile enrichment ($)** — enables IG + FB per the user's requested defaults. |

```json
{
  "facebooks": true,
  "instagrams": true,
  "youtubes": false,
  "tiktoks": false,
  "twitters": false
}
```

Enabling any sub-flag auto-enables `scrapeContacts`. Flat-rate cost per enriched profile — the platform mix doesn't change price, so add YouTube/TikTok/X only if the user asks.

### Add-on: Business leads enrichment (the "people" enrichment)

This is what returns names, job titles, emails, phones, and LinkedIn URLs for people at each place.

| Field | Type | Value | Notes |
|---|---|---|---|
| `maximumLeadsEnrichmentRecords` | int | default 3 | Leads returned **per place**. Multiplier: `50 places × 3 leads = 150 lead attempts`. Never `0`. |
| `leadsEnrichmentDepartments` | string[] | default `[]` | Enum values below. Empty = any department. |
| `verifyLeadsEnrichmentEmails` | bool | `true` | Always. Never `false`. Adds `emailVerification.result` and `.quality`. |

Enum values for `leadsEnrichmentDepartments`:

```
c_suite, product, engineering_technical, design, education,
finance, human_resources, information_technology, legal,
marketing, medical_health, operations, sales, consulting
```

Big-chain leads are excluded server-side (McDonald's, Starbucks, Domino's, Pizza Hut, Burger King, KFC, Subway, Wendy's, Dunkin', Taco Bell) — they're not "local".

### Add-on: Reviews (only when scoring is on)

| Field | Type | Value | Notes |
|---|---|---|---|
| `maxReviews` | int | `10` when scoring on, `0` otherwise | Extract N reviews per place. |
| `reviewsSort` | string | `"newest"` | Recent reviews matter more for freshness. |
| `reviewsOrigin` | string | `"all"` | Include Tripadvisor etc. — better signal. |

If the user wants **server-side** rating pre-filter (cheaper — skips low-star places before enrichment), set:

| Field | Type | Value |
|---|---|---|
| `placeMinimumStars` | string | one of `"three"`, `"threeAndHalf"`, `"four"`, `"fourAndHalf"` |

Use client-side scoring for anything more nuanced (review count thresholds, weighted formulas).

### Full example payload — "dentists in Berlin, scoring on"

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

## 2. apify/ai-web-scraper (name discovery fallback)

Call **per place** in Step 5, only when Google Maps enrichment came back without a usable person name and the place has a working website.

| Field | Type | Required | Notes |
|---|---|---|---|
| `startUrls` | object[] | yes | One URL per call — the business website. Do not batch multiple business sites in one call. |
| `extractionMode` | string | default `"agentic"` | `"agentic"` lets the LLM navigate the site; `"single-page"` restricts to `startUrls` only. Agentic is what handles /about, /team, etc. |
| `prompt` | string | yes | Natural-language description of what to extract. |
| `maxPagesToVisit` | int | default `20` | Per start URL. Small-business sites are shallow; the blog example uses `100` — for lead-gen you rarely need more than 20. |
| `maxCrawlDepth` | int | default `3` | Link hops from `startUrls`. |

### Payload — retargeted from the "list of writers" example

Same shape as the [Apify AI Web Scraper "get a list of writer for any blog" example](https://apify.com/apify/ai-web-scraper/examples/get-a-list-of-writer-for-any-blog); only the prompt and crawl caps change:

```json
{
  "startUrls": [{"url": "https://example-dental.de/"}],
  "extractionMode": "agentic",
  "prompt": "Find the owner, founder, or key decision-makers of this business. For each person, include their full name and job title. Prioritize pages like /about, /team, /contact, or the site footer.",
  "maxPagesToVisit": 20,
  "maxCrawlDepth": 3
}
```

### Prompt variants

Pick the phrasing that matches the vertical when the default underperforms:

| Vertical | Prompt override |
|---|---|
| Restaurants, cafés, bars | `Find the owner, chef, or general manager. Include full name and role.` |
| Agencies, professional services (blog-heavy sites) | `Find writer profiles. For each writer, include the name and title.` — the original blog example, useful when the "decision maker" is the content author |
| Medical / dental / legal practices | `Find the practice owner or senior practitioner. Include full name and title.` |
| Retail / e-commerce | `Find the founder or CEO. Include full name and role.` |

### Output shape

Each dataset row has `url`, `data`, `markdown`. `data` is the LLM's structured extraction — schema varies with the prompt, but expect either an array of people or a `{ "people": [...] }` object. Handle both shapes when merging results.

### Cost / coverage notes

- Priced per crawled page — `maxPagesToVisit × pages_actually_visited`. Keep the caps low; the LLM decides when to stop before hitting them.
- Coverage is best when the site has real "about"/"team" pages; single-page landing sites often yield nothing.
- Falls back to a description-only prompt if omitted — don't leave `prompt` blank.

## 3. scalelist/phone-finder

Call **after** Step 4 with the leads that are still missing a phone.

| Field | Type | Required | Notes |
|---|---|---|---|
| `leads` | object[] | yes | Batch of leads to look up. |

Each lead needs **one** of:
- `linkedin_profile_url` alone (sufficient), or
- `first_name` + `last_name` (add `company_domain` — preferred — or `company_name` to improve match rate).

Example payload:

```json
{
  "leads": [
    {"linkedin_profile_url": "https://www.linkedin.com/in/example-owner/"},
    {"first_name": "Anna", "last_name": "Schmidt", "company_domain": "example-dental.de"},
    {"first_name": "Marco", "last_name": "Rossi", "company_name": "Studio Rossi"}
  ]
}
```

Pricing is **pay-per-event** — only successful matches are billed.

## 4. scalelist/email-finder

Call **after** Step 4 with the leads that are still missing an email.

| Field | Type | Required | Notes |
|---|---|---|---|
| `leads` | object[] | yes | Batch of leads to look up. |

Each lead needs `first_name` + `last_name` (both required). Add `company_domain` (preferred) or `company_name` for match rate.

Example payload:

```json
{
  "leads": [
    {"first_name": "Anna", "last_name": "Schmidt", "company_domain": "example-dental.de"},
    {"first_name": "Marco", "last_name": "Rossi", "company_name": "Studio Rossi"}
  ]
}
```

Verification is included in the output — you don't need to call an external verifier. Pay-per-event pricing.

## Batching guidance

Both scalelist Actors accept large `leads` arrays. Keep batches ≤ 100 leads per call — smaller batches recover faster on transient failures, and the tail-of-cost tradeoff is negligible since you only pay on success.
