# Gotchas — apify-video-content-intelligence

## Cost guardrails

All four Actors are `PAY_PER_EVENT`. Check current prices with:

    apify actors info "tubetext/video-breakdown-ai" --json \
      --user-agent apify-awesome-skills/apify-video-content-intelligence 2>/dev/null

(look at `pricingInfo`).

Quick estimates (FREE tier):

| Job | Rough cost |
|---|---|
| 100 YouTube transcripts with captions | ~$0.40 |
| 100 YouTube videos without captions, 10 min each, `aiFallback: true` | ~$6.40 |
| 100 TikTok transcripts | ~$0.30 |
| 20 channels with Social Blade stats | ~$0.18 |
| 50 short TikToks broken down | ~$1.50 |
| A YouTube channel with `maxVideosPerSource: 200` in video-breakdown-ai, 10-min videos | ~$20 (confirm first) |

Suggested thresholds: warn above $5, and require explicit confirmation above $20.

## Common errors

| Error / status | Cause | Fix |
|-------|-------|-----|
| `no_transcript` (YouTube) | No captions available | Set `aiFallback: true` |
| `skipped` (TikTok, music only) | Clip uses a song with no speech | Expected. Set `transcribeMusic: true` only if lyrics are wanted |
| `skipped` (profile URL) | Profiles aren't supported | Pass video URLs |
| `video_unavailable` | Deleted, private or region-locked | Not charged; drop it |
| `youtube_blocking_now` (video-breakdown-ai) | YouTube bot checks across the run | Not charged; retry later. From 2026-10-22 `proxyMode: "residential"` is available (billed per MB) |
| Very slow Instagram Reels | Reels download is slower (beta) | Expect up to ~5 min per reel |
