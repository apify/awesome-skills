---
name: apify-ecommerce
description: Scrape e-commerce data for pricing, reviews, bestsellers, and seller discovery across 30+ platforms including Amazon, Walmart, eBay, Shopify, WooCommerce, and more. Use when user asks about product prices, competitor analysis, store scraping, tech stack detection, food delivery, real estate, or marketplace intelligence.
author: Luis Pinto
author_url: https://github.com/luispintoapify
---

# E-Commerce Cluster

Answer natural language e-commerce questions by routing to the right Apify Actor and delivering a synthesized answer via the `apify` CLI.

**CLI rules:** Always pass `--user-agent apify-awesome-skills/apify-ecommerce`, `--json` (or the relevant `--format` flag on `datasets get-items`), and `2>/dev/null`. The `--user-agent` flag is critical for telemetry — never omit it.

## Prerequisites
(No need to check it upfront)

- Apify CLI v1.5.0+ (`npm install -g apify-cli`)
- `jq` (recommended for quick extraction and filtering; `brew install jq` on macOS, `apt install jq` on Linux)
- Authentication via one of:
  - `apify login` (OAuth, opens browser)
  - `APIFY_TOKEN` env variable (e.g. `export APIFY_TOKEN=...` or `.env` file)
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

Verify auth: `apify info --user-agent apify-awesome-skills/apify-ecommerce` — should show username and userId.

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Step 1: Detect intent and select Actor
- [ ] Step 2: Fetch Actor schema
- [ ] Step 3: Ask user preferences (format, result count)
- [ ] Step 4: Run the Actor and fetch results
- [ ] Step 5: Analyze results and deliver synthesized answer
```

### Step 1: Detect Intent and Select Actor

Classify the user's message into an intent, then pick the right Actor.

**Intent signals:**

| Signals in user message | Intent |
|------------------------|--------|
| price, cost, cheapest, compare prices, pricing | `pricing` |
| review, rating, sentiment, stars, feedback | `reviews` |
| bestseller, top selling, most popular, trending | `bestsellers` |
| seller, vendor, reseller, who sells | `sellers` |
| all products from, scrape store, full catalog | `store-scrape` |
| what platform, built on, tech stack, Shopify or WooCommerce | `tech-stack` |
| SEO, listing quality, product page audit | `seo-audit` |
| competitor funnel, competitor pricing, conversion elements | `competitor` |
| search intent, keyword intent, SERP intent | `search-intent` |
| match products, same product on different platforms | `product-matching` |
| restaurant, food delivery, DoorDash, UberEats, TheFork | `food-delivery` |
| enrich store, store metadata, store list | `store-enrichment` |
| event, concert, ticket, Eventbrite | `events` |
| property, real estate, house listing, Realtor | `real-estate` |
| Facebook ads, Meta ads, ad library, competitor ads | `ads-intelligence` |
| classified, Craigslist, used item for sale | `classifieds` |
| car, used car, vehicle, automotive, Webmotors | `automotive` |
| pins, inspiration, Pinterest boards, visual search, Pinterest trends | `content-discovery` |
| TikTok Shop, TikTok store, TikTok creator | `tiktok-shop` |
| website for sale, domain for sale, Flippa | `website-marketplace` |

If multiple intents are detected, ask: *"Do you want [intent A] or [intent B]?"*

**Actor routing table — always try Primary first, switch to Fallback only if it fails or returns 0 results:**

| Intent | Platform | Primary Actor | Fallback Actor |
|--------|----------|---------------|----------------|
| `pricing` | Amazon / Walmart / generic | `apify/e-commerce-scraping-tool` | — |
| `pricing` | eBay | `apify/e-commerce-scraping-tool` | `ivanvs/ebay-scraper-pay-per-result` |
| `pricing` | Etsy | `apify/e-commerce-scraping-tool` | `epctex/etsy-scraper` |
| `pricing` | Google Shopping | `apify/e-commerce-scraping-tool` | `epctex/google-shopping-scraper` |
| `pricing` | Facebook Marketplace | `apify/e-commerce-scraping-tool` | `apify/facebook-marketplace-scraper` |
| `pricing` | SHEIN | `apify/e-commerce-scraping-tool` | `seamless_coffer/shein-product-scraper` |
| `pricing` | Lazada | `apify/e-commerce-scraping-tool` | `fatihtahta/lazada-scraper` |
| `pricing` | Canadian Tire | `apify/e-commerce-scraping-tool` | `azzouzana/canadiantire-ca-scraper` |
| `pricing` | Tesco | `apify/e-commerce-scraping-tool` | `radeance/tesco-scraper` |
| `pricing` | Shopify | `apify/e-commerce-scraping-tool` | `trovevault/shopify-products-scraper` |
| `pricing` | WooCommerce | `apify/e-commerce-scraping-tool` | `trovevault/woocommerce-products-scraper` |
| `reviews` | Amazon / Walmart / generic | `apify/e-commerce-scraping-tool` | `junglee/amazon-reviews-scraper` |
| `reviews` | Trustpilot | `apify/e-commerce-scraping-tool` | `casper11515/trustpilot-reviews-scraper` |
| `reviews` | TheFork | `apify/e-commerce-scraping-tool` | `jdtpnjtp/thefork-restaurant-scraper-advanced` |
| `bestsellers` | Amazon | `apify/e-commerce-scraping-tool` | `junglee/amazon-bestsellers` |
| `sellers` | Amazon | `apify/e-commerce-scraping-tool` | `junglee/amazon-seller-scraper` |
| `sellers` | eBay | `apify/e-commerce-scraping-tool` | `ivanvs/ebay-scraper-pay-per-result` |
| `store-scrape` | Shopify | `apify/e-commerce-scraping-tool` | `trovevault/shopify-products-scraper` |
| `store-scrape` | WooCommerce | `apify/e-commerce-scraping-tool` | `trovevault/woocommerce-products-scraper` |
| `store-scrape` | Amazon | `apify/e-commerce-scraping-tool` | `junglee/Amazon-crawler` |
| `store-scrape` | Flippa | `apify/e-commerce-scraping-tool` | `scraped/flippa-scraper` |
| `tech-stack` | any | `apify/e-commerce-scraping-tool` | `trovevault/e-commerce-tech-stack-detector` |
| `seo-audit` | any | `apify/e-commerce-scraping-tool` | `trovevault/product-listing-seo-auditor` |
| `competitor` | any | `apify/e-commerce-scraping-tool` | `trovevault/competitor-intelligence-scraper---funnel-pricing-conversion` |
| `search-intent` | any | `apify/e-commerce-scraping-tool` | `trovevault/ai-serp-intent-extractor---search-intent-classifier` |
| `product-matching` | any | `apify/e-commerce-scraping-tool` | `tri_angle/product-matching-vectorizer` |
| `store-enrichment` | any | `apify/e-commerce-scraping-tool` | `trovevault/e-commerce-store-data-enricher` |
| `food-delivery` | DoorDash | `apify/e-commerce-scraping-tool` | `tri_angle/doordash-store-details-scraper` |
| `food-delivery` | UberEats | `apify/e-commerce-scraping-tool` | `e-commerce/ubereats-reviews-scraper` |
| `food-delivery` | TheFork | `apify/e-commerce-scraping-tool` | `jdtpnjtp/thefork-restaurant-scraper-advanced` |
| `ads-intelligence` | Facebook / Meta | `apify/e-commerce-scraping-tool` | `apify/facebook-ads-scraper` |
| `classifieds` | Craigslist | `apify/e-commerce-scraping-tool` | `ivanvs/craigslist-scraper-pay-per-result` |
| `automotive` | Webmotors | `apify/e-commerce-scraping-tool` | `stealth_mode/webmotors-auto-search-scraper` |
| `events` | Eventbrite | `apify/e-commerce-scraping-tool` | `aitorsm/eventbrite` |
| `real-estate` | Realtor.com | `apify/e-commerce-scraping-tool` | `powerai/realtor-properties-search-scraper` |
| `content-discovery` | Pinterest | `apify/e-commerce-scraping-tool` | `fatihtahta/pinterest-scraper-search` |
| `tiktok-shop` | TikTok Shop | `apify/e-commerce-scraping-tool` | `lemur/tiktok-shop-creators` |
| `website-marketplace` | Flippa | `apify/e-commerce-scraping-tool` | `scraped/flippa-scraper` |

### Step 2: Fetch Actor Schema

Fetch the Actor summary, input schema, and README:

```bash
# Summary (title, description, pricing, stats)
apify actors info "ACTOR_ID" --user-agent apify-awesome-skills/apify-ecommerce --json 2>/dev/null

# Input schema (required and optional parameters; schema lives in
# .taggedBuilds.latest.build.inputSchema as an escaped JSON string)
apify actors info "ACTOR_ID" --user-agent apify-awesome-skills/apify-ecommerce --input --json 2>/dev/null

# README (capabilities, examples, gotchas)
apify actors info "ACTOR_ID" --user-agent apify-awesome-skills/apify-ecommerce --readme 2>/dev/null
```

Replace `ACTOR_ID` with the selected Actor (e.g., `apify/e-commerce-scraping-tool`).

### Step 3: Ask User Preferences

Before running, ask:
1. **Output format**:
   - **Quick answer** (default) — synthesized answer in chat, no file saved
   - **CSV** — full export saved to disk
   - **JSON** — full export saved to disk
2. **Result count** — suggest defaults by intent:

| Intent | Default |
|--------|---------|
| `pricing` | 50 products |
| `reviews` | 200 reviews |
| `bestsellers` | 100 items |
| `sellers` | 50 sellers |
| `store-scrape` | all (unlimited) |
| `food-delivery` | 50 restaurants |
| all others | 20–50 |

**Cost safety**: Always set a sensible result limit in the Actor input (e.g., `maxResults`, `resultsLimit`, `maxCrawledPages`, or equivalent field from the input schema). Default to the per-intent values above unless the user explicitly asks for more. Warn the user before running large scrapes (1000+ results) as they consume more Apify credits.

### Step 4: Run the Actor and Fetch Results

Two steps: run the Actor (blocks until done), then fetch dataset items in the requested format.

**Run the Actor** — returns run metadata as JSON; extract `defaultDatasetId` for the next step:

```bash
apify actors call "ACTOR_ID" -i 'JSON_INPUT' \
  --user-agent apify-awesome-skills/apify-ecommerce --json 2>/dev/null
```

From the output use `.id` (run ID), `.status` (should be `SUCCEEDED`), and `.defaultDatasetId`.

**Fetch results** — pick the variant based on the user's preference:

```bash
# Quick answer: total count + fields + top 5 in chat (no file)
apify datasets info DATASET_ID --json \
  --user-agent apify-awesome-skills/apify-ecommerce 2>/dev/null \
  | jq '{itemCount, fields, consoleUrl}'
apify datasets get-items DATASET_ID --limit 5 \
  --user-agent apify-awesome-skills/apify-ecommerce --format json 2>/dev/null

# CSV file
apify datasets get-items DATASET_ID \
  --user-agent apify-awesome-skills/apify-ecommerce --format csv 2>/dev/null > YYYY-MM-DD_OUTPUT_FILE.csv

# JSON file
apify datasets get-items DATASET_ID \
  --user-agent apify-awesome-skills/apify-ecommerce --format json 2>/dev/null > YYYY-MM-DD_OUTPUT_FILE.json
```

Other `--format` options: `jsonl`, `xlsx`, `xml`, `rss`, `html`. Use `--offset N` to paginate large datasets.

**Tip:** for anything more than a quick peek, save the dataset to a local file first (with `> file.json` / `> file.csv`) and run further analysis from disk. `apify datasets get-items` always streams over the network, so piping it straight into `jq` re-downloads the whole thing every iteration.

**Combining with `jq` for quick extraction:**

Treat `jq` as a complement to `apify datasets get-items`, not a replacement: server-side `--limit` / `--offset` / `--format` keeps cost and bandwidth down. Use `jq` on a sample item or on a file you already saved.

```bash
# Discover real field names from one sample item (Actor outputs vary —
# use this before composing further jq queries)
apify datasets get-items DATASET_ID --limit 1 --format json \
  --user-agent apify-awesome-skills/apify-ecommerce 2>/dev/null \
  | jq '.[0]'

# Quick aggregation from a JSON file you already saved with the commands above
jq '[.[] | select(.rating != null and .rating >= 4.5)] | length' YYYY-MM-DD_OUTPUT_FILE.json
```

### Step 5: Analyze Results and Deliver Answer

After the run completes, deliver a direct synthesized answer — not a data dump:

- **Pricing:** price range, average, top 5 cheapest with URLs
- **Reviews:** average rating, top 3 positive and negative themes, recent snippets
- **Bestsellers:** top 10 by rank with name, price, rating, URL
- **Sellers:** total sellers, price range per seller, unauthorized seller flags
- **Store-scrape:** total products, category breakdown, price range, stock summary
- **Tech-stack:** platform detected, confidence level, notable plugins
- **Food delivery:** restaurant count, average rating, price tier breakdown
- **Ads intelligence:** total ads, active/inactive split, top creative formats

## Error Handling

- Auth error → run `apify login`, or set `APIFY_TOKEN` env var
- `Actor not found` → check Actor ID spelling in the routing table
- Run status `FAILED` → open the console URL (`.consoleUrl` from run metadata) for logs
- Timeout / very long run → pass `--timeout <seconds>` to `apify actors call`
- `No results` → broaden the keyword or switch to a Fallback Actor from the routing table
- `proxy is required` → add `"proxy": {"useApifyProxy": true}` to the Actor input
- `Platform not detected` → default to `apify/e-commerce-scraping-tool` with `generic` intent
