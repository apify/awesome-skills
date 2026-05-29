# Actor index — apify-tech-stack-prospecting

Comprehensive Actor routing table for the three-stage discovery → contact → enrichment pipeline.

| Stage | User intent | Actor ID | Tier | Notes |
|-------|-------------|----------|------|-------|
| Discovery | Find companies via tech/hiring signal queries | `apify/google-search-scraper` | apify | Core discovery step; returns organic SERP results. Use `resultsPerPage: 25–50`, `maxPagesPerQuery: 1–2`. PAY_PER_EVENT (per result page). |
| Contact | Extract emails, phones, and social links from company websites | `vdrmota/contact-info-scraper` | community | Crawls `/about`, `/contact`, `/team` at depth 2. Set `maxDepth: 2` and `maxPagesPerCrawl: 20` to bound cost. PAY_PER_EVENT (per page crawled). |
| Enrichment | Add company name, industry, headcount, HQ from LinkedIn | `apify/linkedin-companies-scraper` | apify | Input: `companyUrls` array of LinkedIn company page URLs (not profile URLs). PAY_PER_EVENT (per company). Cap batches at 30 to avoid blocks. |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Signal query construction

The discovery stage quality depends entirely on the queries. Use the templates from `SKILL.md`; key rules:

- Combine a **tech signal** ("uses Rails", "built with Next.js") with an **intent qualifier** ("hiring", "engineering blog", "GitHub") to filter out tutorial sites.
- Use `site:` restrictions only when precision matters more than volume — they significantly reduce result count.
- 3–5 queries per technology signal, 25–50 results each, is the cost-efficient default before committing to broader sweeps.

## How to inspect Actor schemas

```bash
# Fetch input schema for any Actor
apify actors info "ACTOR_ID" --input --json \
  --user-agent apify-awesome-skills/apify-tech-stack-prospecting 2>/dev/null

# Search for alternative Actors if a tier-1 choice is unavailable
apify actors search "contact scraper email" --json --limit 10 2>/dev/null
```

## Alternative Actors

If `vdrmota/contact-info-scraper` is unavailable or underperforms on a target domain:

| Alternative | Actor ID | When to prefer |
|-------------|----------|----------------|
| General site crawler with email extraction | `apify/website-content-crawler` | When contact pages are JavaScript-rendered |
| Email extractor only | `apify/email-address-scraper` | Faster when you only need emails, no phones |
