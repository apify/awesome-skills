# Module: n8n template scout

Run from Step 7 of [SKILL.md](../SKILL.md). It looks at what n8n users build around the niche, using the top-MAU competitor (or the idea itself) as the reference, and labels each relevant template with an action:

1. **Marketing replica:** solves the same problem without Apify. Swap in the planned Actor, or use it as a launch-post angle.
2. **Actor power-up:** a scraper plus an LLM step and nothing else. That LLM step belongs inside the planned Actor.
3. **MCP-connector integration:** a scraper plus a service that Apify MCP connectors support. The Actor plus a connector covers the same workflow with no n8n.
4. **Other / mixed:** listed for reference.

Output: `~/apify-reports/<reference-actor-slug>-n8n-scout.md`. Use the template in [report-templates.md](report-templates.md#n8n-scout).

## N1 — Inputs

- **Reference:** the top-MAU competitor's README (`apify actors info "OWNER/ACTOR" --readme --user-agent apify-awesome-skills/apify-actor-idea-validator`), or the idea description if there's no competitor.
- **Competitor scrapers:** ask whether templates built on non-Apify scrapers should count as power-up / MCP candidates, flagged ⚠️ *Conversion needed*. The default is yes. The tracked list is in the [competitor table](#competitor-scrapers). Accept extra names for this run only.

## N2 — Keywords and adjacent terms

- **`keywords`:** 6–12 sharp terms, covering the platform name, platform + data type, output type, and common verbs (scrape, monitor, enrich). Skip generic noise ("data", "api", "automation"). When competitors are opted in, append their names after the Actor-specific terms.
- **`adjacentTerms`:** 4–8 words a template with the same job to be done would use even without naming the platform. For Quora, that's "Q&A", "questions", "forum", "community", "reddit", "answers". For XING, it's "job listings", "hiring signals", "recruiting", "DACH". Write them into the report header.

## N3 — Search the n8n library

```bash
apify actors call advantageous_subcontra/n8n-template-scraper \
  --input '{"keywords": ["quora", "quora answers", "forum questions"], "maxResultsPerKeyword": 20, "sort": "popularity", "includeWorkflowJson": true}' \
  --user-agent apify-awesome-skills/apify-actor-idea-validator \
  --json 2>/dev/null
```

The dataset is large (about 2 MB for 150 templates). Fetch `id,name,views,matchedKeywords` first, then pull node lists only for the shortlist:

```bash
curl -s "https://api.n8n.io/api/templates/workflows/TEMPLATE_ID"
```

Read `workflow.workflow.nodes[].type` (or `workflow.nodes[].type`).

## N4 — Relevance filter (before ranking by views)

Competitor-name keywords return each competitor's most popular templates, whatever the topic. In one run, 125 of 132 results were off-topic. Short names also match inside other words ("Exa" in "example" or "ExactBuyer", "xing" in "processing" or "mixing").

Keep a template only if at least one of these holds:
- an **Actor-specific keyword** matched it, as a whole word rather than a substring, or
- its title or description mentions the target platform or an `adjacentTerms` entry.

Then drop templates with fewer than 100 views and keep the top 10 by views.

**Empty niche:** if no template mentions the platform, put that in a **Key finding** section at the top. An empty niche on n8n is itself a signal, pointing to a replica opportunity and low ecosystem competition. In that case, also list any platform-specific templates under the view cutoff, because they're the only direct evidence.

## N5 — Classify (first match wins)

Classify by node `type`, not the display name. Ignore infrastructure nodes: triggers (`manualTrigger`, `scheduleTrigger`, `webhook`, `formTrigger`), control flow (`if`, `switch`, `merge`, `splitInBatches`, `splitOut`, `aggregate`, `filter`, `wait`), data shaping (`set`, `code`, `function`, `html`), and `stickyNote`.

- **Scraper node:**
  - the native `n8n-nodes-base.apify` node, or a title or description saying "with Apify"
  - when competitors are opted in, a competitor node, `httpRequest`, or a title naming a competitor
- **LLM node:** `openAi`, `anthropic`, `gemini`, `mistral`, `ollama`, `cohere`, `deepseek`, `groq`, `openRouter`, any `@n8n/n8n-nodes-langchain.lmChat*`, `agent`, `chainLlm`, `informationExtractor`, `sentimentAnalysis` or `textClassifier`.
- **MCP-connector services:** Notion, Slack, GitHub, Sentry, Supabase. Check [docs.apify.com/integrations/mcp-connectors](https://docs.apify.com/integrations/mcp-connectors) for additions. Google Sheets, Gmail, Airtable and CRMs are **not** connectors yet, so they go to Other / mixed.

| # | Bucket | Rule |
|---|---|---|
| 1 | MCP-connector integration | ≥1 scraper node AND ≥1 MCP-connector service |
| 2 | Actor power-up | ≥1 scraper node AND every other non-infrastructure node is an LLM |
| 3 | Marketing replica | 0 scraper nodes |
| 4 | Other / mixed | everything else |

Templates that reach bucket 1 or 2 through a competitor scraper carry `⚠️ Conversion needed`, naming the competitor and the Apify Actor to swap in.

Even when no template fits bucket 2 strictly, report the **LLM steps users add after scraping**: classification, pain points, sentiment, lead scoring, pitch writing. Those are the power-up signal for the planned Actor.

## Competitor scrapers

| Competitor | Typical n8n signal | Generic Apify swap-in |
|---|---|---|
| Firecrawl | `@mendable/n8n-nodes-firecrawl.firecrawl`, `httpRequest` to `api.firecrawl.dev` | `apify/website-content-crawler` |
| Bright Data | `brightData` node, `httpRequest` to brightdata.com, Bright Data MCP client | A platform-specific Actor, else `apify/web-scraper` |
| Exa | `httpRequest` to `api.exa.ai` | `apify/google-search-scraper` + `apify/website-content-crawler` |
| Airtop | `airtop` node | `apify/puppeteer-scraper` |
| ScrapingBee | `httpRequest` to scrapingbee.com | `apify/web-scraper` |
| Dumpling AI | `httpRequest` to dumplingai.com | `apify/website-content-crawler` |
| Phantombuster | `phantombuster` node | A platform-specific Actor |

For the planned idea, the swap-in is usually **the planned Actor itself**. Say so in the report.
