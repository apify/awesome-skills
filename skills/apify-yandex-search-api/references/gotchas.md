# Gotchas: Yandex search API (johnvc/Scrape-Yandex)

Cost guardrails, error recovery, and input quirks. The agent reads this on demand when building inputs or when a run fails.

## Cost guardrails

Pricing model: pay per event. Fetch current `pricingInfos` with `apify actors info "johnvc/Scrape-Yandex" --json --user-agent apify-awesome-skills/apify-yandex-search-api 2>/dev/null`. Use the latest entry whose `startedAt` is not in the future and the authenticated account’s discount tier.

Estimate the one-time `setup` event, `page_processed` events, and `apify-default-dataset-item` for each stored dataset row. Use `eventPriceUsd` for flat rates or `eventTieredPricingUsd` for the account’s tier; nested results are not dataset rows. Use a positive `max_pages` to bound the run; zero means no limit.

Suggested confirmation thresholds:

- Rough estimate over $5: warn the user.
- Rough estimate over $20: get explicit confirmation before running.
- Always present cost as "around $X", not a guarantee.

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| Empty dataset | Query has no results on that domain or region | Broaden the query; check it manually on the chosen `yandex_domain`. |
| Results in the wrong language | `lr` set without `lang` and domain | Set `yandex_domain`, `lang`, and `lr` together. |
| Fewer pages than `max_pages` | Results may be exhausted or a fetch may have failed | Inspect returned items and run errors; `pagination_limit_reached` true means the configured limit was reached. |
| Error rows with `error` or `error_type` | No results or a fetch failure | Read `error_message` before filtering by result type; adjust the query, or retry if the failure is transient. |

## Actor-specific notes

- `organic_results` may contain advertising redirects; `displayed_link` may be empty.
- `text` is the only required input; organic results are on by default.
- Output shape: one dataset item per page per result type, tagged `item_type` (`organic`, `ads`, `knowledge_graph`, `inline_images`, `inline_videos`). The actual results are nested arrays on the item (`organic_results`, `ads_results`, and so on): flatten client-side for CSV or row-level work.
- Organic rows always carry `position`, `title`, `link`, `displayed_link`, `snippet`; `date`, `rich_snippet`, and `sitelinks` appear only when Yandex shows them.
- `lr` region IDs: 213 Moscow, 2 Saint Petersburg, 65 Novosibirsk; any of 123,000 plus location IDs work.
- `sort_mode` "date" plus `period` gives a fresh-results read; default is relevance.
- Dedicated video search (`include_video_search`) can return `video_results` with empty `title`, `link`, and `duration`. Do not present such rows as usable video results; request an Actor fix. Inline videos use a different output path (`inline_videos`); `video_duration` and `video_hd` apply only to the dedicated vertical. The Yandex image search API skill covers `include_image_search`.
- Rank tracking over time belongs to the pay-per-result edition (`johnvc/yandex-scrape-yandex-search-results-at-scale---per-result`), not this Actor.
