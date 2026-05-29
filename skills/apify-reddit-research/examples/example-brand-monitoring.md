# Example: Brand Monitoring on Reddit

## Goal
The user wants to understand recent sentiment around "Claude AI" on Reddit, including what articles people are linking to.

## Step 1 — Reddit Discovery

```bash
apify actors call trudax/reddit-scraper-lite \
  -i '{
    "searches": ["Claude AI OR Anthropic"],
    "searchPosts": true,
    "searchComments": true,
    "sort": "relevance",
    "time": "week",
    "maxItems": 100
  }' \
  --user-agent apify-awesome-skills/apify-reddit-research \
  --json 2>/dev/null
```

**Typical output highlights (from real runs):**
- Posts and comments mentioning the brand (note: broad keywords can sometimes surface older/irrelevant threads)
- Upvote counts and engagement
- Links to articles, reviews, or comparisons being shared

**Tip from testing:** Using more specific subreddits or tighter queries often yields cleaner, more relevant results.

## Step 2 — (Optional) Enrich Key Links

From the Reddit results, pick the most relevant URLs (e.g. a detailed review or announcement) and crawl them:

```bash
apify actors call apify/website-content-crawler \
  -i '{
    "startUrls": [{"url": "https://www.anthropic.com/news/claude-3-5-sonnet"}],
    "maxCrawlPages": 2
  }' \
  --user-agent apify-awesome-skills/apify-reddit-research \
  --json 2>/dev/null
```

## Final Deliverable
The agent can now provide:
- Summary of recent sentiment on Reddit
- Key themes from discussions
- Context from the actual articles people are sharing
- Links + engagement data for the most important threads

This two-step approach gives much richer output than Reddit data alone.
