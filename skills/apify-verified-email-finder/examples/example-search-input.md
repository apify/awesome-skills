# Example — SERP route ("best CRM software")

## Anchors

| # | Value |
|---|---|
| 1 What do you have | SERP keyword |
| 2 Input | `best CRM software` |
| 3 Departments | `sales` |
| 4 Max contacts | `3` |
| 5 Format | JSON |
| 6 Scope | `verified-only` |

Optional follow-ups: `countryCode=us`, `languageCode=en`, `maxPagesPerQuery=1`.

Routing: unambiguous → `apify/google-search-scraper`.

## Actor input

```json
{
  "queries": "best CRM software",
  "maxPagesPerQuery": 1,
  "countryCode": "us",
  "languageCode": "en",
  "maximumLeadsEnrichmentRecords": 3,
  "leadsEnrichmentDepartments": ["sales"],
  "verifyLeadsEnrichmentEmails": true
}
```

Run via MCP `call-actor` or the script (SKILL.md Step 4). `expected_leads ≈ 10 × 3 = 30` — well under the warning threshold.

## Sample output (truncated to one contact)

```json
{
  "runMetadata": {
    "runId": "AbCdEfGhIjK",
    "datasetId": "LmNoPqRsTuV",
    "actor": "apify/google-search-scraper",
    "finishedAt": "2026-05-18T13:02:11Z",
    "consoleUrl": "https://console.apify.com/actors/runs/AbCdEfGhIjK"
  },
  "filter": {"scope": "verified-only", "rowKeepLogic": "emailVerification.result == 'ok'"},
  "contacts": [
    {
      "source": "Search",
      "sourceQueryOrUrl": "best CRM software",
      "business": "acme-crm.example",
      "fullName": "Sample Contact 1",
      "jobTitle": "Account Executive",
      "seniority": "manager",
      "email": "contact1@acme-crm.example",
      "emailVerificationStatus": "ok",
      "emailVerificationQuality": "good",
      "linkedin": "http://www.linkedin.com/in/example-user-1",
      "businessWebsite": "https://www.acme-crm.example",
      "dateScraped": "2026-05-18T13:02:11Z"
    }
    /* + 2 more, schema in reference/output-formats.md */
  ]
}
```

A `run_metadata.json` sidecar is written next to the JSON output.
