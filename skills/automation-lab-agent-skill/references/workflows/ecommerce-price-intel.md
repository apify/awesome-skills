# Ecommerce price intelligence workflow

Use when the user asks for product pricing, seller monitoring, marketplace research, MAP checks, arbitrage, current vs sold prices, review quality, or product assortment across Amazon, eBay, Etsy, or Google Shopping.

## Trigger phrases

- "compare prices across Amazon/eBay/Etsy/Google Shopping"
- "find eBay sold listings"
- "monitor competitor prices"
- "scrape Amazon reviews/bestsellers/sellers"
- "marketplace product research"

## Actor routing

| Need | Actor ID |
|---|---|
| Amazon product search/details | `automation-lab/amazon-scraper` |
| Amazon review text and ratings | `automation-lab/amazon-reviews-scraper` |
| Amazon bestseller rankings | `automation-lab/amazon-bestsellers-scraper` |
| Amazon seller intelligence | `automation-lab/amazon-sellers-scraper` |
| eBay active listings | `automation-lab/ebay-scraper` |
| eBay realized/sold prices | `automation-lab/ebay-sold-scraper` |
| Etsy listings/shops | `automation-lab/etsy-scraper` |
| Google Shopping offers | `automation-lab/google-shopping-scraper` |

## Input schema hints

Fetch the current schema. Common input shapes are:

- search query fields: `query`, `search`, `keyword`, `keywords`
- URL lists: `startUrls`, `urls`, product URLs, shop URLs
- bounds: `maxItems`, `maxResults`, `pages`
- marketplace filters: country, locale, condition, sort, min/max price when supported

## Example payloads

```bash
apify actors call "automation-lab/ebay-sold-scraper" -i '{"query":"Sony WH-1000XM5","maxItems":100}' --user-agent automation-lab-agent-skill --json 2>/dev/null
```

```bash
apify actors call "automation-lab/amazon-scraper" -i '{"query":"Sony WH-1000XM5","maxItems":50}' --user-agent automation-lab-agent-skill --json 2>/dev/null
```

```bash
apify actors call "automation-lab/google-shopping-scraper" -i '{"query":"wireless earbuds noise cancelling","maxItems":100}' --user-agent automation-lab-agent-skill --json 2>/dev/null
```

## Output normalization

Normalize to:

- `sourcePlatform`
- `sourceActor`
- `productTitle`
- `brand` if available
- `sellerName`
- `price`
- `currency`
- `condition`
- `availability`
- `rating`
- `reviewCount`
- `soldAt` for sold listings
- `productUrl`

For price intelligence, compute median/min/max price by platform and flag outliers. For sold listings, distinguish asking prices from realized prices.
