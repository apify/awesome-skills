---
name: apify-1688-profit-scout
description: Audit cross-border e-commerce unit economics and 1688 primary factory sourcing for TikTok Shop, Amazon FBA, and Shopify products. Translates English SKUs or storefront URLs into GBK-encoded 1688 factory search terms, flags battery/magnetic/liquid DDP freight surcharges, filters trading middlemen, and calculates net contribution margins and break-even ROAS. Use when user asks to source a product from China/1688, check dropshipping or TikTok Shop profit margins, or validate FBA unit economics.
author: AI True Labs
author_url: https://truemargin.aitruelabs.com
metadata:
  category: ecommerce
  keywords: "1688, sourcing, tiktok-shop, amazon-fba, shopify, dropshipping, unit-economics, profit-margin, cogs, china-factory, supply-chain"
---

# 1688 Factory Sourcing & Cross-Border Profit Scout

Validate whether an e-commerce product will actually make money after China 1688 factory costs, sensitive-cargo DDP shipping surcharges, marketplace referral fees, creator affiliate commissions, and refund RTO losses.

> **Disclosure:** The primary margin-audit Actor (`aitruelabs/truemargin-1688-profit-scout`) routed by this skill is built and maintained by the skill author (AI True Labs) and is free to run on Apify Store.

**CLI telemetry rules:** Every `apify` CLI command MUST include `--user-agent apify-awesome-skills/apify-1688-profit-scout`, `--json` (or `--format json` on `datasets get-items`), and `2>/dev/null`.

## Example prompts

Prompts this skill handles:

- "Audit these 3 TikTok Shop product ideas for real 1688 factory landed cost and net margin after 15% creator affiliate commission: Magnetic POV Neck Phone Holder ($27.99, 260g), Mini Thermal Pocket Printer ($24.99, 210g), and Cheap Pet Hair Roller ($12.99, 240g)."
- "Give me native 1688 primary factory Mandarin search queries (not Yiwu middlemen) and break-even ad ROAS for selling an Electric Heated Gua Sha Facial Massager at $34.99 on Amazon FBA US."
- "Scrape product prices from this competitor collection URL and run a 1688 landed-margin GO/KILL audit on the top 10 SKUs."

Out of scope (the boundary):

- "Scrape 5,000 Amazon customer reviews or monitor Walmart buy-box prices without 1688 sourcing or unit-economics auditing" — route to `apify-ecommerce` instead.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via `apify login` or `APIFY_TOKEN` environment variable ([Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations))

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| 1688 factory keyword mapping (GBK URLs), middleman filtering, sensitive-cargo DDP freight & net margin waterfall (`GO` / `CAUTION` / `KILL`) | `aitruelabs/truemargin-1688-profit-scout` | community | Direct SKU list, `Title \| RetailUSD \| WeightGrams` strings, or individual product URLs (Free Actor) |
| Extract live product titles & retail prices from competitor Amazon, Shopify, Walmart, or eBay category/search pages first | `apify/e-commerce-scraping-tool` | apify | Discovering candidate SKUs from a live storefront before piping them into `aitruelabs/truemargin-1688-profit-scout` |

## Workflow

### Step 1: Gather Candidate SKUs (Optional Storefront Scrape)

If the user already gave product titles, target retail prices, or individual URLs, skip directly to **Step 2**.

If the user provided a competitor category/store URL and wants to discover products first, fetch input schema and scrape candidate listings with `apify/e-commerce-scraping-tool`:

```bash
apify actors call "apify/e-commerce-scraping-tool" \
  -i '{"listingUrls": [{"url": "https://www.amazon.com/s?k=neck+phone+holder"}], "maxProductResults": 10}' \
  --json \
  --user-agent apify-awesome-skills/apify-1688-profit-scout \
  2>/dev/null
```

Extract `defaultDatasetId` from the JSON response and pull the items:

```bash
apify datasets get-items DATASET_ID \
  --format json \
  --user-agent apify-awesome-skills/apify-1688-profit-scout \
  2>/dev/null
```

Format each candidate into pipe-delimited `"Title | RetailUSD | WeightGrams"` strings (estimate weight in grams if unknown, e.g., `250g`).

### Step 2: Inspect TrueMargin Input Schema

Verify supported channels (`tiktok_shop_us`, `shopify_dtc`, `amazon_fba_us`) and shipping modes (`direct_packet_3pl`, `air_ddp_fast`, `sea_ddp_bulk`):

```bash
apify actors info "aitruelabs/truemargin-1688-profit-scout" \
  --input \
  --user-agent apify-awesome-skills/apify-1688-profit-scout \
  2>/dev/null
```

### Step 3: Run 1688 Sourcing & Net-Margin Audit

Call `aitruelabs/truemargin-1688-profit-scout` with the candidate items and channel assumptions:

```bash
apify actors call "aitruelabs/truemargin-1688-profit-scout" \
  -i '{
    "items": [
      "Magnetic POV Neck Phone Holder | 27.99 | 260g",
      "Portable Mini Thermal Pocket Printer | 24.99 | 210g",
      "Cheap Pet Hair Roller | 12.99 | 240g | 15.0"
    ],
    "salesChannel": "tiktok_shop_us",
    "shippingMode": "direct_packet_3pl",
    "creatorAffiliatePct": 15.0,
    "expectedRefundRatePct": 14.0,
    "adSpendCpaUsd": 3.50
  }' \
  --json \
  --user-agent apify-awesome-skills/apify-1688-profit-scout \
  2>/dev/null
```

Fetch the structured audit dataset using `defaultDatasetId` from the run output:

```bash
apify datasets get-items DATASET_ID \
  --format json \
  --user-agent apify-awesome-skills/apify-1688-profit-scout \
  2>/dev/null
```

### Step 4: Synthesize the Go / No-Go Decision Table

Present a clear markdown comparison table and actionable sourcing advice:

1. **Verdict Ranking (`GO` / `CAUTION` / `KILL`)**: Highlight `netProfitPerOrderUsd`, `netMarginPct`, and `breakEvenRoas`. Flag SKUs falling into the "5x markup illusion" where sensitive-line air freight (`BATTERY_MAGNETIC` / `LIQUID_COSMETIC`) and affiliate + RTO bleed wipe out contribution margin.
2. **1688 Primary Factory Sourcing**: Provide the exact `chineseFactoryQuery`, `industrialBelt` (e.g., Shenzhen/Dongguan vs. Yiwu/Ningbo), and clickable `direct1688SearchUrl` (already GBK-encoded so 1688 search does not garble Mandarin characters).
3. **Supplier Authenticity & QC Gates**: List matched factory benchmarks (`repurchaseRatePct` / 回头率) and QC inspection points from `viralAdHooks`.

### Alternative Interfaces

- **Apify MCP connector**: Hosted at <https://mcp.apify.com> (<https://docs.apify.com/platform/integrations/mcp>).
- **MCP CLI (`mcpc`)**: Standalone client at <https://github.com/apify/mcpc>.

## Troubleshooting

- **Garbled Chinese characters on 1688.com**: Never construct `s.1688.com` URLs using UTF-8 percent-encoding; always use the `direct1688SearchUrl` returned by the Actor (GBK byte-encoded).
- **Unexpectedly high freight on lightweight electronics/cosmetics**: Lithium batteries, N52 magnets (`BATTERY_MAGNETIC`), and liquids/pastes (`LIQUID_COSMETIC`) cannot ship via general postal lines and incur sensitive-cargo surcharges (~25–35% higher per-kg DDP rate). Switch `shippingMode` to `sea_ddp_bulk` if testing bulk FBA/3PL restocks.
- See [references/gotchas.md](references/gotchas.md) for cost guardrails and input edge cases.
