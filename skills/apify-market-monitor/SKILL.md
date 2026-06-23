---
name: apify-market-monitor
description: Monitor competitors, markets, prices, listings, creators, and hiring over time across TikTok, Instagram, YouTube, Reddit, Amazon, Airbnb, Booking.com, Zillow, LinkedIn, Indeed, and Google Maps. Where the Actor supports it, runs are compared against prior runs to surface what changed since you last looked (price and rank moves, new breakouts, supply and rate shifts, hiring momentum, rating trajectory) instead of re-dumping raw rows. Use when the user wants to watch a competitor, track a market or price trajectory, detect breakout content or trending sounds, follow hiring signals, monitor review reputation, or get a recurring "what changed" feed from any of these platforms.
author: apifyforge
author_url: https://github.com/apifyforge
license: MIT
metadata:
  version: "1.0"
---

# Market Monitor — track competitors and markets over time

Route a monitoring or market-intelligence question to the right Actor, run it, and deliver what changed rather than a raw data dump.

This skill is organized around one task, not a list of platforms: monitoring change over time. Every Actor in the table can be used for recurring observation of a market, competitor set, creator ecosystem, hiring landscape, or pricing environment. Where the Actor supports it (a stable watchlist name, or a `monitor` mode where offered), the next run compares against the prior run and surfaces the deltas — new breakouts, price and rank moves, supply and rate shifts, hiring momentum, rating shifts — instead of re-dumping rows. That memory cannot be backfilled, so the value compounds on a schedule.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)
- These Actors render real pages and default to Apify **residential** proxies, which cost more than datacenter. Confirm scope before a large run (see [references/gotchas.md](references/gotchas.md)).

## Workflow

1. Detect the platform and intent, pick the Actor from the routing table below.
2. Fetch the Actor's input schema so you build a valid input (modes and field names differ per Actor):
   `apify actors info "ACTOR_ID" --input --json --user-agent apify-awesome-skills/apify-market-monitor 2>/dev/null`
3. Decide one-shot vs monitoring. For a recurring feed, set a stable `watchlistName` (or `mode: "monitor"` where offered) and tell the user the first run establishes the baseline; deltas appear from run 2 onward.
4. Confirm result limits and estimated cost with the user before a large run.
5. Run the Actor, fetch the dataset, and deliver the change briefing first, raw rows only if asked.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| TikTok breakouts, creator momentum, trending sounds | `ryanclinton/tiktok-scraper` | community | What is breaking out under a hashtag, which creators are heating up, who rode a sound earliest |
| Instagram creator / influencer momentum, engagement quality | `ryanclinton/instagram-scraper` | community | Creator vetting, engagement authenticity, brand-fit, follower and engagement trajectory |
| YouTube video and channel breakout detection | `ryanclinton/youtube-scraper` | community | Attention queue, breakout detection, channel watchlist deltas |
| YouTube sponsor / creator qualification | `ryanclinton/youtube-sponsorship-intelligence` | community | Whether a channel is sponsor-worthy, sponsor and creator fit signals |
| Reddit brand-mention tracking, sentiment, topic surge | `ryanclinton/reddit-scraper` | community | Brand-mention monitoring, sentiment, topic surge, subreddit watch |
| Amazon price / BSR / buybox / defect monitoring | `ryanclinton/amazon-product-scraper` | community | Track ASINs over time, price and rank trajectory, seller-change and defect-emergence incidents |
| Airbnb market pricing, revenue and supply | `ryanclinton/airbnb-scraper` | community | Comp-set price position, fenced revenue and occupancy estimate, supply-surge, market monitor |
| Booking.com hotel rate and demand | `ryanclinton/booking-scraper` | community | Rate-value position, comp-set, rate-drop and demand-pressure signals, saved rate-by-date memory |
| Zillow property deal, price-cut and market signals | `ryanclinton/zillow-scraper` | community | Deal score, comp position, price-cut and motivated-seller radar, kept price history |
| LinkedIn hiring momentum, ghost-job detection | `ryanclinton/linkedin-jobs-scraper` | community | Hiring momentum, skill demand, ghost-job detection, dedup, hiring trajectory |
| Indeed hiring intelligence | `ryanclinton/indeed-hiring-intelligence` | community | Hiring-momentum signals with a trust layer over raw Indeed job rows |
| Google Maps review reputation and trajectory | `ryanclinton/google-maps-reviews-scraper` | community | Coverage-integrity reviews, sentiment and theme synthesis, rating trajectory, response priority |
| Google Maps local market and competitor intelligence | `ryanclinton/google-maps-scraper` | community | Saturation and service-gap mapping, competitor momentum, new-entrant and closure detection |

`Tier` = `apify` (Apify-maintained) or `community` (third-party developer). Every Actor in this table is a `community` Actor published by the skill author.

## The monitoring pattern (the differentiator)

These Actors are built to run on a schedule. Where the Actor's schema exposes a `watchlistName` or a `monitor` mode (confirm in step 2), use it:

1. First run: pass a stable `watchlistName` (and `mode: "monitor"` where the schema offers it). This establishes a baseline and returns today's signals.
2. Schedule the same input on a daily or weekly Apify schedule.
3. From run 2 onward, a monitoring-capable Actor returns a change briefing first: what is new, what moved, what went quiet. Trajectory and anomaly reads unlock after a few runs; they cannot be backfilled.

Tell the user this explicitly. A single run is a snapshot; the product is the feed. If an Actor does not expose a watchlist or monitor mode, run it on a schedule and diff the datasets yourself.

## Calling Actors — choose your interface

### Option A: Apify CLI (recommended for portability)

Three flags on every call: `--json` (stable output), `--user-agent apify-awesome-skills/apify-market-monitor` (attribution), `2>/dev/null` (suppress progress noise that breaks JSON).

The example inputs below are illustrative. Field names and modes vary by Actor and can change between versions, so always inspect the Actor's input schema (workflow step 2) before building input rather than copying these verbatim.

Worked example — what is breaking out under a TikTok hashtag, kept as a daily feed:

```
apify actors call "ryanclinton/tiktok-scraper" \
  -i '{"mode":"hashtag","hashtags":["skincare"],"rankBy":"breakoutPotential","watchlistName":"skincare-daily"}' \
  --json \
  --user-agent apify-awesome-skills/apify-market-monitor \
  2>/dev/null
```

Worked example — monitor a set of Amazon ASINs for price, rank and defect changes:

```
apify actors call "ryanclinton/amazon-product-scraper" \
  -i '{"mode":"monitor","track":["B09X7MPX8L"],"marketplaces":["amazon.com"],"watchlistName":"my-catalog"}' \
  --json \
  --user-agent apify-awesome-skills/apify-market-monitor \
  2>/dev/null
```

Worked example — rank an Airbnb market by pricing opportunity and track it over time:

```
apify actors call "ryanclinton/airbnb-scraper" \
  -i '{"mode":"monitor","market":"Austin, TX","rankBy":"pricingOpportunity","watchlistName":"austin-str"}' \
  --json \
  --user-agent apify-awesome-skills/apify-market-monitor \
  2>/dev/null
```

For every other Actor in the table, fetch its schema first (step 2 of the workflow) — modes and field names differ — then build the input the same way.

Other useful commands:

```
# Search the Store if no row fits the user's platform
apify actors search "KEYWORDS" --json --limit 10 --user-agent apify-awesome-skills/apify-market-monitor 2>/dev/null

# Fetch results (first peek)
apify datasets get-items DATASET_ID --limit 5 --format json --user-agent apify-awesome-skills/apify-market-monitor 2>/dev/null

# Full export to CSV
apify datasets get-items DATASET_ID --format csv --user-agent apify-awesome-skills/apify-market-monitor 2>/dev/null > output.csv
```

### Option B: Apify MCP connector

Hosted MCP server at <https://mcp.apify.com>. Documented at <https://docs.apify.com/platform/integrations/mcp>.

### Option C: MCP client of your choice

Standalone CLI client. See <https://github.com/apify/mcpc>.

## Do not use this skill when

- The user wants a one-off scrape with no monitoring or change-over-time need — a plain scraper is simpler.
- The user only needs a single URL or record extracted once.
- The user wants historical data from before the first watchlist run — the memory clock cannot be backfilled.
- A platform the user named is not in the routing table — search the Store or use a dedicated skill instead.

## Troubleshooting

- Auth failure → run `apify login` or set `APIFY_TOKEN`.
- A run returns a snapshot with no deltas → that is run 1 of a watchlist. Schedule it and re-run; deltas appear from run 2.
- Empty or wrong prices on Amazon / Airbnb / Booking → these Actors require residential proxies pinned to the right country; do not override the proxy default to datacenter.
- No row matches the platform the user named → search the Store (command above) and pick the closest Apify-maintained Actor, or tell the user this skill does not cover that platform.
- For cost guardrails and the memory-clock caveat, see [references/gotchas.md](references/gotchas.md).
