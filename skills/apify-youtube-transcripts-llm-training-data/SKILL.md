---
name: apify-youtube-transcripts-llm-training-data
description: Build LLM training data from YouTube transcripts in bulk with the Apify Actor johnvc/YoutubeTranscripts. Feed it an array of video URLs and get one clean row per video, with non_timestamped transcript text ready for tokenization, timestamped snippets, language_code, and provenance metadata (title, channel_name, upload_date, view_count) for dataset documentation. Filter by language or translate every transcript into one target language for a consistent corpus. Use when the user wants LLM training data from videos, a fine-tuning or RAG corpus from YouTube, bulk YouTube transcripts for machine learning, or a text dataset from spoken video content without running speech-to-text. Pay-per-video billing, MCP-ready for Claude and other AI agents.
author: John Cole
author_url: https://github.com/johnisanerd
license: MIT
metadata:
  version: "1.0"
---

# YouTube Transcripts as LLM Training Data

Turn a list of YouTube videos into a clean text corpus for LLM fine-tuning, RAG, or analysis. One run takes an array of URLs and returns one row per video: the full transcript as a single text field, plus the provenance metadata (title, channel, upload date, views) a documented dataset needs.

## When to use this skill

- The user wants LLM training data, a fine-tuning corpus, or RAG documents sourced from YouTube videos.
- They want bulk transcripts from a channel dump, a playlist export, or a keyword-collected URL list.
- They want spoken-video content as text without running their own speech-to-text.
- They need a single-language corpus from mixed-language sources (translate everything to one target).

Not for: discovering which videos to include (collect URLs first; see the chain table in `references/actor-index.md`), videos without caption tracks (those return error rows), or verbatim audio ground truth (captions are YouTube's own tracks, not fresh ASR).

## What you get (one row per video)

The corpus fields: `non_timestamped` (the full transcript as one string, the training-text column), `language_code`, `source_type` (Manual or Auto-generated, a quality signal), `snippet_count`, `total_seconds`. The provenance fields for dataset documentation: `title`, `channel_name`, `channel_url`, `upload_date`, `view_count`, `like_count`, `tags`, `categories`, `url`, `video_id`. Optional alignment data: `timestamped` (snippets with `text`, `start`, `duration`). Failures arrive as error rows (`success` false), so a bad URL never kills the batch.

## Prerequisites

- Apify account (sign up at https://apify.com?fpr=9n7kx3&fp_sid=awesomeskills).
- Authentication via `apify login`, or an `APIFY_TOKEN` environment variable (Apify Console, Settings, Integrations).

## The Actor

- Store page: https://apify.com/johnvc/YoutubeTranscripts?fpr=9n7kx3&fp_sid=awesomeskills
- Actor ID: `johnvc/YoutubeTranscripts`
- Pricing: pay per video transcribed; failed videos are free (see `references/gotchas.md`).

## Run it with the Apify CLI

Batch corpus run, English preferred, metadata on for provenance:

```bash
apify actors call "johnvc/YoutubeTranscripts" -i '{"youtube_url":["https://www.youtube.com/watch?v=jNQXAC9IVRw","https://www.youtube.com/watch?v=dQw4w9WgXcQ"],"languages":["en"],"include_metadata":true}' \
  --json \
  --output-dataset \
  --user-agent apify-awesome-skills/apify-youtube-transcripts-llm-training-data \
  2>/dev/null
```

Mixed-language sources normalized into a Spanish corpus:

```bash
apify actors call "johnvc/YoutubeTranscripts" -i '{"youtube_url":["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],"translate_to":"es"}' \
  --json \
  --output-dataset \
  --user-agent apify-awesome-skills/apify-youtube-transcripts-llm-training-data \
  2>/dev/null
```

Every call carries the three flags this repo expects: `--json`, `--user-agent apify-awesome-skills/apify-youtube-transcripts-llm-training-data`, and `2>/dev/null`. The `--output-dataset` flag prints the dataset rows (the transcript data) on success instead of just run metadata.

## Run it from Claude or another AI agent (MCP)

The Actor is MCP-ready. Add the hosted server URL:

`https://mcp.apify.com/?tools=actors,docs,johnvc/YoutubeTranscripts`

Then ask, for example: "Pull the transcripts for these 50 videos and build me a JSONL training file with text and metadata columns." MCP setup docs: https://docs.apify.com/platform/integrations/mcp

## Workflow

1. Collect the URL list. Channel exports, playlist dumps, or keyword discovery (see the chain table); dedupe by `video_id` before running.
2. Decide the corpus language policy. Same-language sources: set `languages` to that code. Mixed sources: set `translate_to` to normalize, and note the translation caveat below.
3. Run the batch. Pass the whole array in one call; the Actor processes videos in parallel and records failures as error rows without stopping.
4. Filter for quality. Drop rows where `success` is false. If caption quality matters, prefer rows with `source_type` Manual, or set `transcript_type` to `manual` up front.
5. Export the corpus. Map `non_timestamped` to your text column and carry `title`, `channel_name`, `upload_date`, `url`, and `language_code` as metadata columns; write JSONL or CSV.
6. Document provenance. The metadata fields exist so the dataset card can say what the corpus contains and where it came from.

## Inputs

- `youtube_url` (array of URLs, the batch)
- `languages` (ordered array of ISO 639-1 codes, default `["en"]`)
- `translate_to` (single ISO code, normalizes the corpus language; see limits)
- `transcript_type` (`manual` restricts to human-written captions, a quality filter)
- `include_metadata` (boolean, default true; keep it on for provenance)
- `list_only` (boolean; free dry run that shows the available languages per video)

## Cost

Billing is per video successfully transcribed, at a fraction of a cent per video; a 10,000-video corpus costs well under a dollar. Failed videos are not charged. Details and the live-price check are in `references/gotchas.md`.

## Honest limits

- Captions are YouTube's own tracks. Auto-generated captions contain recognition errors; filter on `source_type` Manual when accuracy matters more than coverage.
- Translation (`translate_to`) covers only the languages YouTube exposes for auto-translation, roughly 18 codes. Rows without a `translated_to` field were NOT translated; exclude them or re-plan the corpus language.
- Respect the licensing context of the content you collect; a transcript corpus inherits the source videos' copyright status. That judgment belongs to the dataset builder, not this API.

## Troubleshooting

- Many error rows in one channel batch: that channel likely disables captions; check a few URLs with `"list_only": true`.
- Corpus language is inconsistent: some rows fell back to a different track. Group by `language_code` and re-run outliers with `translate_to`.
- Batch runs long: thousands of URLs take minutes; split into parallel runs of about 500 URLs if wall-clock matters.

See `references/gotchas.md` for cost guardrails and error recovery, and `references/actor-index.md` for the Actor routing table.

## Related Actors

- Google Short Videos API (discover short-form videos by keyword to feed this corpus builder): https://apify.com/johnvc/google-short-videos-api?fpr=9n7kx3&fp_sid=awesomeskills
