# Example — Maps route ("dentists in Berlin")

## Anchors

| # | Value |
|---|---|
| 1 What do you have | location query |
| 2 Input | `dentists in Berlin` |
| 3 Departments | `marketing`, `c_suite` |
| 4 Max contacts | `3` |
| 5 Format | CSV |
| 6 Scope | `verified-only` |

Optional follow-ups: `language=en`, `maxCrawledPlacesPerSearch=20`, `scrapePlaceDetailPage=true` (so address / phone come back).

Routing: unambiguous → `compass/crawler-google-places`.

## Actor input

```json
{
  "searchStringsArray": ["dentists"],
  "locationQuery": "Berlin, Germany",
  "maxCrawledPlacesPerSearch": 20,
  "language": "en",
  "scrapePlaceDetailPage": true,
  "maximumLeadsEnrichmentRecords": 3,
  "leadsEnrichmentDepartments": ["marketing", "c_suite"],
  "verifyLeadsEnrichmentEmails": true
}
```

Run it via the MCP `call-actor` tool or the script (SKILL.md Step 4). `expected_leads = 20 × 3 = 60` — under the 200-lead warning threshold, no confirm needed.

## Sample output

| Source | Business | Full Name | Job Title | Seniority | Email | Status | Quality | Phone | City |
|---|---|---|---|---|---|---|---|---|---|
| Maps | Example Dental A | Sample Contact 1 | Marketing Lead | manager | contact1@dental-a.example | ok | good | +49 30 5550001 | Berlin |
| Maps | Example Dental B | Sample Contact 2 | Owner | c_suite | contact2@dental-b.example | ok | good | +49 30 5550002 | Berlin |
| Maps | Example Dental C | Sample Contact 3 | CMO | c_suite | contact3@dental-c.example | ok | good | +49 30 5550003 | Berlin |

Deliverable header: *Scope `verified-only`, spurious-match drops: 0. Ask to re-render under a wider scope to include catch-all / unknown.* A `run_metadata.json` sidecar is written next to the CSV.
