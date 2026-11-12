---
name: apify-fmcsa-trucking-leads
description: Find new US trucking companies and look up carriers from the official FMCSA register. Use when the user asks for "new trucking companies", "new MC authority leads", "carriers added this week", "trucking leads for insurance, factoring, ELD or fuel cards", "look up this USDOT or MC number", "vet these carriers", "carriers in Texas with 20 to 50 trucks", "reefer carriers in California", or "enrich my CRM with fleet size and cargo". Routes to one Actor that reads the FMCSA Company Census open dataset, returns one row per carrier (legal name, DBA, USDOT, MC docket, status, phone, e-mail, address, fleet size, drivers, cargo classes, hazmat flag, record date) and runs every filter before billing. No login, no proxy, no scraping of the FMCSA website.
author: Stanislau Ryzhkou — routes to an Actor built by the author; no affiliate or referral parameters
author_url: https://github.com/Stasnislau
metadata:
  category: lead-generation
  keywords: "fmcsa, trucking, carriers, usdot, mc-number, new-carriers, trucking-leads, freight, logistics, carrier-vetting, factoring, eld, insurance-leads, lead-generation, apify"
---

# FMCSA trucking leads and carrier lookup

Turn "who just registered as a trucking company" or "what is this USDOT number" into one clean table from the official FMCSA Company Census, without scraping the FMCSA website.

Disclosure: the author of this skill owns the Actor it routes to (`solidfetch/fmcsa-carriers`). It is a pay-per-result Actor on the Apify Store. No referral or tracking parameters are used in this skill.

## Example prompts

Prompts this skill handles:

- "Give me the trucking companies registered in Florida and Georgia in the last 3 days, with e-mail, as a CSV."
- "Look up these 40 USDOT numbers and tell me which are inactive or have a conditional safety rating."
- "For-hire carriers in Texas with 20 to 50 power units that haul refrigerated food."
- "Every morning, the new carriers since yesterday." (a saved Task on a schedule, see Step 4)

Out of scope (the boundary):

- "Is this carrier's operating authority active, and is their insurance on file?" The census record's docket status is not the operating authority status and the Actor has no insurance data. Send the user to FMCSA's licensing and insurance pages.
- Named decision-makers or owner e-mails. The Actor returns the contact data the carrier filed with FMCSA, nothing more. For person-level enrichment use an enrichment skill such as `apify-lead-scoring-enrichment`.
- Carriers outside the US and Canada.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

Never paste a token into a URL or into a file inside this skill; pass it as `Authorization: Bearer` (the CLI does this for you).

## Workflow

```
Task Progress:
- [ ] Step 1: Is it a search or a lookup?
- [ ] Step 2: Check the live input schema
- [ ] Step 3: Build the input and state the cost
- [ ] Step 4: Run, then check the run summary
- [ ] Step 5: Deliver rows and what is missing
```

### Step 1: Search or lookup

- Search: filters (new since a date, state, city, fleet size, cargo, hazmat, e-mail required).
- Lookup: a list of USDOT or MC numbers. A lookup cannot be combined with search filters; the Actor would ignore them, so do not mix them.

### Step 2: Check the live input schema

    apify actors info "solidfetch/fmcsa-carriers" --input --json \
      --user-agent apify-awesome-skills/apify-fmcsa-trucking-leads 2>/dev/null

An unknown field name stops the run with a hint (for example `"state" (did you mean "states"?)`). Use the schema, not memory.

### Step 3: Build the input and state the cost

Price: $3.00 per 1,000 carriers saved on the free plan, lower on paid plans, plus $0.00005 per run. Numbers not found, rows dropped by `requireEmail` and rows past the cost limit are not charged. Left empty, a search stops at 100 carriers: always set `maxItems` and tell the user the ceiling (`maxItems` 1,000 is at most about $3).

New carriers in two states, with e-mail:

    {"newCarriersSince": "3 days", "states": ["FL", "GA"], "requireEmail": true, "maxItems": 500}

Fleet and cargo filter:

    {"states": ["TX"], "minPowerUnits": 20, "maxPowerUnits": 50, "authorizedForHireOnly": true, "cargoTypes": ["refrigeratedFood"], "maxItems": 1000}

Lookup:

    {"dotNumbers": ["53467", "USDOT 80806"], "mcNumbers": ["MC-138328"]}

### Step 4: Run and check the summary

    apify actors call "solidfetch/fmcsa-carriers" -i 'JSON_INPUT' \
      --json \
      --user-agent apify-awesome-skills/apify-fmcsa-trucking-leads \
      2>/dev/null

Read the `SUMMARY` record of the run's key-value store. It lists numbers not found, numbers not reached because of `maxItems` or the cost limit, and how many rows had contacts hidden.

For a daily feed, save the input as an Apify Task with `newCarriersSince: "2 days"` (the overlap avoids gaps) and add a schedule in Console; de-duplicate on `dotNumber`.

### Step 5: Deliver and be honest about gaps

Report row count, how many have a phone and an e-mail, and these caveats:

- Rows that look like a private person (sole proprietors) have e-mail and street left out by default (`contactsHidden: true`). Do not switch `includeContactsForSoleProprietors` on unless the user confirms they may process that data.
- New records often have no MC docket number: FMCSA moved to the Motus registration system on 14 May 2026. In the Actor's own test run on 4 October 2026, 0 of 2,395 carriers added in 7 days had one. If the user needs MC numbers, say so before the run.
- A new record does not prove the company operates.

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Run fails at once with an input error | Unknown or misspelled field | Fetch the schema (Step 2) and use the hint in the error |
| 100 rows when the user wanted more | `maxItems` left empty | Set `maxItems` |
| Fewer rows than expected with `requireEmail` | In the 7-day test run, 15.2% of new records looked like private persons and had no e-mail shown | Drop `requireEmail` and filter afterwards |
| Lookup returns fewer rows than numbers | Numbers not in the register | Read `SUMMARY`; they were not charged |

## Related skills

- [`apify-lead-scoring-enrichment`](../apify-lead-scoring-enrichment/SKILL.md): scoring and contact enrichment once you have a carrier list with websites.
