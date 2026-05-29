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

**Actor routing table — always try Primary first, switch to Fallback only if it fails or returns 0 results.** The Primary actor (`apify/e-commerce-scraping-tool`) handles most intents once you feed the right input mode:

- **Have target URLs** (a listing, profile, or category page) → `detailsUrls` / `listingUrls`.
- **Have a keyword/marketplace** → `keyword` + `marketplaces` (product-details mode).
- **Broad discovery (competitor, search-intent, classifieds, automotive, real-estate, website-marketplace, events)** → use `searchEngineKeyword` (search-engine mode) or `keyword`/`detailsUrls` depending on whether you have a query or URLs.

**Exception — skip the Primary and go straight to the Fallback** for intents the Primary genuinely can't do (different data source or specialized analysis): `tech-stack`, `seo-audit`, `store-enrichment`, `product-matching`, `ads-intelligence`, `content-discovery` (Pinterest), and `tiktok-shop`. Routing these to the Primary wastes a run and credits.

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

**Escalation — if both Primary and Fallback fail or return 0 results**, discover a current alternative live instead of guessing an ID:

```bash
# Find relevant, well-rated, pay-per-event Actors for the platform/intent.
# Keep the default relevance sort — `--sort-by popularity` surfaces generic
# big-name scrapers over the platform you actually asked for.
apify actors search "PLATFORM or INTENT keywords" \
  --pricing-model PAY_PER_EVENT --limit 10 --json \
  --user-agent apify-awesome-skills/apify-ecommerce 2>/dev/null \
  | jq '[.items[]
      | select(.stats.totalUsers > 100 and .actorReviewRating > 4.5)
      | {id: (.username + "/" + .name), users: .stats.totalUsers,
         rating: (.actorReviewRating | (. * 100 | round / 100)),
         pricing: .currentPricingInfo.pricingModel}]'
```

Pick the top match. Before running it, confirm it requests only **limited permissions** (check the Actor's Store page / README — prefer Actors that don't require full account access). If the `PAY_PER_EVENT` filter returns nothing, drop the `--pricing-model` flag and re-run, keeping the ≥100-users and ≥4.5-rating bar.

### Step 2: Fetch Actor Schema

Fetch the Actor summary, input schema, and README:

```bash
# Summary (title, description, pricing, stats)
apify actors info "ACTOR_ID" --user-agent apify-awesome-skills/apify-ecommerce --json 2>/dev/null

# Input schema — use --input WITHOUT --json to get the clean schema directly.
# (Adding --json returns the full ~250 KB actor object instead, with the schema
#  buried as an escaped string under .taggedBuilds.latest.build.inputSchema.)
apify actors info "ACTOR_ID" --user-agent apify-awesome-skills/apify-ecommerce --input 2>/dev/null

# README (capabilities, examples, gotchas)
apify actors info "ACTOR_ID" --user-agent apify-awesome-skills/apify-ecommerce --readme 2>/dev/null
```

Replace `ACTOR_ID` with the selected Actor (e.g., `apify/e-commerce-scraping-tool`).

**Primary actor input cheat-sheet.** `apify/e-commerce-scraping-tool` is mode-driven — pick fields by intent (always set the matching `max…Results` cap):

| Intent | Minimal input |
|--------|---------------|
| `pricing` (keyword) | `{"keyword": "wireless earbuds", "marketplaces": ["www.amazon.com"], "maxProductResults": 50}` |
| `pricing` (specific URLs) | `{"detailsUrls": [{"url": "https://…"}], "maxProductResults": 50}` |
| `store-scrape` (category) | `{"listingUrls": [{"url": "https://…/category"}], "maxProductResults": 500}` |
| `reviews` | `{"keywordReviews": "echo dot", "marketplacesReviews": ["www.amazon.com"], "sortReview": "Most recent", "maxReviewResults": 200}` |
| `sellers` | `{"sellerUrls": [{"url": "https://…"}], "maxSellerResults": 50}` |
| `pricing` (Google Shopping) | `{"searchEngineKeyword": "ps5", "countryCode": "us", "maxSearchEngineResults": 50}` |
| `food-delivery` | `{"keywordDelivery": "pizza", "marketplacesDelivery": ["www.doordash.com"], "addressDelivery": "New York, NY", "maxDeliveryResults": 50}` |

For any other actor (or fields not listed), fetch the schema with the `--input` command above.

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

**Cost safety**: Always set a sensible result limit in the Actor input. For the Primary actor the cap field is **mode-specific** — `maxProductResults`, `maxReviewResults`, `maxSellerResults`, `maxSearchEngineResults`, or `maxDeliveryResults` (there is no single `maxResults`). For Fallback actors, use whatever the schema exposes (`maxResults`, `resultsLimit`, `maxItems`, `maxCrawledPages`, etc.). Default to the per-intent values above unless the user explicitly asks for more. Warn the user before running large scrapes (1000+ results) as they consume more Apify credits.

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
- `No results` → broaden the keyword, switch to the Fallback Actor, then use the **Escalation** discovery command (under Step 1) if both fail
- `proxy is required` → add `"proxy": {"useApifyProxy": true}` to the Actor input
- `Platform not detected` → default to `apify/e-commerce-scraping-tool` with `generic` intent

## Gotchas

- **`--input --json` is a trap.** It returns the full ~250 KB actor object, not the schema. Use `apify actors info ID --input` (no `--json`) for the clean schema; only dig into `.taggedBuilds.latest.build.inputSchema` if you specifically need it as JSON.
- **The Primary actor has no `maxResults` field.** Its caps are mode-specific (`maxProductResults`, `maxReviewResults`, `maxSellerResults`, `maxSearchEngineResults`, `maxDeliveryResults`). Setting `maxResults` does nothing and the run scrapes unbounded.
- **The Primary handles most intents via the right input mode** (URLs → `detailsUrls`/`listingUrls`; query → `keyword` or `searchEngineKeyword`), including competitor, search-intent, classifieds, automotive, real-estate, website-marketplace, and events. It genuinely **can't** do `tech-stack`, `seo-audit`, `store-enrichment`, `product-matching`, `ads-intelligence`, `content-discovery` (Pinterest), or `tiktok-shop` — route those straight to the Fallback.
- **`apify actors call -i` expects valid JSON on one line.** For inputs with URL arrays or quotes, write a file and pass `-i @input.json` instead of inlining — shell quoting silently corrupts complex inputs.
- **`datasets get-items` always streams over the network.** Save to a file once (`> file.json`), then run `jq` against the file — don't re-pipe the command into `jq` repeatedly or you re-download every time.
- **`apify actors search --sort-by popularity` ignores relevance.** It returns the biggest-name scrapers regardless of your query (an "etsy" search surfaces Instagram/Google Maps Actors). For escalation discovery keep the default relevance sort and filter on `stats.totalUsers`/`actorReviewRating` instead.
- **`marketplaces` values are full domain slugs**, e.g. `["www.amazon.com", "www.ebay.com"]` — not `"amazon"` or display names. Delivery mode is even narrower: `marketplacesDelivery` only accepts `["www.doordash.com", "www.instacart.com"]` (no UberEats — use the `e-commerce/ubereats-reviews-scraper` fallback for that). Always confirm accepted values from the `--input` schema's `enum` before guessing.
