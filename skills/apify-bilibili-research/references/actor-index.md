# Actor routing table: Bilibili research

All Bilibili jobs route to one Actor, `crawlplant/bilibili-trending-history` (built by this skill's author, pay per event). Pick the mode by the job:

| Job | `mode` | Key inputs | Row type |
|-----|--------|-----------|----------|
| Trending now, in Bilibili's own order (up to 500) | `popular` | `maxItems`, `minViews`, `onlyNew` | `video` |
| Top 100 per category | `ranking` | `rankingCategories`: `all`, `animation`, `chinese-animation`, `music`, `dance`, `gaming`, `knowledge`, `tech`, `sports`, `cars`, `life`, `food`, `animals`, `kichiku`, `fashion`, `entertainment`, `film-tv` | `video` |
| Weekly must-watch issues (每周必看), March 2019 to now | `weekly` | `weeklyIssues`: `"latest"`, `"392"`, `"341-392"` | `video` |
| All-time must-watch list (入站必刷) | `mustWatch` | none | `video` |
| Top 50 hot searches (热搜) | `hotSearches` | none | `hotSearch` |
| Videos by keyword | `search` | `searchQueries`, `sortBy` (`relevance`, `views`, `newest`, `danmaku`, `favorites`), `durationFilter` (`any`, `under10`, `10to30`, `30to60`, `over60`), `searchCategory`, `publishedAfter` / `publishedBefore` (`"2026-09-01"` or `"7 days"`) | `video` |
| Creators by name or topic | `search` | `searchType: "creators"`, `searchQueries` | `creator` |
| Known videos: exact stats, tags, honours | `videos` | `videos` (BV ids, av numbers, URLs), `includeDetails` | `video` |
| Comments | `comments` | `videos`, `commentsSort` (`hot`, `newest`), `maxCommentsPerVideo` (1-5000), `includeReplies`, `maxRepliesPerComment` (1-20) | `comment` |
| Danmaku (bullet comments) | `danmaku` | `videos`, `maxDanmakuPerVideo` (1-10000, evenly sampled over the video) | `danmaku` |
| Creator profiles | `creators` | `creators` (ids or space.bilibili.com URLs), `creatorVideos` (0-50) | `creator` + `video` |
| Hour-by-hour history | `tracked` | optional `videos` / `creators`, `historyResolution` (`daily`, `hourly`) | `trackedVideo`, `trackedCreator` |

Options shared by the video modes: `includeDetails` (exact counts, tags, honours; one extra request per video), `minViews` (drop small videos before they are charged), `trackHistory` (default on: trend fields vs the previous run), `onlyNew` (only rows earlier runs of the same board or search did not return), `historyKey` (separate comparison history per task), `maxItems` (total rows, also the cost cap).

Subscriptions: `trackDays` (1-90) on a `videos` or `creators` run starts hourly server-side tracking, charged per item per day. Confirm with the user first.

## Store and MCP

- Store page: https://apify.com/crawlplant/bilibili-trending-history
- Hosted MCP server: `https://mcp.apify.com/?tools=actors,docs,crawlplant/bilibili-trending-history`
- MCP docs: https://docs.apify.com/platform/integrations/mcp

## Not covered

Video or audio files, logged-in data, live-stream chat. Other Chinese platforms (Weibo, Douyin, Xiaohongshu): unaffiliated Actors, found with `apify actors search` as shown in SKILL.md.
