---
name: apify-lead-scoring-enrichment
description: Score and enrich a CSV of B2B leads using Apify Actors. Takes a CSV with company URLs, free-text scoring rules, and an enrichment preference; runs BuiltWith (tech stack), Website Content Crawler (content classification), and Contact Info Scraper (company metadata) for scoring; enriches with either department-specific contacts (Contact Info Scraper + Bulk Email Finder fallback) or copywriter discovery (Google Search Scraper → AI Web Scraper → Bulk Email Finder). Outputs an enriched CSV with a numeric score and a per-lead outreach_hook column that personalizes cold email copy (e.g. "uses Shopify → send Shopify install guide"). Use when user asks to score leads, qualify leads, enrich a lead list, detect a company's tech stack for outreach, find marketing/sales/engineering contacts at a list of companies, hunt down blog copywriters for guest-post pitches, personalize cold email at scale, or turn a raw domain list into a ready-to-pitch account list.
author: Fabian Maume
author_url: https://github.com/fmaume
metadata:
  keywords: "lead-scoring, lead-enrichment, outreach, cold-email, personalization, tech-stack, builtwith, email-finder, copywriter-discovery, guest-post, prospecting, b2b, csv-workflow"
---

# Lead Scoring & Enrichment

Turn a CSV of company URLs into a scored, contact-enriched pitch list. The
agent asks the user for scoring rules in plain English ("+10 if using Shopify",
"-5 if company size <10"), picks an enrichment path (departments or
copywriters), and orchestrates six Apify Actors through four helper scripts.

## Prerequisites

- Apify account with an active `APIFY_TOKEN` ([Console → Settings → Integrations](https://console.apify.com/settings/integrations))
- Node.js 20.6+ (needed for native `--env-file` support)
- A `.env` file at the skill root containing `APIFY_TOKEN=apify_api_...`
- One-time inside `scripts/`: `npm install` (installs `csv-parse`, `csv-stringify`)

Optional but recommended: the Apify CLI (`npm i -g apify-cli`) for ad-hoc Actor
calls. The helper scripts hit the REST API directly and do not need the CLI.

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Step 1: Collect CSV path and validate required column (company_url)
- [ ] Step 2: Collect scoring rules per source (tech / content / metadata)
- [ ] Step 3: Collect enrichment path (departments OR copywriters)
- [ ] Step 4: Run scoring Actors (writes scoring.json)
- [ ] Step 5: Apply scoring rules per lead → assign per-source scores + outreach_hook (writes scored.json)
- [ ] Step 5b: Compute theoretical min/max score, ask user for qualification threshold, filter leads → qualified_leads.csv
- [ ] Step 6: Run enrichment path against qualified_leads.csv (writes enrichment.json)
- [ ] Step 7: Merge scoring + enrichment onto the ORIGINAL CSV → leads.enriched.csv (qualified column marks who made the cut)
```

### Step 1: CSV intake

Ask the user for the CSV path. Required column: `company_url`. Recognized
optional columns pass through untouched: `company_name`, `first_name`,
`last_name`, `role`, `department`. Reject the run if `company_url` is
missing. Trim to a bare domain (strip trailing slash, `www.` optional) when
feeding downstream Actors that expect a domain.

### Step 2: Scoring rules (per source)

Ask **one question per source** so it's obvious to the user (and to you at
Step 5) which data each rule tests. Ask only for the sources the user
wants to fetch — each source has a matching `--enable-*` flag in Step 4.

**2a. Tech-stack rules** — applied against
`scoring.json[url].tech` (BuiltWith output). Only ask if the user wants
`--enable-tech`. Example rules to show:

- *+10 if the company uses Shopify or WooCommerce (we sell a Shopify integration).*
- *+5 if the tech stack includes HubSpot, Marketo, or Segment (marketing-ops ICP).*
- *-3 if no analytics or CDP is detected (likely too early-stage).*

**2b. Website-content rules** — applied against
`scoring.json[url].content` (Website Content Crawler markdown/text). Only
ask if the user wants `--enable-content`. Also ask for `maxCrawlDepth`
here (default `0` = homepage only; higher = more $). Example rules:

- *+8 if the homepage describes a SaaS or platform business.*
- *-5 if the homepage describes a services agency (not our ICP).*
- *+3 if the homepage mentions "developers" or "API" (technical buyer).*

**2c. Company-metadata rules** — applied against
`scoring.json[url].metadata` (Contact Info Scraper metadata). Only ask if
the user wants `--enable-metadata`. Example rules:

- *+3 if industry is e-commerce, retail, or B2C.*
- *-3 if company size is under 10 employees (too small to buy).*
- *+5 if the company has a LinkedIn presence (bigger operation).*

Store each rule block verbatim, tagged with its source. If the user
folds a metadata rule into the tech block (e.g. "+3 if size >50" under
tech), re-file it to the correct block before Step 5 and tell them why.

Any source the user has no rules for should also be dropped from the
Step 4 `--enable-*` flags — no point paying for a signal you won't
score on. Full example rule sets: [examples/scoring-rules.example.md](examples/scoring-rules.example.md).

### Step 3: Enrichment path (pick one)

Ask: *"Which enrichment path?*
- *(A) Department contacts — find named people (with title + email) in a specific team at each company. Uses Contact Info Scraper's "Business leads enrichment" add-on, falls back to Bulk Email Finder for any lead without a discovered email.*
- *(B) Copywriter hunt — for each domain, Google-search `site:{domain} blog`, extract author names from top posts, find their emails. Good for guest-post outreach."*

For **Path A**, collect two more inputs:

1. **Department(s)** — one or more from this enum (comma-separated):
   `c_suite`, `product`, `engineering_technical`, `design`, `education`,
   `finance`, `human_resources`, `information_technology`, `legal`,
   `marketing`, `medical_health`, `operations`, `sales`, `consulting`.
   Example: `marketing,sales`.
2. **Max leads per domain** — integer. Recommend 3–5 for typical SDR work.
   ⚠️ This is a **cost multiplier**: 5 leads × 500 domains = up to 2500
   billed leads. Apify only charges for leads successfully found. Warn
   the user before running if `max_leads × domain_count > 500`.

For **Path B** no additional input is needed.

### Step 4: Run scoring Actors

```bash
node --env-file=.env scripts/run_scoring.js \
  --input leads.csv \
  --output scoring.json \
  --enable-tech --enable-content --enable-metadata \
  --content-crawl-depth 0
```

`run_scoring.js` batches all URLs into a single call per enabled Actor (not
one call per lead), then reshapes the datasets into a per-URL sidecar so the
agent can look up every signal by `company_url`. Actors that weren't
`--enable-*`'d are skipped. Read the resulting `scoring.json` — its shape
is `{ "https://acme.com": { "tech": {...}, "content": {...}, "metadata": {...} }, ... }`.

### Step 5: Apply scoring rules (per source, then sum)

For each lead in `scoring.json`, run **one pass per source** using only
that source's rules from Step 2. This keeps the score auditable — if
`content_score = -5` on a lead the user expected to convert, you can
inspect exactly which content rule fired without re-deriving the whole
computation.

Produce five fields per lead:

- `tech_score` (number, or `null` if `--enable-tech` was off) — sum of
  Step 2a rule deltas against `scoring.json[url].tech`.
- `content_score` (number, or `null` if `--enable-content` was off) —
  sum of Step 2b rule deltas against `scoring.json[url].content`.
- `metadata_score` (number, or `null` if `--enable-metadata` was off) —
  sum of Step 2c rule deltas against `scoring.json[url].metadata`.
- `score` (number) — sum of the three above, treating `null` as `0`.
- `outreach_hook` (string, one sentence) — the single most-personalizable
  signal across **all** sources: a specific CMS ("uses Shopify"), a
  named analytics tool, an industry match, a hiring signal in the copy
  — whatever a human sales rep would open the email with.

The `null` vs `0` distinction matters: a source that wasn't fetched must
not be conflated with a source that was fetched and simply scored zero.
Downstream CSV columns render `null` as blank, `0` as `"0"`.

Store scored rows as an intermediate `scored.json` (agent writes it
directly, keyed by canonical `https://domain`), then pass it to
`filter_qualified.js` at Step 5b and to `merge_output.js` at Step 7.

### Step 5b: Qualification threshold gate

Enrichment is the expensive part — running it on unqualified leads
burns credits with no ROI. Gate it with a user-set threshold before you
call any enrichment Actor.

1. **Compute the theoretical score range** from the Step 2 rules the
   user gave. For each source's rule set, sum every positive delta into
   `max_source` and every negative delta into `min_source`. Then
   `min_total = min_tech + min_content + min_metadata` and same for
   `max_total`. This is a hard bound: no lead can score outside it.
2. **Also compute the observed range** from `scored.json` — the actual
   minimum and maximum `score` values across all leads. Often the
   observed range is much narrower than the theoretical one.
3. **Present both to the user, plus a rough tiering suggestion:**

   > *"Theoretical range: **{min_total} to {max_total}**. Observed range
   > in your list: **{observed_min} to {observed_max}** across
   > **{n_leads}** leads. Distribution: {count above 75th percentile} /
   > {count above 50th percentile} / {count above 25th percentile} at
   > those thresholds. What threshold do you want? Leads scoring at or
   > above the threshold move to enrichment; everything below is
   > flagged in the final CSV as `qualified=false` and skipped."*

   Recommend the 75th-percentile score as a starting point if the user
   is unsure — enrichment cost drops ~75% while keeping the top of the
   funnel. Warn if their chosen threshold would qualify 0 leads or
   qualify all of them (no filtering).

4. **Mark `qualified: true|false`** on every row in `scored.json` based
   on the chosen threshold (write it back), then run:

   ```bash
   node scripts/filter_qualified.js \
     --leads leads.csv \
     --scores scored.json \
     --output qualified_leads.csv
   ```

   `filter_qualified.js` is a pure-Node CSV filter — it reads
   `scored.json`, keeps only rows where `qualified === true`, and
   writes them to `qualified_leads.csv` preserving all original columns.
   The full lead list (including unqualified rows) still lives in the
   original `leads.csv` — Step 7's merge uses that as the join base.

### Step 6: Run enrichment path (qualified leads only)

Feed **`qualified_leads.csv`** from Step 5b into the enrichment scripts,
not the original `leads.csv`. This is where the threshold gate pays for
itself.

**Path A — Department contacts:**

```bash
node --env-file=.env scripts/enrich_departments.js \
  --input qualified_leads.csv \
  --department marketing,sales \
  --max-leads 5 \
  --output enrichment.json
```

Add `--verify-emails` to also validate every returned email (small extra
charge per verified/invalid/disposable result; catch-all and unknown are
free per the Actor docs).

**Path B — Copywriter hunt:**

```bash
node --env-file=.env scripts/enrich_copywriters.js \
  --input qualified_leads.csv \
  --output enrichment.json
```

Path A calls `vdrmota/contact-info-scraper` with the **Business leads
enrichment** add-on enabled (`maximumLeadsEnrichmentRecords` +
`leadsEnrichmentDepartments`) so the Actor returns actual people
per domain — name, title, work email, LinkedIn. For any lead that comes
back without a resolved email, the script calls
`scalelist/email-finder` on the `(firstName, lastName, domain)`
triple as a fallback. Path B chains
`apify/google-search-scraper` → `apify/ai-web-scraper` (with the
[`get-author-name-from-blog-post`](https://apify.com/apify/ai-web-scraper/examples/get-author-name-from-blog-post)
example input) → `scalelist/email-finder`.

### Step 7: Merge

```bash
node scripts/merge_output.js \
  --leads leads.csv \
  --scoring scoring.json \
  --enrichment enrichment.json \
  --scores scored.json \
  --output leads.enriched.csv
```

Note that `--leads` is the **original** `leads.csv`, not
`qualified_leads.csv`. That way every input lead appears in the final
CSV — unqualified ones simply have blank enrichment columns and
`qualified=false`. This preserves the audit trail: you can see which
leads got scored below threshold and why.

`merge_output.js` is pure Node (no Actor calls). It left-joins on
`company_url` and emits `leads.enriched.csv` with the original columns plus:
`tech_summary`, `content_summary`, `company_size`, `industry`,
`tech_score`, `content_score`, `metadata_score`, `score` (sum),
`qualified` (`true` / `false` — matches Step 5b threshold), `outreach_hook`,
`leads` (full JSON of the per-domain people found via Path A),
`lead_names` and `lead_titles` (semicolon-separated summaries for CSV
readability), `emails` (semicolon-separated), and `authors` (Path B).

## Actor routing

| User intent | Actor | Tier | Notes |
|---|---|---|---|
| Detect tech stack | [`builtwith/builtwith-official-technology-scraper`](https://apify.com/builtwith/builtwith-official-technology-scraper) | community | Input: `{ "startDomains": ["acme.com", ...] }` (bare domains, no protocol). CMS, analytics, hosting drive outreach hooks. |
| Website content classification | [`apify/website-content-crawler`](https://apify.com/apify/website-content-crawler) | apify | Set `maxCrawlDepth: 0` for homepage only; higher = more $. |
| Company metadata (scoring path) | [`vdrmota/contact-info-scraper`](https://apify.com/vdrmota/contact-info-scraper) | community | Add-on **OFF**. Returns emails/phones/socials + company metadata from About/Contact pages. |
| Dept-specific leads (Path A enrichment) | [`vdrmota/contact-info-scraper`](https://apify.com/vdrmota/contact-info-scraper) | community | Add-on **ON** via `maximumLeadsEnrichmentRecords` + `leadsEnrichmentDepartments` (enum). Returns actual people: name, title, work email, LinkedIn. |
| Blog discovery | [`apify/google-search-scraper`](https://apify.com/apify/google-search-scraper) | apify | Query `site:{domain} blog`, `resultsPerPage: 5`. |
| Blog author extraction | [`apify/ai-web-scraper`](https://apify.com/apify/ai-web-scraper) | apify | Use example `get-author-name-from-blog-post`. |
| Email finder fallback | [`scalelist/email-finder`](https://apify.com/scalelist/email-finder) | community | Input: `{ "leads": [{ "first_name", "last_name", "company_domain" }] }`. Called only for leads with a name but no email. |

Full input schemas and quirks: [references/actor-index.md](references/actor-index.md).

## Calling Actors — the CLI recipe

Every `apify` CLI call must carry three flags (CI-enforced):

```bash
apify actors call ACTOR_ID \
  -i 'JSON_INPUT' \
  --user-agent apify-awesome-skills/apify-lead-scoring-enrichment \
  --json 2>/dev/null
```

```bash
apify actors info ACTOR_ID --input \
  --user-agent apify-awesome-skills/apify-lead-scoring-enrichment \
  --json 2>/dev/null
```

```bash
apify datasets get-items DATASET_ID \
  --user-agent apify-awesome-skills/apify-lead-scoring-enrichment \
  --format json 2>/dev/null
```

The helper scripts use the REST API directly and set the same
`apify-awesome-skills/apify-lead-scoring-enrichment` user-agent header on
every request, so attribution is consistent whether you drive by CLI or by
script.

## Alternative interfaces

- **Apify MCP connector** — <https://mcp.apify.com> ([docs](https://docs.apify.com/platform/integrations/mcp)). Skip the helper scripts; the agent calls Actors as MCP tools.
- **mcpc** — standalone MCP client, <https://github.com/apify/mcpc>.

If you skip the helper scripts, you still need to apply the Step 5 scoring
logic yourself and produce the final CSV.

## Troubleshooting

- **`APIFY_TOKEN not set`** — the scripts read it from `.env` via `node --env-file=.env`. Ensure `.env` is at the directory you `cd`'d into, not in the skill dir. Absolute paths help: `node --env-file=/abs/path/.env scripts/...`.
- **`fetch failed` on Node <20.6** — `--env-file` requires 20.6+. Check `node --version`. Upgrade or export `APIFY_TOKEN` manually in the shell.
- **BuiltWith returned empty for a URL** — the domain is unreachable, WAF-blocked, or new (no historical detections). Feed the bare domain (`acme.com`) not the full URL, and retry the failed rows only.
- **Contact Info Scraper returned 0 leads for a domain** — the domain is filtered out by the Actor's built-in exclusion list (large chains, social platforms, retail giants, food-delivery services), or the site has no discoverable employees in the requested department. Try broader departments (e.g. add `c_suite` alongside `marketing`) or fall back to the copywriter path for that segment.
- **Lead has a name but no email** — the Business-Leads add-on couldn't resolve one. Path A auto-falls-back to `scalelist/email-finder` on `(firstName, lastName, domain)`. If the fallback also returns nothing, the person's email is genuinely not in Scalelist's index — try LinkedIn Sales Navigator manually or drop the row.
- **Copywriter path returns 0 authors for a domain** — the domain has no blog, or blog posts don't expose an author byline. Skip the row; guest-post outreach isn't the right play for that domain.
- **Ran out of Apify credits mid-run** — no partial recovery in `run_scoring.js` v1. Re-run against a smaller CSV slice. See [references/gotchas.md](references/gotchas.md) for cost estimates per Actor.
