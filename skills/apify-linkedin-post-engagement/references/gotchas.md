# Gotchas: LinkedIn post engagement (johnvc/linkedin-posts-api)

Cost guardrails, error recovery, and analysis notes. The agent reads this on demand when building inputs or when a run fails.

## Cost guardrails

Pricing model: pay per event, one charge per post returned, about $0.004 per post at the time of writing. Confirm the live price on the Store card or with `apify actors info "johnvc/linkedin-posts-api" --json 2>/dev/null` (look at `pricingInfo`).

Estimate before running:

- Discovery: cost is roughly (number of profiles) times `maxPostsPerProfile` times the price per post. Example: 5 competitors at 50 posts each at $0.004 is about $1.00.
- Fetch by URL: cost is roughly (number of post URLs) times the price per post.

Suggested confirmation thresholds:

- Rough estimate over $5: warn the user.
- Rough estimate over $20: get explicit confirmation before running.
- Always present cost as "around $X", not a guarantee.

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| Error row with `error_type` "CollectionError" | Profile has no public posts, or none in the date window | Expected. Skip the row; the rest of the batch still returns. |
| `error_type` "MissingRequiredParameter" | Neither `profileUrls` nor `postUrls` was supplied | Provide at least one input array. |
| Engagement rate is blank | `authorFollowers` was not available for that author | Report raw counts (likes, comments, shares) instead. |

## Analysis notes

- Total engagement per post is `numLikes` + `numComments` + `numShares`.
- Engagement rate needs `authorFollowers`; it is returned when available. When it is missing, fall back to raw counts.
- Counts are a snapshot at fetch time. To track a trend, run on a schedule and compare `datePosted` windows with `startDate`/`endDate`.
- The `engagement` dataset view already lines up reach and reactions, so you can rank posts without extra transformation.
- Public posts only. This does not read LinkedIn's private analytics.
