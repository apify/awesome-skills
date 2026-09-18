# Actor Index — apify-jobs-data

Routing table, input schemas, anchor→field mappings, and primary/fallback pairs
for every Actor this skill uses. Read on demand when building an input (Step 3).

**Always confirm the live schema before the first run** — Actor inputs change:

```bash
apify actors info "ACTOR_ID" --input --json \
  --user-agent apify-awesome-skills/apify-jobs-data 2>/dev/null
```

If a schema fetch disagrees with the field names below, trust the schema.

**Every Actor here is pay-per-result — no subscriptions:**

- `agentx/all-jobs-scraper` (default aggregator) — community, ≈ $0.0035/job + $0.01
  start (free tier, 2026-09-16). Covers LinkedIn, Indeed, Glassdoor, ZipRecruiter and
  more in one run — **not Google Jobs**.
- `misceres/indeed-scraper` — community, ≈ $0.006/job (≈ $6/1,000, free tier,
  2026-09-16). Optional Indeed-only route.
- `memo23/glassdoor-scraper-ppr` — community, ≈ $0.00475/row + $0.005 start
  (2026-09-16). Optional salary benchmark (analysis mode). **Always set `maxItems`.**

No per-board LinkedIn subscription Actor is used — the aggregator already covers
LinkedIn. Google Jobs is not covered by any Actor in this skill. If a board is blocked
on a given run, note it in the header rather than reaching for a paid per-board Actor.

**Legal note:** these Actors scrape third-party boards against those sites' Terms of
Service (see SKILL.md Prerequisites). All routes run on Apify's infrastructure (no
user login), so they never put the user's own board accounts at risk.

---

## Job-board Actors (Step 2)

### `agentx/all-jobs-scraper` — multi-board aggregator (DEFAULT)

One run fans out across 20+ boards (LinkedIn, Indeed, Glassdoor, ZipRecruiter,
StepStone, Naukri, Bayt, Reed, Totaljobs, InfoJobs, Talent.com, Jooble, and more —
the live `platforms` enum is authoritative; Google Jobs is not in it) with
country-aware routing. Pay-per-result, no subscription.
**Fallback:** the per-board Actor for a board that returned 0 in-area rows (SKILL.md
Step 2 rule), one run, merged in Step 5.

| Anchor | Field | Notes (verified against the live schema) |
|---|---|---|
| #1 Role | `keyword` | Job title or skill string. Required. |
| #2 Location | `location` | Free-text city/region (e.g. `Berlin`) |
| #2 Location | `country` | **Full country NAME from the actor's enum** (e.g. `Germany`, `United States`) — *not* an ISO-2 code. Required, **no default** — omitting it fails validation. |
| #4 Result cap | `max_results` | Integer, **minimum 1**. **Per platform, not total** — with empty `platforms` the actor runs every platform it supports for the country (42 in the enum), so `max_results: 10` can return far more than 60 rows. Multiply by the platforms hit for the real count and cost; pin `platforms` to control it (Step 3). Required. |
| #5 Recency | `posted_since` | **String, not an integer** — natural-language window like `"1 day"`, `"1 week"`, `"2 weeks"`, `"1 month"`, `"6 months"` (default). Passing a bare number is ignored. |
| #6 job_type | `job_type` | Enum: `all` (default) / `fulltime` / `parttime` / `internship` / `contract` — **no hyphen** (`fulltime`, not `full-time`). |
| #6 remote_only | `remote_only` | `true` flips remote filter on |
| boards / **cost lever** | `platforms` | Array of exact enum values (`LinkedIn`, `Indeed`, `Glassdoor`, `Stepstone`, …); **empty = every platform the Actor supports for the country**, not ~6. Pin it whenever cost matters. |

```json
{ "keyword": "senior backend engineer", "location": "Berlin",
  "country": "Germany", "max_results": 50, "posted_since": "2 weeks",
  "job_type": "fulltime", "remote_only": false }
```

Output (verified): per-job fields include `title`, `company_name`, `location`,
`salary_minimum` / `salary_maximum` / `salary_currency` / `salary_period`, `skills`
(list), `job_type`, `job_level`, `is_remote` / `work_mode`, `posted_date`,
`applicant_count`, `easy_apply`, `platform` (the source board), and `official_url` /
`platform_url`. **Coverage varies sharply by board and region** — in a live Berlin
test only **1 of 58** postings disclosed salary, and that figure had an inconsistent
currency/period — so salary always needs coverage labeling and period normalization
(analysis.md). Rate as of 2026-09-16 (free tier): `$0.01` start + `$0.0035` / job —
and remember a job is counted per platform, so budget `max_results × platforms`.
**Confirm live in console.**

### `misceres/indeed-scraper` — Indeed only (optional, community)

Community board Actor. Cheap pay-per-result (≈ `$0.006` / job ≈ `$6` / 1,000 listings,
free tier, 2026-09-16). Only needed if the user wants Indeed exclusively; otherwise
the aggregator covers it.

| Anchor | Field | Notes |
|---|---|---|
| #1 Role | `position` | |
| #2 Location | `location` | |
| #2 Location | `country` | ISO-2; required, must match `location` |
| #4 Result cap | `maxItemsPerSearch` | **Not `maxItems`** — the schema does not reject unknown fields, so an unrecognised cap is silently ignored and the run is uncapped. |
| dedupe | `saveOnlyUniqueItems` | `true` — drops Indeed-side dupes early (helps Step 5) |

```json
{ "position": "data analyst", "location": "San Francisco", "country": "US",
  "maxItemsPerSearch": 100, "saveOnlyUniqueItems": true }
```

Output: salary, company + logo, location, company rating, full description
(text + HTML), post date, direct job URL.

### `memo23/glassdoor-scraper-ppr` — Glassdoor salary benchmark (optional, pay-per-result)

From a Glassdoor company-page URL it returns the company's jobs, reviews, salary
estimates, and more — one Actor, selected by a `command`/section field. Pay-per-result.
This skill uses it only for the **salary benchmark** in analysis mode (the `salaries`
section), to cross-check posted salary bands against Glassdoor estimates.

| Need | Field | Notes |
|---|---|---|
| Company | `startUrls` | Glassdoor **company-page URLs** (array of `{url}`). There is **no `companyName` field** — supply the Glassdoor URL (find it via a quick SERP for "<company> glassdoor"). |
| Section | `command` | `salaries` here — **always set it explicitly**; the Actor's default is `reviews`. |
| Cap | `maxItems` | **Required for cost control** — the Actor's default is 20,000 per URL (≈ $95 at the current rate); use ≤ 50 for a salary benchmark. |

**Always fetch the live schema first** — the section selector's exact name/values
change between versions:

```bash
apify actors info "memo23/glassdoor-scraper-ppr" --input --json \
  --user-agent apify-awesome-skills/apify-jobs-data 2>/dev/null
```

If Glassdoor has no data for a company, report "no Glassdoor data found" rather than
substituting another source silently.

---

## Picking the route

1. Anchor #3 names a board → that board's primary Actor (fallback per the SKILL.md Step 2 rule).
2. Anchor #3 is `auto` (default) → `agentx/all-jobs-scraper`.
3. User names two+ boards → run their primaries in parallel, tag `source`, dedupe.

Never run more than the user asked for. The aggregator already covers most boards in
one run — split into per-board Actors only when the user wants one board's deeper
fields or its cheaper rate.
