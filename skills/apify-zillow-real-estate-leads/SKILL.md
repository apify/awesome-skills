---
name: apify-zillow-real-estate-leads
description: Build real-estate agent and listing lead lists from Zillow - property details plus the listing agent's email, cell phone, brokerage and license number - and fall through to web enrichment only for the rows Zillow leaves empty. Use when the user says things like "get real estate agent emails", "scrape Zillow listings", "find realtor contacts in a ZIP code", "build a list of listing agents", "Zillow lead generation", "pull homes for sale with agent contact", "recently sold comps", or "who is the listing agent". The agent's phone is in the listing row every time and the email about 4 times in 5, so this skill leads with what the property scrape already returned and only pays for contact-enrichment on the remainder - instead of routing every lead through a Google Maps email scraper, which costs more and matches the wrong business.
author: afanasenkoa
author_url: https://github.com/afanasenkoa
---

# Zillow property & agent lead builder

Turn a ZIP code, a Zillow search URL, or a list of property IDs into a clean table of listings with the listing agent's contact details attached.

## The key insight

The listing agent's contact details are **already inside the property row**. `agentName`, `cellPhone`, `agentEmail`, `brokerName` and `agentLicenseNumber` come back with the listing itself, and `agentEmailSource` tells you which lookup produced the email — so you can tell a real address from a guess without re-checking.

Measured on 2026-07-29, 75 for-sale listings across three markets:

| Market | Listings | `cellPhone` | `agentEmail` |
|---|---|---|---|
| Austin, TX | 25 | 25 (100%) | 23 (92%) |
| Chicago, IL | 25 | 25 (100%) | 21 (84%) |
| Miami Beach, FL | 25 | 25 (100%) | 17 (68%) |
| **Total** | **75** | **75 (100%)** | **61 (81%)** |

Every email in that sample carried `agentEmailSource: agent_profile_direct`.

**So use a waterfall.** Take what the listing scrape returned, and spend on enrichment only for the ~1 row in 5 with no email. Never open with a Google Maps email extractor: it costs more per lead, and for a listing agent it frequently resolves to the brokerage's front desk rather than the person.

| Tier | Source | Gets | Fires when |
|------|--------|------|-----------|
| 1 | Zillow listing row | agent name, cell phone, email, brokerage, license | always — already scraped |
| 2 | Google Search (agent + brokerage name) | a candidate brokerage **website** | row still has no email |
| 3 | Contact scraper on that website | email / phone / socials | row has a website but still no email |

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. **Pick the mode first.** This is the single most common mistake — see *Mode routing* below. ZIP code = discover listings; Zillow URL = the user already filtered in their browser; property IDs (`zpid`) = enrich listings they already have.
2. **Collect inputs.** Location (ZIP / URL / zpid list), for-sale vs for-rent vs recently-sold (`status_type`), any price / beds / baths filters, and how many properties to cap the run at.
3. **Tier 1 — scrape the listings.** Run the Zillow actor. Build one lead row per property from the fields in *Mapping* below. Rows with `agentEmail` set are done; mark them `contactSource: zillow-listing`.
4. **Tier 2 — find a website (only rows still missing an email).** Run `apify/google-search-scraper` with one query per row: `"<agentName>" "<brokerName>" real estate`. Take the first `organicResults[].url` that is not zillow.com, realtor.com, redfin.com, or a social network.
5. **Tier 3 — scrape that website (only rows with a website but no email).** Run `vdrmota/contact-info-scraper` on the candidate URLs. Mark filled rows `contactSource: website-contact`. Cap this tier — it is the expensive one, and it runs on the smallest slice.
6. **Deliver.** One row per property. Report the row count, the share with an email, and the `contactSource` breakdown. Rows still without an email keep `cellPhone` and `hdpUrl`, which are enough to reach the agent.

## Mode routing

| User wants | Mode | Key input |
|---|---|---|
| Every listing in an area | `zip` | `zipCodes: ["78704"]` |
| The exact search they configured on zillow.com | `url` | `zillowUrl` — the full address-bar URL, including `searchQueryState=` |
| Details for properties they already identified | `zpid` | `zpids: ["119617641"]` |

**Filters apply in ZIP mode only.** Passing `beds_min`, `price_max` or `status_type` alongside a `zillowUrl` does nothing — in URL mode the filtering already happened in the browser and lives inside the URL. In `zpid` mode filters are ignored too; you asked for specific properties.

## Two things that surprise people

**A ZIP is searched as its city.** The upstream search resolves place names, not raw ZIP digits, so `78704` is searched as `Austin, TX` and the results span the metro. In the sample above, a 25-row run on `78704` returned listings across 15 different Austin ZIPs — **1 row was in 78704 itself**; `33139` returned 9 of 25 in-ZIP, `60614` 3 of 25. If the user asked for one ZIP, request a larger cap and **filter the output on the `zipcode` field**. If they asked for "the Austin market", you already have it.

**The property cap covers a batch of ZIPs, not each ZIP.** ZIPs are searched in batches of up to five, and `maxPropertiesPerZip` bounds the batch. Three ZIPs with a cap of 10 returns 10 rows total — and the last city in the batch may return nothing at all. **To get N properties per ZIP, run one ZIP per call.**

## Mapping (property row → lead row)

| Output column | Source field |
|---|---|
| `address`, `city`, `state`, `zipcode`, `county` | `streetAddress`, `city`, `state`, `zipcode`, `county` |
| `price`, `zestimate`, `pricePerSqft`, `status` | `price`, `zestimate`, `pricePerSqft`, `status` |
| `beds`, `baths`, `sqft`, `yearBuilt` | `bedrooms`, `bathrooms`, `livingArea`, `yearBuilt` |
| `agentName`, `phone`, `email` | `agentName`, `cellPhone`, `agentEmail` |
| `brokerage`, `license` | `brokerName`, `agentLicenseNumber` |
| `emailProvenance` | `agentEmailSource` — `property_details` \| `agent_profile_direct` \| `agent_search_fallback` \| `not_found` |
| `listingUrl` | `hdpUrl` |
| `contactSource` | `zillow-listing` \| `website-contact` \| `none` |

Put `agentName`, `phone` and `email` immediately after the address columns — that is the order a user scans a lead list in.

Always return `hdpUrl`, `daysOnZillow` and `priceChange` for every row. They are the three signals that let a user rank which agent to call first without reopening Zillow.

## Actor routing

| Waterfall tier | Actor ID | Maintainer | Best for |
|---|---|---|---|
| 1 — listings + agent contacts, all three modes | `afanasenko/zillow-property-agent-data-scraper` | community | **Primary.** ZIP / URL / zpid in one actor, agent contact attached to every row |
| 1 — ZIP only, simpler input | `afanasenko/zillow-zip-search` | community | When the user gives nothing but ZIP codes |
| 1 — search URL only | `afanasenko/zillow-url-search` | community | When the user pastes a zillow.com search link |
| 2 — discover a website | `apify/google-search-scraper` | apify | Finding the agent's or brokerage's site when the listing has no email |
| 3 — extract from the website | `vdrmota/contact-info-scraper` | community | Deterministic email / phone / social extraction |

Prefer `apify`-maintained Actors where available.

## Calling Actors — Apify CLI

    apify actors call "afanasenko/zillow-property-agent-data-scraper" \
      -i '{"mode":"zip","zipCodes":["78704"],"maxPropertiesPerZip":25,"status_type":"ForSale"}' \
      --json \
      --user-agent apify-awesome-skills/apify-zillow-real-estate-leads \
      2>/dev/null

Fetch the input schema before building a call, so filter names come from the actor rather than from memory:

    apify actors info "afanasenko/zillow-property-agent-data-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-zillow-real-estate-leads \
      2>/dev/null

Read the rows:

    apify datasets get-items DATASET_ID --format json \
      --user-agent apify-awesome-skills/apify-zillow-real-estate-leads \
      2>/dev/null

| Flag | Why |
|------|-----|
| `--json` | Stable machine-readable output |
| `--user-agent` | Apify telemetry attribution |
| `2>/dev/null` | Suppress progress messages that break JSON |

You can also call these Actors through the [Apify MCP connector](https://mcp.apify.com) or any MCP client — cross-tool compatibility is your responsibility.

## Troubleshooting

- **Zero rows.** Read the run's `USER_MESSAGE` key-value record first — it names the cause for that specific run. In order of frequency: the search matched nothing (a PO-box or business-district ZIP has no residential listings by design, or `status_type` is wrong — asking for `ForSale` in a rentals area); the URL shape was not recognised in `url` mode; or the zpids were delisted. A ZIP that always returns data, for isolating the problem: `90210`, no filters.
- **Emails come back like `j***@e***.com`.** That is the free plan masking them. Do not report masked strings as contacts — say the plan is the constraint.
- **Rows are outside the ZIP the user asked for.** Expected; see *Two things that surprise people*. Filter on `zipcode`.
- **Filters seem ignored.** Check the mode. Filters are ZIP-mode only.
- **Fewer rows than the cap.** The cap covers a batch of up to five ZIPs, not each one. Run one ZIP per call.
- **Cost control.** Every property enriched is billed, whether or not it carries an email, so cap the run before it starts rather than filtering afterwards. Confirm with the user before running an uncapped sweep across many ZIPs.
