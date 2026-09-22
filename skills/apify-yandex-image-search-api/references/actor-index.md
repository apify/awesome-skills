# Actor index: Yandex image search API

The primary Actor for this skill, plus the Actors worth chaining for adjacent image and Yandex intents. The agent reads this after `SKILL.md` to pick the right Actor for a specific user intent.

| Platform | User intent | Actor ID | Tier | Notes |
|----------|-------------|----------|------|-------|
| Yandex Images | Search images by text, get full-size URLs with filters | `johnvc/Scrape-Yandex` | community | Set `include_image_search` true. Filters: type, color, orientation, file type, exact size, site, recency. Rows tagged `item_type` "image_search". Pay per run start plus per page. |

## Chain with adjacent Actors

| User intent | Actor ID | Notes |
|-------------|----------|-------|
| Find where a known image appears on the web | `johnvc/yandex-reverse-image-search` | Reverse lookup by image URL. |
| Google Images equivalent | `johnvc/google-images-api` | Same job on Google's index. |
| Full Yandex web SERP | `johnvc/Scrape-Yandex` | Same Actor, organic mode; see the Yandex search API skill. |
| Track keyword ranks on Yandex | `johnvc/yandex-scrape-yandex-search-results-at-scale---per-result` | Per-result billing; the rank-tracking edition. |

## How to extend

1. Search candidates: `apify actors search "yandex images" --json --limit 20 2>/dev/null`
2. Fetch the input schema: `apify actors info "johnvc/Scrape-Yandex" --input --json 2>/dev/null`
3. Add a row above with the user intent that should trigger it.

Note: `Tier` here is `community` because these are third-party Actors published by John Cole on the Apify Store, not Apify-maintained Actors.
