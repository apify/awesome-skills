# Actor index — apify-eu-company-data

Per-intent routing table. The agent reads this after `SKILL.md` to pick the right Actor for a specific request. All seven Actors are built by the skill author (EuroScrape), priced per event, with a free summary row where noted.

| Platform / source | User intent | Actor ID | Tier | Notes |
|---|---|---|---|---|
| SIRENE + RNE (France, official API) | French companies by activity (`nafCodes`, `sectors`), area (`departments`, `postalCodes`, `regions`), size (`employeeRanges`, `companyCategories`), finances (`revenueMin`), age (`createdAfter`), label (`labels`) | `euroscrape/france-companies` | community | $0.004 per company, +$0.025 per company with website and contacts found (`findContacts`). `sirens` enriches an existing list. `monitorName` returns only new or changed companies on later runs. |
| SIRENE + RNE | Directors (natural persons and parent companies), VAT number, latest revenue and net income of a French company | `euroscrape/france-companies` | community | Directors are in `directors[]`; revenue is `null` when accounts are confidential. `onlyWithDirectors: true` for outreach lists. |
| Companies House (UK) | UK companies by `sicCodes`, `location`, `incorporatedInLastDays`, `statuses`, `companyTypes` | `euroscrape/uk-companies` | community | $0.004 per company including officers, +$0.025 with website and contacts found. No 10,000-result cap. |
| Companies House | Officers, accounts due dates, charges, insolvency history, previous names | `euroscrape/uk-companies` | community | `includeDetails` and `includeOfficers` are on by default; `maxOfficersPerCompany` defaults to 50. |
| VIES (European Commission) | Validate EU VAT numbers in bulk, get the registered name and address, keep an official consultation number | `euroscrape/vat-validator` | community | $0.002 per number. `requesterVatNumber` is required for the consultation number. GB numbers are explained, not checked (the UK left VIES). |
| VIES | Monthly re-check of customer VAT numbers with alerts when one becomes invalid | `euroscrape/vat-validator` | community | `monitorName` + a schedule; alerts to Telegram, Discord, Slack or a webhook. |
| Company websites (Impressum, mentions légales, legal notice) | Legal entity, registry numbers, VAT IDs, managing directors, address, emails, phones of a website's owner | `euroscrape/company-identity` | community | $0.004 per website identified; $0.004 per Google search page when `searchQueries` is used. `verifyInRegistry` checks French and UK identities in the official register. |
| Company websites | CMS, frameworks, analytics, consent tools, e-commerce platform; outdated-CMS, no-HTTPS, GDPR signals; opportunity score for agencies | `euroscrape/website-intelligence` | community | $0.02 per website analyzed (unreachable and parked sites free). Identity fields included by default. |
| Companies House, BODACC (France), state open data (NY, TX, CO, CT, OR) | Companies registered in the last N days that have no website, with the domain-age signal | `euroscrape/no-website-leads` | community | $0.005 per lead; `output: "newDomain"` keeps companies whose domain was bought around the registration; `output: "all"` adds companies with a site at $0.002 per row. Legal entities only. |
| Trusted Shops (DE, AT, CH, FR, ES, IT, NL, BE, PL, GB, PT) | Online shops by product keyword with rating, review volume, company name, address, phone, email, commercial register | `euroscrape/trusted-shops-scraper` | community | $0.002 per shop, $0.004 per company profile (`includeProfile`). `minReviews` is a proxy for order volume. |
| Trusted Shops | Customer reviews of given shops, complaints only, low-rating alerts | `euroscrape/trusted-shops-scraper` | community | `shops` + `maxReviewsPerShop` + `reviewStars: ["1", "2"]`; $0.0006 per review; `monitorName` + `alertMaxStars` for alerts. |

## How to extend

1. Search for candidates: `apify actors search "KEYWORDS" --json --limit 20 --user-agent apify-awesome-skills/apify-eu-company-data 2>/dev/null`
2. Fetch an input schema: `apify actors info "ACTOR_ID" --input --json --user-agent apify-awesome-skills/apify-eu-company-data 2>/dev/null`
3. Add a row above with the user intent that should trigger it.
