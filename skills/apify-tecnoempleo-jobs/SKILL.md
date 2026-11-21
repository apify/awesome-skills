---
name: apify-tecnoempleo-jobs
description: "Scrape Tecnoempleo IT job offers in Spain by keyword, province or remote mode. Get title, company, city, contract, experience, skills, published salary and offer URL. Schedule monitor runs for only new, changed and removed jobs. Uses the Apify Actor redomic/tecnoempleo-jobs. Use when the user asks to 'tecnoempleo scraper', 'tecnoempleo jobs', 'tecnoempleo IT jobs', or wants Tecnoempleo Jobs Scraper results as structured JSON or CSV."
metadata:
  category: data-extraction
  keywords: "tecnoempleo scraper, tecnoempleo jobs, tecnoempleo IT jobs"
author: Redomic
author_url: https://apify.com/redomic
---

# Tecnoempleo Jobs Scraper

Scrape Tecnoempleo IT job offers in Spain by keyword, province or remote mode. Get title, company, city, contract, experience, skills, published salary and offer URL. Schedule monitor runs for only new, changed and removed jobs.

Disclosure: the routed Actor, `redomic/tecnoempleo-jobs`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get Tecnoempleo Jobs Scraper results for query java; province Madrid; maxItems 10"
- "Get Tecnoempleo Jobs Scraper results for query python; province Barcelona; maxItems 10; includeDescription True"
- "Get Tecnoempleo Jobs Scraper results for query "data engineer"; province Valencia; maxItems 10"

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

- `query` (string): What to search for on Tecnoempleo, for example java, SAP, remote python or "data engineer". Spanish operators AND, OR, AND NOT and quoted phrases work too. Used by search and monitor; ignored when you
- `province` (string): Spanish province or a big city, for example Madrid, Barcelona, Valencia or Bilbao. Leave empty for all of Spain. Tecnoempleo's own province code is looked up for you.
- `remoteOnly` (boolean): Keep only 100% remote offers. Uses the site's own remote filter and drops anything the site lets through.
- `mode` (string): search lists open offers; detail fetches full descriptions for offer URLs you paste; monitor returns only new, changed and removed offers since the last run.
- `startUrl` (string): Optional. Paste a search URL copied from tecnoempleo.com, including any filters you set in the browser. Pagination is added automatically. Leave empty to use the fields above.
- `jobUrls` (array): For mode 'detail': full tecnoempleo.com offer URLs. The short /ofertas-trabajo/rf-... link is a search page, so paste the full offer link.
- `includeDescription` (boolean): For search and monitor: open the first offers to add the full description, skills, contract, experience and any published salary. Bounded by maxDetailFetches, so long runs stay observable. Costs no ex
- `maxItems` (integer): Upper limit on delivered offer rows, and therefore on what you pay. Default 100, maximum 1000.
- `maxPages` (integer): How many search result pages to open at 30 offers per page. Default 10, maximum 50. Stops early at maxItems or the last page.
- `maxDetailFetches` (integer): When 'Include full descriptions' is on, how many offer pages may be opened in one run. Default 10, maximum 100. Each fetch has a 30 second timeout.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Tecnoempleo Jobs Scraper | `redomic/tecnoempleo-jobs` | community | tecnoempleo scraper |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/tecnoempleo-jobs" \
      -i '{"query": "java", "remoteOnly": false, "mode": "search", "includeDescription": false, "maxItems": 100, "maxPages": 10, "maxDetailFetches": 10}' \
      --json \
      --user-agent apify-awesome-skills/apify-tecnoempleo-jobs \
      2>/dev/null

    apify actors info "redomic/tecnoempleo-jobs" --input --json \
      --user-agent apify-awesome-skills/apify-tecnoempleo-jobs 2>/dev/null

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-tecnoempleo-jobs 2>/dev/null
