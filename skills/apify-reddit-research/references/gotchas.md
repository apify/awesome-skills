# Gotchas — apify-reddit-research

Cost guardrails, error recovery, and Reddit-specific pitfalls.

## Cost guardrails

`trudax/reddit-scraper-lite` uses **PAY_PER_EVENT** pricing.

- ~$3.40 per 1,000 results stored
- Cost is driven mainly by `maxItems`, `maxPostCount`, and `maxComments`

### Recommended confirmation thresholds

- Expected cost **>$6** → warn the user and show rough estimate
- Expected cost **>$15** → require explicit confirmation before running
- Always be conservative — Reddit threads can grow quickly

## Common errors & fixes (based on live testing)

| Error / Symptom | Likely Cause | Fix / What to tell the user |
|-----------------|--------------|-----------------------------|
| Run finishes with "0 succeeded, X failed" (even if status = SUCCEEDED) | Reddit blocking or temporary Actor issues | Very common. In recent tests we saw runs with only 1 success out of 12 requests. Show the consoleUrl. Offer retries with tighter subreddit focus or different keywords. |
| Dataset is empty (0 items stored) even on "SUCCEEDED" | Actor could not extract data | You may still pay the ~$0.04 startup fee. Be honest: "The scraper had a bad run — this happens often." |
| Very few or zero relevant results | Broad keywords matching old/unrelated threads (e.g. people named "Claude" in old posts) | Use more specific queries, add subreddit restrictions via startUrls, or add time filters. Broad brand names are noisy. |
| Run takes very long or times out | Huge comment threads or very large subreddit | Lower `maxComments` and `maxPostCount`. Use `skipComments: true` if comments not needed |
| 403 / rate limit errors | Aggressive scraping or datacenter proxies | The Actor defaults to residential proxies. Retry later with smaller limits. |
| NSFW content appearing | `includeNSFW` defaults to true | Explicitly set `"includeNSFW": false` for brand/professional work |
| Duplicate or weird data | Mixing search + startUrls incorrectly | Prefer one method per run (either `searches` or `startUrls`) |

## Actor-specific notes for `trudax/reddit-scraper-lite`

- **Comments explode fast**: One popular post can return thousands of comments. Always cap with `maxComments`.
- **Subreddit URLs**: Use clean URLs like `https://www.reddit.com/r/saas/` (no trailing paths needed for most cases).
- **Search vs startUrls**: 
  - Use `searches` for open research across Reddit.
  - Use `startUrls` when the user gives you a specific subreddit or post.
- **Deleted content**: Expect missing posts and comments. Reddit removes a lot.
- **Date filters**: `time` only applies to post searches. Use `postDateLimit` / `commentDateLimit` for more precise control when needed.

## Interpreting run results (very important)

After every run, look at these fields in the output:

- `statusMessage`: Often says things like "Finished! Total 1 requests: 0 succeeded, 1 failed." This is the most honest signal.
- `chargedEventCounts.result`: How many items you actually paid for. 0 is common during flaky periods.
- `consoleUrl`: Always share this with the user when things go wrong — they can see the detailed log.

**Real pattern observed in testing (May 2026):** Multiple small runs returned 0 results and "0 succeeded" even with conservative settings. In these cases:
- Be honest with the user immediately.
- Offer 2–3 retry options (different keywords, subreddit instead of search, remove time filter, lower limits).
- Mention that Reddit scrapers frequently go through periods of high failure rates.

If the user needs reliable data right now, consider suggesting they check the Actor's page on the Apify Store for recent run success rates.

## Output quality tips

- Always summarize themes + sentiment instead of raw dumping.
- When user wants the full data, save as CSV/JSON and give them the file + the Apify dataset console link.
- Include key fields: title, score, subreddit, author, created, url, comment count.
