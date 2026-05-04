---
name: portfolio-sweep
description: >
  Run a comprehensive data sweep across all portfolio companies using all three skills
  (apify-public-registries, apify-financial-news, apify-financial-osint).
  Use when user asks for "full portfolio scan", "weekly sweep", "complete data pull",
  "portfolio report", or "executive briefing".
argument-hint: "[1d|7d|1y]  (default: 7d)"
arguments: [window]
allowed-tools:
  - Bash(python3 *)
  - Bash(node *)
  - Read
  - Skill
disable-model-invocation: true
---

# Portfolio Sweep

## Time window

!`python3 -c "
import datetime, sys
w = '$window' if '$window' else '7d'
if w not in ('1d', '7d', '1y'):
    print(f'ERROR: invalid window \"{w}\". Use 1d, 7d, or 1y.')
    sys.exit(1)

end = datetime.date.today()
days_map = {'1d': 1, '7d': 7, '1y': 365}
days = days_map[w]
start = end - datetime.timedelta(days=days)

gnews_map = {'1d': '1d', '7d': '7d', '1y': '1y'}
reddit_map = {'1d': 'day', '7d': 'week', '1y': 'year'}

print(f'''SCAN_SINCE={start.isoformat()}
SCAN_UNTIL={end.isoformat()}
SCAN_DAYS={days}
SCAN_WINDOW={w}
GNEWS_TIMEFRAME={gnews_map[w]}
REDDIT_TIMEFRAME={reddit_map[w]}
REDDIT_DATE_FROM={start.isoformat()}
REDDIT_DATE_TO={end.isoformat()}
TWITTER_SINCE={start.isoformat()}_00:00:00_UTC
TWITTER_UNTIL={end.isoformat()}_23:59:59_UTC
TRUSTPILOT_FILTER_AFTER={start.isoformat()}''')
"
`

Use the computed values above as time parameters when invoking skills below.
Override the default timeframes in each skill with the values above.

## Phase 1: Registry

Invoke /financial-services-plugin:apify-public-registries and run a full portfolio batch:
- Batch fetch all countries with scripts and identifiers (CZ, SK, PL, EU, ESG, RO)
- DE and UK keyword lookup via Apify fallback
- Cross-reference EU GLEIF for companies missing LEI
- Save output as JSON to output/ per-country
- Print summary table: company | country | sources OK | sources FAIL | missing identifiers

## Phase 2: News Intelligence

Invoke /financial-services-plugin:apify-financial-news and run a portfolio scan:
- Google News timeframe=GNEWS_TIMEFRAME
- Follow the skill's 2-phase discovery, dedup, routing, extraction, and cleanup pipeline exactly
- Use only actors listed in the skill's "Allowed Apify Actors" table -- do NOT substitute
- Add macro context (ING Think, IMF) per skill instructions
- Output: Tier 1 + Tier 2 table per company

## Phase 3: OSINT Social Listening

Invoke /financial-services-plugin:apify-financial-osint and run a portfolio sweep:
- Follow the skill's per-company routing from data/osint-targets.json
- Override timeframes: Reddit timeframe=REDDIT_TIMEFRAME dateFrom=REDDIT_DATE_FROM dateTo=REDDIT_DATE_TO, Twitter since=TWITTER_SINCE until=TWITTER_UNTIL
- Trustpilot: limit=50, post-filter date >= TRUSTPILOT_FILTER_AFTER
- Skip actors where company has no presence (per osint-targets.json routing)
- Output: sentiment summary + top posts/tweets/reviews per company

## Executive report

After all three phases, produce a summary report:
- Time window: SCAN_SINCE to SCAN_UNTIL (SCAN_WINDOW)
- Companies processed per phase
- Top 5 most important cross-phase findings
- Missing data / failed sources
