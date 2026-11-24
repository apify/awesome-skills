---
name: apify-product-demand-check
description: >
  Decide whether a physical product is worth selling, with evidence. Use when the user asks
  "should I sell X", "is there demand for X", "is X a good product to sell on Amazon",
  "validate this product idea", "is the X market saturated", "is X seasonal, when should I
  launch", "what do customers hate about the X on Amazon", "product research for dropshipping",
  or wants a go / no-go brief before sourcing or launching a product. Combines Google Trends
  (5-year demand and seasonality), Amazon search and Best Sellers (proof of sales, price band,
  how open the top of the category is), critical Amazon reviews (what to fix) and TikTok
  trending hashtags (viral tailwind). Not for margin or fee calculations, unit sales
  estimates, or keyword volumes.
author: Data Xplorer
author_url: https://github.com/dataxplore19
license: MIT
metadata:
  version: "1.0"
  category: data-extraction
  keywords: "product research, product validation, amazon product research, demand check, market saturation, seasonality, dropshipping, amazon fba, best sellers, google trends, amazon reviews, tiktok trends, apify"
---

# Should I sell this product?

Turn a product idea into a go / no-go brief backed by live data: is demand growing, is it seasonal, does it already sell, can a newcomer still reach the top of its category, at what price, and what do buyers complain about. Each signal comes from a different Actor; the value of this skill is in chaining them on the same product, country and category, and in reading them with explicit thresholds instead of impressions.

Disclosure: three of the routed Actors (Google Trends, Amazon Best Sellers, TikTok Trends, all `data_xplorer/...`) are built and sold by the skill author (Data Xplorer). Store links use the author's Apify affiliate code. The other Actors are third-party.

## Example prompts

Prompts this skill handles:

- "Should I start selling posture correctors on Amazon US?"
- "Is there still room for a new brand of silicone baby bibs on Amazon.de, and when should I launch?"
- "What do customers hate about the best-selling electric milk frothers?"

Out of scope (the boundary):

- "What margin will I make after FBA fees?" This skill measures demand and competition, not costs. Use a fee calculator with your own sourcing price.
- "How many units does the #1 posture corrector sell per month?" Amazon only shows "bought in past month" badges, which the skill reports as they are; it never invents unit numbers.

## Actors

| Step | Actor ID | Tier | Signal |
|---|---|---|---|
| Demand trend and seasonality | [`data_xplorer/google-trends-fast-scraper`](https://apify.com/data_xplorer/google-trends-fast-scraper?fpr=6vi1cs) | community | 5 years of weekly search interest (0 to 100), interest by region |
| Products that sell for this query | `junglee/Amazon-crawler` | community | Price, rating, review count, "bought in past month", Best Sellers rank and category |
| Top of the category | [`data_xplorer/amazon-bestsellers`](https://apify.com/data_xplorer/amazon-bestsellers?fpr=6vi1cs) | community | Top 50 or 100 of the exact subcategory: rank, price, rating, review count |
| What buyers complain about | `junglee/amazon-reviews-scraper` | community | Critical (1 to 3 star) reviews of the leaders |
| Viral tailwind | [`data_xplorer/tiktok-trends`](https://apify.com/data_xplorer/tiktok-trends?fpr=6vi1cs) | community | Trending TikTok hashtags of a country and industry, with views and direction |
| Optional: discussions | `harshmaur/reddit-scraper` | community | Posts from a relevant subreddit |

## Prerequisites

- Apify CLI (`npm i -g apify-cli`), authenticated with `apify login` or `APIFY_TOKEN`
  ([token](https://console.apify.com/settings/integrations)). The Apify MCP server (<https://mcp.apify.com>) works with the same inputs.
- `jq` to read the results.

Every step uses the same two commands. Never drop the three flags:

```bash
apify actors call "ACTOR_ID" -i 'INPUT_JSON' --json --user-agent apify-awesome-skills/apify-product-demand-check 2>/dev/null > /tmp/run.json
apify datasets get-items "$(jq -r .defaultDatasetId /tmp/run.json)" --format json --user-agent apify-awesome-skills/apify-product-demand-check 2>/dev/null > /tmp/step.json
```

## Set the market once

Use the same country in every step. A product can boom in the US and be flat in Germany.

| Amazon store | Search URL | Trends `geo` | TikTok `countryCode` |
|---|---|---|---|
| amazon.com | `https://www.amazon.com/s?k=QUERY` | `US` | `US` |
| amazon.co.uk | `https://www.amazon.co.uk/s?k=QUERY` | `GB` | `GB` |
| amazon.de | `https://www.amazon.de/s?k=QUERY` | `DE` | `DE` |
| amazon.fr | `https://www.amazon.fr/s?k=QUERY` | `FR` | `FR` |
| amazon.it / .es | `https://www.amazon.it/s?k=QUERY` | `IT` / `ES` | `IT` / `ES` |
| amazon.ca / .com.mx / .com.br | same pattern | `CA` / `MX` / `BR` | `CA` / `MX` / `BR` |

Write the query the way a shopper types it, in the store's language (`posture corrector`, `Haltungskorrektur`, `correcteur de posture`), and reuse that exact term in Google Trends.

## Workflow

### 1. Demand: is it growing, and when does it peak? (about $0.03)

```bash
apify actors call "data_xplorer/google-trends-fast-scraper" -i '{"mode": "keyword", "keyword": "posture corrector", "geo": "US", "predefinedTimeframe": "today 5-y", "fetchRegionalData": true}' --json --user-agent apify-awesome-skills/apify-product-demand-check 2>/dev/null > /tmp/run.json
apify datasets get-items "$(jq -r .defaultDatasetId /tmp/run.json)" --format json --user-agent apify-awesome-skills/apify-product-demand-check 2>/dev/null > /tmp/trends.json
jq -r '.[0] | .timeline_data[.keyword] | [.[]] as $v | "first 12 months avg: \($v[0:52] | add / length | floor)  last 12 months avg: \($v[-52:] | add / length | floor)"' /tmp/trends.json
jq -r '.[0] | .timeline_data[.keyword] | to_entries | group_by(.key[5:7]) | map("\(.[0].key[5:7]): \(map(.value) | add / length | floor)") | join("  ")' /tmp/trends.json
```

- Use `today 5-y`, not the default `today 12-m`: one year cannot separate a trend from a season. `today 5-y` gives 262 weekly points.
- **Trend** = last-12-months average ÷ first-12-months average. Above 1.2: growing. 0.8 to 1.2: stable. Below 0.8: declining.
- **Seasonality** = highest month average ÷ lowest month average. At 1.5 or more the product is seasonal: plan stock and the launch about 8 weeks before the peak month, so the listing has reviews when demand arrives.
- If the item has an `error` field ("Not enough search volume..."), the product is too niche for Google Trends in that country. That is a signal in itself: rely on the Amazon steps, and try a broader term.
- `region_data` shows where interest concentrates. A small-population region at 100 (Wyoming, for posture corrector in the US) usually means a small sample, not a target market.

### 2. Proof of sales on Amazon (10 results, about $0.05)

```bash
apify actors call "junglee/Amazon-crawler" -i '{"categoryOrProductUrls": [{"url": "https://www.amazon.com/s?k=posture+corrector"}], "maxItemsPerStartUrl": 10}' --json --user-agent apify-awesome-skills/apify-product-demand-check 2>/dev/null > /tmp/run.json
apify datasets get-items "$(jq -r .defaultDatasetId /tmp/run.json)" --format json --user-agent apify-awesome-skills/apify-product-demand-check 2>/dev/null > /tmp/search.json
jq -r '.[] | "\(.price.value // "?") \(.price.currency // "") | \(.stars // "?")★ \(.reviewsCount // 0) reviews | \(.monthlyPurchaseVolume // "n/a") | #\(.bestsellerRanks[-1].rank // "?") in \(.bestsellerRanks[-1].category // "?") | \(.title[0:60])"' /tmp/search.json
jq -r '[.[] | .bestsellerRanks[-1] | select(.url != null) | "\(.category)\t\(.url | sub("/ref=.*"; ""))"] | group_by(.) | map("\(length)x \(.[0])") | .[]' /tmp/search.json
```

- Always set `maxItemsPerStartUrl`: the search goes through many pages otherwise, each result billed.
- `monthlyPurchaseVolume` ("20K+ bought in past month") is Amazon's own badge and the best public proof that a product sells. Several results at "1K+" or more mean real, current demand.
- The last entry of `bestsellerRanks` is the product's **subcategory** and its Best Sellers URL. The second command counts which subcategory the results share: that URL is the input of step 3. Do not use the department (the first entry, here "Health & Household"): its top 100 mixes thousands of unrelated products.

### 3. How open is the top of the category? (top 50, about $0.08)

```bash
apify actors call "data_xplorer/amazon-bestsellers" -i '{"mode": "urls", "startUrls": [{"url": "https://www.amazon.com/gp/bestsellers/hpc/5006367011"}], "maxItemsPerCategory": 50}' --json --user-agent apify-awesome-skills/apify-product-demand-check 2>/dev/null > /tmp/run.json
apify datasets get-items "$(jq -r .defaultDatasetId /tmp/run.json)" --format json --user-agent apify-awesome-skills/apify-product-demand-check 2>/dev/null > /tmp/top.json
jq -r '.[] | select(.title | test("posture"; "i")) | "#\(.rank) $\(.price) \(.rating)★ \(.reviewsCount) | \(.title[0:55])"' /tmp/top.json
jq -r '[.[] | select(.title | test("posture"; "i"))] | "matching listings in top 50: \(length), under 500 reviews: \(map(select(.reviewsCount < 500)) | length), median price: \(map(.price) | sort | .[length/2|floor])"' /tmp/top.json
```

- A subcategory is often wider than the product ("Back Braces" also holds lower-back belts). Filter titles on the product's key word before counting, as above.
- **Openness** = share of matching listings in the top 50 with fewer than 500 reviews. 30 % or more: newcomers reach the top, the market is open. Under 10 %: the top is held by brands with thousands of reviews, entry needs a clear difference or a large launch budget.
- The median price of the matching listings is the price band to fit, or to beat with a reason.
- The same Actor also takes `"listTypes": ["new-releases", "movers-and-shakers"]` with `"mode": "categories"`: Movers & Shakers shows what is accelerating right now in that category.

### 4. What buyers complain about (2 leaders × 15 reviews, about $0.18)

```bash
apify actors call "junglee/amazon-reviews-scraper" -i '{"productUrls": [{"url": "https://www.amazon.com/dp/B07ZQPKTVV"}, {"url": "https://www.amazon.com/dp/B07VST9VYH"}], "filterByRatings": ["critical"], "sort": "recent", "maxReviews": 15}' --json --user-agent apify-awesome-skills/apify-product-demand-check 2>/dev/null > /tmp/run.json
apify datasets get-items "$(jq -r .defaultDatasetId /tmp/run.json)" --format json --user-agent apify-awesome-skills/apify-product-demand-check 2>/dev/null > /tmp/reviews.json
jq -r '.[] | "\(.ratingScore)★ \(.reviewTitle) | \(.reviewDescription[0:160] | gsub("\n"; " "))"' /tmp/reviews.json
```

- Pick the 2 or 3 leaders by review count from step 3 (`asin` gives the URL `https://www.amazon.com/dp/ASIN`).
- `filterByRatings: ["critical"]` and `sort: "recent"`: the defaults (all stars, most helpful) surface old praise, not current problems.
- `maxReviews` applies per product, and each review is billed.
- Report a complaint only when it repeats (3 or more of the reviews read). Those repeated complaints are the product brief: in the example, out of 30 critical reviews, 10 mention discomfort at the neck or armpits, 6 sizing, 5 that it is hard to put on alone.

### 5. Viral tailwind on TikTok (top 50 hashtags, about $0.10)

```bash
apify actors call "data_xplorer/tiktok-trends" -i '{"trendType": "hashtags", "countryCode": "US", "hashtagPeriod": "30", "industryId": "29000000000", "maxItems": 50}' --json --user-agent apify-awesome-skills/apify-product-demand-check 2>/dev/null > /tmp/run.json
apify datasets get-items "$(jq -r .defaultDatasetId /tmp/run.json)" --format json --user-agent apify-awesome-skills/apify-product-demand-check 2>/dev/null > /tmp/tiktok.json
jq -r '.[] | "\(.Rank). \(.Hashtag) | \(."Video Views") views | \(."Trend Direction")"' /tmp/tiktok.json
```

- **Set `countryCode` and `industryId`.** The defaults are France and all industries, which says nothing about a US health product.
- Industries: `14000000000` Beauty & Personal Care, `29000000000` Health, `15000000000` Tech & Electronics, `18000000000` Household Products, `12000000000` Baby, Kids & Maternity, `19000000000` Pets, `22000000000` Apparel & Accessories, `27000000000` Food & Beverage, `28000000000` Sports & Outdoor, `21000000000` Home Improvement.
- Output keys have spaces and capitals (`."Video Views"`, `."Trend Direction"`): quote them in `jq`.
- A related hashtag in the top 50 with direction `up` is a tailwind worth a launch on TikTok. None (the usual case) is not a negative: it means growth has to come from search, which step 1 measures.

### 6. Optional: what people say on Reddit (20 posts, about $0.06)

Only when the user wants qualitative context. Search inside one relevant subreddit (`withinCommunity`, for example `Posture`) and set `postedAfter`: a site-wide search for a product name returns mostly unrelated posts (in testing, `posture corrector` across Reddit returned posts from r/babywearing and r/dropshipping among 20 results).

```bash
apify actors call "harshmaur/reddit-scraper" -i '{"searchTerms": ["posture corrector"], "withinCommunity": "Posture", "postedAfter": "2026-05-01", "maxPostsCount": 20}' --json --user-agent apify-awesome-skills/apify-product-demand-check 2>/dev/null > /tmp/run.json
```

## Verdict

Write a short brief with one line per signal, then the decision:

| Signal | Source | Example (posture corrector, US, 2026-11-18) |
|---|---|---|
| Trend | Step 1 | 19 → 33 over 5 years (×1.7): growing |
| Seasonality | Step 1 | April 30 vs October 18 (×1.7): seasonal, launch in February |
| Proof of sales | Step 2 | 7 of 10 results at "1K+ bought in past month" or more, the #1 at "20K+" |
| Openness | Step 3 | 21 of 35 matching listings in the Back Braces top 50 have under 500 reviews: open |
| Price band | Step 3 | Median $24.69 |
| What to fix | Step 4 | Neck and armpit discomfort (10 of 30), sizing (6), hard to put on alone (5) |
| TikTok | Step 5 | No related hashtag in the US Health top 50: no viral tailwind |

Then one of:

- **Go**: growing or stable demand, proof of sales, an open top.
- **Go with conditions**: say which (launch window, price, the complaint to fix, a budget for reviews).
- **No-go**: declining demand, no "bought in past month" badges, or a closed top with no complaint to exploit.

State what the data cannot tell (margins, unit sales, ad costs) instead of guessing.

## Cost

Prices for the free Apify plan (paid plans pay less). Check each Actor's Store page before a large run.

| Step | Price | Typical |
|---|---|---|
| 1. Google Trends | $0.025 per run + $0.002 per result | $0.03 |
| 2. Amazon search | $0.005 per product | $0.05 for 10 |
| 3. Amazon Best Sellers | $0.0015 per product | $0.08 for 50 |
| 4. Amazon reviews | $0.006 per review | $0.18 for 2 × 15 |
| 5. TikTok Trends | $0.025 per run + $0.0015 per hashtag | $0.10 for 50 |
| 6. Reddit (optional) | $0.02 per run + $0.002 per post | $0.06 for 20 |
| Full check | | about $0.45 |

Guardrails: always set `maxItemsPerStartUrl`, `maxItemsPerCategory` and `maxReviews`; read reviews for 2 or 3 leaders, not the whole top 50; ask before going above $2 (for example comparing many products at once).

## Troubleshooting

- **Google Trends returns an `error` field**: too little search volume for that term and country. Try the broader term (`back brace` instead of a brand-like phrase) or rely on steps 2 and 3.
- **Amazon search returns products from other niches**: the query is too generic. Add the product type (`posture corrector brace`) and check that the subcategory count in step 2 points to one subcategory.
- **`bestsellerRanks` is empty**: some listings have no rank (new or restricted products). Use the ranks of the other results.
- **Best Sellers run returns 0 products**: use the subcategory URL without the `/ref=...` suffix, as the `sub()` in step 2 does, and check the store matches (`amazon.de` URL for a German check).
- **TikTok Trends fails or returns nothing**: skip step 5 and say so. It is a tailwind signal, not the core of the verdict.
- **Reviews from other countries**: `reviewedIn` says where each review was written ("Reviewed in the United States on ..."). Keep those from the target store when counting complaints.
