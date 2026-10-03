---
name: apify-website-lead-enrichment
description: Enrich a lead list you already have (a Google Maps export or Apify dataset, a directory or trade-show list, a CRM export, or a plain list of domains) by reading each company website once. Returns emails, phones, 13 social networks, a one-line company description, industry, B2B/B2C and tech stack, with exactly one output row per input row so results join back by placeId or any kept field. Places with no website, Instagram/Facebook/Yelp pages used as a website, dead domains and chain branches are handled explicitly and not charged. Use when the user says "find emails for this list", "enrich my Google Maps leads", "add socials to these companies", "what do these companies do", "which of these sites use WordPress/Shopify", "enrich this CSV of domains", or has a Google Maps dataset ID and wants contacts without re-scraping Maps.
author: TidyTools
author_url: https://apify.com/tidytools
metadata:
  category: lead-generation
  keywords: "lead-enrichment, email-finder, contact-extraction, google-maps, company-enrichment, social-profiles, tech-stack, b2b, local-business, csv-workflow, dataset-enrichment"
---

# Website Lead Enrichment (for lists you already have)

Turn a list of websites, or the dataset of a previous Apify run such as `compass/crawler-google-places`, into contact-ready rows without scraping the source again.

Disclosure: the routed Actors (`tidytools/*`) are built and monetized by the author of this skill.

## Example prompts

Prompts this skill handles:

- "Here is the dataset ID of my Google Maps run. Add the email, Instagram and a short description for every place."
- "Find contact emails for these 200 domains and tell me which ones run WordPress."
- "What do these 30 companies do, and are they B2B or B2C?"

Out of scope (the boundary):

- "Find the name and email of the owner / a specific person at each company." This skill only returns what is published on the company website (usually info@, office@). For named people use `apify-google-maps-leads` (leads enrichment) or `apify-verified-email-finder`.
- "Scrape dentists in Austin from Google Maps." Build the list first with `apify-google-maps-leads` or `compass/crawler-google-places`, then use this skill on its dataset.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

```
Task Progress:
- [ ] Step 1: Identify the input (dataset ID + field, or a list of domains)
- [ ] Step 2: Pick the Actor (contacts only vs. full profile)
- [ ] Step 3: Estimate cost and confirm if above $1
- [ ] Step 4: Run and fetch results
- [ ] Step 5: Deliver the joined table and explain the status column
```

### Step 1: Identify the input

- **Apify dataset** (e.g. Google Maps results): you need `datasetId`, the field holding the website (`website` for Google Maps) and the fields to carry over (`datasetKeepFields`, e.g. `["title", "placeId", "phone", "address", "categoryName"]`).
- **CSV or pasted list**: pass the websites as `domains` (plain strings; bare domains like `example.com` work).

### Step 2: Pick the Actor

| User need | Actor ID | Tier | Price (FREE plan, Sept 2026) |
|-----------|----------|------|------------------------------|
| Emails, phones, social profiles only | `tidytools/website-contact-extractor` | community | $0.002 per website where something was found; nothing found = free |
| Contacts + one-line description, industry, B2B/B2C, country guess and tech stack | `tidytools/company-website-enrichment` | community | $0.006 per website with a result; unreachable sites free |

`company-website-enrichment` already includes the contact details and the tech stack, so never run both on the same list.

### Step 3: Estimate cost

`websites × price`. Rows without a website, social/directory pages and unreachable sites are free, so the real bill is usually 70–90% of the estimate. For large lists, confirm the estimate with the user first and set a maximum cost per run (Apify run option `maxTotalChargeUsd`) if they want a hard cap.

### Step 4: Run

From a Google Maps dataset:

```bash
apify actors call "tidytools/company-website-enrichment" \
  -i '{"datasetId": "DATASET_ID", "datasetField": "website", "datasetKeepFields": ["title", "placeId", "phone", "address", "categoryName"]}' \
  --json \
  --user-agent apify-awesome-skills/apify-website-lead-enrichment \
  2>/dev/null
```

From a list of domains (contacts only):

```bash
apify actors call "tidytools/website-contact-extractor" \
  -i '{"domains": ["katzsdelicatessen.com", "hofbraeuhaus.de"]}' \
  --json \
  --user-agent apify-awesome-skills/apify-website-lead-enrichment \
  2>/dev/null
```

Fetch the rows:

```bash
apify datasets get-items DATASET_ID --format json \
  --user-agent apify-awesome-skills/apify-website-lead-enrichment 2>/dev/null
```

### Step 5: Deliver

Each input row produces exactly one output row with `datasetItemIndex` and the kept fields under `source`. Explain the status to the user:

| Field value | Meaning |
|---|---|
| `charged: true` | Website read, results returned |
| `errorType: "no_website"` | The input row had no website (free) |
| `errorType: "not_a_website"` | The "website" was an Instagram/Facebook/Yelp/Linktree/delivery page; not read, free |
| `duplicateOf` present | Branch of a chain sharing one website; read once, copied |
| `warning` / `redirectedTo` present | Site redirects to another domain (often an expired domain on a directory); contacts may not belong to the business |

Useful output fields: `primaryEmail`, `emails`, `primaryPhone`, `socialProfiles`, `address`, `contactFormUrl`; plus `description`, `industry`, `businessModel`, `countryGuess`, `techStack` from `company-website-enrichment`.

## Calling Actors via MCP instead

Add `https://mcp.apify.com/?tools=tidytools/company-website-enrichment,tidytools/website-contact-extractor` to any MCP client (OAuth sign-in or `Authorization: Bearer <APIFY_TOKEN>`), then call the tools with the same inputs as above.

## Troubleshooting

- **Run rejected with HTTP 400 when using `startUrls`**: `startUrls` rejects bare domains and blank lines. Use `domains` instead.
- **Low email coverage on local businesses**: many small sites only show a phone number or a contact form; check `contactFormUrl`. In a 30-place Google Maps test, 88% of readable websites had an email.
- **"bot challenge" errors**: running several enrichment Actors on the same sites at the same time can trigger protection. Run one Actor per list.
- **Industry label looks off for a local shop**: for local businesses, prefer the Google Maps `categoryName` carried in `source`; use this Actor's `description` for the one-liner.
