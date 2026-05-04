# Morning Note Detail — Reference

Detailed morning note formatting, output schemas, and guidelines.
Referenced from SKILL.md — load when producing portfolio morning briefing.

## HTML Newsletter Format

Use Design System (see `../design-system/`):

- Navy header with brand logo
- Dark title bar with date and "Top Call" highlight
- Collapsible company sections with logos and Portfolio/Competitor badges
- Copper accents for action items and trade ideas
- Separate Tier 1 / Tier 2 sections
- Fonts: Neue Haas Unica W1G (body), PPFDisplay (headings)
- Reference template: `News_Intelligence_Report_2026-03-20.html` in project root

## JSON Output Schema

For downstream processing, output structured JSON:

```json
{
  "morning_note": {
    "date": "2026-03-20",
    "top_call": {
      "headline": "...",
      "company": "InPost",
      "event_type": "earnings",
      "take": "...",
      "action": "Review PT"
    },
    "companies": [
      {
        "name": "InPost",
        "event_type": "earnings",
        "summary": "...",
        "take": "...",
        "action": "Review PT",
        "source": "bloomberg.com",
        "date": "2026-03-19"
      }
    ],
    "competitors": [...],
    "market_context": "...",
    "key_events_today": [...],
    "trade_ideas": [
      {
        "direction": "Long",
        "company": "InPost",
        "thesis": "...",
        "catalyst": "...",
        "risk": "..."
      }
    ],
    "no_material_news": ["Air Bank", "PPF Real Estate"]
  },
  "tier1": {
    "sources_queried": 8,
    "articles_found": 5,
    "articles": [
      {
        "tier": "verified",
        "title": "...",
        "source": "bloomberg.com",
        "author": "...",
        "published_date": "2026-03-19T14:17:09Z",
        "url": "...",
        "text_chars": 7577,
        "text_preview": "First 200 chars...",
        "discovery_method": "google_news_site",
        "extraction_actor": "jamie_tran/bloomberg-article-scraper",
        "extraction_cost": 0.02
      }
    ]
  },
  "tier2": {
    "articles_found": 3,
    "articles": [
      {
        "tier": "broad",
        "title": "...",
        "source": "seekingalpha.com",
        "url": "...",
        "text_chars": 1200,
        "extraction_actor": "apify/rag-web-browser",
        "extraction_cost": 0.005,
        "quality_warning": null
      }
    ]
  },
  "total_extraction_cost": 0.15
}
```

## Earnings Analysis Template

When a portfolio company reports earnings, include this table:

| Metric | Consensus | Actual | Beat/Miss |
|--------|-----------|--------|-----------|
| Revenue | | | |
| EPS | | | |
| [Key sector metric] | | | |
| FY Guidance | | | |

Our Take: [Is this a beat or miss that matters? Quality of earnings? Guidance trajectory?]
Action: [Maintain rating / Review PT / Flag for deep dive]

## M&A Event Analysis Template

For M&A events, assess:
- Deal terms (premium to undisturbed price, structure, conditionality)
- Strategic fit for portfolio
- Probability of completion (regulatory, financing, shareholder approval)
- Impact on related portfolio companies

## Important Notes

- **Be opinionated** — notes without a view are useless. If no view can be formed, state "insufficient data to form view, monitoring"
- **Lead with the most important thing** — Top Call is #1, do not bury the headline
- **"No news" is valid** — "Nothing material overnight across [N] portfolio companies. Maintaining positioning."
- **Distinguish signal from noise** — a minor analyst note is not the same as an earnings miss. Use priority classification.
- **Time-stamp takes** — if writing at 6am, note that pre-market may change by open
- **Own mistakes** — if yesterday's take was wrong, acknowledge it. Credibility > being right every time.
- **Competitor context matters** — a competitor's earnings miss can be bullish for portfolio company
- **Don't over-extract** — for morning note, extract only material articles (typically 3–10 per run). Skip general coverage unless slow news day.