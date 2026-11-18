---
name: apify-seo-data
description: >-
  SEO research with pay-per-use Apify Actors: keyword search volume, CPC and difficulty (Google Ads and Bing), keyword ideas,
  keywords a competitor ranks for and keyword gaps, backlinks and referring domains, DA/PA-style authority, website and page
  traffic estimates, Google SERP results, AI Overview citations, brand visibility in AI answers, and website SEO audits.
  Use when the user says "keyword search volume", "find keyword ideas", "what keywords does X rank for", "keyword gap",
  "check backlinks", "domain authority", "website traffic", "top pages", "SERP for", "rank check", "AI Overview",
  "is my brand mentioned by ChatGPT", or "audit my site for SEO".
author: Rowfeed
author_url: https://apify.com/rowfeed
metadata:
  category: seo
  keywords: "seo, keyword search volume, keyword research, keyword gap, backlinks, referring domains, domain authority, da pa, website traffic, top pages, serp, rank tracking, ai overview, geo, ai visibility, site audit"
---

# SEO data (keywords, backlinks, traffic, SERP, AI visibility)

Answer SEO research questions with live data from pay-per-use Apify Actors, one row per keyword, domain, page or link.

Disclosure: the routed Actors are built and sold by the skill author (Rowfeed); you pay per result on Apify, no subscription.

## Example prompts

Prompts this skill handles:

- "Get monthly search volume, CPC and difficulty for these 200 keywords in the UK"
- "Which keywords does competitor.com rank for that we don't?"
- "Check the backlinks and domain authority of these 50 domains"
- "Is our brand cited in Google AI Overviews or ChatGPT answers for 'best crm for small business'?"

Out of scope (the boundary):

- "Log in to my Google Search Console and pull my clicks" — needs the user's own Search Console access; use Google's API instead.

## Prerequisites

- Apify account ([sign up](https://apify.com)); most of these Actors need a paid Apify plan for live data
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. Identify the question: keywords, competitor keywords, backlinks/authority, traffic, SERP/rank, AI visibility or audit. Pick the Actor from the table below.
2. Fetch the Actor's input schema (`apify actors info ACTOR_ID --input --json`) and build the input. Every Actor takes a list (keywords, domains, queries or URLs), so batch the user's items into one run.
3. Tell the user the estimated cost before large runs (the Actor's Store page lists the price per event) and cap spend with `maxTotalChargeUsd`.
4. Run, then summarise: rows returned, the key numbers the user asked for, and the dataset link.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Search volume, CPC, competition, difficulty | `rowfeed/keyword-search-volume` | community | Bulk lists (thousands of keywords), Google Ads or Bing data, any country/language |
| Keyword ideas from a seed | `rowfeed/keyword-generator` | community | Autocomplete-based ideas, alphabet and question expansion |
| Keywords a site ranks for, keyword gap | `rowfeed/competitor-keywords` | community | Position, volume and traffic per keyword; add `yourDomain` for the gap |
| Backlinks and referring domains | `rowfeed/backlink-checker` | community | Anchors, dofollow, first seen, domain rank; one link per domain mode |
| Link gap vs competitors | `rowfeed/competitor-backlink-checker` | community | Domains linking to competitors but not to you |
| Domain/page authority (DA/PA-style) | `rowfeed/da-pa-checker` | community | Bulk authority, spam score, referring domains |
| Website traffic estimate | `rowfeed/website-traffic-checker` | community | Organic/paid traffic, keywords and rank for many domains at once |
| Top pages by organic traffic | `rowfeed/page-traffic-checker` | community | Which pages of a site get the most Google traffic |
| Google results for a query, rank check | `rowfeed/google-serp-api` | community | Organic results, People Also Ask, any location |
| AI Overview citations | `rowfeed/google-ai-overview-tracker` | community | Whether tracked domains are cited in Google AI Overviews |
| Brand visibility in AI answers | `rowfeed/ai-search-visibility-tracker` | community | Brand vs competitor mentions in AI answers |
| On-page SEO audit of a website | `rowfeed/seo-site-audit` | community | Titles, meta, H1, canonicals, broken links, score per page |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling Actors — choose your interface

### Option A: Apify CLI (recommended for portability)

    apify actors call "rowfeed/keyword-search-volume" \
      -i '{"keywords":["web scraping","price tracking"],"location":"United States"}' \
      --json \
      --user-agent apify-awesome-skills/apify-seo-data \
      2>/dev/null

    apify actors call "rowfeed/backlink-checker" \
      -i '{"targets":["notion.so"],"mode":"one_per_domain","maxBacklinks":100}' \
      --json --user-agent apify-awesome-skills/apify-seo-data 2>/dev/null

    # Fetch results
    apify datasets get-items DATASET_ID --format json \
      --user-agent apify-awesome-skills/apify-seo-data 2>/dev/null

### Option B: Apify MCP connector

Hosted MCP server with these tools preloaded:
`https://mcp.apify.com?tools=rowfeed/keyword-search-volume,rowfeed/competitor-keywords,rowfeed/backlink-checker,rowfeed/da-pa-checker,rowfeed/website-traffic-checker,rowfeed/google-serp-api,rowfeed/google-ai-overview-tracker,rowfeed/seo-site-audit`.
Documented at <https://docs.apify.com/platform/integrations/mcp>.

### Option C: MCP client of your choice (e.g. `mcpc`)

Standalone CLI client. See <https://github.com/apify/mcpc>.

## Troubleshooting

- A row with `error: paid_plan_required` → the account is on the free Apify plan; live data needs any paid plan (the pre-filled example still works).
- A row with `error` and `errorMessage` → that item was not charged; the message says what to fix (unknown location, invalid domain, provider timeout to retry).
- Locations and languages are plain names ("United Kingdom", "German"); unknown ones are explained in the results instead of failing the run.
