---
name: apify-yandex-search-api
description: Get structured Yandex search results without an official API key using the Apify Yandex Search Scraper Actor (johnvc/Scrape-Yandex). One query returns the full SERP as JSON, with organic results (position, title, link, displayed_link, snippet), and optional ads, knowledge graph, inline images, and inline videos, targeted by Yandex domain, language, and any of 123,000 plus lr region IDs. Use when the user wants a yandex search api, a yandex serp api, Yandex search results as JSON or CSV, to scrape Yandex search, to check what ranks on yandex.ru for a query or region, or SEO research for Russian-speaking markets. Pay-per-page billing, MCP-ready for Claude and other AI agents.
author: John Cole
author_url: https://github.com/johnisanerd
license: MIT
metadata:
  version: "1.0"
---

# Yandex Search API: Full SERP Results as JSON

A Yandex search API without an official API key. One query returns the full Yandex SERP as structured JSON: organic results with positions and sitelinks, plus ads, knowledge graph, and inline media when you ask for them, targeted to any Yandex domain, language, and region.

## When to use this skill

- The user wants a "Yandex search API" or "Yandex SERP API" without registering for an official key.
- They want Yandex search results as JSON or CSV for a query, market, or region.
- They want to see what ranks on yandex.ru for a query, by city or region.
- They are doing SEO or competitor research for Russian-speaking markets.

Not for: keyword rank tracking over time (use the pay-per-result Yandex edition), reverse image lookups (use the Yandex Reverse Image Search Actor), or Google SERPs.

## What you get (one dataset item per page, tagged by `item_type`)

Each dataset item is one page of one result type, tagged with `item_type` (`organic`, `ads`, `knowledge_graph`, `inline_images`, `inline_videos`). The results sit in a nested array on that item: `organic_results` holds rows with `position`, `title`, `link`, `displayed_link`, `snippet` (plus `date`, `rich_snippet`, and `sitelinks` when Yandex shows them); the optional types use `ads_results`, `knowledge_graph`, `inline_images`, and `inline_videos` arrays. Every item also carries page metadata: `total_results_found`, `page_number`, `pages_processed`, `pagination_limit_reached`.

## Prerequisites

- Apify account (sign up at https://apify.com?fpr=9n7kx3&fp_sid=awesomeskills).
- Authentication via `apify login`, or an `APIFY_TOKEN` environment variable (Apify Console, Settings, Integrations).

## The Actor

- Store page: https://apify.com/johnvc/Scrape-Yandex?fpr=9n7kx3&fp_sid=awesomeskills
- Actor ID: `johnvc/Scrape-Yandex`
- Pricing: a small per-run start fee plus a per-page fee (see `references/gotchas.md`).

## Run it with the Apify CLI

Organic results for a query on yandex.com:

```bash
apify actors call "johnvc/Scrape-Yandex" -i '{"text":"crm software","max_pages":2}' \
  --json \
  --user-agent apify-awesome-skills/apify-yandex-search-api \
  2>/dev/null
```

Full Russian SERP for Moscow (lr 213), organic plus ads plus knowledge graph:

```bash
apify actors call "johnvc/Scrape-Yandex" -i '{"text":"купить ноутбук","yandex_domain":"yandex.ru","lang":"ru","lr":213,"include_ads":true,"include_knowledge_graph":true,"max_pages":2}' \
  --json \
  --user-agent apify-awesome-skills/apify-yandex-search-api \
  2>/dev/null
```

Every call carries the three flags this repo expects: `--json`, `--user-agent apify-awesome-skills/apify-yandex-search-api`, and `2>/dev/null`.

## Run it from Claude or another AI agent (MCP)

The Actor is MCP-ready. Add the hosted server URL:

`https://mcp.apify.com/?tools=actors,docs,johnvc/Scrape-Yandex`

Then ask, for example: "Get the first two pages of Yandex results for 'hotel booking' on yandex.ru and list the organic links with positions." MCP setup docs: https://docs.apify.com/platform/integrations/mcp

## Workflow

1. Build the query. `text` is the only required field. Pick `yandex_domain` (six domains), `lang` (19 languages), and `lr` (region ID, for example 213 for Moscow, 2 for Saint Petersburg) for the market you care about.
2. Choose result types. Organic is on by default; flip `include_ads`, `include_knowledge_graph`, `include_inline_images`, or `include_inline_videos` as needed. Each page of each type comes back as its own dataset item tagged with `item_type`.
3. Bound the volume. `max_pages` (default 2) is the cost driver; `sort_mode` "date" and `period` narrow to recent results.
4. Estimate cost, then confirm with the user if the run is large. See `references/gotchas.md`.
5. Run the Actor and read the dataset. Filter items by `item_type`, then read the nested array on each item (`organic_results` for the web SERP). Flatten the arrays client-side if the user wants CSV.

## Inputs

- `text` (string, required): the search query
- `yandex_domain` (enum, 6 domains, default `yandex.com`)
- `lang` (enum, 19) and `lr` (integer region ID, 123,000 plus locations)
- `include_organic_results` (default true), `include_ads`, `include_knowledge_graph`, `include_inline_images`, `include_inline_videos` (booleans)
- `max_pages` (integer, default 2) and `groups_on_page` (default 10)
- `sort_mode` (`relevance` or `date`), `period`, `family_mode`, `fix_typo`

The dedicated Images and Videos verticals (`include_image_search`, `include_video_search`) have their own skill: see the Yandex image search API skill.

## Cost

Billing is a small one-time start fee per run plus a per-page fee, so cost is roughly proportional to `max_pages`. A default two-page run costs well under a dollar; live prices and thresholds are in `references/gotchas.md`.

## Honest limits

- Positions reflect the SERP at crawl time for the chosen `lr` region; they vary by region and personalization-free crawling can still fluctuate run to run.
- This skill reads the SERP; it does not track ranks over time (that is the pay-per-result edition's job).
- Knowledge graph, ads, and inline media appear only when Yandex shows them for that query.

## Troubleshooting

- Empty organic results: check the query on the chosen domain manually; try `fix_typo` true and a broader query.
- Wrong-market results: set `yandex_domain`, `lang`, and `lr` together; `lr` alone does not switch language.
- Fewer pages than `max_pages`: Yandex ran out of results; `pagination_limit_reached` shows in run metadata.

See `references/gotchas.md` for cost guardrails and error recovery, and `references/actor-index.md` for the Actor routing table.

## Related Yandex and international SERP Actors

- Yandex Search, pay per result edition (rank tracking): https://apify.com/johnvc/yandex-scrape-yandex-search-results-at-scale---per-result?fpr=9n7kx3&fp_sid=awesomeskills
- Yandex Reverse Image Search API: https://apify.com/johnvc/yandex-reverse-image-search?fpr=9n7kx3&fp_sid=awesomeskills
- Baidu Search Scraper: https://apify.com/johnvc/Baidu-Search-Scraper?fpr=9n7kx3&fp_sid=awesomeskills
- Naver Search API (Korea): https://apify.com/johnvc/naver-search-api?fpr=9n7kx3&fp_sid=awesomeskills
