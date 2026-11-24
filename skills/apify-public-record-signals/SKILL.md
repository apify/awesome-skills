---
name: apify-public-record-signals
description: Find and rank companies likely to buy now from official public records - new SEC Form D raises, new company registrations (France, Norway, Finland, Estonia, US states), public contracts won and open tenders, US customs import growth and lookalike importers, trade show exhibitor lists, and hiring for given roles - then score each account and add contacts from its own website. Use when the user asks for warm leads, account lists, intent or trigger signals, "who just raised money", "new companies in my area", "who wins government contracts in my sector", "which brands import from China", "who exhibits at <show>", or prospect research for an ICP with a reason to reach out.
author: tacps126
author_url: https://github.com/tacps126
metadata:
  category: lead-generation
  keywords: "buying-signals, trigger-events, public-records, sec-form-d, funding, company-registry, new-businesses, tenders, government-contracts, import-records, bill-of-lading, trade-shows, exhibitors, hiring-signals, lead-scoring, contact-enrichment, b2b, prospecting"
---

# Public-Record Buying Signals

Turns official public records into a short, ranked account list where every row has a dated signal, a source link, a score and a contact.

Routed Actors are built by the author of this skill (paid per result on the user's Apify account).

## Example prompts

Prompts this skill handles:

- "Find California fintech startups that raised at least $2M in the last two weeks, with a contact for each."
- "Which US brands import furniture from Vietnam and are growing? Give me the ten best to pitch our freight service."
- "New restaurants registered in Oslo this month, and their websites and emails."

Out of scope (the boundary):

- "Monitor LinkedIn posts about our category every week" - a recurring social-content pipeline; use `apify-buying-signal-detection`.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. **Pin down the ideal customer**: what the user sells, which team buys it, where (countries, states, cities) and what size. Ask before running anything.
2. **Pick two or three signals** that fit the product (table below). Fetch each Actor's input schema and build a small input: 20-50 items, a 7-30 day window. Tell the user the expected cost before a large pull.
3. **Run, then join** rows on the company name or website domain (lowercase; drop `Inc`, `LLC`, `Ltd`, `GmbH`, `SAS`).
4. **Score each account 0-100** and show the parts:
   - Fit (up to 40): industry, place and size match.
   - Signal strength (up to 40): raise size, contract value, import growth (last 12 months against the 12 before), hiring `signalScore`.
   - Freshness (up to 20): 20 if the newest signal is under 7 days old, 10 if under 30.
   - Plus 10 for each extra independent signal, capped at 100. Drop accounts with no fit.
5. **Add contacts** for the top 10-20 only. Form D filings and most registers carry no website, so find it first: one Google search per company name plus city, keep the official domain. Then run Website Contact Details on those websites with `requireEmail: true`. Founders and executives in Form D filings (`people`) are named contacts too. Never invent an email or a person.
6. **Deliver** a table (account, score, signals with dates, why now, contact, source links), a two-sentence opener for the top five that cites the signal, and the run cost. Offer a weekly schedule with *Only new* so later runs return only new accounts.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| New private raises (seed to growth) with founders and executives | `tacps126/startup-funding` | community | SEC Form D filings; `postedWithinDays`, `states`, `industries`, `minAmountRaised` |
| Brand-new businesses | `tacps126/company-registry` | community | `mode: "new"`, `countries` (FR, NO, FI, EE, US-NY, US-CO, US-CT, US-OR), `registeredWithinDays`, `industryCodes` (NACE), `locations` |
| Who wins public contracts, open tenders | `tacps126/tenders-radar` | community | US, EU/EEA, UK and 10+ more countries; `keywords`, `sectors`, `countries`; supplier mode lists a company's won contracts |
| Importers, their factories, lookalike importers | `tacps126/us-import-records` | community | US customs bills of lading; `companies`, `suppliers`, `findLookalikes` |
| Companies at a trade show | `tacps126/exhibition-scraper` | community | Any show's exhibitor-list link in `startUrls`; booth, email, phone, website |
| Companies hiring for given roles | `tacps126/hiring-signals` | community | `roleKeywords`, `companies`, `searches`, `postedWithinDays`; returns `signalScore` |
| A company's website (Form D and registers have none) | `apify/google-search-scraper` | apify | `queries`: company name plus city, one per line; take the first official domain |
| Contacts for the shortlisted accounts | `tacps126/contact-details` | community | `startUrls` (websites), `requireEmail`; charged only for sites with contacts |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling Actors - choose your interface

### Option A: Apify CLI

    apify actors info "tacps126/startup-funding" --input \
      --user-agent apify-awesome-skills/apify-public-record-signals 2>/dev/null

    apify actors call "tacps126/startup-funding" \
      -i '{"postedWithinDays": 14, "states": ["CA"], "industries": ["Other Technology"], "minAmountRaised": 2000000, "maxItems": 50}' \
      --json \
      --user-agent apify-awesome-skills/apify-public-record-signals \
      2>/dev/null

    apify datasets get-items DATASET_ID --format json \
      --user-agent apify-awesome-skills/apify-public-record-signals 2>/dev/null

### Option B: Apify MCP connector

Hosted MCP server at <https://mcp.apify.com>: `fetch-actor-details` for the input schema, then `call-actor`. Documented at <https://docs.apify.com/platform/integrations/mcp>.

### Option C: MCP client of your choice (e.g. `mcpc`)

Standalone CLI client. See <https://github.com/apify/mcpc>.

## Troubleshooting

- Few or no Form D rows: widen `postedWithinDays` (300-500 filings arrive per weekday across all states) or drop the industry filter.
- Registry rows without industry: French announcements carry no industry code, so an industry filter looks each company up first and takes a few minutes; add keywords or places to narrow it.
- Import records: a name finds the page with the same name; if a company trades under another name, pass its importyeti.com page link.
- Exhibitor lists without emails: some organisers publish only websites; pass those websites to `tacps126/contact-details`.
- Cost: every Actor is pay-per-result with a small start fee; start with `maxItems` 20-50 and set a maximum charge on large runs.

## Rules

- Public business records only. Use contacts for relevant, personal outreach and follow the law where the user is (CAN-SPAM, GDPR, CASL).
- Every signal in the answer carries its source link and date. Say when a source returned nothing; don't fill gaps with guesses.
