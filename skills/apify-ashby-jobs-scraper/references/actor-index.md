# Actor routing table

One Actor and one skill cover three output modes. Route by question and input shape.

| Question | Actor mode | Actor input shape |
|---|---|---|
| Job rows with salary from named boards | `jobs` | explicit `outputMode: "jobs"`, `companies` list, filters |
| New postings since yesterday | `jobs` | explicit `outputMode: "jobs"`, `publishedAfter: "25h"` on a schedule |
| Which companies use Ashby | `companiesOnly` | directory sweep, optionally with `discoveryQuery` |
| Does this company have an Ashby board | `companiesOnly` | your `companies` list |
| Cheapest full index of a board | `urlsOnly` | `companies` list or board input |

For a discovery-to-jobs pipeline, keep only valid `company` rows, dedupe their non-empty `boardToken` values, and pass those values as `companies` in a second call with explicit `outputMode: "jobs"`. Stop when no valid tokens remain: `companies: []` triggers a directory sweep and would broaden the run.

- Actor: https://apify.com/johnvc/ashby-job-board-scraper?fpr=9n7kx3&fp_sid=awesomeskills
- Actor ID: `johnvc/ashby-job-board-scraper`
- Related family: Greenhouse Job Board API (https://apify.com/johnvc/greenhouse-job-board-api?fpr=9n7kx3&fp_sid=awesomeskills) shares the row shape for cross-ATS merging.
