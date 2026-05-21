# Apify Actor Usage

Exact input parameters per Actor. Every payload includes the three shared add-on fields:

| Field | Value | Notes |
|---|---|---|
| `maximumLeadsEnrichmentRecords` | anchor #4 (default 3, min 1) | `0` disables enrichment — never use. |
| `leadsEnrichmentDepartments` | anchor #3 as array, or `[]` for any | Enum: `c_suite`, `product`, `engineering_technical`, `design`, `education`, `finance`, `human_resources`, `information_technology`, `legal`, `marketing`, `medical_health`, `operations`, `sales`, `consulting`. |
| `verifyLeadsEnrichmentEmails` | `true` always | **Guard rail.** Adds `emailVerification` per lead. Never `false`. |

## 1. Google Maps — `compass/crawler-google-places`

Anchor #1 is a location + business type.

| Field | Type | Required? | Notes |
|---|---|---|---|
| `searchStringsArray` | string[] | yes | Business type(s), e.g. `["dentists"]`. |
| `locationQuery` | string | yes | Free-form location, e.g. `"Berlin, Germany"`. |
| `maxCrawledPlacesPerSearch` | int | optional, default 20 | Places per search string. |
| `language` | string | optional | UI language, e.g. `"en"`. |
| `countryCode` | string | optional | ISO 3166 alpha-2. |
| `city`, `state`, `postalCode` | string | optional | Narrower filters. |
| `scrapePlaceDetailPage` | bool | optional, default `false` | Set `true` for address / hours / phone. |
| `skipClosedPlaces` | bool | optional, default `false` | Drop permanently-closed listings. |

Example:
```json
{
  "searchStringsArray": ["dentists"],
  "locationQuery": "Berlin, Germany",
  "maxCrawledPlacesPerSearch": 20,
  "language": "en",
  "scrapePlaceDetailPage": true,
  "maximumLeadsEnrichmentRecords": 3,
  "leadsEnrichmentDepartments": ["marketing", "c_suite"],
  "verifyLeadsEnrichmentEmails": true
}
```

## 2. Google Search — `apify/google-search-scraper`

Anchor #1 is a keyword.

| Field | Type | Required? | Notes |
|---|---|---|---|
| `queries` | string | yes | Newline-separated queries, each ≤ 32 words. |
| `maxPagesPerQuery` | int | optional, default 1 | Each page ≈ 10 results. |
| `countryCode` | string | optional, default `"us"` | Drives the `google.xx` domain. |
| `languageCode` | string | optional | UI language. |
| `searchLanguage` | string | optional | `lr` filter — restricts result-page language. |
| `mobileResults` | bool | optional, default `false` | Mobile SERP. |

Example:
```json
{
  "queries": "best CRM software",
  "maxPagesPerQuery": 1,
  "countryCode": "us",
  "languageCode": "en",
  "maximumLeadsEnrichmentRecords": 3,
  "leadsEnrichmentDepartments": ["sales"],
  "verifyLeadsEnrichmentEmails": true
}
```

## 3. URL list — `vdrmota/contact-info-scraper`

Anchor #1 is a pre-existing URL list.

| Field | Type | Required? | Notes |
|---|---|---|---|
| `startUrls` | object[] | yes | `[{"url": "https://..."}, ...]`. Pre-validate as http/https; emit a `skipped — invalid URL` row for each rejection. |
| `proxyConfig` | object | yes | Default `{"useApifyProxy": true}` works for most. |
| `maxRequestsPerStartUrl` | int | optional, default 20 | Pages crawled per start URL. |
| `maxDepth` | int | optional, default 2 | Link-depth from start. |
| `mergeContacts` | bool | optional, default `true` | Merge per-domain contacts. Keep on. |
| `sameDomain` | bool | optional, default `true` | Stay inside the start URL's domain. |
| `useBrowser` | bool | optional, default `false` | Headless browser for JS-heavy sites; raises cost. |

Example:
```json
{
  "startUrls": [
    {"url": "https://acme-co.example"},
    {"url": "https://demo-co.example"}
  ],
  "maxRequestsPerStartUrl": 10,
  "maxDepth": 2,
  "mergeContacts": true,
  "proxyConfig": {"useApifyProxy": true},
  "maximumLeadsEnrichmentRecords": 3,
  "leadsEnrichmentDepartments": [],
  "verifyLeadsEnrichmentEmails": true
}
```
