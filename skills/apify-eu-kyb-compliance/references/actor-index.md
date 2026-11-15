# Actor index — apify-eu-kyb-compliance

Routing table with the fields an agent needs from each run. All Actors below are built by the
author of this skill (see the Disclosure in `SKILL.md`). Prices read on 2026-11-02.

| Register | User intent | Actor ID | Tier | Notes |
|----------|-------------|----------|------|-------|
| EU Consolidated Financial Sanctions List (DG FISMA FSF) | Screen names, EU reference numbers or ID numbers | `itulo/eu-sanctions-screen` | community | Pay per event: $0.01 per run + $0.002 per row. Input `queries[]`, `subjectType` (`all`/`person`/`enterprise`), `programmes[]`, `country`, `fuzzyThreshold` (default 0.78), `maxMatchesPerQuery` (default 5), `includeClearQueries` (default true). Output `status`, `score`, `matchedValue`, `euReferenceNumber`, `programme`, `primaryName`, `aliases[]`, `countries[]`, `listPublicationDate`, `disclaimer`, `attribution`. |
| EU VIES | Validate VAT numbers, reverse-charge flag | `itulo/eu-vies-vat-validator` | community | $0.0025 per VAT check. `mode=validate_batch`, `vatNumbers[]` with country prefix, `supplierCountryCode`. Output `valid`, `companyName`, `companyAddress`, `entityClassification`, `isCrossBorderEuB2B`, `reverseChargeCandidate`, `requestDateUtc`. `mode=member_state_status` returns 28 availability rows (28 × $0.0025). `requesterMemberStateCode` + `requesterNumber` request an official VIES consultation number. |
| Insee Sirene (API Recherche d'entreprises, Licence Ouverte 2.0) | French company status by SIREN/SIRET or search | `itulo/france-sirene-company-search` | community | $0.0025 per company. `mode=lookup` + `sirenNumbers[]`, or `mode=search` + `query` and filters (`nafCodes`, `postCodes`, `departements`, `legalForms`, `status`, `maxResults`, default 100). Output `siren`, `name`, `legalForm`, `activity`, `status`, `creationDate`, `closureDate`, `headOffice`, `vatNumberComputed`, `marketingOptOut`. Sole traders are always excluded. |
| GLEIF LEI (CC0) | LEI by name or national register number | `itulo/uk-companies-house-kyb` `mode=gleif_search` | community | $0.002 per LEI record. `gleifName` and/or `gleifRegisteredAs`, `gleifCountry`, `gleifStatus`, `maxResults`. Output `lei`, `legalName`, `entityStatus`, `registeredAs`, `legalAddress`, `registration.status`. Keyless. |
| GLEIF Level 2 | Direct and ultimate parent | `itulo/uk-companies-house-kyb` `mode=gleif_ownership` | community | $0.003 per chain. `leis[]`. Output `directParent`, `ultimateParent` (each with `parentLei`, `relationshipStatus`, `reportingException`), `directChildrenCount`. |
| UK Companies House | UK company profile, filings, charges, insolvency | `itulo/uk-companies-house-kyb` `mode=lookup` / `search` / `advanced_search` | community | $0.0025 per company + $0.001 per filing/charge/insolvency item. Needs the user's free key in `apiKey` (secret input). Officer and PSC names are not output. `filingHistoryItems`, `includeCharges`, `includeInsolvency` add billable items. |
| Finnish PRH / YTJ open data (CC BY 4.0), Norwegian Brreg (NLOD 2.0) | Bankruptcy, liquidation, name change, new company events; watchlist diffs | `itulo/prh-company-events` | community | $0.01 per run + $0.002 per event. `registry` (`fi_prh`/`no_brreg`), `eventTypes[]`, `dateFrom`/`dateTo`, `location`, `companyForm`, `maxPerEvent` (default 500). `watchBusinessIds[]` stores a snapshot on the first run and emits change events on later runs with the same `alertStateKey`. |

## Free first-party alternatives

Each register can also be checked by hand, free, at its official site: the EU Sanctions Map /
FSF files, the VIES web form, annuaire-entreprises.data.gouv.fr, search.gleif.org,
find-and-update.company-information.service.gov.uk, ytj.fi and brreg.no. Mention them when the
user only needs one or two manual checks.

## How to extend

1. Search for candidates: `apify actors search "KEYWORDS" --json --limit 20 --user-agent apify-awesome-skills/apify-eu-kyb-compliance 2>/dev/null`
2. Fetch input schema: `apify actors info "ACTOR_ID" --input --user-agent apify-awesome-skills/apify-eu-kyb-compliance 2>/dev/null`
3. Add a row above with the user intent that should trigger it.
