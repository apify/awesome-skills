# Actor index — apify-career-site-jobs-feed

| Actor | Input | Output row | Price |
|---|---|---|---|
| `cleanfeedsapi/ats-jobs-feed` | `boards` (string[] of `source:slug` or careers URLs), `maxJobsPerBoard` (int, 0 = all) | `source, company, title, location, department, url, posted_at, updated_at, id` (+ `error` on a failed board) | $0.002 per row |
| `cleanfeedsapi/hn-who-is-hiring` | `kind` ("hiring"), `thread` ("latest" or item id), `maxComments`, `query` (substring filter) | `source, thread_id, comment_id, company, title, location, remote, salary, url, links, posted_at, text` | $0.002 per row |
| `cleanfeedsapi/remote-jobs-feed` | `sources` (["remoteok","arbeitnow"]), `search`, `maxJobsPerSource` | `source, title, company, location, remote, tags, salary, url, source_url, posted_at, id` | $0.002 per row |

Source endpoints are the ATS's own public job-board JSON (Greenhouse boards-api, Lever postings API, Ashby posting-api, Workday CXS jobs JSON, SmartRecruiters Posting API, Recruitee offers JSON), the official Hacker News Firebase API, and the RemoteOK / Arbeitnow public APIs. No proxies, no login, no HTML parsing. Source code: <https://github.com/cleanfeedsapi/apify-actors>.
