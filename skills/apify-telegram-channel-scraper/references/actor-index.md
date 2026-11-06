# Actor index, apify-telegram-channel-scraper

Routing table for the two Actors this skill uses. Both are built and published by the author of the skill (see the Disclosure in SKILL.md). Prices are Store list prices at the time of writing; confirm with `apify actors info "<actor-id>" --json --user-agent apify-awesome-skills/apify-telegram-channel-scraper 2>/dev/null`.

| Platform | User intent | Actor ID | Tier | Notes |
|----------|-------------|----------|------|-------|
| Telegram | Messages from channels the user names: latest N, a date window, keyword filter inside those channels, media URLs, view counts, forwards, free channel metadata | `george.the.developer/telegram-channel-scraper` | community | Pay per event. `message-scraped` $0.005 per message, no start fee. Caps: `maxMessages` per channel (default 100, 0 unlimited, up to 10,000 per channel per run), `dateFrom` / `dateTo`. Timeout 60 min. |
| Telegram | Posts containing a phrase across named channels plus channels discovered by web search | `george.the.developer/telegram-keyword-search` | community | Pay per event. `message-found` $0.004 per matching post, `apify-actor-start` $0.00005. Caps: `keywords` 1 to 20, `maxChannelsPerKeyword` default 10 max 50, `maxResultsPerKeyword` default 50 max 1,000, `dateFrom`. Timeout 30 min. |

## Choosing between the two

Channel known and the feed is wanted: channel scraper. Phrase known and the channels are not: keyword search. Both named channels and a phrase: either works; the channel scraper keeps media URLs and `textHtml`, the keyword search is cheaper per row and can add discovered channels.

## How to extend

1. Fetch a live input schema: `apify actors info "george.the.developer/telegram-keyword-search" --input --user-agent apify-awesome-skills/apify-telegram-channel-scraper 2>/dev/null`
2. Add a row above with the user intent that should trigger it.
