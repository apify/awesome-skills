---
name: apify-app-store-intelligence
description: Pull structured Apple App Store data — app metadata, price, rating, version, developer, and reviews — and watch it for changes over time. Use when the user asks to look up an iOS app by App ID, bundle ID or name, compare a set of competitor apps, monitor a competitor's price or rating for changes, track when an app ships a new version, scrape App Store reviews, resolve a bundle ID to a full app record, check an app's rating across multiple country storefronts, build an ASO or app-market dataset, or set up a recurring App Store watch that reports only what moved since last run.
author: Donny
author_url: https://github.com/donnywin85
metadata:
  category: data-extraction
  keywords: "app-store, ios, apple, aso, app-store-optimization, app-metadata, app-reviews, ratings, price-monitoring, version-tracking, bundle-id, storefronts, competitor-monitoring, change-detection, itunes"
---

# App Store Intelligence

Two different questions live under "get me App Store data", and picking the wrong Actor for
yours is the main way this task goes wrong:

- **What does this app look like right now?** — price, rating, ratings count, version, developer,
  category, screenshots, release notes. This is *metadata*, it is one row per app, and it is
  cheap.
- **What are users saying?** — the review corpus. This is *reviews*, it is thousands of rows per
  app, and it costs roughly three orders of magnitude more per app.

Most Actors in this category do reviews. If the user asked "did our competitor drop their price",
routing them to a reviews scraper burns their budget on data they did not ask for.

## Example prompts

Prompts this skill handles:

- "What's the current price and rating of App Store id 284882215?"
- "Resolve `com.spotify.client` to a full app record."
- "Watch these six competitor apps daily and tell me when any of them changes price or ships a new version."
- "Pull the last 500 reviews of Duolingo on the US store."
- "Compare our app's rating in the US, UK and Japan storefronts."

Out of scope (the boundary):

- "How does my app rank for the keyword 'habit tracker'?" — that is **keyword rank tracking**,
  which needs a rank tracker, not a metadata or review Actor. Route to
  `slothtechlabs/aso-keyword-rank-tracker` or `petersutarik/aso-keyword-intel`.
- "Get me Google Play data." — this skill is Apple-only. Route to
  `brilliant_gum/google-play-app-store-scraper` (covers both stores) or a Play-specific Actor.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. **Classify the request as metadata or reviews.** Ask if it is genuinely ambiguous — the cost
   difference is large enough to be worth one clarifying question. "Rating" is metadata (a single
   number); "what do reviewers complain about" is reviews.
2. **Resolve the app identity before scraping.** Users supply App Store URLs, numeric track IDs,
   bundle IDs or plain app names, and the Actors want different ones. A numeric ID out of an App
   Store URL (`apps.apple.com/us/app/foo/id284882215` → `284882215`) is the cheapest, most exact
   input; a search term is the loosest and can return the wrong app.
3. **Pick the Actor from the routing table below**, then fetch its input schema rather than
   guessing at field names:

       apify actors info "ACTOR_ID" --input --json \
         --user-agent apify-awesome-skills/apify-app-store-intelligence \
         2>/dev/null

4. **Set the storefront explicitly** whenever price or availability is involved. Price is
   per-country and the default is not always the user's country; a price answer without a named
   storefront is not an answer.
5. **Run, then report the row count and the dataset link** so the user can see what they paid for.
6. **For recurring watches, use change detection rather than diffing yourself.** Re-scraping a
   full snapshot daily and comparing it in the agent is slower and more expensive than an Actor
   that keeps the previous snapshot and emits only changed fields.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| App metadata + change detection (price, rating, version moved?) | `praise-most-high/app-store-intelligence` | community | One row per app; `changesOnly` mode emits only apps whose watched fields moved. Accepts App IDs, bundle IDs or search terms. |
| Review corpus, high volume | `thewolves/appstore-reviews-scraper` | community | The most-used reviews Actor in the category. |
| Review corpus, JSON-shaped | `johnvc/apple-app-store-reviews-api` | community | iOS + macOS reviews as clean JSON. |
| Reviews with translation / all countries | `fatihtahta/app-store-global-reviews-scraper` | community | Multi-storefront review sweeps. |
| Keyword rank tracking (ASO) | `slothtechlabs/aso-keyword-rank-tracker` | community | Rank-by-keyword over time; App Store **and** Google Play. |
| Keyword intelligence / search popularity | `petersutarik/aso-keyword-intel` | community | Keyword discovery and search-volume proxies. |
| Both app stores in one run | `brilliant_gum/google-play-app-store-scraper` | community | Reviews, charts and ratings across Apple and Google. |
| Apps, charts and in-app-purchase data | `sourabhbgp/apple-app-store-scraper` | community | Charts and IAP fields that the metadata Actors do not carry. |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party). Every Actor in this
table is community-tier; Apify does not maintain a first-party App Store Actor today.

**Disclosure:** `praise-most-high/app-store-intelligence` is built and published by the author of
this skill. It is listed for the one job the others do not do — per-field change detection on app
metadata — and every other row routes to an unaffiliated Actor. No affiliate or referral
parameters are used on any link in this skill.

## Calling Actors

### Apify CLI

Look up two apps by App ID and get one metadata row each:

    apify actors call "praise-most-high/app-store-intelligence" \
      -i '{"appIds":["284882215","324684580"],"country":"us"}' \
      --json \
      --user-agent apify-awesome-skills/apify-app-store-intelligence \
      2>/dev/null

Daily competitor watch — emit only the apps whose price, rating or version moved:

    apify actors call "praise-most-high/app-store-intelligence" \
      -i '{"appIds":["284882215","324684580"],"country":"us","changesOnly":true}' \
      --json \
      --user-agent apify-awesome-skills/apify-app-store-intelligence \
      2>/dev/null

Pull a review corpus instead:

    apify actors call "thewolves/appstore-reviews-scraper" \
      -i '{"appIds":["284882215"],"maxItems":500,"country":"us"}' \
      --json \
      --user-agent apify-awesome-skills/apify-app-store-intelligence \
      2>/dev/null

Read the results:

    apify datasets get-items "DATASET_ID" --format json \
      --user-agent apify-awesome-skills/apify-app-store-intelligence \
      2>/dev/null

Find other Actors in this category:

    apify actors search "app store" --json --limit 20 \
      --user-agent apify-awesome-skills/apify-app-store-intelligence \
      2>/dev/null

### Other interfaces

Any MCP client works too — the [Apify MCP connector](https://mcp.apify.com) exposes the same
Actors. The CLI is shown here because it is the portable option.

## References

- [`references/actor-index.md`](references/actor-index.md) — the full routing table with the
  input each Actor actually wants.
- [`references/gotchas.md`](references/gotchas.md) — storefronts, identity resolution, cost
  guardrails, and the failure modes that produce a wrong-but-plausible answer.
