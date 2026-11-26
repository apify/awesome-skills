# Actor routing table: company name to domain, then contacts

| Job | Actor | Key inputs | Row returned |
|-----|-------|-----------|--------------|
| Names to websites and domains | `datagleaner/company-domain-finder` | `companies` (array), or `csvUrl` + `csvNameColumn`, or `datasetId` + `datasetNameField`; optional `country`, `city`, `industry`, `minConfidence` (default 0.5) | one row per name: `found`, `domain`, `website`, `confidence`, `evidence`, `logoUrl`, `linkedinUrl`, `alternatives` |
| Names to websites plus emails and phones, one run | `datagleaner/company-domain-finder` | the above plus `findContacts: true`, `maxContactSites` (default 50, at most 500) | the domain row plus `bestEmail`, `emailList`, `phoneList`, `contactsNote` |
| Websites to emails, phones, socials | `datagleaner/website-contact-details-scraper` | `websites` (array of domains or URLs), or `datasetId` (reads `website`, `url`, `domain`), or `csvUrl` + `csvColumn`; optional `maxPagesPerSite` (default 8), `euRoleOnly`, `extractPeople` | one row per site: `status`, `bestEmail`, `emails[]` with `foundOn`, `phones[]`, socials, `contactForms` |

## Choosing between one run and two

- Up to about 500 found websites and the user wants contacts: one run with `findContacts: true`.
- More than that, or the user wants to review the domains before paying for contacts: run the domain finder, show the low-confidence rows, then run the contacts Actor with `{"datasetId": "<domain run dataset ID>"}`.

## Store and MCP

- Company Domain Finder: https://apify.com/datagleaner/company-domain-finder
- Website Contact Details Scraper: https://apify.com/datagleaner/website-contact-details-scraper
- Hosted MCP server: `https://mcp.apify.com/?tools=actors,docs,datagleaner/company-domain-finder,datagleaner/website-contact-details-scraper`
- MCP docs: https://docs.apify.com/platform/integrations/mcp
