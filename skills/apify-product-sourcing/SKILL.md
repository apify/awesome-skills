---
name: apify-product-sourcing
description: Find where to buy a product wholesale in China (1688, Taobao, AliExpress) and what it sells for retail (Amazon, Google Shopping, TikTok Shop), then show buy price, minimum order, sell price and gross margin side by side. Use when the user asks to source a product, find a supplier or manufacturer in China, check dropshipping or private-label margins, compare 1688 or AliExpress prices with Amazon prices, or asks "where can I buy this cheaper". Runs Apify Actors through the Apify MCP server.
author: UnseenUser
author_url: https://github.com/UnseenUser
metadata:
  category: data-extraction
  keywords: "product sourcing, wholesale, 1688, taobao, aliexpress, amazon, google shopping, tiktok shop, dropshipping, private label, supplier, margin, china"
---


# Product Sourcing: China Wholesale vs. Retail Price

Given a product (a name, a keyword, or an Amazon link), this skill finds:
1. **What it sells for** on Amazon, Google Shopping and TikTok Shop.
2. **What it costs to buy** on 1688, Taobao and AliExpress.
3. **The margin** between the two, in one table with links.

It uses six Apify Actors through the Apify MCP server (`https://mcp.apify.com`). Start each run with the `call-actor` tool using `waitSecs: 0`, wait with `get-actor-run`, and read rows with `get-dataset-items` (pass `fields` to keep only the columns listed below). Check an Actor's input with `fetch-actor-details` if anything below is unclear.

Free Apify accounts can run at most 5 Actors at the same time. Run Step 1 (3 Actors) and Step 2 (3 Actors) one after the other, not all six at once.


> Disclosure: all six Actors this skill routes to are paid Actors built by the skill's author (Apify user `unseenuser`). No affiliate or referral codes are used in any link.

## Example prompts

Prompts this skill handles:

- "Source a silicone phone case and tell me the margin."
- "Find 1688 suppliers for this Amazon product: https://www.amazon.com/dp/B0DRF9WYV5"
- "What does a LED face mask cost wholesale in China vs. on TikTok Shop?"

Out of scope (the boundary):

- "Track the price of this Amazon product every day." That is price monitoring of one listing; use a single Amazon or Google Shopping Actor on a schedule instead.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- The Apify MCP server connected to your agent: `https://mcp.apify.com` (OAuth sign-in, no token needed)

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Amazon retail price | `unseenuser/amazon-products` | community | Price, rating, reviews and monthly sales by keyword or ASIN, 21 marketplaces |
| Price across web stores | `unseenuser/google-shopping-scraper` | community | Prices from many stores at once |
| TikTok Shop retail price | `unseenuser/TikTok-Shop-Scraper` | community | Price, units sold and rating on TikTok Shop (US) |
| 1688 wholesale price | `unseenuser/1688-wholesale-product-search` | community | Factory price, quantity price ladder (MOQ), supplier, English titles |
| Taobao and Tmall price | `unseenuser/taobao-product-search` | community | Small-quantity China prices, English titles |
| AliExpress price | `unseenuser/aliexpress-product-search` | community | Single-unit price in USD, shipped to the buyer's country |

## Step 0: understand the request

Work out, and ask only if it is truly unclear:
- **Product**: a short English search phrase of 2 to 5 words (for example `silicone phone case iphone 15`). If the user gave an Amazon link or ASIN, use it in Step 1 and build the phrase from the product title it returns.
- **Retail market**: default the United States. Use the matching Amazon marketplace, Google Shopping country and TikTok Shop region.
- **How many results per source**: default 10. Use more only if the user asks.
- **Which sources**: default all six. If the user names only some ("just 1688 and Amazon"), run only those.

## Step 1: retail prices (what it sells for)

Run these in parallel.

**Amazon** `unseenuser/amazon-products`
```json
{ "keywords": ["<search phrase>"], "marketplace": "US", "maxProductsPerKeyword": 10, "includeSponsored": false }
```
For an Amazon link or ASIN instead: `{ "asins": ["<ASIN or URL>"], "marketplace": "US" }`.
Use: `title`, `price`, `currency`, `rating`, `reviewsCount`, `boughtPastMonth`, `url`.

**Google Shopping** `unseenuser/google-shopping-scraper`
```json
{ "queries": ["<search phrase>"], "country": "United States", "language": "en", "maxProductsPerQuery": 10 }
```
Use: `title`, `price`, `currency`, `merchant` (the store, which can itself be Amazon, eBay or TikTok Shop), `rating`, `reviewCount`, `productUrl` (a Google Shopping link).

**TikTok Shop** `unseenuser/TikTok-Shop-Scraper`
```json
{ "mode": "shop_search", "searchKeywords": ["<search phrase>"], "region": "US", "maxResults": 10 }
```
Always set `maxResults`; 0 means every result. The US is the only fully supported region.
Use: `title`, `price`, `currency`, `soldCount`, `rating`, `reviewCount`, `shopName`, `productUrl`.

## Step 2: wholesale prices (what it costs to buy)

Run these in parallel. All three accept English keywords and translate them for you.

**1688** `unseenuser/1688-wholesale-product-search`
```json
{ "keywords": ["<search phrase>"], "maxProductsPerKeyword": 10, "translateTitles": true }
```
Use: `titleEn`, `price`, `currency`, `priceTiers` (quantity price ladder, for example `2~499个` at 7.5 and `≥8000个` at 6.5; 个 means pieces), `isFactory`, `supplierCompany` (in Chinese), `city`, `soldCount`, `url`. Prices are in Chinese yuan (CNY). The lowest quantity in `priceTiers` is the minimum order; if `priceTiers` is empty, show the minimum order as unknown.
For exact minimum order quantities, add `"fetchDetails": true`; it adds the full price ladder with MOQ, specs and shipping promise per product and takes longer.

**Taobao and Tmall** `unseenuser/taobao-product-search`
```json
{ "keywords": ["<search phrase>"], "maxProductsPerKeyword": 10, "translateTitles": true }
```
Use: `titleEn`, `price`, `currency`, `salesCount` (can be empty), `shopName`, `location`, `url`. Prices are in CNY. Taobao sells mostly single units; treat it as a small-quantity buying option.

**AliExpress** `unseenuser/aliexpress-product-search`
```json
{ "keywords": ["<search phrase>"], "maxProductsPerKeyword": 10, "sort": "salesDesc", "shipTo": "US", "currency": "USD", "language": "en_US" }
```
Use: `title`, `price`, `currency`, `salesCount`, `rating`, `productUrl`. Prices are already in USD and include the ship-to market's view.

## Step 3: clean the results

- **Keep only product rows.** Every dataset can also contain summary or notice rows. Drop any row whose `status` is `info`, `no_data` or `error`, any row with a `type` field (for example `KEYWORD_SUMMARY` or `FREE_PLAN_LIMIT`), and any row without both a title and a price.
- **Drop products that are not the same item.** Compare titles with the search phrase; remove accessories, bundles and unrelated items. Say how many you removed.
- **Convert CNY to USD.** Use a current exchange rate if a tool can look one up; otherwise use 7.1 CNY per USD and state the rate you used.
- **Retail price per source**: the median price of the matching products (state how many products it is based on), plus the lowest and highest.
- **Buy price per source**: the lowest price among the matching products with real sales (`soldCount` or `salesCount` above 0), and the median.

## Step 4: the answer

Lead with one sentence: the typical retail price, the typical wholesale price, and the gross margin.

Then one table, best options first:

| Source | Product | Buy price (USD) | Min. order | Sold | Supplier / store | Link |
|---|---|---|---|---|---|---|

Then a short retail table:

| Marketplace | Median price | Range | Products compared |
|---|---|---|---|

Then the margin:
- **Gross margin per unit** = median retail price minus buy price.
- **Gross margin %** = that difference divided by the median retail price.
- Say clearly that this is before shipping, import duties, marketplace fees and returns, and show the numbers for the best two or three supplier options.

If a source returned nothing, say so in one line and carry on with the rest.

## Notes for the agent

- On a free Apify plan each of these Actors returns up to 5 products per run and at most 5 Actors can run at the same time. If you get 5 products when you asked for 10, that is why.
- Each Actor run takes about 1 to 3 minutes. Start all runs of a step at once, then collect results.
- Never invent prices, suppliers or links. Every number in the answer must come from a dataset row.
