---
name: apify-ecommerce
description: Scrape e-commerce data for pricing, reviews, bestsellers, and seller discovery across 30+ platforms including Amazon, Walmart, eBay, Shopify, WooCommerce, and more. Use when user asks about product prices, competitor analysis, store scraping, tech stack detection, food delivery, real estate, or marketplace intelligence.
---

# E-Commerce Cluster

Answer natural language e-commerce questions by routing to the right Apify Actor and delivering a synthesized answer.

## Prerequisites
(No need to check it upfront)

- `.env` file with `APIFY_TOKEN`
- Node.js 20.6+ (for native `--env-file` support)
- `mcpc` CLI tool: `npm install -g @apify/mcpc`

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Step 1: Detect intent and select Actor
- [ ] Step 2: Fetch Actor schema via mcpc
- [ ] Step 3: Ask user preferences (format, result count)
- [ ] Step 4: Run the Actor
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

Fetch the Actor's input schema dynamically using mcpc:

```bash
export $(grep APIFY_TOKEN .env | xargs) && mcpc --json mcp.apify.com --header "Authorization: Bearer $APIFY_TOKEN" tools-call fetch-actor-details actor:="ACTOR_ID" | jq -r ".content"
```

Replace `ACTOR_ID` with the selected Actor (e.g., `apify/e-commerce-scraping-tool`).

This returns:
- Actor description and README
- Required and optional input parameters
- Output fields (if available)

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

### Step 4: Run the Actor

**Quick answer (display in chat, no file):**
```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "ACTOR_ID" \
  --input 'JSON_INPUT'
```

**CSV:**
```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "ACTOR_ID" \
  --input 'JSON_INPUT' \
  --output YYYY-MM-DD_filename.csv \
  --format csv
```

**JSON:**
```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "ACTOR_ID" \
  --input 'JSON_INPUT' \
  --output YYYY-MM-DD_filename.json \
  --format json
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

`APIFY_TOKEN not found` — Ask user to create `.env` with `APIFY_TOKEN=your_token`
`mcpc not found` — Ask user to install: `npm install -g @apify/mcpc`
`Actor not found` — Check Actor ID spelling in routing table
`Run FAILED` — Ask user to check the Apify console link in error output
`Timeout` — Reduce result count or increase `--timeout`
`No results` — Broaden keyword or switch to Fallback Actor from routing table
`proxy is required` — Add `"proxy": {"useApifyProxy": true}` to input
`Platform not detected` — Default to `apify/e-commerce-scraping-tool` with `generic` intent
