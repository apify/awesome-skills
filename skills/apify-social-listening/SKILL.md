---
name: apify-social-listening
description: Monitor what people actually say about a brand, product, competitor, or topic on Reddit — mentions, sentiment, the communities driving the conversation, and verbatim voice-of-customer quotes — then optionally layer in YouTube channel/video engagement. Routes keyword and community monitoring to a Reddit scraper with built-in sentiment scoring, aggregates sentiment and themes, and surfaces the strongest quotes. Use when a user asks to track brand mentions, run social listening, do voice-of-customer research, gauge sentiment about a product or competitor, find Reddit discussions about a topic, monitor a subreddit, or analyze a YouTube channel's engagement.
author: Renzo Madueno
author_url: https://github.com/renzomacar
---

# Social Listening

Turn a brand/topic and a few options into a social-listening report: Reddit mentions with sentiment, the subreddits driving the conversation, emerging themes, and verbatim voice-of-customer quotes — plus optional YouTube channel/video engagement analysis.

This skill is Reddit-first because Reddit is where unprompted, candid opinions about products and brands live, and the routed Actor scores sentiment in the same run. YouTube is a secondary, **engagement-analysis** module (it inspects specific channels/videos you name — it does not keyword-search YouTube for mentions).

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

Two execution paths, same Actors:

- **MCP path (default in Claude sessions).** If the [Apify MCP server](https://mcp.apify.com) is connected, no setup is needed — auth runs through the user's account. Use the `call-actor` and `get-dataset-items` tools.
- **CLI path (portable / scheduled / non-Claude).** Requires the Apify CLI and a token. Every CLI call in this skill uses three flags: `--json`, `--user-agent apify-awesome-skills/apify-social-listening`, and `2>/dev/null`.

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Step 1: Collect the listening brief (subject, scope, window, depth, modules)
- [ ] Step 2: Route each module to the right Actor + input
- [ ] Step 3: Run the Actor(s), confirm cost if the run is large
- [ ] Step 4: Aggregate sentiment, themes, communities, and quotes
- [ ] Step 5: Deliver the listening report
```

### Step 1: Collect the listening brief

Ask these as one block before any Actor call:

1. **Subject** — the brand, product, competitor, or topic to listen for (e.g. `"Notion AI"`, `"my-saas"`, `"electric bikes"`). This becomes the Reddit `searchQueries` term(s). Accept several.
2. **Scope** — `whole-of-Reddit` (keyword search everywhere, default) **or** `specific communities` (the user names subreddits, e.g. `r/SaaS`, `r/productivity`). Communities give depth; keyword search gives reach. You can do both.
3. **Time window** — `today` / `week` (default) / `month` / `year` / `all`. Maps to the Reddit `timeFilter`.
4. **Depth** — how many posts to pull per query/subreddit (`maxPostsPerSubreddit`, default `100`). Larger = more cost and more signal.
5. **Voice-of-customer** — include comments? (`includeComments`). Default `yes` for listening, since the candid opinions live in comment threads. Comments add cost per post.
6. **YouTube module** (optional) — if the user wants engagement on specific channels/videos (theirs or a competitor's), collect the channel or video URLs. Skip if they only care about mentions.

If the subject is ambiguous (a common word that will pull noise, e.g. `"apple"`), say so and suggest narrowing via communities or a more specific query.

### Step 2: Route each module to the right Actor

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Brand/topic **mentions + sentiment** across Reddit | `renzomacar/reddit-scraper` | community | keyword search (`searchQueries`) with built-in sentiment scoring |
| Deep-dive on **specific subreddits** | `renzomacar/reddit-scraper` | community | community monitoring via `subreddits` |
| **Voice-of-customer** quotes | `renzomacar/reddit-scraper` | community | `includeComments: true` pulls candid comment threads |
| **YouTube channel/video engagement** (named URLs) | `renzomacar/youtube-scraper` | community | competitor channel analysis, view/like/comment signals |

`Tier` = `apify` (Apify-maintained) or `community` (third-party). Both Actors are public on the [Apify Store](https://apify.com/store).

> Note: the YouTube Actor takes channel/video **URLs**, not search keywords — it analyzes engagement on content you name, it does not find mentions of your brand on YouTube. Set expectations accordingly.

### Step 3: Run the Actor(s)

Build the Reddit input from the brief. Keyword listening + voice-of-customer, last week:

```bash
apify actors call "renzomacar/reddit-scraper" \
  -i '{"searchQueries": ["Notion AI"], "sortBy": "relevance", "timeFilter": "week", "maxPostsPerSubreddit": 100, "includeComments": true, "maxCommentsPerPost": 50}' \
  --user-agent apify-awesome-skills/apify-social-listening \
  --json 2>/dev/null
```

Specific-community monitoring instead of (or in addition to) keyword search:

```bash
apify actors call "renzomacar/reddit-scraper" \
  -i '{"subreddits": ["SaaS", "productivity"], "sortBy": "top", "timeFilter": "month", "maxPostsPerSubreddit": 75, "includeComments": true}' \
  --user-agent apify-awesome-skills/apify-social-listening \
  --json 2>/dev/null
```

Optional YouTube engagement module:

```bash
apify actors call "renzomacar/youtube-scraper" \
  -i '{"channelUrls": ["https://www.youtube.com/@competitor"], "maxVideosPerChannel": 30}' \
  --user-agent apify-awesome-skills/apify-social-listening \
  --json 2>/dev/null
```

**MCP path equivalent:** call `call-actor` with the same actor id and the same input object, then `get-dataset-items` for the run's dataset.

Cost guardrails and recovery are in [`references/gotchas.md`](references/gotchas.md). If a run looks large (high depth × many queries × comments), state the rough scale and confirm before launching.

### Step 4: Aggregate sentiment, themes, communities, quotes

The Reddit dataset has one item per post and (when `includeComments`) per comment, distinguished by `dataType`. Each carries `score`, `upvoteRatio`, `commentCount`, `subreddit`, `body`, `postTitle`, `author`, `createdUtc`, `url`. Build the report from these:

- **Sentiment** — the Actor scores community reception via `score` and `upvoteRatio`. Treat high-`score` / high-`upvoteRatio` items as positively received and low/negative as contested. Read the text of the top and bottom items to label sentiment (positive / neutral / negative) rather than trusting the number alone — a high score can sit on a critical post.
- **Volume & trend** — count mentions over the window; note spikes by `createdUtc`.
- **Communities** — group by `subreddit`; report which communities drive the conversation.
- **Themes** — cluster recurring topics from `postTitle` + `body` (praise, complaints, comparisons, feature requests, questions).
- **Voice-of-customer** — pull 3–8 verbatim quotes from high-signal posts/comments, each with its `subreddit` and `url` so the user can verify.

For the YouTube module, summarize per video: `viewCount`, `likeCount`, `commentCount`, `publishDate`, and engagement rate (likes+comments / views).

### Step 5: Deliver the listening report

Render a compact report:

1. **Summary** — subject, window, total mentions, overall sentiment split (e.g. 60% positive / 25% neutral / 15% negative).
2. **Top communities** — subreddits by mention volume.
3. **Themes** — 3–6 bullets, each with a representative quote + link.
4. **Voice-of-customer** — the strongest verbatim quotes with `subreddit` + `url`.
5. **Notable posts** — highest-`score` and most-discussed items, linked.
6. **YouTube engagement** (if run) — per-channel/video table.
7. **Dataset link** — the Apify dataset/console URL for the full data.

Always link back to source posts so claims are verifiable. State the data window and that this is public-Reddit data, not a representative survey.

## Responsible use

Only public Reddit/YouTube content is collected. Don't use this to target, dox, or harass individuals — aggregate sentiment and themes, not profiles of named private users. Respect each platform's terms.
