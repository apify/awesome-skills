# Apify competitor scrapers in n8n

**Opt-in.** The skill asks the user at step 2.5 whether to include competitors. When opted in, templates that use any of these services are **not** pure replicas — they're already doing a scrape step, so if the rest of the workflow fits the **Actor power-up** or **MCP-connector integration** shape, promote them into those buckets with a ⚠️ `conversion needed` flag that names the competitor and a candidate Apify Actor to swap in. When opted out, they stay in Replicas like any other non-Apify scrape.

The user may also supply **extras** at step 2.5 — one-off names for a single run (e.g. "Scrapfly, Decodo"). Treat them exactly like the tracked list for that scout. Do **not** silently edit this file; if an extra produces hits worth keeping, the chat summary should suggest the user add it here permanently.

Last checked: 2026-10-29. Add new competitors here as they appear in templates.

| Competitor | n8n node `name` patterns to match | What they do | Apify equivalent to pitch |
|------------|-----------------------------------|--------------|---------------------------|
| Firecrawl | `n8n-nodes-base.httpRequest` with `parameters.url` matching `api.firecrawl.dev`; community `firecrawl` nodes | Hosted scraping API with LLM-friendly output. | `apify/website-content-crawler` for crawl + Markdown output; `apify/web-scraper` for custom extraction. |
| Bright Data | `n8n-nodes-base.brightData`, `n8n-nodes-base.httpRequest` to `brightdata.com` endpoints | Proxy network + dataset marketplace. | `apify/web-scraper` + residential proxy group; for specific datasets (Glassdoor, Google Shopping, etc.) a dedicated Apify Actor usually exists. |
| Exa | `n8n-nodes-base.httpRequest` to `api.exa.ai`; community `exa` nodes | AI-powered web search with content extraction. | `apify/google-search-scraper` + `apify/website-content-crawler` chain; or a dedicated AI-search Actor if present. |
| Airtop | `n8n-nodes-base.airtop` | Browser-automation API with LLM extraction. | `apify/web-scraper` or `apify/puppeteer-scraper` for browser-driven workflows. |
| ScrapingBee | `n8n-nodes-base.httpRequest` to `app.scrapingbee.com` or `api.scrapingbee.com` | Hosted scraping API, JS rendering. | `apify/web-scraper` for custom targets; `apify/website-content-crawler` for site-wide crawls. |
| Dumpling AI | `n8n-nodes-base.httpRequest` to `app.dumplingai.com` | LLM-friendly content/product scraping. | `apify/website-content-crawler` for pages; a product-specific Actor from the Apify Store when the use case is e-commerce (search before pitching an Actor ID). |
| Phantombuster | `n8n-nodes-base.phantombuster` | Growth-automation + social scraping. | A platform-specific Apify Actor (e.g. `apify/instagram-profile-scraper` for Instagram; search the Store for LinkedIn, Twitter, etc.). |

## How to pick the Apify equivalent

Prefer, in order:

1. A platform-specific Apify Actor from the [Apify Store](https://apify.com/store) when the competitor was used against a single named platform. Verify the exact Actor ID exists before putting it in the report — Store ownership shifts and names you remember may now live under a community author. `apify/instagram-profile-scraper` is confirmed as of 2026-10-29; others (LinkedIn, Amazon, YouTube, Google Maps) are owned by community authors — search the Store for the current best one and quote it with its real username.
2. `apify/website-content-crawler` when the use case is "give me the page as clean Markdown" (RAG, docs, blog audits).
3. `apify/web-scraper` or `apify/puppeteer-scraper` for custom extraction.

If none of the above fits, say so in the report — not every competitor template has a one-shot swap-in.

## Conversion-needed flag

Templates promoted into bucket 2 or 3 via this file must carry:

- A `⚠️ Conversion needed` marker.
- The specific competitor service(s) that would need replacing.
- The Apify Actor you'd pitch as the swap-in (one of the three options above, by name).

That extra line is what distinguishes a "clean" power-up / MCP integration (just add our connector) from one where the user has to rebuild the scrape step first.
