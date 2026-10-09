# Gotchas — apify-eu-company-data

Cost guardrails, error recovery and the pitfalls of each Actor. The agent reads this when building inputs or when a run fails.

## Cost guardrails

All seven Actors are `PAY_PER_EVENT`: $0.003 per run start plus the events below. Platform usage is included in the event prices. Apify subscribers get 10 to 30 % off.

| Actor | Events | Cap it with |
|---|---|---|
| `euroscrape/france-companies` | $0.004 per company; $0.025 per company whose website and contacts were found (`findContacts`) | `maxItems`; leave `findContacts` off for a count or a first look |
| `euroscrape/uk-companies` | $0.004 per company (profile + officers); $0.025 per company with website and contacts found | `maxItems`; `findContacts` off |
| `euroscrape/vat-validator` | $0.002 per number checked | the length of `vatNumbers` |
| `euroscrape/company-identity` | $0.004 per website identified; $0.004 per Google search page (10 results) | `maxWebsites`, `resultsPerQuery` |
| `euroscrape/website-intelligence` | $0.02 per website analyzed; $0.004 per search page; unreachable and parked sites free | `maxWebsites`, `resultsPerQuery`, `onlyWithTechnologies` |
| `euroscrape/no-website-leads` | $0.005 per lead without a website; $0.002 per other new company, only with `output: "all"` | `maxItems`, a narrower area or `activityKeywords` |
| `euroscrape/trusted-shops-scraper` | $0.002 per shop; $0.004 per company profile; $0.0006 per review | `maxShopsPerSearch`, `maxReviewsPerShop` (0 = no reviews), `minReviews` |

Estimate formulas:

```
france/uk companies ≈ $0.003 + companies × $0.004 (+ found × $0.025, found ≈ 1/3 of SMEs with findContacts)
vat                 ≈ $0.003 + numbers × $0.002
identity            ≈ $0.003 + search pages × $0.004 + websites identified × $0.004
intelligence        ≈ $0.003 + search pages × $0.004 + reachable websites × $0.02
no-website leads    ≈ $0.003 + leads × $0.005 (+ others × $0.002 with output "all")
trusted shops       ≈ $0.003 + shops × ($0.002 + $0.004 with profile) + reviews × $0.0006
```

### Confirmation thresholds (suggested)

- Estimated cost **>$5** → warn the user.
- Estimated cost **>$20** → require explicit user confirmation before running.
- Always present cost as a **rough estimate** ("around $X"), not a guarantee. Contact enrichment is the only event that cannot be predicted exactly: it is charged only when a site is found and verified.

Every Actor stops cleanly at a maximum cost set on the run (`--max-total-charge-usd` on the CLI, or the Console field): the rows already paid for are delivered, nothing is charged for unfinished work, and the run ends as `SUCCEEDED` with a message saying how many items were left.

## Common errors

| Error | Cause | Fix |
|---|---|---|
| Run `SUCCEEDED` with 0 rows (`france-companies`) | NAF code without its dot, department given as a number, or a filter combination that matches nothing | Write `"43.22A"`, `"69"`, loosen filters one at a time |
| Run `SUCCEEDED` with 0 rows (`uk-companies`) | SIC code with fewer than 5 digits, or `location` not in any registered office address | Use the 5-digit SIC 2007 code; try a town name without the county |
| `valid: false` for a number you know is valid | Wrong country prefix or a typo; VIES is strict on format | Check `syntaxValid` and the message; `vatNumberFormatted` shows what was checked |
| `memberStateUnavailable: true` | The national database behind VIES is down | Re-run later; the Actor does not mark the number invalid |
| `consultationNumber` is `null` | `requesterVatNumber` not set | Set the user's own VAT number |
| `registryCheck.found: false` (`company-identity`) | The SIREN or company number printed on the site is wrong or outdated | Report it as a finding: it is exactly what a supplier check looks for |
| Website rows missing from `website-intelligence` | Site unreachable from a datacenter and from the residential retry, parked or not HTML | Not charged; verify the domain spelling |
| Fewer French leads than UK leads in `no-website-leads` | BODACC publishes French registrations a few days later | Use `registeredInLastDays: 14` or `registeredFrom` |
| `domainCreatedOn` empty on some leads | A domain registry slowed down and the Actor stopped asking it for the rest of the run | Re-run later for those rows; `output: "newDomain"` then returns fewer leads |
| Shops without phone, email or register | Non-member profiles created by Trusted Shops carry little company data | `membersOnly: true` or `certifiedOnly: true` |

## Actor-specific notes

### `euroscrape/france-companies`

- `departments` matches companies with *any* establishment in the area, not only the headquarters; `matchingEstablishments` lists them.
- `employeeRanges` are INSEE codes: `"NN"` no employees, `"01"` 1–2, `"02"` 3–5, `"03"` 6–9, `"11"` 10–19, `"12"` 20–49, `"21"` 50–99, `"22"` 100–199, `"31"` 200–249, `"32"` 250–499, `"41"` 500–999, up to `"53"` 10,000+.
- `labels` include `rge`, `organic`, `ess`, `qualiopi`, `training_organization`, `mission_company`, `association`, `sole_proprietor`, `exclude_sole_proprietors`, `siae`, `epv`, `finess`.
- `legalForms` are INSEE legal category codes: `5710` SAS, `5720` SASU, `5499` SARL, `1000` sole proprietor.
- `websiteConfidence` is `verified_siren` when the SIREN is printed on the site, `probable` when the domain carries the name and the site shows the headquarters postal code; nothing is returned rather than a wrong site. `useGoogleSearch: true` finds a few more sites for companies whose name does not give away their domain.
- Director names are personal data under the GDPR; companies that opted out of public dissemination are never returned.

### `euroscrape/uk-companies`

- `location` is matched against the registered office, often an accountant's address.
- Monitoring runs re-check every matching company to detect changes, so keep monitored searches narrow (SIC + town, or `incorporatedInLastDays`); `monitorChanges: false` reports only new companies.
- Officer names and months of birth are personal data under UK GDPR; `includeOfficers: false` leaves them out.

### `euroscrape/vat-validator`

- Input formats are tolerant: `IE 6388047V`, `PL 526-025-09-95` and `FR40303265045` all work; the country prefix is required.
- `vatNumbersUrl` accepts a plain-text or CSV file (one number per line) or a JSON array, combined with the list.
- A GB number gets an explanatory message, not a wrong answer.

### `euroscrape/company-identity`

- `searchCountry` sets Google's country and language for `searchQueries`: `de`, `at`, `ch`, `fr`, `be`, `nl`, `it`, `es`, `uk`, `ie`. Default `de`.
- Directories, marketplaces and social networks found in search results are skipped; only company sites are read.
- `registrations[].type` names the register (`FR_SIREN`, `FR_SIRET`, `DE_HRB`, `NL_KVK`, `BE_BCE`, `UK_COMPANY`…); `verifyInRegistry` is implemented for France and the UK.
- Personal e-mail addresses printed on a site (firstname.lastname@) are kept out; role addresses (`info@`, `kontakt@`) are kept.

### `euroscrape/website-intelligence`

- No browser: detection reads HTML, scripts, headers and cookies, so it is fast and cheap, but technologies injected through a tag manager are not always seen.
- `opportunityScore` (0–100) sums the sales signals; `minOpportunityScore: 30` is a reasonable prospecting filter.
- `verifyInRegistry` is off by default here (on by default in `company-identity`).
- `searchCountry` also accepts `us`.

### `euroscrape/no-website-leads`

- Legal entities only: sole traders are never read, no director name is returned, and "care of" mentions are stripped from addresses.
- Domains checked are built from the registered name and trade name; a company trading under an unrelated brand is reported without a website.
- `domainCreatedOn` comes from the registries (RDAP for `.uk`, `.com`; Afnic open data for `.fr`); `domainRecent: true` is the strongest signal.
- `excludeHoldingsAndPropertyCompanies` is on by default: holdings, SCI and dormant shells never need a website.

### `euroscrape/trusted-shops-scraper`

- Search terms are matched in the language of the market: `"fahrrad"` (DE), `"chaussures"` (FR), `"zapatillas"` (ES); `countries: ["ALL"]` searches every market.
- The directory returns the best matches first, up to 10,000 shops per keyword; `reviewsAllTime` tracks order volume, use `minReviews` to size shops.
- Reviews cover the last 12 months, most recent first, up to 10,000 per shop; `reviewStars: ["1", "2"]` reads only complaints.
- `includeSoleTraders` is off by default: a shop run by a private person has a home address.
