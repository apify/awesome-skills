---
name: apify-reddit-research
description: Research discussions, sentiment, opinions, and trends on Reddit. Use when the user asks what Reddit thinks about a topic/brand/product/company, wants subreddit analysis, needs to find real conversations, monitor brand mentions, analyze customer sentiment, research trends, or gather Reddit data for competitive intelligence and market research. Supports keyword search, specific subreddits, user profiles, and post URLs.
author: Jose Gabriel Rivera
author_url: https://github.com/grivera82
---

# Reddit Research

This skill helps agents research discussions, sentiment, and trends on Reddit. It chains two Actors:

- `trudax/reddit-scraper-lite` — Finds conversations, posts, comments, and links across Reddit.
- `apify/website-content-crawler` (optional) — Crawls the most relevant pages linked in those discussions for deeper context.

It is particularly strong for brand monitoring, competitor analysis, customer sentiment research, and market intelligence.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## When to use this skill

Use this skill when the user says things like:
- "What does Reddit think about [topic/product/brand]?"
- "Find discussions about [X] on Reddit"
- "Reddit sentiment on [company]"
- "Research r/[subreddit]"
- "Scrape Reddit for [keyword]"
- "What are people saying about [new feature/launch]?"
- "Find complaints/praise about [product] on Reddit"
- "Market research on Reddit for [category]"

## Actor routing

| Step | Actor ID | Purpose | When to use |
|------|----------|---------|-------------|
| 1 | `trudax/reddit-scraper-lite` | Discover Reddit discussions, sentiment, and links | Always (core of the skill) |
| 2 (optional) | `apify/website-content-crawler` | Enrich the best linked articles/pages found in Reddit threads | When you need deeper context beyond comments |

### Why this skill chains two Actors

- **Step 1** (`trudax/reddit-scraper-lite`): Discover real conversations, sentiment, and links people are sharing on Reddit.
- **Step 2** (optional but powerful): `apify/website-content-crawler` crawls the most relevant linked pages to get full article/review content.

This combination delivers significantly more value than scraping Reddit alone, especially for brand monitoring and competitive intelligence.

## Prerequisites & CLI Rules

**Every `apify` CLI command in this skill must use these three flags** (CI will reject the PR otherwise):

```bash
apify actors call trudax/reddit-scraper-lite \
  -i 'JSON_HERE' \
  --user-agent apify-awesome-skills/apify-reddit-research \
  --json 2>/dev/null
```

- `--user-agent` → required for telemetry / bounty attribution
- `--json` → machine-readable output
- `2>/dev/null` → hides progress spinners that break JSON parsing

## Workflow (Two-Actor Chain)

1. Clarify the goal (brand monitoring, competitor research, sentiment, etc.).
2. Run `trudax/reddit-scraper-lite` to discover relevant Reddit discussions, sentiment, and links.
3. Review the results and pull out the most useful URLs mentioned in posts and comments.
4. (Optional but recommended) Chain to `apify/website-content-crawler` to crawl the best linked pages for full content.
5. Synthesize the findings: Reddit sentiment + source material.
6. Deliver a clear summary and offer the raw datasets.

## Main Actor Usage

This skill primarily uses two Actors in sequence:

1. `trudax/reddit-scraper-lite` — Discover relevant Reddit discussions and extract URLs.
2. `apify/website-content-crawler` — Enrich the most promising linked articles found in those discussions.

### Recommended input patterns for the Reddit discovery Actor (Step 1)

**Tip for brand monitoring:** Broad keywords (e.g. "Claude AI") frequently return noisy/old/irrelevant results (game characters, people named Claude in old politics threads, etc.). Recent live tests showed this clearly. Always prefer:
- Specific subreddits via `startUrls`
- Tighter phrases + negative/positive keywords
- Time filters (`time: "week"` or `time: "month"`)

**1. Keyword search across Reddit (most common starting point)**
```json
{
  "searches": ["Claude AI OR Anthropic"],
  "searchPosts": true,
  "searchComments": true,
  "sort": "relevance",
  "time": "week",
  "maxItems": 100,
  "includeNSFW": false
}
```

**2. Targeted subreddit monitoring (usually cleaner results)**
```json
{
  "startUrls": [{ "url": "https://www.reddit.com/r/singularity/" }],
  "maxPostCount": 30,
  "maxItems": 80
}
```

**3. Negative sentiment / complaints about a brand**
```json
{
  "searches": ["Claude AI (bad OR sucks OR disappointed OR scam OR worse)"],
  "searchPosts": true,
  "searchComments": true,
  "sort": "relevance",
  "time": "month",
  "maxItems": 50
}
```

**4. Specific post + full comment thread**
```json
{
  "startUrls": [{ "url": "https://www.reddit.com/r/..." }],
  "maxComments": 200
}
```

### Chaining the Second Actor (Website Content Enrichment)

After running the Reddit discovery Actor, you will often find high-value URLs in the posts and comments (articles, reviews, company pages, etc.). You can optionally chain to the second Actor to crawl those pages for deeper context.

**Concrete example:**

```bash
# Step 2: Enrich a linked article found in Reddit results
apify actors call apify/website-content-crawler \
  -i '{
    "startUrls": [{"url": "https://www.anthropic.com/news/claude-3-5-sonnet"}],
    "maxCrawlPages": 2
  }' \
  --user-agent apify-awesome-skills/apify-reddit-research \
  --json 2>/dev/null
```

**Why this two-Actor chain is valuable:**
- The Reddit Actor captures community sentiment and surfaces the links people are actually sharing.
- The Website Crawler pulls the real source content behind those links.
- Combined, the agent gets both the social discussion and the underlying material — much stronger than Reddit data alone for brand monitoring and competitive research.

### Option B & C (MCP)

Both Actors work via the [Apify MCP connector](https://mcp.apify.com) or `mcpc`.

## Cost & Limits

- The Reddit Actor is pay-per-result (~$3.40 per 1,000 items stored).
- The Website Crawler adds extra cost only when you choose to use it.
- Always set sensible limits (`maxItems`, `maxPostCount`, `maxComments`).
- Warn the user before large or deep comment-heavy runs.
- Residential proxies are enabled by default.

## Common Pitfalls & Gotchas

- **The scraper is often flaky.** In live testing, multiple runs returned "0 succeeded" even with small limits. This is common with Reddit actors. Always inspect the run after it finishes.
- You can be charged ~$0.04 (actor start fee) **even when you get zero results**.
- `status: "SUCCEEDED"` does **not** guarantee good data. Check `statusMessage` and the number of successful vs failed requests.
- Reddit is aggressive with rate limiting. Large or very fast scrapes can still fail even with residential proxies.
- NSFW content is included by default. Always set `"includeNSFW": false` for professional/brand work unless the user specifically wants it.
- Comments can explode in size. Use `maxComments` and `skipComments: true` when you only need the posts.
- `maxItems` is the global limit. `maxPostCount` and `maxComments` control per-page depth.
- Very new or niche topics often return few results — try broader keywords or different time filters.
- Deleted/removed posts and comments are common on Reddit.

See [references/gotchas.md](references/gotchas.md) for detailed error handling and retry strategies.

## Output Guidance

The Actor returns rich structured data (posts, comments, scores, authors, dates, URLs, etc.).

**Never** just dump hundreds of raw items to the user. Instead:
- Summarize the main themes and sentiment
- Show top posts with scores and links
- Offer to export the full dataset as CSV or JSON when they need the raw data
- Include the Apify dataset URL for transparency

**When the run returns little or no data** (very common):
- Always show the user the exact `statusMessage` (e.g. "Finished! Total 12 requests: 1 succeeded, 11 failed.").
- Explain that Reddit scrapers are frequently flaky and that getting 0 results or mostly failed requests does **not** mean the brand has no discussion.
- Offer 2-3 concrete retry options:
  - Use a more specific subreddit (e.g. r/singularity instead of broad search)
  - Tighten or broaden the keyword
  - Switch to `startUrls` for a specific subreddit or post
  - Remove the `time` filter
- Share the `consoleUrl` so they can inspect it themselves.
- Be transparent: "This Actor often has bad runs. This is normal behavior on Reddit scrapers."
