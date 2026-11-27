---
name: apify-tradeindia-supplier-leads-scraper
description: "One run returns TradeIndia supplier leads: company, product, city, published price in INR or USD, MOQ, badges and product URL. Search by keyword, open product pages for public company facts, or monitor price and MOQ changes since your last run. Uses the Apify Actor redomic/tradeindia-supplier-leads-scraper. Use when the user asks to 'tradeindia scraper', 'tradeindia products scraper', 'tradeindia supplier leads', or wants TradeIndia Scraper — Supplier Leads results as structured JSON or CSV."
metadata:
  category: data-extraction
  keywords: "tradeindia scraper, tradeindia products scraper, tradeindia supplier leads, tradeindia supplier leads scraper"
author: Redomic
author_url: https://apify.com/redomic
---

# TradeIndia Scraper — Supplier Leads

One run returns TradeIndia supplier leads: company, product, city, published price in INR or USD, MOQ, badges and product URL. Search by keyword, open product pages for public company facts, or monitor price and MOQ changes since your last run.

Disclosure: the routed Actor, `redomic/tradeindia-supplier-leads-scraper`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get TradeIndia Scraper — Supplier Leads results for query basmati rice; maxItems 12; maxPages 1"
- "Get TradeIndia Scraper — Supplier Leads results for mode search; query rice mill plant; maxItems 10; maxPages 1"
- "Get TradeIndia Scraper — Supplier Leads results for mode search; query rice polishing machine; maxItems 8; maxPages 1"

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

- `mode` (string): search returns supplier rows for a keyword; detail opens product URLs for the full company block; monitor returns only new, changed and removed rows since the last run.
- `query` (string): The TradeIndia product keyword, e.g. 'basmati rice' or 'rice mill plant'. A manufacturer page URL also works. Used by search and monitor mode.
- `category` (string): Keep only listings whose TradeIndia category contains this text, e.g. '1121 basmati rice'.
- `city` (string): Keep only suppliers in this city, e.g. 'Ahmedabad'. Applied while pages are collected, so maxItems is honoured after filtering.
- `productUrls` (array): TradeIndia product page URLs for detail mode, e.g. https://www.tradeindia.com/products/1121-white-sella-basmati-rice-9329845.html.
- `maxItems` (integer): Maximum result rows to return, up to 5000. Pagination keeps going past the first page until this many rows are collected.
- `maxPages` (integer): Safety cap on how many result pages are fetched in one run. 28 suppliers are on each page.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| TradeIndia Scraper — Supplier Leads | `redomic/tradeindia-supplier-leads-scraper` | community | tradeindia scraper |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/tradeindia-supplier-leads-scraper" \
      -i '{"mode": "search", "query": "basmati rice", "maxItems": 100, "maxPages": 100}' \
      --json \
      --user-agent apify-awesome-skills/apify-tradeindia-supplier-leads-scraper \
      2>/dev/null

    apify actors info "redomic/tradeindia-supplier-leads-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-tradeindia-supplier-leads-scraper 2>/dev/null

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-tradeindia-supplier-leads-scraper 2>/dev/null
