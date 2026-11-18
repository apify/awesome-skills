---
name: apify-youtube-data
description: >-
  YouTube data with pay-per-use Apify Actors: video transcripts and subtitles (timestamps optional), YouTube search results with views, channel and position, and video comments. Use when the user says "youtube transcript", "get the subtitles of", "summarize this youtube video", "search youtube for", "youtube rank", "top youtube videos for", or "download youtube comments".
author: Rowfeed
author_url: https://apify.com/rowfeed
metadata:
  category: data-extraction
  keywords: "youtube, youtube transcript, subtitles, captions, youtube search, youtube rank tracker, youtube comments, video summary, rag"
---

# YouTube data (transcripts, search results, comments)

YouTube data with pay-per-use Apify Actors: video transcripts and subtitles (timestamps optional), YouTube search results with views, channel and position, and video comments.

Disclosure: the routed Actors are built and sold by the skill author (Rowfeed); you pay per result on Apify, no subscription.

## Example prompts

Prompts this skill handles:

- "Get the transcripts of these 20 YouTube videos with timestamps"
- "Which videos rank in the top 20 on YouTube for "best running shoes" in the US?"
- "Download the comments of this video and summarize the main complaints"

Out of scope (the boundary):

- "Download the video file" — this skill returns text and metadata, not video files.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. Pick the Actor from the routing table for the user's need.
2. Fetch its input schema (`apify actors info ACTOR_ID --input --json`) and build the input. Every Actor takes a list, so batch the user's items into one run.
3. Tell the user the estimated cost before large runs (the price per event is on the Actor's Store page) and cap spend with `maxTotalChargeUsd`.
4. Run, then summarise the rows returned and give the dataset link.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Transcripts and subtitles of videos | `rowfeed/youtube-transcript-api` | community | Many videos per run, timestamps optional, plain text for LLMs |
| YouTube search results and rank tracking | `rowfeed/youtube-search-api` | community | Views, channel, publish date and position per keyword and country |
| Comments of videos | `rowfeed/youtube-comments-scraper` | community | Comment text, likes and replies; author names off by default |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling Actors — choose your interface

### Option A: Apify CLI (recommended for portability)

    apify actors call "rowfeed/youtube-transcript-api" \
      -i '{"videos":["https://www.youtube.com/watch?v=8jPQjjsBbIc"],"includeTimestamps":true}' \
      --json \
      --user-agent apify-awesome-skills/apify-youtube-data \
      2>/dev/null

    # Fetch results
    apify datasets get-items DATASET_ID --format json \
      --user-agent apify-awesome-skills/apify-youtube-data 2>/dev/null

### Option B: Apify MCP connector

Hosted MCP server at <https://mcp.apify.com>, for example `https://mcp.apify.com?tools=rowfeed/youtube-transcript-api,rowfeed/youtube-search-api,rowfeed/youtube-comments-scraper`.
Documented at <https://docs.apify.com/platform/integrations/mcp>.

### Option C: MCP client of your choice (e.g. `mcpc`)

Standalone CLI client. See <https://github.com/apify/mcpc>.

## Troubleshooting

- Videos without captions return a row with an error message and are not charged.
- Pass video URLs or IDs as a list to batch many videos in one run.
- A row with `error` and `errorMessage` was not charged; the message says what to fix.
