# Actor index — apify-reddit-research

This skill uses a two-Actor chain optimized for brand and topic monitoring on Reddit:

| Step | Actor ID | Purpose | Recommended for |
|------|----------|---------|-----------------|
| 1 | `trudax/reddit-scraper-lite` | Discover posts, comments, sentiment, and links from Reddit | Primary step for almost all use cases |
| 2 (optional) | `apify/website-content-crawler` | Crawl and extract content from the most relevant URLs found in Reddit threads | Deeper research when you need the actual articles/reviews being discussed |

## Common patterns

- Brand monitoring → Reddit discovery + selective page crawling
- Competitor analysis → Focus on specific subreddits + enrichment of key links
- Trend research → Broad searches + follow high-engagement links

## How to extend

1. Search for candidates: `apify actors search "reddit" --json --limit 10 2>/dev/null`
2. Fetch input schema: `apify actors info "trudax/reddit-scraper-lite" --input --json 2>/dev/null`
3. Test small runs before adding new routing.

Primary documentation:
- https://apify.com/trudax/reddit-scraper-lite
- https://apify.com/apify/website-content-crawler

For a more advanced reference, see the official Apify agent-skills ultimate-scraper.
