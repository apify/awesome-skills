# Actor index: YouTube transcript API

The primary Actor for this skill, plus the Actors worth chaining when a task needs more than transcripts. The agent reads this after `SKILL.md` to pick the right Actor for a specific user intent.

| Platform | User intent | Actor ID | Tier | Notes |
|----------|-------------|----------|------|-------|
| YouTube | Get the transcript of one or many videos as JSON, SRT, VTT, or text | `johnvc/YoutubeTranscripts` | community | Pay per video. Inputs: `youtube_url` (string or array), `languages`, `translate_to`, `transcript_type`, `output_formats`, `list_only`, `include_metadata`. One flat row per video with transcript plus title, channel, views. |

## Chain with related Actors

| User intent | Actor ID | Notes |
|-------------|----------|-------|
| Find Shorts or short-form videos by keyword, then transcribe them | `johnvc/google-short-videos-api` | Feed its video URLs into `youtube_url` here. |

## How to extend

1. Search candidates: `apify actors search "youtube transcript" --json --limit 20 2>/dev/null`
2. Fetch the input schema: `apify actors info "johnvc/YoutubeTranscripts" --input --json 2>/dev/null`
3. Add a row above with the user intent that should trigger it.

Note: `Tier` here is `community` because these are third-party Actors published by John Cole on the Apify Store, not Apify-maintained Actors.
