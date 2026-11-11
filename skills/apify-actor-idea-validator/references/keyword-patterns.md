# Keyword patterns

Pick variants that match the idea. Always keep the four base keywords. Total ≤ 15. Keep each keyword 2–4 words — full questions return no volume.

`<brand>` = how people name the site (`zillow`, `google maps`, `linkedin`). `<data>` = the extracted data type in plain words (`reviews`, `listings`, `jobs`, `profiles`, `products`, `prices`).

## Base (always)

- `<brand> scraper`
- `<brand> api`
- `<brand> mcp`
- `<brand> data`

## By data type

| Pattern | Example |
|---|---|
| `<brand> <data> scraper` | `zillow listings scraper` |
| `<brand> <data> api` | `google maps reviews api` |
| `scrape <brand> <data>` | `scrape linkedin jobs` |
| `scrape <brand>` | `scrape zillow` |
| `<brand> <data> export` / `export <brand> <data>` | `export google reviews` |
| `<brand> <data> download` | `instagram followers download` |
| `<brand> dataset` | `amazon dataset` |

## By Actor type

| Actor type | Extra patterns |
|---|---|
| Scraper | `<brand> crawler`, `<brand> data extraction`, `<brand> scraper python` |
| API wrapper | `<brand> api alternative`, `<brand> unofficial api`, `<brand> api pricing`, `<brand> api free` |
| MCP server | `<brand> mcp server`, `<brand> ai agent`, `<brand> claude` |
| Enrichment / leads | `<brand> leads`, `<brand> email finder`, `<brand> contact data` |
| Monitoring / tracking | `<brand> price tracker`, `<brand> monitor`, `<brand> alerts` |
| Analytics | `<brand> analytics`, `<brand> statistics`, `<brand> insights` |

## By audience (only when the description names one)

- Sales / lead gen → `<brand> leads`, `<brand> b2b data`
- E-commerce → `<brand> price monitoring`, `<brand> product data`
- Real estate → `<brand> property data`, `<brand> listings data`
- Recruiting → `<brand> job data`, `<brand> candidate search`
- SEO / marketing → `<brand> keyword data`, `<brand> rank tracker`

## Reading the results

- **High volume on `scraper` / `scrape …`** — classic Apify buyer; a scraper Actor fits.
- **High volume or CPC on `api` / `api alternative`** — people want programmatic access; a clean API mode (Standby / server Actor) is a differentiator.
- **Any volume on `mcp`** — early AI-agent demand; an MCP mode can be a differentiator even if the scraper niche is crowded.
- **High CPC on `data` / `dataset`** — buyers with budget; consider dataset-style output, scheduling, deltas.
- **0 volume everywhere but site traffic is high** — demand may come through Apify Store search and integrations rather than Google; say so rather than reading it as zero demand.
