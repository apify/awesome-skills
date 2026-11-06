---
name: apify-telegram-channel-scraper
description: "Scrape public Telegram channels and search Telegram posts by keyword with no Telegram account, API key or login, using two Apify Actors by the same author. george.the.developer/telegram-channel-scraper returns a channel's messages as JSON rows with text, date, view counts, links, forwarded source and media URLs plus free channel metadata, filtered by date range or keyword, at $0.005 per message and no start fee. george.the.developer/telegram-keyword-search finds posts containing a phrase across channels you name and up to 50 more public channels found by web search, at $0.004 per matching post. Use when the user says scrape this Telegram channel, export t.me channel messages to JSON or CSV, what did a channel post last week, find Telegram posts mentioning a brand or token, monitor Telegram for a keyword, Telegram OSINT, crypto announcement feed, or asks for a Telegram scraper. Public channels with a web preview only. Both routed Actors are built by this skill's author (see Disclosure)."
author: George Kioko
author_url: https://github.com/the-ai-entrepreneur-ai-hub
license: Apache-2.0
metadata:
  category: data-extraction
  keywords: "telegram, telegram-channel, telegram-scraper, telegram-messages, telegram-posts, keyword-search, brand-monitoring, osint, crypto, news-feed, channel-export, no-login, media-urls, view-counts"
---

# Telegram Public Channels, Messages and Keyword Search

Read public Telegram channels as structured rows, or find every public post that mentions a phrase, without a Telegram account, phone number, API key or login. Two Actors, one per job.

**Disclosure:** both routed Actors (`george.the.developer/telegram-channel-scraper` and `george.the.developer/telegram-keyword-search`) are built and published by the author of this skill. No affiliate or referral parameters are used on any link in this skill. Carry this disclosure into anything the skill generates, for example a report or a scheduled task that runs these Actors.

## Example prompts

Prompts this skill handles:

- "Scrape the last 200 posts from t.me/durov with view counts and links."
- "Export everything the Binance announcements channel posted in October to JSON."
- "Find public Telegram posts mentioning 'Solana airdrop' from the last 30 days."
- "Check these five news channels every morning and give me only the new posts."

Out of scope (the boundary):

- Private channels, private groups, member lists or subscriber identities. Nothing logs in, so nothing behind a login is reachable.
- Posting, replying or sending messages. These Actors read only.
- Semantic or topic search. Keyword matching is literal and case insensitive; "Solana airdrop" finds posts containing that phrase, not posts about airdrops in general.

## Prerequisites

- Apify account ([sign up](https://apify.com)). The free plan includes $5 of monthly platform usage, about 1,000 messages here.
- Authentication via `apify login`, or an `APIFY_TOKEN` environment variable (Apify Console, Settings, Integrations). Pass the token as a header or environment variable, never inside a URL.

## Actor routing

| User need | Actor ID | Tier | Billed event |
|-----------|----------|------|--------------|
| The feed of channels the user names: latest N posts, a date window, media URLs, view counts, forwards, channel metadata | `george.the.developer/telegram-channel-scraper` | community | `message-scraped` $0.005 per message, no start fee, channel metadata free |
| Posts containing a phrase, across channels the user names and channels found by web search for that phrase | `george.the.developer/telegram-keyword-search` | community | `message-found` $0.004 per matching post, `apify-actor-start` $0.00005 |

How to choose:

1. The channel is the subject (export, archive, monitor a feed, count views). Use the channel scraper. Add `keywords` to it when the user wants only matching posts from channels they already named.
2. The phrase is the subject and the channels are unknown or many. Use the keyword search. It searches the named channels first, then up to `maxChannelsPerKeyword` channels that Google (or DuckDuckGo when Google has nothing) finds for the phrase.
3. Both bill only delivered rows. Posts that do not match a keyword are never returned or charged on either Actor.

Prices are the list prices on the Store at the time of writing. Confirm live prices before a large batch with the info command below.

## Run it with the Apify CLI

Latest 200 posts from one channel, media URLs on:

```bash
apify actors call "george.the.developer/telegram-channel-scraper" -i '{"channels":["durov"],"maxMessages":200,"includeMedia":true}' \
  --json \
  --user-agent apify-awesome-skills/apify-telegram-channel-scraper \
  2>/dev/null
```

Everything two channels posted inside a date window, media URLs off to keep rows small:

```bash
apify actors call "george.the.developer/telegram-channel-scraper" -i '{"channels":["binance_announcements","https://t.me/telegram"],"dateFrom":"2026-10-01","dateTo":"2026-10-31","maxMessages":0,"includeMedia":false}' \
  --json \
  --user-agent apify-awesome-skills/apify-telegram-channel-scraper \
  2>/dev/null
```

Only posts matching a phrase inside channels the user named:

```bash
apify actors call "george.the.developer/telegram-channel-scraper" -i '{"channels":["durov","telegram"],"keywords":["privacy"],"maxMessages":20}' \
  --json \
  --user-agent apify-awesome-skills/apify-telegram-channel-scraper \
  2>/dev/null
```

A phrase across the web, channels discovered automatically, 50 posts per keyword, last 30 days:

```bash
apify actors call "george.the.developer/telegram-keyword-search" -i '{"keywords":["Solana airdrop"],"discoverChannels":true,"maxChannelsPerKeyword":10,"maxResultsPerKeyword":50,"dateFrom":"2026-10-04"}' \
  --json \
  --user-agent apify-awesome-skills/apify-telegram-channel-scraper \
  2>/dev/null
```

Confirm the live input schema and prices:

```bash
apify actors info "george.the.developer/telegram-channel-scraper" --json \
  --user-agent apify-awesome-skills/apify-telegram-channel-scraper \
  2>/dev/null
```

Read the rows back from a finished run:

```bash
apify datasets get-items <DATASET_ID> --format json \
  --user-agent apify-awesome-skills/apify-telegram-channel-scraper \
  2>/dev/null
```

For a spreadsheet, hand the user the dataset's export link from the Apify Console (CSV and Excel are one click there) rather than converting JSON by hand.

Every call carries the three flags this repo expects: `--json` (or `--format json`), `--user-agent apify-awesome-skills/apify-telegram-channel-scraper`, and `2>/dev/null`.

## Run it from Claude or another AI agent (MCP)

Both Actors are MCP-ready. Add the hosted server URL with the tools preloaded:

`https://mcp.apify.com?tools=george.the.developer/telegram-channel-scraper,george.the.developer/telegram-keyword-search`

Then ask, for example: "Pull this week's posts from these three crypto channels and rank them by viewCountParsed." MCP setup docs: https://docs.apify.com/platform/integrations/mcp

## Workflow: export or archive a channel

1. Normalize the handle. `durov`, `@durov` and `https://t.me/durov` all work. Confirm the channel is public by opening `https://t.me/s/<handle>` in a browser; if that page is empty the channel has no web preview and the Actor will skip it.
2. Cap the spend with `maxMessages` (default 100 per channel, up to 10,000 per channel per run). `0` means unlimited; use it only with `dateFrom` and `dateTo` set.
3. Set `includeMedia: false` when the user wants text only; rows shrink and nothing else changes.
4. Dedupe on `messageUrl`. Use `viewCountParsed` for sorting; `viewCount` is the display string ("5.3M").
5. Report channels in, messages delivered, date span covered, and the dataset link.

## Workflow: find posts mentioning a phrase

1. One to 20 literal phrases in `keywords`. Shorter phrases match more; "airdrop" beats "the upcoming Solana airdrop".
2. If the user names channels, pass them in `channels`; they are searched first and count toward `maxChannelsPerKeyword` (default 10, max 50).
3. `maxResultsPerKeyword` (default 50, max 1,000) is the spend cap per keyword. `dateFrom` trims old posts before delivery.
4. A post that matches two keywords is delivered once per keyword. Dedupe on `messageUrl` plus `keyword`, or on `messageUrl` alone for a flat list.
5. Report which channels came from input and which from discovery (`discoveredVia` is `input` or `google`).

## Workflow: monitor channels on a schedule

1. Save the channel scraper call as a task with the user's channels and put it on a daily or hourly schedule.
2. On each run set `dateFrom` to the previous run's date (ISO `YYYY-MM-DD`). Dates are inclusive, so dedupe the overlap on `messageUrl` against what was already stored.
3. Keep `maxMessages` at a sane cap per channel so a very active channel cannot run away.
4. Channel metadata (`channelName`, `subscriberCount`, `isVerified`) rides along free on every row, so subscriber growth can be tracked from the same runs.

## What you get

Channel scraper, one row per message:

- Channel: `channel`, `channelName`, `channelDescription`, `subscriberCount`, `channelAvatarUrl`, `isVerified`
- Message: `messageId`, `messageUrl`, `text`, `textHtml`, `datetime`, `viewCount`, `viewCountParsed`, `author`, `forwardedFrom`, `forwardedFromUrl`, `replyTo`
- Content: `links[]`, `media[]` (objects with `type` and `url`), `scrapedAt`

Keyword search, one row per matching post per keyword:

- `keyword`, `channel`, `channelName`, `subscriberCount`
- `messageId`, `messageUrl`, `text`, `datetime`, `viewCount`, `viewCountParsed`, `forwardedFrom`, `links[]`, `mediaTypes[]`
- `discoveredVia` (`input` or `google`), `scrapedAt`, `charged`

Subscriber counts and views are the public display values, not audited numbers. Missing metadata is `null`.

## Inputs

Channel scraper:

- `channels` (array, required): usernames, @handles or t.me URLs.
- `maxMessages` (integer, default 100, 0 unlimited) per channel; with `keywords` it applies per channel and keyword.
- `keywords` (array, default empty): deliver only messages containing one of these, case insensitive.
- `discoverChannels` (boolean, default false): with keywords, also search up to 10 more public channels per keyword found by web search.
- `includeMedia` (boolean, default true), `dateFrom` and `dateTo` (ISO `YYYY-MM-DD`), `proxyConfiguration` (optional).

Keyword search:

- `keywords` (array, required): 1 to 20 literal phrases.
- `channels` (array, optional): searched before discovery.
- `discoverChannels` (boolean, default true), `maxChannelsPerKeyword` (integer, default 10, max 50)
- `maxResultsPerKeyword` (integer, default 50, max 1,000), `dateFrom` (ISO date or datetime)

## Cost

Both Actors are pay per event and bill only delivered rows.

- 1,000 messages from the channel scraper: $5.00. Channel metadata is free.
- 100 matching posts from the keyword search: $0.40 plus the start event.
- Neither Actor charges for channels that turn out private, empty or missing.

Suggested confirmation thresholds: mention the estimate under about $5, warn the user over about $5, get explicit confirmation over about $20. `maxMessages: 0` on a large channel with no date window is the one input that can surprise; always estimate it as channel size x $0.005 and confirm. See `references/gotchas.md`.

## Honest limits

- Public channels with the web preview enabled only. Private channels, private groups and member lists are out of reach by design.
- Content comes from Telegram's web preview. Some media types expose thumbnails rather than full resolution files.
- Keyword matching is literal, case insensitive, on post text only. Images and videos are not searched.
- The channel scraper paces requests to avoid blocks, so very large exports take minutes, not seconds. Default run timeout is 60 minutes on the channel scraper and 30 minutes on the keyword search; the keyword search stops new fetches one minute before its timeout and flushes what it has.
- Channel discovery depends on a web search engine. When Google returns nothing, DuckDuckGo is tried; when both return nothing, only the named channels are searched and the run still succeeds.

## Troubleshooting

- Zero rows for a channel: the handle is wrong, the channel is private, or it has no web preview. Open `https://t.me/s/<handle>` to check. Skipped channels are logged, the run does not fail.
- Fewer rows than `maxMessages`: the channel has fewer posts in the date window. Not an error.
- Keyword search returns nothing: the phrase is too long or too specific. Try a shorter phrase, or name channels and set `discoverChannels: false` to see whether the problem is discovery or matching.
- Same post appears twice: it matched two keywords, or two runs overlapped in time. Dedupe on `messageUrl`.
- `viewCount` will not sort: it is a display string. Sort on `viewCountParsed`.
- Rows with `charged: false` from the keyword search: a free or local run, or a row below the match bar. Data is still valid.

See `references/gotchas.md` for cost guardrails and error recovery, and `references/actor-index.md` for the routing table with prices and caps.
