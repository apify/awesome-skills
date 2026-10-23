# Gotchas — Google Maps review analysis

## Cost guardrails

- Two bills when the classifier collects for you: the classifier ($0.50 per 1,000 reviews) and compass' scraper (about $0.006 per place + $0.0005 per review, set by compass). The Store price card of the classifier shows only its own part.
- Size the run: 50–100 newest reviews per place is enough for a diagnosis. Thousands per place rarely change the top complaints.
- Filtered reviews are free: `maxStars` and `reviewsNewerThan` drop reviews before classification, and dropped reviews are not charged.
- For weekly monitoring use `reviewsNewerThan: "7 days"` so each run only pays for new reviews.

## Input traps

- Business names need `location` ("New York, USA"). Without it the search runs from a US data center and may pick another branch. URLs and `ChIJ…` place IDs do not need it.
- Reviews in many languages are accepted; accuracy is measured on English reviews.
- With `datasetId`, fields are detected automatically. If detection misses a field (e.g. a custom scraper), set `textField`, `ratingField`, `dateField`, `ownerReplyField` or `placeNameField` explicitly.

## Reading results

- `needsReply` is the model's judgement that a review deserves a reply; `unanswered` is a fact from the data (no owner reply). The reply queue uses both.
- `alert` marks serious issues: health and safety (food poisoning, injury, pests), discrimination, harassment or abuse by staff, theft, fraud or scam accusations, threats of legal action or chargebacks. Rude staff, long waits or high prices alone are not. Report alerts first.
- `REPORT` change fields (`ratingDelta`, `newReviews`, …) appear only from the second run with the same `monitorKey`.

## Recovery

- Collection step fails with a credit message → top up or lower `maxReviewsPerPlace`; starting compass' scraper may need about $0.50 of remaining credit.
- Empty reply queue → the dataset had no owner-reply field; say so instead of reporting "no unanswered reviews".
