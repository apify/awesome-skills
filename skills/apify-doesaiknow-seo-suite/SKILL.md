---
name: apify-doesaiknow-seo-suite
description: >-
  Get SEO and AI-search data with the doesaiknow Apify Actors — keyword search volume + CPC (Google AND
  Bing), AI keyword clustering / topical maps, a competitor's ranked keywords + keyword gap, backlinks and
  referring domains, AI brand visibility across ChatGPT/Perplexity/Gemini (AEO/GEO share of voice), and
  Amazon keyword volume + reverse-ASIN. Use when the user asks for keyword research, search volume or CPC,
  keyword difficulty/clustering, a topical map, competitor keywords, a keyword gap, backlinks or referring
  domains, link prospecting, "answer engine optimization" / "generative engine optimization", whether a
  brand is cited in ChatGPT/Perplexity/Gemini, Amazon (FBA) keyword research, or a reverse-ASIN lookup —
  especially when they want it programmatically without an Ahrefs / Semrush / Helium 10 subscription.
author: doesaiknow
author_url: https://apify.com/doesaiknow
---

# doesaiknow SEO suite

A family of native-data, pay-per-event Apify Actors for SEO and AI-search work. Pick the right Actor for
the user's goal, run it, and return the dataset. All run under limited permissions and bill only on success.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. Understand the user's goal and pick the Actor(s) from the routing table below.
2. Fetch the Actor's input schema (via MCP or its Store page) and build a valid input.
3. Run the Actor; if a scan is large/paid, confirm the estimated cost with the user first.
4. Deliver results — count, a short summary of the key fields, and the dataset/console link.

## Actor routing

`Tier` = `apify` (Apify-maintained) or `community` (third-party). These are all `community`.

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Search volume, CPC, competition, 12-mo trend (Google **+ Bing**) | `doesaiknow/doesaiknow-keyword-metrics-apify` | community | Bulk keyword metrics, incl. Bing |
| Group keywords into clusters + a SERP-validated topical map | `doesaiknow/ai-keyword-clustering-tool-topical-clustering-bulk-serp` | community | Content planning, topical authority |
| Every keyword a competitor domain ranks for (+ keyword gap) | `doesaiknow/doesaiknow-competitor-keywords-apify` | community | Competitor teardown, gap analysis |
| Backlinks, referring domains, competitor backlink gap | `doesaiknow/backlink-checker-api-referring-domains-competitor-gap` | community | Off-page audit, link prospecting |
| Is a brand cited/recommended in ChatGPT/Perplexity/Gemini? | `doesaiknow/ai-brand-visibility-tracker-chatgpt-perplexity-gemini` | community | AEO/GEO, AI share of voice |
| Amazon keyword volume / related keywords / reverse-ASIN | `doesaiknow/amazon-keyword-research-tool-volume-reverse-asin` | community | Amazon/FBA listing keywords |

## Calling Actors — choose your interface

Cross-tool compatibility is your responsibility. Use whichever fits your runtime.

### Option A: Apify CLI (recommended for portability)

Three flags on every call:

    apify actors call "doesaiknow/doesaiknow-keyword-metrics-apify" \
      -i '{"keywords":["keyword research","seo tools"],"country":"us","language":"en"}' \
      --json \
      --user-agent apify-awesome-skills/apify-doesaiknow-seo-suite \
      2>/dev/null

| Flag | Why |
|------|-----|
| `--json` | Stable machine-readable output |
| `--user-agent apify-awesome-skills/apify-doesaiknow-seo-suite` | Apify telemetry attribution |
| `2>/dev/null` | Suppress progress messages that break JSON |

### Option B: Apify MCP server

The Actors are exposed as tools via the [Apify MCP server](https://mcp.apify.com); call by Actor ID with a
JSON input. The MCP server also exposes each Actor's input schema — read it to discover every option.

## Actor inputs & examples

Confirm the full input via each Actor's input schema; the load-bearing fields are below.

**Keyword Metrics Pro** — Google **+ Bing** volume, CPC, competition, 12-month trend.

    {"keywords":["best crm","crm software"],"country":"us","language":"en"}

**AI Keyword Clustering Tool** — clusters + topical map (`businessContext` required).

    {"keywords":["best crm","crm for startups"],"businessContext":"CRM software for SMBs","country":"us"}

**Competitor Keyword Research** — `mode:"ranked"` for their keywords; `"gap"` + `compareToDomain` for the gap.

    {"target":"competitor.com","mode":"ranked","maxKeywords":250}

**Backlink Checker API** — `mode`: `summary` | `referring_domains` | `competitor_gap`. Prefer referring domains over raw backlink counts.

    {"domain":"example.com","mode":"summary"}

**AI Brand Visibility Tracker** — share of voice vs competitors across AI engines.

    {"brand":"HubSpot","category":"CRM software","competitors":["Salesforce","Zoho"],"queries":["best CRM 2026","HubSpot alternatives"],"platforms":["chatgpt","perplexity","gemini"],"language":"us","tier":"pro_auditor"}

> `tier:"demo"` is free but only serves pre-seeded showcase brands (HubSpot, Salesforce, Ahrefs, Semrush, Moz).
> For any other brand use `tier:"pro_auditor"` (billed per query) with ≥3 queries.

**Amazon Keyword Research Tool** — `mode`: `search_volume` | `related_keywords` | `reverse_asin`.

    {"mode":"search_volume","keywords":["wireless earbuds","yoga mat"],"country":"us"}
    {"mode":"reverse_asin","asin":"B0BDHWDR12","country":"us","maxKeywords":100}

`reverse_asin` returns every keyword an ASIN ranks for + position (the Helium 10 "Cerebro" use case). Amazon
volume is **estimated**; reverse-ASIN positions are **factual**.

## Chained workflows

- **Content/SEO plan:** Keyword Metrics Pro (volume/CPC) → AI Keyword Clustering (topical map) → one page per cluster.
- **Competitor teardown:** Competitor Keyword Research (ranked + gap) → Backlink Checker (referring domains) → Keyword Metrics Pro on the gap keywords.
- **AEO / AI-search audit:** AI Brand Visibility Tracker on buyer-intent queries → see which competitors AIs cite → act on the cited sources.
- **Amazon listing:** Amazon `search_volume` on seed terms + `reverse_asin` on top competitor ASINs → build the listing keywords.

## Cost & safety

- Every Actor is **pay-per-event** — billed only on a successful run, never on failed/empty runs. Warn the user before a large/paid scan.
- Cap inputs (`maxKeywords`, keyword-list size) to keep cost predictable; free Apify plans are limited per run.
- Actors run under **limited permissions** — they only call their data API and write your dataset; they never touch the rest of the Apify account.
