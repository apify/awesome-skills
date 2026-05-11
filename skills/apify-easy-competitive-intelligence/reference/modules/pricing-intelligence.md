# Pricing Intelligence

**When to use**: Compare pricing, understand pricing models, or find positioning opportunities.

## Data Gathering

```
# Scrape pricing pages (parallel)
call-actor: apify/website-content-crawler  # [competitor]/pricing for each vendor

# E-commerce products (if applicable)
call-actor: junglee/Amazon-crawler
call-actor: e-commerce/walmart-product-detail-scraper

# Third-party pricing breakdowns
call-actor: apify/google-search-scraper
  input: { "queries": "[competitor] pricing review" }
```

## Analysis

Extract plan names, prices, feature lists, limits. Normalize into comparison matrix. Identify pricing model types (per-seat, usage-based, freemium, enterprise-only). Flag positioning signals — gaps, undercut potential, differentiation opportunities.
