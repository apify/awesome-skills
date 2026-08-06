# Gotchas — apify-lead-scoring-enrichment

Cost guardrails and per-Actor traps to look for before you kick off a run.

## Cost guardrails

Total run cost scales with (leads × Actors enabled). For a 100-lead CSV
with all three scoring Actors + Path A enrichment:

| Actor | Rough $ per 100 URLs | Notes |
|---|---|---|
| `builtwith/builtwith-official-technology-scraper` | $0.50 – $2 | Pay-per-result; cheapest of the three. |
| `apify/website-content-crawler` (depth 0) | $0.20 – $1 | Homepage-only. Higher depth multiplies. |
| `vdrmota/contact-info-scraper` (scoring, add-on OFF) | $2 – $5 | Fetches multiple pages per domain. |
| `vdrmota/contact-info-scraper` (Path A, add-on ON) | **`max_leads × domains × ~$0.03–$0.10`** | Multiplier. 5 leads × 100 domains ≈ $15–$50, charged only for leads actually found. |
| `scalelist/bulk-email-finder-dep` | $1 – $4 (fallback only) | Only invoked for leads with a name but no email. |
| `apify/google-search-scraper` | $0.30 – $1 | 5 results × 100 domains. |
| `apify/ai-web-scraper` | $2 – $8 | LLM cost dominates; scales with blog-post count. |

**Confirmation thresholds** — surface these to the user before running:
- Estimated cost **>$5** → warn.
- Estimated cost **>$20** → require explicit confirmation.
- Always frame as "roughly $X" not a guaranteed number.

**Rule of thumb:** for CSVs over ~500 leads, do a 10-row dry run first,
inspect the sidecars, then commit to the full run. Apify credit is
non-refundable once spent.

## Content Crawler depth trap

`maxCrawlDepth: 0` = homepage only. `maxCrawlDepth: 1` = homepage + every
same-origin link found on it, which can be **50-100 pages** for a
marketing site. Multiply by the lead count and it's easy to spend $50+
without meaning to.

Set `maxCrawlPages` explicitly as a safety cap (`run_scoring.js` sets it
to `urls.length * (depth + 1)`, which is conservative but not zero risk).

## BuiltWith empty-result rows

Domains with no historical Wappalyzer-style detection return an empty
technologies array — not an error. Common causes:
- Brand-new domains not yet indexed.
- Sites behind Cloudflare full-page challenge.
- Non-web domains (e.g. `mail.company.com`).

Feed the bare apex domain (`company.com`, not `blog.company.com`) when
possible. Retry only the empty rows with a longer timeout before deciding
the domain is un-fingerprintable.

## Business-Leads-Enrichment cost multiplier

`vdrmota/contact-info-scraper` has an opt-in add-on activated by setting
`maximumLeadsEnrichmentRecords > 0`. This is what Path A enrichment uses to
return actual named people per domain.

The gotcha: `maximumLeadsEnrichmentRecords` is **per domain**. Setting it to
`10` on a CSV of 500 leads attempts up to **5,000** leads. Apify only bills
for leads successfully found, but the ceiling is real and easy to blow past.

Recommended defaults:
- SDR-style top-of-funnel prospecting: `max_leads = 3–5`
- ABM deep dive for a shortlist: `max_leads = 10–20`, but keep the CSV under 50 rows

The Actor also silently filters out large chains, social media, retail
giants, and food-delivery domains from its lead index. Enterprise B2B ICPs
are usually fine; consumer/agency ICPs may return 0 leads for many rows.

## Contact Info Scraper missing emails

The Actor scrapes visible page text; it doesn't crack:
- Cloudflare email obfuscation (the `.email-decode` class → JS-decoded on page load).
- Contact forms with no fallback mailto.
- Emails hidden behind "click to reveal" buttons.

Path A's fallback to `scalelist/bulk-email-finder-dep` covers most of
these. If a domain still returns 0 emails after fallback, the company is
probably filtering all inbound — mark the lead as "phone-only" or "form
submission required" in your outreach plan.

## Bulk Email Finder input shape

`scalelist/bulk-email-finder-dep` takes a single required key `leads`
holding an array of snake_case objects:

```json
{ "leads": [{ "first_name": "Jane", "last_name": "Doe", "company_domain": "acme.com" }] }
```

Common wrong shapes (all reject):
- `{ "people": [...] }` — wrong outer key.
- `{ "firstNames": [], "lastNames": [], "domains": [] }` — flat pluralized arrays.
- Per-lead objects with `firstName` / `lastName` — camelCase is rejected.

If a call 400s, re-fetch the schema before guessing:

```bash
apify actors info scalelist/bulk-email-finder-dep --input \
  --user-agent apify-awesome-skills/apify-lead-scoring-enrichment \
  --json 2>/dev/null
```

## Google Search Scraper query-attribution bug

Multiple `site:X` queries in one `queries` string return separate result
buckets — but the bucket's `searchQuery` field can be reformatted by the
Actor (e.g. URL-encoded, quoted). `enrich_copywriters.js` matches on the
`site:` regex which is robust to those reformattings. If a domain is
losing results, log `bucket.searchQuery` and confirm the regex still
matches.

## AI Web Scraper — null authors

Not every blog post has a byline. Sites that use:
- A single company account
- "Team" or "Editors" as the author
- No author metadata at all

...will return `author: null` (or a single word). The copywriter path
filters these out before the email-finder step, so the run doesn't waste
credits looking up "Team" at `acme.com`.

## Windows path gotcha

`node --env-file=.env` resolves the path relative to the current working
directory. On Windows Git Bash, `cd`-ing into the skill directory and
running the command works; running it from the repo root looks for
`./.env` at the repo root and fails silently (no error, just no token
loaded). Prefer absolute paths in scripted runs.
