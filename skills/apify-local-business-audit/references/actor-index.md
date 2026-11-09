# Actor index — local business audit

Inputs, outputs and chaining notes for the four Actors. Prices are Free-plan prices; each Actor's Store page shows the tier table for paid plans.

## sherwood/google-maps-scraper — Google Maps Scraper API (places, leads, AI verdicts)

- **Store**: https://apify.com/sherwood/google-maps-scraper
- **Price**: `place-scraped` $0.0005 per unique place (Free plan; $0.0015 Starter, $0.00125 Scale, $0.001 Business). `place-qualified` $0.001 per place judged by the AI model. `contacts-found` $0.001 per place whose website gave at least one email or social profile. Duplicates, places beyond the run budget, websites with no contact: free.
- **Input** (nothing required): `searchStringsArray` (aliases `query`, `queries`, `search`, `searchTerms`, `keywords`; a string with commas or new lines is split), `locationQuery` (alias `location`; leave empty when the term names the place), `maxCrawledPlacesPerSearch` (default 50, Google stops around 120), `maxPlaces` (default 1,000), `language`, `qualifyPlaces`, `idealCustomer` (one sentence → `idealCustomerFit`), `customQuestions` (up to 5: `{"id": "terrace", "question": "Outdoor terrace?"}`, with `options` for a choice, `"type": "scale"` for ordered levels), `scrapeContacts`, `datasetId` (qualify an existing Maps dataset instead of searching), `proxyConfiguration`.
- **Output item** (field names of `compass/crawler-google-places`): `searchString`, `rank`, `title`, `description`, `categoryName`, `categories`, `address`, `street`, `city`, `postalCode`, `state`, `countryCode`, `website`, `phone`, `phoneUnformatted`, `totalScore`, `reviewsCount`, `imagesCount`, `price`, `claimThisBusiness`, `permanentlyClosed`, `temporarilyClosed`, `reserveTableUrl`, `bookingLinks`, `openingHours`, `additionalInfo`, `location`, `placeId`, `cid`, `fid`, `url`, `searchPageUrl`, `kgmid`, `businessProfileId`, `imageUrl`, `language`, `scrapedAt`, hotel fields (`hotelStars`, `hotelAds`, `checkInDate`, `checkOutDate`) when relevant.
- **`verdicts`** — free, computed from the listing: `reputation` (`strong`, `good`, `fragile`, `invisible`, `no_reviews`, `unknown`), `listingGaps` (unclaimed listing, no opening hours, few photos, no website, no phone), `bookingTool` (Planity, Treatwell, Fresha, Booksy, Doctolib, TheFork, Zenchef, OpenTable, SevenRooms, Resy, own system, other platform, none), `sameWebsiteInResults`, `samePhoneInResults`, `intermediarySignals`, `webPresence`. AI, when `qualifyPlaces` / `idealCustomer` / `customQuestions` is set: `digitalMaturity` (0–3) and `digitalMaturityLabel`, `bookingExpected`, `bookingMissing`, `ownership`, `sizeHint`, `priceTier`, `clientele`, `intermediaryProbability`, `idealCustomerFit` (0–1), `custom`. Each AI judgment carries a confidence and answers `unsure` when low.
- **Contacts** (`scrapeContacts: true`): `emails`, `thirdPartyEmails`, `phones`, `facebooks`, `instagrams`, `linkedIns`, `twitters`, `youtubes`, `tiktoks`, `pinterests`, `discords`, `contactsStatus` (`ok`, `no_website`, `social_page_only`, `booking_platform_page`, `website_unreadable`), `websiteReadError` (`slow`, `refused`, `error`, `not_html`).
- **Not included**: reviews (Google no longer shows them to signed-out visitors), popular times, Q&A, reviews distribution by stars.
- **Chain out**: `placeId` → `compass/Google-Maps-Reviews-Scraper` (`placeIds`); `defaultDatasetId` → `sherwood/google-maps-scraper` again with `datasetId` to add verdicts later.

## compass/crawler-google-places — Google Maps Scraper (unaffiliated)

- **Store**: https://apify.com/compass/crawler-google-places
- **Price** (Free plan): `place-scraped` $0.004; add-ons `place-details-scraped` $0.002 per place (needed for reviews, hours, popular times), `review-scraped` $0.0005, `contact-details-scraped` $0.002 per place, `filter-applied` $0.001, `lead-scraped` $0.10 per lead, `social-profile-scraped` $0.10, `image-scraped` $0.0005; Actor start $0.00005.
- **Input used here**: `searchStringsArray`, `locationQuery`, `maxCrawledPlacesPerSearch`, `language`, `skipClosedPlaces`, `scrapePlaceDetailPage`, `maxReviews` (per place; 0 = none), `reviewsSort`, `reviewsStartDate`, `scrapeContacts`, `placeMinimumStars`, `categoryFilterWords`.
- **Output**: same core fields as above; with `maxReviews > 0`, a `reviews[]` array nested in each place (`text`, `stars`, `publishedAtDate`, `responseFromOwnerText`, ...), which `sherwood/review-analyzer` unfolds and groups by `placeId`.
- **When**: reviews on every place in one run, detail-page-only fields, or people enrichment.

## compass/Google-Maps-Reviews-Scraper — Google Maps Reviews Scraper (unaffiliated)

- **Store**: https://apify.com/compass/Google-Maps-Reviews-Scraper
- **Price** (Free plan): `review-scraped` $0.0006 per review ($0.00045 measured on a Starter plan, 2026-11-09); Actor start $0.00005.
- **Input**: `placeIds` (27-character ids starting with `ChIJ` or `GhIJ`) or `startUrls` (`/maps/place`, `/maps/search` or `/maps/reviews` URLs), `maxReviews` (per place; the default scrapes every review, so always set it), `reviewsSort` (`newest`, `mostRelevant`, `highestRanking`, `lowestRanking`), `reviewsStartDate` (absolute `2026-05-03` or relative `3 months`), `reviewsOrigin` (`all` or `google`), `language`, `personalData` (reviewer id, name, photo and the review URL).
- **Output item** (one per review): `text`, `textTranslated`, `stars` (`rating` is `null` on Google reviews), `publishedAtDate`, `publishAt`, `likesCount`, `reviewId`, `reviewUrl` (with `personalData`), `responseFromOwnerText`, `responseFromOwnerDate`, `reviewImageUrls`, `reviewContext`, `reviewDetailedRating`, `originalLanguage`, `isLocalGuide`, `reviewerNumberOfReviews` (reviewer `name`, `reviewerId`, `reviewerUrl`, `reviewerPhotoUrl` are `null` without `personalData`), plus the place: `placeId`, `title`, `categoryName`, `categories`, `totalScore`, `reviewsCount`, `url`, `cid`, `address`, `location`, `businessProfileId`.
- **Chain out**: `defaultDatasetId` → `sherwood/review-analyzer` (`datasetId`), no field mapping needed.

## sherwood/review-analyzer — Review Analyzer API

- **Store**: https://apify.com/sherwood/review-analyzer
- **Price**: `review-analyzed` $0.001 per review with a text (all plans). Reviews without text and reviews that could not be analyzed: free. Actor start $0.00005.
- **Input** (nothing required): `datasetId` (the output of a reviews scraper; tested on `compass/Google-Maps-Reviews-Scraper`, `compass/crawler-google-places` with `maxReviews`, `maxcopell/tripadvisor-reviews`, `memo23/trustpilot-scraper-ppe`, `sherwood/trustpilot-reviews-scraper`, `voyager/booking-reviews-scraper`, `tri_angle/yelp-review-scraper`) or `reviews` (strings or objects with `text`, `rating`, `date`, `placeName`, `category`, `reviewUrl`); field overrides `textField`, `ratingField`, `dateField`, `replyField`, `placeIdField`, `placeNameField`, `categoryField` (dotted paths); `businessType` (`auto`, `restaurant`, `hotel`, `health`, `trades`, `beauty`, `professional`, `retail`, `generic`), `themes` (your own, `"name: definition"`), `maxReviews` (default 500 per run), `maxReviewsPerPlace` (default 100, most recent kept), `includeReviewText`.
- **Output item** (one per business): `placeId`, `placeName`, `category` (the place's `categoryName`), `businessType`, `reviewsAnalyzed`, `reviewsWithoutText`, `averageRating`, `positive`, `mixed`, `negative`, `negativeShare`, `recentNegativeShare` and `olderNegativeShare` (90-day trend; `olderNegativeShare` is `null` when every review is less than 90 days old), `ownerReplyRate`, `unansweredComplaints`, `unansweredComplaintUrls[]` (when the source has review links), `languages` (count per language code), `strengths[]` and `weaknesses[]` (`theme`, `mentions`), `alerts[]` (`date`, `rating`, `severity`, `excerpt`, `url`), `summary`, `reviews[]` (per review: `reviewId`, `reviewUrl`, `reviewDate`, `reviewRating`, `reviewLanguage`, `reviewText` (first 1,000 characters), `sentiment`, `sentimentConfidence`, `severity`, `severityLabel`, `needsReply`, `ownerReplied`, `recommendation`, `praised[]`, `criticized[]`). Reviewer names are never read or copied.
- **Join key**: `placeId` matches the Maps datasets above.
- **Speed**: about 250 reviews in 15 seconds. Themes are read in the review's language; labels come back in English.

## Chaining summary

```
sherwood/google-maps-scraper  ──placeId──►  compass/Google-Maps-Reviews-Scraper  ──datasetId──►  sherwood/review-analyzer
         │                                                                                                │
         └── verdicts, contacts ────────────────────── join on placeId ──────────────────────────────────┘
```

Or, in two runs: `compass/crawler-google-places` with `maxReviews` → `sherwood/review-analyzer` with `datasetId`, then `sherwood/google-maps-scraper` with `datasetId` + `idealCustomer` to add the AI verdicts to the same places.

For an always-on audit, schedule the first Actor and add the next one on its **Integrations** tab with `{"datasetId": "{{resource.defaultDatasetId}}"}`.
