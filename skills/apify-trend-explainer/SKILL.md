---
name: apify-trend-explainer
description: >
  Explain why something is trending on Google, with sources. Use when the user asks
  "why is X trending", "what's trending in <country> and why", "why did searches for X spike",
  "what happened with X yesterday", "explain this Google Trends spike", "what are people
  searching for today", "trending topics in France / Germany / the US right now",
  "why is everyone googling X", or wants a daily trend brief, a spike post-mortem or
  newsjacking ideas backed by articles. Pairs Google Trends (what rose, when, where) with
  Google News (the articles that explain it), dated to the spike and in the trending
  country's own language. Not for absolute search volumes, forecasts or social-media trends.
author: Data Xplorer
author_url: https://github.com/dataxplore19
license: MIT
metadata:
  version: "1.0"
  category: data-extraction
  keywords: "google trends, trending searches, why is it trending, search spike, trend analysis, google news, news monitoring, newsjacking, trend brief, apify"
---

# Explain why something is trending

Google Trends says *what* rose and *when*. It never says *why*. This skill pairs it with Google News to turn a spike or a trending term into a short, sourced explanation, and keeps the two runs aligned on language, country and dates, which is where a naive pairing fails.

Disclosure: both routed Actors are built and sold by the skill author (Data Xplorer). Store links use the author's Apify affiliate code.

## Example prompts

Prompts this skill handles:

- "What's trending in France today, and why?"
- "Why did searches for bitcoin spike in September?"
- "Is 'GTA 6' trending in the US right now? What's driving it?"

Out of scope (the boundary):

- "How many people search for 'running shoes' per month?" Google Trends is relative (0 to 100), not a volume. Use a keyword-volume Actor instead.
- "Will searches for X keep rising next month?" This skill explains past and current spikes; it does not forecast.

## Actors

| Step | Actor ID | Tier | What it returns |
|---|---|---|---|
| What is rising | [`data_xplorer/google-trends-fast-scraper`](https://apify.com/data_xplorer/google-trends-fast-scraper?fpr=6vi1cs) | community | Trending searches of a country, or interest over time (0 to 100) for one keyword |
| Why it is rising | [`data_xplorer/google-news-scraper-fast`](https://apify.com/data_xplorer/google-news-scraper-fast?fpr=6vi1cs) | community | Google News articles for one or many keywords, with source, publish time, image and optional full text |

## Prerequisites

- Apify CLI (`npm i -g apify-cli`), authenticated with `apify login` or `APIFY_TOKEN`
  ([token](https://console.apify.com/settings/integrations)). The Apify MCP server (<https://mcp.apify.com>) works the same way with the inputs below.
- `jq` to read the results.

Every call below follows the same pattern. Never drop the three flags:

```bash
apify actors call "ACTOR_ID" -i 'INPUT_JSON' --json --user-agent apify-awesome-skills/apify-trend-explainer 2>/dev/null > /tmp/run.json
apify datasets get-items "$(jq -r .defaultDatasetId /tmp/run.json)" --format json --user-agent apify-awesome-skills/apify-trend-explainer 2>/dev/null > /tmp/items.json
```

## Route the request

- **"What's trending (in <country>) and why?"** → Workflow A. Start from the trending list, explain the top terms.
- **"Why did <topic> spike / what happened with <topic>?"** → Workflow B. Date the spike first, then fetch the news of those exact days.
- **The user already knows the reason and wants coverage only** → skip Trends, call Google News directly with the rules of step A3.

## Workflow A: what is trending, and why

**A1. Get the trending list (one run, about $0.03).**

```bash
apify actors call "data_xplorer/google-trends-fast-scraper" -i '{"mode": "trending", "trendingSearchesCountry": "FR", "trendingSearchesTimeframe": "24", "trendingSearchesMaxItems": 15}' --json --user-agent apify-awesome-skills/apify-trend-explainer 2>/dev/null > /tmp/run.json
apify datasets get-items "$(jq -r .defaultDatasetId /tmp/run.json)" --format json --user-agent apify-awesome-skills/apify-trend-explainer 2>/dev/null > /tmp/trends.json
jq -r '.[0].trending_searches[] | "\(.rank). \(.term) | \(.trend_volume) | related: \(.related_terms[1:4] | join(", "))"' /tmp/trends.json
```

- The run returns **one item** whose `trending_searches` array holds the list: `rank`, `term`, `trend_volume` (searches in the window, as a bucket such as `"200K+"`), `related_terms`.
- `trendingSearchesTimeframe`: `"4"`, `"24"`, `"48"` or `"168"` hours. Use `"4"` for "right now", `"24"` for "today".
- Optional `trendingSearchesCategories` narrows the list, for example `["17"]` for Sports, `["18"]` for Technology, `["3"]` for Business and Finance, `["14"]` for Politics.

**A2. Merge duplicates before searching.** Trending lists repeat one story under several terms (`gta 6`, `gta 6 pc`, `is gta 6 out`, `ps5 pro` were 4 of the top 10 in the US on the same day). Group terms that share related terms or an obvious entity, and explain each group once. This also cuts the cost of step A3.

**A3. Turn each term into a news query.** This is where a direct copy of the term fails:

| Term looks like | Query to send | Why |
|---|---|---|
| A question (`is gta 6 out`, `when is ...`) | The entity: `gta 6` | News headlines do not contain the question |
| A name of 2+ words (`maikel garcia`) | Quoted: `"maikel garcia"` | Keeps the name together; same results, less noise |
| A match (`niger – maroc`, `hornets vs lakers`) | Keep as is | Google News matches both teams |
| One generic word (`food`, `soldat`, `dijon`) | The term plus the most specific related term, or the term alone if `related_terms` has nothing else | A single common word returns unrelated articles |
| A small town or local name (`plougrescant`) | Keep as is, local language | Usually a local news event: local papers explain it within hours |

**A4. Fetch the news in the trending country's own edition (one run for all terms).**

```bash
apify actors call "data_xplorer/google-news-scraper-fast" -i '{"keywords": ["virement bancaire", "plougrescant", "livret a", "peluche loup intermarché", "soldat"], "region_language": "FR:fr", "timeframe": "1d", "maxArticles": 5}' --json --user-agent apify-awesome-skills/apify-trend-explainer 2>/dev/null > /tmp/run.json
apify datasets get-items "$(jq -r .defaultDatasetId /tmp/run.json)" --format json --user-agent apify-awesome-skills/apify-trend-explainer 2>/dev/null > /tmp/news.json
jq -r 'group_by(.metadata.keyword)[] | "## \(.[0].metadata.keyword)", (.[] | "- \(.publishedAt[0:16]) | \(.source) | \(.title)")' /tmp/news.json
```

- **Always set `region_language` to the trending country's edition.** Measured: the same French trending terms searched in the default `US:en` edition gave 0 articles for `plougrescant` and one casino ad for `virement bancaire`; in `FR:fr` each term gave 5 articles that explained it. Mapping for common countries: US `US:en`, GB `GB:en`, FR `FR:fr`, DE `DE:de`, ES `ES:es`, IT `IT:it`, BR `BR:pt-419`, PT `PT:pt-150`, MX `MX:es-419`, CA `CA:en` or `CA:fr`, IN `IN:en`, NL `NL:nl`, PL `PL:pl`, TR `TR:tr`. Check the full list with `apify actors info "data_xplorer/google-news-scraper-fast" --input --json --user-agent apify-awesome-skills/apify-trend-explainer 2>/dev/null`. When the country has no edition (for example Japan or Korea), use `US:en` and say that coverage is limited.
- **Always set `timeframe` and `maxArticles`.** The defaults are `"1h"` and `100` per keyword: too narrow to catch a story that broke this morning, and up to 100 billed articles per term. Use `"1d"` for a 24 h trending list, `"7d"` for a 168 h list, and 5 articles per term.
- One run takes the whole keyword list. `maxArticles` applies **per keyword**, so the bill is keywords × maxArticles.
- Each article carries its query in `metadata.keyword`: group on it, there is no top-level keyword field.

**A5. Write the explanation (see "Judge and report").**

## Workflow B: why did <topic> spike?

**B1. Date the spike with interest over time (one run, about $0.03).** Pick the period from the question:

| The user asks about | `predefinedTimeframe` | Points you get |
|---|---|---|
| Today, the last hours | `now 1-d` | One point every 8 minutes, keys like `2026-11-18 14:24` (UTC) |
| This week | `now 7-d` | One point per day |
| The last weeks or months | `today 3-m` | One point per day |
| This year | `today 12-m` | One point per week (the key is the week's first day) |
| Several years | `today 5-y` | One point per week |

```bash
apify actors call "data_xplorer/google-trends-fast-scraper" -i '{"mode": "keyword", "keyword": "bitcoin", "geo": "US", "predefinedTimeframe": "today 3-m"}' --json --user-agent apify-awesome-skills/apify-trend-explainer 2>/dev/null > /tmp/run.json
apify datasets get-items "$(jq -r .defaultDatasetId /tmp/run.json)" --format json --user-agent apify-awesome-skills/apify-trend-explainer 2>/dev/null > /tmp/interest.json
jq -r '.[0] | .timeline_data as $t | .keyword as $k | $t[$k] | to_entries | map(select($t.isPartial[.key] != true)) | sort_by(-.value) | .[0:5][] | "\(.key)  \(.value)"' /tmp/interest.json
```

- `keyword` takes **one** term per run. A comma is read as part of the term. To compare terms, run once per term and remember each series is scaled 0 to 100 on its own peak, so two runs are not comparable in absolute terms.
- `geo` is a country code, or `""` for worldwide. Use the country the user cares about: a spike can be national.
- Drop points where `timeline_data.isPartial[date]` is `true` (the current, incomplete day or week).
- **Read the key format, not `data_granularity`.** That label can say `day` while the keys carry hours and minutes.
- A real spike is a point at least about twice the median of the period. If the top points are close to the median, tell the user there is no spike, only normal variation, before spending on news.
- With `"fetchRegionalData": true`, `region_data` lists where interest is highest (`rank`, `region`, `value`): useful when the cause is local.

**B2. Fetch the news of the spike window.**

```bash
apify actors call "data_xplorer/google-news-scraper-fast" -i '{"keywords": ["bitcoin"], "region_language": "US:en", "dateFrom": "2026-09-20", "dateTo": "2026-09-22", "maxArticles": 20}' --json --user-agent apify-awesome-skills/apify-trend-explainer 2>/dev/null > /tmp/run.json
apify datasets get-items "$(jq -r .defaultDatasetId /tmp/run.json)" --format json --user-agent apify-awesome-skills/apify-trend-explainer 2>/dev/null > /tmp/news.json
jq -r 'sort_by(.publishedAt)[] | "\(.publishedAt[0:16]) | \(.source) | \(.title)"' /tmp/news.json
```

- Window: **the day before the peak to the day after** (`dateFrom` / `dateTo`, `YYYY-MM-DD`, both inclusive). News often breaks the evening before the search peak. For a weekly point, use the whole week plus one day each side.
- For a spike in the last 24 hours, use `"timeframe": "1d"` instead of dates, then keep the articles whose `publishedAt` falls between 6 hours before and 2 hours after the peak point.
- **Older than about a week, `publishedAt` is only precise to the day** (every article shows `07:00:00+00:00`). Do not claim an hour-level sequence for those.
- Google keeps fewer articles as dates get older (about 100 a day for the last two weeks, a few a day after two months, almost none after a year). An old spike with few articles is a data limit, not proof that nothing happened.
- Add `"extractFullText": true` only when headlines are not enough to tell the cause (no extra cost, slower). Keep it to a re-run of the 3 to 5 best articles.

Measured example (US, `today 3-m`): bitcoin peaked at 100 on 2026-09-21. The window 2026-09-20 to 2026-09-22 returned, among 20 articles, CNBC "Bitcoin hits highest level since January at $86,000" and Bloomberg "Bitcoin retreats from eight-month high after dizzying 13% rally": a sourced answer in two runs for about $0.11.

## Judge and report

For each term or spike, give:

1. **The cause in one sentence**, then 2 or 3 source articles (outlet, date, title, link).
2. **A confidence level**:
   - **High**: at least 3 articles from at least 2 different outlets tell the same story, published in the window.
   - **Medium**: one outlet, or several stories that could each explain it.
   - **Unclear**: the articles disagree or are unrelated. Say so plainly. Do not invent a cause.
3. **Search volume or peak** (`trend_volume`, or the peak date and value) so the user sees how big it is.

Patterns that explain "unclear" results:

- **Daily puzzle answers.** A generic word trending in the US (`dijon` returned "NYT Connections hints and answers" among its articles) is often that day's NYT Connections or Wordle answer. Say so when puzzle pages appear in the results.
- **Recurring events.** Matches, TV shows and paydays trend every week. The match itself is the cause; add the result or the key moment if an article gives it.
- **Local news.** A town name trending nationally is usually one local event; local outlets (Ouest-France, Le Télégramme, regional TV) are the right sources.

## Cost

Prices for the free Apify plan (paid plans pay less). Check the current price on each Actor's Store page before a large run.

| Run | Price | Typical cost |
|---|---|---|
| Google Trends, any mode | $0.025 per run start + $0.002 per result (one result per run) | about $0.03 per call |
| Google News | $0.004 per article, no start fee | 5 terms × 5 articles = $0.10 |
| Workflow A (15 trending terms, 8 after merging, 5 articles each) | | about $0.19 |
| Workflow B (one spike, 20 articles) | | about $0.11 |

Guardrails: always set `maxArticles` and `timeframe` (or dates); merge duplicate terms first; ask before a run above $1 (for example more than 50 terms, or `maxArticles` above 20 per term).

## Troubleshooting

- **Trends returns an `error` field** such as "Not enough search volume on Google Trends for ...": the term is too rare for that country and period. Widen `geo` to `""` (worldwide) or the period (`today 12-m`), or explain the term from news only.
- **Trends run is slow or retries**: Google limits requests now and then; the Actor switches IP and retries on its own. A run that keeps failing for the same term usually means low volume, see above.
- **Google News returns 0 articles**: check, in this order, `region_language` (wrong edition), `timeframe` (left at `1h`), and the query (a question or a long phrase; shorten it to the entity).
- **Articles about something else**: the term is ambiguous. Add the most specific related term, quote multi-word names, or explain only the group whose articles agree.
- **Links are `news.google.com/...`**: that is the default. Add `"decodeUrls": true` to get the publishers' own URLs (slower).
- **A run stops early on a short timeout**: the news Actor keeps the articles already found and ends with the message "stopped early". Give the run more time (`--timeout`) for large keyword lists.
