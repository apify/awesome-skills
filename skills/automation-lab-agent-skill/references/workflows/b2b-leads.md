# B2B leads workflow

Use when the user asks for B2B prospecting, company research, employee lists, LinkedIn company data, vendor directories, agency discovery, review-backed lead scoring, Trustpilot ratings, or Clutch profiles.

## Trigger phrases

- "build a lead list"
- "find companies and employees on LinkedIn"
- "scrape LinkedIn company pages"
- "enrich vendors with Trustpilot/Clutch ratings"
- "find agencies in Clutch"
- "company posts/jobs as buying signals"

## Actor routing

| Need | Actor ID |
|---|---|
| LinkedIn company profile data | `automation-lab/linkedin-company-scraper` |
| LinkedIn employee lists | `automation-lab/linkedin-company-employees-scraper` |
| LinkedIn company posts | `automation-lab/linkedin-company-posts-scraper` |
| LinkedIn post details | `automation-lab/linkedin-post-scraper` |
| LinkedIn jobs / hiring signals | `automation-lab/linkedin-jobs-scraper` |
| Trustpilot reviews/ratings | `automation-lab/trustpilot` |
| Trustpilot company metadata | `automation-lab/trustpilot-scraper` |
| Clutch agency/vendor profiles | `automation-lab/clutch-scraper` |

## Input schema hints

Fetch schema. B2B Actors often accept:

- `startUrls`/`urls` for company pages, profile pages, Clutch categories, or Trustpilot pages
- `query`, `keyword`, industry/category/location filters
- `maxItems`, `maxResults`
- optional department/seniority filters if employee extraction supports them

Ask for target market, geography, ICP filters, and desired lead count if absent.

## Example payloads

```bash
apify actors call "automation-lab/linkedin-company-scraper" -i '{"startUrls":[{"url":"https://www.linkedin.com/company/example/"}],"maxItems":25}' --user-agent automation-lab-agent-skill --json 2>/dev/null
```

```bash
apify actors call "automation-lab/linkedin-company-employees-scraper" -i '{"companyUrls":["https://www.linkedin.com/company/example/"],"maxItems":100}' --user-agent automation-lab-agent-skill --json 2>/dev/null
```

```bash
apify actors call "automation-lab/clutch-scraper" -i '{"query":"software development agencies fintech New York","maxItems":100}' --user-agent automation-lab-agent-skill --json 2>/dev/null
```

## Output normalization

Normalize company-level rows to:

- `companyName`
- `companyUrl`
- `linkedinUrl`
- `website`
- `industry`
- `location`
- `employeeCount`
- `rating`
- `reviewCount`
- `sourcePlatform`
- `sourceActor`

Normalize person-level rows to:

- `fullName`
- `title`
- `companyName`
- `linkedinProfileUrl`
- `location`
- `sourceActor`

For lead scoring, combine firmographic fit, hiring/activity signals, review sentiment, and source confidence.
