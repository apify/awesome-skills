---
name: apify-hiring-signals
description: >
  Turns LinkedIn job postings into actionable B2B sales intelligence by chaining
  three Apify Actors: (1) LinkedIn Jobs Scraper to find companies actively hiring
  for target roles, (2) Google Search Scraper to pull funding rounds, expansions,
  and growth signals for each company, and (3) Contact Info Scraper to surface
  decision-maker emails and phones from company websites.
  Use when asked to "find companies hiring [role]", "build a prospect list from
  job postings", "identify hiring signals", "generate leads from job boards",
  "which companies are investing in [department]", "find fast-growing companies
  in [industry]", "sales prospecting from LinkedIn", "map who's building a
  [team type] team", or "find companies that recently posted [job title] jobs".
author: Khaled Ben Yahya
author_url: https://github.com/kingmathers92/
---

# Hiring Signals → Sales Intelligence

Convert LinkedIn job postings into a qualified B2B prospect list enriched with
growth signals and decision-maker contacts.

---

## Non-goals

- This skill does NOT perform general competitive intelligence
- This skill does NOT replace full market research tools
- This skill ONLY uses hiring signals to identify potential buyers

---

## Why Hiring Signals?

Job postings are the strongest buying signal in B2B sales. A company posting
5 "Senior Data Engineer" roles is almost certainly evaluating data tooling.
A company hiring 10 "Account Executive" roles is scaling revenue and likely
needs sales tech. This skill surfaces those signals before your competitors do.

## Prerequisites

_(No need to check upfront — handle errors inline if they arise)_

- `.env` file containing `APIFY_TOKEN=<your_token>`
  → Get one at https://console.apify.com/account/integrations
- Node.js 20.6+ (for native `--env-file` support)

## Workflow

Copy this checklist and track progress as you go:

```
Task Progress:
- [ ] Step 1: Clarify target (role, location, industry filters)
- [ ] Step 2: Scrape LinkedIn jobs → extract company list
- [ ] Step 3: Enrich companies with Google news signals
- [ ] Step 4: Extract decision-maker contacts from company websites
- [ ] Step 5: Synthesize and deliver prospect table
```

---

### Step 1: Clarify the Target Signal

Ask the user (or infer from their message) for:

| Parameter                          | Example                                            |
| ---------------------------------- | -------------------------------------------------- |
| **Target job title(s)**            | "Data Engineer", "VP of Sales", "Head of Security" |
| **Location filter**                | "United States", "London", "Remote"                |
| **Industry filter** _(optional)_   | "SaaS", "Fintech", "Healthcare"                    |
| **Company size hint** _(optional)_ | "startups", "Series B+", "enterprise"              |
| **Max companies to return**        | Default: 20, warn before 50+                       |

**Shortcut**: For simple queries like "find 10 SaaS companies hiring data engineers in NYC", skip asking and proceed directly.

---

### Step 2: Scrape LinkedIn Jobs

**Actor**: `apify/linkedin-jobs-scraper`

First, fetch the schema so you build the input correctly:

```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/fetch_actor_details.js \
  --actor "apify/linkedin-jobs-scraper"
```

Then run the scraper:

```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "apify/linkedin-jobs-scraper" \
  --input '{
    "queries": ["JOB_TITLE"],
    "location": "LOCATION",
    "maxResults": MAX_RESULTS,
    "proxy": { "useApifyProxy": true }
  }'
```

**Extract from results**:

- `companyName` → deduplicate into a unique company list
- `companyLinkedinUrl` or `companyUrl` → use as enrichment seed
- `jobTitle`, `postedAt` → keep for context
- `companySize` → filter if user asked for size

**Fallback** — if LinkedIn returns 0 results (rate-limited or geo-blocked):

```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "apify/google-search-scraper" \
  --input '{
    "queries": ["site:linkedin.com/jobs JOB_TITLE LOCATION"],
    "maxResults": 30,
    "resultsPerPage": 10
  }'
```

Parse company names and URLs from the Google SERP titles and snippets.

---

### Step 3: Enrich with Google News Signals

We batch company enrichment queries to minimize cost and reduce API calls.

For each unique company from Step 2, run **one batched Google Search** to pull
funding rounds, expansions, product launches, and leadership changes.

**Actor**: `apify/google-search-scraper`

Build a query list where each entry is a company-specific signal query:

```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "apify/google-search-scraper" \
  --input '{
    "queries": [
      "\"COMPANY_1\" funding OR raises OR expansion OR launch 2024 OR 2025",
      "\"COMPANY_2\" funding OR raises OR expansion OR launch 2024 OR 2025",
      "\"COMPANY_3\" funding OR raises OR expansion OR launch 2024 OR 2025"
    ],
    "maxResults": 3,
    "resultsPerPage": 3,
    "countryCode": "us"
  }'
```

**Cost control**: batch all company queries in a single Actor run (pass the
full `queries` array). Do NOT run one Actor call per company.

**Extract per company**:

- Latest funding round + amount (if mentioned)
- Recent product or expansion news
- Key executive names from bylines

---

### Step 4: Extract Decision-Maker Contacts

For each company website URL gathered in Step 2, run the Contact Info Scraper
to find emails and phone numbers — especially on `/about`, `/team`, `/contact` pages.

**Actor**: `vdrmota/contact-info-scraper`

```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "vdrmota/contact-info-scraper" \
  --input '{
    "startUrls": [
      { "url": "https://COMPANY_1_WEBSITE/contact" },
      { "url": "https://COMPANY_2_WEBSITE/about" }
    ],
    "maxDepth": 1,
    "maxPagesPerStartUrl": 3,
    "proxyConfiguration": { "useApifyProxy": true }
  }'
```

**Extract**:

- `emails` array → filter out support@, info@, noreply@ — keep personal or
  role-based addresses (e.g. cto@, vp-sales@, firstname.lastname@)
- `phones` array → keep if present
- `linkedInUrls` → executive profile links if present

**Skip this step** for quick/overview queries where the user only asked for a
company list, not contact details.

---

### Step 5: Synthesize and Deliver

Assemble a prospect table sorted by signal strength (most recent funding or
highest job-posting volume first):

```
| Company | Role Posted | # Jobs | Latest Signal | Contact |
|---------|-------------|--------|---------------|---------|
| Acme Corp | Head of Data | 4 | Series B ($12M, Jan 2025) | cto@acme.com |
| Beta Inc | VP of Sales | 2 | Expansion to EU (Mar 2025) | — |
```

Always include:

- **Total companies found** and **after deduplication**
- **Actors used** and approximate credit cost
- **Suggested follow-up**: "Want me to export this as a CSV?" or "Should I
  search for the direct LinkedIn profiles of the decision-makers?"

For CSV output, re-run Step 4 scraper with `--output YYYY-MM-DD_prospects.csv --format csv`.

---

## Output Formats

| Format              | When to use              | Command flag                                       |
| ------------------- | ------------------------ | -------------------------------------------------- |
| Quick table in chat | ≤ 20 companies, overview | _(default — no flag)_                              |
| CSV                 | Full export, CRM import  | `--output YYYY-MM-DD_prospects.csv --format csv`   |
| JSON                | Downstream automation    | `--output YYYY-MM-DD_prospects.json --format json` |

---

## Cost Safety

Always cap results before running:

| Actor                          | Field to cap           | Default cap |
| ------------------------------ | ---------------------- | ----------- |
| `apify/linkedin-jobs-scraper`  | `maxResults`           | 50          |
| `apify/google-search-scraper`  | `maxResults` per query | 3           |
| `vdrmota/contact-info-scraper` | `maxPagesPerStartUrl`  | 3           |

Warn the user before running more than 50 companies through the full 3-actor
pipeline — that can consume significant credits.

---

## Error Handling

| Error                     | Cause                       | Fix                                            |
| ------------------------- | --------------------------- | ---------------------------------------------- |
| `APIFY_TOKEN not found`   | Missing `.env`              | Ask user to add `APIFY_TOKEN=xxx` to `.env`    |
| `Actor not found`         | Typo in Actor ID            | Verify spelling; re-run `fetch_actor_details`  |
| `Run FAILED`              | Auth, quota, or input error | Check Apify console link in error output       |
| `0 results from LinkedIn` | Rate-limited                | Use Google fallback in Step 2                  |
| `contacts array empty`    | No public emails on site    | Note in output; suggest LinkedIn manual lookup |
| `Timeout`                 | Too many URLs in batch      | Reduce `startUrls` to ≤ 10 per run             |
