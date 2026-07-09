---
name: apify-sec-regulatory-intelligence
description: Monitor and extract U.S. SEC and global financial-regulator filings via Apify Actors. Use to track insider trades (Form 4), material corporate events (8-K), institutional 13F holdings and changes, activist stakes (13D/G), private placements (Form D / Reg A+), late-filing warnings (Form NT), fund holdings & proxy votes (N-PORT / N-PX), investment advisers (Form ADV), restricted-stock pre-sales (Form 144), SEC litigation & enforcement, FINRA BrokerCheck, or enforcement from global regulators (Swiss FINMA, Singapore MAS, Hong Kong SFC, India SEBI, Australia ASIC, Japan EDINET, China A-share, UK RNS). Triggers - "track insider buying", "who's buying/selling [ticker]", "recent 8-K events", "13F changes for [fund]", "activist 13D filings", "new Form D raises", "SEC enforcement this year", "check a broker on FINRA", "companies that filed late", "regulatory enforcement in [country]", "SEC filings for [company]". Factual public filing data for research - not financial, legal, or investment advice.
author: NexGenData
author_url: https://apify.com/nexgendata
---

# SEC & Regulatory Intelligence

Extract and monitor public regulatory filings - U.S. SEC plus major global regulators - using NexGenData's Apify Actors. Every result links back to its official source filing. **This is factual public data for research; it is not financial, legal, or investment advice and contains no trading signals.**

**Rules for every `apify` command (CI-enforced in awesome-skills):**
1. `--user-agent apify-awesome-skills/apify-sec-regulatory-intelligence` (telemetry attribution)
2. `--json` (machine-readable output; use `--format json` for `datasets get-items`)
3. `2>/dev/null` (suppress progress messages that break JSON parsers)

## Prerequisites
- Apify CLI v1.5.0+ (`npm install -g apify-cli`)
- Authenticated: `apify login`, or `export APIFY_TOKEN=...` ([get a token](https://console.apify.com/settings/integrations))

## Workflow

### Step 1 — Pick the Actor
Identify the filing type / regulator from the user's goal and choose the Actor from **`references/actor-index.md`**. Most U.S. tasks map to one Actor; for "all SEC events for a company" use `nexgendata/sec-event-router` (unified timeline). If the index has no match, search the Store:

    apify actors search "KEYWORDS" --user-agent apify-awesome-skills/apify-sec-regulatory-intelligence --json --limit 10 2>/dev/null

### Step 2 — Fetch the exact input schema (don't guess)
Schemas evolve; always confirm fields before running:

    apify actors info "nexgendata/SLUG" --user-agent apify-awesome-skills/apify-sec-regulatory-intelligence --input --json 2>/dev/null

Read `references/gotchas.md` for cost guardrails and date-window defaults before running.

### Step 3 — Run
Keep result caps modest first (these are pay-per-row Actors). Typical call:

    apify actors call "nexgendata/sec-form-4-insider-trading-scraper" --input '{"dateFrom":"2026-06-01","dateTo":"2026-06-13","tickers":["AAPL","NVDA"],"transactionTypes":["P","S"],"maxFilings":25}' --user-agent apify-awesome-skills/apify-sec-regulatory-intelligence --json 2>/dev/null

From output: `.defaultDatasetId`, `.status`, `.id`. For long-running pulls, start async and poll:

    apify actors start "nexgendata/SLUG" --input '{...}' --user-agent apify-awesome-skills/apify-sec-regulatory-intelligence --json 2>/dev/null
    apify runs info RUN_ID --user-agent apify-awesome-skills/apify-sec-regulatory-intelligence --json 2>/dev/null   # poll until .status == SUCCEEDED

### Step 4 — Fetch results & deliver
    apify datasets get-items DATASET_ID --user-agent apify-awesome-skills/apify-sec-regulatory-intelligence --format json 2>/dev/null

Report: row count, the key fields, and each row's `source_url` (every filing links to the official regulator). Save large pulls with the Write tool as `YYYY-MM-DD_descriptive-name.csv`/`.json`. For multi-step asks (e.g., "insider clusters, then pull each company's 8-Ks"), chain Actors and suggest the next step.

## Quick map (full list in references/actor-index.md)
| If the user wants... | Actor |
|---|---|
| Insider buys/sells (Form 4) | `nexgendata/sec-form-4-insider-trading-scraper` |
| 3+ insiders buying the same stock | `nexgendata/insider-cluster-detector` |
| Material corporate events (8-K) | `nexgendata/sec-form-8k-material-events-scraper` |
| Institutional 13F holdings + deltas | `nexgendata/sec-form-13f-tracker-pro`, `nexgendata/13f-holdings-delta-tracker` |
| Activist stakes (13D/G) | `nexgendata/sec-schedule-13dg-activist-tracker` |
| Private placements (Form D / Reg A+) | `nexgendata/sec-form-d-tracker`, `nexgendata/sec-reg-a-plus-crowdfunding-offerings-tracker` |
| Late-filing early warnings (NT) | `nexgendata/sec-form-nt-late-filing-tracker` |
| Any-filing company search (10-K/10-Q…) | `nexgendata/sec-edgar-search`, `nexgendata/sec-edgar-filings-scraper` |
| Unified per-company SEC timeline | `nexgendata/sec-event-router` |
| SEC litigation / enforcement | `nexgendata/sec-litigation-releases` |
| Broker / firm registration check | `nexgendata/finra-brokercheck-search` |
| Global regulator enforcement | `nexgendata/finma-mas-sfc-enforcement-tracker`, `nexgendata/hk-sfc-enforcement-tracker`, `nexgendata/singapore-mas-enforcement`, `nexgendata/australia-asic-enforcement`, `nexgendata/india-sebi-filings-tracker` |
| APAC insider/ownership | `nexgendata/japan-edinet-insider-filings`, `nexgendata/hkex-insider-short-tracker`, `nexgendata/china-ashare-insider-trades` |
| Filings as Markdown for RAG/LLM | `nexgendata/sec-filings-rag-markdown`, `nexgendata/regulatory-enforcement-rag` |

## Compliance
All data is public regulatory filing data, retrieved from official sources (sec.gov and equivalents). Present it as facts with source links. **Never frame output as financial/investment/legal advice, a recommendation, or a trading signal.** Not affiliated with the U.S. SEC, FINRA, or any regulator.
