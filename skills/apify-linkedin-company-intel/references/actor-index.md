# Actor index — apify-linkedin-company-intel

All three Actors read LinkedIn's public (signed-out) pages through Apify Proxy, return company and job data only (no people, no profiles), and charge per result.

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Find companies matching a description (keyword, location, industry, size, HQ, followers) | `saliga/linkedin-company-search` | community | Lead lists and market maps. Discovers companies hiring for the keywords plus their LinkedIn "Similar pages", checks each page against the filters, returns and charges only matches. |
| Company data for known companies (LinkedIn links, page names or website domains) | `saliga/linkedin-company-scraper` | community | CRM enrichment, domain → LinkedIn lookup, look-alikes of best customers, up to 10 recent posts per company. |
| Recent posts of companies, or only new posts since the last run | `saliga/linkedin-company-scraper` (`"outputMode": "posts"`, `"onlyNewPosts": true`) | community | Competitor and account monitoring on a schedule. |
| Jobs by keyword and location, or a hiring-companies list | `saliga/linkedin-jobs-scraper` | community | Hiring signals, recruiting, job alerts; `"outputMode": "companies"` for one row per hiring company with recent-hiring counts. |

## Choosing between search and scraper

- The user names the companies (a list, a CSV, domains) → scraper.
- The user describes the companies ("B2B SaaS in Berlin, 51-200 people") → search.
- The user has 3-10 example customers and wants more like them → search with `seedCompanies` set to those customers. Use seeds of roughly the size they want: LinkedIn's look-alikes of a large company are mostly large companies.

## Key inputs

`saliga/linkedin-company-search`: `keywords[]`, `locations[]`, `seedCompanies[]`, `industries[]` (substring of the LinkedIn industry), `companySizes[]` (`1-10`, `11-50`, `51-200`, `201-500`, `501-1000`, `1001-5000`, `5001-10000`, `10001+`), `headquartersIn[]`, `minFollowers`, `maxFollowers`, `mustMention[]`, `excludeStaffingAgencies` (default true), `maxCompanies`, `maxPagesToCheck` (default 6 × `maxCompanies`), `expandSimilar`, `lookAlikeDepth` (1-3), `includePosts`.

`saliga/linkedin-company-scraper`: `companies[]` (links, page names or domains), `websites[]`, `includePosts`, `maxPostsPerCompany` (≤ 10), `skipReposts`, `outputMode` (`companies` | `posts`), `onlyNewPosts`, `monitorName`.

`saliga/linkedin-jobs-scraper`: `keywords[]`, `locations[]`, `searchUrls[]` (any linkedin.com/jobs search link), `maxJobsPerSearch` (≤ 1000), `postedWithin` (`any`, `24h`, `week`, `month`), `experienceLevels[]`, `jobTypes[]`, `workplaceTypes[]`, `includeJobDetails`, `excludeStaffingAgencies`, `excludeTitleKeywords[]`, `excludeCompanies[]`, `outputMode` (`jobs` | `companies`), `onlyNewJobs`, `monitorName`.

Always confirm against the live schema: `apify actors info "ACTOR_ID" --input --json --user-agent apify-awesome-skills/apify-linkedin-company-intel 2>/dev/null`.
