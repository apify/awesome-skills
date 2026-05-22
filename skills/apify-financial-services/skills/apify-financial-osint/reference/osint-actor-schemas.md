# OSINT Actor Input Schemas — Complete Reference

> Last updated: 2026-03-16
> Source: Apify API v2 build endpoint (actual inputSchema JSON), verified against demo/data/2w/osint/ outputs.

---

## 1. Reddit — fatihtahta/reddit-scraper-search-fast

**URL:** https://apify.com/fatihtahta/reddit-scraper-search-fast
**Cost:** $1.49 / 1,000 results
**Success rate:** 98.4% (30-day: 40,787 runs, 40,112 succeeded)
**Use case:** Reddit sentiment about InPost delivery, O2 CZ service quality, PPF Group acquisition reactions

### Input Schema (verified from API)

| Field | Type | Default | Required | Description |
|-------|------|---------|----------|-------------|
| `queries` | array of string | `["Cheesecake","Swimming Pool"]` | One of queries/urls/subredditName | Global keyword search terms. Each query runs a Reddit-wide search. |
| `urls` | array of string | — | One of queries/urls/subredditName | Direct Reddit post/comment/subreddit/user URLs to scrape. |
| `subredditName` | string | — | One of queries/urls/subredditName | Subreddit name (without r/) for subreddit-mode scraping. |
| `subredditKeywords` | **array of string** | — | No | Keywords to filter posts inside the subreddit. Leave empty to browse all. |
| `subredditSort` | string (enum) | `"relevance"` | No | Sort order within subreddit. Values: `"relevance"`, `"hot"`, `"top"`, `"new"`, `"comments"` |
| `subredditTimeframe` | string (enum) | `"all"` | No | Time filter within subreddit. Values: `"all"`, `"year"`, `"month"`, `"week"`, `"day"`, `"hour"` |
| `maxPosts` | integer | **50000** | No | Max posts to extract per query/URL. **Minimum 10.** Set low (10-100) to control costs! |
| `maxComments` | integer | **50000** | No | Max comments per post. Only used when `scrapeComments` is true. Set low! |
| `scrapeComments` | boolean | `false` | No | Toggle comment extraction. Must be `true` for `maxComments` to take effect. |
| `sort` | string (enum) | `"relevance"` | No | Sort for search results. Values: `"relevance"`, `"hot"`, `"top"`, `"new"`, `"comments"` |
| `timeframe` | string (enum) | `"all"` | No | Time filter for search. Values: `"all"`, `"year"`, `"month"`, `"week"`, `"day"`, `"hour"` |
| `includeNsfw` | boolean | `false` | No | Include NSFW content. **Note:** lowercase "sfw" — NOT `includeNSFW`. |

**⚠️ No `fastMode` or `proxy` fields** — these do not exist in the current schema.

### Output Fields (per record)

```json
{
  "kind": "post",
  "id": "1qzy80j",
  "title": "...",
  "body": "...",
  "author": "username",
  "score": 651,
  "num_comments": 84,
  "subreddit": "BuyFromEU",
  "created_utc": "2026-02-09T07:48:25.000Z",
  "url": "https://www.reddit.com/r/.../comments/.../",
  "upvote_ratio": 0.98
}
```

### Example Inputs

**InPost delivery sentiment (acquisition reactions):**
```json
{
  "queries": ["InPost parcel locker", "InPost FedEx acquisition", "InPost PPF"],
  "maxPosts": 50,
  "scrapeComments": true,
  "maxComments": 10,
  "sort": "relevance",
  "timeframe": "month",
  "includeNsfw": false
}
```

**O2 CZ service quality:**
```json
{
  "queries": ["O2 Czech Republic", "O2 CZ mobile", "O2 Czechia network"],
  "maxPosts": 30,
  "sort": "new",
  "timeframe": "month",
  "scrapeComments": true,
  "maxComments": 5
}
```

**Group brand perception:**
```json
{
  "queries": ["PPF Group", "PPF investment", "Petr Kellner PPF"],
  "maxPosts": 50,
  "sort": "relevance",
  "timeframe": "year"
}
```

**Subreddit-specific (e.g., r/poland for InPost):**
```json
{
  "subredditName": "poland",
  "subredditKeywords": ["InPost", "delivery", "locker"],
  "subredditSort": "relevance",
  "subredditTimeframe": "month",
  "maxPosts": 30,
  "scrapeComments": true,
  "maxComments": 5
}
```

**InPost peers — logistics sentiment:**
```json
{
  "queries": ["PostNL delivery", "bpost Belgium", "DHL parcel", "Austrian Post delivery"],
  "maxPosts": 30,
  "sort": "relevance",
  "timeframe": "year",
  "scrapeComments": true,
  "maxComments": 5
}
```

**Allegro e-commerce (InPost competitor):**
```json
{
  "queries": ["Allegro Poland shopping", "Allegro delivery", "Allegro vs InPost"],
  "maxPosts": 30,
  "sort": "relevance",
  "timeframe": "year"
}
```

**Telecom portfolio:**
```json
{
  "queries": ["Yettel Hungary mobile", "Yettel Bulgaria", "Deutsche Telekom Europe"],
  "maxPosts": 30,
  "sort": "relevance",
  "timeframe": "year"
}
```

**Banking/fintech:**
```json
{
  "queries": ["MONETA Money Bank Czech", "Air Bank Czech", "Home Credit loan"],
  "maxPosts": 30,
  "sort": "relevance",
  "timeframe": "year"
}
```

**Heureka Group (price comparison):**
```json
{
  "searchQuery": "Heureka price comparison",
  "subreddits": ["czech", "Cesko"],
  "maxPosts": 15
}
```

**Škoda Group (transportation):**
```json
{
  "searchQuery": "Skoda Transportation tram",
  "subreddits": ["trains", "transit"],
  "maxPosts": 15
}
```

**SOTIO biotech:**
```json
{
  "searchQuery": "SOTIO biotech clinical trial",
  "subreddits": ["biotech", "cancer"],
  "maxPosts": 15
}
```

**CME / TV Nova:**
```json
{
  "searchQuery": "TV Nova Voyo streaming Czech",
  "subreddits": ["czech", "Cesko", "television"],
  "maxPosts": 15
}
```

**Dream Yacht Charter:**
```json
{
  "searchQuery": "Dream Yacht Charter review",
  "subreddits": ["sailing", "boating", "travel"],
  "maxPosts": 15
}
```

### Gotchas & Limitations

- **`maxPosts` default is 50000** — always set explicitly to avoid scraping everything and burning credits.
- `subredditKeywords` is an **array**, not a string.
- `sort` enum does NOT include `"rising"` or `"best"` — only: relevance, hot, top, new, comments.
- Use `subredditSort` and `subredditTimeframe` for subreddit-mode (these are separate from the global `sort`/`timeframe`).
- Residential proxies are used internally — no proxy config field exposed.

---

## 2. Twitter/X — kaitoeasyapi/twitter-x-data-tweet-scraper-pay-per-result-cheapest

**URL:** https://apify.com/kaitoeasyapi/twitter-x-data-tweet-scraper-pay-per-result-cheapest
**Cost:** $0.25 / 1,000 tweets (pay-per-result)
**Success rate:** 99.7%
**Rating:** 4.3/5 (58 reviews)
**Use case:** Twitter/X mentions of InPost, PPF, telecom sector, real-time crisis monitoring

### Input Schema (verified from API — 51 properties, key ones below)

**Core fields:**

| Field | Type | Default | Required | Description |
|-------|------|---------|----------|-------------|
| `twitterContent` | string | `"from:elonmusk make -\"live laugh love\""` | One of twitterContent/tweetIDs/searchTerms | Search query using Twitter advanced search syntax. |
| `tweetIDs` | array of string | `["1846987139428634858"]` | One of twitterContent/tweetIDs/searchTerms | Specific tweet IDs to scrape. **Note:** plural `tweetIDs`, not `tweetId`. |
| `searchTerms` | array of string | — | One of twitterContent/tweetIDs/searchTerms | Array of search terms (each follows Twitter search syntax). `maxItems` applies per term. |
| `maxItems` | integer | `200` | **Yes (required)** | Max tweets to return. When `searchTerms` is set, this is per term. |
| `queryType` | string (enum) | `"Latest"` | No | Search tab. Values: `"Latest"`, `"Top"`, `"Photos"`, `"Videos"` |
| `lang` | string (enum) | `"en"` | No | Language filter (ISO 639-1). Includes: `"cs"`, `"pl"`, `"hu"`, `"de"`, `"nl"`, `"sk"`, `"bg"`, etc. |
| `from` | string | — | No | Filter by sender @username (without @). |

**Advanced filters (useful for portfolio monitoring):**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `since` | string | `"2021-12-31_23:59:59_UTC"` | On or after date. Format: `YYYY-MM-DD_HH:MM:SS_UTC` |
| `until` | string | `"2024-12-31_23:59:59_UTC"` | Before date. Same format. |
| `within_time` | string | — | Relative time window, e.g. `"7d"`, `"24h"`, `"30m"` |
| `near` | string | — | Geotagged near place, e.g. `"Warsaw"`, `"Prague"` |
| `min_retweets` | integer | `0` | Minimum retweet count |
| `min_faves` | integer | `0` | Minimum favorites count |
| `min_replies` | integer | `0` | Minimum reply count |
| `filter:news` | boolean | `false` | Only tweets with news links |
| `filter:media` | boolean | `false` | Only tweets with media |
| `filter:blue_verified` | boolean | `false` | Only blue-verified users |
| `filter:safe` | boolean | `false` | Exclude NSFW content |
| `to` | string | — | Replying to @username |
| `@` | string | — | Mentioning @username |

### Output Fields (per tweet)

```json
{
  "id": "2032250178661388521",
  "url": "https://x.com/username/status/...",
  "text": "tweet text here",
  "retweetCount": 0,
  "replyCount": 0,
  "likeCount": 0,
  "viewCount": 11,
  "createdAt": "Fri Mar 13 00:19:34 +0000 2026",
  "lang": "pl",
  "author": {
    "type": "user",
    "userName": "...",
    "id": "...",
    "name": "...",
    "isVerified": false,
    "isBlueVerified": false,
    "followers": 30,
    "following": 134,
    "statusesCount": 1107,
    "description": "..."
  }
}
```

### Example Inputs

**InPost real-time sentiment:**
```json
{
  "twitterContent": "InPost",
  "maxItems": 100,
  "queryType": "Latest",
  "lang": "en"
}
```

**InPost Polish-language mentions:**
```json
{
  "twitterContent": "InPost paczkomat",
  "maxItems": 100,
  "queryType": "Latest",
  "lang": "pl"
}
```

**Group deal reactions:**
```json
{
  "twitterContent": "PPF Group OR \"PPF investment\" OR \"PPF telecom\"",
  "maxItems": 50,
  "queryType": "Top"
}
```

**O2 CZ + Yettel telecom combined:**
```json
{
  "twitterContent": "\"O2 Czech\" OR Yettel OR \"PPF Telecom\"",
  "maxItems": 100,
  "queryType": "Latest"
}
```

**InPost take-private deal monitoring (with date + engagement filters):**
```json
{
  "twitterContent": "InPost FedEx acquisition OR InPost takeover OR INPST",
  "maxItems": 200,
  "queryType": "Latest",
  "since": "2026-01-01_00:00:00_UTC",
  "min_faves": 5,
  "filter:news": true
}
```

**InPost peers — logistics:**
```json
{
  "twitterContent": "PostNL OR bpost OR \"DHL Group\" OR \"Austrian Post\"",
  "maxItems": 100,
  "queryType": "Latest"
}
```

**Allegro competitive intelligence:**
```json
{
  "twitterContent": "Allegro Poland OR allegro.pl OR \"Allegro delivery\"",
  "maxItems": 50,
  "queryType": "Latest",
  "lang": "pl"
}
```

**Telecom:**
```json
{
  "twitterContent": "Yettel OR \"e& PPF Telecom\" OR \"CETIN Group\"",
  "maxItems": 100,
  "queryType": "Latest"
}
```

**MONETA / Air Bank Czech banking:**
```json
{
  "twitterContent": "\"MONETA Money Bank\" OR \"Air Bank\" OR \"PPF banka\"",
  "maxItems": 50,
  "queryType": "Latest",
  "lang": "cs"
}
```

**Heureka:**
```json
{
  "searchQueries": ["Heureka shopping Czech"],
  "maxItems": 20,
  "tweetLanguage": "cs"
}
```

**SOTIO:**
```json
{
  "searchQueries": ["SOTIO biotech OR SOTIO clinical trial"],
  "maxItems": 20
}
```

**Škoda Group:**
```json
{
  "searchQueries": ["Skoda Transportation OR Skoda Group tram"],
  "maxItems": 20
}
```

**Home Credit:**
```json
{
  "searchQueries": ["Home Credit Vietnam OR Home Credit Philippines"],
  "maxItems": 20
}
```

**CME / Nova:**
```json
{
  "searchQueries": ["TV Nova streaming OR Voyo Czech"],
  "maxItems": 20,
  "tweetLanguage": "cs"
}
```

### Gotchas & Limitations

- **`maxItems` is REQUIRED** — the actor will fail without it.
- `twitterContent` is a **single string** — use Twitter operators (`OR`, `-`, `from:`, `since:`, `until:`) to combine.
- `tweetIDs` is plural (array) — not `tweetId`.
- `searchTerms` (array) also works — each term gets up to `maxItems` results independently.
- `lang` default is `"en"` — set explicitly or omit for all languages.
- `since`/`until` format is `YYYY-MM-DD_HH:MM:SS_UTC` — unusual format, not ISO 8601.
- Pay-per-result: you only pay for tweets actually returned.
- Author info is included by default (full profile data).

---

## 3. Trustpilot — getwally.net/trustpilot-reviews-scraper

**URL:** https://apify.com/getwally.net/trustpilot-reviews-scraper
**Cost:** $3.00 / 1,000 results
**Use case:** Customer satisfaction for InPost, O2 CZ, Yettel, Heureka, Home Credit

### Input Schema (verified from API — ONLY 2 fields!)

| Field | Type | Default | Required | Description |
|-------|------|---------|----------|-------------|
| `startUrls` | array of objects | `[{"url":"https://www.trustpilot.com/review/postmarkapp.com"}]` | **Yes** | Review page URLs. Format: `[{"url": "https://www.trustpilot.com/review/domain.com"}]` — **array of objects with `url` key**, not plain strings! |
| `limit` | integer | `1000` | No | Maximum number of reviews to scrape. |

**⚠️ CRITICAL: Only 2 input fields exist.** The following fields from older documentation do **NOT exist**:
- ~~`maxItems`~~ → use `limit`
- ~~`includeCompanyDetails`~~ → does not exist
- ~~`includeStatistics`~~ → does not exist
- ~~`onlyNewerThan`~~ → does not exist
- ~~`maxConcurrency`~~ → does not exist
- ~~`minConcurrency`~~ → does not exist
- ~~`maxRequestRetries`~~ → does not exist
- ~~`customMapFunction`~~ → does not exist

### Output Fields (per review)

```json
{
  "reviewId": "69afe529f0877de1c09ec06e",
  "name": "Yeison Sierra",
  "avatar": "https://user-images.trustpilot.com/.../73x73.png",
  "date": "2026-03-10T11:32:25+00:00",
  "reviewTitle": "Good system and very efficient",
  "reviewText": "I like how the app and the system works...",
  "ratingValue": "5",
  "url": "https://trustpilot.com/reviews/69afe529f0877de1c09ec06e"
}
```

### Example Inputs

**All consumer + peer companies (comprehensive):**
```json
{
  "startUrls": [
    {"url": "https://www.trustpilot.com/review/inpost.pl"},
    {"url": "https://www.trustpilot.com/review/inpost.co.uk"},
    {"url": "https://www.trustpilot.com/review/o2.cz"},
    {"url": "https://www.trustpilot.com/review/yettel.hu"},
    {"url": "https://www.trustpilot.com/review/yettel.bg"},
    {"url": "https://www.trustpilot.com/review/yettel.rs"},
    {"url": "https://www.trustpilot.com/review/heureka.cz"},
    {"url": "https://www.trustpilot.com/review/airbank.cz"}
  ],
  "limit": 50
}
```

**InPost vs logistics peers:**
```json
{
  "startUrls": [
    {"url": "https://www.trustpilot.com/review/inpost.pl"},
    {"url": "https://www.trustpilot.com/review/postnl.nl"},
    {"url": "https://www.trustpilot.com/review/bpost.be"},
    {"url": "https://www.trustpilot.com/review/dhl.com"},
    {"url": "https://www.trustpilot.com/review/post.at"},
    {"url": "https://www.trustpilot.com/review/fedex.com"},
    {"url": "https://www.trustpilot.com/review/ups.com"}
  ],
  "limit": 50
}
```

**Telecom peer comparison:**
```json
{
  "startUrls": [
    {"url": "https://www.trustpilot.com/review/o2.cz"},
    {"url": "https://www.trustpilot.com/review/yettel.hu"},
    {"url": "https://www.trustpilot.com/review/telekom.de"},
    {"url": "https://www.trustpilot.com/review/allegro.pl"}
  ],
  "limit": 50
}
```

**DHL multi-market:**
```json
{
  "startUrls": [
    {"url": "https://www.trustpilot.com/review/dhl.com"},
    {"url": "https://www.trustpilot.com/review/dhl.de"},
    {"url": "https://www.trustpilot.com/review/dhl.nl"}
  ],
  "limit": 50
}
```

**Portfolio — consumer leisure brands:**

**Dream Yacht Charter:**
```json
{
  "startUrls": [{"url": "https://www.trustpilot.com/review/dreamyachtcharter.com"}],
  "limit": 30
}
```

**Leopard Catamarans:** ❌ No Trustpilot profile exists — 0 reviews returned. Do not use.

### Known Trustpilot URLs for Portfolio Companies

| Company | Trustpilot URL | Status |
|---------|---------------|--------|
| InPost PL | trustpilot.com/review/inpost.pl | ✅ |
| InPost UK | trustpilot.com/review/inpost.co.uk | ✅ |
| O2 CZ | trustpilot.com/review/o2.cz | ✅ |
| Yettel HU | trustpilot.com/review/yettel.hu | ✅ |
| Yettel BG | trustpilot.com/review/yettel.bg | ✅ |
| Yettel RS | trustpilot.com/review/yettel.rs | ✅ |
| Heureka CZ | trustpilot.com/review/heureka.cz | ✅ |
| Air Bank | trustpilot.com/review/airbank.cz | ✅ (flaky) |
| PostNL NL | trustpilot.com/review/postnl.nl | ✅ |
| PostNL BE | trustpilot.com/review/postnl.be | ✅ |
| bpost | trustpilot.com/review/bpost.be | ✅ |
| DHL global | trustpilot.com/review/dhl.com | ✅ |
| DHL DE | trustpilot.com/review/dhl.de | ✅ |
| DHL NL | trustpilot.com/review/dhl.nl | ✅ |
| Österr. Post | trustpilot.com/review/post.at | ✅ |
| Allegro | trustpilot.com/review/allegro.pl | ✅ |
| Deutsche Telekom | trustpilot.com/review/telekom.de | ✅ |
| FedEx | trustpilot.com/review/fedex.com | ✅ |
| UPS | trustpilot.com/review/ups.com | ✅ |
| Home Credit CZ | — | ❌ no page |
| MONETA | — | ❌ no page |
| CETIN | — | ❌ no page (B2B) |
| PPF Group | — | ❌ no page (holding) |
| SOTIO | — | ❌ no page (biotech) |
| Dream Yacht Charter | trustpilot.com/review/dreamyachtcharter.com | ✅ |
| Leopard Catamarans | — | ❌ no profile (0 reviews) |

### Gotchas & Limitations

- **`startUrls` is array of OBJECTS** — each item must be `{"url": "..."}`, NOT a plain string.
- **Only `limit` controls max reviews** — no `maxItems`, no `onlyNewerThan`, no `includeCompanyDetails`.
- No date filtering available — the actor returns most recent reviews first, up to `limit`.
- No company details or statistics extraction — only individual reviews are returned.
- `ratingValue` is a **string** ("1" through "5"), not integer — parse before aggregating.
- `limit` default is 1000 — set lower to control costs ($3/1K results).

---

## 4. Economic Calendar — pintostudio/economic-calendar-data-investing-com

**URL:** https://apify.com/pintostudio/economic-calendar-data-investing-com
**Cost:** $10.00 / 1,000 results
**Use case:** Economic calendar events for CZ, PL, HU, EU — central bank rate decisions, GDP releases, CPI data

### Input Schema (verified from API)

| Field | Type | Default | Required | Description |
|-------|------|---------|----------|-------------|
| `country` | string (enum) | `""` | No (not required) | Country name (lowercase). See full enum below. Empty = all countries. |
| `importances` | string (enum) | `""` | No | **Single value only.** Values: `"high"`, `"medium"`, `"low"`, `""` (all). Cannot combine multiple! |
| `timeZone` | string | — | No | Format: `"GMT +X:00"` or `"GMT -X:00"`. E.g., `"GMT +1:00"` for CET. |
| `timeFilter` | string (enum) | `"time_only"` | No | **Note: `timeFilter`, NOT `timeFormat`.** Values: `"time_only"`, `"time_remain"` |
| `categories` | string | `""` | No | Event category filter. Empty = all categories. |
| `fromDate` | string | today | No | Start date. Format: `"YYYY-MM-DD"`. Defaults to today. |
| `toDate` | string | today | No | End date. Format: `"YYYY-MM-DD"`. |

**Country enum (47 countries — NO "euro zone"):**
```
spain, united states, united kingdom, germany, france, italy, netherlands,
belgium, portugal, austria, switzerland, norway, sweden, denmark, finland,
poland, czech republic, hungary, greece, turkey, russia, china, japan,
south korea, india, australia, canada, brazil, mexico, argentina, chile,
colombia, peru, south africa, israel, saudi arabia, united arab emirates,
malaysia, singapore, thailand, indonesia, philippines, vietnam, taiwan,
hong kong, new zealand
```

**⚠️ "euro zone" is NOT in the enum.** For ECB/Eurozone events, use `"germany"` (ECB events appear under Germany) or leave `country` empty and filter results.

**⚠️ `importances` is a single enum value**, not a comma-separated list. To get both high and medium, run two separate calls or leave empty for all.

### Output Fields (per event)

```json
{
  "id": "541956",
  "date": "02/03/2026",
  "time": "08:30",
  "zone": "czech republic",
  "currency": "CZK",
  "importance": "low",
  "event": "S&P Global Czech Republic Manufacturing PMI  (Feb)",
  "actual": "50.0",
  "forecast": "50.4",
  "previous": "49.8"
}
```

### Example Inputs

**Czech Republic — high-importance events (CNB rate decisions, GDP, CPI):**
```json
{
  "country": "czech republic",
  "importances": "high",
  "timeZone": "GMT +1:00",
  "fromDate": "2026-03-01",
  "toDate": "2026-04-30"
}
```

**Poland — all events (InPost, Allegro context):**
```json
{
  "country": "poland",
  "importances": "",
  "timeZone": "GMT +1:00",
  "fromDate": "2026-03-01",
  "toDate": "2026-03-31"
}
```

**Hungary — monetary policy (Yettel HU context):**
```json
{
  "country": "hungary",
  "importances": "high",
  "timeZone": "GMT +1:00",
  "fromDate": "2026-03-01",
  "toDate": "2026-06-30"
}
```

**Germany — includes ECB events (closest proxy for "euro zone"):**
```json
{
  "country": "germany",
  "importances": "high",
  "timeZone": "GMT +1:00",
  "fromDate": "2026-03-01",
  "toDate": "2026-06-30"
}
```

**Netherlands — HQ jurisdiction:**
```json
{
  "country": "netherlands",
  "importances": "",
  "timeZone": "GMT +1:00",
  "fromDate": "2026-03-01",
  "toDate": "2026-03-31"
}
```

**All countries, high importance only:**
```json
{
  "country": "",
  "importances": "high",
  "timeZone": "GMT +1:00",
  "fromDate": "2026-03-01",
  "toDate": "2026-03-31"
}
```

**Turkey (TEMSA territory):**
```json
{
  "country": "turkey",
  "importances": "high",
  "timeZone": "GMT +3:00",
  "timeFilter": "time_only",
  "fromDate": "2026-03-01",
  "toDate": "2026-06-30"
}
```

**Vietnam (Home Credit territory):**
```json
{
  "country": "vietnam",
  "importances": "",
  "timeZone": "GMT +7:00",
  "timeFilter": "time_only",
  "fromDate": "2026-03-01",
  "toDate": "2026-03-31"
}
```

**United States (SOTIO, PPF Real Estate, FedEx/UPS):**
```json
{
  "country": "united states",
  "importances": "high",
  "timeZone": "GMT -5:00",
  "timeFilter": "time_only",
  "fromDate": "2026-03-01",
  "toDate": "2026-03-31"
}
```

**Multi-country batch workflow (run each as separate actor call):**
```python
countries = [
    "czech republic", "poland", "hungary", "germany", "netherlands",
    "united kingdom", "austria", "turkey", "vietnam", "united states"
]
for country in countries:
    input_json = {
        "country": country,
        "importances": "high",
        "timeZone": "GMT +1:00",
        "fromDate": "2026-03-01",
        "toDate": "2026-03-31"
    }
    # call-actor with input_json
```

### Tested Countries (confirmed working)

| Country | Currency | Key Events |
|---------|----------|-------------------|
| czech republic | CZK | CNB rate decision, GDP, CPI, PMI, unemployment |
| poland | PLN | NBP rate decision, GDP, CPI, PMI |
| hungary | HUF | MNB rate decision, GDP, CPI |
| germany | EUR | GDP, PMI, ZEW, Ifo, unemployment, ECB events |
| netherlands | EUR | GDP, CPI, consumer confidence |
| united kingdom | GBP | BoE rate decision, GDP, CPI |
| austria | EUR | GDP, CPI, PMI |
| turkey | TRY | CBRT rate decisions, GDP, CPI, unemployment |
| vietnam | VND | GDP, CPI, trade balance, FDI |
| united states | USD | Fed rate decisions, GDP, CPI, NFP, PMI |

### Gotchas & Limitations

- **One country per call** — or leave empty for all countries.
- **`importances` is SINGLE value** — `"high"`, `"medium"`, `"low"`, or `""` (all). Cannot combine `"high,medium"`.
- **Field name is `timeFilter`** — NOT `timeFormat`.
- **No "euro zone"** in country enum — use `"germany"` or empty + post-filter.
- **No proxy support** — `additionalProperties: false` in schema.
- **Missing countries**: Bulgaria, Serbia, Slovakia are NOT in the API's country enum. These operating territories cannot be monitored via this actor.
- Date format: input is `"YYYY-MM-DD"`, output is `"DD/MM/YYYY"`.
- Cost: $10/1K results. A month × one country ≈ 50-150 events ≈ $0.50-$1.50.
- If no dates provided, returns events for current day only.

---

## Quick Reference: Parameter Names (API-verified)

| Actor | Old/wrong name | Correct API name | Notes |
|-------|---------------|-----------------|-------|
| Reddit | `includeNSFW` | `includeNsfw` | Lowercase "sfw" |
| Reddit | `maxPosts` default 100 | default **50000** | Always set explicitly! |
| Reddit | `subredditKeywords` string | **array of string** | Changed type |
| Reddit | `fastMode`, `proxy` | **do not exist** | Removed from schema |
| Reddit | sort: "rising", "best" | **not valid** | Only: relevance, hot, top, new, comments |
| Twitter | `tweetId` | `tweetIDs` | Plural, array |
| Twitter | `maxItems` optional | **required** | Actor fails without it |
| Twitter | `customMapFunction` | **does not exist** | Removed from schema |
| Trustpilot | `maxItems` | `limit` | Different name, default 1000 |
| Trustpilot | `startUrls` string[] | **object[]** `[{"url":"..."}]` | Array of objects! |
| Trustpilot | `includeCompanyDetails` | **does not exist** | Only 2 fields total |
| Trustpilot | `includeStatistics` | **does not exist** | Only 2 fields total |
| Trustpilot | `onlyNewerThan` | **does not exist** | No date filtering |
| Econ Cal | `timeFormat` | `timeFilter` | Wrong name in old docs |
| Econ Cal | `"euro zone"` | **not in enum** | Use "germany" or empty |
| Econ Cal | `importances: "high,medium"` | **single value only** | Cannot combine |

---

## CLI Examples (call-actor via MCP)

### Reddit — portfolio + peers

```bash
# Core portfolio
mcpc @apify tools-call call-actor \
  actor:="fatihtahta/reddit-scraper-search-fast" \
  input:='{"queries":["InPost parcel locker","O2 Czech Republic","PPF Group","MONETA Money Bank Czech","Air Bank Czech","Yettel Hungary mobile"],"maxPosts":30,"sort":"relevance","timeframe":"month","scrapeComments":true,"maxComments":5}'

# InPost logistics peers
mcpc @apify tools-call call-actor \
  actor:="fatihtahta/reddit-scraper-search-fast" \
  input:='{"queries":["PostNL delivery","bpost Belgium","DHL parcel","Austrian Post delivery"],"maxPosts":30,"sort":"relevance","timeframe":"year","scrapeComments":true,"maxComments":5}'

# Allegro competitive intelligence
mcpc @apify tools-call call-actor \
  actor:="fatihtahta/reddit-scraper-search-fast" \
  input:='{"queries":["Allegro Poland shopping","Allegro delivery","Allegro vs InPost"],"maxPosts":30,"sort":"relevance","timeframe":"year"}'
```

### Twitter — InPost + peers + telecom + banking

```bash
# InPost take-private monitoring
mcpc @apify tools-call call-actor \
  actor:="kaitoeasyapi/twitter-x-data-tweet-scraper-pay-per-result-cheapest" \
  input:='{"twitterContent":"InPost OR INPST OR \"PPF Group\" OR \"InPost FedEx\"","maxItems":100,"queryType":"Latest"}'

# Logistics peers
mcpc @apify tools-call call-actor \
  actor:="kaitoeasyapi/twitter-x-data-tweet-scraper-pay-per-result-cheapest" \
  input:='{"twitterContent":"PostNL OR bpost OR \"DHL Group\" OR \"Austrian Post\"","maxItems":100,"queryType":"Latest"}'

# Telecom
mcpc @apify tools-call call-actor \
  actor:="kaitoeasyapi/twitter-x-data-tweet-scraper-pay-per-result-cheapest" \
  input:='{"twitterContent":"Yettel OR \"e& PPF Telecom\" OR \"CETIN Group\"","maxItems":100,"queryType":"Latest"}'

# Czech banking
mcpc @apify tools-call call-actor \
  actor:="kaitoeasyapi/twitter-x-data-tweet-scraper-pay-per-result-cheapest" \
  input:='{"twitterContent":"\"MONETA Money Bank\" OR \"Air Bank\" OR \"PPF banka\"","maxItems":50,"queryType":"Latest","lang":"cs"}'
```

### Trustpilot — consumer brands + logistics peers

```bash
# All consumer brands
mcpc @apify tools-call call-actor \
  actor:="getwally.net/trustpilot-reviews-scraper" \
  input:='{"startUrls":[{"url":"https://www.trustpilot.com/review/inpost.pl"},{"url":"https://www.trustpilot.com/review/inpost.co.uk"},{"url":"https://www.trustpilot.com/review/o2.cz"},{"url":"https://www.trustpilot.com/review/yettel.hu"},{"url":"https://www.trustpilot.com/review/yettel.bg"},{"url":"https://www.trustpilot.com/review/yettel.rs"},{"url":"https://www.trustpilot.com/review/heureka.cz"},{"url":"https://www.trustpilot.com/review/airbank.cz"}],"limit":50}'

# InPost vs logistics peers
mcpc @apify tools-call call-actor \
  actor:="getwally.net/trustpilot-reviews-scraper" \
  input:='{"startUrls":[{"url":"https://www.trustpilot.com/review/inpost.pl"},{"url":"https://www.trustpilot.com/review/postnl.nl"},{"url":"https://www.trustpilot.com/review/bpost.be"},{"url":"https://www.trustpilot.com/review/dhl.com"},{"url":"https://www.trustpilot.com/review/post.at"},{"url":"https://www.trustpilot.com/review/fedex.com"},{"url":"https://www.trustpilot.com/review/ups.com"}],"limit":50}'
```

### Economic calendar — all territories

```bash
# Czech Republic
mcpc @apify tools-call call-actor \
  actor:="pintostudio/economic-calendar-data-investing-com" \
  input:='{"country":"czech republic","importances":"high","timeZone":"GMT +1:00","fromDate":"2026-03-01","toDate":"2026-04-30"}'

# Poland
mcpc @apify tools-call call-actor \
  actor:="pintostudio/economic-calendar-data-investing-com" \
  input:='{"country":"poland","importances":"high","timeZone":"GMT +1:00","fromDate":"2026-03-01","toDate":"2026-04-30"}'

# Hungary
mcpc @apify tools-call call-actor \
  actor:="pintostudio/economic-calendar-data-investing-com" \
  input:='{"country":"hungary","importances":"high","timeZone":"GMT +1:00","fromDate":"2026-03-01","toDate":"2026-06-30"}'

# Turkey (TEMSA)
mcpc @apify tools-call call-actor \
  actor:="pintostudio/economic-calendar-data-investing-com" \
  input:='{"country":"turkey","importances":"high","timeZone":"GMT +3:00","fromDate":"2026-03-01","toDate":"2026-06-30"}'

# Vietnam (Home Credit)
mcpc @apify tools-call call-actor \
  actor:="pintostudio/economic-calendar-data-investing-com" \
  input:='{"country":"vietnam","importances":"","timeZone":"GMT +7:00","fromDate":"2026-03-01","toDate":"2026-03-31"}'

# United States (SOTIO, Real Estate)
mcpc @apify tools-call call-actor \
  actor:="pintostudio/economic-calendar-data-investing-com" \
  input:='{"country":"united states","importances":"high","timeZone":"GMT -5:00","fromDate":"2026-03-01","toDate":"2026-03-31"}'
```
