---
name: apify-linkedin-intelligence
description: Turn LinkedIn into a B2B go-to-market data source using Apify Actors across the three LinkedIn data pillars — company firmographics, people profiles, and job postings. Use for TAM sizing (count and size companies in a market), prospect / lead list building (find decision-makers by title, company, seniority, geo), headcount benchmarking (compare employee counts and growth across competitors), and hiring-signal selling (turn new job postings into buying signals and timed outreach). Trigger phrases include "size my TAM on LinkedIn", "build a prospect list of <title> at <companies>", "find decision makers / ICP contacts", "how many employees does <company> have", "benchmark headcount vs competitors", "who is hiring for <role>", "hiring signals for sales", "LinkedIn company / people / jobs scraper", or "enrich these LinkedIn URLs". Chains firmographics + people + jobs instead of a single scraper, and confirms input schemas before running because LinkedIn Actor inputs drift.
author: Yoghesh D
author_url: https://github.com/yogeshd
---

# LinkedIn intelligence for B2B go-to-market

Turn LinkedIn's three data pillars — **companies** (firmographics), **people** (profiles), and **jobs** (postings) — into four sales/RevOps workflows: TAM sizing, prospect list building, headcount benchmarking, and hiring-signal selling.

## The key insight

LinkedIn value comes from **chaining the three pillars**, not from any one scraper:

- A **company search** gives you the *accounts* in a market (TAM).
- A **people search** inside those accounts gives you the *contacts* (prospects).
- A **jobs feed** for those accounts gives you the *timing* (hiring signals = budget + pain).

So the routing decision is "which pillar(s) does this question touch", then chain them. The output of one pillar (a company slug, a company name, a profile URL) is the input to the next.

| Pillar | Answers | Primary use |
|--------|---------|-------------|
| Company | "which/how many companies, how big" | TAM sizing, headcount benchmarking |
| People | "who are the decision-makers" | prospect/lead lists, ICP enrichment |
| Jobs | "who is hiring, for what, when" | hiring-signal selling, expansion timing |

**Always confirm the input schema before running** (`apify actors info "ACTOR_ID" --input --json`). LinkedIn Actor inputs differ between Actors and change often — the same intent ("scrape a company") uses `profileUrls` in one Actor and `companyUrls`/`identifier` in another. A wrong field name silently returns 0 results.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. **Classify the goal** into one of the four workflows below (or a combination), and identify which pillar(s) it needs.
2. **Resolve identifiers first.** LinkedIn Actors key off exact slugs/URLs, not loose names. Discover them via SERP before scraping — `apify/google-search-scraper` with `"<company> site:linkedin.com/company"` (company slug) or `"<title> <company> site:linkedin.com/in"` (people). A wrong slug returns 0 rows silently.
3. **Confirm the schema.** Run `apify actors info "ACTOR_ID" --input --json` and build input against the *actual* field names. Note where output lands (dataset vs key-value store — see gotchas).
4. **Estimate cost, then run.** LinkedIn Actors are usually `PAY_PER_EVENT` (per profile/company/job). Multiply by your row count and confirm with the user if the estimate is significant (see [references/gotchas.md](references/gotchas.md)).
5. **Deliver.** Report row count, the columns, and a link to the dataset/console. Default to CSV for lists; summarize counts/medians for TAM and benchmarking.

### The four workflows

| Workflow | Pillars chained | Recipe |
|----------|-----------------|--------|
| **TAM sizing** | Company | Search companies by industry + headcount band + geo → dedupe → report count, size distribution, and the account list. Treat counts as **modeled/directional**, not exact. |
| **Prospect list building** | Company → People | Get target accounts (or take a user list) → people-search each by title/seniority → enrich profiles → output one contact per row, deduped. |
| **Headcount benchmarking** | Company | Scrape firmographics for a competitor set → compare `employeeCount`, follower count, industry, HQ → rank. Re-run on a schedule to track headcount growth over time. |
| **Hiring-signal selling** | Jobs (→ Company → People) | Pull recent job postings for target accounts/roles → a new posting = active budget + pain → optionally chain to people-search for the hiring manager → draft timed outreach. |

## Actor routing

LinkedIn is a protected platform — **never** use a generic crawler (`website-content-crawler`, `rag-web-browser`) on `linkedin.com`. Use a dedicated Actor.

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Company firmographics | `dev_fusion/Linkedin-Company-Scraper` | community | Employee count, industry, HQ, followers, about. **Output lands in the key-value store, not the dataset.** Field is `profileUrls`. |
| Company firmographics (alt) | `harvestapi/linkedin-company` | community | Firmographics with dataset output; good when you have many slugs. |
| People profiles (enrich URLs) | `harvestapi/linkedin-profile-scraper` | community | Full profile from a profile URL: title, company, location, experience, headline. |
| People search (build lists) | `harvestapi/linkedin-profile-search` | community | Find people by keywords/title/company/location without knowing URLs — the prospecting engine. |
| Job postings | `curious_coder/linkedin-jobs-scraper` | community | Jobs from a LinkedIn jobs **search URL** (not keywords). `count` min is 10. Returns company firmographics too (`companyEmployeesCount`, `companyWebsite`). |
| Job postings (alt) | `harvestapi/linkedin-job` | community | Jobs feed with dataset output; pair with company search. |
| Resolve slugs / profile URLs | `apify/google-search-scraper` | apify | Discover the exact `linkedin.com/company/<slug>` or `linkedin.com/in/<handle>` before scraping. |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party). These are starting points — run `apify actors search "linkedin" --json --limit 20` to find current alternatives, and always confirm the schema (step 3). See [references/actor-index.md](references/actor-index.md) for the full table and field notes.

## Calling Actors — Apify CLI

Three flags on every call (`--json`, `--user-agent`, `2>/dev/null`):

    # 0. Resolve the exact company slug first (names != slugs: "Oxylabs" -> "oxylabs-io")
    apify actors call "apify/google-search-scraper" \
      -i '{"queries":"Acme Corp site:linkedin.com/company","maxPagesPerQuery":1,"resultsPerPage":5}' \
      --json \
      --user-agent apify-awesome-skills/apify-linkedin-intelligence \
      2>/dev/null

    # 1. Company firmographics (TAM / headcount benchmarking) — output is in the KV store
    apify actors call "dev_fusion/Linkedin-Company-Scraper" \
      -i '{"profileUrls":["https://www.linkedin.com/company/oxylabs-io/"]}' \
      --json \
      --user-agent apify-awesome-skills/apify-linkedin-intelligence \
      2>/dev/null

    # 2. People search (build a prospect list by title + company + geo)
    apify actors call "harvestapi/linkedin-profile-search" \
      -i '{"currentCompanies":["Acme Corp"],"jobTitles":["VP Sales","Head of Revenue"],"locations":["United States"],"maxItems":50}' \
      --json \
      --user-agent apify-awesome-skills/apify-linkedin-intelligence \
      2>/dev/null

    # 3. Enrich specific profile URLs
    apify actors call "harvestapi/linkedin-profile-scraper" \
      -i '{"profileUrls":["https://www.linkedin.com/in/some-handle/"]}' \
      --json \
      --user-agent apify-awesome-skills/apify-linkedin-intelligence \
      2>/dev/null

    # 4. Hiring signals — jobs from a LinkedIn jobs SEARCH URL (not keywords), count >= 10
    apify actors call "curious_coder/linkedin-jobs-scraper" \
      -i '{"urls":["https://www.linkedin.com/jobs/search/?keywords=Account%20Executive&location=United%20States"],"count":10,"scrapeCompany":true}' \
      --json \
      --user-agent apify-awesome-skills/apify-linkedin-intelligence \
      2>/dev/null

    # Inspect input schema (DO THIS before every new Actor) / fetch dataset results
    apify actors info "harvestapi/linkedin-profile-search" --input --json \
      --user-agent apify-awesome-skills/apify-linkedin-intelligence 2>/dev/null
    apify datasets get-items DATASET_ID --format json \
      --user-agent apify-awesome-skills/apify-linkedin-intelligence 2>/dev/null

The input fields above are **illustrative** — confirm them against each Actor's real schema before running. The Apify MCP server (<https://mcp.apify.com>) and any MCP client (e.g. `mcpc`) are equivalent alternatives.

## Troubleshooting

- **0 rows returned** → almost always a wrong slug/name/URL or wrong input field. Re-resolve the slug via SERP (step 2), and re-check the field name against `apify actors info ... --input`.
- **Company scraper "returned nothing"** → `dev_fusion/Linkedin-Company-Scraper` writes to the **key-value store**, not the dataset. Read the KV store keys after the run.
- **Jobs Actor rejects keywords** → `curious_coder/linkedin-jobs-scraper` needs a full `linkedin.com/jobs/search/?...` URL, and `count` min is 10. URL-encode multi-word values (`Bright Data` → `Bright%20Data`).
- **Headcount looks off** → LinkedIn employee/TAM counts are **modeled and directional**, not a ground-truth census. Label them as estimates; cross-check against the company website or jobs Actor's `companyEmployeesCount`.
- **Cost climbing on a big list** → these Actors bill per result. Cap `maxItems`, run a small sample first to validate the schema, then scale. See [references/gotchas.md](references/gotchas.md).
