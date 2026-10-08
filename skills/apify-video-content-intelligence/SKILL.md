---
name: apify-video-content-intelligence
description: >
  Turn YouTube, TikTok and Instagram Reels videos into structured data with four TubeText Labs Apify
  Actors: YouTube transcripts (videos, Shorts, playlists, channels; Whisper when captions are missing),
  TikTok transcripts, YouTube channel analytics (subscribers, views, upload rate, Social Blade grade,
  estimated earnings) and an AI video breakdown (hook, shot list, cut pacing, products on screen,
  organic vs ad intent, script). Use when the user says "get the transcript of this YouTube video",
  "transcribe these TikToks", "pull every transcript from this channel", "build a RAG index from a
  YouTube channel", "why did this TikTok go viral", "break down this UGC ad", "shot list of this
  video", "analyze the hooks of these Reels" or "compare these YouTube channels". Out of scope:
  downloading video files, posting, private or login-only content, live streams, and TikTok or
  Instagram profile scraping.
author: TubeText Labs
author_url: https://apify.com/tubetext
metadata:
  category: data-extraction
  keywords: "youtube, youtube-transcript, tiktok, tiktok-transcript, instagram-reels, video-transcript, whisper, speech-to-text, video-analysis, hook-analysis, shot-list, ugc-ads, youtube-channel-analytics, social-blade, rag"
---

# Video Content Intelligence (YouTube, TikTok, Instagram Reels)

Route a plain-language video request to the right TubeText Labs Actor and return structured JSON: transcripts, channel stats or an AI breakdown of how a video is built.

Disclosure: all four routed Actors are paid (pay per event) and built by the skill author (TubeText Labs). Links carry no affiliate parameters.

## Example prompts

Prompts this skill handles:

- "Get the transcripts of the last 20 videos on https://www.youtube.com/@mkbhd as plain text with timestamps."
- "These 5 TikToks are our best ads. Break down the hook, the cuts and the products shown in each one."
- "Compare subscribers, average views and upload frequency for @veritasium and @3blue1brown."

Out of scope (the boundary):

- "Download this TikTok as an MP4." This skill returns text and analysis, not media files.
- "Get all videos from this TikTok profile." TikTok and Instagram profiles aren't supported. Ask the user for video links, or use a profile scraper first and pass the video URLs.

## Prerequisites

- Apify account ([sign up](https://apify.com)); the free plan's monthly credit covers small runs.
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)
- Apify CLI (`npm install -g apify-cli`) or the Apify MCP server.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| YouTube transcript / subtitles / captions; whole channel or playlist; RAG chunks | `tubetext/youtube-transcript-fast` | community | Text, timestamps, SRT, ~N-word chunks; `aiFallback: true` transcribes caption-less videos with Whisper |
| TikTok transcript / speech to text | `tubetext/tiktok-transcript` | community | TikTok captions, or Whisper when missing; share links (`tiktok.com/t/…`) work |
| YouTube channel stats, competitor tracking, Social Blade grade, estimated earnings | `tubetext/youtube-channel-analytics` | community | One row per channel; accepts channel URLs, `@handles`, channel IDs or any video URL |
| Why a video works: hook, shot list, cut pacing, products, ad intent, script | `tubetext/video-breakdown-ai` | community | TikTok, Instagram Reels (beta), YouTube videos, channels and playlists |

If the user only needs the words of a video, use a transcript Actor. It's about 10x cheaper than a breakdown.

## Workflow

### Step 1 — Classify the request

| User gives you | Actor | Input |
|---|---|---|
| YouTube video, Short, playlist or channel URL(s) + "transcript" | youtube-transcript-fast | `{"urls": [...]}`; add `"aiFallback": true` if videos may lack captions; `"maxVideosPerSource": N` for channels/playlists (default 50); `"chunkWords": 300` for RAG |
| TikTok URL(s) + "transcript" | tiktok-transcript | `{"urls": [...]}`; `"aiTranscription": "missing"` (default), `"all"` or `"off"` |
| Channel(s) + "stats / compare / growth / earnings" | youtube-channel-analytics | `{"channels": [...]}`; `"includeSocialBlade": false` skips the Social Blade add-on |
| Any video URL + "why / hook / breakdown / shot list / storyboard / ad analysis" | video-breakdown-ai | `{"urls": [...]}`; `"outputLanguage": "English"` (or "Same as video" and 18 others); `"maxVideosPerSource": N` for YouTube channels/playlists (default 10) |

### Step 2 — Estimate cost and confirm if large

FREE-tier prices (lower on paid Apify plans). Check current pricing with `apify actors info`:

- youtube-transcript-fast: $0.004 per transcript; Whisper fallback $0.006 per audio minute
- tiktok-transcript: $0.003 per transcript; Whisper $0.006 per audio minute
- youtube-channel-analytics: $0.004 per channel, plus $0.005 if Social Blade stats are included (default on)
- video-breakdown-ai: $0.03 per video up to 3 minutes, plus $0.01 per extra started minute. From 2026-10-22: $0.005 per video that couldn't be fetched, and optional `proxyMode: "residential"` at $0.015 per MB.

Invalid, private and unavailable videos are not charged. Before a large run, show the estimate (see [references/gotchas.md](references/gotchas.md)).

### Step 3 — Run

    apify actors call "tubetext/youtube-transcript-fast" -i '{"urls": ["https://www.youtube.com/watch?v=aircAruvnKk"], "aiFallback": true}' \
      --json \
      --user-agent apify-awesome-skills/apify-video-content-intelligence \
      2>/dev/null

    apify actors call "tubetext/video-breakdown-ai" -i '{"urls": ["https://www.tiktok.com/@user/video/1234567890"]}' \
      --json \
      --user-agent apify-awesome-skills/apify-video-content-intelligence \
      2>/dev/null

The call returns run metadata. Read `storage.defaultDatasetId` and fetch the results:

    apify datasets get-items DATASET_ID --format json \
      --user-agent apify-awesome-skills/apify-video-content-intelligence 2>/dev/null

Fetch the input schema before building unusual inputs:

    apify actors info "tubetext/video-breakdown-ai" --input --json \
      --user-agent apify-awesome-skills/apify-video-content-intelligence 2>/dev/null

### Step 4 — Deliver

- Transcripts: report `status` per video (`ok`, `no_transcript`, `skipped`, …) and hand back `transcript` (or `timestampedText` / `srt` / `chunks` if requested).
- Breakdowns: lead with `hook` (type and why it works), `whyItWorked`, `pacing.cutsPerMinute`, `products` and `commercialIntent`. Then offer the `shots` list.
- Channel analytics: a comparison table of `subscribers`, `avgViewsRecent`, `uploadsPerWeek`, `socialBlade.grade` and estimated earnings.

## Calling Actors — other interfaces

- Apify MCP connector: <https://mcp.apify.com> ([docs](https://docs.apify.com/platform/integrations/mcp))
- MCP client of your choice, e.g. [mcpc](https://github.com/apify/mcpc)

## Troubleshooting

- `no_transcript` on YouTube → the video has no captions. Rerun with `"aiFallback": true` (billed per audio minute).
- `youtube_blocking_now` on video-breakdown-ai → YouTube is blocking broadly right now. These items aren't charged; retry later.
- TikTok/Instagram profile URL returns `skipped` → pass individual video links.
- More in [references/gotchas.md](references/gotchas.md).
