# Gotchas — `apify-1688-profit-scout`

Cost guardrails, input formatting rules, and common pitfalls when auditing 1688 sourcing and cross-border unit economics.

## Cost guardrails

Check current Actor pricing metadata before large runs:

```bash
apify actors info "aitruelabs/truemargin-1688-profit-scout" \
  --json \
  --user-agent apify-awesome-skills/apify-1688-profit-scout \
  2>/dev/null
```

- `aitruelabs/truemargin-1688-profit-scout` is free on Apify Store and executes deterministic industrial-lexicon + margin calculations in seconds with minimal compute units (~$0.001 platform compute per batch).
- If chaining `apify/e-commerce-scraping-tool` first to scrape live Amazon/Walmart/Shopify category pages, keep `maxProductResults` ≤ 25 unless the user explicitly asks for a larger catalog audit. Confirm with the user before any scrape estimated above **$5**.

## Input formatting tips (`items` array)

Each string in `items` supports up to four pipe-delimited segments:

`Product Title | TargetRetailUSD | WeightGrams | OptionalKnownFactoryCNY`

Examples:
- `"Magnetic POV Neck Phone Holder | 27.99 | 260g"` — uses industrial-cluster benchmark RMB cost.
- `"Silicone Ice Face Roller | 16.99 | 190g | 6.5"` — overrides factory unit cost to `¥6.50 RMB`.
- `"https://example-shop.com/products/led-mask"` — attempts lightweight title/price extraction from the URL; if a storefront blocks bots with anti-bot challenges, pass `"Title | RetailUSD | WeightGrams"` text directly instead.

## Common errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `netProfitPerOrderUsd` is negative despite 4x–5x RMB-to-USD markup | Single-piece `direct_packet_3pl` air shipping + `BATTERY_MAGNETIC` surcharge + 15% creator affiliate + 14% refund RTO bleed | Test `shippingMode: "sea_ddp_bulk"`, bundle 2-packs to raise AOV above $28, or kill the SKU |
| URL item falls back to generic title | Target storefront requires JS rendering or blocks plain HTTP fetches | Scrape title/price first via `apify/e-commerce-scraping-tool` and pass `"Title \| RetailUSD \| WeightGrams"` |
| Empty dataset output | `items` array omitted or contained empty strings | Pass at least one non-empty string in `items` |
