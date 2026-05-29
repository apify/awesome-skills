---
name: apify-tech-stack-prospecting
description: >-
  Discover and qualify B2B prospects by their tech stack. Chains Google Search signal queries to find companies using specific technologies, contact-info scraping to extract decision-maker emails and phones, and LinkedIn company enrichment to add firmographic data (size, industry, headcount). Use when user asks to find companies using a specific framework or tool, build a prospect list by technology, identify companies by language or framework, find companies integrating AI into their products, locate devtools customers, qualify engineering leads by stack, or wants a list of companies to reach out to based on what they're built on.
---

# Tech Stack Prospecting

Discover companies by what they're built on, extract contact information from their sites, and enrich with firmographic data — producing a qualified B2B prospect list in a single pipeline run.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. **Clarify the target.** Ask the user for their primary technology signal (e.g., "Ruby on Rails"), a secondary qualifier (e.g., "hiring AI engineers", "uses OpenAI"), geography, and desired output format (quick preview, CSV, or JSON).
2. **Discover companies via search signals.** Build Google Search queries that surface companies *using* the stack — job postings, engineering blogs, GitHub READMEs — and run `apify/google-search-scraper`. Extract unique root domains from results; discard job boards, news sites, and directories.
3. **Extract contact information.** Feed the domain list into `vdrmota/contact-info-scraper`, crawling `/about`, `/contact`, and `/team` pages at depth 2. Capture emails, phones, and LinkedIn company URLs.
4. **Enrich with firmographics.** Pass LinkedIn company URLs from step 3 into `apify/linkedin-companies-scraper` to get company name, industry, headcount, and headquarters.
5. **Merge and deliver.** Join the three datasets on domain. Report count, file location, and top prospects. Warn the user before running enrichment on more than 100 companies — costs scale linearly.

For a worked 4-step workflow, see [apify/agent-skills ultimate-scraper](https://github.com/apify/agent-skills/blob/main/skills/apify-ultimate-scraper/SKILL.md).

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Discover companies via tech/hiring signal queries | `apify/google-search-scraper` | apify | Surfacing company domains from job postings, engineering blogs, GitHub READMEs |
| Extract emails, phones, and social links from company sites | `vdrmota/contact-info-scraper` | community | Crawling `/about`, `/contact`, `/team` pages for direct contact info |
| Add company size, industry, and headcount | `apify/linkedin-companies-scraper` | apify | Firmographic enrichment from LinkedIn company pages |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

### Signal query templates

Construct Google Search queries that surface companies **using** the technology, not articles *about* it:

| Signal type | Query template |
|-------------|---------------|
| Job posting signal | `site:linkedin.com/jobs "TECH" "ROLE"` |
| Engineering blog signal | `"built with TECH" OR "we use TECH" engineering blog` |
| GitHub README signal | `site:github.com "TECH" "SECONDARY_TECH" README` |
| Direct stack mention | `"powered by TECH" OR "built on TECH" site:*.io OR site:*.com` |

Run 3–5 queries per stack signal. 25–50 results per query is a safe default.

### Merged output columns

| Column | Source Actor |
|--------|-------------|
| `domain` | `apify/google-search-scraper` |
| `discovery_signal` | `apify/google-search-scraper` (which query surfaced it) |
| `emails` | `vdrmota/contact-info-scraper` |
| `phones` | `vdrmota/contact-info-scraper` |
| `linkedin_url` | `vdrmota/contact-info-scraper` |
| `company_name` | `apify/linkedin-companies-scraper` |
| `industry` | `apify/linkedin-companies-scraper` |
| `employee_count` | `apify/linkedin-companies-scraper` |
| `headquarters` | `apify/linkedin-companies-scraper` |

## Calling Actors — choose your interface

Skills in this repo can call Actors via any of these interfaces. Pick the one that fits your runtime; cross-tool compatibility is your responsibility.

### Option A: Apify CLI (recommended for portability)

Works in any shell-capable agent. Three flags on every call:

    apify actors call "ACTOR_ID" -i 'JSON_INPUT' \
      --json \
      --user-agent apify-awesome-skills/apify-tech-stack-prospecting \
      2>/dev/null

| Flag | Why |
|------|-----|
| `--json` | Stable machine-readable output |
| `--user-agent` | Apify telemetry attribution |
| `2>/dev/null` | Suppress progress messages that break JSON |

Other useful commands:

    # Search Actors
    apify actors search "KEYWORDS" --json --limit 10 2>/dev/null

    # Fetch Actor schema
    apify actors info "ACTOR_ID" --input --json \
      --user-agent apify-awesome-skills/apify-tech-stack-prospecting 2>/dev/null

    # Fetch results
    apify datasets get-items DATASET_ID --format json \
      --user-agent apify-awesome-skills/apify-tech-stack-prospecting 2>/dev/null

For the canonical command set with all flags, see [apify/agent-skills ultimate-scraper](https://github.com/apify/agent-skills/blob/main/skills/apify-ultimate-scraper/SKILL.md).

### Option B: Apify MCP connector

Hosted MCP server at <https://mcp.apify.com>. Documented at <https://docs.apify.com/platform/integrations/mcp>.

### Option C: MCP client of your choice (e.g. `mcpc`)

Standalone CLI client. See <https://github.com/apify/mcpc>.

## Troubleshooting

- `APIFY_TOKEN not found` → Create a `.env` file with `APIFY_TOKEN=your_token` or run `apify login`
- `0 results from Google Search scraper` → Broaden queries; remove `site:` restrictions; try alternate signal types from the query template table above
- `No emails found by contact scraper` → Company may use contact forms only; use the extracted `linkedin_url` for manual outreach
- `LinkedIn scraper rate-limited or blocked` → Reduce batch size to 20–30 companies; spread runs over time
- `Actor not found` → Actor IDs are case-sensitive; verify spelling before retrying
- For detailed cost guardrails and recovery, see [references/gotchas.md](references/gotchas.md)
