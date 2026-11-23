---
name: apify-fmcsa-carriers
description: "An FMCSA scraper for freight brokers and trucking-insurance sellers. One run returns US motor carriers with USDOT and MC numbers, legal and DBA names, state, fleet size, cargo, operating and authority status, and insurance dates. Monitor mode reports new, changed and removed carriers. Uses the Apify Actor redomic/fmcsa-carriers. Use when the user asks to 'fmcsa scraper', or wants FMCSA Carrier Scraper results as structured JSON or CSV."
metadata:
  category: data-extraction
  keywords: "fmcsa scraper, fmcsa carriers"
author: Redomic
author_url: https://apify.com/redomic
---

# FMCSA Carrier Scraper

An FMCSA scraper for freight brokers and trucking-insurance sellers. One run returns US motor carriers with USDOT and MC numbers, legal and DBA names, state, fleet size, cargo, operating and authority status, and insurance dates. Monitor mode reports new, changed and removed carriers.

Disclosure: the routed Actor, `redomic/fmcsa-carriers`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get FMCSA Carrier Scraper results for mode search; query TX; addedSinceDays 7; maxItems 10"
- "Get FMCSA Carrier Scraper results for mode search; query California; status active; cargo general"
- "Get FMCSA Carrier Scraper results for mode search; query FL; cargo household; maxItems 10"

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

- `mode` (string): search lists carriers, detail looks up numbers you paste into query, monitor reports only new, changed and removed carriers since the last run of the same search.
- `query` (string): A US state name or two-letter code (TX, Texas) for new-carrier searches, a carrier name to match, or one or more USDOT / MC numbers separated by commas in detail mode.
- `state` (string): Optional two-letter state code. Narrows a carrier-name search. Leave blank to use the state in query.
- `status` (string): Filter on the carrier census status code. Active is the default; inactive finds carriers whose authority was revoked.
- `addedSinceDays` (integer): Keep carriers added to the census in the last N days. 0 means no date filter. Use 7 for a weekly new-authority lead list.
- `minPowerUnits` (integer): Keep carriers with at least this many power units. 0 means no minimum. Applied before rows are charged.
- `maxPowerUnits` (integer): Keep carriers with no more than this many power units. 0 means no maximum. Applied before rows are charged.
- `cargo` (string): Filter on a cargo type from the FMCSA census. Blank means any cargo.
- `maxItems` (integer): Upper limit on delivered carrier rows per run. In monitor mode it limits change rows.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| FMCSA Carrier Scraper | `redomic/fmcsa-carriers` | community | fmcsa scraper |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/fmcsa-carriers" \
      -i '{"mode": "search", "query": "TX", "status": "active", "addedSinceDays": 0, "minPowerUnits": 0, "maxPowerUnits": 0, "maxItems": 100}' \
      --json \
      --user-agent apify-awesome-skills/apify-fmcsa-carriers \
      2>/dev/null

    apify actors info "redomic/fmcsa-carriers" --input --json \
      --user-agent apify-awesome-skills/apify-fmcsa-carriers 2>/dev/null

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-fmcsa-carriers 2>/dev/null
