# Schemas for the scraper + index pair

Each Actor has its own `.actor/` folder. Files per Actor:

| File | Actor A (scraper) | Actor B (index) |
|---|---|---|
| `actor.json` | yes | yes, with `usesStandbyMode` + `webServerSchema` |
| `input_schema.json` | source + scrape settings | the search filters |
| `dataset_schema.json` | the record | the record (same fields) |
| `output_schema.json` | link to default dataset | link to default dataset |
| `openapi.json` | - | Standby endpoints |

Validate with `apify validate-schema --user-agent apify-awesome-skills/apify-index-actor-development` in each project. It does not check `output_schema.json` or `openapi.json`, so check those by hand against this page.

## `actor.json`

```json
{
    "actorSpecification": 1,
    "name": "startup-funding-index",
    "title": "Startup Funding Index",
    "description": "Search accumulated startup funding records by sector, amount and date - as a batch run or a Standby API.",
    "version": "0.1",
    "meta": {
        "templateId": "ts-empty",
        "generatedBy": "<FILL-IN-TOOL-AND-MODEL>"
    },
    "inputSchema": "./input_schema.json",
    "outputSchema": "./output_schema.json",
    "storages": { "dataset": "./dataset_schema.json" },
    "usesStandbyMode": true,
    "webServerSchema": "./openapi.json",
    "dockerfile": "../Dockerfile"
}
```

Actor A's file is the same without `usesStandbyMode` / `webServerSchema`. Use `inputSchema` / `outputSchema`, not the deprecated `input` / `output` keys. Pricing does **not** go here - it is set in Console.

## Do not mix up the two output files

| File | Top-level shape | Purpose |
|---|---|---|
| `.actor/dataset_schema.json` | `{ "actorSpecification": 1, "fields": {...}, "views": {...} }` | Field definitions + table layout of the dataset |
| `.actor/output_schema.json` | `{ "actorOutputSchemaVersion": 1, "title", "properties": {...} }` | Links shown in the Output tab, built from templates |

### `dataset_schema.json`

```json
{
    "actorSpecification": 1,
    "fields": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "id": { "type": "string", "description": "Stable record key", "example": "https://example.com/startups/acme" },
            "name": { "type": "string", "nullable": true, "description": "Company name", "example": "Example Startup" },
            "sector": { "type": "string", "nullable": true, "description": "Sector", "example": "fintech" },
            "amount": { "type": "number", "nullable": true, "description": "Round size in USD", "example": 2500000 },
            "date": { "type": "string", "nullable": true, "description": "Announcement date (YYYY-MM-DD)", "example": "2025-01-15" },
            "url": { "type": "string", "nullable": true, "description": "Source page", "example": "https://example.com/news/12345" },
            "websiteMarkdown": { "type": "string", "nullable": true, "description": "Company website as Markdown, capped", "example": "# Example Startup\n\nWe build..." },
            "enrichmentError": { "type": "string", "nullable": true, "description": "Why enrichment failed, null on success", "example": null },
            "scrapedAt": { "type": "string", "description": "When the record was scraped", "example": "2025-01-15T12:00:00.000Z" }
        },
        "required": [],
        "additionalProperties": true
    },
    "views": {
        "overview": {
            "title": "Overview",
            "description": "Most important fields at a glance",
            "transformation": { "fields": ["name", "sector", "amount", "date", "url", "enrichmentError", "scrapedAt"] },
            "display": {
                "component": "table",
                "properties": {
                    "name": { "label": "Name", "format": "text" },
                    "sector": { "label": "Sector", "format": "text" },
                    "amount": { "label": "Amount (USD)", "format": "number" },
                    "date": { "label": "Date", "format": "date" },
                    "url": { "label": "Source", "format": "link" },
                    "enrichmentError": { "label": "Enrichment error", "format": "text" },
                    "scrapedAt": { "label": "Scraped at", "format": "date" }
                }
            }
        }
    }
}
```

Rules: every field has `type`, `description`, an anonymized `example`, and `nullable: true` unless the code guarantees a value. `required: []` and `additionalProperties: true` on the top-level `fields` object and on every nested object. Keep Actor A's and B's dataset schemas identical so B's results render the same way. Add `enrichmentError` (Pattern 3).

### `output_schema.json`

```json
{
    "actorOutputSchemaVersion": 1,
    "title": "Search results",
    "description": "Records that matched the filters",
    "properties": {
        "results": {
            "type": "string",
            "title": "Results",
            "description": "Matching records",
            "template": "{{links.apiDefaultDatasetUrl}}/items"
        },
        "resultsCsv": {
            "type": "string",
            "title": "Results (CSV)",
            "description": "Matching records as CSV",
            "template": "{{links.apiDefaultDatasetUrl}}/items?format=csv&clean=1"
        }
    }
}
```

Every property has `"type": "string"`. The templates point at the **default** dataset - which is why Actor A must dual-write (Pattern 1). Template variables: `links.apiDefaultDatasetUrl`, `links.apiDefaultKeyValueStoreUrl`, `links.publicRunUrl`, `links.consoleRunUrl`, `links.apiRunUrl`, `links.containerRunUrl`, `run.defaultDatasetId`, `run.defaultKeyValueStoreId`.

## Pattern 9 - Input schema editor choices

- **Dates**: `"type": "string"`, `"editor": "datepicker"` - renders a calendar and stores `YYYY-MM-DD` (add `"dateType": "absolute"`).
- **Proxy**: `"type": "object"`, `"editor": "proxy"`, default `{ "useApifyProxy": true }`.
- **Hidden field with default**: `"editor": "hidden"` + `"default": "..."` - useful, but still editable via API.
- **Hardcoded source names** (dataset name, KV store name, base URL) are `const` in code, not input fields and not hidden inputs.
- `default` reaches the Actor when the caller omits a field; `prefill` only fills the form. Put example values in `prefill`.

### Actor B `input_schema.json` (mirror of the search filters)

```json
{
    "title": "Startup Funding Index input",
    "type": "object",
    "schemaVersion": 1,
    "properties": {
        "query": { "title": "Keyword", "type": "string", "editor": "textfield", "description": "Case-insensitive match on name and description", "prefill": "payments" },
        "sector": { "title": "Sector", "type": "string", "editor": "textfield", "description": "Exact sector match, e.g. fintech" },
        "minAmount": { "title": "Minimum amount (USD)", "type": "integer", "editor": "number", "minimum": 0, "description": "Only rounds at least this large" },
        "fromDate": { "title": "From date", "type": "string", "editor": "datepicker", "dateType": "absolute", "description": "Only records on or after this date" },
        "limit": { "title": "Max results", "type": "integer", "editor": "number", "minimum": 1, "maximum": 1000, "default": 100, "description": "Each returned record is charged as one result" }
    },
    "required": []
}
```

The names must match the Standby query parameters exactly, so `parseFilters()` works on both.

## Pattern 6 - `openapi.json` must be OpenAPI 3.0

Apify's build validator rejects OpenAPI 3.1 / JSON Schema 2020 syntax:

```json
// WRONG - build fails with "must be string"
"sector": { "type": ["string", "null"] }

// RIGHT - OpenAPI 3.0
"sector": { "type": "string", "nullable": true }
```

Set `"openapi": "3.0.3"`. A minimal schema for Actor B:

```json
{
    "openapi": "3.0.3",
    "info": { "title": "Startup Funding Index API", "version": "0.1" },
    "servers": [{ "url": "https://<username>--startup-funding-index.apify.actor" }],
    "components": {
        "securitySchemes": { "bearerAuth": { "type": "http", "scheme": "bearer" } },
        "schemas": {
            "Record": {
                "type": "object",
                "properties": {
                    "id": { "type": "string" },
                    "name": { "type": "string", "nullable": true },
                    "sector": { "type": "string", "nullable": true },
                    "amount": { "type": "number", "nullable": true },
                    "date": { "type": "string", "nullable": true },
                    "url": { "type": "string", "nullable": true },
                    "enrichmentError": { "type": "string", "nullable": true }
                }
            }
        }
    },
    "security": [{ "bearerAuth": [] }],
    "paths": {
        "/search": {
            "get": {
                "summary": "Search records",
                "parameters": [
                    { "name": "query", "in": "query", "schema": { "type": "string" } },
                    { "name": "sector", "in": "query", "schema": { "type": "string" } },
                    { "name": "minAmount", "in": "query", "schema": { "type": "number" } },
                    { "name": "fromDate", "in": "query", "schema": { "type": "string", "format": "date" } },
                    { "name": "limit", "in": "query", "schema": { "type": "integer", "minimum": 1, "maximum": 1000, "default": 100 } }
                ],
                "responses": {
                    "200": {
                        "description": "Matching records",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "count": { "type": "integer" },
                                        "total": { "type": "integer" },
                                        "items": { "type": "array", "items": { "$ref": "#/components/schemas/Record" } }
                                    }
                                }
                            }
                        }
                    },
                    "400": { "description": "Invalid filter" }
                }
            }
        }
    }
}
```

The schema renders as Swagger UI on the Standby tab and Store page, and its presence counts toward publication quality. Stay inside OpenAPI 3.0: no `type` arrays, no `const`, no `$defs` anywhere in the file.

## TypeScript types

After the schemas validate, run `apify actor generate-schema-types --user-agent apify-awesome-skills/apify-index-actor-development` and type `Actor.getInput()` with the generated input interface.
