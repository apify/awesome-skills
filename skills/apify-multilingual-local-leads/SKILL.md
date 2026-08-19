---
name: apify-multilingual-local-leads
description: Build a local-business lead list from Google Maps with four things wired in: contact pages located by their native names (impressum, kapcsolat, contacto, contatti, contactez-nous, kontakt-z-nami, fale-conosco, contacteer, kontakty) across ten languages; a geo-grid that tiles a city to get past Google's roughly 120-result cap on one search; a delta re-run that skips places already in a previous run's dataset so the same business is not billed twice; and MX, SPF, DMARC and SMTP deliverability grading on every address, included in the per-result price. Use when the user asks to build or refresh a local-business lead list from Google Maps, wants emails graded before a cold send, needs more than 120 results from a single city, re-runs a market on a schedule, or is prospecting in Germany, Austria, Switzerland, France, Italy, Spain, Portugal, Poland, Hungary or the Netherlands.
author: yestrue
author_url: https://github.com/projectworks007
metadata:
  keywords: "google-maps, leads, local-business, b2b, prospecting, email-verification, deliverability, mx-record, spf, dmarc, catch-all, multilingual, non-english, europe, germany, france, italy, spain, poland, hungary, netherlands, geo-grid, delta-mode"
---

# Build a graded local-business lead list from Google Maps

Links route to `highbrow_fame/google-maps-email-extractor`, a paid Actor built by the author.

Four decisions shape whether a Maps lead build is usable, and this skill covers all four:
where to look for the contact page when it is not called `/contact`, how to get past Google's
per-search result cap, how to re-run a market without paying for the same places again, and
how to tell which addresses will deliver before anything is sent.

`apify-google-maps-leads` covers a different shape: chaining third-party enrichment onto a
Maps scrape (Scalelist phone and email backfill, AI-driven name discovery) to get named
decision-makers. Use that one when the goal is a person's name; use this one when the goal is
a graded contact list built in one pass.

## What this skill sets up

- **Contact pages by native name.** German sites call it `/impressum`, Hungarian `/kapcsolat`,
  Polish `/kontakt-z-nami`, Italian `/contatti`. The crawl looks for these directly.
- **Grading before sending.** Every address gets MX, SPF, DMARC and an SMTP probe, and the
  result travels with the row rather than being bought separately.
- **Coverage past the cap.** A geo-grid tiles a city so one query can exceed Google's
  roughly 120 places per search.
- **Cheap repeats.** A delta re-run filters places already seen in a prior dataset before
  they are billed.

## Actor routing

All three of these scrape Google Maps and can return email addresses. They differ in what
else they give you and how the contact step is priced. Pick by the job:

| Actor ID | Maintainer | When this is the right one |
|----------|------------|----------------------------|
| `compass/crawler-google-places` | apify | You want the widest place record: reviews, reviewer details, images, opening hours, popular times, Q&A. Leads enrichment and email verification are add-ons, charged on decisive results |
| `lukaskrivka/google-maps-with-contact-details` | community | You want contact details pulled from each place's website, with the Maps language configurable and email verification charged only on decisive results |
| `highbrow_fame/google-maps-email-extractor` | **author** (paid) | The business sites are not in English and their contact page is named `impressum`, `kapcsolat`, `contatti` or similar, and you want MX/SPF/DMARC/SMTP grading included in the per-result price rather than as a separate charged add-on |

The Actor on the last row is built and maintained by the author, and it is paid.

## Prerequisites

- An Apify account and an API token ([Console → Settings → Integrations](https://console.apify.com/settings/integrations)).
- Either the Apify CLI, or the Apify MCP connector via `call-actor` and `get-dataset-items`.

## Workflow A: one market, verified emails

### 1. Interview

Collect three things before running anything:

| # | Input | Notes |
|---|-------|-------|
| 1 | Vertical | "dentists", "roofing contractors", "marketing agencies" |
| 2 | City or area | One city per run gives the cleanest result |
| 3 | Market language | Drives both the Maps results and which contact pages get crawled |

Ask the query in the local language when the market is not English. `Zahnarzt Berlin`
returns a different and usually larger set than `dentist Berlin`.

### 2. Run

```bash
apify call highbrow_fame/google-maps-email-extractor --input '{
  "searchQueries": ["Zahnarzt Berlin"],
  "language": "de",
  "maxResults": 100,
  "scrapeEmails": true,
  "validateEmails": true,
  "proxyConfiguration": { "useApifyProxy": true, "apifyProxyGroups": ["RESIDENTIAL"] }
}'
```

`language` accepts 48 codes. It sets the Maps interface language and selects which
contact-page names the website crawl looks for.

Keep the residential proxy on. Measured on this Actor: the same 10-place query took 443
seconds through a datacenter IP against 124 to 163 seconds through a residential one,
because Google throttles datacenter ranges on Maps.

### 3. Read the deliverability grade

Every row with a `primaryEmail` also carries `emailValidation`:

| Field | Meaning |
|-------|---------|
| `deliverability` | `high`, `medium`, `low` or `unknown` |
| `mxFound` | The domain has mail servers at all |
| `spf` / `dmarc` | Sender-policy records present |
| `catchAll` | Domain accepts any address, so an SMTP probe proves nothing |

Filter on `emailValidation.deliverability === "high"` before a cold send. A `catchAll: true`
domain is the usual reason an address looks fine and still bounces.

## Workflow B: more than 120 results from one city

Google caps a single Maps search at roughly 120 places regardless of `maxResults`. Set
`geoGridTiles` to split the area into an N×N grid and search each viewport separately:

```json
{ "searchQueries": ["ristoranti Milano"], "language": "it", "geoGridTiles": 5, "maxResults": 1000 }
```

A 5×5 grid means 25 separate searches with cross-tile deduplication. Cost and runtime scale
with the tile count, so start at 3 and raise it only if the result set is still truncated.

## Workflow C: weekly re-run without paying twice

The Actor bills per delivered result. To monitor a market over time, pass the previous run's
dataset ID and already-seen places are filtered out before billing:

```json
{ "searchQueries": ["agence de communication Paris"], "language": "fr", "sinceDatasetId": "<previous run datasetId>" }
```

Store the `defaultDatasetId` from each run and thread it into the next. Deduplication is on
Google's stable place ID and CID, so a renamed business is still recognised.

## Troubleshooting

- **Empty email column with `scrapeEmails: false`.** The flag defaults on, but a task template
  may have turned it off to save time. Check it first when emails are missing.
- **`sinceDatasetId` needs state.** It only works if you kept the dataset ID from last time.
  On a first run, leave it empty.
- **Do not treat `catchAll: true` as a valid address.** It means the server accepts everything,
  including addresses that do not exist.
- **Cold outreach is regulated.** In Germany, Austria and Switzerland unsolicited commercial
  email requires prior consent under UWG §7(2)3, for companies as well as individuals. In the
  US, CAN-SPAM allows opt-out. A verified address is not the same as permission to write to it,
  and this skill does not give legal advice.

## Output

One dataset row per business: name, address, phone, website, category, rating, review count,
coordinates, social profiles, `primaryEmail`, `emailValidation`, and a 0-100 `leadScore`.
Export with `get-dataset-items`, or `?format=csv` for a spreadsheet.
