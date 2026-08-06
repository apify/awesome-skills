# Actor index — apify-lead-scoring-enrichment

Full routing table with the input shape each script sends. All six Actors
are drivable by CLI, MCP, or the raw REST API — pick your interface. Refer
to each Actor's live schema (`apify actors info <id> --input --json 2>/dev/null`)
if you change any input beyond what's captured here.

## Scoring Actors

### `builtwith/builtwith-official-technology-scraper` (community)

**Intent:** "What technologies does this company use?"
**Cost:** pay-per-result (usually cents per domain).
**Input shape used by `run_scoring.js`:**

```json
{ "startDomains": ["acme.com", "foo.com"] }
```

Bare domains, no protocol. Passing `urls` (or full URLs) makes the Actor
succeed with zero-item output — the sidecar then attaches no `tech` block
to any lead.

**Output shape:** dataset item per domain with a `technologies` array (name +
category). Field names vary; `merge_output.js` collapses the top 8 into a
comma-separated `tech_summary` column.

**Common outreach hooks derived from tech:**
- CMS detected (Shopify, WordPress, Webflow) → link a platform-specific integration guide
- Analytics stack (GA4, Segment, Amplitude) → pitch a data-add-on
- CDP or MAP (HubSpot, Marketo) → pitch marketing ops
- No detected framework → likely a static/agency site; low value for tech-heavy products

### `apify/website-content-crawler` (apify)

**Intent:** "What does this company actually say they do?"
**Cost:** pay-per-page; homepage-only (`maxCrawlDepth: 0`) is cheapest.
**Input shape:**

```json
{
  "startUrls": [{"url": "https://acme.com"}],
  "maxCrawlDepth": 0,
  "maxCrawlPages": 1,
  "crawlerType": "playwright:firefox",
  "saveMarkdown": true
}
```

**Output shape:** `{ url, markdown, text, metadata }` per crawled page.

**Use for content-based scoring rules:** the agent reads
`content_summary` (first 240 chars of markdown) and applies user rules like
*"+5 if the site describes a SaaS business"*. Increase `maxCrawlDepth` when
homepage content is thin (e.g. marketing sites with everything on `/product`).

### `vdrmota/contact-info-scraper` (community)

**Intent:** Two very different jobs depending on whether the "Business leads
enrichment" add-on is enabled.

- **Scoring path (add-on OFF):** page-level emails/phones/socials + company
  metadata scraped from About and Contact pages. Fed to `merge_output.js`
  as the `metadata` sidecar.
- **Enrichment Path A (add-on ON):** returns actual **people** (name, title,
  work email, department, LinkedIn) working at each domain. Requires
  `maximumLeadsEnrichmentRecords > 0` and `leadsEnrichmentDepartments`.

**Cost:** pay-per-result. With the add-on, cost multiplies:
`max_leads × domains`, and Apify only charges for leads actually found.

**Input shape — scoring (add-on OFF), used by `run_scoring.js`:**

```json
{ "startUrls": [{"url": "https://acme.com"}], "maxDepth": 2, "maxRequests": 10 }
```

**Input shape — Path A enrichment (add-on ON), used by `enrich_departments.js`:**

```json
{
  "startUrls": [{"url": "https://acme.com"}],
  "maxRequestsPerStartUrl": 1,
  "mergeContacts": true,
  "maxDepth": 0,
  "maximumLeadsEnrichmentRecords": 5,
  "leadsEnrichmentDepartments": ["marketing", "sales"],
  "verifyLeadsEnrichmentEmails": false
}
```

**`leadsEnrichmentDepartments` enum** — pick one or more:

| Value | Label |
|---|---|
| `c_suite` | C-Suite |
| `product` | Product |
| `engineering_technical` | Engineering & Technical |
| `design` | Design |
| `education` | Education |
| `finance` | Finance |
| `human_resources` | Human Resources |
| `information_technology` | Information Technology |
| `legal` | Legal |
| `marketing` | Marketing |
| `medical_health` | Medical & Health |
| `operations` | Operations |
| `sales` | Sales |
| `consulting` | Consulting |

**Setup recommendations (from the Actor's own docs):**
- For leads only → `maxRequestsPerStartUrl: 1`
- For leads + maximum contact discovery → `maxRequestsPerStartUrl: 3`

**Output (add-on ON):** one item per start URL with a `leadsEnrichment`
(also seen as `leads` / `businessLeads` across Actor versions) array of
people, each with `firstName`, `lastName`, `email` (optional),
`emailVerification` (when `verifyLeadsEnrichmentEmails: true`), `title`,
`department`, and `linkedin`. `enrich_departments.js` handles all three
field-name variants defensively.

## Enrichment Actors

### `scalelist/bulk-email-finder-dep` (community)

**Intent:** Given a first name, last name, and company domain, return a
verified business email. This skill uses it **only as a fallback** — when
`vdrmota/contact-info-scraper` (Path A) or the copywriter chain (Path B)
returns a lead whose name is known but whose email wasn't discovered.
**Cost:** pay-per-found-email.
**Input shape (single required key `leads`):**

```json
{
  "leads": [
    {
      "first_name": "Jane",
      "last_name": "Doe",
      "company_domain": "acme.com",
      "company_name": "Acme Corp"
    }
  ]
}
```

Field names are **snake_case** and the required per-lead fields are
`first_name` + `last_name`. `company_domain` is preferred over
`company_name` for better match rate (per the Actor's own schema
description). Do not send the pluralized flat-array shapes seen in
older skills — this Actor rejects them.

**Output:** dataset item per input lead with `email` (or `null` when
unresolved), plus echoes of the input identifiers. Field names in the
output can be either snake_case or camelCase depending on Actor
version; `enrich_departments.js` and `enrich_copywriters.js` read both.

**When to run the fallback:** only for leads with a first+last name and
no email. Do **not** call this Actor to enumerate contacts at a domain —
that's `vdrmota/contact-info-scraper`'s job (with the
Business-leads-enrichment add-on enabled).

### `apify/google-search-scraper` (apify)

**Intent:** Discover blog posts on a domain via `site:{domain} blog`.
**Cost:** pay-per-search-page.
**Input shape:**

```json
{
  "queries": "site:acme.com blog\nsite:foo.com blog",
  "resultsPerPage": 5,
  "maxPagesPerQuery": 1,
  "countryCode": "us",
  "languageCode": "en"
}
```

**Output:** one bucket per query with an `organicResults` array. `enrich_copywriters.js`
re-attaches each bucket to its domain by regex-matching `site:...` in the
query.

### `apify/ai-web-scraper` (apify)

**Intent:** LLM-driven structured extraction from arbitrary URLs. This skill
uses the [`get-author-name-from-blog-post`](https://apify.com/apify/ai-web-scraper/examples/get-author-name-from-blog-post)
example input shape.
**Cost:** LLM tokens per URL + fetch cost.
**Input shape:**

```json
{
  "startUrls": [{"url": "https://acme.com/blog/post-1"}],
  "prompt": "Extract the author name of this blog post. Return the full name only.",
  "schema": {"type": "object", "properties": {"author": {"type": "string"}}, "required": ["author"]},
  "proxyConfiguration": {"useApifyProxy": true}
}
```

**Output:** `{ url, author }` per crawled URL, or `author: null` if no byline
was found. `enrich_copywriters.js` drops null/single-word authors before the
email-finder step.

## How to extend

If you want to swap an Actor (e.g. use a different email finder), keep the
same three-flag CLI recipe from the SKILL and update `run_scoring.js` /
`enrich_*.js` accordingly.

1. Search candidates: `apify actors search "KEYWORDS" --user-agent apify-awesome-skills/apify-lead-scoring-enrichment --json --limit 10 2>/dev/null`
2. Fetch schema: `apify actors info "ACTOR_ID" --input --user-agent apify-awesome-skills/apify-lead-scoring-enrichment --json 2>/dev/null`
3. Wire it into the matching helper script.
