---
name: apify-linkedin-post-engagement
description: Analyze LinkedIn post engagement with the Apify LinkedIn Posts API Actor (johnvc/linkedin-posts-api). Collect a profile's posts or a list of post URLs, then measure reactions, comments, and shares alongside author reach (followers, headline) to see what performs. Use when the user wants to analyze LinkedIn post engagement, measure engagement rate, find a creator's or a competitor's top-performing posts, benchmark engagement across profiles, track post engagement over time, or build a LinkedIn engagement report. Returns one row per post with numLikes, numComments, numShares, datePosted, and a ready-made engagement view. Pay-per-post billing, MCP-ready for Claude and other AI agents.
author: John Cole
author_url: https://github.com/johnisanerd
license: MIT
metadata:
  version: "1.0"
---

# Analyze LinkedIn Post Engagement

Measure how LinkedIn posts perform with the Apify LinkedIn Posts API. Collect a profile's posts (or a set of post URLs), then compare reactions, comments, and shares against author reach to find what works and what does not.

## When to use this skill

- The user wants to analyze LinkedIn post engagement or an engagement rate.
- They want a creator's or a competitor's top-performing posts.
- They want to benchmark engagement across several profiles, or track it over time.
- They want a simple engagement report from a set of LinkedIn posts.

Not for: LinkedIn's own private analytics dashboard, profile bio data (use the LinkedIn Profile API), or ad performance.

## What you get (per post)

`authorName`, `authorHeadline`, `authorFollowers`, `numLikes`, `numComments`, `numShares`, `datePosted`, `postUrl`, `text`, `hashtags`. The Actor also ships a ready-made "engagement" dataset view with exactly these engagement columns, so you can read reach and reactions side by side.

## Prerequisites

- Apify account (sign up at https://apify.com?fpr=9n7kx3&fp_sid=awesomeskills).
- Authentication via `apify login`, or an `APIFY_TOKEN` environment variable (Apify Console, Settings, Integrations).

## The Actor

- Store page: https://apify.com/johnvc/linkedin-posts-api?fpr=9n7kx3&fp_sid=awesomeskills
- Actor ID: `johnvc/linkedin-posts-api`
- Pricing: pay per post returned (see `references/gotchas.md`).

## Run it with the Apify CLI

Collect a profile's recent posts for engagement analysis:

```bash
apify actors call "johnvc/linkedin-posts-api" -i '{"profileUrls":["https://www.linkedin.com/in/williamhgates"],"maxPostsPerProfile":50}' \
  --json \
  --user-agent apify-awesome-skills/apify-linkedin-post-engagement \
  2>/dev/null
```

Read the engagement view of the resulting dataset:

```bash
apify datasets get-items DATASET_ID --format json \
  --user-agent apify-awesome-skills/apify-linkedin-post-engagement \
  2>/dev/null
```

Every call carries the three flags this repo expects: `--json`, `--user-agent apify-awesome-skills/apify-linkedin-post-engagement`, and `2>/dev/null`.

## Run it from Claude or another AI agent (MCP)

The Actor is MCP-ready. Add the hosted server URL:

`https://mcp.apify.com/?tools=actors,docs,johnvc/linkedin-posts-api`

Then ask, for example: "Pull Bill Gates's last 50 posts, rank them by engagement, and tell me which hashtags get the most reactions." MCP setup docs: https://docs.apify.com/platform/integrations/mcp

## Workflow

1. Pick the profiles to measure (the user's own, a creator, or competitors), up to 25 per run.
2. Collect posts. Use discovery with a generous `maxPostsPerProfile` (say 50), and an optional `startDate`/`endDate` window for period-over-period comparisons.
3. Score engagement per post. Total engagement is `numLikes` + `numComments` + `numShares`. When `authorFollowers` is present, engagement rate is total engagement divided by `authorFollowers`.
4. Rank and summarize: top posts, engagement by hashtag, and trend by `datePosted`. Deliver a short table or the dataset link.

## Inputs

- `profileUrls` (array of `/in/` profile URLs, up to 25, discovery mode)
- `postUrls` (array of post URLs, up to 1000, exact fetch)
- `maxPostsPerProfile` (integer, default 20, max 200)
- `startDate` / `endDate` (YYYY-MM-DD, discovery only)

## Cost

Billing is per post returned, so a discovery run costs roughly the number of profiles times `maxPostsPerProfile`. Estimate first and confirm large runs. See `references/gotchas.md`.

## Honest limits

- Engagement rate depends on `authorFollowers`, which is returned when available. If it is missing, report raw counts instead.
- Counts are a snapshot at fetch time. For trend tracking, run on a schedule and compare dates.
- Public posts only. This does not read LinkedIn's private analytics.

## Troubleshooting

- Empty profile: you get an error row (`result_type` "error"), not a failed run. Skip it.
- Over a limit: keep profiles at 25 or fewer per run; split larger jobs into batches.

See `references/gotchas.md` for cost guardrails and error recovery, and `references/actor-index.md` for the Actor routing table.

## Related LinkedIn Actors

- LinkedIn Profile API: https://apify.com/johnvc/linkedin-profile-api?fpr=9n7kx3&fp_sid=awesomeskills
- LinkedIn Company API: https://apify.com/johnvc/linkedin-company-api?fpr=9n7kx3&fp_sid=awesomeskills
- LinkedIn Jobs API: https://apify.com/johnvc/linkedin-jobs-api?fpr=9n7kx3&fp_sid=awesomeskills
