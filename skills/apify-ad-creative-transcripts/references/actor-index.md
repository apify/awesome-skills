# Actor index — ad creative transcripts

The full routing table. Read this after `SKILL.md` when the platform or the input mode is not
obvious. Every Actor listed is public on the Apify Store.

**Disclosure:** the `steadyfetch/*` Actors are paid, pay-per-event Actors built and published by this
skill's author. Third-party Actors are listed only as upstream sources you can chain from.

## The six routing targets

| Platform | User intent | Actor | Tier | Notes |
|---|---|---|---|---|
| Meta (Facebook + Instagram) | Transcribe Ad Library video ads; read the text on image ads | `steadyfetch/facebook-ads-transcript-scraper` | community | Keyword/advertiser search built in. `mediaType` defaults to `video`, `activeStatus` to `active` |
| TikTok | Transcribe Creative Center top ads for a market | `steadyfetch/tiktok-ads-transcript-scraper` | community | Discovery is region-first, not brand-first. Supply `videoUrls` / `materialIds` for one brand |
| LinkedIn | Transcribe Ad Library video ads; OCR the image ads | `steadyfetch/linkedin-ads-transcript-scraper` | community | Most LinkedIn ads are static images; `includeImageText` is on by default |
| Google | Transcribe Transparency Center **video** ads | `steadyfetch/google-ads-video-transcript-scraper` | community | Search by advertiser name or by domain |
| Google | Extract Transparency Center **text and image** creative | `steadyfetch/google-ads-creative-text-scraper` | community | `formats` defaults to `["TEXT","IMAGE","VIDEO"]`; returns `headline`, `body`, `cta`, `rawText` |
| Anything else | Transcribe an arbitrary media URL | `steadyfetch/media-transcriber` | community | Priced per audio minute, not per item. `outputFormats` supports `text`, `segments`, `srt`, `vtt` |

## Input fields by Actor

| Actor | Search inputs | Paste inputs | Chain inputs | Cap | Repeat-run controls |
|---|---|---|---|---|---|
| `steadyfetch/facebook-ads-transcript-scraper` | `searchQueries`, `country`, `mediaType`, `activeStatus`, `searchMaxAds` | `adLibraryUrls`, `videoUrls` | `datasetId`, `datasetItems` | `maxAds` | `watchlistId`, `newAdsOnly` |
| `steadyfetch/tiktok-ads-transcript-scraper` | `discoverRegion`, `discoverIndustry`, `discoverPeriod`, `discoverSort`, `discoverMaxAds` | `videoUrls`, `materialIds` | `datasetId`, `datasetItems` | `maxAds` | `watchlistId`, `newAdsOnly` |
| `steadyfetch/linkedin-ads-transcript-scraper` | `accountOwners`, `keywords`, `countries`, `dateOption`, `startdate`, `enddate`, `payer`, `impressionsMin`, `impressionsMax` | `videoUrls` | `datasetId`, `datasetItems` | `maxItems` | `watchlistId`, `newAdsOnly` |
| `steadyfetch/google-ads-video-transcript-scraper` | `advertisers`, `domains`, `region`, `maxAdvertisersPerName` | `videoUrls` | `datasetId`, `datasetItems` | `maxItems` | `watchlistId`, `newAdsOnly` |
| `steadyfetch/google-ads-creative-text-scraper` | `advertisers`, `domains`, `formats`, `region`, `maxAdvertisersPerName` | — | `datasetId`, `datasetItems` | `maxCreativesPerAdvertiser` | `watchlistId`, `newCreativesOnly` |
| `steadyfetch/media-transcriber` | — | `urls` (required) | `datasetId`, `datasetItems` | `maxMinutesPerItem`, `maxTotalMinutes` | — |

Optional reading toggles on the ad Actors: `includeImageText` (Meta, LinkedIn — on by default) reads
the words inside image creatives; `includeOnScreenText` (Meta, TikTok, LinkedIn — off by default)
reads on-screen text on silent video ads; `includeNonVideo` (LinkedIn) passes documents, carousels
and text-only creatives through as uncharged rows.

## Upstream Actors you can chain from

Pass any of these runs' `defaultDatasetId` into the matching transcript Actor's `datasetId`. They
find the ads; the transcript Actor reads them. These are the Actors `apify-ads-intelligence` routes
to, which makes that skill's output a direct input here.

| Library | Upstream Actor | Feeds |
|---|---|---|
| Meta Ad Library | `apify/facebook-ads-scraper` | `steadyfetch/facebook-ads-transcript-scraper` |
| Meta Ad Library | `curious_coder/facebook-ads-library-scraper` | `steadyfetch/facebook-ads-transcript-scraper` |
| LinkedIn Ad Library | `silva95gustavo/linkedin-ad-library-scraper` | `steadyfetch/linkedin-ads-transcript-scraper` |
| Google Ads Transparency | `solidcode/ads-transparency-scraper` | both Google Actors |

Chained media links can be short-signed and go stale. If a chained run returns
`unavailable_expired` / `image_expired` rows, re-run the upstream scraper for fresh URLs, or search
directly in the transcript Actor so the link and the media are read in the same run.

## How to extend

1. Search for candidates:

   ```bash
   apify actors search "ad library transcript" --limit 20 \
     --user-agent apify-awesome-skills/apify-ad-creative-transcripts --json 2>/dev/null
   ```

2. Fetch the input schema:

   ```bash
   apify actors info "ACTOR_ID" --input \
     --user-agent apify-awesome-skills/apify-ad-creative-transcripts 2>/dev/null
   ```

3. Add a row above with the user intent that should trigger it.
