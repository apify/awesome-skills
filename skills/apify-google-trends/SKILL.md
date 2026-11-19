---
name: apify-google-trends
description: Get Google Trends data through Apify - interest over time for any number of keywords on one comparable 0-100 scale, related and rising queries, interest by country, region, city or US metro, and today's trending searches per country. Use when the user asks to "compare these keywords on Google Trends", "rank keywords by search interest", "which of these brands is searched more", "compare more than 5 keywords", "Google Trends for 50 keywords", "pytrends alternative", "pytrends 429 / TooManyRequestsError", "rising queries for X", "where is X searched most", "what is trending in Germany today", or pastes a trends.google.com link and wants the data. Not for absolute search volumes or CPC. The routed Actor granola2/google-trends-scraper is built by this skill's author (see Disclosure).
author: granola2
author_url: https://github.com/sassrami
metadata:
  category: data-extraction
  keywords: "google-trends, trends, search-interest, keyword-research, keyword-comparison, seo, pytrends, pytrends-alternative, related-queries, rising-queries, interest-by-region, trending-searches, trending-now, brand-comparison, market-research, google-topics"
---

# Google Trends (compare any number of keywords on one scale)

Disclosure: the routed Actor `granola2/google-trends-scraper` is built by this skill's author and is paid per result. The other row in the routing table is unaffiliated.

The main way this task goes wrong is **scale**. Google Trends compares at most 5 terms per request and rescales every request so its own peak is 100. A "50" from one batch of 5 and a "50" from another batch are not the same thing. If the user wants more than 5 keywords compared or ranked, the numbers must come from one shared scale, or the answer is wrong. The routed Actor stitches batches together through overlapping anchor keywords, so every keyword in a run is on one 0-100 scale, and each row carries `rank` and `shareOfTotalPct`.

The second trap is reading the numbers as volumes. Values are relative: the biggest keyword in the run peaks at 100. Say so when presenting results.

## Example prompts

Prompts this skill handles:

- "Rank these 30 SEO keywords by Google search interest in the US over the last 12 months."
- "Compare ChatGPT, Gemini, Claude, Perplexity, Copilot and DeepSeek on Google Trends worldwide."
- "What are the rising related queries for 'pickleball' in the UK?"
- "Which US states search for 'padel' the most?"
- "What's trending on Google in Germany and France today?"
- "Get me the data behind this chart: https://trends.google.com/trends/explore?q=padel,pickleball&geo=GB"

Out of scope (the boundary):

- "How many searches per month does 'running shoes' get?" Google Trends has no absolute volumes; use a keyword-volume tool (Google Ads Keyword Planner data) instead.
- Related *topics*: Google returns them empty to automated tools. Use related queries, or `resolveTopics` to query keywords as topics.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. **Pick the report(s).** `interestOverTime` for comparing or ranking keywords, `relatedQueries` for keyword ideas and rising terms, `interestByRegion` for where a term is searched, `trendingNow` (country codes) for today's trending searches. Ask only if the request is ambiguous; default to `interestOverTime`.
2. **Build the input.** Keywords as given (any number; more than 5 are stitched automatically). `geo` is a country or sub-region code (`US`, `US-NY`), empty for worldwide. `timeRange` is a preset (`now 7-d`, `today 3-m`, `today 12-m`, `today 5-y`, `all`) or `YYYY-MM-DD YYYY-MM-DD`. If the user pasted a trends.google.com link, pass it as `trendsUrl` instead; it sets keywords, geo, time range, category and search type. For ambiguous short terms ("apple", "sca"), set `resolveTopics: true`.
3. **Estimate cost and run.** One result is one keyword's time series, one keyword's related queries, one keyword's region list, or one trending search. About $0.005 per result on the free plan, less on paid plans; keywords with no data are never charged. Set `maxResults` to cap spend on large lists. The run always stops inside `maxRunSeconds` (default 300) and keeps what it got.
4. **Deliver.** For comparisons, lead with the ranking (`rank`, `keyword`, `averageValue`, `shareOfTotalPct`), then say that values are relative to the biggest keyword. Report keywords listed under `noData` in the run's `SUMMARY` record instead of showing them as zeros.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Compare or rank any number of keywords; related queries; regions; trending now; pasted Trends links | `granola2/google-trends-scraper` | community | One shared 0-100 scale across all keywords, `rank` and `shareOfTotalPct` per keyword, hard time limit, no charge for empty keywords |
| Search terms loaded from a Google Sheet | `apify/google-trends-scraper` | apify | Reading keywords from a public spreadsheet (`spreadsheetId`) |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling Actors - choose your interface

### Option A: Apify CLI (recommended for portability)

Compare keywords on one scale:

    apify actors call "granola2/google-trends-scraper" \
      -i '{"keywords": ["chatgpt", "gemini", "claude", "perplexity", "copilot", "deepseek"], "geo": "US", "timeRange": "today 12-m"}' \
      --json \
      --user-agent apify-awesome-skills/apify-google-trends \
      2>/dev/null

Related queries and regions for a few keywords:

    apify actors call "granola2/google-trends-scraper" \
      -i '{"keywords": ["pickleball", "padel"], "geo": "GB", "reports": ["relatedQueries", "interestByRegion"]}' \
      --json \
      --user-agent apify-awesome-skills/apify-google-trends \
      2>/dev/null

Today's trending searches (no keywords needed):

    apify actors call "granola2/google-trends-scraper" \
      -i '{"trendingNow": ["DE", "FR"]}' \
      --json \
      --user-agent apify-awesome-skills/apify-google-trends \
      2>/dev/null

Fetch the input schema or the results:

    apify actors info "granola2/google-trends-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-google-trends 2>/dev/null

    apify datasets get-items DATASET_ID --format json \
      --user-agent apify-awesome-skills/apify-google-trends 2>/dev/null

Every dataset row has a `report` field (`interestOverTime`, `relatedQueries`, `interestByRegion`, `trendingNow`); filter on it when a run mixes reports.

### Option B: Apify MCP connector

Hosted MCP server at <https://mcp.apify.com>. Documented at
<https://docs.apify.com/platform/integrations/mcp>.

### Option C: MCP client of your choice (e.g. `mcpc`)

Standalone CLI client. See <https://github.com/apify/mcpc>.

## Troubleshooting

- A small keyword is missing next to a big one: it is too small relative to the set and is listed in `SUMMARY.noData` as `too_low_relative_to_set`. Run it with similar-sized keywords, or set `sameScale: false` for per-keyword scales (then no `rank` is given).
- Results mix several meanings of a short word: rerun with `resolveTopics: true`.
- For cost guardrails and other errors, see [references/gotchas.md](references/gotchas.md).
