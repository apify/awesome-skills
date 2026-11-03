---
name: apify-career-site-jobs-feed
description: Pull live job openings straight from named companies' career sites via the ATS's own public JSON (Greenhouse, Lever, Ashby, Workday, SmartRecruiters, Recruitee) with the cleanfeedsapi/ats-jobs-feed Actor, plus companion feeds for Hacker News "Who is hiring?" threads and remote boards (RemoteOK, Arbeitnow). Takes board slugs or pasted careers URLs, returns one row per job (title, location, department, apply URL, dates, stable id) at $2 per 1,000 rows with no proxies, no login and no HTML scraping. Use when the user asks to list open roles at specific companies, watch a company's careers page for new jobs, build a hiring-signal feed from a target-account list, pull Workday or SmartRecruiters postings, get structured jobs out of the monthly HN hiring thread, or diff today's openings against yesterday's. Triggers - "what jobs is X hiring for", "watch these careers pages", "new openings at my target accounts", "Workday jobs for company Y", "parse HN who is hiring", "cheap ATS jobs feed".
author: CleanFeeds
author_url: https://github.com/cleanfeedsapi/apify-actors
metadata:
  category: data-extraction
  keywords: "jobs, careers-page, ats, greenhouse, lever, ashby, workday, smartrecruiters, recruitee, hiring-signals, hn-who-is-hiring, remote-jobs, job-feed, official-api, apify"
---

# Career-site jobs feed (official ATS JSON)

Turn a list of companies into one table of their open roles, read from each ATS's public job-board JSON instead of scraping HTML. Disclosure: the routed Actors are built by the author (CleanFeeds); links carry no affiliate parameters.

## Example prompts

Prompts this skill handles:

- "List every open engineering role at Stripe, Ramp and Spotify right now."
- "Watch these 20 careers pages daily and tell me which companies posted new jobs."
- "Pull all Adobe Workday postings in EMEA into a sheet."
- "Give me the October HN Who is hiring thread as structured rows, remote only."

Out of scope (the boundary):

- "Search LinkedIn/Indeed/Glassdoor for data engineer jobs in Berlin" — that is keyword search across aggregators; use `apify-job-boards` or `apify-jobs-data` instead. This skill needs company boards you already know.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. Resolve the companies to board specs. Accept `source:slug` (`greenhouse:stripe`, `lever:spotify`, `ashby:ramp`, `workday:adobe.wd5/external_experienced`, `smartrecruiters:InPost`, `recruitee:prisma`) or just the careers URL; the Actor parses `boards.greenhouse.io/<slug>`, `jobs.lever.co/<slug>`, `jobs.ashbyhq.com/<slug>`, `<tenant>.<wdN>.myworkdayjobs.com/<site>`, `jobs.smartrecruiters.com/<Company>`, `<slug>.recruitee.com`. If the ATS is unknown, open the careers page once and read the host.
2. Estimate cost: rows × $0.002. A 20-company list is typically 500 to 5,000 rows, so under $10. Set `maxJobsPerBoard` to cap large Workday tenants.
3. Run the Actor (command below). A board that fails yields one row with an `error` field; the rest of the run continues, so check for those rows before reporting coverage.
4. Deliver: counts per company, the dataset link, and for monitoring store the `source:company:id` set and diff it on the next run. New ids are new openings, missing ids are closed roles.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Jobs from named companies' ATS boards (6 ATS) | `cleanfeedsapi/ats-jobs-feed` | community | Greenhouse, Lever, Ashby, Workday, SmartRecruiters, Recruitee; slugs or URLs; $2/1k rows |
| Structured rows from HN "Who is hiring?" | `cleanfeedsapi/hn-who-is-hiring` | community | Company, role, location, remote flag, links from the official HN API; latest or a given thread id |
| Remote-only openings | `cleanfeedsapi/remote-jobs-feed` | community | RemoteOK and Arbeitnow public APIs, with required source attribution |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling Actors — choose your interface

### Option A: Apify CLI (recommended for portability)

    apify actors call "cleanfeedsapi/ats-jobs-feed" \
      -i '{"boards":["greenhouse:stripe","https://jobs.lever.co/spotify","ashby:ramp"],"maxJobsPerBoard":0}' \
      --json \
      --user-agent apify-awesome-skills/apify-career-site-jobs-feed \
      2>/dev/null

| Flag | Why |
|------|-----|
| `--json` | Stable machine-readable output |
| `--user-agent` | Apify telemetry attribution |
| `2>/dev/null` | Suppress progress messages that break JSON |

Other useful commands:

    # Fetch Actor input schema
    apify actors info "cleanfeedsapi/ats-jobs-feed" --input --json \
      --user-agent apify-awesome-skills/apify-career-site-jobs-feed 2>/dev/null

    # HN Who is hiring, latest thread, remote mentions only
    apify actors call "cleanfeedsapi/hn-who-is-hiring" \
      -i '{"kind":"hiring","thread":"latest","query":"remote"}' \
      --json \
      --user-agent apify-awesome-skills/apify-career-site-jobs-feed \
      2>/dev/null

    # Fetch results
    apify datasets get-items DATASET_ID --format json \
      --user-agent apify-awesome-skills/apify-career-site-jobs-feed 2>/dev/null

### Option B: Apify MCP connector

Hosted MCP server at <https://mcp.apify.com>. Documented at
<https://docs.apify.com/platform/integrations/mcp>. Search for "ats jobs feed".

### Option C: MCP client of your choice (e.g. `mcpc`)

Standalone CLI client. See <https://github.com/apify/mcpc>.

## Troubleshooting

- Row with `error: "404 ..."` → wrong slug or the company moved ATS; open the careers page and re-read the host.
- `unrecognized careers URL` → the host is not one of the six ATS; pass `source:slug` manually or fall back to `apify-job-boards`.
- Workday rows have `posted_at: null` and `department: null` → the Workday list payload does not carry them; this is expected, not a failure.
- For detailed cost guardrails and recovery, see [references/gotchas.md](references/gotchas.md).
