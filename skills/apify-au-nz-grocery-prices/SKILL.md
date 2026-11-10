---
name: apify-au-nz-grocery-prices
description: Compare supermarket prices in Australia and New Zealand. Use when the user asks for Coles, Woolworths or ALDI Australia prices, Woolworths New Zealand prices, the cheapest supermarket for a shopping list or basket, this week's specials or half-price deals, unit prices (per 100 g, per litre), grocery price tracking or price-drop alerts, or barcode, ingredients and nutrition data for Australian supermarket products. Routes each store to its pay-per-product Actor, sizes the run so the cost is known before it starts, lines the stores up on unit price and returns one comparison table.
author: highbrow_fame — routes to Actors built by the author; no affiliate or referral parameters
author_url: https://apify.com/highbrow_fame
metadata:
  category: data-extraction
  keywords: "grocery, supermarket, coles, woolworths, aldi, australia, new-zealand, grocery-prices, specials, half-price, unit-price, price-comparison, shopping-list, basket, price-tracking, price-alerts, barcode, nutrition, apify"
---

# Australia and New Zealand grocery prices

Disclosure: the author of this skill built and owns all four Actors it routes to (`highbrow_fame/coles-au-products`, `highbrow_fame/woolworths-au-products`, `highbrow_fame/aldi-au-products`, `highbrow_fame/woolworths-nz-products`). They are pay-per-product Actors on the Apify Store; no referral or tracking parameters are used anywhere in this skill.

Turn "which supermarket is cheaper for this?" into one table: run the same shopping list on each store, keep only rows that really are the product the user meant, compare on unit price instead of shelf price, and say when each price was read. Treat the Actor output as raw search results: a store's search for "milk 2l" also returns flavoured milk and 1 L cartons, so matching is this skill's job, not the Actor's.

## Example prompts

Prompts this skill handles:

- "Where is my shopping list cheapest this week: Coles, Woolworths or ALDI? Milk 2L, a dozen free range eggs, 1 kg bananas, Vegemite 380 g."
- "Show me the half-price specials on coffee and laundry liquid at Coles and Woolworths."
- "Track the price of Weet-Bix 1.2 kg at Woolworths New Zealand and tell me only when it changes."

Out of scope (the boundary):

- "Put these in my cart", "order it for delivery", or anything behind a login (Flybuys, Everyday Rewards, saved lists). This skill only reads public prices.
- Supermarkets outside Australia and New Zealand, or general product pages on other shops: use the `apify-ecommerce` skill in this repository instead.
- Prices from before the first run. Tracking starts when the user starts it; there is no price history to backfill.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

Never put a token into a URL or into a file inside this skill; the CLI sends it as a header for you.

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Step 1: Get the list, the stores and the country
- [ ] Step 2: Route each store to its Actor
- [ ] Step 3: Build the inputs and state the cost
- [ ] Step 4: Run, one Actor per store
- [ ] Step 5: Match, compare on unit price, deliver
```

### Step 1: Get the list, the stores and the country

Ask as one block, and do not start a run before you have the first two:

1. **What** - the products, with size where it matters (`full cream milk 2l`, not `milk`). Write each one the way a shopper types it into the store's search box.
2. **Which stores** - default for Australia: Coles, Woolworths and ALDI. New Zealand: Woolworths NZ.
3. **Specials only?** - yes when the user asks for deals, half price or "what's on special".
4. **A particular Coles store?** - optional. Coles prices can differ by store; without a store the Actor returns the online price.

### Step 2: Route each store to its Actor

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Coles Australia | `highbrow_fame/coles-au-products` | community | search words, category and specials links, prices per store, multi-buy offers |
| Woolworths Australia | `highbrow_fame/woolworths-au-products` | community | search words and links; barcode in every row, ingredients and nutrition where the store publishes them |
| ALDI Australia | `highbrow_fame/aldi-au-products` | community | search words and links, Special Buys with their dates |
| Woolworths New Zealand | `highbrow_fame/woolworths-nz-products` | community | search words only, prices in NZD, club prices and stock level |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party). There is no Apify-maintained Actor for these four stores.

Fetch the input schema before the first call of each Actor; do not build the input from memory:

    apify actors info "highbrow_fame/coles-au-products" --input --json \
      --user-agent apify-awesome-skills/apify-au-nz-grocery-prices 2>/dev/null

### Step 3: Build the inputs and state the cost

The same three fields work on all four Actors:

| Field | Use |
|-------|-----|
| `searchTerms` | array of search words, one per product on the list |
| `maxProductsPerInput` | rows per search word. The default is 100; set 5 for a basket comparison, more only for a category sweep |
| `onlySpecials` | `true` returns only discounted products; skipped full-price products are not charged |

Per-store extras:

| Actor | Extra fields |
|-------|--------------|
| Coles | `urls` (category, specials or product links), `storeNames` or `storeIds` for store prices, `includeDetails` for barcode, ingredients, allergens and nutrition, `onlyNew` + `monitorKey` for tracking |
| Woolworths AU | `urls`, `onlyNew` + `monitorKey` |
| ALDI AU | `urls`, `includeDetails` for description, ingredients and storage |
| Woolworths NZ | `onlyNew` + `monitorKey` (no links) |

**Cost before the run.** One delivered product is one charged row. Rows = search words x `maxProductsPerInput` (x stores, on Coles with stores). Prices in November 2026, per 1,000 products on the Free plan: Coles $1.00, Woolworths AU $0.70, ALDI AU $1.00, Woolworths NZ $0.70; Coles and Woolworths AU are cheaper on paid Apify plans. The current price is on each Actor's Store page. A 10-item list at 5 rows on three Australian stores is 150 rows, about $0.14. Tell the user the row count and the estimate, and ask before any run above 1,000 rows.

### Step 4: Run, one Actor per store

    apify actors call "highbrow_fame/coles-au-products" \
      -i '{"searchTerms":["full cream milk 2l","free range eggs 12 pack"],"maxProductsPerInput":5}' \
      --json \
      --user-agent apify-awesome-skills/apify-au-nz-grocery-prices \
      2>/dev/null

    apify actors call "highbrow_fame/woolworths-au-products" \
      -i '{"searchTerms":["full cream milk 2l","free range eggs 12 pack"],"maxProductsPerInput":5}' \
      --json \
      --user-agent apify-awesome-skills/apify-au-nz-grocery-prices \
      2>/dev/null

    apify actors call "highbrow_fame/aldi-au-products" \
      -i '{"searchTerms":["full cream milk 2l","free range eggs 12 pack"],"maxProductsPerInput":5}' \
      --json \
      --user-agent apify-awesome-skills/apify-au-nz-grocery-prices \
      2>/dev/null

For New Zealand call `highbrow_fame/woolworths-nz-products` with the same input. Each call returns the run with `defaultDatasetId`; read the rows with:

    apify datasets get-items DATASET_ID --format json \
      --user-agent apify-awesome-skills/apify-au-nz-grocery-prices 2>/dev/null

The stores are independent, so the calls can run in parallel. A basket-sized run finishes in well under a minute per store (the two-item example above: 15 to 19 seconds per store, 10 rows each, tested 10 November 2026).

### Step 5: Match, compare on unit price, deliver

1. **Drop non-results.** Keep rows with `status: "OK"`. A row with another `status` and an `error` text is a search that returned nothing; it is not charged. Report it, do not hide it.
2. **Match the product, not the search.** For each list item pick the rows that are the product asked for: same kind, same size. Match Coles and Woolworths AU rows by `barcode` (Woolworths returns it by default, Coles with `includeDetails`). ALDI sells mostly its own brands and has no barcode in the output: match ALDI by product kind and size, and say it is the ALDI equivalent, not the same item. On Coles skip rows with `sponsored: true` unless they are the product asked for.
3. **Compare on unit price.** Every store returns `unitPrice` with `unitMeasure`, but the spelling differs (`1l`, `1L`, `1 L`, `100G`, `100 g`, `1ea`): lower-case it and remove spaces before comparing. The base can differ too (eggs are per 100 g in Australia and per each in New Zealand; some rows are per kg): convert to one base, or compare within one store only when you cannot. If `unitPrice` is missing, compute it from `price` and the pack size.
4. **Show the offer.** `wasPrice`, `savings` and `promotion` say what the special is (`savingsText` and `promotions` on ALDI); Coles adds `multiBuy` ("Buy 2 for $9.40" is cheaper only if the user buys two). On Woolworths NZ `isClubPrice: true` means the price needs the store's loyalty card.
5. **Deliver** one table per list item (store, product, size, price, unit price, special) and a basket total per store that counts only items found in every store, with the unmatched items listed under it. State the `scrapedAt` time and that these are online prices (or the named Coles store's prices).

Field names differ by store:

| Meaning | Coles | Woolworths AU | ALDI AU | Woolworths NZ |
|---------|-------|---------------|---------|---------------|
| Product number | `productId` | `stockcode` | `sku` | `stockcode` |
| Pack size | `size` | `packageSize` | `packSize` | `packageSize` |
| In stock | `isAvailable` | `isInStock` | `isDiscontinued` (reverse) | `isInStock`, `stockLevel` |
| Offer text | `promotion`, `multiBuy` | `promotion`, `isHalfPrice` | `promotions`, `specialBuyText` | `promotion`, `isHalfPrice`, `isClubPrice` |
| Currency | AUD | AUD | AUD | NZD (`currency`) |

`name`, `brand`, `price`, `wasPrice`, `isOnSpecial`, `unitPrice`, `unitMeasure`, `unitPriceText`, `department`, `category`, `url`, `input` and `position` are the same everywhere.

### Tracking a price over time

On Coles, Woolworths AU and Woolworths NZ set `onlyNew: true`. The first run delivers everything and marks each product `isNew: true`. Every later run of the same search delivers only products no earlier run delivered, plus products whose price changed (see `changes` and `previousSeenAt`); seen products are skipped and not charged. `maxProductsPerInput` counts the products checked, not the products delivered, so keep it above the size of the list being watched. Set `monitorKey` (a name for the watch list) to keep one list when the search words are edited, or to keep several lists apart. The list of seen products is kept for 60 days. Schedule the saved input daily in Apify Console. An empty dataset on a later run means "nothing changed", not a failure.

## Troubleshooting

- **Run cost far more than estimated** → `maxProductsPerInput` was left at the default 100, or a specials link was used without a limit (the Coles specials page alone holds thousands of products). Always set the limit.
- **Coles run returns the same product hundreds of times** → `allStores` was on: every search is read once per store. Use `storeNames` for the stores the user named; never set `allStores` without the user asking for a national sweep and agreeing to the row count.
- **Search word returns the wrong things** → make it more specific and add the size (`weet-bix 1.2kg`). A product number on its own works on Coles.
- **No rows with `onlySpecials: true`** → nothing in that search is on special right now. Say so; do not rerun without the filter unless the user wants regular prices.
- **Barcode missing on Coles rows** → `includeDetails` is off. Switch it on only when needed; it reads one extra page per product and is slower.
- **Links ignored on Woolworths NZ** → that Actor takes search words only.
- **Prices differ from the shelf** → without a Coles store the output is the online price; store prices and online prices can differ.
