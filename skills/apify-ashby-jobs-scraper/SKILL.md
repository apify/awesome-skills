---
name: apify-ashby-jobs-scraper
description: "Scrape Ashby jobs or discover companies using Ashby with the Apify Ashby Job Board API Actor (johnvc/ashby-job-board-scraper). Job mode returns live job rows with title, company, location, remote and employment fields, publish date, apply URL, employer-published salary columns, equity flag, and Markdown descriptions. Company mode finds Ashby boards from a bundled directory or checks a prospect list, returning company name, board slug and URL, live open-job count, and verification fields. Takes company names, board slugs, or board URLs; supports pre-billing job filters and publishedAfter feeds. Use for Ashby jobs data or API requests, salary and remote-role collection, job-board pipelines, companies using Ashby/Ashby customers, ATS market maps, prospect checks, and recruiting or sales target lists. Billed per delivered result with no start fee, and MCP-ready for Claude and other AI agents."
author: John Cole
author_url: https://github.com/johnisanerd
license: MIT
metadata:
  version: "1.0"
  keywords: "ashby, jobs, job-board, salary, remote-work, company-discovery, prospect-check"
---

# Ashby Companies and Jobs, as Structured Rows

Find companies using Ashby, check a prospect list, or retrieve their job postings with employer-published salary data. Choose the output mode for the requested result.

## When to use this skill

- Someone wants Ashby jobs and does not want to read jobs.ashbyhq.com boards by hand.
- You are filling a job board, a market-intel dashboard, or a sourcing tool with roles from Ashby-hosted careers pages.
- You need salary as numbers the employer actually published, not a string a human has to read or a model has to guess.
- You went looking for an Ashby jobs API and found only the employer-side APIs you cannot sign up for.
- Someone asks which companies use Ashby, wants an ATS market map, or needs to check a prospect list for Ashby boards.
- You need live open-role counts before choosing which boards to feed into a jobs pipeline.

Choose `outputMode` for the question: `jobs` for postings, `companiesOnly` for company discovery or verification, and `urlsOnly` for a cheap board index. See `references/actor-index.md`.

## What you get

In `jobs` mode, one dataset row per job. `resultType` separates `job` rows from `error` rows.

Core fields:

- `id`, `url` (canonical, safe as a dedupe key), `applyUrl`, `title`
- `companyName`, `boardToken`, `boardUrl`
- `department`, `team`, `departments`, `employmentType`, `workplaceType`, `isRemote`
- `location`, `secondaryLocations`, `locationsDerived`, `countriesDerived`, `address`
- `datePublished`, `isListed`
- `compensationSummary` (the employer's own pay line), `salaryRaw` (structured, verbatim), `salaryDerived`, and flat `salaryMin`, `salaryMax`, `salaryCurrency`, `salaryPeriod`, `salaryTiers`, `offersEquity`
- `descriptionMarkdown` (default add-on), `descriptionHtml`, `descriptionText` (opt-in add-ons)
- `source` (always `ashby`), `sourceType`, `scrapedAt`

With `includeCompanyData` on, each row also carries `companyWebsite`, `companyLogo`, `remoteEligibility` (the countries remote applicants may live in, as the employer declared them), `applicationDeadline`, and `directApply`.

The Actor ships dataset views for the console: `overview`, `salaries` (sortable pay columns), `companies`, and `newPostings`.

### Company rows

With `outputMode: "companiesOnly"`, the dataset has one row per company. `resultType` separates `company` rows from `error` rows.

- `companyName`, `boardToken`, `boardUrl`
- `jobCount`: live open roles at verification time
- `live`: whether the board answered the probe (`null` when verification is off)
- `verifiedAt`, `scrapedAt`

A failed prospect check returns an error row with `errorCode: board_not_found`, `errorMessage`, and optional `didYouMean` suggestions. The `companies` dataset view presents company name, slug, open jobs, live flag, and board link.

## Prerequisites

- Apify account (sign up at https://apify.com?fpr=9n7kx3&fp_sid=awesomeskills).
- Authentication via `apify login`, or an `APIFY_TOKEN` environment variable (Apify Console, Settings, Integrations).

## The Actor

- Store page: https://apify.com/johnvc/ashby-job-board-scraper?fpr=9n7kx3&fp_sid=awesomeskills
- Actor ID: `johnvc/ashby-job-board-scraper`
- Pricing: pay per event, no start fee. See the cost section below and `references/gotchas.md` for the live-price command.

## Run it with the Apify CLI

Engineering roles from two boards, capped at 25:

```bash
apify actors call "johnvc/ashby-job-board-scraper" -i '{"companies":["cerebras","ramp"],"titleKeywords":["engineer"],"maxJobs":25}' \
  --json \
  --user-agent apify-awesome-skills/apify-ashby-jobs-scraper \
  2>/dev/null
```

Remote full-time roles with pay, descriptions off for cheaper metadata rows:

```bash
apify actors call "johnvc/ashby-job-board-scraper" -i '{"companies":["openai","ramp","deel"],"remoteOnly":true,"employmentTypes":["FullTime"],"includeDescriptionMarkdown":false,"maxJobs":100}' \
  --json \
  --user-agent apify-awesome-skills/apify-ashby-jobs-scraper \
  2>/dev/null
```

Only postings added in the last day, the shape to put on a daily schedule:

```bash
apify actors call "johnvc/ashby-job-board-scraper" -i '{"companies":["openai","notion","linear"],"publishedAfter":"25h","maxJobs":200}' \
  --json \
  --user-agent apify-awesome-skills/apify-ashby-jobs-scraper \
  2>/dev/null
```

Confirm the live schema and prices before a large batch:

```bash
apify actors info "johnvc/ashby-job-board-scraper" --json \
  --user-agent apify-awesome-skills/apify-ashby-jobs-scraper \
  2>/dev/null
```

Read the rows back from a finished run:

```bash
apify datasets get-items <DATASET_ID> --format json \
  --user-agent apify-awesome-skills/apify-ashby-jobs-scraper \
  2>/dev/null
```

Discover up to 100 Ashby boards from the directory and verify them live:

```bash
apify actors call "johnvc/ashby-job-board-scraper" -i '{"outputMode":"companiesOnly","maxCompanies":100}' \
  --json \
  --user-agent apify-awesome-skills/apify-ashby-jobs-scraper \
  2>/dev/null
```

Check a prospect list, including explicit misses:

```bash
apify actors call "johnvc/ashby-job-board-scraper" -i '{"companies":["Black Semiconductor","Morse Micro","Ramp","Notarealcompany Xyz"],"outputMode":"companiesOnly"}' \
  --json \
  --user-agent apify-awesome-skills/apify-ashby-jobs-scraper \
  2>/dev/null
```

Every call carries the three flags this repo expects: `--json` (or `--format json`), `--user-agent apify-awesome-skills/apify-ashby-jobs-scraper`, and `2>/dev/null`.

## Run it from Claude or another AI agent (MCP)

The Actor is MCP-ready. Add the hosted server URL:

`https://mcp.apify.com/?tools=actors,docs,johnvc/ashby-job-board-scraper`

Then ask, for example: "Pull the remote engineering jobs from OpenAI and Ramp with published salary ranges, and rank them by salaryMax." MCP setup docs: https://docs.apify.com/platform/integrations/mcp

## Workflow: job postings

1. Start with one or two boards and `maxJobs` around 25. Look at the row shape before you pay for a wide crawl.
2. Company names work as input. "Black Semiconductor" finds the blacksemiconductor board; the Actor tries slug spellings automatically and returns a `board_not_found` error row on a miss, optionally with `didYouMean` suggestions.
3. Filter at the source, not downstream. `titleKeywords`, `departments`, `locationKeywords`, `employmentTypes`, `remoteOnly`, and `publishedAfter` all drop jobs before they are billed. For fully remote requests, also check `workplaceType`: `remoteOnly` can return Hybrid jobs.
4. Keep `includeDescriptionMarkdown` on for LLM pipelines; turn it off for metadata-only rows at roughly half the per-row cost.
5. For salary work, read the flat columns and `salaryDerived.source`. Published ranges can come from native compensation data or description parsing, even when `shouldDisplayCompensation` is false. Do not infer missing pay.
6. Check `resultType` before treating a row as a job. An `error` row carries `errorCode` and a human-readable `errorMessage`.
7. Dedupe downstream on `url`. It is canonical and survives a company editing the title.

## Workflow: companies and prospect checks

1. For directory discovery, select `outputMode: "companiesOnly"`, optionally narrow names and slugs with `discoveryQuery`, and cap the sweep with `maxCompanies`. For prospect checks, supply the requested names, slugs, or board URLs in `companies`.
2. Keep `verifyCompanies` on for current counts; distinguish `company` rows from errors. Sort verified rows by `jobCount` within the returned sample, not as a claim about every Ashby customer. A name match is not an industry classification.
3. Deduplicate by `boardToken`, since one company can operate multiple boards. Re-run when current counts are needed rather than presenting a cached directory snapshot as live.

### Continue from companies to job postings

When the request includes retrieving their jobs, keep valid `company` rows and deduplicate their non-empty `boardToken` values. Pass those values as `companies` in a second call to the same Actor with explicit `outputMode: "jobs"`, the user's filters, and a separate job cap. Stop when no valid tokens remain: an empty `companies` array triggers a directory sweep and would broaden the request.

## Inputs

- `companies` (array): company names, board slugs, or jobs.ashbyhq.com URLs (board, embed, or single job), mixed freely. Empty sweeps the bundled directory.
- `startUrls` (array): the same values in URL-list form; merged with `companies`.
- `outputMode` (enum `jobs`, `urlsOnly`, `companiesOnly`, default `jobs`)
- `titleKeywords`, `departments`, `locationKeywords` (arrays): keep-only filters, run before billing.
- `employmentTypes` (array of `FullTime`, `PartTime`, `Intern`, `Contract`, `Temporary`)
- `remoteOnly` (boolean, default false)
- `publishedAfter` (string): `24h`, `7d`, `2w`, or an ISO date.
- `includeDescriptionMarkdown` (boolean, default true), `includeDescriptionHtml`, `includeDescriptionText` (default false)
- `includeCompanyData` (boolean, default false): job-page enrichment, one extra request per job.
- `report` (enum `none`, `markdown`, `html`): a whole-run digest in the key-value store.
- `maxJobs` (integer, default 100): the primary spend cap. `maxJobsPerCompany`, `maxCompanies`, `maxConcurrency` refine it.
- `proxyConfiguration` (object): off by default; direct connections work.

Company-mode inputs:

- `outputMode`: set `companiesOnly` for discovery or prospect verification.
- `companies` (array): prospect names, slugs, or board URLs; omit it for a directory sweep.
- `discoveryQuery` (string): case-insensitive text match over directory names and slugs.
- `verifyCompanies` (boolean, default true): live-probe candidates; dead boards are skipped and not billed as company rows.
- `maxCompanies` (integer, default 25): the primary cap for directory sweeps.
- `maxConcurrency` (integer, default 5): parallel probes.

## Cost

Billing is pay per event with no start fee, so a run that returns nothing costs almost nothing. Confirm live prices with the info command above rather than trusting a number copied here.

The base `job-result` event fires once per delivered job row, salary data included. Add-on events fire only on rows that carry the extra: `job-description-markdown` (on by default), `job-description-html`, `job-description-text`, `job-company-data`, and a flat `run-report`. Company discovery rows and URL index rows have their own cheaper events.

Jobs removed by your filters are never charged. As a shape, 100 jobs with Markdown descriptions is small change.

Suggested confirmation thresholds: mention the estimate under about $5, warn the user over about $5, get explicit confirmation over about $20. Present cost as "around $X", never as a guarantee.

## Honest limits

- **No update timestamps exist.** Ashby publishes only `publishedAt`, so `publishedAfter` gives you a new-postings feed; there is no changed-jobs feed and no field pretends otherwise.
- Salary appears only when the employer displays compensation on the posting. Nothing is inferred by a model; `salaryDerived.source` tells you whether a value came from the structured data or a deterministic text parse.
- Public board data only. No applicant data, no recruiter contacts, nothing behind a login.
- One board is one request, so very large boards return in a single response; a board too large to process returns a clear in-band error rather than a partial dataset.
- The bundled directory can omit newly launched boards. Try a direct company or board-URL check when a directory search misses a known prospect.
- Company names come from the directory; a board outside it may use its slug as the name. One company may operate multiple board slugs, each returned as its own row.
- Public board presence shows that a company hires through Ashby; it does not establish contract value, seats, or tenure.

## Troubleshooting

- `board_not_found`: the slug does not exist on the public API. Check `didYouMean` if present on the error row, or paste the board URL instead of a name.
- `job_not_found`: a single-job URL points at a posting that closed. Fetch the whole board instead.
- `http_error`: the source answered abnormally; the row says which HTTP status. Retry once before assuming anything.
- Zero rows and no error row: your filters removed everything. Relax `publishedAfter` or `titleKeywords` first.
- Duplicates across runs: dedupe on `url`, never on title.
- Empty company sweep: loosen or remove `discoveryQuery`.
- `jobCount` and `live` are null: `verifyCompanies` was off, so the row is a directory snapshot rather than a live read.

See `references/gotchas.md` for cost guardrails and error recovery, and `references/actor-index.md` for the Actor routing table.

## Related Actors

- Greenhouse Job Board API: https://apify.com/johnvc/greenhouse-job-board-api?fpr=9n7kx3&fp_sid=awesomeskills
- Workday Careers API: https://apify.com/johnvc/workday-careers-api?fpr=9n7kx3&fp_sid=awesomeskills
- Wellfound Jobs API: https://apify.com/johnvc/wellfound-jobs-api?fpr=9n7kx3&fp_sid=awesomeskills
- LinkedIn Jobs API: https://apify.com/johnvc/linkedin-jobs-api?fpr=9n7kx3&fp_sid=awesomeskills
- Crunchbase Company API: https://apify.com/johnvc/crunchbase-company-api?fpr=9n7kx3&fp_sid=awesomeskills
- LinkedIn Company API: https://apify.com/johnvc/linkedin-company-api?fpr=9n7kx3&fp_sid=awesomeskills
- PitchBook Company API: https://apify.com/johnvc/pitchbook-company-api?fpr=9n7kx3&fp_sid=awesomeskills
