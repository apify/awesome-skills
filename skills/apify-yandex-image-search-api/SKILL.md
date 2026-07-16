---
name: apify-yandex-image-search-api
description: Search the Yandex Images vertical and get full-size image URLs as structured JSON with the Apify Yandex Search Scraper Actor (johnvc/Scrape-Yandex). A yandex image search api for agents and pipelines. One text query returns image results with the original full-size image URL, hosting page link, thumbnail, and source, filtered by image type, color, orientation, file type, exact size, site, and recency. Use when the user wants a yandex image search api or yandex images api, wants to search Yandex Images programmatically, collect image datasets with full-size URLs, source images from Russian-language sites, or filter image results by color, size, or license-friendly site. Pay-per-page billing, MCP-ready for Claude and other AI agents.
author: John Cole
author_url: https://github.com/johnisanerd
license: MIT
metadata:
  version: "1.0"
---

# Yandex Image Search API: Full-Size Image URLs as JSON

A Yandex image search API built on the Yandex Images vertical. One text query returns structured image results: the original full-size image URL, the page hosting it, a thumbnail, and the source, with filters for type, color, orientation, file type, exact dimensions, site, and recency.

## When to use this skill

- The user wants a "Yandex image search API" or "Yandex images API".
- They want to search Yandex Images programmatically and get full-size image URLs rather than thumbnails.
- They are collecting an image dataset (by topic, color, orientation, or exact size) for research, ML, or content work.
- They want images hosted on a specific site, or only recent images.

Not for: finding where a known image appears on the web (use the Yandex Reverse Image Search Actor), Google Images (use the Google Images API Actor), or plain web results (use the Yandex search API skill).

## What you get (one dataset item per page, tagged `item_type` "image_search")

Each dataset item is one page of the Images vertical, tagged `item_type` "image_search", holding an `image_results` array of about 30 rows per page. Per image row: `original` (the full-size image URL), `link` (the hosting page), `thumbnail`, `title`, `source`, `size`, `snippet`, `position`. Each item also carries page metadata (`total_results_found`, `page_number`, `pages_processed`).

## Prerequisites

- Apify account (sign up at https://apify.com?fpr=9n7kx3&fp_sid=awesomeskills).
- Authentication via `apify login`, or an `APIFY_TOKEN` environment variable (Apify Console, Settings, Integrations).

## The Actor

- Store page: https://apify.com/johnvc/Scrape-Yandex?fpr=9n7kx3&fp_sid=awesomeskills
- Actor ID: `johnvc/Scrape-Yandex`
- Pricing: a small per-run start fee plus a per-page fee (see `references/gotchas.md`).

## Run it with the Apify CLI

Basic image search, two pages:

```bash
apify actors call "johnvc/Scrape-Yandex" -i '{"text":"aurora borealis","include_image_search":true,"include_organic_results":false,"max_pages":2}' \
  --json \
  --user-agent apify-awesome-skills/apify-yandex-image-search-api \
  2>/dev/null
```

Filtered: recent, large, horizontal photos from one site:

```bash
apify actors call "johnvc/Scrape-Yandex" -i '{"text":"moscow skyline","include_image_search":true,"include_organic_results":false,"image_type":"photo","image_orientation":"horizontal","image_recent":true,"image_site":"commons.wikimedia.org","max_pages":2}' \
  --json \
  --user-agent apify-awesome-skills/apify-yandex-image-search-api \
  2>/dev/null
```

Every call carries the three flags this repo expects: `--json`, `--user-agent apify-awesome-skills/apify-yandex-image-search-api`, and `2>/dev/null`.

## Run it from Claude or another AI agent (MCP)

The Actor is MCP-ready. Add the hosted server URL:

`https://mcp.apify.com/?tools=actors,docs,johnvc/Scrape-Yandex`

Then ask, for example: "Search Yandex Images for red vintage bicycles, photos only, and give me the full-size URLs with their hosting pages." MCP setup docs: https://docs.apify.com/platform/integrations/mcp

## Workflow

1. Build the query. `text` is required. Set `include_image_search` true; turn `include_organic_results` false unless you also want the web SERP in the same run.
2. Apply filters. `image_type` (photo, clipart, and so on), `image_color`, `image_orientation`, `image_file_type`, exact `image_width` and `image_height`, `image_site` (one hosting site), `image_recent` (fresh images only).
3. Bound the volume. `max_pages` (default 2) is the cost driver.
4. Estimate cost, then confirm with the user if the run is large. See `references/gotchas.md`.
5. Run the Actor, filter the dataset to `item_type` = "image_search", and read each item's `image_results` array (`original` is the full-size URL, `link` the hosting page). Download files yourself only where the hosting page's license allows it.

## Inputs

- `text` (string, required): the image search query
- `include_image_search` (boolean): turn the Images vertical on
- `image_type` (enum, 6), `image_color` (enum, 12), `image_orientation` (enum, 4), `image_file_type` (enum, 4)
- `image_width` / `image_height` (integers, exact size), `image_site` (string), `image_recent` (boolean)
- `yandex_domain`, `lang`, `lr` (market targeting), `max_pages` (default 2)

## Cost

Billing is a small one-time start fee per run plus a per-page fee, so cost is roughly proportional to `max_pages`. A default two-page image run costs well under a dollar; live prices and thresholds are in `references/gotchas.md`.

## Honest limits

- Result URLs point at third-party image files; hotlinks can rot, so persist what you need (where licensing allows) rather than relying on the URLs long-term.
- Licensing is your responsibility: the Actor returns what Yandex Images lists; it does not check usage rights.
- Filter combinations can be sparse; strict size plus color plus site filters may return few or no rows.

## Troubleshooting

- No image rows: confirm `include_image_search` is true, filter items on `item_type` = "image_search", and read the nested `image_results` array (results are not flat rows).
- Too few results: relax filters one at a time, starting with exact `image_width`/`image_height`.
- Wrong-market images: set `yandex_domain`, `lang`, and `lr` together.

See `references/gotchas.md` for cost guardrails and error recovery, and `references/actor-index.md` for the Actor routing table.

## Related image and Yandex Actors

- Yandex Reverse Image Search API: https://apify.com/johnvc/yandex-reverse-image-search?fpr=9n7kx3&fp_sid=awesomeskills
- Google Images API: https://apify.com/johnvc/google-images-api?fpr=9n7kx3&fp_sid=awesomeskills
- Yandex Search, pay per result edition (rank tracking): https://apify.com/johnvc/yandex-scrape-yandex-search-results-at-scale---per-result?fpr=9n7kx3&fp_sid=awesomeskills
