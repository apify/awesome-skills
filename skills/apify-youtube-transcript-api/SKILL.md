---
name: apify-youtube-transcript-api
description: Get YouTube transcripts as structured JSON with a hosted YouTube transcript API (the Apify Actor johnvc/YoutubeTranscripts). Pass one video URL or a batch array and get back non_timestamped text, timestamped snippets, language metadata, and optional SRT, VTT, and plain text formats, plus video title, channel, and view count. Works with standard videos and Shorts, handles language preference and translation, and runs from cloud IPs without IpBlocked errors. Use when the user wants a youtube transcript api, needs to get or download a YouTube transcript or subtitles, asks to extract the transcript from a YouTube video, or wants captions as JSON, SRT, or VTT. Pay-per-video billing, MCP-ready for Claude and other AI agents.
author: John Cole
author_url: https://github.com/johnisanerd
license: MIT
metadata:
  version: "1.0"
---

# YouTube Transcript API: Captions to Structured JSON

Fetch the transcript of any YouTube video as clean JSON with a hosted YouTube transcript API. Pass a single URL or a batch array; each video comes back as one row with the full plain text, timestamped snippets, language details, and the video's title, channel, and view count.

## When to use this skill

- The user wants a YouTube transcript API, or asks to get, fetch, or download the transcript of a YouTube video.
- They want subtitles or captions as JSON, SRT, VTT, or plain text.
- They ask to extract the transcript from a YouTube video, a Short, or a list of URLs.
- Their own transcript library keeps failing with IpBlocked or RequestBlocked from a cloud or datacenter IP.

Not for: videos with no caption track at all (those return an error row, not a transcript), private or age-gated videos, or generating captions with speech-to-text (this API reads YouTube's published caption tracks; it does not run ASR).

## What you get (one row per video)

`non_timestamped` (full transcript text), `timestamped` (snippets with `text`, `start`, `duration`), `language`, `language_code`, `source_type` (Manual or Auto-generated), `is_translatable`, `translation_languages`, `total_seconds`, `duration_human`, `snippet_count`, `video_id`, `url`, `success`. With metadata on (the default): `title`, `channel_name`, `channel_url`, `view_count`, `like_count`, `upload_date`, `thumbnail_url`, `tags`, `categories`. Optional extra formats: `srt`, `vtt`, `text`. A video that cannot be transcribed comes back as an error row (`success` false with `error_type` and `error_message`) instead of failing the run.

## Prerequisites

- Apify account (sign up at https://apify.com?fpr=9n7kx3&fp_sid=awesomeskills).
- Authentication via `apify login`, or an `APIFY_TOKEN` environment variable (Apify Console, Settings, Integrations).

## The Actor

- Store page: https://apify.com/johnvc/YoutubeTranscripts?fpr=9n7kx3&fp_sid=awesomeskills
- Actor ID: `johnvc/YoutubeTranscripts`
- Pricing: pay per video transcribed; failed videos are free (see `references/gotchas.md`).

## Run it with the Apify CLI

Single video:

```bash
apify actors call "johnvc/YoutubeTranscripts" -i '{"youtube_url":"https://www.youtube.com/watch?v=jNQXAC9IVRw"}' \
  --json \
  --user-agent apify-awesome-skills/apify-youtube-transcript-api \
  2>/dev/null
```

Batch, with SRT and VTT added to each row:

```bash
apify actors call "johnvc/YoutubeTranscripts" -i '{"youtube_url":["https://www.youtube.com/watch?v=jNQXAC9IVRw","https://www.youtube.com/shorts/s4UkCaf_scs"],"output_formats":["srt","vtt"]}' \
  --json \
  --user-agent apify-awesome-skills/apify-youtube-transcript-api \
  2>/dev/null
```

Every call carries the three flags this repo expects: `--json`, `--user-agent apify-awesome-skills/apify-youtube-transcript-api`, and `2>/dev/null`.

## Run it from Claude or another AI agent (MCP)

The Actor is MCP-ready. Add the hosted server URL:

`https://mcp.apify.com/?tools=actors,docs,johnvc/YoutubeTranscripts`

Then ask, for example: "Get the transcript of this YouTube video and summarize it." MCP setup docs: https://docs.apify.com/platform/integrations/mcp

## Workflow

1. Collect the URL or URLs. Standard watch URLs, Shorts, youtu.be, embed, and mobile URLs all work; batches go in one array.
2. Pick the language if it matters. `languages` is an ordered preference list (default `["en"]`); first available track wins, with fallback to whatever exists.
3. Optional: discover before fetching. `"list_only": true` returns `available_transcripts` per video (language, manual vs generated, translatable) without fetching or charging for any transcript.
4. Optional: request `output_formats` (`srt`, `vtt`, `text`) if the user needs subtitle files rather than JSON.
5. Run the Actor and read the dataset. Deliver `non_timestamped` for reading or LLM input, `timestamped` for alignment, `srt` or `vtt` for players.

## Inputs

- `youtube_url` (string or array, required)
- `languages` (ordered array of ISO 639-1 codes, default `["en"]`)
- `translate_to` (single ISO code; see limits below)
- `transcript_type` (`any`, `manual`, `generated`; default `any`)
- `output_formats` (array: `srt`, `vtt`, `text`)
- `preserve_formatting` (boolean, keeps inline italic and bold tags)
- `list_only` (boolean, discovery mode, free of the per-video charge)
- `include_metadata` (boolean, default true; set false for slightly faster runs)

## Cost

Billing is per video successfully transcribed, at a fraction of a cent per video; a thousand-video batch costs on the order of a few cents. Failed videos and `list_only` discovery runs are not charged the per-video fee. Details and the live-price check are in `references/gotchas.md`.

## Honest limits

- Translation (`translate_to`) only covers the languages YouTube exposes for auto-translation, roughly 18 codes. An unsupported code returns the original track unchanged; check for the `translated_to` field in the output to confirm translation actually happened.
- No captions means no transcript: the API reads YouTube's caption tracks, so a video with captions disabled returns an error row.
- Very large batches take time; the Actor processes several videos in parallel, but thousands of URLs can run for many minutes.

## Troubleshooting

- Error row with `error_type` IpBlocked or RequestBlocked: rare and transient; the Actor retries with fresh sessions automatically. Rerun the failed URLs; only successes are charged.
- Empty `translated_to` after requesting translation: the target code is not in `translation_languages` for that video. Pick a supported code from a `list_only` run.
- Timed-out run on a huge batch: split the input into smaller arrays, or raise the run timeout in the run options.

See `references/gotchas.md` for cost guardrails and error recovery, and `references/actor-index.md` for the Actor routing table.

## Related Actors

- Google Short Videos API (find Shorts by keyword, then feed the URLs into this transcript API): https://apify.com/johnvc/google-short-videos-api?fpr=9n7kx3&fp_sid=awesomeskills
