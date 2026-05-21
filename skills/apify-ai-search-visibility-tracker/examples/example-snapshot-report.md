# AI Visibility Snapshot -- 2026-05-20

- Run ID: `a1B2c3D4e5F6g7H8` ([console](https://console.apify.com/actors/runs/a1B2c3D4e5F6g7H8))
- Prompt: "How to get data from ExampleSite.com"
- Sources enabled: ai_overviews, ai_mode, chatgpt, perplexity, copilot, gemini
- Entities: Acme, Contoso, Northwind
- Prior runs compared against: **3**
- Verbosity: `include_full_answers = on_demand`

## Summary

- **First-ever citations today:** 1
  - copilot / "How to get data from ExampleSite.com" -> **Acme**
- **First-ever mentions today:** 1
  - perplexity / "How to get data from ExampleSite.com" -> **Northwind**
- **Drops today:** 1
  - ai_mode / "How to get data from ExampleSite.com" -> **Contoso**

## Per-entity scorecards

### Acme (brand)

| Source | Cited | Mentioned | SoV% | Matched URLs | History |
|--------|-------|-----------|------|--------------|---------|
| ai_overviews | no  | no  | 0.0  | -- | cited 0/3 prior runs |
| ai_mode      | no  | no  | 0.0  | -- | cited 0/3 prior runs |
| chatgpt      | no  | no  | 0.0  | -- | cited 0/3 prior runs |
| perplexity   | no  | no  | 0.0  | -- | cited 0/3 prior runs |
| copilot      | yes | yes | 25.0 | https://blog.acme.com/crawling-examplesite-47511a59eef/ | cited 0/3 prior runs (first-ever cited) |
| gemini       | no  | yes | 0.0  | -- | cited 0/3 prior runs |

Acme is **cited** in copilot (https://blog.acme.com/crawling-examplesite-47511a59eef/); **mentioned by name** in copilot ("Use a scraping API (Northwind, Fabrikam, Acme)") and gemini ("Acme (ExampleSite.com Actor): Acme features ready-made cloud scrapers").

### Contoso (competitor)

| Source | Cited | Mentioned | SoV% | Matched URLs | History |
|--------|-------|-----------|------|--------------|---------|
| ai_overviews | no | no | 0.0 | -- | cited 0/3 prior runs |
| ai_mode      | no | no | 0.0 | -- | cited 2/3 prior runs (dropped vs last) |
| chatgpt      | no | no | 0.0 | -- | cited 0/3 prior runs |
| perplexity   | no | no | 0.0 | -- | cited 0/3 prior runs |
| copilot      | no | no | 0.0 | -- | cited 0/3 prior runs |
| gemini       | no | no | 0.0 | -- | cited 0/3 prior runs |

Contoso has zero citations and zero mentions across all enabled sources.

### Northwind (competitor)

| Source | Cited | Mentioned | SoV% | Matched URLs | History |
|--------|-------|-----------|------|--------------|---------|
| ai_overviews | no  | no  | 0.0  | -- | cited 0/3 prior runs |
| ai_mode      | yes | no  | 8.3  | https://www.northwind.com/blog/example-site-data/ | cited 2/3 prior runs |
| chatgpt      | no  | no  | 0.0  | -- | cited 1/3 prior runs |
| perplexity   | yes | yes | 11.1 | https://www.northwind.com/blog/example-site-data/ | cited 1/3 prior runs (first-ever mentioned) |
| copilot      | yes | yes | 25.0 | https://www.northwind.com/blog/how-to-pull-examplesite/ | cited 1/3 prior runs |
| gemini       | yes | yes | 7.1  | https://www.northwind.com/blog/example-site-data/ | cited 2/3 prior runs |

Northwind is **cited** in ai_mode, perplexity, copilot, gemini; **mentioned by name** in perplexity ("Scraping frameworks like Northwind or Fabrikam"), copilot ("Use a scraping API (Northwind, Fabrikam, Acme)"), and gemini ("web scraping APIs (like Fabrikam or Northwind)").

## Top 10 most-cited URLs (this run)

### ai_mode
- (1x) https://developers.examplesite.com/demand
- (1x) https://www.northwind.com/blog/example-site-data/
- (1x) https://tailspin.com/examplesite-scraper/
- [...]

[... one top-10 per source, see the runner's actual output ...]
