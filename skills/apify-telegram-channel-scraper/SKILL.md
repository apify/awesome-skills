---
name: apify-telegram-channel-scraper
description: "Scrape public Telegram channels and search Telegram posts by keyword with no Telegram account, API key or login, using two Apify Actors by the same author. george.the.developer/telegram-channel-scraper returns a channel's messages as JSON rows with text, date, view counts, links, forwarded source and media URLs plus free channel metadata, filtered by date range or keyword, at $0.005 per message and no start fee. george.the.developer/telegram-keyword-search finds posts containing a phrase across channels you name plus public channels found by web search, up to 50 channels per keyword, at $0.004 per matching post. Use when the user says scrape this Telegram channel, export t.me channel messages to JSON or CSV, what did a channel post last week, find Telegram posts mentioning a brand or token, monitor Telegram for a keyword, Telegram OSINT, crypto announcement feed, or asks for a Telegram scraper. Public channels with a web preview only. Both routed Actors are built by this skill's author (see Disclosure)."
author: George Kioko
author_url: https://github.com/the-ai-entrepreneur-ai-hub
license: Apache-2.0
metadata:
  category: data-extraction
  keywords: "telegram, telegram-channel, telegram-scraper, telegram-messages, telegram-posts, keyword-search, brand-monitoring, osint, crypto, news-feed, channel-export, no-login, media-urls, view-counts"
---

# Telegram Public Channels, Messages and Keyword Search

Read public Telegram channels as structured rows, or find public posts that mention a phrase in the channels you name and in channels found by web search, without a Telegram account, phone number, API key or login. Two Actors, one per job. Telegram has no open search across every channel, so coverage is the channels searched, not all of Telegram.

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
3. Both bill per delivered row. Posts that do not match a keyword are never returned or charged on either Actor. The keyword search also has a start event of $0.00005 per run.

Prices are the Store list prices at the time of writing. On the keyword search they are the Free and Bronze plan prices; Silver pays 10% less, Gold and above 20% less. The channel scraper has one flat price. Confirm live prices before a large batch with the info command below.

## Run it with the Apify CLI

Latest 200 posts from one channel, media URLs on:

```bash
apify actors call "george.the.developer/telegram-channel-scraper" -i '{"channels":["durov"],"maxMessages":200,"includeMedia":true}' \
  --json \
  --user-agent apify-awesome-skills/apify-telegram-channel-scraper \
  2>/dev/null
```

Posts from two channels inside a date window, media off to keep rows small. `maxMessages` is at its maximum so the scraper pages back far enough to reach the window:

```bash
apify actors call "george.the.developer/telegram-channel-scraper" -i '{"channels":["binance_announcements","https://t.me/telegram"],"dateFrom":"2026-10-01","dateTo":"2026-10-31","maxMessages":10000,"includeMedia":false}' \
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

A phrase across channels found by web search, 50 posts per keyword, only posts on or after `dateFrom` (set it to today minus 30 days for a rolling month):

```bash
apify actors call "george.the.developer/telegram-keyword-search" -i '{"keywords":["Solana airdrop"],"discoverChannels":true,"maxChannelsPerKeyword":10,"maxResultsPerKeyword":50,"dateFrom":"2026-10-04"}' \
  --json \
  --user-agent apify-awesome-skills/apify-telegram-channel-scraper \
  2>/dev/null
```

Fetch the live input schema before building an input that is not shown here, and check required fields, types and limits against it:

```bash
apify actors info "george.the.developer/telegram-channel-scraper" --input --json \
  --user-agent apify-awesome-skills/apify-telegram-channel-scraper \
  2>/dev/null
```

Confirm live prices:

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
2. Cap the spend with `maxMessages` (default 100, minimum 1, maximum 10,000, per channel). There is no unlimited value and `0` is rejected. For a date window, set `dateFrom` and `dateTo` and raise `maxMessages`. The scraper starts at the newest post and pages back about 20 posts per page for at most `maxMessages / 20 + 5` pages, so a low value can stop before an older window is reached. Only posts inside the window are delivered and billed.
3. Set `includeMedia: false` when the user wants text only. `media[]` is then empty on every row (photos, videos, documents and link previews), `links[]` and `textHtml` stay, and a post with media but no text is delivered free with `billable: false`.
4. Dedupe on `messageUrl`. Use `viewCountParsed` for sorting; `viewCount` is the display string ("5.3M").
5. Report channels in, messages delivered, date span covered, and the dataset link. Call an export complete only when the oldest `datetime` delivered reaches the start of the window, or the row count for the channel is below `maxMessages`.

## Workflow: find posts mentioning a phrase

1. One to 20 literal phrases in `keywords`. Shorter phrases match more; "airdrop" beats "the upcoming Solana airdrop".
2. If the user names channels, pass them in `channels`; they are searched first and count toward `maxChannelsPerKeyword` (default 10, max 50).
3. `maxResultsPerKeyword` (default 50, max 1,000) is the spend cap per keyword. `dateFrom` trims old posts before delivery.
4. A post that matches two keywords is delivered once per keyword. Dedupe on `messageUrl` plus `keyword`, or on `messageUrl` alone for a flat list.
5. Report which channels came from input and which from discovery (`discoveredVia` is `input` or `google`).

## Workflow: monitor channels on a schedule

1. Save the channel scraper call as a task with the user's channels and put it on a daily or hourly schedule.
2. On each run set `dateFrom` to the previous run's date (ISO `YYYY-MM-DD`). Dates are whole days and inclusive, so posts from that day which the previous run already delivered are delivered and billed again. Dedupe on `messageUrl` against what was already stored, and count the overlap day in the cost estimate.
3. Keep `maxMessages` at a sane cap per channel so a very active channel cannot run away. A channel that returns exactly `maxMessages` rows was cut off; raise the cap or run more often.
4. Channel metadata (`channelName`, `subscriberCount`, `isVerified`) rides along free on every row, so subscriber growth can be tracked from the same runs.

## What you get

Channel scraper, one row per message:

- Channel: `channel`, `channelName`, `channelDescription`, `subscriberCount`, `channelAvatarUrl`, `isVerified`
- Message: `messageId`, `messageUrl`, `text`, `textHtml`, `datetime`, `viewCount`, `viewCountParsed`, `author`, `forwardedFrom`, `forwardedFromUrl`, `replyTo`
- Content: `links[]`, `media[]` (objects with a `type`; photos, videos and stickers carry `url`, link previews carry `title`, `description`, `siteName` and `imageUrl`, documents carry `title` and `size`), `scrapedAt`
- Billing: `billable` (false on a row delivered free), and `matchedKeyword` when `keywords` is set

Keyword search, one row per matching post per keyword:

- `keyword`, `channel`, `channelName`, `subscriberCount`
- `messageId`, `messageUrl`, `text`, `datetime`, `viewCount`, `viewCountParsed`, `forwardedFrom`, `links[]`, `mediaTypes[]`
- `discoveredVia` (`input` or `google`), `scrapedAt`, `charged`

`subscriberCount` and `viewCount` are display strings such as "5.3M", not audited numbers. Missing metadata is `null` or absent.

## Inputs

Channel scraper:

- `channels` (array, required): usernames, @handles or t.me URLs.
- `maxMessages` (integer, default 100, 1 to 10,000) per channel; with `keywords` it applies per channel and keyword.
- `keywords` (array, default empty, up to 20): deliver only messages containing one of these, case insensitive.
- `discoverChannels` (boolean, default false): with keywords, also search up to 10 more public channels per keyword found by web search.
- `includeMedia` (boolean, default true), `dateFrom` and `dateTo` (ISO `YYYY-MM-DD`), `proxyConfiguration` (optional).

Keyword search:

- `keywords` (array, required): 1 to 20 literal phrases.
- `channels` (array, optional): searched before discovery.
- `discoverChannels` (boolean, default true), `maxChannelsPerKeyword` (integer, default 10, max 50)
- `maxResultsPerKeyword` (integer, default 50, max 1,000), `dateFrom` (ISO date or datetime)

## Cost

Both Actors are pay per event and bill per delivered row.

- 1,000 messages from the channel scraper: $5.00. Channel metadata is free.
- 100 matching posts from the keyword search: $0.40 plus the start event.
- Neither Actor charges message events for channels that turn out private, empty or missing. The keyword search start event of $0.00005 still applies.

Suggested confirmation thresholds: mention the estimate under about $5, warn the user over about $5, get explicit confirmation over about $20. Two inputs can surprise. One is a high `maxMessages` with no date window (10,000 messages is $50 per channel). The other is `discoverChannels: true` on the channel scraper, which adds up to 10 channels per keyword. Estimate both and confirm before running. See `references/gotchas.md`.

## Honest limits

- Public channels with the web preview enabled only. Private channels, private groups and member lists are out of reach by design.
- The keyword search covers the channels it searches, named plus discovered. It is not a complete search of every public Telegram channel.
- Content comes from Telegram's web preview. Some media types expose thumbnails rather than full resolution files.
- Keyword matching is literal, case insensitive, on post text only. Images and videos are not searched.
- The channel scraper paces requests to avoid blocks, so very large exports take minutes, not seconds. Default run timeout is 60 minutes on the channel scraper and 30 minutes on the keyword search; the keyword search stops new fetches one minute before its timeout and flushes what it has.
- Channel discovery depends on a web search engine. When Google returns nothing, DuckDuckGo is tried; when both return nothing, only the named channels are searched and the run still succeeds.

## Troubleshooting

- Zero rows for a channel: the handle is wrong, the channel is private, or it has no web preview. Open `https://t.me/s/<handle>` to check. Skipped channels are logged, the run does not fail.
- Fewer rows than `maxMessages`: usually the channel has fewer posts in the date window. For an older window with a low `maxMessages`, the scraper stopped paging before it reached the window; raise `maxMessages` (up to 10,000) and run again.
- Input rejected with `maxMessages must be >= 1`: `0` is not allowed and there is no unlimited value. Use 1 to 10,000.
- Keyword search returns nothing: the phrase is too long or too specific. Try a shorter phrase, or name channels and set `discoverChannels: false` to see whether the problem is discovery or matching.
- Same post appears twice: it matched two keywords, or two runs overlapped in time. Dedupe on `messageUrl`.
- `viewCount` will not sort: it is a display string. Sort on `viewCountParsed`.
- Rows with `charged: false` from the keyword search: the run was not a paid pay per event run, for example a local run. The data is the same.

See `references/gotchas.md` for cost guardrails and error recovery, and `references/actor-index.md` for the routing table with prices and caps.
