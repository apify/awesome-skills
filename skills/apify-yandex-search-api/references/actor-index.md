# Actor index: Yandex search API

The primary Actor for this skill, plus the Actors worth chaining for adjacent Yandex and international-SERP intents. The agent reads this after `SKILL.md` to pick the right Actor for a specific user intent.

| Platform | User intent | Actor ID | Tier | Notes |
|----------|-------------|----------|------|-------|
| Yandex | Full SERP (organic, ads, knowledge graph, inline media) as JSON | `johnvc/Scrape-Yandex` | community | Pay per run start plus per page. Inputs: `text` (required), `yandex_domain`, `lang`, `lr` region, include flags per result type, `max_pages`. Items tagged `item_type`. |

## Chain with adjacent Actors

| User intent | Actor ID | Notes |
|-------------|----------|-------|
| Track keyword ranks on Yandex over time | `johnvc/yandex-scrape-yandex-search-results-at-scale---per-result` | Per-result billing; the rank-tracking edition. |
| Find where an image appears on the web | `johnvc/yandex-reverse-image-search` | Reverse image lookups. |
| Chinese SERP data | `johnvc/Baidu-Search-Scraper` | Baidu equivalent of this skill. |
| Korean SERP data | `johnvc/naver-search-api` | Web, news, image, video, shopping verticals. |

## How to extend

1. Search candidates: `apify actors search "yandex search" --json --limit 20 2>/dev/null`
2. Fetch the input schema: `apify actors info "johnvc/Scrape-Yandex" --input --json 2>/dev/null`
3. Add a row above with the user intent that should trigger it.

Note: `Tier` here is `community` because these are third-party Actors published by John Cole on the Apify Store, not Apify-maintained Actors.
