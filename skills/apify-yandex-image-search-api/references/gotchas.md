# Gotchas: Yandex image search API (johnvc/Scrape-Yandex, Images vertical)

Cost guardrails, error recovery, and input quirks. The agent reads this on demand when building inputs or when a run fails.

## Cost guardrails

Pricing model: pay per event. At the time of writing: a one-time start fee of about $0.08 per run, plus about $0.10 per page of results processed on the free tier (volume discounts bring pages to $0.05), plus a negligible per-result fee. Confirm the live price on the Store card or with `apify actors info "johnvc/Scrape-Yandex" --json --user-agent apify-awesome-skills/apify-yandex-image-search-api 2>/dev/null` (look at `pricingInfo`).

Estimate before running: cost is about $0.08 + (`max_pages` times the per-page price). The image filters do not change the price; they change how many rows a page yields.

- Default 2-page image run: about $0.28.
- 10 queries at 2 pages each: about $2.80.
- 100-query dataset build: about $28; get explicit confirmation first.

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

- The Images vertical shares the Actor and pricing with the web SERP skill; one run can return both if you leave `include_organic_results` true.
- `image_site` takes one hosting site (for example commons.wikimedia.org), useful for license-friendly sourcing.
- `image_recent` limits to recently indexed images; combine with `image_type` "photo" for news-adjacent work.
- The Actor returns listing data only; it does not download files and it does not check usage rights.
- Reverse lookups (find where an image appears) belong to `johnvc/yandex-reverse-image-search`, not this Actor.
