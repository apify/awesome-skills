---
name: apify-linkedin-company-employees
description: "Find the people behind a company on LinkedIn with no LinkedIn login, using three Apify Actors by the same author. Resolve website domains to verified LinkedIn company pages (george.the.developer/linkedin-company-by-domain), list a company's employees searched by title, seniority and location (george.the.developer/linkedin-company-employees-scraper), or deliver only owners, founders, C-level, VPs and directors with seniority band and department (george.the.developer/linkedin-decision-makers-finder). The domain resolver can also diff headcount and names between scheduled runs. Use when the user says find decision makers at a company, who works at a company in sales, list employees of a company on LinkedIn, get the LinkedIn page for these domains, build an ABM or outbound list from a domain list, watch headcount changes across a domain list, or asks for a LinkedIn company employees scraper. No emails or phone numbers. All three routed Actors are built by this skill's author (see Disclosure)."
author: George Kioko
author_url: https://github.com/the-ai-entrepreneur-ai-hub
license: Apache-2.0
metadata:
  category: data-extraction
  keywords: "linkedin, company-employees, decision-makers, c-level, founders, vp, director, domain-to-linkedin, company-url, abm, outbound, lead-list, sales-intelligence, recruiting, headcount-monitoring, b2b"
---

# LinkedIn Company Employees and Decision Makers

Turn a company name, a LinkedIn company URL or a plain website domain into rows of real people found in Google's index of public LinkedIn profiles, classified by seniority and department, with no LinkedIn account, cookies or login. Three Actors cover the chain. Pick one, or run them back to back.

**Disclosure:** all three routed Actors (`george.the.developer/linkedin-company-by-domain`, `george.the.developer/linkedin-company-employees-scraper`, `george.the.developer/linkedin-decision-makers-finder`) are built and published by the author of this skill. No affiliate or referral parameters are used on any link in this skill. Carry this disclosure into anything the skill generates, for example a report or a scheduled task that runs these Actors.

## Example prompts

Prompts this skill handles:

- "Find the decision makers at Stripe and Shopify, sales and marketing only."
- "List the engineering managers at Microsoft in Seattle on LinkedIn."
- "Here are 300 customer domains. Give me their LinkedIn company pages, then the VPs at each."

Out of scope (the boundary):

- Emails or phone numbers. The rows carry name, headline, title match, location and profile URL. Feed the `profileUrl` values to the email finder the user already uses.
- Full work history, education or private profile data. These Actors return short public profiles only.
- Tracking who joined or left a company between runs. The people Actors expose `compareWithPreviousRun`, but its diff needs a complete scan with live profile verification, and verification did not run at the list prices in this skill, so the diff row comes back with `diffUnavailable` and empty arrays. Do not promise hires and departures tracking.
- A raw bulk employee dump at the lowest possible price per row with no company evidence or classification. `harvestapi/linkedin-company-employees` is cheaper per row for that job; this skill does not route there.

## Prerequisites

- Apify account ([sign up](https://apify.com)). The free plan includes $5 of monthly platform usage, enough to try every workflow below.
- Authentication via `apify login`, or an `APIFY_TOKEN` environment variable (Apify Console, Settings, Integrations). Pass the token as a header or environment variable, never inside a URL.

## Actor routing

| User need | Actor ID | Tier | Billed event |
|-----------|----------|------|--------------|
| Only the buying committee at named companies: owners, founders, C-level, VPs, directors | `george.the.developer/linkedin-decision-makers-finder` | community | $0.022 per company-matched decision maker, $0.00005 per run |
| Employees at named companies, any seniority, searched by title, seniority, location or industry | `george.the.developer/linkedin-company-employees-scraper` | community | $0.01 per company-matched short profile, $0.05 per run |
| Website domains to verified LinkedIn company pages, with headcount and follower counts | `george.the.developer/linkedin-company-by-domain` | community | $0.0075 per resolved domain, $0.002 per run |

How to choose:

1. The user has domains, not company names. Start with the domain resolver. Its `linkedinUrl` output is the exact `companies` input the other two Actors want.
2. The user wants leaders only. Use the decision makers finder. Everyone below director is skipped before any charge, so a run never pays for individual contributors.
3. The user wants a wider list, a specific title set, managers, or a seniority or industry filter. Use the employees scraper. `decisionMakersOnly: true` on it keeps leaders only.
4. The user wants change tracking. Only the domain resolver supports it today. `mode: "monitor"` adds one free `diff-summary` row per run with new and removed companies, headcount changes and name changes. Tracking people (who joined, who left) is out of scope, see Honest limits.

Prices are the Store list prices at the time of writing, which are the Free and Bronze plan prices. Silver pays 10% less, Gold and above 20% less. Confirm live prices before a large batch with the info command below. Rows without company evidence are delivered with `charged: false` and cost nothing.

## Run it with the Apify CLI

Decision makers in sales and marketing at two companies, 10 per company:

```bash
apify actors call "george.the.developer/linkedin-decision-makers-finder" -i '{"companies":["https://www.linkedin.com/company/stripe/","Shopify"],"departments":["sales","marketing"],"maxDecisionMakersPerCompany":10}' \
  --json \
  --user-agent apify-awesome-skills/apify-linkedin-company-employees \
  2>/dev/null
```

Engineering managers at one company, searched with a city, capped at 25 rows:

```bash
apify actors call "george.the.developer/linkedin-company-employees-scraper" -i '{"companies":["https://www.linkedin.com/company/microsoft/"],"targetTitles":["Engineering Manager","Director of Engineering"],"location":"Seattle","maxEmployees":25}' \
  --json \
  --user-agent apify-awesome-skills/apify-linkedin-company-employees \
  2>/dev/null
```

Domains to LinkedIn company pages, unresolved rows included so coverage is visible:

```bash
apify actors call "george.the.developer/linkedin-company-by-domain" -i '{"domains":["stripe.com","vercel.com","gitlab.com"],"includeUnresolved":true}' \
  --json \
  --user-agent apify-awesome-skills/apify-linkedin-company-employees \
  2>/dev/null
```

Headcount watch on a domain list, meant for a schedule. `forceRefresh` looks every company up again, so resolved rows are billed again:

```bash
apify actors call "george.the.developer/linkedin-company-by-domain" -i '{"domains":["stripe.com","vercel.com","gitlab.com"],"mode":"monitor","monitorBatchId":"customers","forceRefresh":true}' \
  --json \
  --user-agent apify-awesome-skills/apify-linkedin-company-employees \
  2>/dev/null
```

Fetch the live input schema of the Actor you picked before building an input that is not shown here, and check required fields, types and limits against it:

```bash
apify actors info "george.the.developer/linkedin-company-employees-scraper" --input --json \
  --user-agent apify-awesome-skills/apify-linkedin-company-employees \
  2>/dev/null
```

Confirm live prices before a large batch:

```bash
apify actors info "george.the.developer/linkedin-decision-makers-finder" --json \
  --user-agent apify-awesome-skills/apify-linkedin-company-employees \
  2>/dev/null
```

Read the rows back from a finished run:

```bash
apify datasets get-items <DATASET_ID> --format json \
  --user-agent apify-awesome-skills/apify-linkedin-company-employees \
  2>/dev/null
```

Every call carries the three flags this repo expects: `--json` (or `--format json`), `--user-agent apify-awesome-skills/apify-linkedin-company-employees`, and `2>/dev/null`.

## Run it from Claude or another AI agent (MCP)

All three Actors are MCP-ready. Add the hosted server URL with the tools preloaded:

`https://mcp.apify.com?tools=george.the.developer/linkedin-decision-makers-finder,george.the.developer/linkedin-company-employees-scraper,george.the.developer/linkedin-company-by-domain`

Then ask, for example: "Resolve these 50 domains to LinkedIn pages, then list the VPs and C-level at each, grouped by department." MCP setup docs: https://docs.apify.com/platform/integrations/mcp

## Workflow: domains to decision makers (the outbound list)

1. Run the domain resolver with the user's domains. Up to 50,000 per run, duplicates collapse automatically, `maxDomains` defaults to 1000.
2. Keep rows where `confidence` is `high` or `medium` and `linkedinUrl` is not null. Rows with `confidence: "low"` are free and mean no verified match. Report the unresolved count to the user instead of guessing.
3. Pass the kept `linkedinUrl` values as `companies` to the decision makers finder, with the user's `departments` and `seniorityBands`. Up to 200 companies per run; split larger lists.
4. Dedupe on `profileUrl` when it is not empty. Group by `company`, then `department`, then `seniorityBand`.
5. Report counts: domains in, resolved, decision makers delivered, rows delivered free (`charged: false`). Link the dataset.

## Workflow: employees by title and location

1. Prefer a LinkedIn company URL over a plain name. A name can match the wrong page or none; the URL is exact.
2. Put the titles the user cares about in `targetTitles` (up to 30). Without it, runs of 50 companies or fewer use a built in decision maker title set in English and Spanish, and larger runs use no title expansion.
3. `location`, `seniorityFilter` and `industryFilter` narrow the Google search. They are search hints, not hard filters, so a billed row can still sit in another city or seniority band. Check `location` and `seniorityBand` on each row before presenting it as a match. `maxEmployees` is per company, 1 to 100.
4. Check `titleMatchType` (`exact`, `partial`, `none`) and `matchedTitles` on each row before presenting a person as holding a title.
5. Rows with `source: "google-serp-no-profile-link"` are free and carry a name and headline but an empty `profileUrl`. Keep them apart from the deduped list, or drop them and report the count.

## Workflow: watch a domain list for changes

1. Save the domain resolver call as a task with `mode: "monitor"` and a stable `monitorBatchId`, and put it on a schedule. Snapshots live in a named key-value store in the user's own account (`company-by-domain-snapshots`) and are never charged.
2. Add `forceRefresh: true`, or set `cacheTtlDays` below the schedule interval. Without that, a domain resolved in the last 30 days comes back from the cache with its old name and headcount, so no change can show. Refreshed rows are billed again.
3. Each run adds one free row with `recordType: "diff-summary"`, `isFirstRun`, `previousRunAt`, `newCompanies[]`, `removedCompanies[]`, `headcountChanges[]` and `nameChanges[]`. The first run only saves the baseline. Filter on `recordType` before mixing it with the company rows (`recordType: "company"`).
4. `removedCompanies` stays empty when the run was cut short by the charge limit, the time budget or `maxDomains`. The row then carries `removalsUnavailable`.

## What you get

Employees scraper, one row per company-matched person:

- `publicIdentifier`, `profileUrl`, `fullName`, `headline`, `location`, `company`
- `matchedTitles[]`, `titleMatchType` (`exact`, `partial`, `none`)
- `isDecisionMaker`, `seniorityBand` (`owner`, `partner`, `cxo`, `vp`, `director`, `manager`, `senior`, `entry`, `training`, `unpaid`, `unknown`), `department` (`executive`, `engineering`, `data`, `product`, `design`, `sales`, `marketing`, `finance`, `hr`, `legal`, `support`, `operations`, `other`)
- `confidence` (`high` live profile verified, `medium` Google index matched, `low` unmatched and free), `source`, `charged`, `scrapedAt`. Live verification did not run at the list prices in this skill, so expect `medium` and `low`.
- Rows with `source: "google-serp-no-profile-link"` have an empty `profileUrl` and `publicIdentifier`. They are free and carry a name and headline only.

Decision makers finder, one row per charged or free decision maker: the fields above plus `firstName` and `lastName`. `isDecisionMaker` is always true on these rows.

Domain resolver, one row per domain:

- `domain`, `linkedinUrl`, `companyName`, `confidence` (`high`, `medium`, `low`), `method` (for example `homepage-sameas`)
- `employeeCount`, `followers`, `websiteStatus`, `cached`, `charged`, `recordType` (`company`)
- In `mode: "monitor"`, one extra free row with `recordType: "diff-summary"` (see the workflow above)

## Inputs

Decision makers finder:

- `companies` (array, required): LinkedIn company URLs or plain names, up to 200 per run.
- `seniorityBands` (array, default all five of `owner`, `partner`, `cxo`, `vp`, `director`)
- `departments` (array, default any): `executive`, `sales`, `marketing`, `engineering`, `data`, `product`, `design`, `finance`, `hr`, `legal`, `support`, `operations`, `other`. With departments set, the search asks for the leaders of those functions instead of the C-suite.
- `maxDecisionMakersPerCompany` (integer, default 10, 1 to 50): caps delivered rows per company, billed and free, so it is also the primary spend cap.
- `targetTitles`, `location`, `searchQuery`, `maxConcurrency` (1 to 10).

Employees scraper:

- `companies` (array, required), up to 200 per run.
- `targetTitles` (array, up to 30), `searchQuery`, `location` and `industryFilter` (both search hints)
- `seniorityFilter` (array): `owner`, `partner`, `cxo`, `vp`, `director`, `manager`, `senior`, `entry`, `training`, `unpaid`. A search hint as well.
- `maxEmployees` (integer, default 25, max 100) per company: the primary spend cap.
- `decisionMakersOnly` (boolean, default false), `maxConcurrency` (default 3).
- `profileDepth` is `short` only. Proxy fields are normalized by the Actor; leave them alone.

Domain resolver:

- `domains` (array, required), with or without protocol, up to 50,000 per run.
- `mode` (`resolve` or `monitor`), `monitorBatchId` (string, default `default`)
- `includeUnresolved` (boolean, default true), `forceRefresh` (boolean, default false), `cacheTtlDays` (default 30)
- `maxDomains` (integer, default 1000), `concurrency` (default 10, above 25 some sites rate limit), `useVpsRender` (default true)

## Cost

All three Actors are pay per event. A row is billed only when it carries evidence that the person or page belongs to the company asked for. Unmatched rows, cached domain lookups and the domain resolver's monitor row are free.

Worked shapes at list price:

- 10 companies, 10 decision makers each, 62 matched: 62 x $0.022 plus the start event, about $1.36.
- 1 company, 25 matched employees: $0.05 plus 25 x $0.01, $0.30.
- 1,000 domains, 850 resolved: $0.002 plus 850 x $0.0075, about $6.38.

Each Actor ships a default run charge limit that stops a run cleanly, status `SUCCEEDED`, when reached: $1 on the employees scraper, $5 on the decision makers finder, $25 on the domain resolver. The $1 default on the employees scraper covers about 95 billed rows. A run that returns fewer rows than expected with status `SUCCEEDED` hit that limit, the time budget, or the end of what Google has indexed. The last lines of the run log say which (`Charge limit reached`, `Soft deadline reached`). Raise `maxTotalChargeUsd` on the run or task only when the charge limit was the cause.

Suggested confirmation thresholds: mention the estimate under about $5, warn the user over about $5, get explicit confirmation over about $20. Present cost as "around $X", never as a guarantee. See `references/gotchas.md`.

## Honest limits

- No emails, phone numbers, full work history or education. Short public profiles only.
- Discovery runs on Google search through the Apify GOOGLE_SERP proxy group. Live profile verification on the employees scraper runs only when a margin check passes. At the list prices in this skill it did not pass in test runs, so rows are `confidence: "medium"` (billed, the person's own indexed headline names the company) or `"low"` (free). The decision makers finder never verifies. Nothing logs in to LinkedIn.
- A person Google placed near the company without their headline naming it is delivered free at `confidence: "low"`. On the decision makers finder the same holds when the headline names a longer company that starts with the same word (Notion Capital for Notion). The employees scraper does not make that second check, so read `headline` before trusting a `medium` row for a company with a common name.
- No people level change tracking today. `compareWithPreviousRun` adds a `company-diff-summary` row, but without live verification the row carries `diffUnavailable`, its arrays are empty and no baseline is saved. Empty arrays there do not mean nobody joined or left.
- The domain resolver's monitor mode compares cached values unless `forceRefresh` is on (30 day cache).
- The domain resolver returns the LinkedIn page, headcount and followers. It does not return employees; chain into the people Actors for that.
- Default timeouts: 20 minutes on both people Actors, 2 hours on the domain resolver. Large lists finish with partial coverage rather than failing; split them.

## Troubleshooting

- Zero rows for a company given by name: the name matched the wrong page or none. Pass the `https://www.linkedin.com/company/<slug>/` URL instead.
- Many rows with `charged: false` and `confidence: "low"`: the company match bar was not met. Free rows, not an error. Tighten `targetTitles` or `departments`, or accept them as leads to check by hand.
- Run ended with fewer rows than `maxEmployees` times companies and status `SUCCEEDED`: read the last lines of the run log. `Charge limit reached: yes` means raise `maxTotalChargeUsd` or split the company list. `Soft deadline reached: yes` means split the list. Neither means Google had no more indexed profiles for that company.
- `linkedinUrl` null with `confidence: "low"` on a domain: no verified match. Try `forceRefresh: true` if the site changed recently; keep `useVpsRender` on for JavaScript-only homepages.
- Diff row with empty arrays and `diffUnavailable`: the run had no live profile verification, the normal case at list prices. It does not mean nobody joined or left.
- Duplicates across runs: dedupe on `profileUrl` when it is not empty, never on `fullName` alone.

See `references/gotchas.md` for cost guardrails and error recovery, and `references/actor-index.md` for the routing table with prices and caps.
