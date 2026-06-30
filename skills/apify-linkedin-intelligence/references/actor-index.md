# Actor index — apify-linkedin-intelligence

Full routing table for LinkedIn's three data pillars. The agent reads this after
`SKILL.md` to pick the right Actor for a specific intent, then **confirms the
schema** with `apify actors info "ACTOR_ID" --input --json` before running —
LinkedIn Actor input field names drift and differ between Actors.

| Pillar | User intent | Actor ID | Tier | Notes |
|--------|-------------|----------|------|-------|
| Company | Firmographics for known slugs | `dev_fusion/Linkedin-Company-Scraper` | community | Input field `profileUrls` (full `linkedin.com/company/<slug>/` URLs). **Output written to the key-value store, not the dataset.** Returns employee count, industry, HQ, followers, specialties, about. |
| Company | Firmographics, many slugs, dataset output | `harvestapi/linkedin-company` | community | Dataset output; convenient for benchmarking sets. Confirm the URL/identifier field name in the schema. |
| People | Enrich known profile URLs | `harvestapi/linkedin-profile-scraper` | community | Full profile: name, headline, current title/company, location, experience, education, skills. Input is a list of `linkedin.com/in/<handle>` URLs. |
| People | Search/discover by ICP (no URLs yet) | `harvestapi/linkedin-profile-search` | community | **The prospecting engine.** Filter by title, company, location, keywords. Confirm exact filter field names (e.g. `jobTitles`, `currentCompanies`, `locations`) and the result cap (`maxItems`). |
| Jobs | Postings from a jobs search URL | `curious_coder/linkedin-jobs-scraper` | community | Input `urls` = full `linkedin.com/jobs/search/?...` URLs (NOT keywords). `count` min is 10. `scrapeCompany: true` adds firmographics (`companyEmployeesCount`, `companyWebsite`, `companyLinkedinUrl`). |
| Jobs | Postings, dataset output, pair w/ company set | `harvestapi/linkedin-job` | community | Alternative jobs feed; confirm input shape in schema. |
| Resolver | Find exact slug / profile URL | `apify/google-search-scraper` | apify | `"<company> site:linkedin.com/company"` → slug; `"<title> <company> site:linkedin.com/in"` → people URLs. Take the first matching `organicResults[].url`. |

## Field cheat-sheet (confirm against live schema)

`curious_coder/linkedin-jobs-scraper` output keys (verified in a sibling skill):
`id`, `title`, `companyName`, `companyLinkedinUrl`, `companyWebsite`,
`companyEmployeesCount`, `location`, `country`, `postedAt`,
`postedAtTimestamp`, `salary`, `salaryInsights`, `seniorityLevel`,
`employmentType`, `jobFunction`, `industries`, `descriptionText`,
`applicantsCount`, `applyUrl`, `workplaceTypes`, `workRemoteAllowed`, `link`.

## Workflow → Actor chains

- **TAM sizing** → `harvestapi/linkedin-company` (or people/company search) → dedupe → size distribution.
- **Prospect list** → `apify/google-search-scraper` (resolve) → `harvestapi/linkedin-profile-search` (discover) → `harvestapi/linkedin-profile-scraper` (enrich).
- **Headcount benchmarking** → `apify/google-search-scraper` (slugs) → `dev_fusion/Linkedin-Company-Scraper` (read KV store) → compare `employeeCount`.
- **Hiring signals** → `curious_coder/linkedin-jobs-scraper` (search URL) → optionally `harvestapi/linkedin-profile-search` for the hiring manager.

## How to extend

1. Search for candidates: `apify actors search "linkedin <pillar>" --json --limit 20 2>/dev/null`
2. Fetch input schema: `apify actors info "ACTOR_ID" --input --json 2>/dev/null`
3. Add a row above with the user intent that should trigger it, and note its output sink (dataset vs KV store) and the exact input field name.

Prefer `apify`-maintained Actors where a comparable one exists.
