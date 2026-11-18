---
name: apify-china-sourcing
description: This skill should be used when the user asks to "find suppliers on 1688", "search 1688 for a product", "get the price tiers and MOQ for this 1688 link", "find Alibaba suppliers", "compare 1688 and Alibaba prices", "source a product from China", "find a factory for", or wants wholesale prices, minimum order quantities, SKU variants or supplier details from 1688.com or Alibaba.com. It picks the right Apify Actor for search vs product page, builds a valid input, keeps the run cheap, and returns a comparison in USD with English titles. Do not use it for Taobao, Tmall, AliExpress or Amazon retail listings.
license: MIT
metadata:
  version: "1.0"
  category: data-extraction
  keywords: "1688, alibaba, china sourcing, wholesale prices, MOQ, price tiers, suppliers, factory, product sourcing, dropshipping sourcing, apify"
---

# Source products from China with Apify: 1688.com and Alibaba.com

Find wholesale products and suppliers on 1688.com (China's domestic wholesale site, prices in CNY) and Alibaba.com (export site, prices in USD), then pull quantity price tiers, minimum order (MOQ), variants and supplier facts for the shortlisted items.

Disclosure: the Actors this skill routes to are paid (pay per result) and built by the skill author. Links carry no affiliate parameters.

## Example prompts

Prompts this skill handles:

- "Search 1688 for yoga mats and give me 30 products with price in USD and units sold."
- "Here is a 1688 link https://detail.1688.com/offer/787646790056.html — what are the price tiers, MOQ and variants?"
- "Find Alibaba suppliers of LED strip lights with MOQ under 100 and Trade Assurance. About 20."
- "Compare the 1688 and Alibaba price for bluetooth earphones."

Out of scope (the boundary):

- "Find this product on Taobao / AliExpress / Amazon" — retail marketplaces; use a general e-commerce skill instead.
- Placing orders, contacting suppliers or negotiating — this skill only reads public listings.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. **Decide the site.** Domestic factory prices, Chinese suppliers, lowest unit price → 1688. Export-ready suppliers, English listings, Trade Assurance, MOQ filter → Alibaba. "Compare" → run both with the same keyword.
2. **Decide search vs product page.** A keyword → a search Actor. A product link or ID → the product-page Actor. Never invent a product URL: search first, then take `url` from the rows.
3. **Search cheap, then open only the shortlist.** Run the search without `includeDetails`, pick 3–10 rows with the user (or by price / `soldCount` / supplier years), then fetch product pages for those URLs only. Product pages cost about 9× a search row on 1688 and about 4× on Alibaba.
4. **Comparing the two sites.** Do not try to match identical products across sites. Compare the price band for the same keyword: on 1688 the median and lowest `priceUsd`, on Alibaba the lowest tier price in `priceTiers` at the user's quantity, and say that 1688 prices are domestic (no export service) while Alibaba prices are export quotes.
5. **Report.** Give a table: title (English), price (USD and CNY for 1688), MOQ, price tiers, units sold, supplier name, years, location, link. Say how many rows were returned and what the run cost (`usageTotalUsd` plus billed rows).

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Search 1688 by keyword (English or Chinese) | `blueskyscraper/1688-products-scraper` | community | Price in CNY and USD, units sold, repeat-buyer rate, supplier type, years, province |
| One 1688 product page by URL | `blueskyscraper/1688-product-details-scraper` | community | Price tiers, MOQ, every variant with price and stock, specifications, weight, supplier |
| Search Alibaba.com by keyword | `blueskyscraper/alibaba-products-scraper` | community | Price range, price tiers and MOQ already in search rows; supplier country, years, badges |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Inputs that work

Always fetch the live schema before the first call in a session — fields can change:

    apify actors info "blueskyscraper/1688-products-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-china-sourcing 2>/dev/null

**1688 search.** Keywords may be English; they are translated to Chinese for the search and titles come back in English as `titleEn`.

    apify actors call "blueskyscraper/1688-products-scraper" \
      -i '{"keywords":["yoga mat"],"maxResultsPerInput":30,"sortBy":"sales"}' \
      --json --user-agent apify-awesome-skills/apify-china-sourcing 2>/dev/null

Useful fields: `minPriceCny`, `maxPriceCny` (1 USD ≈ 7.1 CNY), `manufacturersOnly` (factories only), `provinces` (in Chinese, e.g. `["广东"]`), `sortBy` (`bestMatch` or `sales`), `excludeAds`.
There is no price sort: for "cheapest first" fetch the rows and sort them by `priceUsd` yourself. `maxItems` caps the whole run on all three Actors.
Row fields: `titleEn`, `priceCny`, `priceUsd`, `soldCount`, `repurchaseRate`, `supplierName`, `supplierType`, `supplierYears`, `supplierProvince`, `url`.
**Search rows do not carry MOQ or price tiers** — open the product page for those.

**1688 product page.**

    apify actors call "blueskyscraper/1688-product-details-scraper" \
      -i '{"productUrls":["https://detail.1688.com/offer/787646790056.html"]}' \
      --json --user-agent apify-awesome-skills/apify-china-sourcing 2>/dev/null

Row fields: `priceTiers`, `minOrder`, `unit`, `priceMinCny`, `priceMaxCny`, `priceMinUsd`, `priceMaxUsd`, `stock`, `variants`, `variantsEn`, `attributesEn`, `weightKgMin`, `shipsFrom`, `supplierName`.

**Alibaba search.** MOQ and tiers are in the search rows, so a product page is rarely needed.

    apify actors call "blueskyscraper/alibaba-products-scraper" \
      -i '{"keywords":["led strip light"],"maxResultsPerInput":20,"maxMinOrder":100,"tradeAssuranceOnly":true}' \
      --json --user-agent apify-awesome-skills/apify-china-sourcing 2>/dev/null

Useful fields: `minPrice`, `maxPrice` (USD), `maxMinOrder`, `supplierCountries` (ISO codes, e.g. `["CN","VN"]`), `tradeAssuranceOnly`, `verifiedSupplierOnly`, `minSupplierRating`.
Row fields: `title`, `priceMin`, `priceMax`, `priceTiers`, `minOrder`, `minOrderText`, `supplierName`, `supplierCountry`, `supplierYears`, `url`.

**Read the rows.** The call returns `defaultDatasetId`:

    apify datasets get-items DATASET_ID --format json \
      --user-agent apify-awesome-skills/apify-china-sourcing 2>/dev/null

Rows with `type` of `notice` or `error` are explanations, not products — read them to the user instead of counting them.

## Calling Actors — choose your interface

The commands above use the Apify CLI. The same Actors and inputs work through the Apify MCP connector at <https://mcp.apify.com> (`call-actor` with the same input JSON; add `?tools=blueskyscraper/1688-products-scraper` to pin one Actor as a tool) or an MCP client such as [mcpc](https://github.com/apify/mcpc).

## Troubleshooting

- **The user wants MOQ for a 1688 search.** Search rows have no MOQ. Shortlist first, then run the product-page Actor on those URLs. Do not set `includeDetails: true` on a large search unless the user accepts the cost.
- **Zero rows on 1688.** Use a shorter product name (two or three words), drop `provinces` and price filters, or try the Chinese term.
- **A keyword returns unrelated goods.** Add the material or use case ("silicone yoga mat"), or sort by `sales`.
- **The product page returns an empty `priceTiers`.** The product has one price for any quantity: report `priceMinCny` / `priceMinUsd` and `minOrder`.
- **The link is `m.1688.com` or a short link.** Pass it as is in `productUrls`; mobile links are accepted.
- For cost guardrails see [references/gotchas.md](references/gotchas.md).
