# Gotchas: YouTube transcript API (johnvc/YoutubeTranscripts)

Cost guardrails, error recovery, and input quirks. The agent reads this on demand when building inputs or when a run fails.

## Cost guardrails

Pricing model: pay per event. One charge per video successfully transcribed, about $0.00001 per video at the time of writing (about a penny per 1,000 videos), plus small platform fees per run start and per dataset item. Confirm the live price on the Store card or with `apify actors info "johnvc/YoutubeTranscripts" --json 2>/dev/null` (look at `pricingInfo`).

Estimate before running:

- Cost is roughly (number of URLs) times the per-video price, plus one dataset-item fee per row. Example: 1,000 videos is around two cents all-in.
- Failed videos (no captions, invalid URL, blocked fetch) are not charged the per-video fee.
- `list_only` discovery runs skip the per-video charge entirely.

Suggested confirmation thresholds: cost is negligible at any realistic batch size, so confirm with the user only when the run is over roughly 50,000 URLs (wall-clock time, not cost, becomes the constraint). Always present cost as "around $X", not a guarantee.

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| Error row with `error_type` IpBlocked or RequestBlocked | A transient block on the fetch session | The Actor already retries with fresh sessions; rerun the failed URLs. Only successes are charged. |
| Error row, message says transcripts are disabled | The video has no caption track | Expected. Skip the row; the rest of the batch still returns. |
| Error row with `error_type` ValueError | The URL is not a valid YouTube video URL | Check the URL; watch, Shorts, youtu.be, embed, and mobile formats are accepted. |
| `translated_to` missing after requesting translation | The target code is not supported for that video | Run `"list_only": true` and pick a code from `translation_languages`. |
| Run TIMED-OUT on a large batch | Batch too big for the run timeout | Split the array or raise the timeout in run options. |

## Actor-specific notes

- `youtube_url` accepts a single string or an array; batches process several videos in parallel.
- `languages` is an ordered preference list; the first available track wins. If none of the preferred codes exist, the Actor falls back to what the video has.
- Translation via `translate_to` covers only the codes YouTube exposes for auto-translation (roughly 18). Gate on the `translated_to` output field, never assume.
- `include_metadata` defaults to true and adds title, channel, views, upload date, thumbnail, tags per row; it costs nothing extra but adds a second or two per video. Set false for speed.
- `source_type` distinguishes Manual captions from Auto-generated; filter with `transcript_type` when only human captions will do.
- Output is flat, one row per video, so it loads straight into a sheet, a database, or an LLM pipeline.
