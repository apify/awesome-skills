---
name: apify-ad-creative-transcripts
description: Turn a competitor's ad creative into text — the full spoken transcript, the first-3-seconds hook with the second it starts, the CTA, and the words baked into image ads — across the Meta (Facebook & Instagram) Ad Library, the TikTok Creative Center, the LinkedIn Ad Library and the Google Ads Transparency Center. Works from a keyword or advertiser search, from pasted ad links, or by chaining the dataset of an ad-library scraper you already ran. Use when the user asks what a competitor actually says in their ads, wants ad transcripts, ad scripts, opening lines, hooks, VSL or UGC script teardowns, wants to know which angle or offer a brand is testing, asks to transcribe ad videos in bulk, read the text on image ads, build a swipe file of ad copy from video creative, compare hooks across platforms, or wants a scheduled watch that transcribes only the ads a competitor launched since the last run. Pair it with apify-ads-intelligence, which finds which ads exist; this skill reads what they say.
author: Steadyfetch
author_url: https://github.com/steadyfetch
metadata:
  category: data-extraction
  keywords: "ad-transcripts, ad-creative, hooks, video-ads, ad-library, meta-ad-library, facebook-ads, tiktok-creative-center, linkedin-ad-library, google-ads-transparency, creative-intelligence, swipe-file, ad-copy, speech-to-text, ocr, competitor-ads, watchlist"
---

# Ad Creative Transcripts

Read what a competitor's ads **say**, not just which ads they run: full speech transcripts, the
first-3-seconds hook, the CTA, and the text inside image creatives — Meta, TikTok, LinkedIn and
Google, one JSON row per ad.

**Author:** Steadyfetch. **Disclosure:** the `steadyfetch/*` Actors this skill routes to are paid,
pay-per-event Apify Actors built and published by the author. No affiliate or referral parameters
appear anywhere in this skill — every link is a plain Apify Store URL.

**CLI rules:** every `apify` command below carries `--user-agent apify-awesome-skills/apify-ad-creative-transcripts`,
`--json` (or `--format json` on `datasets get-items`) and `2>/dev/null`. Never drop the user-agent.

## Where this sits next to `apify-ads-intelligence`

They answer different halves of the same question and are meant to be chained, not swapped.

| Question | Skill |
|---|---|
| *Which* ads is this brand running, since when, to which landing page? | `apify-ads-intelligence` |
| *What do those ads say* — script, hook, CTA, on-image text? | this skill |
| Both, in one pass | run `apify-ads-intelligence` first, then pass its `defaultDatasetId` into the `datasetId` field here |

If the user only needs ad counts, advertisers or landing-page domains, stay in
`apify-ads-intelligence` — this skill charges per transcript and would be the expensive way to
answer a metadata question.

## Example prompts

Prompts this skill handles:

- "What hook does HelloFresh open its Facebook video ads with right now?"
- "Transcribe the top TikTok ads in the US from the last 7 days and group them by opening line."
- "Watch these five LinkedIn advertisers weekly and only transcribe ads that are new since last time."
- "I already scraped the Meta Ad Library — here's the dataset ID, give me every script."

Out of scope (the boundary):

- "Which ads is Nike running, and where do they click through to?" — that is a metadata question.
  Use `apify-ads-intelligence`, then bring its dataset ID back here if the wording matters.
- Organic social content (a brand's regular posts, Reels, YouTube uploads, podcasts). This skill is
  about paid creative from public ad libraries. A one-off media URL can go through
  `steadyfetch/media-transcriber`, but discovering organic content is another skill's job.

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
- [ ] Step 1: Pick the entry mode (search here, or chain a dataset you already have)
- [ ] Step 2: Route to the platform Actor
- [ ] Step 3: Fetch the input schema before building input
- [ ] Step 4: Set the cost ceiling BEFORE the run
- [ ] Step 5: Run, then fetch the dataset
- [ ] Step 6: Answer with hooks and scripts, and report what did not deliver
```

### Step 1: Pick the entry mode

Every Actor here takes four kinds of input. Pick one — they compose, but one is usually right.

| The user has… | Field to use | Notes |
|---|---|---|
| A brand name, advertiser or keyword | `searchQueries` (Meta), `accountOwners` / `keywords` (LinkedIn), `advertisers` / `domains` (Google), `discoverRegion` (TikTok) | The Actor searches the ad library itself. Finding ads is not charged; only delivered transcripts are. |
| Ad links copied from an ad library | `adLibraryUrls` (Meta), `videoUrls` (all) | Fastest path when the user already picked the ads. |
| A dataset from an ad-library scraper they already ran | `datasetId` | The chaining path — see the `apify-ads-intelligence` note above. |
| Rows pasted from somewhere else | `datasetItems` | Array of raw JSON rows. |

Nothing at all set = a small live sample run (3 ads on the ad Actors) that is charged like any other
run. Say so before pressing Start on a user's account; do not use a bare run as a "free preview".

### Step 2: Route to the platform Actor

| Platform / user need | Actor | Search input | Price per delivered result |
|---|---|---|---|
| Meta — Facebook & Instagram Ad Library, video **and** image ads | `steadyfetch/facebook-ads-transcript-scraper` | `searchQueries`, `country`, `mediaType`, `activeStatus` | $0.020 free plan → $0.010 top plans |
| TikTok — Creative Center top ads | `steadyfetch/tiktok-ads-transcript-scraper` | `discoverRegion`, `discoverIndustry`, `discoverPeriod`, `discoverSort` | $0.020 → $0.008 |
| LinkedIn — Ad Library, video + image ads | `steadyfetch/linkedin-ads-transcript-scraper` | `accountOwners`, `keywords`, `countries`, `dateOption` | $0.020 → $0.008 |
| Google — Transparency Center **video** ads | `steadyfetch/google-ads-video-transcript-scraper` | `advertisers`, `domains`, `region` | $0.020 → $0.008 |
| Google — Transparency Center **text & image** creatives (headline, body, CTA, image OCR) | `steadyfetch/google-ads-creative-text-scraper` | `advertisers`, `domains`, `formats`, `region` | $0.015 free plan; paid plans lower — read it live, a change lands 2026-09-15 |
| Any other media URL (a podcast, a landing-page video, a file) | `steadyfetch/media-transcriber` | `urls` | $0.003 per audio minute |

All six are `PAY_PER_EVENT`, all charge **only on delivery**, and platform usage is included in the
event price (no start fee, no separate compute bill). Prices read from the live pricing tabs on
2026-09-07 — re-check with `apify actors info` before quoting them to a user.

Google splits across two Actors on purpose: the Transparency Center carries a lot of text and image
creative, and a "what are they saying" question is only half answered by the video ads. Run both for
a full Google picture; run only the video one if the user asked about scripts.

### Step 3: Fetch the input schema before building input

Do not guess field names — they differ per platform (`maxAds` on Meta and TikTok, `maxItems` on
LinkedIn and Google video, `maxCreativesPerAdvertiser` on Google text).

```bash
apify actors info "steadyfetch/facebook-ads-transcript-scraper" --input \
  --user-agent apify-awesome-skills/apify-ad-creative-transcripts 2>/dev/null

apify actors info "steadyfetch/facebook-ads-transcript-scraper" --readme \
  --user-agent apify-awesome-skills/apify-ad-creative-transcripts
```

### Step 4: Set the cost ceiling BEFORE the run

Two independent ceilings. Use both.

**a) The Actor's own cap** — cheapest and always available:

| Actor | Cap field | Default |
|---|---|---|
| `steadyfetch/facebook-ads-transcript-scraper` | `maxAds` (+ `searchMaxAds` per keyword) | 1000 (25 per keyword) |
| `steadyfetch/tiktok-ads-transcript-scraper` | `maxAds` (+ `discoverMaxAds`) | 1000 (20 discovered) |
| `steadyfetch/linkedin-ads-transcript-scraper` | `maxItems` | 1000 |
| `steadyfetch/google-ads-video-transcript-scraper` | `maxItems` | 100 |
| `steadyfetch/google-ads-creative-text-scraper` | `maxCreativesPerAdvertiser` | 30 |
| `steadyfetch/media-transcriber` | `maxTotalMinutes`, `maxMinutesPerItem` | 0 (unlimited) |

**b) A hard dollar cap.** `apify actors call` has **no** cost-cap flag — checked against apify-cli
1.6.2 and the [CLI reference](https://docs.apify.com/cli/docs/reference#apify-actors-call), whose
`call` and `start` flags are only `--build`, `--input`, `--input-file`, `--json`, `--memory`,
`--output-dataset`, `--silent`, `--timeout`. A dollar ceiling has to be set on the API call, where
`maxTotalChargeUsd` is a documented query parameter of
[`POST /v2/acts/{actorId}/runs`](https://docs.apify.com/api/v2/act-runs-post):

```bash
curl -sS -X POST \
  "https://api.apify.com/v2/acts/steadyfetch~facebook-ads-transcript-scraper/runs?maxTotalChargeUsd=2&waitForFinish=300" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"searchQueries":["hellofresh"],"country":"US","maxAds":50}'
```

These Actors set a minimum accepted ceiling of **$0.05**; a smaller value is rejected. When the cap
is reached the run does not silently truncate — every remaining ad still ships as its own uncharged
`skipped_budget` row carrying the ad's identity, so you can raise the cap and re-run exactly those.

Thresholds to apply on the user's behalf: estimate before running, warn above **$5**, ask for
explicit confirmation above **$20**, and always present the number as an estimate. Estimate =
`delivered ads × per-result price` + `$0.005 × started minutes beyond the first 3 per video ad`.

### Step 5: Run, then fetch the dataset

```bash
apify actors call "steadyfetch/facebook-ads-transcript-scraper" \
  -i '{"searchQueries":["hellofresh"],"country":"US","mediaType":"video","activeStatus":"active","searchMaxAds":25,"maxAds":25}' \
  --user-agent apify-awesome-skills/apify-ad-creative-transcripts \
  --json 2>/dev/null
```

Take `.id`, `.status` (want `SUCCEEDED`) and `.defaultDatasetId` from the output, then:

```bash
apify datasets get-items DATASET_ID --format json \
  --user-agent apify-awesome-skills/apify-ad-creative-transcripts 2>/dev/null > ads.json
```

`apify datasets get-items` streams over the network every time, so save the file once and analyse
from disk instead of re-piping it into `jq` per query. A hook table from the saved file:

```bash
jq -r '.[] | select(.transcript != null) | [.pageName, (.hookStartSeconds|tostring), .hook3s] | @tsv' ads.json
```

**Filter on the content field, not on `charged` and not on one status string.** Two traps, both
measured on live runs:

- `charged: false` does **not** mean empty. An ad the account already had comes back as a *repeat*
  row — `repeat: true`, `charged: false`, `firstSeenRunId` naming the earlier run — carrying the
  **full transcript**. Filtering on `charged` throws that content away, and on any re-run or
  watchlist schedule most rows are repeats. Use `charged` for cost accounting only.
- The delivered `status` differs by Actor and by creative: `transcribed` on the four video Actors,
  `extracted` on `steadyfetch/google-ads-creative-text-scraper`, `ok` on
  `steadyfetch/media-transcriber`, plus `image_text_extracted` (an image ad read by OCR) and
  `onscreen_text_extracted` (a silent video read from the screen).

So: test the field you actually want — `transcript`, `imageText`, `onScreenText` or `rawText` — for
non-null. Confirm real field names on a new dataset before writing further queries:

```bash
apify datasets get-items DATASET_ID --limit 1 --format json \
  --user-agent apify-awesome-skills/apify-ad-creative-transcripts 2>/dev/null | jq '.[0]'
```

### Step 6: Answer with hooks and scripts, and report what did not deliver

Synthesise, do not dump. Useful shapes:

| The user asked | Lead with |
|---|---|
| "what's their hook" | The `hook3s` of each ad, sorted by `hookStartSeconds` — a high value means the ad makes you wait for the pitch |
| "what are they testing" | Clusters of near-identical opening lines, and where the scripts diverge |
| "give me their scripts" | Full `transcript` per ad with `ctaText` and `durationSeconds` beside it |
| "what changed this week" | Rows with `isNew: true`, against `firstSeenAt` on the rest |

Always close with the honest count: *N delivered and charged, M returned uncharged* (and why — see
the status table below). Silent ads and expired links are normal, not a failed run.

## Recipes

### A — One competitor, one platform

`searchQueries: ["<brand>"]`, `country`, `maxAds: 25`. Deliver a hook table plus the two or three
full scripts that carry the offer.

### B — Cross-platform hook audit

Run Meta, TikTok, LinkedIn and Google video in parallel — background each call with `&`, then `wait`
— and merge on advertiser. What this reveals that a metadata audit cannot: the same offer told four
different ways, and which platform gets the strongest opening line.

```bash
apify actors call "steadyfetch/facebook-ads-transcript-scraper" -i '{"searchQueries":["<brand>"],"maxAds":15}' \
  --user-agent apify-awesome-skills/apify-ad-creative-transcripts --json 2>/dev/null > meta_run.json &
apify actors call "steadyfetch/tiktok-ads-transcript-scraper" -i '{"discoverRegion":"US","discoverPeriod":"30","discoverMaxAds":15}' \
  --user-agent apify-awesome-skills/apify-ad-creative-transcripts --json 2>/dev/null > tiktok_run.json &
apify actors call "steadyfetch/linkedin-ads-transcript-scraper" -i '{"accountOwners":["<brand>"],"maxItems":15}' \
  --user-agent apify-awesome-skills/apify-ad-creative-transcripts --json 2>/dev/null > linkedin_run.json &
apify actors call "steadyfetch/google-ads-video-transcript-scraper" -i '{"advertisers":["<brand>"],"region":"US","maxItems":15}' \
  --user-agent apify-awesome-skills/apify-ad-creative-transcripts --json 2>/dev/null > google_run.json &
wait
```

### C — A weekly watch that only pays for new ads

This is the mode that makes recurring creative research affordable, and the one to reach for whenever
the user says "track", "monitor", "weekly" or "since last time".

1. Name a watchlist: `"watchlistId": "acme-competitors"`.
2. Turn on `"newAdsOnly": true`.
3. Save it as an Apify **Task** and give the Task a schedule.

Each later run delivers only the ads that list has never answered — ads already on it are dropped
before anything is downloaded, so they are not fetched, not transcribed and not charged. New rows
carry `isNew: true` and `firstSeenAt`. The list lives in a key-value store **in the user's own Apify
account** (`fb-ads-watch-<name>` on Meta, one per platform); deleting that store starts the history
over. Watching 20 advertisers daily costs only the handful of ads they launched overnight.

Independently of any watchlist, each Actor remembers every ad it has already delivered to that
account: re-running the same links returns those ads with `repeat: true`, `firstSeenRunId` and
`charged: false`. Entries older than 90 days stop counting as repeats. The no-input sample run is the
one exception — it always runs live and is charged again.

### D — Chained from a scraper the user already ran

```bash
apify actors call "steadyfetch/facebook-ads-transcript-scraper" \
  -i '{"datasetId":"<dataset id of any Facebook Ad Library scraper run>","maxAds":100}' \
  --user-agent apify-awesome-skills/apify-ad-creative-transcripts \
  --json 2>/dev/null
```

Works after any Meta ad-library scraper — for example `apify/facebook-ads-scraper` or
`curious_coder/facebook-ads-library-scraper`, the Actors `apify-ads-intelligence` routes to. The same
`datasetId` field exists on the LinkedIn and both Google Actors for their own libraries.

## Output fields

One row per ad. Every row carries `status`, `charged` and `statusReason`; a field that does not apply
to a given creative is usually an explicit `null`, but a few (`repeat`, `onScreenText`) are simply
absent when they do not apply — read them with `// null` / `?` rather than assuming the key exists.

| Actor | Key fields |
|---|---|
| `steadyfetch/facebook-ads-transcript-scraper` | `status`, `charged`, `isNew`, `firstSeenAt`, `pageName`, `searchQuery`, `hook3s`, `hookStartSeconds`, `ctaText`, `ctaType`, `adText`, `transcript`, `segments`, `language`, `imageText`, `durationSeconds`, `adArchiveId`, `videoUrl`, `imageUrl`, `statusReason` (+ `onScreenText` when on-screen reading is on, `repeat` on a re-run) |
| `steadyfetch/tiktok-ads-transcript-scraper` | `brandName`, `adTitle`, `hook3s`, `hookStartSeconds`, `transcript`, `segments`, `language`, `ctr`, `likes`, `industryKey`, `objectiveKey`, `durationSeconds`, `materialId`, `videoUrl`, `urlExpiresAt` + the common status fields (+ `onScreenText` when on-screen reading is on) |
| `steadyfetch/linkedin-ads-transcript-scraper` | `advertiser`, `payingEntity`, `hook3s`, `hookStartSeconds`, `transcript`, `segments`, `language`, `imageText`, `onScreenText`, `headline`, `adText`, `ctaText`, `format` (e.g. `SPONSORED_VIDEO`), `impressions`, `impressionsByCountry`, `availability`, `adId`, `detailUrl`, `videoUrl`, `posterUrl`, `imageUrl`, `repeat`, `firstSeenRunId` + the common status fields |
| `steadyfetch/google-ads-video-transcript-scraper` | `advertiserName`, `title`, `hook3s`, `hookStartSeconds`, `transcript`, `segments`, `language`, `transcriptSource`, `durationSeconds`, `videoId`, `videoUrl`, `creativeId`, `repeat`, `firstSeenRunId` + the common status fields |
| `steadyfetch/google-ads-creative-text-scraper` | `advertiserName`, `advertiser`, `advertiserId`, `creativeId`, `format`, `headline`, `body`, `cta`, `displayUrl`, `rawText`, `screenshotUrl`, `firstShown`, `lastShown`, `isNew`, `firstSeenAt` + the common status fields |
| `steadyfetch/media-transcriber` | `title`, `siteName`, `sourceType`, `durationSeconds`, `language`, `wordCount`, `text`, `chargedMinutes`, `url`, `note` |

`hook3s` is the ad's first three seconds of **speech**, not of runtime: creatives that open on music
or a logo sting are common, so when nothing is said up front the hook is taken from wherever speech
actually starts and `hookStartSeconds` names that second (`0` when the ad opens talking). An ad with
no speech at all leaves both `null` — never an empty string, so "opens silent" and "we lost the
opening" cannot be confused.

## Reading rows that did not deliver

A row with `charged: false` is an answer, not an error — its `status` says what the creative was. The common
ones, with what to do about each:

| `status` | Meaning | Action |
|---|---|---|
| `no_audio` / `no_speech` | Music-only or genuinely silent creative — the Actors return an honest uncharged row instead of the filler text speech models hallucinate over music | Re-run with `"includeOnScreenText": true` to read the words on screen instead |
| `no_onscreen_text` | Silent ad with nothing readable on screen either | Nothing to recover; report it as a silent creative |
| `ocr_no_text_found` | Plain photo with no text | Expected on image-heavy accounts |
| `unavailable_expired` / `image_expired` | The library's signed media link went stale, usually in a chained dataset | Re-run the upstream scraper for fresh URLs, or search directly here so the link and the media are read in one run |
| `skipped_budget` / `skipped_deadline` | Your cost cap or run timeout hit before this ad's turn | Raise the cap or the timeout and re-run those rows; the identity is in the row |
| `search_no_results` | The keyword matched no live ads this minute | Widen the keyword, the country, or set `activeStatus: "all"` |
| `search_blocked` / `asr_unavailable` | Transient upstream refusal; the row is marked `retryable` | Re-run later; nothing was charged |
| `failed_download` / `failed_processing` | The file could not be fetched or finished in time | Re-run; for long videos raise run memory, which also raises CPU |
| `sample_note` | You set options but named no ads, so the default sample ran under your settings | Provide a keyword, link or dataset |

None of these are charged.

## Quirks

- **Meta searches by keyword, not by page URL.** Put the brand in `searchQueries`; paste Ad Library
  links into `adLibraryUrls` if the user already has them.
- **`mediaType` defaults to `video` and `activeStatus` to `active`.** A user asking "everything they
  have ever run" needs `"mediaType":"all"` and `"activeStatus":"all"` — and should be warned that
  this multiplies the charged rows.
- **TikTok discovery is region-first**, not brand-first: it pulls the Creative Center's top ads for a
  region (`US`, `GB`, `DE`, `FR`, `BR`, …), optionally an industry, over `7` / `30` / `180` days,
  ranked `for_you` / `ctr` / `like`. To transcribe one specific brand's TikTok ads, supply
  `videoUrls` or `materialIds` instead of discovering.
- **Most LinkedIn ads are static images.** The Actor spots the video creatives before opening them,
  reads image ads with OCR (`includeImageText`, on by default), and only charges for what it
  delivers. `dateOption` takes `last-30-days`, `current-month`, `current-year`, `last-year` or
  `custom-date-range`; `countries` accepts codes or names.
- **Long videos cost extra, they do not fail.** Three minutes of each video are included; beyond that
  it is $0.005 per started minute. A 7-minute VSL adds four. Images never carry the surcharge.
- **On-screen text is opt-in** (`includeOnScreenText`, default `false`) on the video Actors. Turn it
  on for kinetic-typography and silent creative; leave it off and those ads come back uncharged.
- **Google needs both Actors for full coverage** — video scripts in one, text and image creative in
  the other. `maxAdvertisersPerName` defaults to 1, so an ambiguous brand name opens only the first
  matching advertiser; raise it when the user names a brand with many Google advertiser entities.
- **`region` does not pin the advertiser on Google.** A name with no advertiser entity in the region
  you asked for falls back to another region's entity and says so in the run's status line
  (measured: `"HelloFresh" has no US match — used HelloFresh SE (DE)`). Read that line back to the
  user before presenting the ads as that market's, or search by `domains` instead of by name.
- **`media-transcriber` is per audio minute, not per item.** A 60-minute file is 60 charged minutes.
  Cap it with `maxMinutesPerItem` / `maxTotalMinutes` before running anything long.

## Error handling

- Auth error → `apify login`, or set `APIFY_TOKEN`
- `Actor not found` → check the id against the routing table; all six are `steadyfetch/<name>`
- Run status `FAILED` → open the console URL from the run metadata and read the log
- Zero rows → the search matched nothing; widen keyword, country or date range, or switch
  `activeStatus` to `all`
- Every row uncharged with `no_audio` → the creatives are silent; re-run with
  `"includeOnScreenText": true`
- Cost cap rejected → the minimum `maxTotalChargeUsd` on these Actors is `0.05`
- Run hits the time limit on long videos → raise memory with `--memory` (more memory buys more CPU)
  or split the batch
- Chained dataset gives expired media → re-run the upstream scraper, or search directly here

For the full routing table and the cost guardrails in one place, see
[references/actor-index.md](references/actor-index.md) and [references/gotchas.md](references/gotchas.md).
