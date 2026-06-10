# Actor Index

## `apify/google-search-scraper`

- Tier: Apify-maintained
- Use for: discovering public GitHub, Algora, Polar, and maintainer-direct bounty pages.
- Inputs to tune:
  - `queries`: one query or newline-separated queries.
  - `resultsPerPage`: keep at 10 for first pass.
  - `maxPagesPerQuery`: start with 1 or 2.
  - `countryCode` and `languageCode`: use the user's target market when relevant.
- Output to inspect:
  - result title, URL, snippet, displayed URL, and ranking position.

Good first-pass queries:

```text
site:github.com "bounty" "$" "Steps to solve" "/attempt"
site:github.com "bounty" "$100" "open" "GitHub"
site:github.com "Polar" "Funding" "issue is completed"
```

## `apify/website-content-crawler`

- Tier: Apify-maintained
- Use for: one-page evidence capture from issue pages, PR pages, docs, Algora claim pages, and Polar funding pages.
- Inputs to tune:
  - `startUrls`: candidate page URLs.
  - `maxCrawlPages`: set to 1 for issue pages.
  - `crawlerType`: `cheerio` is usually enough for public GitHub pages.
  - `saveMarkdown`: useful for extracting body text and tables.
- Output to inspect:
  - page title, URL, Markdown body, extracted links, and visible text.

## `apify/web-scraper`

- Tier: Apify-maintained
- Use for: custom selectors when the generic crawler does not expose the table or page state cleanly.
- Keep custom code minimal and document selectors. Prefer APIs for GitHub state when available.
