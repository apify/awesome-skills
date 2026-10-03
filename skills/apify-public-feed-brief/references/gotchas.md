# Public feed brief: recovery and field handling

These notes describe the two public Technical Dost Actors as checked on
October 3, 2026. Re-read their live Store pages and input schemas before a
run; pricing, defaults, and output can change.

## Cost guardrails

| Route | Published charge | Bound the first run |
| --- | --- | --- |
| `technicaldost/rss-feed-scraper` | $0.008 per default-dataset row. Metadata and error rows also count. | One feed, `maxItemsPerFeed: 5`; up to six rows when it succeeds. |
| `technicaldost/rss-feed-monitor` | $0.002 Actor-start event at 1 GB, scaled with memory, plus $0.01 per new item. | One feed, `maxItemsFirstRun: 5`, a finite `maxItemsPerFeed`, and a stable `stateKey`. |

The scraper's omitted `maxItemsPerFeed` defaults to 50. The monitor's omitted
`maxItemsFirstRun` defaults to 10 and omitted `maxItemsPerFeed` defaults to
50. An Apify maximum-charge setting is a ceiling, not a fixed run price. Do
not treat an empty monitor dataset as a free run because its start event can
still be charged.

## Output that needs interpretation

| Observation | Correct handling |
| --- | --- |
| Scraper run `SUCCEEDED` but one `error` row appears | Report that feed as failed; keep successful feeds' `feed_item` rows. Do not call it an all-feed success. |
| `feed_metadata.itemCount` exceeds returned entries | This can be the source feed's total entries before the configured slice. Use the actual `feed_item` count for delivered results. |
| `pubDate`, `guid`, `author`, `summary`, or `content` absent | The publisher may omit it. Leave unknown; do not fabricate fields or claim full article text. |
| Same scraper items appear on a later run | Expected: this Actor does not keep cross-run seen-item history. For recurring new-only collection, use the monitor route. |
| Monitor returns no rows after baseline | Could mean no new entries. Verify the run succeeded and check the next feed update; do not claim the feed was permanently inactive. |
| Monitor `stateKey` changes | Treat the next run as a fresh baseline, which can change which items are returned and billed. |

## Errors and safe recovery

- **Invalid input**: read the live input schema and correct field names and
  limits before another paid attempt. `feedUrls` is an array of public feed
  URLs, not a single string or a list of ordinary webpages.
- **Unreachable or malformed feed**: record the affected `feedUrl` and error
  text. Ask the user for a working public feed URL or confirm the publisher's
  own feed. Do not retry repeatedly or bypass access controls.
- **Authentication failure**: use Apify's ordinary CLI login or environment
  token setup. Never put a token in a URL, file, issue, or chat response.
- **Run-level failure or timeout**: report the run ID and status. Inspect
  authorized run logs in Apify Console before proposing a corrected input;
  do not infer a successful dataset from a started run.
- **Full-text request**: these Actors return only content supplied by the
  feed. Do not fetch linked articles or present their full text as collected
  unless a separate, authorized workflow actually does that work.
