# Output Formats

One row per contact (subject to anchor #6 scope), in CSV or JSON.

## Row schema (16 columns)

The lead object lives on `leadsEnrichment[]` for Maps and SERP; URL-list leads sit on the same field inside a per-domain merged record. Field names are the actual keys the Apify lead-enrichment service returns.

| Column | Source field |
|---|---|
| `Source` | Literal: `Maps`, `Search`, or `URL list` (set by the route used) |
| `Source Query or URL` | Original search string or input URL |
| `Business / Domain` | `title` (Maps) / domain of `url` (SERP) / start URL host (URL list) |
| `Full Name` | `leadsEnrichment[].fullName` |
| `Job Title` | `leadsEnrichment[].jobTitle` |
| `Departments` | `leadsEnrichment[].departments` joined with `\|` (array of enum strings; often empty) |
| `Seniority` | `leadsEnrichment[].seniority` (`entry` / `manager` / `director` / `c_suite` / etc., blank if unavailable) |
| `Email` | `leadsEnrichment[].email` |
| `Email Verification Status` | `leadsEnrichment[].emailVerification.result` (`ok` / `invalid` / `disposable` / `catch_all` / `unknown` / `error`) |
| `Email Verification Quality` | `leadsEnrichment[].emailVerification.quality` (`good` / `risky` / `bad`) |
| `LinkedIn` | `leadsEnrichment[].linkedinProfile` |
| `Phone` | place `phone` if present (Maps) else `leadsEnrichment[].companyPhoneNumber` |
| `City` | `leadsEnrichment[].city` (or place `city` for Maps) |
| `Country` | `leadsEnrichment[].country` (or place `countryCode` for Maps) |
| `Business Address` | place `address` (Maps only; blank for SERP / URL list) |
| `Business Website` | place `website` / `url` / `leadsEnrichment[].companyWebsite` |
| `Date Scraped` | run finish time (ISO 8601) |

**Notes:**

- `departments` is a **plural array** on the lead (not a string field called `department`). Often empty, but populated for ~30% of leads with values like `["marketing"]` or `["c_suite", "finance"]`. Join with `|` for the CSV column.
- Missing fields stay blank — never invent a value.

## Filter & dedupe

1. **Spurious-match filter (mandatory, always on).** The lead-enrichment service sometimes returns global-fallback leads when no local match exists — e.g., a US-zoo CFO with `companyWebsite=zoo.org` attributed to 8 unrelated Polish zoos because the matcher latched onto the `zoo` substring.

   Row-keep logic: extract hostnames (strip `https?://`, leading `www.`, anything after `/`; lowercase) from both the source URL and the lead's `companyWebsite`, and keep only if both non-empty and equal. The source URL is `place.website` (Maps), the SERP result `url` (Search), or the original `startUrls[].url` (URL list). If either hostname is empty, drop the lead.

   Count drops in `run_metadata.json` under `stats.spuriousMatchesDropped` and surface in the deliverable header if non-zero.

2. **Result-scope filter (anchor #6).** Applied after spurious-match.

   | Scope | Row-keep logic |
   |---|---|
   | `verified-only` (default) | `emailVerification.result == "ok"` |
   | `verified-plus-catchall` | `emailVerification.result in {"ok", "catch_all"}` |
   | `all-emails` | `email` is non-empty (any result, including missing verification) |
   | `with-phone` | place `phone` or `companyPhoneNumber` is non-empty (regardless of email) |
   | `everything` | no filter |

3. **Dedupe:** for scopes that produce email rows, group by `email.toLowerCase()`. Keep the first occurrence. If the same email comes from multiple sources, concatenate `Source Query or URL` with ` | `. For `with-phone` rows that have no email, dedupe by lowercased phone instead.
4. **Empty-result rows:** if the **department filter** (anchor #3) produced zero leads for a given domain, include one row for that domain with blank `Email` and `Email Verification Status = "no leads matched filter"`. These rows are inserted before result-scope filtering and are always shown — they tell the user the filter narrowed too much.
5. **Invalid-URL rows (URL-list route only):** include one row per pre-skipped URL with `Email Verification Status = "skipped — invalid URL"`. Also always shown.

State both the active result scope **and** the spurious-match drop count in the deliverable header.

## Rendering

Post-process the raw dataset (from `get-dataset-items` or the script's output file) the same way regardless of route:

1. Flatten `leadsEnrichment` so each lead becomes its own row.
2. Apply both filters (spurious-match, then scope).
3. Dedupe.
4. Project to the 16 columns above (CSV) or to a `contacts` array (JSON).

**CSV deliverable** — one header row, one row per lead, trailing `RUN_METADATA` row: `RUN_METADATA, runId=..., datasetId=..., actor=..., finishedAt=...`.

**JSON deliverable** — envelope:
```json
{
  "runMetadata": {"runId": "...", "datasetId": "...", "actor": "...", "finishedAt": "...", "consoleUrl": "https://console.apify.com/actors/runs/..."},
  "filter": {"scope": "verified-only", "rowKeepLogic": "emailVerification.result == 'ok'"},
  "contacts": [ /* ... */ ]
}
```

**Sidecar** — always write `run_metadata.json` next to the deliverable with the same `runMetadata` fields plus `stats` (placesScraped, rawLeads, spuriousMatchesDropped, keptUnderScope). For multi-route deliverables, `actor` / `runId` / `datasetId` become arrays in matching order.
