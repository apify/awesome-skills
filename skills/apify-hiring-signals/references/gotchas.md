# Gotchas — apify-hiring-signals

Cost guardrails, error recovery, and common pitfalls for hiring-signal intelligence workflows.

## Cost guardrails

Before running any Actor, estimate cost based on expected scale.

| Model                | Notes                                      |
| -------------------- | ------------------------------------------ |
| FREE                 | Safe to run                                |
| PAY_PER_EVENT        | Cost scales with number of jobs or results |
| FLAT_PRICE_PER_MONTH | Subscription-based                         |

### Suggested thresholds

- Estimated cost > $5 → warn the user
- Estimated cost > $20 → require explicit user confirmation
- Always describe costs as estimates, not guarantees

## Common errors

| Error                        | Cause                                   | Fix                                                  |
| ---------------------------- | --------------------------------------- | ---------------------------------------------------- |
| `0 results from LinkedIn`    | Geo-blocking or rate limiting           | Use Google Search fallback                           |
| `MAX_RESULTS exceeded`       | Query size too large                    | Reduce result count                                  |
| `EMPTY contacts array`       | No public contact information available | Try `/about`, `/team`, or skip contact discovery     |
| `Low quality Google results` | Query too broad                         | Narrow search using company name and signal keywords |

## Actor-specific notes

### `apify/linkedin-jobs-scraper`

- Some regions may throttle results
- Enable Apify proxy support when available
- Deduplicate companies after scraping

### `apify/google-search-scraper`

- Batch company queries into a single run whenever possible
- Avoid one-request-per-company enrichment
- Focus on:
  - funding announcements
  - expansion signals
  - product launches
  - leadership changes

### `vdrmota/contact-info-scraper`

- Not every company exposes contact information publicly
- Prioritize:
  - `/contact`
  - `/about`
  - `/team`

- Prefer personal or role-based emails over generic addresses such as `info@` or `support@`
