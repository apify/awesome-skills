---
name: apify-financial-osint
description: Social-listening signals for tracked portfolio companies via Apify Actors — Reddit sentiment (fatihtahta), Twitter/X real-time mentions (kaitoeasyapi pay-per-result), Trustpilot service quality (getwally.net). Use when the user asks for sentiment, social media mentions, customer reviews, brand perception, crisis signals, OSINT, social listening, "what are people saying about X". Reads tracked companies from data/companies.json. Do NOT use for news (use apify-financial-news) or registry lookups (use apify-public-registries).
---

# Financial OSINT — Social Listening

Discover and quantify what the internet is saying about portfolio companies. Three verified Apify Actors only — Reddit (sentiment + threaded discussion), Twitter/X (real-time mentions, crisis monitoring), Trustpilot (customer satisfaction). All actors verified against real demo data with ≥98% success rate.

## Prerequisites

- Apify access — preferred: `apify` CLI (`npm install -g apify-cli && apify login`); fallback: Apify MCP connector (`call-actor` tool). CLI is faster and preferred when both are available.
- Companies data at `${CLAUDE_PLUGIN_ROOT}/data/companies.json` (read fields: `queries.reddit`, `queries.twitter`, `trustpilot_urls`, `identifiers.ticker`)
- Per-company routing pre-computed at `${CLAUDE_PLUGIN_ROOT}/skills/apify-financial-osint/data/osint-targets.json`

`${CLAUDE_PLUGIN_ROOT}` is the plugin's root directory (where `.claude-plugin/` lives). It is resolved automatically by Claude Code when the plugin is installed, or set to the `--plugin-dir` path during development.

## Workflow checklist

Copy this and tick boxes as you progress:

```
Task Progress:
- [ ] Step 0: Verify Apify access — try `apify --version && apify info`; if unavailable, check for `call-actor` MCP tool; if neither, tell user to install apify CLI or Apify MCP connector
- [ ] Step 1: Pick actor(s) by signal type — see "Choose Actor by Signal" table
- [ ] Step 2: Build input — read data/osint-targets.json or construct from data/companies.json
- [ ] Step 3: Run actor via apify CLI
- [ ] Step 4: Output — present top results with sentiment + engagement signals
```

## Constraints

### Allowed Apify Actors (exhaustive — do NOT use others)

| Actor | Purpose | Cost | Success rate |
|-------|---------|------|--------------|
| `fatihtahta/reddit-scraper-search-fast` | Reddit sentiment, acquisition reactions, brand perception | $1.49 / 1k results | 98.4% (40,787 runs/30d) |
| `kaitoeasyapi/twitter-x-data-tweet-scraper-pay-per-result-cheapest` | Real-time mentions, crisis monitoring, dealflow signals | $0.25 / 1k tweets | 99.7% (4.3/5, 58 reviews) |
| `getwally.net/trustpilot-reviews-scraper` | Service quality, complaint patterns (telcos, e-commerce, banks) | $3.00 / 1k results | verified working |

Do NOT use any other actor. Do NOT use WebSearch, WebFetch, or browser tools.

### Choose Actor by Signal

| If you need | Use Actor | When NOT to use |
|---|---|---|
| Sentiment / discussion threads / reactions to corporate events | `fatihtahta/reddit-scraper-search-fast` | If company has no consumer base (B2B fintech, biotech) — expect <5 posts |
| Real-time mentions / crisis signals / dealflow chatter | `kaitoeasyapi/twitter-x-data-tweet-scraper-pay-per-result-cheapest` | If you need >1 week historical depth — Twitter API limits |
| Customer satisfaction / service quality complaints | `getwally.net/trustpilot-reviews-scraper` | If company has no Trustpilot page (B2B, holding companies) — see verified URL list in `reference/osint-actor-schemas.md` Section 3 |

## Pipeline

### Step 1: Pick actor(s)

For portfolio companies, look up the company in [`data/osint-targets.json`](data/osint-targets.json) — it pre-computes which actors to run with templated inputs. Routing rule (mirrors how the file was built):

- `queries.reddit` non-empty → run Reddit actor
- `queries.twitter` non-empty → run Twitter actor (always set for tracked companies)
- `trustpilot_urls` non-empty → run Trustpilot actor

For ad-hoc / non-portfolio targets, construct input from scratch (see Step 2).

### Step 2: Build input

#### Reddit input (key fields)

| Field | Type | Default | Notes |
|---|---|---|---|
| `queries` | array of string | required (one of queries / urls / subredditName) | Global Reddit-wide search terms. |
| `maxPosts` | integer | **50000** (!) | **ALWAYS set explicitly** — typical 30-50 for scans, 100-200 for deep-dives. |
| `scrapeComments` | boolean | `false` | Set `true` to extract threaded discussion. |
| `maxComments` | integer | 50000 (!) | Only used when `scrapeComments: true`. Typical 5–10. |
| `sort` | enum | `"relevance"` | One of `relevance`, `hot`, `top`, `new`, `comments`. (NOT `rising` / `best`.) |
| `timeframe` | enum | `"all"` | One of `all`, `year`, `month`, `week`, `day`, `hour`. Must be >= dateFrom–dateTo range. |
| `dateFrom` | string | — | `YYYY-MM-DD`. Post-fetch filter: keep posts from this date onward. |
| `dateTo` | string | — | `YYYY-MM-DD`. Post-fetch filter: keep posts up to this date. |

Example:

```bash
apify call fatihtahta/reddit-scraper-search-fast \
  --input '{"queries":["InPost FedEx acquisition"],"maxPosts":50,"scrapeComments":true,"maxComments":10,"sort":"relevance","timeframe":"month"}'
```

#### Twitter/X input (key fields)

| Field | Type | Default | Notes |
|---|---|---|---|
| `twitterContent` | string | — | One of `twitterContent` / `tweetIDs` / `searchTerms`. Twitter advanced-search syntax (`OR`, `-`, `from:`, `since:`). |
| `tweetIDs` | array of string | — | **Plural** — not `tweetId`. |
| `searchTerms` | array of string | — | Each term gets `maxItems` results independently. |
| `maxItems` | integer | 200 | **REQUIRED** — actor fails without it. Pay-per-result. |
| `queryType` | enum | `"Latest"` | One of `Latest`, `Top`, `Photos`, `Videos`. |
| `lang` | string | `"en"` | ISO 639-1. Set `cs`/`pl`/`hu`/`bg`/`sk`/`tr` for single-country B2C; omit for multilingual. |
| `since` / `until` | string | — | Format: `YYYY-MM-DD_HH:MM:SS_UTC` (NOT ISO 8601). |
| `filter:news` / `filter:media` / `min_faves` / `min_retweets` | various | — | Engagement / content filters. |

Example:

```bash
apify call kaitoeasyapi/twitter-x-data-tweet-scraper-pay-per-result-cheapest \
  --input '{"twitterContent":"InPost FedEx acquisition OR INPST","maxItems":100,"queryType":"Latest","since":"2026-01-01_00:00:00_UTC","filter:news":true}'
```

#### Trustpilot input (only 2 fields exist!)

| Field | Type | Required | Notes |
|---|---|---|---|
| `startUrls` | array of `{"url": "..."}` objects | Yes | **NOT plain strings** — array of objects. |
| `limit` | integer | No (default 1000) | Set lower to control cost ($3/1k). |

Example:

```bash
apify call getwally.net/trustpilot-reviews-scraper \
  --input '{"startUrls":[{"url":"https://www.trustpilot.com/review/inpost.pl"}],"limit":50}'
```

Older docs reference fields like `maxItems`, `includeStatistics`, `includeCompanyDetails`, `onlyNewerThan` — these **do NOT exist** on this actor.

### Step 3: Cost-bound the run

Always cap output before running. Defaults are dangerously high.

| Actor | Cap field | Portfolio scan | Deep-dive |
|---|---|---|---|
| Reddit | `maxPosts` | 30–50 | 100–200 |
| Reddit comments | `maxComments` | 5–10 (only if `scrapeComments: true`) | 20–50 |
| Twitter/X | `maxItems` | 50–100 | 200–500 |
| Trustpilot | `limit` | 30–50 | 100–200 |

Twitter and Trustpilot are pay-per-result — every returned item is billed.

### Step 4: Run

Single example pulling Reddit threads + Twitter mentions for InPost (driven by [`data/osint-targets.json`](data/osint-targets.json)):

```bash
apify call fatihtahta/reddit-scraper-search-fast \
  --input "$(jq -c '.targets[] | select(.company_id=="inpost") | .inputs.reddit' \
    ${CLAUDE_PLUGIN_ROOT}/skills/apify-financial-osint/data/osint-targets.json)" \
  --output-dataset > reddit_inpost.json
```

Full per-actor input schema (all 51 Twitter properties, every Reddit enum, every Trustpilot edge case) plus 30+ example invocations: [reference/osint-actor-schemas.md](reference/osint-actor-schemas.md).

### Step 4b: Post-filter Reddit results

Reddit search ignores quotes and matches partial words ("InPost" matches "in post game thread"). After fetching, filter results client-side: keep only posts where any of the company's search queries appears as a whole word (case-insensitive) in `title` or `body`. Use the `queries` array from `data/osint-targets.json` for matching (these are the terms the company is actually known by). Normalise diacritics before comparing (Š↔S, ö↔o, etc.).

Expect 90–95% of raw Reddit results to be false positives. This is normal — `maxPosts` is set to 200 to compensate.

### Step 5: Output

Key output fields per actor:

| Actor | Date field | Date format | URL field | Engagement fields |
|---|---|---|---|---|
| Reddit | `created_utc` | ISO 8601 (`2026-05-01T17:26:41.000Z`) | `canonical_url` | `score`, `num_comments` |
| Twitter | `createdAt` | Non-standard (`Fri May 01 17:35:21 +0000 2026`) | `url` | `likeCount`, `retweetCount`, `replyCount` |
| Trustpilot | `date` | ISO 8601 (`2026-01-27T21:53:45.000Z`) | `url` (review ID, not company page) | `ratingValue` (string "1"–"5") |

Present top results with:

- **Sentiment hint** (positive / negative / neutral) where derivable from text
- **Engagement** — see table above
- **Author / handle**
- **Date** — normalise to YYYY-MM-DD for display
- **Permalink**

Example output for a sentiment scan:

```markdown
## OSINT Scan: InPost — Last 30 days

### Reddit (3 posts, 47 comments analyzed)
| Title | Subreddit | Score | Sentiment | Date | URL |
|---|---|---|---|---|---|
| InPost lockers in UK getting better? | r/unitedkingdom | 124 | positive | 2026-04-12 | … |
| Anyone else missing parcels? | r/poland | 38 | negative | 2026-04-09 | … |

### Twitter/X (87 tweets)
| Tweet (truncated) | Author | Likes | Replies | Date | URL |
|---|---|---|---|---|---|
| FedEx-InPost rollout looks promising… | @logistics_eu | 412 | 27 | 2026-04-22 | … |

### Trustpilot (50 reviews — avg 3.2 / 5)
| Rating | Title | Author | Date | URL |
|---|---|---|---|---|
| 5 | Good system, very efficient | Yeison S. | 2026-03-10 | … |
| 1 | Parcel never delivered | Anna K. | 2026-04-18 | … |
```

## Per-company routing

[`data/osint-targets.json`](data/osint-targets.json) maps each portfolio company → which OSINT actors to run, with pre-built input templates derived from `data/companies.json`. Coverage as of v1.0: 31 entries (30 portfolio + group), Reddit 27, Twitter 31, Trustpilot 5, all-three 5, Twitter-only 4. Empty-actor entries reflect verified absence (e.g., MONETA / CETIN / SOTIO have no Trustpilot page).

## Critical gotchas (high-frequency mistakes)

- **Reddit `maxPosts` default is 50000** — ALWAYS set explicitly (typical: 30–50 for scans).
- **Reddit `maxComments` default is 50000** — set low whenever `scrapeComments: true`.
- **Reddit `subredditKeywords` is an array**, not a string.
- **Reddit `sort` enum has no `"rising"` / `"best"`** — only relevance, hot, top, new, comments.
- **Reddit `includeNsfw`** — lowercase "sfw" (not `includeNSFW`).
- **Twitter `maxItems` is REQUIRED** — actor fails without it. Pay-per-result.
- **Twitter `since` / `until` format is `YYYY-MM-DD_HH:MM:SS_UTC`** (NOT ISO 8601).
- **Twitter `tweetIDs` is plural array** — not `tweetId`.
- **Twitter `lang` default is `"en"`** — set explicitly or omit for all languages.
- **Trustpilot `startUrls` must be array of objects** with `url` key — NOT plain strings.
- **Trustpilot has ONLY 2 input fields** (`startUrls`, `limit`) — older docs reference `maxItems`, `includeStatistics`, `includeCompanyDetails`, `onlyNewerThan` that DO NOT EXIST.
- **Trustpilot `ratingValue` is a STRING** ("1"–"5"), not integer — parse before aggregating.
- **Trustpilot has no date filter** — actor returns most recent first up to `limit`; post-filter by `date` field.
- **Trustpilot URLs verified per company** — see "Known Trustpilot URLs" table in `reference/osint-actor-schemas.md` Section 3. Some companies have NO Trustpilot page (B2B holdings, biotech) — running the actor returns 0 reviews.

Full per-actor schemas + 30+ example invocations: [reference/osint-actor-schemas.md](reference/osint-actor-schemas.md).

## Reference

- [data/osint-targets.json](data/osint-targets.json) — per-company routing + pre-built actor inputs (31 entries)
- [reference/osint-actor-schemas.md](reference/osint-actor-schemas.md) — verbatim source: all 4 actor schemas with portfolio examples (Section 4 Economic Calendar archived; out of scope for this skill — see PLAN.md)
- Shared portfolio data: [`${CLAUDE_PLUGIN_ROOT}/data/companies.json`](../../data/companies.json)
