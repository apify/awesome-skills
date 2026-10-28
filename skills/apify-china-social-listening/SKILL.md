---
name: apify-china-social-listening
description: China social listening and research across Weibo, Douban, WeChat Official Accounts, and Bilibili using Integration Yard Apify Store actors. Use when the user asks for Chinese social mentions, Douban ratings/reviews, WeChat articles, Bilibili creators/videos, brand monitoring in China, or 微博/豆瓣/微信/B站 data without building scrapers.
metadata:
  category: data-extraction
  keywords: china, weibo, douban, wechat, bilibili, social listening, brand monitoring, 微博, 豆瓣, 微信, B站
author: Integration Yard
author_url: https://apify.com/dheerajitbhu
---

# China social listening (Weibo · Douban · WeChat · Bilibili)

Pull public Chinese social and cultural signals for brand monitoring, audience research, and content decisions — without writing scrapers.

## Example prompts

- "Monitor Weibo mentions of our brand this week"
- "Export Douban ratings and short comments for these movies"
- "Find recent WeChat Official Account articles about EVs"
- "Get Bilibili creator stats and trending videos for 原神"
- "China social listening pack for competitor X"

Out of scope:

- Scraping X/Twitter, Instagram, TikTok global, or LinkedIn — use other Store actors / skills
- Anything that needs a logged-in WeChat/Weibo consumer session beyond what the public Actors already support
- Building new Actors — this skill only routes to published Store Actors

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Auth: `apify login`, or `APIFY_TOKEN`, or Console → Settings → Integrations

## Workflow

1. Clarify the goal: brand mentions, ratings/reviews, articles, video/creator stats, or a multi-platform pack.
2. Pick Actor(s) from the routing table. Prefer a published [example task](https://apify.com/dheerajitbhu) when one matches — presets are SEO-tested and ready to run.
3. Confirm spend caps (`maxChargeUsd`, row limits). Douban search/comments/reviews: first 20 rows free when that mode’s limit is ≤ 50.
4. Run via CLI, MCP, or Console; return dataset link + row count; offer CSV/Excel.

## Actor routing

| User need | Actor | Store | Best for |
|-----------|-------|-------|----------|
| Microblog posts, hot search, comments, profiles | `dheerajitbhu/weibo-scraper` | [weibo-scraper](https://apify.com/dheerajitbhu/weibo-scraper) | Brand mentions, 热搜, KOL profiles |
| Movie/book ratings, 短评, 影评/书评, charts | `dheerajitbhu/douban-scraper` | [douban-scraper](https://apify.com/dheerajitbhu/douban-scraper) | Audience scores, China film/book research |
| Official Account article search + full text | `dheerajitbhu/wechat-articles-scraper` | [wechat-articles-scraper](https://apify.com/dheerajitbhu/wechat-articles-scraper) | Brand PR, industry coverage |
| Video search, comments, trending, UP主 stats | `dheerajitbhu/bilibili-scraper` | [bilibili-scraper](https://apify.com/dheerajitbhu/bilibili-scraper) | Creator discovery, fandom trends |

All listed Actors are **community** tier (Integration Yard / dheerajitbhu).

## Multi-platform packs

- **Brand pulse:** Weibo brand-mentions + WeChat brand-monitoring (+ Bilibili search if the brand is entertainment/gaming).
- **Title launch:** Douban ratings/comments/reviews + Weibo search + Bilibili search for the same title string.
- **Creator vetting:** Bilibili creator-stats + Weibo user-profile for the same KOL.

## Calling Actors — Apify CLI

```bash
apify actors call "dheerajitbhu/weibo-scraper" -i '{"mode":"search","searchQueries":["小米"],"maxResults":50,"maxChargeUsd":1}' \
  --json \
  --user-agent apify-awesome-skills/apify-china-social-listening \
  2>/dev/null
```

```bash
apify actors call "dheerajitbhu/douban-scraper" -i '{"mode":"search","searchType":"movie","searchQueries":["流浪地球"],"fetchDetails":true,"maxResults":10,"maxChargeUsd":1}' \
  --json \
  --user-agent apify-awesome-skills/apify-china-social-listening \
  2>/dev/null
```

Always include `--json`, `--user-agent apify-awesome-skills/apify-china-social-listening`, and `2>/dev/null`.

## Troubleshooting

- Empty WeChat/Weibo results → try the Chinese keyword people actually publish; English brand names often under-index.
- Douban chart runs are billed from row 1 (free-first-20 is for search/comments/reviews with limit ≤ 50).
- Rate limits / blocks → re-run with smaller `maxResults`; check Actor run log for `incomplete` rows.
- See [references/gotchas.md](references/gotchas.md) and [references/actor-index.md](references/actor-index.md).
