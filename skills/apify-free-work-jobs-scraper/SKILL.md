---
name: apify-free-work-jobs-scraper
description: "Free-Work jobs scraper for French IT recruiters: freelance informatique missions with TJM day rates, annual pay, skills and remote mode. Monitor mode reports new, changed and removed missions since the last run. Uses the Apify Actor redomic/free-work-jobs-scraper. Use when the user asks to 'free-work scraper', 'free-work jobs', 'freelance informatique scraper', or wants Free-Work Jobs Scraper results as structured JSON or CSV."
metadata:
  category: data-extraction
  keywords: "free-work scraper, free-work jobs, freelance informatique scraper, free work jobs scraper"
author: Redomic
author_url: https://apify.com/redomic
---

# Free-Work Jobs Scraper

Free-Work jobs scraper for French IT recruiters: freelance informatique missions with TJM day rates, annual pay, skills and remote mode. Monitor mode reports new, changed and removed missions since the last run.

Disclosure: the routed Actor, `redomic/free-work-jobs-scraper`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get Free-Work Jobs Scraper results for mode search; query developpeur; maxItems 10; maxPages 1"
- "Get Free-Work Jobs Scraper results for mode search; query python; maxItems 10; maxPages 1"
- "Get Free-Work Jobs Scraper results for mode search; query chef de projet; maxItems 8; maxPages 1"

Out of scope (the boundary):

- Personal contact data or logged-in content: this Actor reads public pages only.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via `apify login`, the `APIFY_TOKEN` environment variable, or a token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. Map the request onto the input fields below; fetch the live schema for anything unusual.
2. Run the Actor and read its dataset. Rows with a `_status` field are per-input status rows, not data.
3. Deliver a count, a short table of the key fields, and the dataset link or an export.

## Input

- `mode` (string): search lists missions for a keyword; detail reads full mission pages; monitor reports only new, changed and removed missions since the last run of the same input.
- `query` (string): Keyword to search on Free-Work, for example developpeur, python or chef de projet. Used by search and monitor. Leave empty for every IT mission.
- `urls` (array): Mission pages to read in detail mode. Full https://www.free-work.com/... URLs or paths starting with / both work. Up to 100 URLs per run.
- `maxItems` (integer): Upper limit on rows returned in one run. Applies after filters and before charging. Maximum 1000.
- `maxPages` (integer): How many listing pages (16 missions each) to read per keyword in search and monitor mode. Maximum 40.
- `remoteMode` (string): Keep only missions with this remote mode. Empty keeps all. Values on the site are none, partial and full.
- `contractType` (string): Keep only missions of this contract type: contractor, worker, permanent or fixed-term. Empty keeps all.
- `minDailyRate` (integer): Keep only missions whose TJM is at least this amount in EUR per day. 0 keeps all.
- `includeDescription` (boolean): Add the mission description as plain text to every row. On by default; turn off for smaller rows.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Free-Work Jobs Scraper | `redomic/free-work-jobs-scraper` | community | free-work scraper |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/free-work-jobs-scraper" \
      -i '{"mode": "search", "query": "developpeur", "maxItems": 100, "maxPages": 5, "minDailyRate": 0, "includeDescription": true}' \
      --json \
      --user-agent apify-awesome-skills/apify-free-work-jobs-scraper \
      2>/dev/null

    apify actors info "redomic/free-work-jobs-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-free-work-jobs-scraper 2>/dev/null

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-free-work-jobs-scraper 2>/dev/null
