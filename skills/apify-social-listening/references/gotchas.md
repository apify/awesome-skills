# Gotchas — cost guardrails & error recovery

## Cost scaling

Reddit run cost scales with **queries × depth × comments**:

- `maxPostsPerSubreddit` is per query *and* per subreddit. Three `searchQueries` at depth 100 ≈ 300 posts.
- `includeComments: true` adds a fetch per post and multiplies items by `maxCommentsPerPost`. For a quick sentiment read, start with `includeComments: false`; turn it on once the subject and scope are confirmed.
- Confirm with the user before launching anything above ~500 posts or comments enabled at depth > 100.

A cheap calibration first run: one query, `timeFilter: "week"`, `maxPostsPerSubreddit: 25`, `includeComments: false`. Inspect relevance, then scale.

## Relevance / noise

- Short or generic subjects ("apple", "spring", a one-word product name) pull unrelated posts. Narrow with `subreddits` or a more specific phrase (`"apple vision pro"` not `"apple"`).
- Use `sortBy: "relevance"` for keyword listening and `sortBy: "top"` for community deep-dives.

## Sentiment caveat

The Reddit Actor's `score` / `upvoteRatio` measure community **reception**, not text polarity. A highly-upvoted post can be a complaint the community agrees with. Always read the text of the top and bottom items before labeling sentiment.

## Empty or partial results

- Zero items usually means the query was too narrow or the `timeFilter` too short. Widen the window (`week` → `month`) or drop to whole-of-Reddit keyword search.
- Reddit throttles aggressive crawling; the Actor honors `proxyConfiguration` (residential by default). If results look thin, leave the default proxy on.

## YouTube module

- `channelUrls` / `videoUrls` only — it cannot keyword-search YouTube for brand mentions. If the user wants YouTube *mentions*, set expectations: you can analyze named channels/videos, not discover them by topic.
- `maxVideosPerChannel` defaults to 50; lower it for a quick engagement snapshot.
