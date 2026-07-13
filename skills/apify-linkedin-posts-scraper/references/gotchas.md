# Gotchas: LinkedIn posts scraper (johnvc/linkedin-posts-api)

Cost guardrails, error recovery, and input quirks. The agent reads this on demand when building inputs or when a run fails.

## Cost guardrails

Pricing model: pay per event, one charge per post returned, about $0.004 per post at the time of writing. Confirm the live price on the Store card or with `apify actors info "johnvc/linkedin-posts-api" --json 2>/dev/null` (look at `pricingInfo`).

Estimate before running:

- Discovery: cost is roughly (number of profiles) times `maxPostsPerProfile` times the price per post. Example: 10 profiles at 20 posts each at $0.004 is about $0.80.
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
| A profile URL returns nothing | The URL is not an `/in/` profile (company or school page), so it is skipped | Use `/in/` profile URLs for discovery. |

## Actor-specific notes

- Two modes: `profileUrls` discovers recent posts newest-first; `postUrls` fetches exact posts. You can pass both in one run.
- Limits per run: `profileUrls` up to 25, `postUrls` up to 1000, `maxPostsPerProfile` up to 200 (default 20). Split larger jobs into batches. The Actor notes you can ask to raise these limits for an account.
- `startDate` and `endDate` (YYYY-MM-DD) apply to discovery only, not to specific post URLs.
- Output is flat, one row per post, so it loads straight into a sheet, a database, or a BI tool.
- Public posts only. No private or connection-gated content.
