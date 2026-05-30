# Gotchas — apify-hiring-signals

Cost guardrails, error recovery, and common pitfalls for hiring-signal intelligence workflows.

---

## Cost guardrails

Before running any Actor, estimate cost based on expected scale.

| Model         | Notes                              |
| ------------- | ---------------------------------- |
| FREE          | Safe to run                        |
| PAY_PER_EVENT | Scales with number of jobs/results |
| FLAT_PRICE    | Subscription-based                 |

### Suggested thresholds

- > $5 estimated cost → warn user
- > $20 estimated cost → require explicit confirmation
- Always describe cost as approximate

---

## Common errors

| Error                                        | Cause                    | Fix                                      |
| -------------------------------------------- | ------------------------ | ---------------------------------------- |
| `0 results from LinkedIn`                    | Geo-block or rate-limit  | Switch to Google fallback search         |
| `MAX_RESULTS exceeded`                       | Too large query          | Reduce to ≤ 50 results                   |
| `EMPTY contacts array`                       | No public emails on site | Try deeper crawl (/about, /team) or skip |
| `Google scraper returns low quality results` | Too broad query          | Narrow company name + keyword            |

---

## Actor-specific notes

### `apify/linkedin-jobs-scraper`

- Some regions may throttle results
- Use proxy enabled (`useApifyProxy: true`)
- Company deduplication is required after scraping jobs

### `apify/google-search-scraper`

- Best used in batches (multiple queries in one run)
- Avoid one-request-per-company (too expensive)
- Focus queries on:
  - funding
  - hiring announcements
  - product launches

### `vdrmota/contact-info-scraper`

- Not all companies expose emails publicly
- Prioritize:
  - /contact
  - /about
  - /team
- Ignore generic emails (info@, support@) when possible
