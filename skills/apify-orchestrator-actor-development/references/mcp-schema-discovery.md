# Apify MCP: sub-Actor schema discovery

Before wiring a sub-Actor into an orchestrator, you need its input schema (what fields to send) and output shape (what fields the dataset contains). Use the Apify MCP server as the primary source; fall back to the REST API when MCP is unavailable.

## MCP server

- **Hosted URL:** `https://mcp.apify.com` (OAuth-based; supported by Claude.ai, VS Code, Cursor, and Claude Code)
- **Scope with a query string:** `https://mcp.apify.com/?tools=actors,docs`
- **Docs:** <https://docs.apify.com/platform/integrations/mcp>
- **Repo:** <https://github.com/apify/apify-mcp-server>

If the user has the Apify MCP server configured, its tools are already available. Otherwise, ask them to add it — or fall back to the REST route below.

## Primary tool: `fetch-actor-details`

Returns the input schema, output schema, README (summary or full), and pricing for a given Actor ID.

**Call it once per sub-Actor** during the interactive creation flow. Example flow the agent should follow:

1. User says "add `apify/website-content-crawler` as step 1".
2. Agent calls `fetch-actor-details` with `actorId: "apify/website-content-crawler"`.
3. Agent presents the input schema back to the user, highlighting `REQUIRED`-prefixed fields.
4. Agent asks the user which input fields should be exposed as top-level orchestrator input, which should be hardcoded, and which should be derived from a previous step's output.

## Supporting tools

| Tool | Purpose |
|---|---|
| `search-actors` | Free-text search the Apify Store. Use when the user names a task ("summarize X") rather than an Actor ID. |
| `call-actor` | Trigger a Run programmatically. Rarely needed from within an orchestrator (the orchestrator itself makes the runs), but useful during scaffolding to sanity-check inputs. |
| `get-dataset-items` | Inspect a sample Run's dataset to understand the actual field shape (schemas can lie or be incomplete). |
| `get-actor-run` / `abort-actor-run` | Ops-time inspection and cancellation. |

## The truncation gotcha

`fetch-actor-details` post-processes schemas before returning them:

- Field **descriptions** are truncated to **500 chars**.
- **Enum** lists are truncated (combined string length capped at **200 chars**).
- **Required fields** get a `REQUIRED` prefix in their descriptions (because some MCP clients ignore JSON Schema `required`).

For high-fidelity scaffolding — especially for Actors with long enum lists (locales, model names, etc.) — fetch the raw `INPUT_SCHEMA.json` directly:

```bash
# Public Actors usually have their source on GitHub
curl https://raw.githubusercontent.com/<org>/<repo>/master/.actor/input_schema.json
```

Or via the Apify REST API (falls back if MCP is unavailable):

```bash
curl -s https://api.apify.com/v2/acts/apify~website-content-crawler \
    -H "Authorization: Bearer $APIFY_TOKEN" | jq .data
```

Note the tilde (`~`) replacing the slash in the actor ID for the REST URL.

## What to do with the schemas

Once fetched, the agent should:

1. **Generate a TypeScript `interface` for each sub-Actor's input** — this catches typos at build time. If the schema has an `enum`, translate it to a union of string literals.
2. **Note required fields** — those `REQUIRED`-prefixed descriptions become the fields whose values the orchestrator's own input schema must expose or hardcode.
3. **Skim the output schema (or a sample dataset)** — you need to know which output field(s) to read to feed the next step. If the output schema is missing, use `get-dataset-items` with `limit=1` on a public sample Run to peek.
4. **Cite the source** — leave a comment in `src/main.ts` next to each `client.actor(id).call(...)` linking to the Actor's Apify Store page. Future maintainers will thank you.

## Fallback: no MCP configured

If the Apify MCP server is not available in the session, use `curl` (or `fetch()` from a scratch script) against the REST API:

```
GET https://api.apify.com/v2/acts/{userOrOrg}~{actorName}
Authorization: Bearer $APIFY_TOKEN
```

Response body has `data.exampleRunInput`, `data.stats`, and enough metadata to guide scaffolding, though the input schema itself lives at `.actor/input_schema.json` inside the Actor's source and is best fetched from GitHub.
