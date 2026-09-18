---
name: apify-list-vc-firms-by-city
description: Export a list of VC firms for one city, region, or sector, ready for a CRM import. Use this when someone asks for a list of VC firms, venture capital firms in San Francisco or New York or London, which firms invest in a sector, or wants a firm directory rather than individual investors. Returns firm name, firm profile link, and the stage and sector context of the list it came from, with optional LinkedIn and Crunchbase enrichment adding industry, size, followers, funding, rank, and operating status per firm. Trigger phrases include list of vc firms, vc firms in san francisco, venture capital firms list, vc firm directory, firms investing in a sector, build a VC target list, and export VC firms to CSV.
author: John Cole
author_url: https://github.com/johnisanerd
license: MIT
metadata:
  keywords: "vc-firms, venture-capital, investor-directory, firm-list, san-francisco, new-york, london, crm-import, lead-generation, nfx, signal"
  category: data-extraction
---

# List VC firms by city or sector

Get the venture firms behind a market as a clean directory, then optionally enrich each one with firmographics and funding data.

## When to use

Use this when the ask is about firms rather than people: a list of VC firms in a city, the firms active in a sector, or a directory to import into a CRM. Use the investor-level skill instead when the user needs named partners and cheque sizes.

## What it returns

Per firm: `firmName`, `firmSlug`, `firmUrl`, `sourceListSlug`, `sourceListStage`, `sourceListVertical`. With enrichment on: `linkedinIndustry`, `linkedinSize`, `linkedinFollowers`, `linkedinUrl`, `crunchbaseRank`, `crunchbaseEmployees`, `crunchbaseStatus`, `crunchbaseUrl`.

## Prerequisites

- An Apify account and API token. Free account: https://apify.com?fpr=9n7kx3&fp_sid=awesomeskills
- The Apify CLI, authenticated: `apify login`

## The Actor

[NFX Signal Investor API](https://apify.com/johnvc/nfx-signal-investor-api?fpr=9n7kx3&fp_sid=awesomeskills)

## Run it with the Apify CLI

Geographic directory, for example the San Francisco Bay Area:

```bash
apify call johnvc/nfx-signal-investor-api \
  --input '{"mode":"firms","listSlugs":["san-francisco-bay-area"]}' \
  --json \
  --user-agent apify-awesome-skills/apify-list-vc-firms-by-city \
  2>/dev/null
```

Sector directory with firm enrichment:

```bash
apify call johnvc/nfx-signal-investor-api \
  --input '{"mode":"firms","listSlugs":["ai-seed"],"maxItems":50,"enrichWithCrunchbase":true}' \
  --json \
  --user-agent apify-awesome-skills/apify-list-vc-firms-by-city \
  2>/dev/null
```

## Run it from Claude (MCP)

Point an MCP client at `https://mcp.apify.com/?tools=actors,docs,johnvc/nfx-signal-investor-api` and ask it to run the NFX Signal Investor API in `firms` mode for the list you want.

## Workflow

1. Establish whether the user wants a place or a sector.
2. For a place, use one of the 14 geographic lists: `san-francisco-bay-area`, `new-york-city`, `london`, `boston-new-england`, `los-angeles-southern-california`, `israel`, `midwest`, `raleigh-durham-southeast-us`, `austin`, `latam-latin-america`, `seattle-portland`, `canada`, `colorado-utah`, `british-columbia`.
3. For a sector, run `mode: "lists"` and pick a `<sector>-<stage>` slug.
4. Run `mode: "firms"` on the chosen slugs.
5. Offer enrichment only if the user needs size, industry, funding, or status per firm, and explain that it bills per firm.
6. Hand back a table keyed on `firmName` with `firmUrl`, ready to import.

## Inputs

| Field | Type | Default | Notes |
|---|---|---|---|
| `mode` | string | `investors` | Set to `firms` for this workflow |
| `listSlugs` | array | none | Required. One or more list slugs. |
| `maxItems` | integer | `0` | 0 means no limit |
| `enrichWithLinkedIn` | boolean | `false` | Industry, size, followers, page link |
| `enrichWithCrunchbase` | boolean | `false` | Funding, rank, employees, status |

## Cost guardrails

Billing is per delivered row, and a large geography can return thousands of firms, so set `maxItems` on a first pass. Enrichment bills per unique firm and adds minutes; unresolved firms are never charged.

## Honest limits

- The public firm record is a name and a profile link. Depth comes from the enrichment toggles.
- Name-based enrichment does not resolve every firm, so expect some rows without enrichment fields.
- Only the 14 geographies above exist as lists. Places outside them cannot be served.

## Troubleshooting

- Empty result: check the slug against `mode: "lists"` output.
- Missing enrichment on some rows: the firm name did not match a company record. The row still ships, and you are not billed for the miss.
- A run takes several minutes: that is enrichment doing name lookups. Turn it off for a fast directory.

## Related

- [NFX Signal Investor API](https://apify.com/johnvc/nfx-signal-investor-api?fpr=9n7kx3&fp_sid=awesomeskills)
- Python and MCP examples: https://github.com/johnisanerd/Apify-NFX-Signal-Investor-API
