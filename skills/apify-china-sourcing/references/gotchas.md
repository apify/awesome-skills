# Cost guardrails and gotchas

## What a run costs (pay per result, approximate list prices)

| Actor | Search row | Product page |
|-------|-----------|--------------|
| `blueskyscraper/1688-products-scraper` | about $0.0009 | about $0.0081 (only with `includeDetails`) |
| `blueskyscraper/1688-product-details-scraper` | — | about $0.0081 |
| `blueskyscraper/alibaba-products-scraper` | about $0.0008 | about $0.0036 (only with `includeDetails`) |

- A 30-row 1688 search costs about 3 cents; the same 30 rows with product pages cost about 25 cents. Ask before opening more than 20 product pages.
- `maxResultsPerInput` is per keyword, not per run. Three keywords × 60 = 180 billed rows. Set `maxItems` as a hard ceiling for the whole run.
- Error and notice rows are free.

## Things that surprise people

- 1688 prices are in CNY for buyers inside China. `priceUsd` is a conversion, not a quote; shipping, agent fees and export paperwork are not included.
- 1688 search shows a single price per product. Quantity tiers and MOQ exist only on the product page (`priceTiers`, `minOrder`).
- On Alibaba, `priceMin`–`priceMax` is the range across tiers; the real price for the user's quantity is in `priceTiers`.
- `provinces` on 1688 must be written in Chinese (`浙江`, `广东`, `义乌`).
- A run of 20–30 search rows usually finishes in under half a minute; product pages take a few seconds each.
