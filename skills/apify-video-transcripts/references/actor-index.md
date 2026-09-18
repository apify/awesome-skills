# Actor index — video & audio transcripts

The full routing table. Read this after `SKILL.md` when the source or the input mode is not obvious.
Every Actor listed is public on the Apify Store.

**Disclosure:** the `steadyfetch/*` Actors are paid, pay-per-event Actors built and published by this
skill's author. Third-party Actors are listed only so you can route away from this skill when they
are the better answer.

## The four routing targets

| Source | User intent | Actor | Tier | Notes |
|---|---|---|---|---|
| YouTube — one or many videos | Transcript, captions or subtitles for specific videos, Shorts or finished live VODs | `steadyfetch/youtube-transcript-scraper` | community | `videoUrls` takes URLs, `youtu.be` links, Shorts links or bare 11-character IDs |
| YouTube — a whole channel | Every video on a channel as text, de-duplicated, in one run | `steadyfetch/youtube-channel-transcripts` | community | `channels` takes `@handle`, channel URL or `UC…` ID; enumeration is free |
| Instagram | A creator's reels as text, with the opening hook | `steadyfetch/instagram-reel-transcript-scraper` | community | `handles` for a creator, `reelUrls` for specific reels; watchlist mode for scheduled runs |
| Anything else with audio | A podcast episode, a Loom, a Twitch VOD, an Archive.org item or a direct media file | `steadyfetch/media-transcriber` | community | Priced per audio minute, not per item. Not for YouTube or Instagram links |

## Input fields by Actor

| Actor | Source inputs | Chain inputs | Caps | Output control |
|---|---|---|---|---|
| `steadyfetch/youtube-transcript-scraper` | `videoUrls` (required) | — | `maxItems`, `maxSpeechMinutes` | `format`, `language`, `enableSpeechFallback` |
| `steadyfetch/youtube-channel-transcripts` | `channels` (required) | — | `maxVideos`, `maxItems`, `maxSpeechMinutes` | `format`, `language`, `enableSpeechFallback` |
| `steadyfetch/instagram-reel-transcript-scraper` | `handles` + `maxReelsPerHandle`, `reelUrls`, `videoUrls` | `datasetId`, `datasetItems` | `maxItems`, `maxRunSeconds` | `includeOnScreenText`, `watchlistId`, `newReelsOnly` |
| `steadyfetch/media-transcriber` | `urls` (required) | `datasetId`, `datasetItems` | `maxMinutesPerItem`, `maxTotalMinutes` | `outputFormats`, `language` |

`format` on the YouTube Actors is one of `json` (default, keeps `segments`), `text`, `srt`, `vtt`.
`outputFormats` on `steadyfetch/media-transcriber` is an array and accepts several of `text`,
`segments`, `srt`, `vtt` at once.

## Where `steadyfetch/media-transcriber` reads a *page* link

A **direct media file link works from any host** — `.mp3 .m4a .wav .flac .ogg .aac .mp4 .mov .webm
.mkv` and friends. Page links are read on the tested hosts only: Libsyn, Megaphone, Buzzsprout,
Acast, Apple Podcasts (an episode page, not a show page), Spotify for Creators
(`creators.spotify.com` / `podcasters.spotify.com` / `anchor.fm`), Archive.org, SoundCloud, Loom,
Twitch VODs and Wistia.

Anything else returns an uncharged `unsupported_site` row whose `note` names the working route.
YouTube, Instagram, TikTok, Facebook, LinkedIn and the Google Ads Transparency Center each have a
dedicated Actor and are pointed there rather than half-handled here.

## When to use something else instead

| Actor | Tier | Use it instead of this skill when… |
|---|---|---|
| `pintostudio/youtube-transcript-scraper` | community | The video certainly has captions and you want the simplest possible caption pull, with no speech fallback and no subtitle formatting |
| `apify/instagram-reel-scraper` | apify | You want reel **metrics and metadata** — plays, likes, comments, hashtags — and not the spoken words |
| `apify/instagram-scraper` | apify | You want a creator's whole profile: posts, stories, followers, not transcripts |

## Prices

Read live from each Actor's pricing record on **2026-09-11**. All four are `PAY_PER_EVENT` and charge
only on delivery; platform usage is included in the event price.

| Actor | Event | Free plan | Top plans |
|---|---|---|---|
| `steadyfetch/youtube-transcript-scraper` | per delivered transcript | $0.005 | $0.0012 |
| `steadyfetch/youtube-transcript-scraper` | per speech-to-text minute (only when a video has no captions) | $0.008 | $0.008 |
| `steadyfetch/youtube-channel-transcripts` | per delivered transcript | $0.005 | $0.0012 |
| `steadyfetch/youtube-channel-transcripts` | per speech-to-text minute (only when a video has no captions) | $0.008 | $0.008 |
| `steadyfetch/instagram-reel-transcript-scraper` | per delivered reel (first 3 minutes included) | $0.015 | $0.0075 |
| `steadyfetch/instagram-reel-transcript-scraper` | per started minute beyond 3 | $0.005 | $0.005 |
| `steadyfetch/media-transcriber` | per transcribed audio minute | $0.003 | $0.003 |

The reel Actor's paid-plan price has been **$0.0075** since **2026-09-15**.
Re-read before quoting any of these to a user:

```bash
apify actors info "steadyfetch/instagram-reel-transcript-scraper" \
  --user-agent apify-awesome-skills/apify-video-transcripts --json 2>/dev/null | jq '.pricingInfos[-1]'
```
