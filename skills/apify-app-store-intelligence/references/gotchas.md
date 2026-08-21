# Gotchas — apify-app-store-intelligence

The failure modes here mostly do not throw. They return a confident, well-formed, wrong answer.

## Identity: four things users call "the app"

| What the user pastes | What it is | Use it? |
|---|---|---|
| `https://apps.apple.com/us/app/foo/id284882215` | Store URL — the ID is the `id…` segment | Yes, extract `284882215` |
| `284882215` | numeric track ID | Yes — exact, cheapest lookup |
| `com.spotify.client` | bundle ID | Yes — exact |
| `"Spotify"` | a search term | **Last resort.** Search returns ranked guesses, and the top hit is not always the app meant. Confirm the resolved name and developer with the user before scraping anything expensive off it. |

Resolving a search term to an ID once, then reusing the ID, is both cheaper and reproducible.
A pipeline keyed on a search term silently re-points itself when store ranking shifts.

## Storefronts: price and availability are per-country

There are ~175 storefronts and the same app has different prices, different availability, and
sometimes a different name in each. Two consequences:

- **Never report a price without naming the storefront it came from.** "It costs $4.99" is not a
  fact; "it costs $4.99 on the US store" is.
- **An app can be absent from a storefront entirely.** An empty result for `country: "jp"` means
  "not sold in Japan", not "the run failed". Do not retry it as an error.

Ratings are also per-storefront. A worldwide average is not something any of these Actors return;
if the user wants one, you have to sweep countries and say so.

## Change detection: what "changed" means

`changesOnly: true` compares this run against the **previous run's stored snapshot**. Therefore:

- **The first run emits nothing in `changesOnly` mode** — there is no previous snapshot to diff
  against. Run once without it to establish a baseline, then schedule with it. A first scheduled
  run that returns 0 rows is working correctly; reporting that as "no changes detected" is wrong,
  it is "no baseline yet".
- `watchFields` defaults to `["price","rating","version"]`. Fields outside that list change
  without triggering a row. If the user cares about `ratingsCount` (which moves constantly), add
  it deliberately — it will make almost every app report as changed every run.
- A gap in the schedule means the diff spans the gap. "Changed since yesterday" is really
  "changed since the last successful run", and those differ after an outage.

## Cost: the metadata/reviews split is ~1000×

One metadata row per app versus thousands of review rows per app. Before a reviews run over more
than a handful of apps, state the expected item count and confirm. The specific trap: a user asks
to "monitor competitors", an agent routes to a reviews scraper, and a daily schedule re-pulls the
entire review corpus of ten apps every morning.

Always cap reviews runs with the Actor's own limit field (`maxItems` on
`thewolves/appstore-reviews-scraper`) rather than relying on the default.

## Rate limits and upstream behaviour

The metadata Actors here read Apple's public lookup/search API, which is keyless but not
unlimited. Symptoms of being throttled are empty results and slow responses rather than an
explicit 429, so **an empty result set is ambiguous** — it can mean "no such app", "not in this
storefront", or "we are being throttled". If a lookup that previously returned rows starts
returning none, treat it as inconclusive and re-probe with a single known-good App ID
(`284882215`, Facebook, present in every storefront) before concluding the app is gone.

Lower `maxConcurrency` before assuming a wide sweep is broken.

## Reporting

Give the user the row count and the dataset link on every run. A run that "succeeded" with zero
rows and no explanation is the most common way this category wastes someone's afternoon.
