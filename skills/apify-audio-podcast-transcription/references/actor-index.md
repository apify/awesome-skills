# Actor index: audio and podcast transcription

Input fields and output fields of the Actor, in one file.

## Routing

| Actor | Use it for |
|---|---|
| `conserving_celerytop/audio-podcast-transcription` | Transcripts and subtitles from file links or podcast feeds |
| `conserving_celerytop/podcast-episode-scraper` | Episode lists and audio links from podcast feeds (inputs: `feedUrls` required, `maxEpisodesPerFeed`, `publishedSince`, `maxResults`) |

## Input: `conserving_celerytop/audio-podcast-transcription`

Every field of the `conserving_celerytop/audio-podcast-transcription` input, read from its published input schema. Pass them as JSON in the `--input` value of `apify actors call`.

| Field | Type | Default | What it does |
|---|---|---|---|
| `audioUrls` | list |  | Enter direct links to audio or video files, one per line: MP3, M4A, AAC, WAV, FLAC, OGG, OPUS, MP4, MOV, WEBM or MKV. Use your own files or a podcast episode's file link. |
| `rssFeedUrls` | list |  | Enter podcast RSS feed links, one per line. The newest episodes of each feed are transcribed (see Episodes per feed). |
| `episodesPerFeed` | int | `1` | Transcribe this many of the newest episodes from each podcast RSS feed. |
| `maxFiles` | int | `20` | Transcribe at most this many files in this run, file links first, then feed episodes. Duplicates count once. |
| `language` | str | `"en"` | Choose the spoken language. English uses the English models. Any other choice, or Detect automatically, uses the multilingual model (about 100 languages), which costs more per minute. Values: `auto`, `en`, `es`, `fr`, `de`, `it`, `pt`, `nl`, `pl`, `ru`, `uk`, `tr`, `ar`, `he`, `hi`, `ja`, `ko`, `zh`, `sv`, `da`, `no`, `fi`, `cs`, `ro`, `hu`, `el`, `id`, `vi`, `th`, `ca`. |
| `englishAccuracy` | str | `"standard"` | Standard is the lowest price. High uses a larger English model with fewer errors and costs more per minute. Applies when Language is English. Values: `standard`, `high`. |
| `subtitleFormats` | list | `["srt"]` | Save these subtitle files for each transcript in the key-value store. Each dataset row links to them. Values: `srt`, `vtt`. |
| `includeSegments` | bool | `true` | Add the segments list (start, end, text) to each dataset row. |
| `maxMinutesPerFile` | int | `240` | Transcribe at most the first this many minutes of each file. You pay only for the minutes transcribed. |
| `maxFileSizeMb` | int | `1024` | Download files up to this size. Larger files return a row with status file_too_large and are free. |

## Output

Every field of a `conserving_celerytop/audio-podcast-transcription` result row, read from its published dataset schema. The CSV has the same columns; lists and objects are written as JSON text.

| Field | What it holds |
|---|---|
| `inputUrl` | The file or episode link as entered or as listed in the feed. |
| `fileUrl` | The file address after redirects. |
| `source` | url for a file link you entered, rss for a feed episode. |
| `feedUrl` | The podcast RSS feed the episode came from. |
| `feedTitle` | Podcast title from the feed. |
| `episodeTitle` | Episode title from the feed. |
| `episodePublishedAt` | Episode publish date from the feed (ISO 8601, UTC). |
| `status` | ok, or why there is no transcript: no_speech, not_found, blocked, rate_limited, robots_disallowed, robots_unreadable, not_media, undecodable, no_audio, file_too_large, timeout, network_error, http_error, domain_not_found, too_many_redirects, invalid_input, invalid_feed, no_episodes. |
| `language` | Spoken language code (for example en). |
| `durationSeconds` | Length of the file in seconds. |
| `transcribedSeconds` | Seconds of audio transcribed (less than the length when a limit cut the file). |
| `speechSeconds` | Seconds in which speech was detected. |
| `billedMinutes` | Audio minutes charged for this file (started minutes of the transcribed audio). 0 when the file failed or had no speech. |
| `truncated` | true when only the first part of the file was transcribed (Maximum minutes per file or your spending limit). |
| `text` | The full transcript. |
| `wordCount` | Words in the transcript. |
| `segments` | Timestamped segments: start and end in seconds, and text. |
| `srtUrl` | Link to the SRT subtitle file in the key-value store. |
| `vttUrl` | Link to the WebVTT subtitle file in the key-value store. |
| `model` | Speech model used. |
| `fileSizeBytes` | Size of the downloaded file. |
| `audioCodec` | Audio codec of the file (for example mp3, aac, opus). |
| `transcribedAt` | When the row was written (ISO 8601, UTC). |
| `charged` | true when this file was charged as audio-minute events. |
| `error` | Why the file has no transcript, or a note (for example that the file was cut at a limit). |
