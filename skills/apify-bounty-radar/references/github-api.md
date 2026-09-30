# GitHub API evidence procedure

Use an available connector that exposes these endpoints and pagination, or the included Python helper. The helper uses only GET requests to `api.github.com`, reads optional `GH_TOKEN`/`GITHUB_TOKEN` from the environment, refuses private repository evidence, and does not post claims or execute repository code.

| Step | Endpoint | Evidence to retain |
|---|---|---|
| Discover | `GET /search/issues?q=...` | `items`, `total_count`, `incomplete_results`, search query and time |
| Repository | `GET /repos/{owner}/{repo}` | canonical name, `private`, `archived`, `disabled` |
| Issue or PR conversation | `GET /repos/{owner}/{repo}/issues/{number}` | body, state, labels, assignees, comment count, `updated_at`, `html_url` |
| All conversation comments | `GET /repos/{owner}/{repo}/issues/{number}/comments?per_page=100` | full body, author, date, source URL on every page |
| Timeline | `GET /repos/{owner}/{repo}/issues/{number}/timeline?per_page=100` | assignments, closures/reopens, cross-references and source issues/PRs |
| A relevant PR | `GET /repos/{owner}/{repo}/pulls/{number}` | current head, draft, state, `merged`, `merged_at`, base repository |
| PR reviews | `GET /repos/{owner}/{repo}/pulls/{number}/reviews?per_page=100` | reviewer, state, body, date, commit and review URL |

The helper's `evidence` command re-fetches the issue at the end and marks coverage incomplete if comment counts or `updated_at` changed during collection. `coverage.complete` refers only to those fetched collections, **not** reward eligibility, absence of other PRs, correctness of submitted code, or confirmed payment.

Read timeline `cross-referenced` events' `source.issue` objects and explicit PR links in the issue/comments. Check referenced PRs individually, including their conversations, and keep a record of what was checked. To search for additional attempts with a connector/CLI, use Search Issues with `repo:OWNER/REPO is:pr` plus the issue URL or issue number/title; inspect matches because a textual reference may be unrelated. Absence of a cross-reference alone does not establish no competition.

## Pagination and failure behavior

Follow the response `Link` header's `rel="next"`, not just the number of returned rows. The helper defaults to five pages per collection and records the next page when it stops; increase the explicit bound if needed, otherwise keep the candidate unverified. Partial collections remain in output with errors. No paid Actor or browser fallback is needed to recover API rate limits.

Search is capped by GitHub at 1,000 results per query and can time out with `incomplete_results: true`. Narrow by repository/date/language and use independent queries instead of treating a bounded search as exhaustive. The helper always constrains discovery to public issues; inspect PRs through `evidence` rather than changing its search mode.

On 403/429, observe `Retry-After` or `X-RateLimit-Reset` before retrying; do not tight-loop. On 401, correct authorized authentication. On 404, record inaccessible/not found; it may be deleted, renamed, or unavailable to the token, so it does not prove closure. The helper stops on HTTP/network errors and redirects, never disables TLS verification, and avoids printing token values or response bodies in error messages.

## Sources and review context

- [Search API and its limits](https://docs.github.com/en/rest/search/search#search-issues-and-pull-requests)
- [Issue comments and pagination](https://docs.github.com/en/rest/issues/comments#list-issue-comments)
- [Issue timeline](https://docs.github.com/en/rest/issues/timeline#list-timeline-events-for-an-issue)
- [Pull request metadata](https://docs.github.com/en/rest/pulls/pulls#get-a-pull-request)
- [API pagination](https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api)

The API-first design follows the maintainer's [specific review on PR #43](https://github.com/apify/awesome-skills/pull/43#issuecomment-5705263180): GitHub HTML missed later comments and returned an already-paid bounty as a candidate. This explicitly uses GitHub's read-only API in addition to public Apify Actors; it needs maintainer acceptance of that exception to the repository's general Actor-only rule.
