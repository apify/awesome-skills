# Actor index, apify-linkedin-company-employees

Routing table for the three Actors this skill uses. All three are built and published by the author of the skill (see the Disclosure in SKILL.md). Prices are Store list prices at the time of writing; confirm with `apify actors info "<actor-id>" --json --user-agent apify-awesome-skills/apify-linkedin-company-employees 2>/dev/null`.

| Platform | User intent | Actor ID | Tier | Notes |
|----------|-------------|----------|------|-------|
| LinkedIn | Owners, founders, C-level, VPs and directors at named companies, by department | `george.the.developer/linkedin-decision-makers-finder` | community | Pay per event. `decision-maker` $0.022 per company-matched row, `actor-start` $0.00005. Everyone below director skipped before charge. Caps: `maxDecisionMakersPerCompany` 1 to 50 (default 10), 200 companies per run, default run charge limit $5, timeout 20 min. Free diff row with `compareWithPreviousRun`. |
| LinkedIn | Employees at named companies filtered by title, seniority, location, industry; leaders only with `decisionMakersOnly` | `george.the.developer/linkedin-company-employees-scraper` | community | Pay per event. `short-profile` $0.01 per company-matched row, `actor-start` $0.05 per run. Caps: `maxEmployees` 1 to 100 per company (default 25), 200 companies per run, 30 `targetTitles`, default run charge limit $1, timeout 20 min. Free `company-diff-summary` row with `compareWithPreviousRun`. |
| LinkedIn | Website domains to verified LinkedIn company pages with headcount and followers | `george.the.developer/linkedin-company-by-domain` | community | Pay per event. `company-resolved` $0.0075 per high or medium confidence row, `apify-actor-start` $0.002. Unresolved, low confidence and cached (30 days) rows free. Caps: 50,000 domains per run, `maxDomains` default 1000, default run charge limit $25, timeout 2 h. `mode: "monitor"` diffs name and headcount per `monitorBatchId`. |

## Chaining

Domain resolver `linkedinUrl` (keep `confidence` high or medium) feeds `companies` on either people Actor. Both people Actors accept LinkedIn company URLs and plain names mixed in one array.

## How to extend

1. Fetch a live input schema: `apify actors info "george.the.developer/linkedin-company-employees-scraper" --input --user-agent apify-awesome-skills/apify-linkedin-company-employees 2>/dev/null`
2. Add a row above with the user intent that should trigger it.
