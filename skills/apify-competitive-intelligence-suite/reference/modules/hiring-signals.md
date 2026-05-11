# Hiring Signal Analysis

**When to use**: Infer competitor's strategic direction from hiring patterns.

## Data Gathering

```
# 1: LinkedIn job listings (requires search URL, NOT keywords)
call-actor: curious_coder/linkedin-jobs-scraper
  input: {
    "urls": ["https://www.linkedin.com/jobs/search/?keywords=[competitor]&position=1&pageNum=0"],
    "count": 50, "scrapeCompany": true
  }

# 2: Fallback — careers page
call-actor: apify/website-content-crawler
  input: {
    "startUrls": [{"url": "[competitor-url]/careers"}],
    "maxCrawlPages": 3,
    "proxyConfiguration": {"useApifyProxy": true}
  }

# 3: Glassdoor — culture, salaries, internal signals
call-actor: memo23/glassdoor-scraper-ppr

# 4: Recent hiring news
call-actor: apify/google-search-scraper
  input: { "queries": "[competitor] hiring jobs careers [current-year]\n[competitor] layoffs OR expansion [previous-year] [current-year]" }
```

**0 LinkedIn results = signal** (not hiring aggressively). Glassdoor compensates — reviews reveal culture/strategy even without active hiring.

## Analysis

Categorize roles by department. Hiring velocity (scaling/stable/contracting). Technology signals from JDs. Geographic expansion. Seniority mix: hiring leaders = new initiative, hiring ICs = scaling existing.
