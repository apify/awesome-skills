# Example — URL-list route (5 URLs in)

## Anchors

| # | Value |
|---|---|
| 1 What do you have | URL list |
| 2 Input | `https://acme-pay.example, https://demo-card.example, https://sample-bank.example, htp://broken-url, https://example-biz.example` |
| 3 Departments | `any` (empty array) |
| 4 Max contacts | `2` |
| 5 Format | CSV |
| 6 Scope | `with-phone` (call campaign — keep any lead that has a phone, regardless of email) |

Optional follow-ups: `maxRequestsPerStartUrl=10`, `maxDepth=2`, `mergeContacts=true`.

Routing: unambiguous → `vdrmota/contact-info-scraper`.

## Pre-validation

`htp://broken-url` is skipped (scheme not http/https) → emitted as a `skipped — invalid URL` row. The other four URLs go to the Actor.

## Actor input (only valid URLs)

```json
{
  "startUrls": [
    {"url": "https://acme-pay.example"},
    {"url": "https://demo-card.example"},
    {"url": "https://sample-bank.example"},
    {"url": "https://example-biz.example"}
  ],
  "maxRequestsPerStartUrl": 10,
  "maxDepth": 2,
  "mergeContacts": true,
  "proxyConfig": {"useApifyProxy": true},
  "maximumLeadsEnrichmentRecords": 2,
  "leadsEnrichmentDepartments": [],
  "verifyLeadsEnrichmentEmails": true
}
```

Run via MCP `call-actor` or the script (SKILL.md Step 4). `expected_leads = 4 × 2 = 8` — well under the threshold.

## Sample output

Under `with-phone` scope, every row needs a non-empty phone — verification status is informational, not a gate.

| Source | Business | Full Name | Job Title | Email | Status | Quality | Phone |
|---|---|---|---|---|---|---|---|
| URL list | acme-pay.example | Sample Contact 1 | Head of BD | contact1@acme-pay.example | ok | good | +1 415 555 0101 |
| URL list | acme-pay.example | Sample Contact 2 | Director, Partnerships | contact2@acme-pay.example | catch_all | risky | +1 415 555 0102 |
| URL list | demo-card.example | Sample Contact 3 | VP Sales | contact3@demo-card.example | ok | good | +1 415 555 0201 |
| URL list | sample-bank.example | Sample Contact 4 | Growth Lead |  | unknown |  | +1 415 555 0301 |
| URL list | example-biz.example | Sample Contact 5 | Account Manager | contact5@example-biz.example | ok | good | +1 415 555 0401 |
| URL list | htp://broken-url | — | — | — | skipped — invalid URL | — | — |

Deliverable header: *Scope `with-phone`, spurious-match drops: 0, 1 URL pre-skipped. Ask to re-render under `verified-only` to narrow.*
