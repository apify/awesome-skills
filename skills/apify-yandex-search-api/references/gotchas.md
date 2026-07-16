# Gotchas: Yandex search API (johnvc/Scrape-Yandex)

Cost guardrails, error recovery, and input quirks. The agent reads this on demand when building inputs or when a run fails.

## Cost guardrails

Pricing model: pay per event. At the time of writing: a one-time start fee of about $0.08 per run, plus about $0.10 per page of results processed on the free tier (volume discounts bring pages to $0.05), plus a negligible per-result fee. Confirm the live price on the Store card or with `apify actors info "johnvc/Scrape-Yandex" --json --user-agent apify-awesome-skills/apify-yandex-search-api 2>/dev/null` (look at `pricingInfo`).

Estimate before running: cost is about $0.08 + (`max_pages` times the per-page price). One page returns all requested result types together; the include flags do not change the price.

- Default 2-page run: about $0.28.
- 10-page deep read: about $1.08.
- 50 queries at 2 pages each: about $14; batch with care.

Suggested confirmation thresholds:

- Rough estimate over $5: warn the user.
- Rough estimate over $20: get explicit confirmation before running.
- Always present cost as "around $X", not a guarantee.

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| Empty dataset | Query has no results on that domain or region | Broaden the query; check it manually on the chosen `yandex_domain`. |
| Results in the wrong language | `lr` set without `lang` and domain | Set `yandex_domain`, `lang`, and `lr` together. |
| Fewer pages than `max_pages` | Yandex ran out of results | Expected; check `pagination_limit_reached` in run metadata. |
| Error rows with `error_type` | Transient fetch failure on one page | Re-run; other pages still return. |

## Actor-specific notes

- `text` is the only required input; organic results are on by default.
- Output shape: one dataset item per page per result type, tagged `item_type` (`organic`, `ads`, `knowledge_graph`, `inline_images`, `inline_videos`). The actual results are nested arrays on the item (`organic_results`, `ads_results`, and so on): flatten client-side for CSV or row-level work.
- Organic rows always carry `position`, `title`, `link`, `displayed_link`, `snippet`; `date`, `rich_snippet`, and `sitelinks` appear only when Yandex shows them.
- `lr` region IDs: 213 Moscow, 2 Saint Petersburg, 65 Novosibirsk; any of 123,000 plus location IDs work.
- `sort_mode` "date" plus `period` gives a fresh-results read; default is relevance.
- One skill per vertical: the dedicated Images and Videos verticals (`include_image_search`, `include_video_search`) are covered by the Yandex image search API skill and priced the same way.
- Rank tracking over time belongs to the pay-per-result edition (`johnvc/yandex-scrape-yandex-search-results-at-scale---per-result`), not this Actor.
