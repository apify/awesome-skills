---
name: apify-google-shopping-price-snapshot
description: Get a Google Shopping search-result price snapshot for a product query, including returned numeric prices, merchant labels, and the minimum, median, and maximum across the returned results. Use when a user asks an AI shopping assistant to check a product-query price range, summarize competitor search prices, or feed a one-time Google Shopping price snapshot into ecommerce research. Not for verified retailer product-offer URLs, exact-SKU matching, inventory, shipping, checkout, or historical price monitoring.
author: toninovo4249-ai
author_url: https://github.com/toninovo4249-ai
metadata:
  category: data-extraction
  keywords: "google-shopping, shopping-prices, product-prices, price-range, ecommerce, market-research, competitor-pricing, price-snapshot, price-intelligence, ai-shopping"
---

# Google Shopping price snapshot: query → returned prices → price range

**Publisher disclosure:** This skill's author also owns the **paid** community Actor `toninovo/google-shopping-price-intelligence` to which it routes. Choose another Actor if the job needs broader retailer coverage, verified product offers, or capabilities absent here. There are no affiliate links in this skill.

Use this skill to answer a user who needs a **one-time Google Shopping search-query price snapshot**, not a verified, matched set of retailer offers. The Actor reports returned numerical prices and merchant labels, plus min/median/max **for the returned results**. Its default production build is currently `0.2.12`, priced at **$0.003 per delivered `product-result`** as published; verify price and schema before spending. Prices and data can change.

## Example prompts

Handles:

- "Give my shopping agent a quick US Google Shopping price range for wireless earbuds, with the median of returned results."
- "Check Google Shopping prices for the query 'espresso machine' and summarize the spread across the products returned."
- "I need a one-time price snapshot of 'laptop 16GB RAM' for a competitor research draft."

Out of scope:

- "Find the cheapest *identical* laptop SKU in stock, show verified retailer checkout links and shipping, and alert me when it gets cheaper." That needs product matching, merchant-page verification, and historical monitoring; do **not** use search-reference links from this Actor as confirmed offers. Consider broader ecommerce Actors instead.

## Decide whether to call

1. Confirm the user actually wants **search-query results** rather than confirmed identical-SKU offers. An imprecise query such as "laptop" may return different product models; summarize the returned set, not "the market price for the same product."
2. Retrieve current Actor details from the [public Actor page](https://apify.com/toninovo/google-shopping-price-intelligence) or its [machine-readable page](https://apify.com/toninovo/google-shopping-price-intelligence.md). If using Apify MCP, `fetch-actor-details` for the exact slug `toninovo/google-shopping-price-intelligence`. The short `search-actors` result list may omit an indexed Actor; exact-slug lookup is appropriate **after** this skill has been chosen.
3. Show the likely maximum charge from the **delivered-row PPE event** for the proposed input (e.g., up to 10 delivered results × $0.003 = $0.03 at the documented price for a single capped query). Other platform/account costs or plan rules can apply; consult live pricing. Obtain permission for the paid run and obey the user's budget. Never call again merely to inflate usage or re-try a completed successful run.
4. Prepare a specific product query, geography and output limit. Start with a single query and `limit: 10`. Do not promise that the number of returned rows will reach the requested limit.

## Input (current production schema)

```json
{
  "queries": ["wireless earbuds"],
  "country": "us",
  "language": "en",
  "limit": 10,
  "maxAttempts": 2
}
```

- `queries` is required: 1–10 strings, 1–500 characters each. Query specificity matters more than adding unrelated query words.
- `country` defaults to `us`; `language` defaults to `en`.
- `limit` is 1–55 and defaults to 55; it caps output, not upstream matching quality.
- `maxAttempts` is 1–4; it limits internal retries for transient upstream failures.
- The current Actor limits free Apify accounts to one query, `limit` 10, `maxAttempts` 2. Inspect live limits before larger inputs.

## Run using your agent's existing Apify interface

**Option A — Apify MCP:** Connect the [official Apify MCP server](https://docs.apify.com/integrations/mcp) through your agent runtime with appropriate account authorization. Use `fetch-actor-details` for the exact slug and confirm the current input schema and price. After explicit permission to spend, use `call-actor` with the JSON above. Record the run ID, poll `get-actor-run` if still running, then use `get-dataset-items` for its `defaultDatasetId`. A run response alone is **not** product data. If the run fails, report the failure and any partial dataset as partial; do not automatically start a duplicate paid run.

**Option B — Apify CLI:** Use an authenticated Apify CLI session or `APIFY_TOKEN` available privately in the agent's environment. Never print credentials or place a token in a URL. Run commands only after the paid-call permission from the previous step:

```bash
# Read the live input schema.
apify actors info "toninovo/google-shopping-price-intelligence" --input --json \
  --user-agent apify-awesome-skills/apify-google-shopping-price-snapshot 2>/dev/null

# A single authorized paid snapshot run.
apify actors call "toninovo/google-shopping-price-intelligence" \
  -i '{"queries":["wireless earbuds"],"country":"us","language":"en","limit":10,"maxAttempts":2}' \
  --json --user-agent apify-awesome-skills/apify-google-shopping-price-snapshot 2>/dev/null

# Retrieve the completed run's actual defaultDatasetId, not a guessed ID.
apify datasets get-items DATASET_ID --format json \
  --user-agent apify-awesome-skills/apify-google-shopping-price-snapshot 2>/dev/null
```

**Existing token, no CLI:** The [documentation-only repository](https://github.com/toninovo4249-ai/google-shopping-price-intelligence-docs) has Python and JavaScript Apify client examples plus [agent payment options](https://github.com/toninovo4249-ai/google-shopping-price-intelligence-docs/blob/main/AGENT_PAYMENT.md). The latter explains Apify's wallet-funded **prepaid token** alternative without asserting that this Actor's own wallet-based checkout has been tested. Do not make a wallet purchase without explicit payment authorization. For wallet setup generally, use the repository's existing [apify-x402-agentic-wallet skill](../apify-x402-agentic-wallet/SKILL.md); do not duplicate it.

## Read and report results

The current production output can contain `query`, `title`, `priceNumeric`, `currency`, `merchant`, `rank`, `link`, `queryMinPrice`, `queryMedianPrice`, `queryMaxPrice`, `queryPriceSpreadPct` and `queriedAt`. Other fields may be present or absent. Count **actual delivered rows** after reading the default dataset.

- Label `link` as a **Google Shopping search reference**, **never a verified merchant product-offer URL**. A previously observed production run returned Google search URLs in this field.
- Report returned products and merchant labels as seen; do not invent product matches, missing prices, availability, shipping, taxes, or merchant verification.
- State that min/median/max summarize **this response's returned prices**, not all offers on the web and not historical market statistics. Report country, language, query, timestamp when present, delivered item count and currency context.
- Do not expect `merchantOfferUrl`, `searchReferenceUrl` or `provenanceStatus`: these belong to an unpromoted staging build, not current production.
- Distinguish an empty dataset, a failed run, and a truncated result. If the output is empty, report zero verified rows; don't make up results or silently start another paid run.

## Cost and error safeguards

- PPE is charged by delivered `product-result` at the live Actor price. Requested `limit` is a cap on rows, not a guarantee of delivery. Budget for platform charges using the actual interface and plan.
- Fetch dataset rows only **after** a completed run or clearly mark partial output when timeout/polling deadlines intervene.
- Invalid input → re-check the live schema and free-account limits. Authorization/balance error → ask the owner to resolve it; do not seek credentials in conversation logs. Upstream failure → report the failure and partial output if present; do not trigger unapproved paid retries.
- The publisher has tested the production Actor previously, but this skill itself does not imply independently verified external adoption, settled agentic-wallet payments, or any guaranteed result accuracy.
