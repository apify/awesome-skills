# Social listening workflow

Use when the user asks to monitor brand mentions, social chatter, Reddit discussions, X/Twitter posts or trends, Threads posts, Trustpilot reviews, complaints, sentiment, or reputation signals.

## Trigger phrases

- "monitor mentions of..."
- "find Reddit discussions about..."
- "track X/Twitter posts or trends for..."
- "scrape Threads posts for..."
- "collect Trustpilot reviews and summarize sentiment"
- "brand reputation, complaints, social listening, VOC"

## Actor routing

| Need | Actor ID |
|---|---|
| Reddit communities, posts, comments | `automation-lab/reddit-scraper` |
| X/Twitter search, account posts, conversations | `automation-lab/twitter-scraper` |
| X/Twitter trending topics | `automation-lab/twitter-trends-scraper` |
| Threads posts/profiles | `automation-lab/threads-scraper` |
| Trustpilot review text and ratings | `automation-lab/trustpilot` |
| Trustpilot company/profile metadata | `automation-lab/trustpilot-scraper` |

## Input schema hints

Fetch the live schema first. Common fields are usually one or more of:

- `query`, `searchQuery`, `keyword`, `keywords`
- `startUrls` / `urls` for known profile, thread, or company URLs
- `maxItems`, `maxResults`, `limit`
- `sort`, `timeRange`, `dateFrom`, `dateTo` when supported

Ask for clarification if the user did not provide a brand/topic or desired result count.

## Example payloads

```bash
apify actors info "automation-lab/reddit-scraper" --user-agent automation-lab-agent-skill --input --json 2>/dev/null
apify actors call "automation-lab/reddit-scraper" -i '{"query":"Acme AI pricing complaints","maxItems":100}' --user-agent automation-lab-agent-skill --json 2>/dev/null
```

```bash
apify actors call "automation-lab/twitter-scraper" -i '{"query":"\"Acme AI\" OR acme.ai","maxItems":100}' --user-agent automation-lab-agent-skill --json 2>/dev/null
```

```bash
apify actors call "automation-lab/trustpilot" -i '{"startUrls":[{"url":"https://www.trustpilot.com/review/example.com"}],"maxItems":200}' --user-agent automation-lab-agent-skill --json 2>/dev/null
```

## Output normalization

Create one normalized row per post/review:

- `sourcePlatform`: `reddit`, `x`, `threads`, or `trustpilot`
- `sourceActor`
- `url`
- `author` / `handle`
- `publishedAt`
- `text`
- `rating` for reviews
- `engagementCount` from available likes/comments/upvotes/replies
- `sentiment` only if the agent performs downstream analysis

For social listening summaries, group by complaint/praise theme and include representative URLs.
