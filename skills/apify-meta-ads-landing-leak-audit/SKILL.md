---
name: apify-meta-ads-landing-leak-audit
description: "Audit active Meta Ads advertisers and DTC landing pages for 404/out-of-stock ad-spend leaks, missing Meta/GA4/Klaviyo pixels, DNS MX/SPF/DMARC deliverability gaps, 110+ e-commerce tech stacks, and verified brand contact emails using maitreya_buddha/meta-ads-advertiser-leak-audit-email-enricher. Accepts landing page URLs, pasted CSV/URLs, or an upstream Apify Meta Ad Library dataset ID; supports weekly watch-diff deduplication (dedupStoreName) that skips unchanged brands at $0, CRM export presets, and interactive OUTPUT_DASHBOARD.html generation. Use when agencies or growth teams want to find DTC advertisers wasting ad spend on broken landing pages, audit e-commerce tracking stacks, or build evidence-backed cold outreach lists."
author: BoGeun Kim (maitreya_buddha)
author_url: https://apify.com/maitreya_buddha
license: MIT
metadata:
  category: data-extraction
  version: "1.0"
  keywords: "meta-ads, facebook-ads, landing-page-audit, dmarc, tech-stack, lead-enrichment, ecommerce, dtc"
---

# Meta Ads Advertiser Leak Audit & Email Enricher

Audit active DTC advertisers' landing pages for 404/out-of-stock waste, missing analytics pixels, DMARC deliverability failures, 110+ tech stacks, and verified brand emails in a single zero-proxy 128MB run.

> **Author disclosure:** The routed Actor (`maitreya_buddha/meta-ads-advertiser-leak-audit-email-enricher`) is built and maintained by the skill author.

## Example prompts

Prompts this skill handles:

- "Audit these 25 Meta Ads landing page URLs for 404/out-of-stock leaks, Shopify pixel gaps, DMARC failures, and owner emails."
- "Take my upstream Meta Ad Library Apify dataset and score every advertiser by ad-spend leak severity with cold-email openers."
- "Run a weekly deduped leak audit on our DTC prospect list and skip already-audited brands at $0."

Out of scope (the boundary):

- "Scrape raw Facebook Ad Library creatives and video assets by keyword" — run a Meta Ad Library scraper first, then pass its `sourceDatasetId` into this skill.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. Confirm the user's input source: direct `landingPageUrls`, pasted `rawCsvOrUrls`, or an upstream Meta Ad Library `sourceDatasetId`.
2. Inspect the Actor input schema if custom presets (`agencyPreset`, `crmExportPreset`, `dedupStoreName`, `onlyWithActiveLeaks`, `minLeakScore`) are requested.
3. Estimate Pay-Per-Event cost (`$0.0045` per unique audited brand; confirm with the user if `maxBrands` is large) and execute the run.
4. Return the top prioritized leaks (`leakScore`, `leadPriority`, `deliverabilityGrade`, `detectedTechStack`, `primaryEmail`, `coldEmailSubject`) plus a link to the dataset and the generated `OUTPUT_DASHBOARD.html` Key-Value Store record.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Audit DTC/Meta Ads landing pages for 404/OOS/DMARC leaks, tech stack & emails | `maitreya_buddha/meta-ads-advertiser-leak-audit-email-enricher` | community | Performance marketing, CRO & cold-email agencies auditing active advertisers |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling Actors — choose your interface

### Option A: Apify CLI (recommended for portability)

    # Fetch Actor input schema
    apify actors info "maitreya_buddha/meta-ads-advertiser-leak-audit-email-enricher" --input --json \
      --user-agent apify-awesome-skills/apify-meta-ads-landing-leak-audit 2>/dev/null

    # Run a leak audit on landing page URLs
    apify actors call "maitreya_buddha/meta-ads-advertiser-leak-audit-email-enricher" \
      -i '{"landingPageUrls":["https://www.chomps.com/","https://www.bellroy.com/"],"maxBrands":10,"agencyPreset":"auto_best_fit"}' \
      --json \
      --user-agent apify-awesome-skills/apify-meta-ads-landing-leak-audit 2>/dev/null

    # Fetch results from the run dataset
    apify datasets get-items DATASET_ID --format json \
      --user-agent apify-awesome-skills/apify-meta-ads-landing-leak-audit 2>/dev/null

### Option B: Apify MCP connector

Hosted MCP server at <https://mcp.apify.com>. Documented at <https://docs.apify.com/platform/integrations/mcp>.

### Option C: MCP client of your choice (e.g. `mcpc`)

Standalone CLI client. See <https://github.com/apify/mcpc>.

## Troubleshooting

- **Aggregator / shortener URLs (e.g., `fb.me`, `bit.ly`, `linktr.ee`)**: Leave `enableShortenerUnwrap: true` (default) so the Actor unwraps 1 hop and isolates unrecoverable platform URLs (`amazon.com`, `wa.me`) at `$0` without cross-brand collisions.
- **Recurring weekly runs billing duplicate brands**: Set `dedupStoreName` (e.g., `"dtc-weekly-watch"`) and `dedupMode: "skip_seen"` so already-audited brands are skipped at `$0`.
- **Chaining from a Meta Ad Library dataset under Limited Permissions**: Pass the dataset via `sourceDatasetId` (declared with `resourceType: "dataset"` READ permission) instead of `sourceRunId`.
