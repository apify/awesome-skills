---
name: apify-youtube-creator-research
description: Research YouTube channels, videos, Shorts, playlists, search results, comments, and creator positioning using Apify Actors. Use when the user asks for YouTube competitor analysis, creator research, content strategy, keyword/video discovery, audience comment mining, Shorts analysis, sponsor/brand mention discovery, or channel performance benchmarking.
---

# YouTube Creator Research

Plan and run YouTube research workflows with Apify Actors, then turn raw channel/video/comment data into a compact research deliverable. Use this skill when a user asks to analyze creators, compare channels, find video opportunities, inspect comments, monitor brand mentions, research Shorts, or build a YouTube content strategy.

## Prerequisites

- Apify account and authentication through an available Apify MCP connector, Apify CLI session, or `APIFY_TOKEN` environment variable.
- Before running any Actor, check the current Actor input schema because community Actor fields can change.
- Keep runs scoped: ask for a maximum result count when the user does not provide one.

## Workflow

1. Classify the user's goal: channel benchmark, keyword/topic discovery, video list extraction, comment mining, Shorts research, or transcript/content analysis.
2. Pick the smallest Actor route that answers the question.
3. Inspect the Actor input schema, then build an input with explicit caps (`maxResults`, `maxItems`, `limit`, or the schema's equivalent field).
4. If the run could be large, state the planned scope and ask for confirmation before launching.
5. Run the Actor, fetch dataset items, normalize fields, deduplicate by video URL or comment ID, and produce the requested table/summary.
6. Include provenance: Actor ID, run ID or dataset ID when available, query/channel URLs, and extraction date.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| General YouTube videos, channels, playlists, search results, metadata, subtitles | `streamers/youtube-scraper` | apify | Default route for most YouTube research tasks |
| Video comments from one or more videos | `streamers/youtube-comments-scraper` | apify | Audience sentiment, FAQ extraction, pain points, objections |
| Shorts from channels | `streamers/youtube-shorts-scraper` | apify | Shorts strategy, hook analysis, short-form competitor monitoring |
| Channel-level profile and recent video data | `streamers/youtube-channel-scraper` | apify | Fast channel inventory, creator benchmarking, upload cadence |
| Broad web discovery before YouTube extraction | `apify/google-search-scraper` | apify | Finding YouTube URLs from a topic, brand, competitor, or niche keyword |

Prefer Apify-maintained `streamers/*` Actors when they cover the task. Use community Actors only if the maintained route lacks a needed field, and call that out in the result.

## Decision guide

| User says | Route |
|-----------|-------|
| "Analyze this channel" plus a YouTube channel URL | `streamers/youtube-scraper` or `streamers/youtube-channel-scraper` |
| "Find top videos for this keyword" | `streamers/youtube-scraper` with search input |
| "What are viewers complaining about?" | First get candidate videos, then run `streamers/youtube-comments-scraper` |
| "Analyze Shorts strategy" | `streamers/youtube-shorts-scraper` |
| "Find YouTube creators talking about this product" | `apify/google-search-scraper` to discover URLs, then `streamers/youtube-scraper` |
| "Compare these 5 creators" | Run channel/video extraction per channel and merge normalized metrics |

If the user gives only a broad niche, ask one follow-up for geography/language and maximum results. If they give a direct URL and a clear objective, proceed.

## Schema inspection

Always inspect schema before constructing input:

```bash
apify actors info "streamers/youtube-scraper" --input \
  --json \
  --user-agent apify-awesome-skills/apify-youtube-creator-research \
  2>/dev/null
```

For discovery:

```bash
apify actors search "youtube comments" \
  --json \
  --user-agent apify-awesome-skills/apify-youtube-creator-research \
  --limit 10 \
  2>/dev/null
```

## Running Actors with CLI

Use the schema-correct JSON for the selected Actor. Keep all example values small unless the user approved a larger crawl.

```bash
apify actors call "streamers/youtube-scraper" \
  --input '{"searchQueries":["ai workflow automation"],"maxResults":25}' \
  --json \
  --user-agent apify-awesome-skills/apify-youtube-creator-research \
  2>/dev/null
```

Fetch dataset rows after the run returns a dataset ID:

```bash
apify datasets get-items DATASET_ID \
  --format json \
  --user-agent apify-awesome-skills/apify-youtube-creator-research \
  2>/dev/null
```

If a field name from the example is not present in the live schema, adapt to the schema. Do not force example keys into an Actor that does not support them.

## Analysis patterns

### Channel benchmark

Normalize per channel:

- Channel name and URL
- Subscribers, total views, total videos when available
- Recent upload count and date range
- Median views, median likes, median comments
- View-to-subscriber ratio when subscriber count is available
- Top 5 videos by views and by engagement
- Content pillars inferred from titles/descriptions

### Topic and keyword discovery

Return:

- Top video titles and URLs
- Channel names
- Publish dates
- Views/likes/comments when available
- Repeated title patterns and hooks
- Underserved angles: high-comment/low-quality, old-ranking, or narrow-topic videos
- Suggested video ideas with evidence from extracted rows

### Comment mining

For comments, cluster into:

- Pain points
- Questions and objections
- Feature requests
- Purchase intent signals
- Repeated phrases
- Positive/negative sentiment examples using short paraphrases, not long quotes

Keep the comment sample size explicit. Do not infer demographic facts unless the dataset directly supports them.

### Shorts analysis

Return:

- Hook types in first words of captions/titles
- Posting cadence
- View distribution
- Repeated formats
- Topics that outperform the channel median
- Ideas to test next

## Output format

Default deliverable:

1. Executive summary: 3-5 bullets.
2. Data scope: Actor IDs, queries/URLs, item counts, extraction date.
3. Findings table with URLs and metrics.
4. Opportunities or recommendations tied to evidence.
5. Caveats: missing metrics, private/deleted videos, limited comments, or schema limitations.

For CSV/JSON requests, include normalized fields:

- `source_query`
- `channel_name`
- `channel_url`
- `video_title`
- `video_url`
- `published_at`
- `views`
- `likes`
- `comments_count`
- `duration`
- `is_short`
- `description`
- `scraped_actor`
- `dataset_id`

## Cost and scope guardrails

- Use small test runs first: 10-25 videos or 100-300 comments.
- Ask before comment mining across more than 10 videos or collecting more than 1,000 comments.
- Prefer metadata extraction before comments; comments are often the expensive second step.
- Avoid duplicate runs by deduplicating video URLs before sending them to the comments Actor.

## Error handling

- Empty dataset: verify URL format, privacy status, region/language filters, and whether the Actor expects channel URLs, video URLs, or search terms.
- Schema mismatch: re-run schema inspection and rebuild the input.
- Rate or timeout error: reduce max results, split by channel/query, or run comments only for top videos.
- Missing metrics: leave fields blank and mention the missing field; do not fabricate values.
- Duplicate videos: dedupe by canonical YouTube video ID when available, otherwise by normalized URL.
