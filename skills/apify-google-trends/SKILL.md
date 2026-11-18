---
name: apify-google-trends
description: >-
  Google Trends data with a pay-per-use Apify Actor: interest over time, interest by country, region or city, top and rising related queries and topics, for up to 5 compared keywords per lookup, across web, YouTube, News, Images or Shopping search. Use when the user says "google trends", "compare search interest", "is X trending", "seasonality of", "rising searches for", "trend by region", or "related queries".
author: Rowfeed
author_url: https://apify.com/rowfeed
metadata:
  category: market-research
  keywords: "google trends, search interest, trending, seasonality, related queries, rising queries, interest by region, keyword trends, market research"
---

# Google Trends data (interest over time, regions, related queries)

Google Trends data with a pay-per-use Apify Actor: interest over time, interest by country, region or city, top and rising related queries and topics, for up to 5 compared keywords per lookup, across web, YouTube, News, Images or Shopping search.

Disclosure: the routed Actors are built and sold by the skill author (Rowfeed); you pay per result on Apify, no subscription.

## Example prompts

Prompts this skill handles:

- "Compare Google search interest for "heat pump", "air conditioner" and "solar panels" over the past 5 years in the US"
- "Which US states search most for "heat pump" and which related queries are rising?"
- "Show YouTube search interest for "minecraft" vs "roblox" over the last 12 months"

Out of scope (the boundary):

- "Give me the exact number of monthly Google searches" — Trends is relative (0-100); use a keyword search volume tool instead.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. Pick the Actor from the routing table for the user's need.
2. Fetch its input schema (`apify actors info ACTOR_ID --input --json`) and build the input. Every Actor takes a list, so batch the user's items into one run.
3. Tell the user the estimated cost before large runs (the price per event is on the Actor's Store page) and cap spend with `maxTotalChargeUsd`.
4. Run, then summarise the rows returned and give the dataset link.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Interest over time, by region, related queries and topics | `rowfeed/google-trends-explorer` | community | Up to 5 keywords compared per lookup, any country, time range and search type |
| What is trending right now | `rowfeed/google-trends-trending-now` | community | Trending searches by country with traffic estimates |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling Actors — choose your interface

### Option A: Apify CLI (recommended for portability)

    apify actors call "rowfeed/google-trends-explorer" \
      -i '{"keywords":["web scraping","data extraction"],"timeRange":"past_12_months","location":"United States"}' \
      --json \
      --user-agent apify-awesome-skills/apify-google-trends \
      2>/dev/null

    # Fetch results
    apify datasets get-items DATASET_ID --format json \
      --user-agent apify-awesome-skills/apify-google-trends 2>/dev/null

### Option B: Apify MCP connector

Hosted MCP server at <https://mcp.apify.com>, for example `https://mcp.apify.com?tools=rowfeed/google-trends-explorer,rowfeed/google-trends-trending-now`.
Documented at <https://docs.apify.com/platform/integrations/mcp>.

### Option C: MCP client of your choice (e.g. `mcpc`)

Standalone CLI client. See <https://github.com/apify/mcpc>.

## Troubleshooting

- Values are relative interest (0-100 within one lookup); compare keywords in the same lookup, not across lookups.
- More than 5 keywords are split into several lookups automatically.
- A row with `error` and `errorMessage` was not charged; the message says what to fix.
