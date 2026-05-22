# Review Intelligence

**When to use**: Understand customer sentiment, competitor pain points, or exploitable gaps.

## SERP Snippet Mining (Always Start Here)

SERP results for review sites contain `averageRating`, `numberOfReviews`, and pros/cons snippets — fast triage before full scraping.

```
call-actor: apify/google-search-scraper
  input: { "queries": "[company] review pros cons site:g2.com\n[company] review site:capterra.com\n[company] vs [rival] review", "maxPagesPerQuery": 1 }
```

## Full Review Scraping

Use **dedicated actors only** — review sites block generic scrapers.

```
# Structured reviews (if applicable)
call-actor: automation-lab/g2-scraper
call-actor: zen-studio/capterra-reviews-scraper
# Gartner: no working actor — use SERP snippet mining above as fallback

# Unfiltered community sentiment (if applicable)
call-actor: harshmaur/reddit-scraper

# Product/location reviews (if applicable)
call-actor: compass/Google-Maps-Reviews-Scraper
call-actor: web_wanderer/amazon-reviews-extractor
call-actor: neatrat/google-play-store-reviews-scraper
call-actor: jdtpnjtp/apple-app-store-scraper
```

## Analysis

Categorize sentiment. Extract top praised features, top complaints, feature requests. Identify switching signals ("switched from X", "better than Y"). Complaints = positioning opportunity.
