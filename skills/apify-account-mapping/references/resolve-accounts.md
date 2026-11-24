# Resolve and qualify the accounts

Every account ends this step as one LinkedIn company URL with a slug, or as an "unresolved" line with the reason. No people run starts for an unresolved account.

## Accounts arrive in three shapes

- LinkedIn company URLs. Normalize them to `https://www.linkedin.com/company/<slug>`: drop a country subdomain, the query string, and any trailing segment such as `/about`, `/jobs` or `/life`. If the user wants no firmographics, skip the Company API; the people run's `RUN_SUMMARY` already carries LinkedIn's own employee count for each company.
- Company names. Send all names in one Company API run. For every row, show the resolved name, `website`, `headquarters` and `companySize`, and keep it only when none of them contradicts what the user said (region, industry, size). A bare name goes to the best-known company of that name, which is often not the one the user means.
- CRM domains. Look up the name from the CRM record (or the domain's first label), then apply decision rule 2: the registrable domain of `website` must match. On a mismatch, run one search scraper query of the form `site:linkedin.com/company "<domain>"` and test the top two or three company pages through the Company API the same way. If none match, the account is unresolved.

## The join key

Take the slug from `slug`, or from `publicUrl` (the segment after `/company/`) when `slug` is empty, and use it everywhere: as the people run input, as the key that joins employee rows (`companySlug`) back to the firmographic row, and as the dedupe key when two inputs turn out to be one company. Two names can resolve to one page; map it once and say which inputs merged.

## Qualify against the profile before any people run

- Filter on the Company API row: `companySize`, `industries`, `headquarters`, `countryCodes`. This is the cheap step; people runs cost more time and money.
- `companySize` is the band the company states, and `employeesInLinkedin` counts profiles that list the company. They can differ by an order of magnitude (a "501-1,000 employees" band next to 7,124 profiles), so when the user gives a size range, say which number you filtered on.
- `affiliatedPages` lists subsidiaries and showcase pages. Their people list the subsidiary as employer, so they never appear in the parent's map. Add a subsidiary as its own account only when the user wants it.

## Output of this step

One table: account as given, resolved name, company page, slug, website, headquarters, size band, and status (resolved; unresolved with the reason; filtered out by the profile with the reason). Show it to the user before mapping people when any account started as a name or a domain.
