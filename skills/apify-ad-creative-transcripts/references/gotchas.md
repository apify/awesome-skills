# Gotchas — ad creative transcripts

Cost guardrails and error recovery. Read on demand: before building an input, before a run larger
than a few dozen ads, or when a run comes back with rows the user did not expect.

**Disclosure:** the `steadyfetch/*` Actors below are paid, pay-per-event Actors built and published
by this skill's author.

## What actually costs money

All six Actors are `PAY_PER_EVENT` and charge **only on delivery**. A miss — an expired link, a
silent creative, a text-free image, a failed download — produces a row with `charged: false` and
costs nothing. Platform usage is included in the event price: no start fee, no separate compute bill.

| Actor | Charged event | Free plan | Top plans | Extra |
|---|---|---|---|---|
| `steadyfetch/facebook-ads-transcript-scraper` | one delivered ad | $0.020 | $0.010 | $0.005 per started video minute past 3 |
| `steadyfetch/tiktok-ads-transcript-scraper` | one delivered ad | $0.020 | $0.008 | $0.005 per started minute past 3 |
| `steadyfetch/linkedin-ads-transcript-scraper` | one delivered creative | $0.020 | $0.008 | $0.005 per started minute past 3 |
| `steadyfetch/google-ads-video-transcript-scraper` | one delivered video ad | $0.020 | $0.008 | $0.005 per started minute past 3 |
| `steadyfetch/google-ads-creative-text-scraper` | one extracted creative | $0.015 | read live — a price change lands 2026-09-15 | — |
| `steadyfetch/media-transcriber` | one transcribed audio minute (rounded up) | $0.003 | $0.003 | — |

Prices read from the live Store pricing tabs on 2026-09-07. They change; re-read them before quoting
a number to a user:

```bash
apify actors info "steadyfetch/facebook-ads-transcript-scraper" \
  --user-agent apify-awesome-skills/apify-ad-creative-transcripts --json 2>/dev/null
```

The pricing lives under `pricingInfos` — the entry with the most recent `startedAt` is the live one;
earlier entries are superseded history, and reading the wrong one quotes a stale price.

### Estimating before you run

```
estimate ≈ (ads you will deliver × per-result price)
         + ($0.005 × started minutes beyond the first 3, per video ad)
```

Worked examples, free plan:

| Job | Estimate |
|---|---|
| 25 short Meta video ads | ≈ $0.50 |
| 100 Meta ads, half of them 5-minute VSLs | ≈ $2.00 + 50 × 2 × $0.005 = ≈ $2.50 |
| 20 competitors watched daily, ~15 new ads a day | ≈ $0.30 a day — ads already on the watchlist are never billed again |
| One 45-minute podcast through `media-transcriber` | ≈ $0.14 |

Thresholds: warn above **$5**, get explicit confirmation above **$20**, and always present the number
as an estimate rather than a guarantee.

### The two ceilings

1. **The Actor's own cap** — `maxAds` (Meta, TikTok), `maxItems` (LinkedIn, Google video),
   `maxCreativesPerAdvertiser` (Google text), `maxTotalMinutes` (media-transcriber). Always set one.
2. **A hard dollar cap.** `apify actors call` has no cost-cap flag (checked against apify-cli 1.6.2
   and the [CLI reference](https://docs.apify.com/cli/docs/reference#apify-actors-call)). To enforce
   dollars, start the run through the API, where `maxTotalChargeUsd` is a documented query parameter
   of [`POST /v2/acts/{actorId}/runs`](https://docs.apify.com/api/v2/act-runs-post):

   ```bash
   curl -sS -X POST \
     "https://api.apify.com/v2/acts/steadyfetch~linkedin-ads-transcript-scraper/runs?maxTotalChargeUsd=2" \
     -H "Authorization: Bearer $APIFY_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"accountOwners":["Acme"],"maxItems":50}'
   ```

   The token goes in the header, never in the URL — a query-string token is copied into every access
   log, proxy log and traceback the request touches. These Actors reject a ceiling below **$0.05**.

   When the cap is reached, remaining ads still ship as uncharged `skipped_budget` rows carrying
   their identity, so raising the cap and re-running picks up exactly those.

### Cost traps specific to this family

- **`mediaType: "all"` and `activeStatus: "all"` on Meta** multiply the charged rows: inactive
  historical ads are usually the bulk of a large advertiser's library.
- **Long-form creative.** A 12-minute B2B webinar ad costs the per-ad price plus nine surcharge
  minutes. Sort by `durationSeconds` on a chained dataset before transcribing everything.
- **`media-transcriber` bills per minute, not per item.** One long file can outspend a hundred ads.
- **Re-running the same ads is free** — each Actor remembers what it delivered to that account
  (`repeat: true`, `charged: false`, entries expire after 90 days), and the repeat row still contains
  the full transcript, so a re-run is a free way to re-read old ads. The bare no-input sample run is
  the exception: it always runs live and is charged again each time.
- **A watchlist run is the cheap way to monitor.** With `watchlistId` set and `newAdsOnly: true`,
  ads already on the list are dropped before download — not fetched, not transcribed, not charged.

## Common errors

| Symptom | Cause | Fix |
|---|---|---|
| `Actor not found` | Wrong owner prefix | All six are `steadyfetch/<name>` |
| Auth error | No token | `apify login`, or export `APIFY_TOKEN` |
| Zero rows | Search matched nothing live | Widen the keyword or country; set `activeStatus: "all"`; for TikTok try another region or a longer `discoverPeriod` |
| Every row `no_audio` / `no_speech` | Creatives are music-only or silent | Re-run with `"includeOnScreenText": true`; the message is on the screen |
| Rows are `ocr_no_text_found` | Plain photos with no text | Expected; report it rather than retrying |
| `unavailable_expired` / `image_expired` on a chained run | The upstream scraper's signed media URLs went stale | Re-run the upstream scraper, or search directly in the transcript Actor so link and media are read together |
| `skipped_budget` rows | Your dollar cap was hit mid-run | Raise `maxTotalChargeUsd` and re-run those rows |
| `skipped_deadline` rows | Run timeout hit first | Raise the run timeout, or split the batch |
| `search_blocked`, `asr_unavailable` | Transient upstream refusal; rows marked `retryable` | Re-run later; nothing was charged |
| `failed_processing` on long videos | Ran out of time | Raise run memory (more memory buys more CPU) or split |
| `sample_note` row | Options set but no keyword, link or dataset given | Provide an actual target |
| `input_error` row | A field could not be used | The row says which one and how to fix it |

## Actor-specific notes

### `steadyfetch/facebook-ads-transcript-scraper`

- Searches by keyword or advertiser name in `searchQueries`; Ad Library links go in `adLibraryUrls`.
- `country` defaults to `US`, `mediaType` to `video`, `activeStatus` to `active`, `searchMaxAds` to
  25 per keyword.
- `includeImageText` is on by default — image ads come back with `imageText`.
- Watchlist store lives in the user's own account as `fb-ads-watch-<name>`; deleting it resets the
  history.

### `steadyfetch/tiktok-ads-transcript-scraper`

- Discovery is region-first: `discoverRegion` (`US`, `GB`, `CA`, `AU`, `DE`, `FR`, `ES`, `IT`, `NL`,
  `SE`, `RO`, `TR`, `BR`, `MX`, `AR`), `discoverPeriod` (`7`, `30`, `180`), `discoverSort`
  (`for_you`, `ctr`, `like`).
- For one specific brand, skip discovery and pass `videoUrls` or `materialIds`.
- Rows carry TikTok's own engagement signals — `ctr`, `likes`, `industryKey`, `objectiveKey` — plus
  `urlExpiresAt`; the media links are short-lived, so transcribe promptly rather than storing URLs
  for later.

### `steadyfetch/linkedin-ads-transcript-scraper`

- Most LinkedIn ads are static images; the Actor identifies video before opening it and reads image
  ads with OCR.
- `dateOption`: `last-30-days`, `current-month`, `current-year`, `last-year`, `custom-date-range`
  (with `startdate` / `enddate`). LinkedIn only serves roughly the last 12 months whatever you pick.
- `countries` accepts codes or full names. `impressions` and `availability` are filled only where
  LinkedIn discloses them (EU-served ads).
- `includeNonVideo: true` passes documents, carousels and text-only creatives through as uncharged
  rows — useful for a complete inventory.

### `steadyfetch/google-ads-video-transcript-scraper` and `steadyfetch/google-ads-creative-text-scraper`

- Two Actors, one library: video scripts in the first, headline/body/CTA/image OCR in the second.
  Run both for a complete Google answer.
- `maxAdvertisersPerName` defaults to 1 — an ambiguous brand name opens only the first matching
  advertiser entity. Raise it for brands with many Google entities, or search by `domains` instead.
- `region` filters the search, not the advertiser: a name with no entity in that region falls back to
  another region's entity and says so in the status line (measured: `"HelloFresh" has no US match —
  used HelloFresh SE (DE)`). Read that line before calling the result a US ad set.
- The text Actor's `formats` defaults to `["TEXT","IMAGE","VIDEO"]`; drop `VIDEO` when the video
  Actor is already covering it.

### `steadyfetch/media-transcriber`

- `urls` is required. `outputFormats` supports `text`, `segments`, `srt`, `vtt`; `language` defaults
  to `auto`.
- Priced per decoded audio minute, rounded up. Files that cannot be reached, cannot be decoded, or
  contain no speech are never charged.
- Cap with `maxMinutesPerItem` and `maxTotalMinutes` before pointing it at anything long.

## Reading the output honestly

Every row carries `status`, `charged` and, when something went wrong, `statusReason`.

**Do not filter on `charged`, and do not filter on one status string.** A repeat row — an ad the
account already had — is `charged: false` and still carries the full transcript (measured live:
`status: "transcribed"`, `charged: false`, `repeat: true`, a 1419-character `transcript`). And the
delivered status differs per Actor: `transcribed` on the four video Actors, `extracted` on
`steadyfetch/google-ads-creative-text-scraper`, `ok` on `steadyfetch/media-transcriber`, plus
`image_text_extracted` and `onscreen_text_extracted` for the non-speech delivery paths. Test the
content field itself — `transcript`, `imageText`, `onScreenText`, `rawText` — for non-null.

Most inapplicable fields come back as an explicit `null`, but a few (`repeat`, `onScreenText`) are
absent altogether when they do not apply, and which ones varies by Actor. `hook3s` is the first three seconds of
**speech**, and `hookStartSeconds` says at which second speech began — both `null` on an ad with no
speech at all, never an empty string. Do not report a `no_audio` row as a failed run; it is the
Actor declining to invent a transcript for a music-only creative.
