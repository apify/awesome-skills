---
name: apify-multilingual-local-leads
description: Build a local-business lead list for non-English markets from Google Maps, where the email column is normally empty. Crawls contact pages by their native names (impressum, kapcsolat, contacto, contatti, contactez-nous, kontakt-z-nami, fale-conosco, contacteer, kontakty) rather than only /contact, and grades every address for deliverability with MX, SPF, DMARC and an SMTP probe before you send. Use when the user asks for leads in Germany, Austria, Switzerland, France, Italy, Spain, Portugal, Poland, Hungary, the Netherlands or any non-English market, says their Google Maps scrape "came back with no emails", asks for verified or deliverable emails, wants to avoid bounces on a cold campaign, needs more than Google's ~120 results per search, or wants to re-run a city weekly without paying for the same places twice.
author: yestrue
author_url: https://github.com/projectworks007
metadata:
  keywords: "google-maps, leads, local-business, b2b, prospecting, email-verification, deliverability, mx-record, spf, dmarc, catch-all, multilingual, non-english, europe, germany, france, italy, spain, poland, hungary, netherlands, geo-grid, delta-mode"
---

# Multilingual local leads with deliverability grading

Links route to `highbrow_fame/google-maps-email-extractor`, a paid Actor built by the author.

Most Google Maps lead pipelines look for `/contact` and `/about` on the business website. In
Germany the page is `/impressum`, in Hungary `/kapcsolat`, in Poland `/kontakt-z-nami`, in
Italy `/contatti`. When the crawler cannot find the page, the email column comes back empty
and the run looks like it worked. This skill is for exactly that situation.

Use `apify-google-maps-leads` instead when the target market is English-speaking and you want
third-party enrichment (Scalelist phone/email backfill, AI name discovery). The two skills
solve different halves of the problem.

## When this is the right tool

- The market is not English-speaking, or is mixed.
- The user needs emails that will actually deliver, not just strings that look like emails.
- A previous Maps scrape returned rows with names and phones but no email addresses.
- The user is about to run cold outreach and cares about bounce rate.

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

`language` accepts 48 codes. It sets the Maps interface language and, more importantly,
tells the crawler which contact-page names to look for.

Residential proxy is not optional here. Google throttles datacenter IPs on Maps hard enough
that runs time out rather than return fewer results.

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
