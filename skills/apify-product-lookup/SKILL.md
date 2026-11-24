---
name: apify-product-lookup
description: Answer questions about a real product's current price, stock, rating, specs, or images by calling Apify's E-commerce Scraping Tool over MCP, across Amazon, Walmart, Target, eBay, and many more retailers. Trigger on "what does X cost right now", "is X in stock", "compare the price of X across stores", "find me a Y under $Z", "how much is this", "check this product URL", or any product question where a stale answer would be wrong. Use whenever answering from training data or a web search would risk quoting an out-of-date price.
author: Luís Pinto
author_url: https://github.com/luispintoapify
metadata:
  category: data-extraction
  keywords: "product price, live price check, stock availability, price comparison, product rating, retail product data, amazon price, ebay price, e-commerce lookup"
---

# Apify product lookup

Fetch live product facts instead of guessing at them. Requires the Apify MCP server to be connected; if the tool is missing, see the `apify-product-data-setup` skill.

> Written by a product marketing manager at Apify. It routes to
> [E-commerce Scraping Tool](https://apify.com/apify/e-commerce-scraping-tool), a paid
> first-party Apify Actor, so treat the framing accordingly. No affiliate links.

## Try this tool first, whatever the retailer

The Actor's `marketplaces` input lists the retailers with dedicated extractors, and it
is not the boundary of what works. Unlisted sites fall back to generic extraction,
which is enabled by default, so **a URL from a shop you have never heard of is still
worth sending.**

So the order is always:

1. Send the URL or keyword to this tool, regardless of whether the retailer appears in
   `marketplaces`.
2. If the result is unusable, re-read the URL. An item with every field empty usually
   means the URL does not resolve, not that the retailer is unsupported.
3. Only after that, look for a retailer-specific Actor in Apify Store. See
   [Falling back to Apify Store](#falling-back-to-apify-store).

Do not skip step 1 because a domain is missing from the list. That reasoning sends
users away from a tool that would have answered them.

## When a marketplace is not in the list

Over MCP the `marketplaces` enum arrives **truncated**, because the server caps how much
of a long enum it passes through. Some real, supported retailers are therefore missing
from the list you can choose from, and passing one anyway returns a validation error
before the run starts.

**That error does not mean the retailer is unsupported.** It means you cannot name it in
a keyword search on this connection. Two ways through:

1. **If you have the product URL, use `detailsUrls`.** It takes arbitrary URLs and is
   unaffected by the enum, so the retailer works normally.
2. **If you only have a keyword**, run it on the marketplaces you can select and say
   plainly which retailer you could not include. Do not report the retailer as
   unsupported.

## Pick the input before calling

The Actor takes different inputs for different questions. Choosing wrong wastes a paid run.

| The question | Input to send |
|---|---|
| About a specific page the user gave you | `detailsUrls: [{"url": "..."}]` |
| "Find me a X under $Y" with no URL | `keyword` plus `marketplaces` |
| "Compare X across stores" | `keyword` plus several `marketplaces` |
| Food delivery catalogs | `keywordDelivery` plus `marketplacesDelivery` |

Always send `maxProductResults` and `additionalProperties: true`. Without the second, stock and rating are missing entirely, because they are nested there.

## The call is two steps, sometimes three

1. Call `apify--e-commerce-scraping-tool` (two hyphens, not a slash). It returns run metadata and a `datasetId`. **It does not return products.**
2. **Check `status`.** If it is not `SUCCEEDED`, call `get-actor-run` with the `runId` and a `waitSecs` until it is. The Actor tool returns when its own wait window elapses, not when the run finishes, so `RUNNING` is normal and the dataset holds nothing at that point.
3. Call `get-dataset-items` with the `datasetId`, a `limit`, and `fields` (see below).

Two failures live here. Stopping after step 1 returns a result that reads like success and holds no product data. Skipping step 2 fetches an empty dataset and reports the product as not found.

## Always project with fields

The full record is large: one Amazon product measured about 88 KB across 142 fields, most of it marketing content and review text. Fetching all of it spends context on data no answer needs.

Pass `fields` in dot notation, naming only what the question needs:

```
name,url,offers.price,offers.priceCurrency,brand.slogan,reviewCount,
additionalProperties.inStock,additionalProperties.inStockText,
additionalProperties.stars,additionalProperties.listPrice.value
```

**Projected output is flattened.** Keys come back as literal dotted strings, so it is `item["offers.price"]`, not `item["offers"]["price"]`. The nesting in `references/fields.md` describes unprojected output. Reading a nested path against a projected response finds nothing and looks exactly like missing data.

## Read the fields defensively

Field names, types, and nesting vary by retailer. See `references/fields.md` for the full map. The four that bite hardest:

- **`offers.price`** is a number on some retailers and a string like `"398.99"` on others. Parse both.
- **Stock and rating live under `additionalProperties`**, as `inStock` and `stars`, not at the top level. The top-level `rating` was `null` on a product whose `stars` was `4.2`.
- **`brand`** may be `{"slogan": "Visit the Sony Store"}`. That is UI text, not a brand. Strip the wrapper or omit the brand.
- **`offers.priceCurrency`** is a symbol (`"$"`) on some retailers and an ISO code (`"USD"`) on others. A symbol butts against the number, a code takes a space.

## Answer honestly

**Say when the data was read.** "As of just now" or the timestamp. The whole point of calling the tool is that the answer is current, so make that visible.

**Never claim a product is unavailable because stock was absent.** Many retailers do not report it. Absent means unknown, so say "the retailer does not report stock" rather than "out of stock".

**If every field comes back empty, suspect the URL before the retailer.** The Actor returns an item with no fields rather than an error, and the most common cause is a URL that does not resolve. Do not report it as a product with no price, and do not conclude the retailer is unsupported until the URL has been checked.

**Quote the source URL** so the user can check, and include the image URL when they asked to see the item.

## Falling back to Apify Store

Only when this tool has genuinely failed on a good URL, and generic extraction did not
produce a name or a price.

Search Apify Store for an Actor covering that retailer, run it, and answer from its
output. Two things to carry into that:

- **The output shape will not match.** The field map in `references/fields.md` describes
  this Actor. Another Actor has its own schema, so read what it actually returns rather
  than assuming `offers.price` exists.
- **Say which source answered.** If the reply came from a different Actor, the freshness
  and coverage caveats are that Actor's, not this one's.

If the connection is scoped with `?tools=`, Store search is not available on it. Report
that the retailer is not covered rather than pretending to search.

## Cost

The Actor bills a start event per call plus per product returned, so:

- Cap with `maxProductResults`. Five is plenty for a comparison; one for a single lookup.
- Prefer one call with several URLs or marketplaces over several calls.
- Do not re-run to "check" a result you already have.

## Gotchas

- Stopping after the first tool call returns run metadata that reads like success and contains no products.
- A `RUNNING` status is not an error and not a reason to retry the Actor. Poll `get-actor-run`; starting a second run doubles the cost and answers no faster.
- Projecting with `fields` flattens the response into dotted keys. Reading the nested path then finds nothing, which is indistinguishable from the retailer not reporting the field.
- Timing is not stable. The same Amazon URL returned in 10 seconds on one call and 40 on the next, and other retailers are slower still. Treat any single measurement as a sample, warn the user before a multi-retailer comparison, and never read slowness as failure.
- A validation error naming `marketplaces` means the enum is truncated on this connection, not that the retailer is unsupported. Use `detailsUrls` with the product URL instead.
- A retailer missing from `marketplaces` is not a reason to skip the call. Generic extraction is on by default, so unlisted shops frequently work. The listed ones have dedicated extractors and deeper field coverage.
- Omitting `additionalProperties: true` silently drops stock, rating, list price, and identifiers.
- `rating: 0` and `stars: 0` mean absent, not a zero-star product.
- A `listPrice` above the current price is a genuine discount; report the percentage, it is usually what the user wanted.
- `additionalProperties` can run to roughly 100 KB per product. Never paste it into a reply; read the fields you need.
- The `?tools=` parameter on the server URL narrows which Actors are visible. If the tool is absent, the connection may be scoped to other Actors.
