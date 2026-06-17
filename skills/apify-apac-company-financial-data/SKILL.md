---
name: apify-apac-company-financial-data
description: Extract APAC company, exchange, and financial-disclosure data via Apify Actors — Korea, Japan, Taiwan, China, Hong Kong, Singapore, India, and SE Asia. Use to look up company registries (Singapore ACRA/UEN, Japan 法人番号, India MCA/OGD), pull listed-company disclosures (Japan TDnet 適時開示, Taiwan MOPS, HKEX 披露易, SGX, India SEBI), track insider/large-shareholder filings (Japan EDINET 大量保有報告書, HKEX 董事股權變動, China A-share 高管增减持), screen stocks on Asian exchanges (KOSPI, TSE/日経225, TWSE, SGX/STI, NSE/BSE India, Eastmoney A-shares, plus Vietnam/Indonesia/Thailand/Philippines/Malaysia), follow IPO calendars (HKEX, Korea, pan-APAC), and check Asian regulator enforcement (Singapore MAS, HK SFC). Triggers — "company registry in Singapore/Japan/India", "listed-company filings in Korea/Taiwan/Hong Kong", "insider filings in Japan/HK/China", "screen Asian stocks / KOSPI / TSE / TWSE / SGX", "Asia IPO calendar", "MAS/SFC enforcement". Factual public data for research — not financial or investment advice.
author: NexGenData
author_url: https://apify.com/nexgendata
---

# APAC Company & Financial Data

Extract and monitor public APAC company, exchange, and financial-disclosure data — Korea, Japan, Taiwan, China, Hong Kong, Singapore, India, and wider Southeast Asia — using NexGenData's Apify Actors. Every result links back to its official source (exchange, registry, or regulator). **This is factual public data for research; it is not financial, legal, or investment advice and contains no trading signals.**

**Rules for every `apify` command (CI-enforced in awesome-skills):**
1. `--user-agent apify-awesome-skills/apify-apac-company-financial-data` (telemetry attribution)
2. `--json` (machine-readable output; use `--format json` for `datasets get-items`)
3. `2>/dev/null` (suppress progress messages that break JSON parsers)

## Prerequisites
- Apify CLI v1.5.0+ (`npm install -g apify-cli`)
- Authenticated: `apify login`, or `export APIFY_TOKEN=...` ([get a token](https://console.apify.com/settings/integrations))
- A few Actors need a **user-supplied source API key** (Korea OpenDART, Japan EDINET). See `references/gotchas.md` before running those.

## Workflow

### Step 1 — Pick the Actor
Identify the **country + data type** (registry / disclosures / insider filings / stock screen / IPO / enforcement) from the user's goal and choose the Actor from **`references/actor-index.md`**. Most tasks map to one country-specific Actor; for "any Asian IPO in the next month" use the pan-APAC `apac-ipo-calendar-sweep`. If the index has no match, search the Store:

    apify actors search "KEYWORDS" --user-agent apify-awesome-skills/apify-apac-company-financial-data --json --limit 10 2>/dev/null

### Step 2 — Fetch the exact input schema (don't guess)
Field names differ by country (e.g. `ticker_filter` vs `tickers` vs `stockCode` vs `stockCodes`); always confirm before running:

    apify actors info "nexgendata/SLUG" --user-agent apify-awesome-skills/apify-apac-company-financial-data --input --json 2>/dev/null

Read `references/gotchas.md` for cost guardrails, locale/encoding notes, date-window defaults, and which Actors need a source API key.

### Step 3 — Run
Keep result caps modest first (these are pay-per-row Actors). Typical call:

    apify actors call "nexgendata/japan-tdnet-timely-disclosures" --input '{"date_from":"2026-06-01","date_to":"2026-06-13","ticker_filter":"7203","max_disclosures":25}' --user-agent apify-awesome-skills/apify-apac-company-financial-data --json 2>/dev/null

From output: `.defaultDatasetId`, `.status`, `.id`. For long-running pulls, start async and poll:

    apify actors start "nexgendata/SLUG" --input '{...}' --user-agent apify-awesome-skills/apify-apac-company-financial-data --json 2>/dev/null
    apify runs info RUN_ID --user-agent apify-awesome-skills/apify-apac-company-financial-data --json 2>/dev/null   # poll until .status == SUCCEEDED

### Step 4 — Fetch results & deliver
    apify datasets get-items DATASET_ID --user-agent apify-awesome-skills/apify-apac-company-financial-data --format json 2>/dev/null

Report: row count, the key fields, and each row's `source_url` (every record links to the official exchange/registry/regulator). Many APAC sources return native-language fields (한국어, 日本語, 中文) — preserve them and add an English gloss. Save large pulls with the Write tool as `YYYY-MM-DD_descriptive-name.csv`/`.json`. For multi-step asks (e.g., "screen KOSPI, then pull each name's disclosures"), chain Actors and suggest the next step.

## Quick map (full list in references/actor-index.md)
| If the user wants... | Actor |
|---|---|
| Singapore company / UEN / director lookup | `nexgendata/singapore-acra-company-lookup` |
| Japan company by 法人番号 (corporate number) | `nexgendata/japan-houjin-bangou-corporate-registry` |
| India company / CIN (OGD master data) | `nexgendata/ogd-india-companies-registry` |
| Japan listed-company disclosures (TDnet 適時開示) | `nexgendata/japan-tdnet-timely-disclosures` |
| Taiwan listed-company announcements (MOPS) | `nexgendata/taiwan-mops-company-announcements` |
| Hong Kong company announcements (HKEXnews 披露易) | `nexgendata/hkex-news-announcements` |
| Singapore exchange disclosures (SGX) | `nexgendata/sgx-company-announcements` |
| India SEBI filings | `nexgendata/india-sebi-filings-tracker` |
| Japan large-shareholder / buyback (EDINET 大量保有報告書) | `nexgendata/japan-edinet-insider-filings` |
| Hong Kong director dealings / short positions (HKEX) | `nexgendata/hkex-insider-short-tracker` |
| China A-share insider transactions (高管增减持) | `nexgendata/china-ashare-insider-trades` |
| Screen Korean stocks (KOSPI/KOSDAQ) | `nexgendata/kospi-stock-screener` |
| Screen Japanese stocks (TSE / 日経225) | `nexgendata/tse-japan-stock-screener` |
| Screen Taiwan stocks (TWSE) | `nexgendata/twse-stock-screener` |
| Screen Singapore stocks (SGX / STI) | `nexgendata/sgx-singapore-stock-screener` |
| Screen India stocks (NSE/BSE) | `nexgendata/nse-india-stock-screener`, `nexgendata/bse-india-stock-screener` |
| Screen China A-shares (Eastmoney) | `nexgendata/eastmoney-china-stock-screener` |
| Asia-wide IPO calendar | `nexgendata/apac-ipo-calendar-sweep` |
| Hong Kong IPO calendar | `nexgendata/hkex-ipo-calendar` |
| Korea IPO pipeline (코스피/코스닥) | `nexgendata/korea-ipo-pipeline-tracker` |
| Asian regulator enforcement (MAS / SFC) | `nexgendata/singapore-mas-enforcement`, `nexgendata/hk-sfc-enforcement-tracker`, `nexgendata/finma-mas-sfc-enforcement-tracker` |

## Compliance
All data is public company, exchange, and regulatory data, retrieved from official APAC sources (exchanges, company registries, and financial regulators). Present it as facts with source links. **Never frame output as financial/investment/legal advice, a recommendation, or a trading signal.** Not affiliated with any exchange, registry, or regulator.
