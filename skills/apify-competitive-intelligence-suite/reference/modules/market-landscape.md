# Market Landscape Map

**When to use**: Understand all players, find white space, or map the competitive landscape.

## Data Gathering

```
# 1: Discover players (parallel)
call-actor: apify/google-search-scraper
  input: { "queries": "[industry] companies\nbest [category] tools\n[category] alternatives" }

# 2: Category/comparison pages
call-actor: apify/rag-web-browser
  input: { "query": "best [category] comparison" }

# 3: Quick snapshot of each discovered competitor
call-actor: apify/website-content-crawler
  input: { "startUrls": ["[url-1]", "[url-2]", ...], "maxCrawlPages": 1, "proxyConfiguration": {"useApifyProxy": true} }

# 4: Funding/size enrichment
call-actor: pratikdani/crunchbase-companies-scraper

# 5: Traffic comparison
call-actor: pro100chok/similarweb-scraper
  input: { "searchType": "similarweb", "domains": ["domain-1.com", "domain-2.com"] }
```

## Analysis

Categorize by tier (enterprise, mid-market, SMB, open-source). Build positioning map (e.g., price vs. feature breadth). Identify white space — underserved segments or unowned positioning. Note trends, recent entrants, consolidation signals.
