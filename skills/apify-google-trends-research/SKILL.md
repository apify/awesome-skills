---
name: apify-google-trends-research
description: Research search demand with Google Trends data. Compare any number of keywords on one shared 0-100 scale (the Trends website stops at 8), see which topics are rising or falling and by how much, find the peak season (busiest month), the regions where a term is most searched, and the fastest rising related searches. Use when the user asks "is X growing or declining", "compare search interest for A, B and C", "which of these 20 keywords is searched most", "when is the peak season for Y", "where is Z most popular", "what is rising around X", wants a pytrends alternative, or needs Google Trends data as CSV or JSON for content, SEO or product research.
author: Ralf IJsbrandij — routes to an Actor built by the author; no affiliate or referral parameters
author_url: https://github.com/RalfIJ
metadata:
  category: data-extraction
  keywords: "google-trends, search-trends, keyword-research, trend-analysis, seasonality, rising-searches, market-research, seo, content-research, pytrends-alternative, apify"
---

# Google Trends Research

Answer "is this growing, how does it compare, and when does it peak?" with Google Trends data for many keywords in one run, including keyword sets larger than the Trends website can compare.

**Disclosure:** `ralfij/google-trends-scraper` is built and published by the author of this skill. No affiliate or referral parameters are used on any link.

**Never invent a trend, a percentage or a peak.** Every number comes from the Actor's dataset, and it is always relative search interest, never a search volume.

## Example prompts

Prompts this skill handles:

- "Compare search interest for these 15 project management tools over the past 5 years, worldwide, and rank them."
- "Is 'matcha' still growing in the US? When is its peak month, and which states search for it most?"
- "What are the rising searches around 'solar panels' in Germany over the past 12 months?"

Out of scope (the boundary):

- "How many people search for 'running shoes' per month?" Google Trends gives relative interest (0-100), not search volumes. Send exact volumes to a keyword-volume or SEO tool instead, and say why.

## Prerequisites

- An Apify account ([sign up](https://apify.com)).
- **MCP path:** with the Apify MCP server connected, use the `call-actor` and `get-dataset-items` tools. No extra setup.
- **CLI path:** the [Apify CLI](https://docs.apify.com/cli), authenticated with `apify login` or an `APIFY_TOKEN` environment variable ([get a token](https://console.apify.com/settings/integrations)). Every call below carries `--json`, `--user-agent apify-awesome-skills/apify-google-trends-research` and `2>/dev/null`.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Trend, seasonality, regions and rising searches for many keywords, on their own scale or one shared scale | `ralfij/google-trends-scraper` | community | Keyword sets of any size, ready-made trend metrics, share of search |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Workflow

```
Task Progress:
- [ ] Step 1: Collect the anchors (one block)
- [ ] Step 2: Pick own scale or shared scale
- [ ] Step 3: Fetch the input schema, build the input, estimate the cost
- [ ] Step 4: Run and pull the dataset
- [ ] Step 5: Read the metrics and answer
```

### Step 1: Collect the anchors

Ask these as one block before any Actor call, with the defaults shown:

1. **Keywords**: any number, one per item. Required.
2. **Location** (`geo`): `""` for worldwide, a country (`US`, `DE`) or a region (`US-CA`). The default is worldwide.
3. **Period** (`timeRange`): `today 12-m` (default), `today 5-y`, `all` (2004 to now), `today 3-m`, `today 1-m`, `now 7-d`, `now 1-d`, `now 4-H` or `now 1-H`. For custom dates use `customTimeRange` (`2024-01-01 2024-12-31`).
4. **Category** (`category`): `0` for all. Set one for ambiguous words, for example `31` (Programming) so "go" and "swift" mean the languages.
5. **Search type** (`searchType`): `web` (default), `images`, `news`, `shopping` or `youtube`.

If the keywords are vague ("compare some AI tools"), ask one clarifying question.

### Step 2: Own scale or shared scale

| `comparison` | Use when | What you get |
|---|---|---|
| `separate` (default) | "Is each of these growing?" | Each keyword on its own 0-100 scale: trend direction, % change, peak, busiest month |
| `shared` | "Which is searched more?" | All keywords on one scale, plus `shareOfSearch` per keyword. Works for more than 8 keywords; groups are linked through their most searched keyword |

### Step 3: Fetch the schema, build the input, estimate the cost

```bash
apify actors info "ralfij/google-trends-scraper" --input \
  --user-agent apify-awesome-skills/apify-google-trends-research 2>/dev/null
```

Example input for a 5-year comparison in one category:

```json
{
  "keywords": ["python", "javascript", "java", "c++", "c#", "go", "rust", "kotlin", "swift", "typescript"],
  "comparison": "shared",
  "timeRange": "today 5-y",
  "geo": "",
  "category": 31
}
```

**Cost:** one result per keyword (about $0.002 per keyword on Apify's free plan, less on paid plans; check the Actor's Pricing tab before quoting it), plus a tiny start fee. A shared comparison makes a few extra Google requests for the linking, but you still pay per keyword. Confirm with the user before runs above about 1,000 keywords.

### Step 4: Run and pull the dataset

```bash
apify actors call "ralfij/google-trends-scraper" \
  -i '{"keywords": ["coffee", "tea", "matcha"], "geo": "US", "timeRange": "today 12-m"}' \
  --json --user-agent apify-awesome-skills/apify-google-trends-research 2>/dev/null

apify datasets get-items DATASET_ID --format json \
  --user-agent apify-awesome-skills/apify-google-trends-research 2>/dev/null
```

Take `DATASET_ID` from `storage.defaultDatasetId` in the JSON the call prints.

### Step 5: Read the metrics and answer

Fields per keyword: `keyword`, `location`, `timeRange`, `category`, `searchType`, `scale`, `averageInterest`, `latestInterest`, `latestDate`, `peakInterest`, `peakDate`, `trend` (`rising`, `falling` or `stable`), `trendChangePercent`, `busiestMonth`, `shareOfSearch` (shared scale only), `interestOverTime[]` (`date`, `value`, `partial`), `interestByRegion[]` (`code`, `name`, `value`), `relatedQueriesTop[]` (`query`, `value`), `relatedQueriesRising[]` (`query`, `change`, `increasePercent`, `breakout`), `googleTrendsUrl`.

- **Growth:** `trend` and `trendChangePercent` compare the last quarter of the period with the first quarter; within ±10% counts as `stable`.
- **Ranking:** use `shareOfSearch` from a shared run, never `averageInterest` from separate runs (each separate keyword has its own 100).
- **Seasonality:** `busiestMonth` needs a period of about a year or longer.
- Deliver a short table (keyword, trend, change %, peak, busiest month, top regions) and say what the numbers mean: relative interest, location, period and category.

## Gotchas and failure modes

- **Relative, not volume.** 100 is the busiest point of the chart. Never present the values as searches per month.
- **Small keywords next to big ones round to 0** on a shared scale. Compare keywords of a similar size, or run small ones separately.
- **The last point is usually incomplete** (`partial: true`) and looks like a drop. Leave it out of growth claims.
- **Rising related searches can include unrelated queries** (in October 2026, "sports scores today" for "coffee" in the US). Google Trends shows the same list, so it is Google's data, not an error. Filter before quoting.
- **A keyword came back with a note or empty series.** Read the `RUN_SUMMARY` record in the run's key-value store; Google has too little data for very rare terms, so widen the period or location.
- **Dates are in UTC.**
