# Cost guardrails and error recovery: Bilibili research

## Confirm live prices before a large run

Prices can change. Read them from the live Actor rather than trusting a copied number:

```bash
apify actors info "crawlplant/bilibili-trending-history" --json \
  --user-agent apify-awesome-skills/apify-bilibili-research \
  2>/dev/null
```

The pay-per-event events are under `pricingInfos` (take the newest entry): `video-row`, `video-detail-row`, `creator-row`, `comment-row`, `hot-search-row`, `danmaku-row`, `history-row`, `tracking-day`, `apify-actor-start`. Each row event has tiered prices per Apify plan (`FREE` is the highest).

## Cost model

- Each row is charged once at its row price; `apify-actor-start` is a fraction of a cent.
- `maxItems` caps the total rows of a run, so it caps the cost. Default 100.
- `minViews` and `onlyNew` drop rows before they are charged: a scheduled `onlyNew` monitor pays only for what is new.
- `includeDetails: true` switches video rows to the higher `video-detail-row` price and adds one request per video. Use it only when exact counts, coins, shares, tags or honours matter.
- Comments with `includeReplies` count replies toward `maxCommentsPerVideo`.
- `trackDays` is a commitment: `tracking-day` x items x days, charged up front when the run starts or extends tracking. Reading the history later costs one `history-row` per tracked item.

Rule of thumb: mention cost under about $5, warn over about $5, get explicit sign-off over about $20, and always before a `trackDays` subscription. Phrase it as "around $X".

## Guardrails

1. Start with `maxItems` 20-50 and check the rows before a wide run.
2. Several `searchQueries` share one `maxItems`; raise it if each keyword needs its own depth.
3. Hourly scheduling of a whole board (500 rows x 24 runs) adds up; prefer `onlyNew: true` for monitors, or read `boardHistory` / `hoursOnPopular`, which already come from hourly snapshots.
4. Deduplicate `bvid`s before `comments`, `danmaku` or `videos` runs.

## Error recovery

- Every run writes a summary to its key-value store record `OUTPUT`: rows saved, requests, warnings (a video not found, ids not understood) and the events charged. Read it when a run returns fewer rows than expected:

```bash
apify key-value-stores get-value <KEY_VALUE_STORE_ID> OUTPUT \
  --user-agent apify-awesome-skills/apify-bilibili-research \
  2>/dev/null
```

  The store id is `storage.defaultKeyValueStoreId` in the `actors call` output.
- "not found, not public or not shown in this region": the video is gone or region-limited. Do not retry the same id.
- A run never fails because one page or one video could not be read; it returns what it has. Zero rows with no warning usually means an empty input list for the chosen mode (for example `videos` empty in `comments` mode).
- Before retrying, check the original run's status. If the start response was lost, find the existing run first so an uncertain response does not start a second paid run (or a second subscription).
