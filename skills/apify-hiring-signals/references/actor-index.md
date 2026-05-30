# Actor index — apify-hiring-signals

Comprehensive Actor routing table for converting hiring signals into sales intelligence.

| Platform / Data Source | User intent                                  | Actor ID                       | Tier      | Notes                                        |
| ---------------------- | -------------------------------------------- | ------------------------------ | --------- | -------------------------------------------- |
| LinkedIn Jobs          | Find companies hiring for a role             | `apify/linkedin-jobs-scraper`  | apify     | Primary signal source. Use `maxResults` ≤ 50 |
| Google Search          | Enrich companies with funding/news/expansion | `apify/google-search-scraper`  | apify     | Batch queries per company for efficiency     |
| Company websites       | Extract emails and contacts                  | `vdrmota/contact-info-scraper` | community | Focus on /about, /contact, /team pages       |

## How the pipeline works

1. Use LinkedIn Jobs Scraper to find companies actively hiring
2. Deduplicate company list
3. Enrich each company using Google Search Scraper (funding, expansion, product launches)
4. Extract decision-maker contacts using Contact Info Scraper

## Notes

- Always batch Google queries to reduce cost
- Prefer company-level enrichment over per-job enrichment
- Skip contact scraping if user only requests company list
