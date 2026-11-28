---
name: apify-shopify-product-catalog
description: "Read the product catalog of any public Shopify store as JSON, with no API key or store login, using the Apify Actor krammer/shopify-products-scraper. Give it store domains, a collection URL or a product URL; it pages through the store's own public product JSON and returns one record per product with every variant's price, compare-at price, SKU, barcode, stock status, weight, images, options, tags and vendor. Optional: real per-variant stock counts (stores that publish them), recommended products and product-page panels such as Materials or Care. From $0.0008 per product down to $0.00056 on higher Apify plans; failed stores are not charged. Use when the user says export a Shopify store's products to CSV, scrape this Shopify store, what does this store sell, list out-of-stock variants, compare prices between two Shopify stores, track a competitor's catalog or prices, or get a collection's products. The routed Actor is built by this skill's author (see Disclosure)."
author: krammer0
author_url: https://github.com/krammer0
license: MIT
metadata:
  category: ecommerce
  keywords: "shopify, shopify-products, shopify-scraper, product-catalog, ecommerce, competitor-prices, price-monitoring, stock-status, out-of-stock, sku, variants, collection, dtc, no-api-key"
---

# Shopify Store Product Catalog

Get a Shopify store's whole product catalog, one collection, or one product as structured records. The Actor reads the store's own public product JSON, so no Shopify API key, app install or store login is needed.

**Disclosure:** the routed Actor `krammer/shopify-products-scraper` is built and published by the author of this skill. No affiliate or referral parameters are used on any link in this skill.

## Example prompts

Prompts this skill handles:

- "Export every product and variant from allbirds.com to CSV with price and SKU."
- "Which variants are out of stock in this collection: https://example-store.com/collections/sale ?"
- "Compare the prices of the same products on these two Shopify stores."

Out of scope (the boundary):

- Finding Shopify stores by niche, or store owner emails. This skill starts from a store you already know.
- Orders, customers or anything in the Shopify admin. The Actor reads public storefront data only.
- Stores that are not on Shopify, or custom Hydrogen storefronts that do not expose `/products.json` (they are listed in the errors dataset).

## Prerequisites

- Apify account ([sign up](https://apify.com)).
- Authentication via `apify login`, or an `APIFY_TOKEN` environment variable (Apify Console, Settings, Integrations).

## Actor routing

| User need | Actor ID | Tier | Billed event |
|-----------|----------|------|--------------|
| Products and variants of a public Shopify store, collection or product | `krammer/shopify-products-scraper` | community | `product` $0.0008 → $0.00056 per product by Apify plan; `collection` $0.00032; `recommends`, `real-inventory`, `content-sections` $0.0008 each, only when you turn them on |

## Workflow

1. Get the store domain (`allbirds.com`) or a collection / product URL.
2. Check the live input schema before you build the input:

        apify actors info "krammer/shopify-products-scraper" --input --json \
          --user-agent apify-awesome-skills/apify-shopify-product-catalog 2>/dev/null

3. Cap the cost: set `maxRequestsPerCrawl` (records for the whole run) or `maxProductsPerStore`. Large stores have thousands of products. Try 20 first, and ask the user before a run above about $1.
4. Run the Actor and read the dataset:

        apify actors call "krammer/shopify-products-scraper" \
          -i '{"domains": ["allbirds.com"], "maxRequestsPerCrawl": 20}' \
          --json --user-agent apify-awesome-skills/apify-shopify-product-catalog 2>/dev/null

    `DATASET_ID` is `storage.defaultDatasetId` in the JSON that `actors call` prints; `run.status` must be `SUCCEEDED`.

        apify datasets get-items DATASET_ID --format json \
          --user-agent apify-awesome-skills/apify-shopify-product-catalog 2>/dev/null

5. Deliver: number of products and variants, a table, and the dataset ID. Say which stores failed and why (errors dataset).

## Input fields

| Field | Default | Notes |
|---|---|---|
| `domains` | — | One store per entry, for example `kith.com`. Whole catalog. |
| `startUrls` | — | A store root, a collection page or a product page. Use this for one collection or one product. |
| `query` | — | Keep only products whose title, vendor, product type or tags contain this text. |
| `maxRequestsPerCrawl` | `0` | Most records saved in the whole run. `0` = no limit. |
| `maxProductsPerStore` | `0` | Most products per store. `0` = no limit. |
| `grabRealInventory` | `false` | Real per-variant stock counts, for stores that publish them. Billed per product with a count. |
| `maxRecommendationsPerProduct` | `0` | Recommended products per product, max 20. Billed per recommended product. |
| `grabContentSections` | `false` | Product-page panels such as Features, Materials or Care. Billed per product with panels. |
| `proxy` | — | Apify Proxy configuration, for stores that block automated requests. |

## Output fields

Product: `title`, `brand`, `description`, `tags`, `categories`, `options`, `medias`, `price`, `priceRange`, `fullyOutOfStock`, `variants`, `source` (`canonicalUrl`, `currency`, `retailer`, `createdUTC`, `updatedUTC`).

Each variant: `id`, `title`, `sku`, `barcode`, `price` (`current`, `previous`, `stockStatus`), `quantityAvailable`, `weight`, `weightUnit`, `options`.

**Prices are integers in minor units:** `6000` means 60.00 in `source.currency`. `price.previous` is the compare-at price (`0` when there is none).

## Calling Actors — other interfaces

- Apify MCP connector: `https://mcp.apify.com/?tools=krammer/shopify-products-scraper` ([docs](https://docs.apify.com/platform/integrations/mcp)).
- [mcpc](https://github.com/apify/mcpc) or any MCP client.

## Troubleshooting

- **404 for a store:** a custom Hydrogen storefront without `/products.json`. Nothing to fix from the input.
- **429 (Vercel Security Checkpoint) or 403 (Cloudflare 1010):** run again later, or set `proxy`.
- **Fewer products than the store shows:** `maxRequestsPerCrawl` or `maxProductsPerStore` stopped the run. Raise or clear it.
- **Prices look 100 times too big:** they are minor units; divide by 100 for most currencies.
