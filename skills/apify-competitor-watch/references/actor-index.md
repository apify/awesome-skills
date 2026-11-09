# Actor index — competitor watch

Inputs, outputs and chaining notes. Prices are Free-plan prices; each Actor's Store page shows the tier table for paid plans.

## sherwood/google-ads-transparency-scraper — Google Ads Transparency Scraper API

- **Store**: https://apify.com/sherwood/google-ads-transparency-scraper
- **Price**: `result` $0.0005 per ad creative delivered (or per advertiser row in advertiser mode); `ad-detail` $0.0005 per ad enriched with `includeDetails`, only when Google answered; Actor start $0.00005. Duplicates, errors and queries with no ad: free.
- **Input** (nothing required): `queries` (websites, brand names, advertiser IDs `AR` + 20 digits, or `adstransparency.google.com` advertiser or creative URLs; aliases `query` as a comma or newline separated string, `domains`, `advertiserIds`, `startUrls`; everything is merged), `region` (two-letter code, English country name, or `ANYWHERE`), `adFormat` (`ALL`, `TEXT`, `IMAGE`, `VIDEO`), `platforms` (`SEARCH`, `YOUTUBE`, `MAPS`, `PLAY`, `SHOPPING`; sent to Google, data exists for ads shown on or after 2023-09-04), `startDate` and `endDate` (`YYYY-MM-DD`; ads whose shown period overlaps the window; Google keeps 12 months of dates; one bound alone is completed), `maxAdsPerQuery` (default 100, 40 per page, no fixed cap), `maxAds` (default 1,000, whole run after de-duplication by `creativeId`), `includeDetails`, `resultType` (`ads` or `advertisers`), `proxyConfiguration`.
- **Output item, always**: `creativeId`, `advertiserId`, `advertiserName`, `domain` (domain searches only), `format`, `firstShown`, `lastShown`, `shownForDays`, `region`, `adUrl`, `previewType` (`image` or `rendered`), `imageUrl`, `previewUrl`, `width`, `height`, `query`, `queryAdsMin`, `queryAdsMax`, `status` (`ok`, `skipped`, `error`), `error`.
- **With `includeDetails`**: `advertiserLegalName`, `variationCount`, `variations[]`, `regionsShown[]` (per country: `firstShownDate`, `lastShownDate`, `firstShownOnOrBefore`, `impressionsMin`/`impressionsMax`, `platformImpressions[]`), `impressionsMin`, `impressionsMax`, `platformCodes`, `platforms`, `audienceSelection`, `adText`, `adHeadline`, `adDescription`, `headlines[]`, `displayUrl`, `landingPage`, `videoId`, `detailError`. Impressions, platform split and audience criteria exist only for ads shown in the EU. The text and landing-page fields are read from Google's preview bundle, so they are filled only when `previewType` is `rendered`; an ad served as a picture (`previewType: "image"`) keeps them `null` (test run on `qonto.com`, FR, 2026-11-09: 20 ads with details, 19 image previews, 1 rendered video ad with `landingPage` and `videoId`).
- **Advertiser mode** (`resultType: "advertisers"`): one item per advertiser account: `advertiserName`, `advertiserId`, `advertiserCountry`, `adsMin`, `adsMax`, `advertiserVerified`, `domain`, `runsGoogleAds`.
- **Not covered**: the Display Network (not part of the Transparency Center), the political-ads surface with spend ranges, shown dates older than 12 months.
- **Measured** (author's README): 16-case panel every run green; 100 % agreement with `scrapesage/google-ads-transparency-scraper` on advertiser name, format, dates, days shown and image URL over 91 common ads.

## scrapesage/google-ads-transparency-scraper — alternative (unaffiliated)

- **Store**: https://apify.com/scrapesage/google-ads-transparency-scraper
- **Price** (Free plan): $0.002 per ad, $0.003 per detail, $0.003 per advertiser, $0.002 per ad text.
- **When**: cross-check a surprising sherwood result, or when the user already has workflows on its field names.

## sherwood/trustpilot-reviews-scraper — Trustpilot Reviews Scraper API

- **Store**: https://apify.com/sherwood/trustpilot-reviews-scraper
- **Price**: `review-scraped` $0.0005 per review (Free plan; $0.0008 Starter, $0.0006 Scale, $0.0005 Business); Actor start $0.00005. Companies not on Trustpilot, companies without matching reviews, failed companies and duplicates: free.
- **Input** (nothing required): `companyUrls` (domains, website URLs, Trustpilot URLs from any country domain; aliases `companyUrl`, `domains`, `startUrls`, `urls`; a string with commas or new lines is split), `maxReviewsPerCompany` (default 20; up to 200 is one listing; above 200 or `0` goes through the deep path), `stars` (e.g. `["1", "2"]`), `languages` (ISO codes), `publishedAfter` (ISO date or datetime; strictly after; pagination stops at the boundary), `date` (`last30days`, `last3months`, `last6months`, `last12months`), `sort` (`recency`, `relevance`), `verifiedOnly`, `withReplies`, `includeCompanyInfo` (default true).
- **Output item** (one per review, `status: "ok"`): `reviewId`, `reviewUrl`, `title`, `text`, `rating`, `publishedDate`, `experienceDate`, `updatedDate`, `language`, `likes`, `verificationLevel`, `isVerified`, `source`, `authorReviewCount`, `country`, `replyMessage` (first-name greeting masked), `replyPublishedDate`, `replyUpdatedDate`, `companyName`, `companyDomain`, `companyTrustScore`, `companyStars`, `companyTotalReviews`, `companyCategories`, `companyUrl`, `error`, `input`. A company with no review gives one item with `status` `notfound`, `empty` or `error`, never charged. No reviewer name, avatar or profile link.
- **Measured** (2026-11-09, `qonto.com`): 50 newest reviews in 20 s; incremental run with `publishedAfter` and `maxReviewsPerCompany: 0` returned the 19 reviews published since the boundary in 33 s, none older.
- **Limits**: 200 reviews per public listing, then the deep path (92–97 % of all reviews on companies with 1,700–3,500 reviews, measured 2026-11-08; the most recent few thousand plus the last 12 months on very large companies); AWS WAF challenge solved by a headless browser every five minutes, a changed challenge gives `status: "error"` items.
- **Chain out**: `defaultDatasetId` → `sherwood/review-analyzer` (`datasetId`); field names detected (the review title is kept in front of the text, `replyMessage` is read as the owner reply, `companyCategories` picks the themes).

## memo23/trustpilot-scraper-ppe — alternative (unaffiliated)

- **Store**: https://apify.com/memo23/trustpilot-scraper-ppe
- **Price**: from $0.00065 per review (Store title: "$0.65+ · No Cap").
- **When**: the user already uses it, or to cross-check a count. `sherwood/review-analyzer` reads its dataset too.

## sherwood/review-analyzer — Review Analyzer API

- **Store**: https://apify.com/sherwood/review-analyzer
- **Price**: `review-analyzed` $0.001 per review with a text (all plans); reviews without text and failures free; Actor start $0.00005.
- **Input** (nothing required): `datasetId` (tested on `sherwood/trustpilot-reviews-scraper`, `memo23/trustpilot-scraper-ppe`, `compass/Google-Maps-Reviews-Scraper`, `compass/crawler-google-places` with `maxReviews`, `maxcopell/tripadvisor-reviews`, `voyager/booking-reviews-scraper`, `tri_angle/yelp-review-scraper`) or `reviews` (strings or objects); field overrides `textField`, `ratingField`, `dateField`, `replyField`, `placeIdField`, `placeNameField`, `categoryField`; `businessType` (`auto`, `restaurant`, `hotel`, `health`, `trades`, `beauty`, `professional`, `retail`, `generic`), `themes` (`"name: definition"`), `maxReviews` (default 500), `maxReviewsPerPlace` (default 100), `includeReviewText`.
- **Output item** (one per company): `placeId` (`null` for Trustpilot, which has no place id; filled from Google Maps datasets), `placeName`, `category`, `businessType`, `reviewsAnalyzed`, `reviewsWithoutText`, `averageRating`, `positive`, `mixed`, `negative`, `negativeShare`, `recentNegativeShare`, `olderNegativeShare` (`null` when every review is less than 90 days old), `ownerReplyRate`, `unansweredComplaints`, `unansweredComplaintUrls[]`, `languages` (count per language code), `strengths[]`, `weaknesses[]` (`theme`, `mentions`), `alerts[]` (`date`, `rating`, `severity`, `excerpt`, `url`), `summary`, `reviews[]` (`reviewId`, `reviewUrl`, `reviewDate`, `reviewRating`, `reviewLanguage`, `reviewText`, `sentiment`, `sentimentConfidence`, `severity`, `severityLabel`, `needsReply`, `ownerReplied`, `recommendation`, `praised[]`, `criticized[]`). Reviewer names are never read or copied.
- **Weekly use**: analyze only the new reviews (the incremental Trustpilot dataset); keep last week's analysis file to compare `weaknesses` and `negativeShare`.

## compass/Google-Maps-Reviews-Scraper — Google reviews of locations (unaffiliated)

- **Store**: https://apify.com/compass/Google-Maps-Reviews-Scraper
- **Price** (Free plan): $0.0006 per review; Actor start $0.00005.
- **Input**: `placeIds` (27-character `ChIJ...` ids) or `startUrls` (Maps place URLs), `maxReviews` (per place; set it, the default is every review), `reviewsSort: "newest"`, `reviewsStartDate` (absolute or relative, e.g. `7 days`), `language`, `personalData`.
- **When**: the competitor is a chain, a franchise or a local business whose customers review on Google rather than Trustpilot. Its dataset goes straight into `sherwood/review-analyzer`, grouped per location by `placeId`.

## sherwood/youtube-transcript-batch — YouTube Transcript API

- **Store**: https://apify.com/sherwood/youtube-transcript-batch
- **Price**: `transcript-fetched` $0.001 per transcript saved, whatever the video length (Free plan; $0.0015 Starter, $0.0012 Scale, $0.001 Business); Actor start $0.00005. Skipped videos (no captions, unavailable, age-restricted) and failed requests: free.
- **Input** (nothing required): `videoUrls` (video URLs incl. Shorts, live and embed, bare 11-character IDs, channel URLs or `@handles`, playlist URLs; a string is split on commas and new lines; aliases `videoUrl`, `urls`, `startUrls`, `youtube_url`, `videoIds`, `channel`, `playlist`), `languages` (ISO 639-1 codes in order of preference; manual track before auto-generated), `transcriptType` (`any`, `manual`, `generated`), `translateTo` (best effort; YouTube rate-limits it), `outputFormats` (`json` → `timestamped`, `text` → `non_timestamped`, `srt`, `vtt`), `includeMetadata` (default true, free), `maxVideosPerSource` (default 100, up to 5,000; newest first), `maxVideos` (default 1,000), `datasetId` + `urlField` (transcribe the videos listed by another Actor).
- **Output item** (field names of the most used YouTube transcript Actor): `url`, `video_id`, `source` (the channel or playlist entry it came from), `title`, `channel_name`, `channel_id`, `channel_url`, `video_duration_seconds`, `view_count`, `thumbnail_url`, `was_live`, `language`, `language_code`, `is_generated`, `is_translatable`, `translation_languages`, `translated_to`, `translation_error`, `source_type`, `snippet_count`, `total_seconds`, `duration_human`, `timestamped[]` (`text`, `start`, `duration`), `non_timestamped`, `srt`, `vtt` (the formats not requested in `outputFormats` are present but `null`), `available_transcripts[]`, `note`, `status` (`ok`, `skipped`, `error`), `success`, `error`, `error_type` (`TranscriptsDisabled`, `NoTranscriptFound`, `VideoUnavailable`, `AgeRestricted`, `PoTokenRequired`, `BotCheck`, `RateLimited`, `RequestFailed`), `timestamp`.
- **Limits**: caption tracks only (no speech-to-text); the channel listing reads the Videos tab, not Shorts or live tabs (use a playlist URL); items capped at 9 MB by Apify (very long videos lose `srt`/`vtt`, then segments, `non_timestamped` kept).

## streamers/youtube-scraper — video and channel statistics (unaffiliated)

- **Store**: https://apify.com/streamers/youtube-scraper
- **Price**: pay per event, per result (see the Store page).
- **When**: the user wants likes, comment counts, publish dates or subscriber counts next to the transcripts. Run it on the channel URL, then pass its `defaultDatasetId` to `sherwood/youtube-transcript-batch` as `datasetId` (video URL found among `url`, `videoUrl`, `id`...), so both datasets share `video_id` / `id` for the join.

## Chaining and scheduling

```
sherwood/google-ads-transparency-scraper ──────────────────────────────► ads.json  (diff on creativeId)
sherwood/trustpilot-reviews-scraper ──datasetId──► sherwood/review-analyzer ──► reviews.json + reviews-analysis.json
sherwood/youtube-transcript-batch ─────────────────────────────────────► videos.json (diff on video_id)
```

- One Apify schedule per Actor (or per saved task holding the competitor's inputs), weekly, same weekday.
- On the Trustpilot scraper's **Integrations** tab, add `sherwood/review-analyzer` with `{"datasetId": "{{resource.defaultDatasetId}}"}` so the analysis follows every scrape.
- Incremental inputs to update each week: `startDate` (ads, the previous run date), `publishedAfter` (Trustpilot, the newest `publishedDate` saved), `maxVideosPerSource` (a little more than the channel's weekly output).
