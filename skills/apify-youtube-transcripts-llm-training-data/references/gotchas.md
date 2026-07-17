# Gotchas: YouTube transcripts as LLM training data (johnvc/YoutubeTranscripts)

Cost guardrails, error recovery, and corpus-quality notes. The agent reads this on demand when building inputs or when a run fails.

## Cost guardrails

Pricing model: pay per event. One charge per video successfully transcribed, about $0.00001 per video at the time of writing (about a penny per 1,000 videos), plus small platform fees per run start and per dataset item. Confirm the live price on the Store card or with `apify actors info "johnvc/YoutubeTranscripts" --json 2>/dev/null` (look at `pricingInfo`).

Corpus math:

- 1,000 videos: around two cents all-in. 10,000 videos: around twenty cents.
- Failed videos (no captions, invalid URL) are not charged the per-video fee, so a noisy URL list does not inflate cost.
- A `list_only` dry run over a URL sample is free of the per-video charge and shows caption availability before you commit.

Cost is never the constraint at realistic corpus sizes; wall-clock time is. Confirm with the user only for runs over roughly 50,000 URLs, and split those into parallel batches anyway.

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| Many error rows from one channel | That channel disables captions | Expected. Drop the rows; spot-check with `"list_only": true`. |
| Error row with `error_type` IpBlocked or RequestBlocked | Transient fetch block | The Actor retries with fresh sessions; rerun just the failed URLs. |
| Rows in unexpected languages | Preferred track missing; the Actor fell back to what exists | Group by `language_code`; re-run outliers with `translate_to`, or drop them. |
| `translated_to` missing on a translated run | Target code not supported for that video | Only about 18 codes are auto-translatable. Exclude those rows or choose a supported target. |
| Run TIMED-OUT | Batch too large for the run timeout | Split into batches of about 500 URLs or raise the run timeout. |

## Corpus-quality notes

- `source_type` is the main quality signal: Manual captions are human-written; Auto-generated ones carry recognition errors. `transcript_type: "manual"` filters at fetch time; filtering the output on `source_type` preserves coverage stats.
- Dedupe by `video_id`, not URL; the same video arrives under watch, short-link, and Shorts URL forms.
- `non_timestamped` is one continuous string per video with no speaker labels or paragraph breaks; sentence-split downstream if the training format needs segments.
- Keep `title`, `channel_name`, `upload_date`, `url`, and `language_code` as metadata columns; a dataset card needs them and they cost nothing extra.
- Licensing judgment stays with the dataset builder: transcripts inherit the copyright status of the source videos.
