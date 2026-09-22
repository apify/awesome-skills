# Gotchas: Yandex image search API (johnvc/Scrape-Yandex, Images vertical)

Cost guardrails, error recovery, and input quirks. The agent reads this on demand when building inputs or when a run fails.

## Cost guardrails

Pricing model: pay per event. Fetch current `pricingInfos` with `apify actors info "johnvc/Scrape-Yandex" --json --user-agent apify-awesome-skills/apify-yandex-image-search-api 2>/dev/null`. Use the latest entry whose `startedAt` is not in the future and the authenticated account’s discount tier.

Estimate the one-time `setup` event, `page_processed` events, and `apify-default-dataset-item` for each stored dataset row. Use `eventPriceUsd` for flat rates or `eventTieredPricingUsd` for the account’s tier; nested results are not dataset rows. Use a positive `max_pages` to bound the run; zero means no limit.

Suggested confirmation thresholds:

- Rough estimate over $5: warn the user.
- Rough estimate over $20: get explicit confirmation before running.
- Always present cost as "around $X", not a guarantee.

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| No image rows in the dataset | `include_image_search` not set, or nested array not read | Set the flag true; filter items on `item_type` = "image_search" and read the `image_results` array (about 30 rows per page item). |
| Very few rows | Over-constrained filters | Relax exact `image_width`/`image_height` first, then color and site. |
| Dead image URLs later | Hotlinked third-party files rot | Persist needed files at collection time, where licensing allows. |
| Wrong-market images | Domain, language, region not aligned | Set `yandex_domain`, `lang`, and `lr` together. |

## Actor-specific notes

- `original` is the image URL returned by the Actor; it may point to a resized image rather than the full-size source.

- The Images vertical shares the Actor and pricing with the web SERP skill; one run can return both if you leave `include_organic_results` true.
- `image_site` takes one hosting site (for example commons.wikimedia.org), useful for license-friendly sourcing.
- `image_recent` limits to recently indexed images; combine with `image_type` "photo" for news-adjacent work.
- The Actor returns listing data only; it does not download files and it does not check usage rights.
- Reverse lookups (find where an image appears) belong to `johnvc/yandex-reverse-image-search`, not this Actor.
