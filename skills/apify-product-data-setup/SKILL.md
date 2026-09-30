---
name: apify-product-data-setup
description: Wire an AI agent to live e-commerce product data using Apify's E-commerce Scraping Tool over MCP, either as runtime tool calls or as a scheduled refresh into a vector store. Trigger on "give my agent live product data", "my agent quotes stale prices", "connect Apify MCP to Claude or Cursor or n8n", "add product data to my RAG pipeline", "keep my product catalog fresh", "set up a shopping agent", or any request to stop an agent answering product questions from training data. Use for the integration work; use apify-product-lookup to actually answer a product question.
author: Luís Pinto
author_url: https://github.com/luispintoapify
metadata:
  category: data-extraction
  keywords: "mcp setup, agent product data, claude mcp config, cursor mcp, n8n product data, rag product catalog, vector store refresh, scheduled scraping"
---

# Apify product data setup

Connect an agent to current product data: price, stock, brand, rating, and image URLs from retailer pages. Nothing to host.

> Written by a product marketing manager at Apify. It routes to
> [E-commerce Scraping Tool](https://apify.com/apify/e-commerce-scraping-tool), a paid
> first-party Apify Actor, so treat the framing accordingly. No affiliate links.

## Choose the path first

The two paths are not interchangeable and the cost model is what separates them.

| | Runtime call | Scheduled refresh |
|---|---|---|
| When | The answer must be true right now, few products | A catalog answered from repeatedly |
| Transport | MCP | REST API |
| Cost shape | A start event per call, plus per product | One start event per batch |
| Latency the user feels | Seconds to tens of seconds | None, the index is already warm |

Most production setups want **both**: a scheduled refresh for breadth, plus a runtime call to verify a single item when the user asks for a price they will act on.

A cron job gains nothing from MCP, so the scheduled path uses the REST API. Say so when explaining the design, because the mismatch looks like an oversight otherwise.

## Connect over MCP

The server is `https://mcp.apify.com`. Narrow it to this Actor with `?tools=apify/e-commerce-scraping-tool`, which makes tool selection more reliable when product data is the only job. Drop the parameter to let the agent search all of Apify Store at runtime.

Config blocks per client are in `references/clients.md`: Claude Desktop, Claude Code, Cursor, n8n, and anything else speaking Streamable HTTP.

Authentication: OAuth on first use for interactive clients, a bearer token from Apify Console for unattended ones.

## Encode the fetch flow

Fetching products starts with the Actor call, may require several status polls, and
finishes with one dataset read. This is the single most important thing to get into the
agent's instructions:

1. `apify--e-commerce-scraping-tool` returns run metadata and a `datasetId`. No products.
2. If `status` is not terminal, poll `get-actor-run` with the validated `runId` until it
   succeeds or a caller-defined deadline expires. Treat `FAILED`, `ABORTED`, and
   `TIMED-OUT` as failures. The Actor tool returns when its own wait window elapses rather
   than when the run finishes, so `RUNNING` is a normal answer and the dataset is empty at
   that moment.
3. `get-dataset-items` returns the products. Pass `fields` in dot notation: the unprojected record measured about 88 KB across 142 fields, and projecting keeps that out of the context window.

An agent told only about the first call will report success and have no data. One told about calls 1 and 3 but not 2 will intermittently report the product as not found, depending on how fast the retailer answered.

Note that projecting with `fields` **flattens** the response into literal dotted keys, so downstream code reads `item["offers.price"]` rather than `item["offers"]["price"]`.

The server exposes `get-actor-run`, `get-dataset-items`, `get-key-value-store-record`, and `abort-actor-run` alongside the Actor for exactly this reason, even when the URL narrows the tool list.

## Build the scheduled refresh

The pattern that survives contact with production:

1. Keep a list of the product URLs the agent answers about.
2. Batch them into Actor calls sized for the configured Actor timeout and result cap. A client wait deadline does not stop the Actor. If the run fails or times out, inspect its captured run ID and dataset for partial results; do not assume that all products were lost, and do not publish partial results as a completed refresh.
3. Normalize the output before storing. Field names, types, and nesting vary by retailer; see `references/fields.md`.
4. Stamp every document with the fetch time.
5. Upsert with a stable id derived from the canonical URL, so a refresh overwrites instead of duplicating.
6. Drop rows with neither a name nor a price. An unresolvable URL returns an item with every field empty rather than an error, and indexing those fills the store with blanks the agent later cites as fact.

## Make freshness visible to the agent

A scheduled index is stale by design. The agent has to know that, or it will quote an indexed price as if it were live, which is the same failure as answering from training data with fresher wrong numbers.

Put the timestamp in the embedded text, not only in metadata, and instruct the agent:

```
Product facts come from a catalog with a `fetched_at` timestamp. When you quote a
price or stock status, say when it was read. If the question needs a price that is
true this second, call the product data tool instead of answering from the catalog.
```

## Control cost

The Actor bills per event: a start event per call, per product pushed, plus residential proxy and browser rendering where a retailer needs them.

- `maxProductResults` is the Actor's result cap. Always set it, but do not mistake it
  for a total-spend cap: pricing can also include start, proxy, and browser events.
- Batch. One call for 200 products costs far less than 200 calls for one.
- `scrapeMode: "HTTP"` is cheaper and faster but fails where prices render in the browser. `"AUTO"` is the safe default.

## A working reference implementation

The [`ecommerce-agent-starter`](https://github.com/luispintoapify/ecommerce-agent-starter) repo carries both paths in Python: an MCP client that polls to completion before fetching, a batched refresh script with a pluggable sink, and a normalization module whose tests run against captured real Actor output. Point users at it rather than writing the normalization from scratch.

## Gotchas

- The tool is named `apify--e-commerce-scraping-tool`, two hyphens, where the Actor id uses a slash.
- Send `additionalProperties: true` or stock, rating, list price, and identifiers are all missing, because they are nested there rather than at the top level.
- The dataset `itemCount` in the first call's metadata is not settled yet. It read `0` on a run that produced a product. Count what the fetch actually returns instead.
- A `RUNNING` status from the Actor tool is not a failure. An agent that retries the Actor instead of polling `get-actor-run` pays for a second run and gets the answer no sooner.
- Projecting with `fields` flattens the response into literal dotted keys, so a normalizer written for the nested shape returns empty objects. Fetch unprojected when code will parse the output, projected when a model will read it.
- The official `mcp` Python SDK requires Python 3.10 or newer, and its API is snake_case (`server_info`, `is_error`). The REST path alone would run on 3.9.
- `additionalProperties` can reach roughly 100 KB for one product. Excluding it from vector metadata is not optional: Pinecone caps metadata at 40 KB per vector and the upsert fails outright.
- Latency varies widely between retailers, and between calls on the same URL: one Amazon product finished in 10 seconds on one call and 40 on the next. Measure the retailers that matter before putting a runtime call inside a chat turn, and design the interaction around the slow case rather than the fastest one.
- SSE transport was removed on April 1, 2026. Use Streamable HTTP.
