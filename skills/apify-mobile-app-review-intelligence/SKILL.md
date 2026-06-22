---
name: apify-mobile-app-review-intelligence
description: Turn App Store and Google Play reviews into product-roadmap intelligence by chaining Apify Actors for iOS reviews, Android reviews, SERP-based app discovery, and website or help-center crawling. Use when the user asks to analyze mobile app reviews, compare app competitors, find bugs or feature requests in reviews, prioritize a mobile roadmap, monitor release feedback, audit ASO sentiment, or explain why an app's ratings changed across iOS and Android.
---

# Mobile App Review Intelligence

Analyze iOS and Android app reviews across a target app and competitors, then convert the raw review text into a prioritized product, QA, and positioning report.

## Prerequisites

- Apify account and either an authenticated Apify CLI session or `APIFY_TOKEN`.
- App Store numeric IDs or URLs when available.
- Google Play package names or URLs when available.
- Target countries, time window, max reviews per app, and whether to include competitors.

## Workflow

1. **Collect scope.** Ask for target app name, known iOS App Store URL or ID, known Android package or Play URL, competitor apps, countries, time window, max reviews per app, and report goal.
2. **Resolve missing app IDs.** If the user only gives app names, run Google Search for `site:apps.apple.com` and `site:play.google.com/store/apps/details` queries. Keep only results whose app title, developer, and category match the target.
3. **Scrape iOS reviews.** Run `jdtpnjtp/apple-app-store-scraper` for known iOS app IDs or URLs, one run per country group if needed.
4. **Scrape Android reviews.** Run `neatrat/google-play-store-reviews-scraper` for known Play package names or URLs.
5. **Crawl supporting pages.** Run Google Search for release notes, help-center pages, pricing pages, public roadmaps, and competitor comparison pages, then crawl the best URLs with `apify/website-content-crawler`.
6. **Normalize evidence.** Merge reviews into a shared schema: platform, app, country, rating, date, version, title, body, developer response, URL or source run ID.
7. **Classify themes.** Assign each review to at most two primary themes: bug, performance, UX confusion, missing feature, pricing, account/login, notification, onboarding, support, localization, billing, privacy, praise, or other.
8. **Prioritize.** Score each theme by volume, rating severity, recency, cross-platform spread, competitor gap, and evidence quality.
9. **Deliver.** Produce a compact executive summary, evidence tables, review excerpts, competitor gaps, and recommended roadmap actions.

## Actor routing

| Need | Actor ID | Tier | Best for |
|------|----------|------|----------|
| Discover app store URLs from names | `apify/google-search-scraper` | apify | Finding App Store and Google Play result URLs when IDs are missing |
| Scrape iOS App Store reviews | `jdtpnjtp/apple-app-store-scraper` | community | App Store reviews, app metadata, country-specific iOS feedback |
| Scrape Google Play reviews | `neatrat/google-play-store-reviews-scraper` | community | Android reviews by package name or Play URL |
| Crawl release notes and help docs | `apify/website-content-crawler` | apify | Competitor docs, release notes, pricing pages, public support pages |

Prefer verified, non-deprecated Actors. Before a large run, inspect each Actor schema because community Actor fields can change.

## Calling Actors - Apify CLI

Use these as payload patterns. Replace IDs, countries, and limits with the user's scope.

```bash
# Discover missing iOS / Android app URLs
apify actors call "apify/google-search-scraper" \
  -i '{"queries":"Slack app site:apps.apple.com\nSlack app site:play.google.com/store/apps/details","maxPagesPerQuery":1,"resultsPerPage":10,"countryCode":"us","languageCode":"en"}' \
  --json \
  --user-agent apify-awesome-skills/apify-mobile-app-review-intelligence \
  2>/dev/null
```

```bash
# iOS App Store reviews
apify actors call "jdtpnjtp/apple-app-store-scraper" \
  -i '{"mode":"lookup","appUrls":["https://apps.apple.com/us/app/slack/id618783545"],"country":"us","includeReviews":true,"maxReviews":500,"timePeriod":"30d","includeAppInfo":true}' \
  --json \
  --user-agent apify-awesome-skills/apify-mobile-app-review-intelligence \
  2>/dev/null
```

```bash
# Android Google Play reviews
apify actors call "neatrat/google-play-store-reviews-scraper" \
  -i '{"appIdOrUrl":"com.Slack","sortBy":"newest","maxReviews":500,"recentDays":30,"uniqueOnly":true}' \
  --json \
  --user-agent apify-awesome-skills/apify-mobile-app-review-intelligence \
  2>/dev/null
```

```bash
# Crawl release notes, help docs, pricing pages, or competitor pages
apify actors call "apify/website-content-crawler" \
  -i '{"startUrls":[{"url":"https://slack.com/release-notes"}],"maxCrawlPages":20,"outputMarkdown":true}' \
  --json \
  --user-agent apify-awesome-skills/apify-mobile-app-review-intelligence \
  2>/dev/null
```

```bash
# Inspect schema and fetch dataset results
apify actors info "neatrat/google-play-store-reviews-scraper" --input --json \
  --user-agent apify-awesome-skills/apify-mobile-app-review-intelligence 2>/dev/null
apify datasets get-items DATASET_ID --format json \
  --user-agent apify-awesome-skills/apify-mobile-app-review-intelligence 2>/dev/null
```

The Apify MCP server at <https://mcp.apify.com> is an equivalent interface. Keep the same actor routing and output schema.

## Inputs to collect

Ask for these before running paid Actors:

| Input | Required | Notes |
|-------|----------|-------|
| Target app | yes | Name plus iOS URL/ID and Android package/URL if known |
| Competitors | no | Use 2-5 direct competitors for gap analysis |
| Countries | yes | Default to `us`; use `all` for iOS only after cost confirmation |
| Time window | yes | Default `30d`; use `7d` for release monitoring |
| Max reviews per app | yes | Default 500; confirm before more than 5,000 per app |
| Ratings to emphasize | no | Default all ratings; use 1-3 stars for bug triage |
| Goal | yes | `roadmap`, `release-regression`, `competitor-gap`, `ASO-sentiment`, or custom |
| Output format | yes | Markdown table, CSV-ready table, or JSON summary |

## Data normalization

Create one normalized row per review:

| Field | Source |
|-------|--------|
| `app` | User label or App Store / Play metadata |
| `platform` | `ios` or `android` |
| `country` | Actor input country |
| `rating` | iOS `rating`; Android `rating` |
| `date` | iOS `date`; Android `date` |
| `version` | iOS `version`; Android `appVersion` |
| `title` | iOS `title`; Android blank if unavailable |
| `body` | iOS `text`; Android `body` |
| `developerResponse` | iOS `developerResponse.body`; Android blank unless present |
| `reviewId` | iOS `id`; Android `reviewId` |
| `sourceRunId` | Apify run ID or dataset URL |

If a field is missing, write `Not found`. Do not infer version, country, or platform.

## Theme and priority scoring

For each normalized review:

1. Drop spam, one-word noise, duplicate bodies, and reviews with no actionable text.
2. Label sentiment from `very_negative`, `negative`, `mixed`, `positive`, `very_positive`.
3. Assign up to two themes. Prefer concrete product themes over generic sentiment.
4. Extract one evidence quote under 35 words.
5. Detect whether the user describes a bug, desired feature, competitor comparison, workflow blocker, or praise.

Score each theme:

| Factor | Points |
|--------|--------|
| Appears in at least 5 reviews | +2 |
| Median rating is 1 or 2 stars | +2 |
| Present on both iOS and Android | +2 |
| Increased in the last 7 days | +2 |
| Mentions a competitor advantage | +2 |
| Mentioned on crawled release notes or help docs | -1 if already solved, +1 if competitor ships it |

Priority:

- `P0`: score 7+ and includes bug, login, billing, data loss, crash, or release regression.
- `P1`: score 5-6 or clear competitor gap with repeated demand.
- `P2`: score 3-4 and useful but not urgent.
- `Watch`: low volume, unclear evidence, or praise-only themes.

## Report format

Return these sections:

1. **Scope and coverage** - apps, platforms, countries, time window, review counts, Apify run IDs or dataset links.
2. **Executive summary** - 5 bullets max, each tied to evidence.
3. **Priority table** - `Priority | Theme | Evidence count | Platforms | Rating impact | Competitor gap | Recommended action`.
4. **Theme evidence** - 2-4 short excerpts per P0/P1 theme with app, platform, rating, date, and version.
5. **Competitor gaps** - features or promises competitors have that the target app reviews complain about.
6. **Release watch** - new or spiking issues in the selected recent window.
7. **Caveats** - missing platforms, missing countries, incomplete schemas, or low review volume.

Never claim statistical certainty from small samples. Label results from fewer than 50 reviews as directional.

## Cost and safety guardrails

- Confirm before scraping more than 5 apps, more than 5 countries, or more than 5,000 reviews per app.
- Avoid iOS `country: "all"` unless the user explicitly wants multi-market coverage; it multiplies work across many countries.
- Start with `maxReviews: 200` for a smoke test when the app ID is uncertain.
- For Google Play, use `recentDays` instead of fetching all history when the user asks about a launch or release.
- For iOS, use `timePeriod` such as `7d`, `30d`, or `90d` for recent analysis.
- Check each Actor pricing tab before quoting exact costs.

## Troubleshooting

- **App not found** - Re-run Google Search with developer name and store-specific query, then verify title and developer manually.
- **Wrong app matched** - Compare developer name, icon, category, and store URL before running review Actors.
- **iOS proxy failure** - The Apple Actor may require an Apify proxy group on some plans. Try one country first and report the run error if it fails.
- **Google Play returns zero reviews** - Check `appIdOrUrl`, switch `sortBy` to `newest`, remove keyword filters, and lower `recentDays` constraints.
- **Dataset too large** - Fetch only needed fields with `apify datasets get-items DATASET_ID --format json` and summarize in batches.
- **Conflicting signals** - Separate platform-specific issues instead of averaging them away.
