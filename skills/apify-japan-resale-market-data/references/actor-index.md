# Actor index — Japan resale & hobby market data

Full routing table for this skill. All Actors are public on the Apify Store and authored by
Apify user `fruitful_quintessence` (the author of this skill).

| # | Actor ID | Marketplace | Input fields (verified) | Key output fields |
|---|----------|-------------|-------------------------|-------------------|
| 1 | `fruitful_quintessence/mandarake-auction-scraper` | Mandarake auction | `mode` (`category`/`keyword`), `category`, `keyword`, `maxPages`, `maxResults`, `language` | `item_no`, `name`, `current_price_jpy`, `start_price_jpy`, `bid_count`, `watch_count`, `shop_name`, `item_url` |
| 2 | `fruitful_quintessence/surugaya-japan-hobby-prices` | Suruga-ya | `searchKeyword`, `maxPages`, `inStockOnly`, `maxResults` | listing rows with a JPY price field |
| 3 | `fruitful_quintessence/japan-anime-figure-price-data` | Multi-shop aggregate | keyword-driven (see Store input tab) | normalized anime-figure price rows |
| 4 | `fruitful_quintessence/kitamura-japan-used-camera-scraper` | Kitamura | `keyword`, `sort`, `maxItems` | `productId`, `title`, `price`, `maker`, `janCode`, `salesStatus`, `productUrl` |
| 5 | `fruitful_quintessence/jackroad-used-watch-scraper` | Jackroad | `keyword`, `classification`, `maxItems` | pre-owned watch listing rows with JPY price |
| 6 | `fruitful_quintessence/komehyo-japan-brand-scraper` | Komehyo | `keyword`, `maxItems` | `brand`, `price`, `referencePrice`, `rank`, `size`, `material`, `store`, `productUrl` |

## Choosing between the two hobby Actors

- Need **auction dynamics** (bids, watch counts, current vs start price) → Actor 1.
- Need **buy-now retail stock** for used hobby goods → Actor 2.
- Need **already-normalized cross-shop figure prices** → Actor 3.

## Choosing between the three luxury/resale Actors

- Cameras → Actor 4. Watches → Actor 5. Handbags/apparel/other brands → Actor 6.

## Search fallback

If a needed marketplace is missing here, search the Store before writing any HTML scraper:

```bash
apify actors search "japan used" --json --limit 10 \
  --user-agent apify-awesome-skills/apify-japan-resale-market-data 2>/dev/null
```
