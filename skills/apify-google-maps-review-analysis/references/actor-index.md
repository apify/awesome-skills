# Actor index — Google Maps review analysis

| User need | Actor ID | Tier | Price (Oct 2026) | Notes |
|---|---|---|---|---|
| Free health check of one business | `leoworks/google-maps-review-health-check` | community (skill author's own) | free (collection billed by compass) | Input `place` (URL or name), `location`, `maxReviews` (default 30) or `datasetId`. Star average, owner reply rate, unanswered 1–3 star reviews, last 90 days vs before. Built by this skill's author. |
| Complaint types, praise, sentiment, alerts, reply queue, monitoring | `leoworks/google-maps-review-classifier` | community (skill author's own) | $0.50 / 1,000 reviews classified | Input `places` (collects via compass) or `datasetId` or `texts`. Reports `REPORT_PLACES.csv`, `REPLY_QUEUE.csv`, `REPORT`. Built by this skill's author. |
| Collect reviews of known places | `compass/google-maps-reviews-scraper` | community | set by compass | Input `startUrls` or `placeIds`, `maxReviews`, `reviewsSort` (`newest`), `reviewsStartDate`, `language`. Set `personalData: false` unless reviewer names are needed. |
| Find places by search term and collect their reviews | `compass/crawler-google-places` | community | set by compass | The collector the classifier calls when given `places`. |

`Tier` = `apify` (Apify-maintained) or `community` (third-party).
