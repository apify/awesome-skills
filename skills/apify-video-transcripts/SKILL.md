---
name: apify-video-transcripts
description: Turn video and audio into text — full transcripts, timestamped segments, SRT and VTT subtitles, and the first-3-seconds hook — from one YouTube video, Short or live VOD, a whole YouTube channel in a single run, a creator's Instagram reels, a podcast episode, a Loom or a Twitch VOD, or any direct media file link. Captions are used where they exist and speech-to-text runs where they do not, in ~90 languages, with no third-party API key and no charge when a video has nothing to say. Use when the user asks to transcribe a video or a podcast, wants a YouTube transcript, captions or subtitles, an SRT or VTT file, a channel's whole back catalogue as text, the script of an Instagram reel, the hook a creator opens with, video-to-text or audio-to-text at scale, a searchable archive of everything someone has said on camera, or a scheduled run that only transcribes what is new since last time.
author: Steadyfetch
author_url: https://github.com/steadyfetch
metadata:
  category: data-extraction
  keywords: "youtube-transcript, channel-transcripts, instagram-reels, reel-transcript, speech-to-text, audio-transcription, podcast-transcript, srt, vtt, subtitles, video-to-text, any-url"
---

# Video & Audio Transcripts

Get the **words** out of video and audio: full transcripts, timestamped segments, ready-made SRT and
VTT, and the first-3-seconds hook — one YouTube video, a whole channel, a creator's Instagram reels,
or any podcast, Loom, Twitch VOD or direct media file.

**Author:** Steadyfetch. **Disclosure:** the `steadyfetch/*` Actors this skill routes to are paid,
pay-per-event Apify Actors built and published by the author. No affiliate or referral parameters
appear anywhere in this skill — every link is a plain Apify Store URL.

**CLI rules:** every `apify` command below carries `--user-agent apify-awesome-skills/apify-video-transcripts`,
`--json` (or `--format json` on `datasets get-items`) and `2>/dev/null`. Never drop the user-agent.

## Where this sits next to the Actors you may already know

| Situation | Use |
|---|---|
| One YouTube video that already has captions, nothing else needed | `pintostudio/youtube-transcript-scraper` — the Store's most-used caption puller, and the simpler tool for that one case |
| Instagram reel **metrics** — plays, likes, comments, hashtags — without the spoken words | `apify/instagram-reel-scraper` |
| The video has **no captions**, or you need speech-to-text, or SRT/VTT, or a hook | this skill |
| A **whole channel** — Shorts and live VODs included — as one de-duplicated run | this skill |
| A **creator's reels** transcribed, with the hook and the second speech starts | this skill |
| A podcast episode, a Loom, a Twitch VOD or a direct media file | this skill |

The line is captions versus speech. A caption-only tool answers a video that has captions and returns
nothing for one that does not — roughly every re-upload, most live VODs, and a large share of Shorts
and reels. These Actors read captions first *and* fall back to speech-to-text, so the answer does not
depend on whether the uploader turned captions on, and a video with genuinely nothing spoken comes
back as an honest uncharged row rather than as invented text.

## Example prompts

Prompts this skill handles:

- "Transcribe this YouTube video and give me an SRT file."
- "Pull the transcript of every video on this channel from the last year and tell me which topics come up most."
- "What hook does this Instagram creator open their reels with?"

Out of scope (the boundary):

- "What is the script of the Facebook ad this brand is running?" — paid ad creative from an ad
  library is a different job. Use `apify-ad-creative-transcripts`, which searches Meta, TikTok,
  LinkedIn and the Google Ads Transparency Center and reads what those ads say.

## Prerequisites

(No need to check upfront.)

- Apify account ([sign up](https://apify.com))
- Apify CLI v1.5.0+ (`npm install -g apify-cli`); `jq` recommended for parsing
- Authentication via one of:
  - `apify login` (OAuth)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

Never put a token in a URL — the Apify API takes `Authorization: Bearer $APIFY_TOKEN`, and a query
parameter would land in every access log the request passes through.

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Step 1: Route to the Actor that matches the source
- [ ] Step 2: Fetch the input schema before building input
- [ ] Step 3: Set the cost ceiling BEFORE the run
- [ ] Step 4: Run, then fetch the dataset
- [ ] Step 5: Read the right text field, and do not filter on `charged`
- [ ] Step 6: Answer, and report what did not deliver
```

### Step 1: Route to the Actor that matches the source

| The user has… | Actor | Main input | Price per delivered result |
|---|---|---|---|
| One or more YouTube videos, Shorts or finished live VODs | `steadyfetch/youtube-transcript-scraper` | `videoUrls` (URLs or bare video IDs) | $0.005 free plan → $0.0012 top plans, per transcript |
| A whole YouTube channel — handle, URL or channel ID | `steadyfetch/youtube-channel-transcripts` | `channels` | $0.005 free plan → $0.0012 top plans, per transcript |
| A creator's Instagram reels, or reel links | `steadyfetch/instagram-reel-transcript-scraper` | `handles`, or `reelUrls` | $0.015 free plan → $0.0075 top plans, per reel |
| A podcast episode, a Loom, a Twitch VOD, an Archive.org item, or a direct media file link | `steadyfetch/media-transcriber` | `urls` | $0.003 per transcribed audio minute, every plan |

All four are `PAY_PER_EVENT` and charge **only on delivery** — a video with no speech, a dead link or
a blocked fetch returns a row that costs nothing. Platform usage is included in the event price: no
start fee, no separate compute bill, no third-party speech API key to bring.

Prices read live from each Actor's pricing record on **2026-09-11**. Re-read before quoting them to a
user (`apify actors info "<actor-id>" --user-agent apify-awesome-skills/apify-video-transcripts --json 2>/dev/null | jq '.pricingInfos[-1]'`); the reel Actor
has carried $0.0075 on its paid plans since **2026-09-15**.

Two surcharges, both per started minute and both easy to predict:

- The YouTube Actors add **$0.008 per speech-to-text minute**, and only when a video has no usable
  captions. A captioned video never triggers it — check `source` on the row (`captions` or `speech`).
- The reel Actor includes the first 3 minutes of each video and adds **$0.005 per started minute**
  beyond that. Reels are almost always under 3 minutes; a long-form Instagram video is not.

### Step 2: Fetch the input schema before building input

Field names differ per Actor — `videoUrls` on the single-video Actor, `channels` on the channel one,
`handles` / `reelUrls` on the reel one, `urls` on the media one. Do not guess.

```bash
apify actors info "steadyfetch/youtube-channel-transcripts" --input \
  --user-agent apify-awesome-skills/apify-video-transcripts 2>/dev/null

apify actors info "steadyfetch/youtube-channel-transcripts" --readme \
  --user-agent apify-awesome-skills/apify-video-transcripts
```

### Step 3: Set the cost ceiling BEFORE the run

Two independent ceilings. Use both.

**a) The Actor's own cap** — cheapest and always available:

| Actor | Cap fields | Defaults |
|---|---|---|
| `steadyfetch/youtube-transcript-scraper` | `maxItems`, `maxSpeechMinutes` | 100 videos, 60 speech minutes |
| `steadyfetch/youtube-channel-transcripts` | `maxVideos` (per channel), `maxItems` (whole run), `maxSpeechMinutes` | 50 per channel, 500 per run, 60 speech minutes |
| `steadyfetch/instagram-reel-transcript-scraper` | `maxReelsPerHandle`, `maxItems`, `maxRunSeconds` | 10 per creator, 1000 per run, 3600 s |
| `steadyfetch/media-transcriber` | `maxMinutesPerItem`, `maxTotalMinutes` | 0 and 0, i.e. unlimited — always set these |

**b) A hard dollar cap.** `apify actors call` has **no** cost-cap flag — checked against apify-cli
1.6.2 and the [CLI reference](https://docs.apify.com/cli/docs/reference#apify-actors-call), whose
`call` and `start` flags are only `--build`, `--input`, `--input-file`, `--json`, `--memory`,
`--output-dataset`, `--silent`, `--timeout`. A dollar ceiling has to be set on the API call, where
`maxTotalChargeUsd` is a documented query parameter of
[`POST /v2/acts/{actorId}/runs`](https://docs.apify.com/api/v2/act-runs-post):

```bash
curl -sS -X POST \
  "https://api.apify.com/v2/acts/steadyfetch~youtube-channel-transcripts/runs?maxTotalChargeUsd=2&waitForFinish=300" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"channels":["https://www.youtube.com/@Apify"],"maxVideos":200}'
```

Thresholds to apply on the user's behalf: estimate before running, warn above **$5**, ask for explicit
confirmation above **$20**, and always present the number as an estimate. A 500-video channel is
~$0.60–$2.50 depending on plan if the videos are captioned, and materially more if they are not —
which is why `maxSpeechMinutes` exists.

### Step 4: Run, then fetch the dataset

```bash
apify actors call "steadyfetch/youtube-transcript-scraper" \
  -i '{"videoUrls":["https://www.youtube.com/watch?v=jNQXAC9IVRw"],"format":"srt","maxItems":1}' \
  --user-agent apify-awesome-skills/apify-video-transcripts \
  --json 2>/dev/null
```

Take `.id`, `.status` (want `SUCCEEDED`) and `.defaultDatasetId` from the output, then:

```bash
apify datasets get-items DATASET_ID --format json \
  --user-agent apify-awesome-skills/apify-video-transcripts 2>/dev/null > transcripts.json
```

`apify datasets get-items` streams over the network every time, so save the file once and analyse from
disk instead of re-piping it into `jq` per query.

`format` on the two YouTube Actors decides what the row carries: `json` (the default) keeps
timestamped `segments`, `text` returns the transcript only, and `srt` / `vtt` put a ready-to-save
subtitle string on the row. On `steadyfetch/media-transcriber` the same choice is the `outputFormats`
array (`text`, `segments`, `srt`, `vtt`) and you can ask for several at once. **Ask for `srt` up
front if the user wants subtitles** — the default leaves `srt` and `vtt` null, and re-running to get
them costs a second transcript.

### Step 5: Read the right text field, and do not filter on `charged`

Two traps, both measured on live runs of these exact Actors:

- **`charged: false` does not mean empty.** These Actors remember what they have already delivered to
  your account: ask for the same video again and it comes back as a *repeat* row — `repeat: true`,
  `charged: false`, `firstSeenRunId` naming the earlier run — carrying the **full transcript**, free.
  A `select(.charged == true)` filter throws that content away, and on any re-run or scheduled watch
  most rows are repeats. Use `charged` for cost accounting only; filter on the content field.
- **The text field is not called the same thing everywhere.** It is `text` on
  `steadyfetch/youtube-transcript-scraper`, `steadyfetch/youtube-channel-transcripts` and
  `steadyfetch/media-transcriber`, and `transcript` on
  `steadyfetch/instagram-reel-transcript-scraper`. Delivered `status` also differs: `ok` on the three,
  `transcribed` (or `onscreen_text_extracted`) on the reel Actor.

So test the field you actually want for non-null, and confirm the real field names on a new dataset
before writing further queries:

```bash
apify datasets get-items DATASET_ID --limit 1 --format json \
  --user-agent apify-awesome-skills/apify-video-transcripts 2>/dev/null | jq '.[0]'
```

A safe cross-Actor extraction:

```bash
jq -r '.[] | select(._summary != true) | [(.title // .ownerUsername), ((.text // .transcript) | length)] | @tsv' transcripts.json
```

### Step 6: Answer, and report what did not deliver

Synthesise, do not dump a wall of transcript. Useful shapes:

| The user asked | Lead with |
|---|---|
| "transcribe this" | The text, plus the SRT/VTT string if they asked for subtitles |
| "what does this channel talk about" | Topic clusters across `text`, with the video titles that carry each |
| "what's their hook" | `hook3s` per reel sorted by `hookStartSeconds` — a high value means the reel makes you wait |
| "find where they said X" | The matching `segments` entries with their `start` seconds, as timestamp links |

Always close with the honest count: *N delivered, M returned uncharged* and why. Silent videos,
region-blocked uploads and expired links are normal, not a failed run.

## Recipes

### A — One video, subtitles included

```bash
apify actors call "steadyfetch/youtube-transcript-scraper" \
  -i '{"videoUrls":["VIDEO_URL_OR_ID"],"format":"vtt"}' \
  --user-agent apify-awesome-skills/apify-video-transcripts --json 2>/dev/null
```

`videoUrls` takes full URLs, `youtu.be` links, Shorts links or bare 11-character video IDs.

### B — A whole channel in one run

```bash
apify actors call "steadyfetch/youtube-channel-transcripts" \
  -i '{"channels":["https://www.youtube.com/@Apify"],"maxVideos":50,"maxItems":50}' \
  --user-agent apify-awesome-skills/apify-video-transcripts --json 2>/dev/null
```

`channels` accepts `@handle`, a channel URL or a `UC…` channel ID, several at once. Enumeration is
free — you pay per transcript, not per video listed. Each row carries `positionInChannel` and
`videosFound`, so you can tell a short run from a truncated one. Shorts and finished live VODs are
included; a stream that is still live returns `live_no_transcript_yet` and costs nothing.

### C — A creator's reels, with the hook

```bash
apify actors call "steadyfetch/instagram-reel-transcript-scraper" \
  -i '{"handles":["natgeo"],"maxReelsPerHandle":10}' \
  --user-agent apify-awesome-skills/apify-video-transcripts --json 2>/dev/null
```

Reels come back newest-first by posted date, each with `hook3s` (the first three seconds of *speech*)
and `hookStartSeconds` (the second speech actually begins — `0` when the reel opens talking). Handle
mode also fills `caption`, `plays`, `likes`, `comments`, `takenAt` and `isPinned` at no extra charge.
Silent reels are uncharged unless you set `"includeOnScreenText": true`, which reads the words off the
frames instead.

### D — A podcast, a Loom, a Twitch VOD or a file

```bash
apify actors call "steadyfetch/media-transcriber" \
  -i '{"urls":["https://example.com/episode-42.mp3"],"outputFormats":["text","segments","srt"],"maxTotalMinutes":120}' \
  --user-agent apify-awesome-skills/apify-video-transcripts --json 2>/dev/null
```

A **direct media file link works from any host** (`.mp3 .m4a .wav .flac .ogg .aac .mp4 .mov .webm
.mkv …`). *Page* links work on the tested hosts: Libsyn, Megaphone, Buzzsprout, Acast, Apple Podcasts
(an episode page, not a show page), Spotify for Creators, Archive.org, SoundCloud, Loom, Twitch VODs
and Wistia. This Actor is priced per audio minute, so cap it: a 60-minute episode is 60 charged
minutes.

### E — A scheduled watch that only pays for what is new

On `steadyfetch/instagram-reel-transcript-scraper`, name a watchlist (`"watchlistId": "my-creators"`)
and set `"newReelsOnly": true`, then save it as an Apify **Task** and give the Task a schedule. Each
later run delivers only the reels that list has never answered; rows carry `isNew` and `firstSeenAt`.
Independently of any watchlist, all four Actors remember what they have delivered to your account, so
re-running the same videos returns them as uncharged `repeat` rows with the text intact — see Step 5.

## Output fields

One row per video, reel or file. Every row carries `status`, `charged`, `retryable` and
`statusReason`; fields that do not apply are explicit `null` rather than missing keys.

| Actor | Key fields |
|---|---|
| `steadyfetch/youtube-transcript-scraper` | `status`, `charged`, `retryable`, `statusReason`, `videoId`, `url`, `title`, `channelName`, `channelId`, `durationSeconds`, `viewCount`, `isLiveContent`, `language`, `source` (`captions` / `speech`), `captionKind`, `text`, `segments`, `srt`, `vtt`, `chargeEvents`, `repeat`, `firstSeenAt`, `firstSeenRunId` |
| `steadyfetch/youtube-channel-transcripts` | the same, plus `inputChannel`, `channelHandle`, `positionInChannel`, `videosFound` |
| `steadyfetch/instagram-reel-transcript-scraper` | `status`, `charged`, `retryable`, `statusReason`, `transcript`, `hook3s`, `hookStartSeconds`, `onScreenText`, `language`, `durationSeconds`, `segments`, `shortCode`, `postUrl`, `ownerUsername`, `caption`, `takenAt`, `plays`, `likes`, `comments`, `thumbnailUrl`, `isPinned`, `postSource`, `videoUrl`, `urlExpiresAt`, `isNew`, `firstSeenAt`, `chargeEvents` |
| `steadyfetch/media-transcriber` | `status`, `charged`, `retryable`, `url`, `resolvedMediaUrl`, `sourceType`, `siteName`, `title`, `durationSeconds`, `language`, `languageConfidence`, `text`, `segments`, `srt`, `vtt`, `wordCount`, `chargedMinutes`, `isNew`, `firstSeenAt`, `repeat`, `firstSeenRunId`, `note` |

`segments` is `[{start, end, text}]` in seconds — use it to build timestamp links, not just to read.

**The reel Actor writes one extra last row:** an uncharged receipt marked `_summary: true` with
`status: "run_summary"`, carrying `attempted`, `delivered`, `unchargedMisses`, `chargedRows`,
`chargedEvents` and `stoppedBy`, so the invoice reconciles from the dataset itself. Drop it with
`select(._summary != true)` before counting rows.

## Reading rows that did not deliver

A row with `charged: false` and no text is an answer, not an error — `status` says what the video was,
and `retryable` says whether another run could do better.

| `status` | Meaning | Action |
|---|---|---|
| `no_speech` | Music or silence — no words were spoken. Returned honestly rather than as the filler text speech models hallucinate over music | Nothing to recover; on reels, re-run with `"includeOnScreenText": true` |
| `no_captions` | No captions, and you switched speech-to-text off for this run | Re-run with `"enableSpeechFallback": true` |
| `no_audio_stream` | The video exposes no audio track at all | Nothing to recover |
| `blocked_retry` | YouTube challenged, throttled, or was still processing the video | **Re-run** — `retryable: true`, nothing was charged |
| `region_blocked` / `channel_region_blocked` | The upload is not served to the country the run went out from (channel lookups try three) | Re-run; a later run may leave from an allowed location |
| `live_no_transcript_yet` | A stream that is still live — no transcript exists until it ends | Re-run after it ends |
| `channel_not_found` / `no_videos_found` | The handle did not resolve, or the channel has no public videos | Check the handle |
| `not_found` / `no_reels_found` | No public Instagram profile with that handle, or a profile with no video posts | Check the handle |
| `unavailable_expired` | A signed Instagram media URL expired before it could be fetched | Re-run from the handle or the reel link rather than a stale chained row |
| `resolve_blocked` | Instagram marks that reel copyright-blocked for embeds | Nothing to recover |
| `unsupported_site` | A page link on a host `media-transcriber` does not read | The row's `note` names the working route — usually a dedicated Actor or the direct file link |
| `unreachable` / `not_media` / `no_media` | 404, DNS failure, an image or a live stream, or a page exposing no fetchable file. A 401/403/451/throttle carries `retryable: true` | Re-run the retryable ones; fix the link otherwise |
| `skipped_deadline` | The run neared its time limit before this item's turn | Raise `maxRunSeconds` / `--timeout` and re-run |

None of these are charged.

## Quirks

- **YouTube links do not go into `steadyfetch/media-transcriber`.** It answers a YouTube page with an
  uncharged `unsupported_site` row whose `note` points at `steadyfetch/youtube-transcript-scraper` —
  cheaper and more reliable for YouTube. Route by source, not by "it's a URL".
- **Captions first, speech second.** `enableSpeechFallback` is on by default; `source` on each row
  says which path produced the text, and `captionKind` distinguishes uploader captions from YouTube's
  automatic ones. Turning the fallback off makes a run free of speech minutes and blind to every
  uncaptioned video.
- **`format` is a run-level choice, not a per-row one** on the YouTube Actors, and it defaults to
  `json`. `srt` and `vtt` are `null` unless you asked for them.
- **Channel enumeration is free**, and `maxVideos` caps per channel while `maxItems` caps the whole
  run — pass both when you list several channels, or the run is capped by whichever bites first.
- **Instagram reels are returned newest-first by posted date**, not in grid order, so a pinned reel
  appears in its real date position with `isPinned: true`.
- **If Instagram walls a creator's post feed**, the reel Actor falls back to the reels shown on the
  profile page; those rows carry the caption and date but leave `plays`, `likes` and `comments` null.
- **`media-transcriber` is per audio minute, not per item.** Set `maxTotalMinutes` and
  `maxMinutesPerItem` before anything long: its defaults are unlimited.
- **A bare run with no input is not a free preview.** Each Actor's no-input default runs a small live
  sample and is charged like any other run; say so before starting one on a user's account.

## Error handling

- Auth error → `apify login`, or set `APIFY_TOKEN`
- `Actor not found` → check the id against the routing table; all four are `steadyfetch/<name>`
- Run status `FAILED` → open the console URL from the run metadata and read the log
- Zero rows → the handle or channel did not resolve; check it before widening anything
- Every row uncharged with `no_captions` → speech-to-text was switched off; re-run with
  `"enableSpeechFallback": true`
- Every row uncharged with `blocked_retry` → transient; re-run, nothing was charged
- `srt` / `vtt` null → the run used the default `format: "json"`; ask for the subtitle format up front
- Long channel run hits the time limit → raise `--timeout`, or split the channel list

For the full routing table and the cost guardrails in one place, see
[references/actor-index.md](references/actor-index.md) and [references/gotchas.md](references/gotchas.md).
