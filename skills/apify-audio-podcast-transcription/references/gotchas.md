# Gotchas: audio and podcast transcription

Cost guardrails, error recovery and common pitfalls. Read this on demand when building inputs or when a run fails.

## Cost guardrails

Both Actors use the `PAY_PER_EVENT` model. Check the live price before a large run, because prices can change:

    apify actors info "conserving_celerytop/audio-podcast-transcription" --json \
      --user-agent apify-awesome-skills/apify-audio-podcast-transcription 2>/dev/null

Prices when this skill was written (check `pricingInfo` for the current ones; Apify plan tiers can lower them):

| Actor | Event | Price (USD) |
|-------|-------|-------------|
| `conserving_celerytop/audio-podcast-transcription` | audio minute, English, standard | 0.0025 |
| | audio minute, English, high accuracy | 0.003 |
| | audio minute, other languages or auto-detect | 0.01 |
| `conserving_celerytop/podcast-episode-scraper` | episode | 0.001 |

Both also charge a one-time Actor start event of 0.00005 per GB of memory (minimum one event). Failed, undecodable and silent files are not charged by the transcription Actor, and broken feeds are free in the scraper.

Rough estimate: 1 hour of English audio at standard accuracy is about $0.15. The same hour with `language` set to anything else, or `auto`, is about $0.60. Always present cost as a rough estimate, not a guarantee.

### How to bound a run

The CLI has no per-run charge cap flag, so bound the run through the input and the call:

- `maxFiles` (default 20) limits how many files or feed episodes are transcribed.
- `maxMinutesPerFile` (default 240) cuts each file; you pay only for the minutes transcribed.
- `episodesPerFeed` (default 1) limits episodes per feed.
- `--timeout SECONDS` on `apify actors call` stops a run that goes on too long.
- Ask the user how long the audio is before starting. Minutes are not known in advance.

### Confirmation thresholds (suggested)

- Estimated cost above $5: warn the user.
- Estimated cost above $20: require explicit user confirmation before running.

### Cost traps

- `language: "auto"` or any language other than English uses the multilingual model, which costs 4 times the English standard price. Set `en` when the audio is English.
- A feed with many episodes and a high `episodesPerFeed` multiplies fast. Transcribe one or two episodes first.
- A started minute counts as a full minute, per file. Many very short files cost slightly more than their total length suggests.

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| Row has `status` `not_media` | The link is a web page (for example a YouTube watch page) | Ask for a direct link to the audio or video file |
| `blocked`, `rate_limited`, `robots_disallowed`, `robots_unreadable` | The host refuses automated downloads | Use a link the user is allowed to fetch, or host the file somewhere public; do not loop |
| `no_speech`, `no_audio`, `undecodable` | Silent, empty or damaged file | Check the file; these rows are free |
| `file_too_large` | File is above `maxFileSizeMb` (default 1024) | Raise `maxFileSizeMb` or split the file |
| `invalid_feed` or `no_episodes` | The RSS link is not a feed, or it has no episodes | Ask for the real RSS link of the show |
| `timeout`, `network_error`, `http_error` | The host was slow or returned an error | Retry once; if it repeats, the link is the problem |
| `truncated` is `true` | `maxMinutesPerFile` or a spending limit cut the file | Raise the limit or report the transcript as partial |
| CLI says you are not logged in | No token | Run `apify login` or set `APIFY_TOKEN` |

## Actor-specific notes

### `conserving_celerytop/audio-podcast-transcription`

- Input needs at least one of `audioUrls` or `rssFeedUrls`. Links must point at the file itself.
- Subtitles: `subtitleFormats` accepts `srt` and `vtt`. Each dataset row links to the files with `srtUrl` and `vttUrl`.
- Segments (start, end, text) are included by default; set `includeSegments` to `false` to shrink the rows.
- No speaker labels. Segments carry timestamps only.

### `conserving_celerytop/podcast-episode-scraper`

- `feedUrls` is required. `publishedSince` filters by date, `maxEpisodesPerFeed` defaults to 20 and `maxResults` to 1000.
- It needs a public RSS feed. Shows that exist only inside one app have no feed to read.
- Hand the `audioUrl` of each episode to the transcription Actor as `audioUrls`.
