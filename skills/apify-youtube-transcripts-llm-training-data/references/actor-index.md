# Actor index: YouTube transcripts as LLM training data

The primary Actor for this skill, plus the Actors worth chaining when a corpus needs discovery or enrichment. The agent reads this after `SKILL.md` to pick the right Actor for a specific user intent.

| Platform | User intent | Actor ID | Tier | Notes |
|----------|-------------|----------|------|-------|
| YouTube | Bulk transcripts for a training or RAG corpus | `johnvc/YoutubeTranscripts` | community | Pay per video. Batch via `youtube_url` array; `non_timestamped` is the text column; `include_metadata` adds provenance (title, channel, upload date, views). |

## Chain with related Actors

| User intent | Actor ID | Notes |
|-------------|----------|-------|
| Discover video URLs by keyword before building the corpus | `johnvc/google-short-videos-api` | Keyword in, video URLs out; feed them into `youtube_url` here. |

## How to extend

1. Search candidates: `apify actors search "youtube transcript" --json --limit 20 2>/dev/null`
2. Fetch the input schema: `apify actors info "johnvc/YoutubeTranscripts" --input --json 2>/dev/null`
3. Add a row above with the user intent that should trigger it.

Note: `Tier` here is `community` because these are third-party Actors published by John Cole on the Apify Store, not Apify-maintained Actors.
