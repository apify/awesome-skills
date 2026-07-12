# Actor index — apify-hiring-signals

Comprehensive Actor routing table for converting hiring signals into sales intelligence.

| Platform / Data Source | User intent                                                  | Actor ID                       | Tier      | Notes                                               |
| ---------------------- | ------------------------------------------------------------ | ------------------------------ | --------- | --------------------------------------------------- |
| LinkedIn Jobs          | Find companies hiring for a role                             | `apify/linkedin-jobs-scraper`  | apify     | Primary hiring signal source. Use `maxResults` ≤ 50 |
| Google Search          | Enrich companies with funding, expansion, and growth signals | `apify/google-search-scraper`  | apify     | Batch multiple company queries into a single run    |
| Company Websites       | Extract publicly available contact details                   | `vdrmota/contact-info-scraper` | community | Focus on `/contact`, `/about`, and `/team` pages    |

## How the pipeline works

1. Scrape LinkedIn job postings
2. Deduplicate companies
3. Batch-enrich companies with Google Search
4. Extract public contact information from company websites
5. Deliver a ranked sales prospect list

## Notes

- Always batch Google enrichment queries to reduce cost
- Prefer company-level enrichment over per-job enrichment
- Skip contact discovery when the user only requests company intelligence
- This skill focuses on sales prospecting, not general competitive intelligence
