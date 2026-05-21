---
name: apify-verified-email-finder
description: Builds a list of verified business emails from Google Maps, Google SERPs, or a user-supplied URL list. Verification happens inside the same Apify run — no third-party verifier needed. Use when user asks to find verified emails, build a leads list, scrape emails from Maps or SERP, verify emails for a URL list, or find an Apollo / Hunter alternative.
---

# Verified Email Finder

Return a list of verified business emails by routing the user's input to the right Apify Actor and turning on the leads enrichment + email verification add-ons in a single run. No third-party verifier (Hunter, NeverBounce, Apollo) needed — verification happens inside the same Actor run.

## Prerequisites
(No need to check it upfront)

The skill supports two execution paths. Pick the one that matches your environment — Steps 4 and 5 show commands for both.

**MCP path (default in Claude sessions, recommended).** If the Apify MCP server is connected, no setup is needed — auth runs through the user's Apify account. Use the `call-actor` and `get-dataset-items` MCP tools.

**Script path (CLI / scheduled / non-Claude execution).** Requires:
- `.env` file with `APIFY_TOKEN`
- Node.js 20.6+ (for native `--env-file` support)

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Step 1: Collect the six required anchor inputs
- [ ] Step 2: Route to the correct Actor (confirm if ambiguous)
- [ ] Step 3: Build the Actor input (verification always ON)
- [ ] Step 4: Run the Actor and wait
- [ ] Step 5: Apply the result-scope filter, deduplicate, and render
```

### Step 1: Collect the Six Required Anchor Inputs

Ask all six as one block before any Actor call. Don't bundle Actor-specific optional fields (country code, language, max pages) into this round — surface those as follow-ups.

1. **What do you have to start with?** — `location query` / `SERP keyword` / `URL list`. This drives the routing decision.
2. **The actual input** — the location string, the keyword(s), or the URLs themselves.
3. **Department filter** — one or more of: `c_suite`, `product`, `engineering_technical`, `design`, `education`, `finance`, `human_resources`, `information_technology`, `legal`, `marketing`, `medical_health`, `operations`, `sales`, `consulting`. Default is `any` (leave the array empty), but ask every time.
4. **Max contacts per domain / business** — passed as `maximumLeadsEnrichmentRecords`. Default `3`, but ask every time.
5. **Output format** — `CSV` or `JSON`. Ask every time.
6. **Result scope** — which leads to keep in the deliverable. The Actor always runs the same way (verification always on); this only controls post-run filtering. Pick one:
   - `verified-only` (default) — only leads with `emailVerification.result == "ok"`. Safest for cold email.
   - `verified-plus-catchall` — `ok` plus `catch_all`. Catch-all is often deliverable but unprovable.
   - `all-emails` — any lead with a non-empty `email`, regardless of verification.
   - `with-phone` — any lead with a non-empty phone number, regardless of email status. Use for call campaigns.
   - `everything` — every lead the Actor returned, even incomplete ones.


### Step 2: Route to the Correct Actor

Inspect anchor #1 and pick the Actor.

| User has to start with | Actor ID | Use when |
|---|---|---|
| Location + business type ("dentists in Berlin") | `compass/crawler-google-places` | Local leads list from Maps listings; best when user wants address / phone / hours too |
| Keyword / search query ("best CRM software") | `apify/google-search-scraper` | Contacts from whichever sites Google ranks for a topic |
| Pre-existing URL list (pasted, file path) | `vdrmota/contact-info-scraper` | User already has domains; cheapest route since no discovery step |

All three Actors share the same three add-on fields, so verification behavior is identical across routes.

**Decision examples**

| User says | Route |
|---|---|
| "Dentists in Munich" / "Lawyers in Prague" | Maps |
| "Marketing contacts at the top results for 'AI agent builder'" | Search |
| "Find emails for these 5 URLs: acme-co.example, demo-co.example..." | URL list |
| "Find HR contacts at Fortune 500 companies" | **Ask:** SERP for "Fortune 500 HR" or a URL list? |
| "Find contacts at SaaS companies in Berlin" | **Ask:** Maps for "SaaS companies in Berlin" or SERP for "SaaS companies Berlin"? Maps works best when businesses are Google-Maps-listed. |
| (User pastes both a SERP keyword AND a URL list) | **Ask:** run one route, the other, or both as separate deliverables? |

**Ambiguity rule:** if anchor #1 is unclear, ask **one** follow-up before running. Never burn Actor compute on a guessed route.

**Mixed deliverables:** if the user explicitly asks for two routes in one deliverable, run both Actors and concatenate. The `Source` column makes the mix clear; dedupe by email across the combined output.

### Step 3: Build the Actor Input

Always set these three fields, regardless of which Actor is selected.

| Field | Value |
|---|---|
| `maximumLeadsEnrichmentRecords` | anchor #4 (default `3`, min `1`) |
| `leadsEnrichmentDepartments` | anchor #3 as array, or `[]` if "any" |
| `verifyLeadsEnrichmentEmails` | `true` (always) — guard rail, never set to `false` |

Full per-Actor input parameters and example payloads are in [reference/apify-actor-usage.md](reference/apify-actor-usage.md).

**URL-list pre-validation:** before submitting URLs to `vdrmota/contact-info-scraper`, parse each one and check it is http/https and parseable. Skipped entries must appear in the output as `skipped — invalid URL`, never silently dropped.

### Step 4: Run the Actor

Maps and SERP runs with leads enrichment can take several minutes per query. Raise the timeout for large jobs.

**MCP path (default in Claude sessions):**

Call the `call-actor` tool:
- `actor`: one of the three Actor IDs (`compass/crawler-google-places`, `apify/google-search-scraper`, `vdrmota/contact-info-scraper`)
- `input`: the JSON payload from Step 3
- `callOptions`: `{"timeout": 1800, "memory": 4096}` for a generous budget

The tool returns `runId` and `datasetId`. If `status` is still `RUNNING`, poll with `get-actor-run` (waitSecs up to 45) until `SUCCEEDED`. Capture both IDs for the `run_metadata.json` sidecar.

**Script path (CLI / scheduled use):**

```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "ACTOR_ID" \
  --input 'JSON_INPUT' \
  --output YYYY-MM-DD_verified-emails.csv \
  --format csv \
  --timeout 900
```

Use `--format json` for JSON. The script writes the raw dataset to disk; Step 5 still applies the spurious-match + scope filters on top.

### Step 5: Filter, Deduplicate, and Render

Pull the dataset:
- **MCP path:** call `get-dataset-items` with the `datasetId` from Step 4. Use the `fields` parameter (e.g., `title,searchString,countryCode,city,address,phone,website,leadsEnrichment`) and `clean: true` to keep the response small. For datasets that still exceed the response cap, fetch directly via `curl https://api.apify.com/v2/datasets/<id>/items?fields=...&clean=true` and pipe through `jq`.
- **Script path:** the raw dataset is already on disk in the file from Step 4.

Each record contains business fields plus a `leadsEnrichment` array (Maps, SERP) or top-level lead fields (URL list). Each lead has a `departments` array, a `companyWebsite`, and an `emailVerification` object with `result` (`ok` / `invalid` / `disposable` / `catch_all` / `unknown` / `error`) and `quality` (`good` / `risky` / `bad`).

- **Spurious-match filter (mandatory, always on).** Apply this **first**, before any other filter. The lead-enrichment service can return global-fallback leads when no local match exists (real case observed: a single US-zoo CFO whose `companyWebsite=zoo.org` was attributed to 8 unrelated Polish zoos because the matcher latched onto the `zoo` substring). Drop any lead whose `companyWebsite` hostname doesn't equal the source URL's hostname (strip `https?://`, leading `www.`, anything after `/`; lowercase). Count drops in `run_metadata.json` and call them out in the deliverable header if non-zero.

- **Filter by result scope** (anchor #6). Applied second.

  | Scope | Row-keep logic |
  |---|---|
  | `verified-only` | `emailVerification.result == "ok"` |
  | `verified-plus-catchall` | `emailVerification.result in {"ok", "catch_all"}` |
  | `all-emails` | `email` is non-empty (any result, including missing verification) |
  | `with-phone` | `phone` (or company phone) is non-empty (regardless of email) |
  | `everything` | keep every lead, no filter |

- **Dedupe:** group by lowercased email; keep the first occurrence and merge `Source Query or URL` if the same email appears from multiple sources. For `with-phone` rows that have no email, dedupe by lowercased phone instead.
- **Empty-result surfacing:** if the department filter (anchor #3) produces zero leads for a given domain, include a row for that domain with `Email = ""` and `Email Verification Status = "no leads matched filter"`. Do not silently drop it. This is separate from the result-scope filter above — empty-domain rows are inserted before scope-filtering and always shown.

Output row schema (16 columns, including `Departments`) and per-format rendering details are in [reference/output-formats.md](reference/output-formats.md).

## Worked Examples

- Maps: [examples/example-maps-input.md](examples/example-maps-input.md)
- SERP: [examples/example-search-input.md](examples/example-search-input.md)
- URL list: [examples/example-url-list-input.md](examples/example-url-list-input.md)

## Quality Rules (always enforce)

- **Guard rail:** never submit a run with `verifyLeadsEnrichmentEmails: false`.
- **Provenance & traceability:** populate the `Source` column on every row; carry Apify `runId` + `datasetId` in `run_metadata.json`.
- **No fabrication:** missing dataset fields stay blank.
- **Deliverable header transparency:** state the active result scope and the spurious-match drop count; offer to re-render under a different scope.
- **Ambiguity confirm:** if anchor #1 is unclear, ask before running.

## Cost & Pricing

Email verification is charged only for **decisive** results (`ok` / `invalid` / `disposable`); `catch_all` / `unknown` / `error` are free. Leads enrichment is charged per successfully extracted lead. Check the Apify console for live rates (they vary by subscription tier and change over time).

## Error Handling

See [reference/troubleshooting.md](reference/troubleshooting.md).
