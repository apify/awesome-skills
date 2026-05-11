# Actor Input & Output Schemas

Verified inputs and output fields from real test runs. Last tested: 2026-05-06.

---

## apify/google-search-scraper

**Input:**
```json
{ "queries": "\"Company Name\" keyword", "maxPagesPerQuery": 1 }
```
Optional: `countryCode` ("us"), `languageCode` ("en"), `maxPagesPerQuery` (1-10).

**Output keys:** `searchQuery`, `url`, `organicResults[]`, `paidResults[]`, `peopleAlsoAsk[]`, `relatedQueries[]`, `aiOverview`, `resultsTotal`

Each `organicResult`: `title`, `url`, `description`, `position`, `date`, `emphasizedKeywords[]`, `siteLinks[]`, `productInfo` (may contain `rating`, `numberOfReviews`).

---

## apify/website-content-crawler

**Input:**
```json
{
  "startUrls": [{"url": "https://example.com/pricing"}],
  "maxCrawlPages": 1,
  "maxCrawlDepth": 0,
  "proxyConfiguration": {"useApifyProxy": true}
}
```
⚠️ `proxyConfiguration` is required. Optional: `crawlerType` ("playwright:adaptive").

**Output keys:** `url`, `markdown`, `text`, `html`, `metadata`, `crawl`, `screenshotUrl`

`metadata`: `title`, `description`, `author`, `keywords`, `languageCode`, `openGraph`, `jsonLd`.
`crawl`: `loadedUrl`, `loadedTime`, `httpStatusCode`, `depth`, `contentType`.

---

## apify/rag-web-browser

**Input:**
```json
{ "query": "Company Name pricing plans" }
```

**Output keys:** `query`, `markdown`, `metadata`, `searchResult`, `crawl`

`searchResult`: `title`, `description`, `url`, `resultType`, `rank`.
`metadata`: `title`, `description`, `languageCode`, `url`.
`markdown`: full page content in markdown.

---

## dev_fusion/Linkedin-Company-Scraper

⚠️ **Before calling:** LinkedIn slugs often differ from company names (e.g., Oxylabs → `oxylabs-io`, not `oxylabs`). Wrong slug silently returns 0 results. **Discover via SERP first:** `"[company] site:linkedin.com/company"`

**Input:**
```json
{ "profileUrls": ["https://www.linkedin.com/company/VERIFIED-SLUG/"] }
```
⚠️ Field is `profileUrls`, NOT `urls`.

**Output:** Data stored in key-value store, not dataset. Check KV store keys after run.

---

## curious_coder/linkedin-jobs-scraper

⚠️ **Before calling:** Verify the company's exact name on LinkedIn via SERP: `"[company] site:linkedin.com/jobs"`. Multi-word names need URL-encoding (`Bright Data` → `Bright%20Data`). Wrong name returns 0 or unrelated jobs silently.

**Input:**
```json
{
  "urls": ["https://www.linkedin.com/jobs/search/?keywords=VERIFIED-COMPANY-NAME&position=1&pageNum=0"],
  "count": 10,
  "scrapeCompany": true
}
```
⚠️ `count` minimum is 10. Requires LinkedIn search URL, NOT keyword string.

**Output keys:** `id`, `title`, `companyName`, `companyLinkedinUrl`, `companyLogo`, `companyWebsite`, `companyDescription`, `companyEmployeesCount`, `companySlogan`, `location`, `country`, `postedAt`, `postedAtTimestamp`, `expireAt`, `salary`, `salaryInsights`, `seniorityLevel`, `employmentType`, `jobFunction`, `industries`, `descriptionText`, `descriptionHtml`, `applicantsCount`, `applyUrl`, `applyMethod`, `workplaceTypes`, `workRemoteAllowed`, `standardizedTitle`, `link`, `inputUrl`

---

## pratikdani/crunchbase-companies-scraper

⚠️ **Before calling:** Verify the org slug via SERP: `"[company] site:crunchbase.com/organization"`. Slug is typically lowercased with hyphens.

**Input:**
```json
{ "url": "https://www.crunchbase.com/organization/VERIFIED-SLUG" }
```
⚠️ Field is `url` (singular string), NOT `urls` (array).

**Output:** May return `{"error": "Issue in running the url."}` for wrong slugs. When successful: company profile data (funding, investors, financials).

---

## junglee/Amazon-crawler

**Input:**
```json
{ "categoryOrProductUrls": [{"url": "https://www.amazon.com/dp/ASIN"}] }
```
⚠️ Field is `categoryOrProductUrls`, NOT `productUrls`.

**How to find the URL:** Any Amazon product page works. The canonical form is `amazon.com/dp/ASIN` where ASIN is the 10-character product identifier (e.g., `B0D1XD1ZV3`). ASIN is visible in the URL or in the product details section of any Amazon listing.

**Output keys:** `title`, `url`, `asin`, `price`, `listPrice`, `brand`, `stars`, `reviewsCount`, `inStock`, `features[]`, `attributes[]`, `productOverview[]`, `description`, `thumbnailImage`, `highResolutionImages[]`, `bestsellerRanks`, `seller`, `delivery`, `aiReviewsSummary`, `productPageReviews[]`, `monthlyPurchaseVolume`, `variantAsins[]`

---

## web_wanderer/amazon-reviews-extractor

**Input:**
```json
{ "products": ["https://www.amazon.com/dp/ASIN"] }
```
⚠️ Field is `products`, NOT `productUrls`. Use the same `amazon.com/dp/ASIN` format as Amazon-crawler.

May return 0 items for some products — try the full product URL with title slug if the short form fails.

---

## e-commerce/walmart-product-detail-scraper

**Input:**
```json
{ "productUrls": ["https://www.walmart.com/ip/Product-Name/ID"] }
```

**How to find the URL:** Use the full URL from Walmart product page. The numeric ID at the end is required (e.g., `/1752657021`).

⚠️ May return 0 items. Verify product URL is accessible (some products are region-locked).

---

## compass/Google-Maps-Reviews-Scraper

**Input:**
```json
{ "startUrls": [{"url": "https://www.google.com/maps/place/Place+Name/@lat,lng,17z"}], "maxReviews": 30 }
```

**How to find the URL:** Search Google Maps for the business → copy full URL from browser address bar. Must include the `@lat,lng,zoom` part. Alternatively use a place ID URL: `https://www.google.com/maps/place/?q=place_id:ChIJ...`.

**Output:** Status object with `isFinished`, `enqueued`, `placeIdsEnqueued`. Review data in separate dataset items.

---

## automation-lab/g2-scraper

Replaces `zhorex/g2-reviews-scraper` (broken).

⚠️ **Before calling:** Discover the G2 slug via SERP: `"[product] site:g2.com/products"`. Extract slug from URL pattern `g2.com/products/[slug]/reviews`. Wrong slug silently returns reviews for a **different product** (e.g., Slack). Always verify `productName` in output matches your target.

**Input:**
```json
{ "mode": "product_reviews", "productUrls": ["VERIFIED-SLUG"], "maxReviews": 25, "sortReviews": "newest" }
```
⚠️ Field is `productUrls` (array of slugs), NOT `startUrls`. `mode` is required.

**Output keys:** `reviewId`, `title`, `starRating`, `nps`, `reviewText`, `publishedAt`, `submittedAt`, `reviewerName`, `country`, `region`, `easeOfUse`, `easeOfSetup`, `easeOfAdmin`, `qualityOfSupport`, `meetsRequirements`, `loveTheme`, `hateTheme`, `switchedFromOtherProduct`, `switchedReason`, `companySegment`, `industry`, `productName`, `productSlug`, `url`, `helpfulVotes`, `sourceType`

---

## zen-studio/capterra-reviews-scraper

⚠️ **Before calling:** Discover the Capterra URL via SERP: `"[product] site:capterra.com/p/"`. URL pattern is `capterra.com/p/[numeric-id]/[Product-Name]/reviews/`. The numeric ID is required — do not guess it.

**Input:**
```json
{ "productUrl": "https://www.capterra.com/p/NUMERIC-ID/Product-Name/reviews/", "maxReviews": 10 }
```
⚠️ Field is `productUrl` (singular string), NOT `startUrls`.

**Output keys:** `url`, `reviewId`, `title`, `writtenOn`, `overallRating`, `easeOfUseRating`, `customerSupportRating`, `functionalityRating`, `valueForMoneyRating`, `recommendationRating`, `prosText`, `consText`, `generalComments`, `adviceToOthers`, `incentivized`, `reviewer`, `vendorResponse`, `scrapedAt`

`reviewer`: `fullName`, `jobTitle`, `companySize`, `industry`, `timeUsedProduct`, `isValidated`.

---

## Gartner Peer Insights

⚠️ **No working actor available** (tested 2026-05-06 with Databricks — major vendor with thousands of reviews). All actors on Apify Store (`zen-studio`, `hello.datawizards`, `memo23`) return empty or fail. Gartner blocks all scrapers. Use SERP snippet mining as fallback:
```
call-actor: apify/google-search-scraper
  input: { "queries": "[product] review site:gartner.com" }
```

---

## memo23/glassdoor-scraper-ppr

⚠️ **Before calling:** Discover the Glassdoor URL via SERP: `"[company] site:glassdoor.com/Overview"`. The URL contains an employer ID (`EI_IE[number]`) — the numeric ID is what matters, not the company name part.

**Input:**
```json
{ "startUrls": [{"url": "https://www.glassdoor.com/Overview/Working-at-COMPANY-EI_IEVERIFIED-ID.htm"}], "command": "reviews" }
```
`command` values: `reviews`, `jobs`, `interviews`, `salaries`, `overview`. Default to `reviews` for CI.

**Output keys:** `reviewId`, `summary`, `pros`, `cons`, `advice`, `ratingOverall`, `ratingWorkLifeBalance`, `ratingCultureAndValues`, `ratingCompensationAndBenefits`, `ratingCareerOpportunities`, `ratingSeniorLeadership`, `ratingDiversityAndInclusion`, `ratingCeo`, `ratingBusinessOutlook`, `ratingRecommendToFriend`, `jobTitle`, `location`, `reviewDateTime`, `isCurrentJob`, `lengthOfEmployment`, `employer`

`employer`: `id`, `shortName`, `squareLogoUrl`.
`jobTitle`: `text`.

---

## harshmaur/reddit-scraper

**Input:**
```json
{ "startUrls": [{"url": "https://www.reddit.com/search/?q=company+keyword"}], "maxItems": 10 }
```

Alternatively, scrape a specific subreddit: `https://www.reddit.com/r/subreddit/search/?q=keyword`.

**Output keys:** `id`, `title`, `body`, `authorName`, `communityName`, `upVotes`, `commentsCount`, `dataType` ("post"/"comment"), `postUrl`, `contentUrl`, `createdAt`, `crawledAt`, `flair`, `postType`

---

## neatrat/google-play-store-reviews-scraper

**Input:**
```json
{ "appIdOrUrl": "com.company.app" }
```
⚠️ Field is `appIdOrUrl`, NOT `appId`.

**How to find the app ID:** Open the app on Google Play → the URL is `play.google.com/store/apps/details?id=com.company.app`. The `id` parameter is the app ID (e.g., `com.slack`, `com.spotify.music`). Both the ID string and the full Play Store URL work as input.

---

## jdtpnjtp/apple-app-store-scraper

⚠️ Requires SHADER proxy group which may not be available on all Apify plans. Verify access before use.

**Input (when proxy available):** App Store URL, e.g., `https://apps.apple.com/us/app/app-name/idNUMBER`.

**How to find the URL:** Search App Store or use SERP: `"[app] site:apps.apple.com"`. The numeric ID at the end (`id618783545`) identifies the app.

---

## pro100chok/similarweb-scraper

**Input:**
```json
{ "searchType": "similarweb", "domains": ["apify.com", "oxylabs.io", "brightdata.com", "zyte.com", "scraperapi.com", "smartproxy.com", "scrapingbee.com", "nimbleway.com", "diffbot.com", "octoparse.com"] }
```
⚠️ `searchType` is required. **Minimum 10 domains required** — actor rejects fewer with "Minimum 10 domains required for analysis." Always batch all competitors into one call. Use bare domain without protocol (e.g., `apify.com`, not `https://apify.com`).

---

## data_xplorer/google-news-scraper-fast

**Input:**
```json
{
  "keywords": ["\"Company Name\""],
  "maxArticles": 10,
  "timeframe": "7d",
  "region_language": "US:en",
  "decodeUrls": true,
  "extractDescriptions": true,
  "extractImages": false
}
```
`timeframe` values: `1h`, `1d`, `7d`, `1y`, `all`. Multi-keyword via array. Use quotes for exact phrase match (e.g., `"\"Bright Data\""` to find articles mentioning "Bright Data" as a phrase, not "bright" and "data" separately). ⚠️ Boolean operators (OR, AND) produce unreliable results — use separate keywords array entries instead of boolean syntax.

**Output keys:** `title`, `url`, `source`, `publishedAt` (ISO), `publishedTimestamp` (unix), `image`, `description` (full text when `extractDescriptions: true`), `metadata`

`metadata`: `scrapeTimestamp`, `keyword`, `sourceType`, `timeframe`.

---

## andok/wayback-machine-scraper

**Input:**
```json
{ "url": "https://example.com/pricing" }
```
No `maxSnapshots` parameter exists. Use full URL including path to specific page (e.g., pricing page, homepage).

**Output keys:** `inputUrl`, `snapshotCount`, `snapshots[]`, `latestSnapshot`, `latestHtml`, `checkedAt`, `error`

Each snapshot contains URL + timestamp of archived version. May return `"error": "Wayback CDX HTTP 503"` when the Wayback Machine API is overloaded — retry later.
