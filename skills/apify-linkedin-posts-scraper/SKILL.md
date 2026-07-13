---
name: apify-linkedin-posts-scraper
description: Scrape public LinkedIn posts into clean, structured JSON with the Apify LinkedIn Posts API Actor (johnvc/linkedin-posts-api). Give a profile URL to discover a person's recent posts, or specific post URLs to fetch directly, and get one row per post with text, hashtags, media, author details, and engagement counts (reactions, comments, shares). Use when the user wants to scrape LinkedIn posts, export LinkedIn posts to JSON or CSV, build a LinkedIn posts dataset, pull a creator's or a competitor's recent posts, or asks for a LinkedIn posts scraper or LinkedIn posts API. Pay-per-post billing, MCP-ready for Claude and other AI agents.
author: John Cole
author_url: https://github.com/johnisanerd
license: MIT
metadata:
  version: "1.0"
---

# LinkedIn Posts Scraper: Posts to Structured JSON

Scrape public LinkedIn posts into clean JSON with the Apify LinkedIn Posts API. Point it at a profile to pull that person's recent posts, or pass specific post URLs to fetch them directly. You get one flat row per post: text, hashtags, media, author, and engagement counts.

## When to use this skill

- The user wants to scrape or export LinkedIn posts (to JSON, CSV, a sheet, or a database).
- They want a creator's, brand's, or competitor's recent posts.
- They want to build a dataset of posts for research, monitoring, or content ideas.
- They ask for a "LinkedIn posts scraper" or "LinkedIn posts API".

Not for: private or connection-only content, profile bio data (use the LinkedIn Profile API), or company pages (use the LinkedIn Company API).

## What you get (one row per post)

`postUrl`, `postId`, `postType`, `datePosted`, `title`, `text`, `hashtags`, `authorName`, `authorHeadline`, `authorUrl`, `authorFollowers`, `authorType`, `numLikes`, `numComments`, `numShares`, `images`, `videos`, `embeddedLinks`, `taggedCompanies`, `taggedPeople`, `topComments`, `summary`. A post that cannot be collected comes back as an error row (`result_type` = "error") instead of failing the run.

## Prerequisites

- Apify account (sign up at https://apify.com?fpr=9n7kx3&fp_sid=awesomeskills).
- Authentication via `apify login`, or an `APIFY_TOKEN` environment variable (Apify Console, Settings, Integrations).

## The Actor

- Store page: https://apify.com/johnvc/linkedin-posts-api?fpr=9n7kx3&fp_sid=awesomeskills
- Actor ID: `johnvc/linkedin-posts-api`
- Pricing: pay per post returned (see `references/gotchas.md`).

## Run it with the Apify CLI

Discover a profile's recent posts:

```bash
apify actors call "johnvc/linkedin-posts-api" -i '{"profileUrls":["https://www.linkedin.com/in/williamhgates"],"maxPostsPerProfile":20}' \
  --json \
  --user-agent apify-awesome-skills/apify-linkedin-posts-scraper \
  2>/dev/null
```

Fetch specific posts by URL:

```bash
apify actors call "johnvc/linkedin-posts-api" -i '{"postUrls":["https://www.linkedin.com/feed/update/urn:li:activity:7446904645010210816"]}' \
  --json \
  --user-agent apify-awesome-skills/apify-linkedin-posts-scraper \
  2>/dev/null
```

Every call carries the three flags this repo expects: `--json`, `--user-agent apify-awesome-skills/apify-linkedin-posts-scraper`, and `2>/dev/null`.

## Run it from Claude or another AI agent (MCP)

The Actor is MCP-ready. Add the hosted server URL:

`https://mcp.apify.com/?tools=actors,docs,johnvc/linkedin-posts-api`

Then ask, for example: "Use the LinkedIn Posts API to pull Bill Gates's last 20 posts and export them as JSON." MCP setup docs: https://docs.apify.com/platform/integrations/mcp

## Workflow

1. Pick the mode. Profile URLs for discovery (up to 25 per run), or post URLs for exact fetches (up to 1000 per run). You can pass both; supply at least one.
2. Bound the volume. Set `maxPostsPerProfile` (default 20, max 200), and, for a window, `startDate` and `endDate` (YYYY-MM-DD, discovery only).
3. Estimate cost, then confirm with the user if the run is large. See `references/gotchas.md`.
4. Run the Actor and read the dataset. Deliver the rows as JSON or CSV, or hand back the dataset link.

## Inputs

- `profileUrls` (array of `/in/` profile URLs, up to 25, discovery mode)
- `postUrls` (array of post URLs, up to 1000, exact fetch)
- `maxPostsPerProfile` (integer, default 20, max 200)
- `startDate` / `endDate` (YYYY-MM-DD, discovery only)

Non-`/in/` profile URLs (company or school pages) are skipped.

## Cost

Billing is per post returned, so a discovery run costs roughly the number of profiles times `maxPostsPerProfile`. Estimate first and confirm large runs. Thresholds are in `references/gotchas.md`.

## Troubleshooting

- Empty profile: you get an error row (`result_type` "error", `error_type` "CollectionError"), not a failed run. Skip it; the rest of the batch still returns.
- Wrong URL type: only `/in/` profile URLs discover posts; company or school URLs are skipped.
- Over a limit: keep profiles at 25 or fewer and post URLs at 1000 or fewer per run; split larger jobs into batches.

See `references/gotchas.md` for cost guardrails and error recovery, and `references/actor-index.md` for the Actor routing table.

## Related LinkedIn Actors

- LinkedIn Profile API: https://apify.com/johnvc/linkedin-profile-api?fpr=9n7kx3&fp_sid=awesomeskills
- LinkedIn Company API: https://apify.com/johnvc/linkedin-company-api?fpr=9n7kx3&fp_sid=awesomeskills
- LinkedIn Jobs API: https://apify.com/johnvc/linkedin-jobs-api?fpr=9n7kx3&fp_sid=awesomeskills
