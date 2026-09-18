---
name: apify-find-investors-for-startup
description: Build a targeted investor list for a fundraise. Use this when someone asks how to find investors for a startup, needs pre seed or seed or Series A investors, wants investors filtered by sector and stage, or asks which investors write a given check size. Returns venture investors with their name, role, firm, min and target and max check size in US dollars, investment locations, and profile links, pulled from public Signal by NFX investor lists across 103 sectors and four stages. Trigger phrases include how to find investors, find investors for my startup, investor list for fundraising, pre seed investors, seed investors, Series A investors, who invests in my sector, investor check size, and build a target investor list.
author: John Cole
author_url: https://github.com/johnisanerd
license: MIT
metadata:
  keywords: "investors, venture-capital, vc, fundraising, startup, seed, pre-seed, series-a, check-size, investor-list, nfx, signal"
  category: data-extraction
---

# Find investors for a startup, by stage and check size

Turn a fundraise into a filtered list of real investors: who invests in your sector, at your stage, and the cheque size they actually write.

## When to use

Use this when a founder asks how to find investors for a startup, needs a target list for a raise, or wants to know which investors back a specific sector and stage. Use it when the answer needs names and cheque sizes, not general fundraising advice.

Do not use it for company or funding lookups on a single startup; that is a company database job.

## What it returns

Per investor: `name`, `position`, `firmName`, `firmUrl`, `personUrl`, `headshotUrl`, `minInvestment`, `targetInvestment`, `maxInvestment` (US dollars), `investmentLocations`, `listMemberships`, `sourceListSlug`, `sourceListStage`, `sourceListVertical`.

## Prerequisites

- An Apify account and API token. Free account: https://apify.com?fpr=9n7kx3&fp_sid=awesomeskills
- The Apify CLI, authenticated: `apify login`

## The Actor

[NFX Signal Investor API](https://apify.com/johnvc/nfx-signal-investor-api?fpr=9n7kx3&fp_sid=awesomeskills)

## Run it with the Apify CLI

Step 1, discover which lists exist. There are 349 across 103 sectors and four stages.

```bash
apify call johnvc/nfx-signal-investor-api \
  --input '{"mode":"lists","maxItems":50}' \
  --json \
  --user-agent apify-awesome-skills/apify-find-investors-for-startup \
  2>/dev/null
```

Step 2, pull investors from the lists that match the raise.

```bash
apify call johnvc/nfx-signal-investor-api \
  --input '{"mode":"investors","listSlugs":["saas-seed"],"maxItems":100,"pageSize":50}' \
  --json \
  --user-agent apify-awesome-skills/apify-find-investors-for-startup \
  2>/dev/null
```

## Run it from Claude (MCP)

Point an MCP client at `https://mcp.apify.com/?tools=actors,docs,johnvc/nfx-signal-investor-api` and ask it to run the NFX Signal Investor API in `investors` mode with the list slugs you want.

## Workflow

1. Ask for the sector, the stage, and the cheque size the founder is raising.
2. Run `mode: "lists"` and pick the slugs whose `vertical` and `stage` match. Slug shape is `<sector>-<stage>`, for example `fintech-seed`, `ai-seed`, `saas-seed`, `fintech-pre-seed`.
3. Run `mode: "investors"` on those slugs with a small `maxItems` first.
4. Sort by `targetInvestment` and drop investors whose range does not cover the round.
5. Present name, firm, position, cheque range, and `personUrl` so the founder can research each one.
6. Offer to widen by adding an adjacent stage list, or narrow by `investmentLocations`.

## Inputs

| Field | Type | Default | Notes |
|---|---|---|---|
| `mode` | string | `investors` | `investors`, `firms`, or `lists` |
| `listSlugs` | array | none | Required for `investors`. Discover with `lists` mode. |
| `maxItems` | integer | `0` | 0 means no limit. Keep it small while exploring. |
| `pageSize` | integer | `50` | Investors requested per page |
| `stage` | string | none | `lists` mode filter: `pre_seed`, `seed`, `series_a`, `series_b` |
| `enrichWithLinkedIn` | boolean | `false` | Adds firmographics per firm, costs more |
| `enrichWithCrunchbase` | boolean | `false` | Adds funding data per firm, costs more |

## Cost guardrails

Billing is per delivered row. Always set `maxItems` while exploring; a single list can hold 8,000 investors. Leave both enrichment toggles off unless firm-level detail is genuinely needed, because they bill per firm and add several minutes.

## Honest limits

- Not every investor publishes a cheque range, so those fields come back empty rather than estimated.
- Coverage is what NFX publishes publicly. It is investor-centric, so it is not a substitute for a company funding database.
- Geography is modeled as a sector-style list (for example `san-francisco-bay-area`), not as a separate location filter on investors.

## Troubleshooting

- No rows: the slug is wrong. Run `mode: "lists"` and copy the exact `slug` value.
- A run feels slow: enrichment is on. Turn it off, or cut `maxItems`.
- Duplicate people across lists: rows are deduplicated per run, so an investor on several lists appears once with `listMemberships` showing the rest.

## Related

- [NFX Signal Investor API](https://apify.com/johnvc/nfx-signal-investor-api?fpr=9n7kx3&fp_sid=awesomeskills)
- Python and MCP examples: https://github.com/johnisanerd/Apify-NFX-Signal-Investor-API
