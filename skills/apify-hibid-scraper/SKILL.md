---
name: apify-hibid-scraper
description: "Follow HiBid auctions and lots as clean rows with the current bid, minimum bid, close date, auctioneer and currency. Search closing lots, inspect a lot, or get new, changed and removed lots since your last run. Built for resellers and auction arbitrage buyers. Uses the Apify Actor redomic/hibid-scraper. Use when the user asks to 'hibid scraper', 'hibid auctions', 'hibid lots', or wants HiBid Auction Scraper results as structured JSON or CSV."
metadata:
  category: data-extraction
  keywords: "hibid scraper, hibid auctions, hibid lots"
author: Redomic
author_url: https://apify.com/redomic
---

# HiBid Auction Scraper

Follow HiBid auctions and lots as clean rows with the current bid, minimum bid, close date, auctioneer and currency. Search closing lots, inspect a lot, or get new, changed and removed lots since your last run. Built for resellers and auction arbitrage buyers.

Disclosure: the routed Actor, `redomic/hibid-scraper`, is built and monetised by this skill's author.

## Example prompts

Prompts this skill handles:

- "Get HiBid Auction Scraper results for mode search; query coin; status OPEN; sortOrder TIME_LEFT"
- "Get HiBid Auction Scraper results for mode search; query coin; status CLOSING; sortOrder TIME_LEFT"
- "Get HiBid Auction Scraper results for mode search; query gold; status OPEN; sortOrder TIME_LEFT"

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

- `mode` (string): search returns current lots; auctions returns matching auctions; detail fetches full records for lot ids; monitor reports only new, changed and removed lots since the previous run.
- `query` (string): What to look for on HiBid, for example coins, jewelry, estate or equipment. Blank runs use 'coin'.
- `queries` (array): Several search terms in one run. Each term gets its own status row. Leave empty to use the single Search term above.
- `status` (string): Which lots or auctions to include. OPEN covers active listings, CLOSING those ending soon, CLOSED finished lots.
- `soldOnly` (boolean): Keep sold comps, not finished lots that never sold. Closed lots need a hammer price to appear; lots still in bidding are kept. On by default.
- `sortOrder` (string): TIME_LEFT puts lots closing soonest first. LOT_NUMBER follows the catalogue order. NO_ORDER uses HiBid's default relevance order.
- `auctionId` (integer): Limit lots to one HiBid auction. Leave empty to search every auction.
- `shippingOffered` (boolean): Keep only lots where the auctioneer offers shipping.
- `lotIds` (array): For mode 'detail': numeric HiBid lot ids to fetch full descriptions and close prices for.
- `maxItems` (integer): Upper limit on rows returned in this run, across all inputs. The Actor stops fetching once this many rows are ready. Maximum 1000.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| HiBid Auction Scraper | `redomic/hibid-scraper` | community | hibid scraper |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "redomic/hibid-scraper" \
      -i '{"mode": "search", "query": "coin", "status": "OPEN", "soldOnly": true, "sortOrder": "TIME_LEFT", "shippingOffered": false, "maxItems": 100}' \
      --json \
      --user-agent apify-awesome-skills/apify-hibid-scraper \
      2>/dev/null

    apify actors info "redomic/hibid-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-hibid-scraper 2>/dev/null

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-hibid-scraper 2>/dev/null
