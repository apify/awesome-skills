---
name: apify-siret-company-scraper
description: "Search French companies by name, SIREN or SIRET. Get official SIRENE data (status, NAF, address, directors) as flat rows, with monitor mode for changes. Pay per result. Uses the Apify Actor redomic/siret-company-scraper. Use when the user asks to 'siret scraper', 'siren scraper', 'french company scraper', or wants SIRET Company Scraper results as structured JSON or CSV."
metadata:
  category: data-extraction
  keywords: "siret scraper, siren scraper, french company scraper, siret company scraper"
author: Redomic
author_url: https://apify.com/redomic
---

# SIRET Company Scraper

Search French companies by name, SIREN or SIRET. Get official SIRENE data (status, NAF, address, directors) as flat rows, with monitor mode for changes. Pay per result.

Disclosure: the routed Actor, `redomic/siret-company-scraper`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get SIRET Company Scraper results for query carrefour; maxItems 10; mode search"
- "Get SIRET Company Scraper results for query 306138900; mode detail"
- "Get SIRET Company Scraper results for query 65201405100732; mode detail"

Out of scope (the boundary):

- Personal contact data or logged-in content: this Actor reads public pages only.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via `apify login`, the `APIFY_TOKEN` environment variable, or a token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. Map the request onto the input fields below; fetch the live schema for anything unusual.
2. Run the Actor and read its dataset. Rows with a `_status` field are per-input status rows, not data.
3. Deliver a count, a short table of the key fields, and the dataset link or an export.

## Input

- `query` (string): Company name, brand, address keyword, or a SIREN (9 digits) / SIRET (14 digits) to look up. You can also use 'queries' for multiple terms.
- `queries` (array): Multiple search terms, SIREN or SIRET numbers to process in one run. Each gets its own status row.
- `sirenOrSiret` (array): Bulk list of SIREN (9 digits) or SIRET (14 digits) identifiers to fetch directly.
- `mode` (string): search/detail = return matching companies now. monitor = compare current results to the previous run for the same input and report new, changed and removed companies (state stored in a named key-value
- `maxItems` (integer): Maximum company rows to return per query. The API caps pagination at 10,000 results per search; narrow filters to cover larger segments.
- `department` (string): Optional department code to filter results (e.g. 75, 13, 2A).
- `region` (string): Optional region code to filter results (e.g. 11 for Île-de-France).
- `activityCode` (string): Optional NAF activity code filter (e.g. 10.71C for boulangerie-pâtisserie).
- `legalStatus` (string): Filter by administrative status: A = active, C = ceased/closed.
- `employeeRange` (string): Optional employee range code as used by SIRENE (e.g. 00, 01, 02, 03, 11, 12, 21...).
- `companyCategory` (string): Optional company size category: PME, ETI, GE.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| SIRET Company Scraper | `redomic/siret-company-scraper` | community | siret scraper |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/siret-company-scraper" \
      -i '{"query": "boulangerie", "mode": "search", "maxItems": 50}' \
      --json \
      --user-agent apify-awesome-skills/apify-siret-company-scraper \
      2>/dev/null

    apify actors info "redomic/siret-company-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-siret-company-scraper 2>/dev/null

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-siret-company-scraper 2>/dev/null

## Output fields

`id`, `siren`, `siret`, `companyName`, `commercialName`, `status`, `headOfficeStatus`, `isHeadOffice`, `creationDate`, `closureDate`, `activityCode`, `activityCodeNaf25`, `legalFormCode`, `activitySection`, `companyCategory`, `employeeRange`, `employeeYear`, `headOfficeIsEmployer`, `openEstablishments`, `totalEstablishments`, `headOfficeAddress`, `headOfficePostalCode`, `headOfficeCity`, `headOfficeDepartment`, `headOfficeRegion`, `headOfficeCountry`, `latitude`, `longitude`, `directorCount`, `directorNames`, `lastUpdate`, `url`, `query`, `changeType`, `observedAt`
