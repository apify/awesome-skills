# Gotchas — cost guardrails and error recovery

Read `SKILL.md` first. This file is the short list of things that cost money, waste a run, or make a
working run look broken.

## Cost

- **Two ceilings, always.** The Actor's own cap (`maxItems` / `maxVideos` / `maxReelsPerHandle` /
  `maxTotalMinutes`) *and* `maxTotalChargeUsd` on the API call. `apify actors call` has no cost-cap
  flag — the dollar ceiling exists only as a query parameter of
  [`POST /v2/acts/{actorId}/runs`](https://docs.apify.com/api/v2/act-runs-post).
- **`steadyfetch/media-transcriber` defaults to unlimited minutes** (`maxTotalMinutes: 0`,
  `maxMinutesPerItem: 0`) and is priced per audio minute. Set both before running anything long; a
  60-minute podcast is 60 charged minutes.
- **Speech-to-text is the variable cost on YouTube.** $0.008 per started minute, charged only when a
  video has no usable captions. `maxSpeechMinutes` (default 60) is the cap; `enableSpeechFallback:
  false` removes the cost entirely at the price of returning nothing for uncaptioned videos.
- **A bare run with no input is not a free preview.** Each Actor's default input runs a small live
  sample and is charged like any other run.
- **Estimating a channel:** delivered transcripts × the per-transcript price, plus $0.008 × the
  minutes of whatever is uncaptioned. Warn above $5, confirm above $20, and call it an estimate.

## Reading the dataset

- **Never `select(.charged == true)`.** These Actors remember what they have already delivered to
  your account. A repeat comes back `repeat: true`, `charged: false`, `firstSeenRunId` set — and
  carrying the **full text**, free. On a re-run or a scheduled watch, most rows are repeats, so that
  filter makes a working run look empty. `charged` is for cost accounting only.
- **The text field has two names.** `text` on `steadyfetch/youtube-transcript-scraper`,
  `steadyfetch/youtube-channel-transcripts` and `steadyfetch/media-transcriber`; `transcript` on
  `steadyfetch/instagram-reel-transcript-scraper`. `(.text // .transcript)` covers both.
- **The delivered status has two names too:** `ok` on the three, `transcribed` on the reel Actor
  (plus `onscreen_text_extracted` when on-screen text was read from a silent reel).
- **The reel Actor appends an uncharged receipt row** marked `_summary: true`, `status:
  "run_summary"` — `attempted`, `delivered`, `unchargedMisses`, `chargedRows`, `chargedEvents`,
  `stoppedBy`. Drop it with `select(._summary != true)` before counting rows, or it inflates every
  count by one.
- **`srt` and `vtt` are `null` unless you asked for them.** `format` (YouTube) defaults to `json`;
  `outputFormats` (media) defaults to `["text"]`. Asking afterwards costs a second transcript.

## Routing

- **YouTube links belong to the YouTube Actors.** `steadyfetch/media-transcriber` answers a YouTube
  page with an uncharged `unsupported_site` row pointing at
  `steadyfetch/youtube-transcript-scraper`. The same is true for Instagram, TikTok, Facebook and
  LinkedIn links.
- **A Spotify or Apple Podcasts *show* page is not an episode page.** Give the episode.
- **Paid ad creative is a different skill.** Ads from the Meta, TikTok or LinkedIn ad libraries or the
  Google Ads Transparency Center go to `apify-ad-creative-transcripts`.

## Recovery

| Symptom | Cause | Fix |
|---|---|---|
| Every row `blocked_retry` | YouTube throttled this run | Re-run; `retryable: true`, nothing charged |
| Every row `no_captions` | `enableSpeechFallback` was off | Re-run with it on |
| Every row `no_speech` | The videos really are music or silence | Nothing to recover; on reels try `includeOnScreenText: true` |
| `channel_region_blocked` | The channel is not served to the locations this run used (it tries three) | Re-run — a later run may leave from an allowed one |
| `live_no_transcript_yet` | The stream has not ended | Re-run after it ends |
| Instagram rows `unavailable_expired` | A signed media URL went stale in a chained dataset | Re-run from the handle or the reel link instead |
| Instagram handle returns nothing, slowly | Instagram walled the post feed; the Actor retries patiently and falls back to the profile page | Let it finish, or raise `maxRunSeconds`; rows from the fallback carry the caption but no `plays`/`likes` |
| Run hits its time limit | Too many items for the window | Raise `--timeout` / `maxRunSeconds`, or split the input |
| `Actor not found` | Wrong id | All four are `steadyfetch/<name>` |
