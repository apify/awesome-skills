# Field map for E-commerce Scraping Tool output

Every shape below was observed in live runs against Amazon, Walmart, and eBay, not
inferred from documentation. Where they disagree, every form is listed, because a reader
that handles only one breaks on the next retailer.

## Contents

- [Top level](#top-level)
- [Inside additionalProperties](#inside-additionalproperties)
- [Per-retailer differences](#per-retailer-differences)
- [Reading each field safely](#reading-each-field-safely)
- [Projecting with fields flattens all of this](#projecting-with-fields-flattens-all-of-this)

## Top level

| Field | Type seen | Notes |
|---|---|---|
| `name` | string | Sometimes `title` instead. **eBay appends `Opens in a new window or tab` to every one**, see the gotcha below |
| `description` | string | Long, often over 1,000 characters |
| `url` | string | Canonical product URL |
| `inputUrl` | string | What was submitted, useful when `url` is absent |
| `image` | string or list | Single URL or a list |
| `offers` | object | Never an array in practice |
| `offers.price` | number or string | `248` on Amazon, `"398.99"` on Walmart, `45.95` on eBay |
| `offers.priceCurrency` | string | `"$"` on Amazon, `"USD"` on Walmart. **Absent on eBay** |
| `offers.currency` | string | `"USD"` on eBay. A different key for the same thing, so read both |
| `offers.availability` | string | schema.org URL on eBay, e.g. `https://schema.org/InStock`. Not present on Amazon |
| `brand` | object | Often only has `slogan`; see below |
| `rating` | number or null | Unreliable: `null` on a 4.2-star product, `0` on Walmart |
| `reviewCount` | number | Reliable on Amazon (20,002 observed) |
| `additionalProperties` | object | Where the useful fields actually live |

## Inside additionalProperties

Only present when the call sends `additionalProperties: true`.

The size of this object is per-retailer: **Amazon returned 44 keys, Walmart returned 4.**

Amazon, the keys worth reading:

| Key | Type | Example |
|---|---|---|
| `inStock` | bool | `true` |
| `inStockText` | string | `"In Stock  Only 15 left in stock - order soon."` |
| `stars` | float | `4.2`, the real rating |
| `listPrice` | object | `{"value": 399.99, "currency": "$"}` |
| `asin` | string | `"B09XS7JWHH"` |
| `delivery` | string | `"Saturday, August 22"` |
| `fastestDelivery` | string | Same shape |
| `breadCrumbs` | string | `"Electronics > Headphones..."` |
| `features` | list of strings | Bullet points from the listing |
| `highResolutionImages` | list of strings | Prefer these over `image` |
| `galleryThumbnails` | list of strings | Lower resolution |
| `variantDetails` | list of objects | Each has a `name` |
| `bestsellerRanks` | list of objects | `rank` and `category` |
| `starsBreakdown` | object | Share per star level |
| `aiReviewsSummary` | object | Has a `text` field |
| `monthlyPurchaseVolume` | string | `"3K+ bought in past month"` |

Walmart returned only these four:

| Key | Type | Notes |
|---|---|---|
| `sku` | string | The identifier, since there is no `asin` |
| `currencyRaw` | string | `"$"` |
| `images` | list of objects | `[{"url": ...}]`, not plain strings |
| `descriptionHtml` | string | HTML, not plain text |

Keys that were present on Amazon but held `null`: `condition`, `shippingPrice`,
`priceRange`, `returnPolicy`, `answeredQuestions`, `author`, `support`. Treat any of
these as absent rather than meaningful.

## Per-retailer differences

Measured on one run per retailer. The point of this table is not the specific counts, it
is that **coverage is a property of the retailer, not of the tool**, so an agent has to
handle a retailer that says less.

| | Amazon | Walmart | eBay |
|---|---|---|---|
| Price key | `offers.price` (number) | `offers.price` (string) | `offers.price` (number) |
| Currency key | `offers.priceCurrency`, a symbol | `offers.priceCurrency`, an ISO code | **`offers.currency`**, an ISO code |
| Stock | `additionalProperties.inStock` | not returned | `offers.availability` only |
| Rating | `additionalProperties.stars` | not returned | not returned |
| List price | `additionalProperties.listPrice.value` | not returned | not returned |
| `additionalProperties` keys | 44 | 4 | 4 |
| `brand` content | `{"slogan": "Sony"}` | `{"slogan": "Visit the Sony Store"}` | `{"slogan": null}` seen |
| Images | string lists | list of objects under extras | string lists, some 1x1 placeholders |
| Identifier | `asin` | `sku` | neither, use the item id in the URL |
| extras size | 44 keys, about 100 KB | 4 keys | 4 keys |
| Name needs cleaning | no | no | **yes**, link text appended |

On the run behind these numbers, eBay returned stock and rating on **none** of its 161
records, and Amazon returned both on **all 14** of its. Treat that as the shape of the
problem rather than as fixed ratios.

## Reading each field safely

**Name**: `name` or `title`, then strip a trailing `Opens in a new window or tab`. Strip
it as a suffix only, so a product whose name genuinely contains the phrase survives.

**Price**: read `offers.price`. If it is a string, strip everything except digits and
dots. Guard against a stray thousands separator leaving two dots. Reject zero and
negatives. In Python, note that `True` is an `int`, so check for `bool` first.

**Currency**: `offers.priceCurrency`, then `offers.currency`, then
`additionalProperties.currencyRaw`. If the value is alphabetic it is a code and takes
a space before the amount; otherwise it is a symbol and butts against it.

**Brand**: `brand.name`, then `brand.slogan`. Unwrap a `Visit the X Store` pattern to
`X`. Then reject anything longer than about 40 characters or more than four words,
because the slot carries free marketing text and a phrase presented as a brand reads
as fact.

**Stock**: `inStock` at top level, then `additionalProperties.inStock`, then parse
`offers.availability` or `availability` for in-stock and out-of-stock wording. Keep
three states: true, false, and unknown. Never map unknown to false.

**Rating**: `additionalProperties.stars` first, then top-level `rating`. Treat zero as
absent.

**Images**: `additionalProperties.highResolutionImages`, then `image`, then `images`,
then `additionalProperties.images`, then `galleryThumbnails`. Entries may be strings
or objects with a `url`. Deduplicate and drop anything not starting with `http`.

**Identifier**: `gtin`, then `sku`, then `additionalProperties.sku`, then
`additionalProperties.asin`.

**Discount**: compare `offers.price` against `additionalProperties.listPrice.value`.
Report a percentage only when the current price is genuinely lower.

### Gotcha

**eBay appends link text to every product name.** Raw, the name reads
`Saucony Women Cohesion 18Opens in a new window or tab`. That is scraped UI furniture, the
same class of problem as `brand.slogan` carrying `Visit the Sony Store`, and left in it
lands in a product card or a cited document as though it were the product's name.
[`read_name()`](https://github.com/luispintoapify/ecommerce-agent-starter/blob/main/apify_products.py) strips it, and only as a
suffix, so a product whose name genuinely contains the phrase survives.

An unresolvable URL returns an item with every field empty rather than an error, and
`brand` may still be present as `{"slogan": null}`. Treat an item with neither a name
nor a price as "page not read", not as a product without a price.

Note what that empty item does **not** tell you. It is not evidence the retailer is
unsupported: generic extraction is enabled by default, so sites absent from the
`marketplaces` list are routinely readable. A bad URL and an uncovered retailer produce
the same empty item, and the URL is the likelier of the two.

## Projecting with fields flattens all of this

Everything above describes the **unprojected** record: nested objects, read with
`item["offers"]["price"]`.

The full record is big. One Amazon product measured about 88 KB across 142 fields, most
of it marketing copy and review text, and the MCP server warns that fetching all of it
may exceed the context window. So `get-dataset-items` takes a `fields` parameter, and
you should almost always pass it:

```
name,url,offers.price,offers.priceCurrency,brand.slogan,reviewCount,
additionalProperties.inStock,additionalProperties.inStockText,
additionalProperties.stars,additionalProperties.listPrice.value
```

**The response comes back flat.** The dots stay in the key names rather than becoming
nesting:

```json
{
  "name": "Sony WH-1000XM5...",
  "offers.price": 248,
  "brand.slogan": "Sony",
  "additionalProperties.inStock": true
}
```

Two consequences:

- An agent reading a projected response uses `item["offers.price"]`. Walking the nested
  path finds nothing, which is indistinguishable from the retailer not reporting the
  field, so the agent says "no price available" about a product whose price it fetched.
- Code written against the nested shape, including `normalize()` in this repo, needs the
  unprojected response. Fetch without `fields` when a normalizer will read the output,
  and cap the row count instead.

Pick one and be consistent: `fields` for an agent answering a question in a chat turn,
no `fields` for a pipeline that normalizes and stores.
