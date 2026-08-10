---
name: apify-company-website-metadata
description: Extract source-backed company name, description, and industry candidates from one public company website domain with provenance and explicit CRM review gates. Use when the user says enrich a company from its domain, get company metadata from a website, prepare a company record for CRM review, inspect website metadata, or turn a company domain into reviewable structured data. Do not use for registry, credit, financial, contact, email, people, or compliance data.
author: BRAINIALL
author_url: https://www.brainiall.com
---

# Company website metadata for CRM review

Turn one bare company domain into website-derived metadata candidates using the public Apify Actor `vivid_astronaut/company-enrichment`. Preserve the source URL and caveat in every result. Never present website metadata as registry truth, financial data, contact enrichment, or a decision.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via `apify login`, `APIFY_TOKEN`, or [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)
- One public company website domain that the user is authorized to process

## Scope gate

Use this skill only when the requested fields can be sourced from the public website itself:

- company name candidate
- description candidate
- industry candidate when present
- canonical website URL and observation time

Stop and explain the mismatch when the user needs legal identity, registration status, owners, revenue, employee count, credit, sanctions, contacts, email addresses, technology stack, or Verification/KYB. This Actor intentionally does not provide those fields.

## Workflow

1. Confirm the user supplied exactly one bare domain. Remove neither ambiguity nor credentials silently. Reject schemes, ports, paths, wildcards, spaces, email addresses, and more than one domain.
2. Inspect the live Actor schema and pricing before the first run. The current documented result price is US$0.005 plus a small Actor-start event, but the live Store price is authoritative.
3. Run one domain only. Do not retry an ambiguous failure automatically and do not convert a failed run into a guessed result.
4. Accept a dataset item only when `success` is `true`, `provenance.method` is `website_metadata_scrape`, `provenance.sourceUrl` is present, and the caveat says the fields are candidates rather than registry data.
5. Present the candidates in a review table and ask the user to approve them before any CRM write. This skill does not write to a CRM.

## Calling the Actor

Inspect the input first:

```bash
apify actors info "vivid_astronaut/company-enrichment" --input \
  --json \
  --user-agent apify-awesome-skills/apify-company-website-metadata \
  2>/dev/null
```

Run one bare domain:

```bash
apify actors call "vivid_astronaut/company-enrichment" \
  --input '{"domain":"example.com","integrationSource":"apify-store"}' \
  --json \
  --user-agent apify-awesome-skills/apify-company-website-metadata \
  2>/dev/null
```

Read the returned `defaultDatasetId`, then fetch the single result:

```bash
apify datasets get-items DATASET_ID --format json \
  --user-agent apify-awesome-skills/apify-company-website-metadata \
  2>/dev/null
```

The hosted MCP route is also available at:

```text
https://mcp.apify.com/?tools=vivid_astronaut/company-enrichment
```

Keep the Apify token in the client's secret storage.

## Output contract

Return a compact review table with:

| Field | Candidate | Source | Review status |
|---|---|---|---|
| Name | `nameCandidate` | `provenance.sourceUrl` | Needs approval |
| Description | `description` | `provenance.sourceUrl` | Needs approval |
| Industry | `industryCandidate` | `provenance.sourceUrl` | Needs approval |

Always state:

- website metadata is not authoritative registry data;
- an empty or failed run produced no verified candidate;
- Actor usage can incur Apify and result charges;
- no CRM record was changed.

## Troubleshooting

- `domain must be a bare hostname` → ask for one value such as `example.com`; do not strip a path or credentials on the user's behalf.
- Run succeeds but dataset is empty → treat it as no result and surface the stable Actor error/run ID; do not infer metadata.
- Website blocks or returns ambiguous data → stop after the single attempt and recommend manual review or an authoritative registry source appropriate to the user's goal.
- User requests a batch → explain that this Actor accepts one domain per run. Ask for an explicit bounded list and cost approval before orchestrating multiple runs.

See [Actor routing](references/actor-index.md) and [cost and data-truth guardrails](references/gotchas.md).
