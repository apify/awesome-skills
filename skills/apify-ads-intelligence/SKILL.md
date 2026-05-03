---
name: apify-ads-intelligence
description: Research, spy on, and analyze ads across Meta (Facebook & Instagram), Google (Ads Transparency Center + paid search results), TikTok (Ads Library + Creative Center), LinkedIn Ad Library, and X (Twitter — promoted tweets, best-effort) using Apify Actors. Use when user asks about competitor ads, ad library research, winning creatives, ad copy analysis, landing page audits from ads, cross-platform ad audits, brand transparency checks, or any task involving paid ad creatives, advertiser data, or ad targeting from public ad libraries.
---

# Ads Intelligence Cluster

Answer natural language questions about ads, ad libraries, and competitor advertising activity by routing to the right Apify Actor and delivering a synthesized answer.

## Note on platform coverage

- **Meta, Google, TikTok, LinkedIn**: real public ad libraries with rich data (creatives, targeting, dates, reach where disclosed).
- **X (Twitter)**: no public ad library exists. Coverage is a **best-effort workaround** that scrapes a brand's tweets and flags items with non-empty `card` field or `source` containing "Ads" as likely promoted. Always include the caveat in synthesis output.

## Note on overlap with `apify-ecommerce`

That skill has an `ads-intelligence` intent that routes to `apify/facebook-ads-scraper` for shallow Meta-ad lookups. This skill is the deep dive across all five platforms. If you only need Meta ads as a side detail of an ecommerce question, stay in `apify-ecommerce`. If ads are the main task, use this skill.

## Prerequisites

(No need to check it upfront)

- `.env` file with `APIFY_TOKEN`
- Node.js 20.6+ (for native `--env-file` support)
- `mcpc` CLI tool: `npm install -g @apify/mcpc`

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Step 1: Detect intent and select Actor(s)
- [ ] Step 2: Fetch Actor schema via mcpc
- [ ] Step 3: Ask user preferences (output format, result count, country)
- [ ] Step 4: Run the Actor (or Actors in parallel for cross-platform-audit)
- [ ] Step 5: Synthesize a direct answer (not a data dump)
```

### Step 1: Detect Intent and Select Actor

Classify the user's message into an intent, then pick the right Actor.

**Intent signals:**

| Signals in user message | Intent |
|-------------------------|--------|
| "what ads is X running", "competitor [brand] ads", "[brand] FB/Google/TikTok/LinkedIn/X/Twitter ads", "show ads from [page]", "promoted tweets from [brand]" | `competitor-ads` |
| "ads about [topic]", "find [keyword] ads", "ads for [vertical]", "fitness/fintech/saas ads" | `keyword-ads` |
| "trending ads", "winning ads", "top ads", "best performing", "long-running ads", "creative inspiration" | `top-creatives` |
| "where do these ads go", "landing pages from ads", "click destinations", "ad funnels" | `landing-page-audit` |
| "compare X's ads across platforms", "all ads from [brand]", "cross-platform ad audit" | `cross-platform-audit` |

If multiple intents detected, ask: *"Do you want [intent A] or [intent B]?"*

**Actor routing — always try Primary first, switch to Fallback only if it fails or returns 0 results:**

| Intent | Platform | Primary Actor | Fallback Actor |
|--------|----------|---------------|----------------|
| `competitor-ads` | Meta (FB/IG) | `apify/facebook-ads-scraper` | `brilliant_gum/facebook-ads-library-scraper` |
| `competitor-ads` | Google | `dz_omar/google-ads-scraper` | `solidcode/ads-transparency-scraper` |
| `competitor-ads` | TikTok | `brilliant_gum/tiktok-ads-library-scraper` (`source: library`) | `silva95gustavo/tiktok-ads-scraper` |
| `competitor-ads` | LinkedIn | `silva95gustavo/linkedin-ad-library-scraper` | `dz_omar/linkedin-ads-scraper` |
| `competitor-ads` | X (workaround) | `apidojo/twitter-scraper-lite` (`twitterHandles: [<brand>]`) + heuristic filter | `apidojo/tweet-scraper` |
| `keyword-ads` | Meta | `brilliant_gum/facebook-ads-library-scraper` | `apify/facebook-ads-scraper` |
| `keyword-ads` | Google | `apify/google-search-scraper` (`focusOnPaidAds: true`) | — |
| `keyword-ads` | TikTok | `brilliant_gum/tiktok-ads-library-scraper` | — |
| `keyword-ads` | LinkedIn | `silva95gustavo/linkedin-ad-library-scraper` | — |
| `keyword-ads` | X (workaround) | `apidojo/twitter-scraper-lite` (`searchTerms: [<keyword>]`) + heuristic filter | `apidojo/tweet-scraper` |
| `top-creatives` | Meta | `brilliant_gum/facebook-ads-library-scraper` (rank by `daysRunning`) | — |
| `top-creatives` | TikTok | `burbn/tiktok-top-ads-spy` (sort by CTR / impressions / likes) | `brilliant_gum/tiktok-ads-library-scraper` (`source: creative_center`) |
| `top-creatives` | Google | n/a — fall back to `competitor-ads` route, filter to active ads | — |
| `top-creatives` | LinkedIn | n/a — fall back to `competitor-ads` route, rank by `impressionsPerCountry` reach | — |
| `top-creatives` | X | n/a in v1 — no reliable promoted-content signal across timelines | — |
| `landing-page-audit` | Meta | `brilliant_gum/facebook-ads-library-scraper` (`resolveSnapshotUrls: true`) | — |
| `landing-page-audit` | Google | `apify/google-search-scraper` (`focusOnPaidAds: true`, `directUrl`) | `dz_omar/google-ads-scraper` (`destinationUrl`) |
| `landing-page-audit` | X | n/a in v1 — heuristics not reliable enough for landing-page extraction | — |
| `cross-platform-audit` | All five | Run Meta + Google + TikTok + LinkedIn primaries in parallel; X workaround runs separately with caveat. Merge by advertiser. | — |

**X (Twitter) heuristic filter** — after scraping, flag a tweet as *likely promoted* if any of the following hold:

- `card` field is non-empty (website cards / CTAs are commonly attached to promoted tweets)
- `source` field contains "Ads" (e.g. "Twitter Ads")

Surface results with the explicit caveat: *"X has no public ad library; results below are tweets from the brand's own timeline that match promoted-content heuristics. They will miss promoted-only ads that appear in other users' feeds."*

### Step 2: Fetch Actor Schema

Fetch the Actor's input schema dynamically using mcpc:

```bash
export $(grep APIFY_TOKEN .env | xargs) && mcpc --json mcp.apify.com --header "Authorization: Bearer $APIFY_TOKEN" tools-call fetch-actor-details actor:="ACTOR_ID" | jq -r ".content"
```

Replace `ACTOR_ID` with the selected Actor (e.g., `apify/facebook-ads-scraper`).

This returns:

- Actor description and README
- Required and optional input parameters
- Output fields (if available)

### Step 3: Ask User Preferences

Before running, ask:

1. **Output format**:
   - **Quick answer** (default) — synthesized answer in chat, no file saved
   - **CSV** — full export saved to disk
   - **JSON** — full export saved to disk
2. **Result count** — defaults by intent:

   | Intent | Default count |
   |--------|---------------|
   | `competitor-ads` | 30 |
   | `keyword-ads` | 30 |
   | `top-creatives` | 20 |
   | `landing-page-audit` | 50 |
   | `cross-platform-audit` | 15 per platform |

3. **Country** — default `US`. For TikTok library specifically, default `DE` (EU-only) and warn the user; for global TikTok use `source: creative_center`. X routes are global by handle/keyword, no country parameter.

### Step 4: Run the Actor

**Quick answer (display in chat, no file):**

```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "ACTOR_ID" \
  --input 'JSON_INPUT'
```

**CSV:**

```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "ACTOR_ID" \
  --input 'JSON_INPUT' \
  --output YYYY-MM-DD_filename.csv \
  --format csv
```

**JSON:**

```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "ACTOR_ID" \
  --input 'JSON_INPUT' \
  --output YYYY-MM-DD_filename.json \
  --format json
```

For `cross-platform-audit`, run multiple Actors in parallel by backgrounding each `node ...` invocation with `&` and calling `wait` before merging the JSON outputs by advertiser.

### Step 5: Analyze Results and Deliver Answer

Synthesize, don't dump. Patterns by intent:

| Intent | What the synthesis surfaces |
|--------|------------------------------|
| `competitor-ads` | Total ads found, active vs inactive split, top creative formats, top 5 ad copy snippets, list of unique landing-page domains. For X specifically: total tweets scraped, count flagged as likely-promoted, top 5 flagged tweets with the heuristic-detection caveat. |
| `keyword-ads` | Top 5 advertisers running ads on this keyword, total ads, country split |
| `top-creatives` | Top 5 by `daysRunning` (Meta) or CTR (TikTok), with creative summary, link to Ad Library entry |
| `landing-page-audit` | List of unique landing URLs, grouped by domain, with ad counts pointing at each |
| `cross-platform-audit` | Per-platform ad count and tone summary, then a "where they're spending most" inference |

**Suggested follow-ups** — keyed off the intent that just ran:

| If user just ran… | Suggest next |
|-------------------|--------------|
| `competitor-ads` (Meta) | Stack with `apify-competitor-intelligence` to add their FB Page posts, IG profile, and Google Maps reviews |
| `landing-page-audit` (any) | Stack with `apify-ecommerce` (`tech-stack` intent) to detect the platform behind the landing pages, or with `apify-lead-generation` to enrich destination domains with contact info |
| `top-creatives` (TikTok / Meta) | Stack with `apify-influencer-discovery` if any creatives are influencer collabs |
| `keyword-ads` (Google / Meta) | Stack with `apify-trend-analysis` to see whether the keyword is rising or falling on Google Trends / Instagram / TikTok |
| `cross-platform-audit` | Stack with `apify-content-analytics` for the brand's organic content side; combined paid + organic picture |

## Quirks

- **TikTok keyword search is loose.** Searching "Nike" can return ads from unrelated advertisers (Interactive Brokers, Shopify in our test). Always post-filter by `advertiserName` matching the user's intended brand; warn the user if zero matches after filter.
- **TikTok Ads Library is EU/EEA/UK only.** The `library` source needs an EU country code (DE / FR / IT / ES / NL / PL / SE etc.). For US/global coverage, switch to `creative_center` source — different fields (CTR, impression ranges, no targeting data).
- **`dz_omar/google-ads-scraper` requires `resultsPerQuery >= 10`.** Smaller values fail validation. Always set 10+ even for small intents.
- **`apify/facebook-ads-scraper` takes URLs, not keywords.** For `competitor-ads`: build `https://www.facebook.com/<PageName>` from the brand name. For `keyword-ads`: build a Meta Ad Library URL with `q=<keyword>&country=<XX>`.
- **`apify/google-search-scraper` paid-ads mode** has a built-in retry (up to 3) when no paid results are found — sometimes a query genuinely has no paid results. Treat empty `paidResults` as a valid answer, not an error.
- **LinkedIn Ad Library URL construction:** company URL `https://www.linkedin.com/company/<slug>/` is allowed but slow and ignores filters. For `competitor-ads` use `https://www.linkedin.com/ad-library/search?accountOwner=<slug>&countries=<XX>`. For `keyword-ads` use `?keyword=<term>&countries=<XX>`.
- **X has no public ad library.** Coverage is heuristic only. The route uses `apidojo/twitter-scraper-lite` to scrape a brand's own tweets (or keyword search results), then flags items with non-empty `card` field or `source` containing "Ads" as *likely* promoted. This will miss promoted-only tweets that never appear in the brand's own timeline.
- **X session sensitivity.** If the primary X Actor returns only `noResults` sentinels, switch to the fallback before declaring zero results.
- **Pricing.** Most primaries are FREE in our pricing tier; `apify/facebook-ads-scraper` charges per ad ($0.001 - $0.0058); X primaries charge per tweet (~$0.0004 / 1k). Default counts (30 / 20 / 50) keep cost negligible. Warn before runs of 500+ ads.

## Error Handling

```
APIFY_TOKEN not found       → ask user to create .env with APIFY_TOKEN=...
mcpc not found              → ask user: npm install -g @apify/mcpc
Actor not found             → check Actor ID against routing table
Run FAILED                  → check Apify console link in error output
Timeout                     → reduce result count or increase --timeout
0 results                   → switch to fallback Actor; if still 0, try a different country code
TikTok library: no EU ctry  → default to DE and warn user
Google Ads minimum: 10      → bump resultsPerQuery to 10
X scraper: noResults only   → switch to fallback X Actor
proxy is required           → add `"proxy": {"useApifyProxy": true}` to input
```
