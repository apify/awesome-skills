---
name: apify-account-hiring-changes
description: Track what changed in hiring at a named list of target accounts since the last check — new roles opened, roles changed (title, location, team), and roles closed — read straight from each company's Greenhouse or Lever job board or LinkedIn company jobs page, then turn the diff into a per-account hiring report for sales, recruiting or investor research. Built for account-based work where the account list is already known, not for searching the whole job market. Use when the user says "what are my target accounts hiring for this week", "which of these companies opened new sales roles", "track job changes at these companies", "tell me when these companies close or add roles", "weekly hiring report for my account list", "monitor Greenhouse and Lever boards for changes", or "hiring signals for my named accounts".
author: Felucca (oshalaby)
author_url: https://apify.com/oshalaby
metadata:
  category: market-research
  keywords: "hiring-signals, account-based, target-accounts, job-changes, closed-jobs, greenhouse, lever, linkedin-company-jobs, sales-triggers, recruiting-intel, weekly-report, change-tracking"
---

# Account hiring changes

Disclosure: this skill's author built and earns from the Actor it routes to (`oshalaby/company-job-changes-monitor`, a pay-per-event Actor on the Apify Store). No referral or tracking parameters are used.

Turn a list of target accounts into a weekly report of **what changed** in their hiring: which roles each account opened, changed or closed since the last run, grouped by account, so the user can act on the accounts that moved.

## Example prompts

Prompts this skill handles:

- "Here are 30 target accounts with their Greenhouse or Lever boards. Every Monday, tell me which ones opened sales or data roles."
- "Which of these companies closed engineering roles in the last two weeks?"
- "Set up a weekly hiring-changes report for my account list and send it to a Google Sheet."

Out of scope (the boundary):

- "Find all data engineer jobs in Berlin across job boards." That is a market-wide job search, not a named-account watch: use `apify-job-boards` or `apify-jobs-data`.
- "Find companies showing buying intent from funding news and LinkedIn posts." Use `apify-buying-signal-detection`, which combines several signal types.
- Anything about candidates, recruiters or hiring managers as people. The Actor returns jobs, not people.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. **Collect the account list.** For each account, get its public job board as a Greenhouse or Lever board URL (e.g. `https://boards.greenhouse.io/<company>`, `https://jobs.lever.co/<company>`), a shorthand (`greenhouse:<company>`, `lever:<company>`), or a LinkedIn company page. Ask the user for the persona or departments they care about (e.g. "Sales", "Data"); these filter the report, not the run.
2. **Fetch the input schema** and build the input. Give the watch list a stable name (`stateKey`) per campaign so later runs compare against the right baseline. Keep `trackChanges: true` and `output: "changes"`. Set `includeDescription: false` unless the user needs job text: it is smaller and faster.
3. **State the cost before the first run.** The first run counts every open job as `new`, so it is the most expensive one. Read the current prices from the Actor's Store page or the schema fetch's pricing block. Later runs charge only for new, changed or closed jobs plus a small per-board fee. Unchanged jobs are free. If the account list has more than about 50 companies, confirm with the user first.
4. **Run, then build the report.** Group rows by `company`. For each account list counts of `new`, `changed` and `closed`, then the matching roles (title, location, team, link), filtered to the user's personas. Show accounts with no change in one line at the end. Rows with `changedFields` say what changed (for example `["location"]`).
5. **Schedule it.** Save the input as an Apify Task with the same `stateKey` and add a weekly Schedule, or re-run on the user's cadence. A board that fails to load is reported in the run and never marks its jobs as closed.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| New, changed and closed jobs at named accounts (Greenhouse, Lever, LinkedIn company pages) | `oshalaby/company-job-changes-monitor` | community | Weekly per-account change reports; only changes are charged after the first run |
| Market-wide job search across boards | see `apify-job-boards` / `apify-jobs-data` | community | Not this skill |

## Calling Actors

### Apify CLI

    # Fetch the input schema
    apify actors info "oshalaby/company-job-changes-monitor" --input --json \
      --user-agent apify-awesome-skills/apify-account-hiring-changes 2>/dev/null

    # Run for a watch list
    apify actors call "oshalaby/company-job-changes-monitor" \
      -i '{"boards": ["greenhouse:examplecompany", "lever:anothercompany"], "trackChanges": true, "stateKey": "q1-target-accounts", "output": "changes", "includeDescription": false}' \
      --json \
      --user-agent apify-awesome-skills/apify-account-hiring-changes \
      2>/dev/null

    # Fetch results
    apify datasets get-items DATASET_ID --format json \
      --user-agent apify-awesome-skills/apify-account-hiring-changes 2>/dev/null

### Apify MCP connector

Hosted MCP server at <https://mcp.apify.com> (docs: <https://docs.apify.com/platform/integrations/mcp>). Call `oshalaby/company-job-changes-monitor` with the same input.

## Troubleshooting

- **A company returned an error.** The board name may be wrong, or the company moved to another job system. The run summary shows the HTTP status. Ask the user for the current careers page and switch the board URL.
- **Everything came back as `new` again.** The `stateKey` changed or was left empty on one run. Use the same watch-list name every time.
- **First run too expensive.** Start with fewer accounts, or set a run spending limit. The Actor stops cleanly and reports what it couldn't deliver on the next run.
- **The user wants people (recruiters, hiring managers).** Out of scope: the Actor returns no personal contact details.
