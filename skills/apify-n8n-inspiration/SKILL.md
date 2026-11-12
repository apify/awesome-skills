---
name: apify-n8n-inspiration
description: Scout the n8n community template library (n8n.io/workflows) for workflows that overlap with a given Apify Actor and classify each hit as a marketing-replication candidate, an Actor power-up opportunity, or an MCP-connector integration opportunity. Use when the user shares an Apify Actor URL (apify.com/<user>/<actor>) and asks about n8n ecosystem research, template discovery, marketing adjacency, or roadmap input inspired by what n8n users build around similar Actors. Triggers "find n8n templates for Actor X", "scout the n8n library for X", "cross-reference this Actor with n8n", "n8n power-up ideas for this Actor", and any request pairing an Apify Actor identifier with n8n discovery, competitive analysis, or product-marketing input. Also surfaces convertible opportunities that use Apify competitors (Firecrawl, Bright Data, Exa, Airtop, ScrapingBee, Dumpling AI, Phantombuster), opt-in per run. Requires Apify CLI or Apify MCP server.
author: Fabian Maume
author_url: https://github.com/fmaume
metadata:
  category: actor-development
  keywords: "n8n, n8n-templates, apify-actor, actor-marketing, actor-power-up, mcp-connector, template-scout, ecosystem-research, competitive-intelligence, firecrawl, bright-data, exa, product-marketing, roadmap-input"
---

# Apify ↔ n8n inspiration

Given an Apify Actor URL, surface the n8n community templates most worth paying attention to and label each one with the action an Apify PM / developer-marketer / Actor developer should take.

The three labels are:

1. **Marketing replica** — the template solves a problem close to what the Actor does, but doesn't use any Apify node (or an opted-in competitor). Candidate for a replica blog post / template submission that swaps in the input Actor.
2. **Actor power-up** — the template is just a scraper node + an LLM step (OpenAI, Anthropic, Gemini, Mistral, Ollama, …). Signal that the LLM step belongs inside the Actor itself (e.g. as output post-processing, enrichment, or summarization).
3. **MCP-connector integration** — the template chains the scraper with one or more services that Apify's MCP connectors already support ([references/apify-mcp-connectors.md](references/apify-mcp-connectors.md)). Signal that wiring the Actor with those services via the MCP connector would unlock the same workflow with no n8n needed.

Opt-in competitor rule: when the user accepts at step 2.5, templates built on an Apify competitor scraper also qualify for Power-up / MCP buckets, with a ⚠️ `Conversion needed` tag that names the competitor and the Apify Actor to swap in. Opt-out and competitors stay in Replicas.

Templates that fit none of these buckets are listed in an "Other / mixed" section so the user can still see what's out there without being pushed to act.

## Example prompts

Prompts this skill handles:

- "Find n8n templates relevant to apify/website-content-crawler — what marketing opportunities are there?"
- "Which n8n workflows mention apify/instagram-profile-scraper and what should I do about them?"
- "Scout the n8n library for apify/google-search-scraper and tell me which templates would be good power-ups."

Out of scope (the boundary):

- "Prepare an n8n workflow JSON for submission to the Creator Hub" — that's the `prepare-n8n-template` skill, not this one.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Calling Actors — choose your interface

Pick the interface that fits the runtime. Cross-tool compatibility is the skill's responsibility.

### Option A: Apify CLI (recommended for portability)

Three flags on every call: `--user-agent apify-awesome-skills/apify-n8n-inspiration`, `--json`, `2>/dev/null`.

```bash
# Fetch an Actor's title + readme (text output, no JSON suppression)
apify actors info "apify/website-content-crawler" --readme \
  --user-agent apify-awesome-skills/apify-n8n-inspiration 2>/dev/null

# Run the n8n template scraper
apify actors call "advantageous_subcontra/n8n-template-scraper" \
  -i '{"keywords":["<kw1>","<kw2>"],"maxResultsPerKeyword":20,"sort":"popularity","includeWorkflowJson":true}' \
  --user-agent apify-awesome-skills/apify-n8n-inspiration \
  --json 2>/dev/null

# Fetch dataset items (replace DATASET_ID with the id returned by the call)
apify datasets get-items DATASET_ID \
  --user-agent apify-awesome-skills/apify-n8n-inspiration \
  --format json 2>/dev/null > /tmp/n8n_templates.json
```

### Option B: Apify MCP server

If the Apify MCP server is connected and the CLI isn't available, use the MCP tools directly: `fetch-actor-details` (readme), `call-actor` (run the n8n scraper), `get-dataset-items` (fetch the dataset).

## Inputs the skill needs before it runs

- **The Actor URL or full name.** Accept both `https://apify.com/apify/website-content-crawler` and `apify/website-content-crawler`. If the user drops just a title ("website content crawler"), ask once for the URL — guessing the username is unsafe.
- **Competitor-inclusion decision.** Opt-in, asked explicitly. See step 2.5 below. The user picks whether templates that use Apify competitors (Firecrawl, Bright Data, Exa, …) count as Power-up / MCP candidates (with a ⚠️ `Conversion needed` flag) or just as regular Replicas.

Keywords, template cutoffs, and ranking are all derived automatically from those two inputs.

## The workflow

Run these steps in order. The analysis step depends on `includeWorkflowJson: true` and on the keyword list from the readme, so don't skip ahead.

### 1. Parse the Actor URL

Pull `<username>/<name>` out of the input:

- `https://apify.com/apify/website-content-crawler` → `apify/website-content-crawler`
- `apify.com/apify/website-content-crawler/` → `apify/website-content-crawler`
- `apify/website-content-crawler` → `apify/website-content-crawler`

Keep both the full name (for the fetch call) and the short slug (`website-content-crawler`) handy — the slug is one of the keywords you'll feed the scraper in step 3.

### 2. Fetch the Actor's title and readme

Use the CLI (or the MCP equivalent). Keep in context:

- The Actor's human-readable title ("Website Content Crawler"). This is the exact string most n8n template authors reference.
- The readme prose. This is what you extract keywords from.
- The Actor's categories (if available). Useful signal when picking keywords (e.g. "SOCIAL_MEDIA" → add "instagram", "tiktok" if the Actor's about social).

### 2.5. Ask whether to include Apify competitors

Before touching the n8n API, ask the user whether templates that use Apify competitor scrapers should be promoted into the Power-up / MCP buckets (with a ⚠️ `Conversion needed` flag) or left in Replicas. Ask explicitly so the choice is recorded:

- **Yes, include tracked competitors.** Promote competitor-driven templates into Power-up / MCP where their shape fits. Tracked list (from [references/competitor-scrapers.md](references/competitor-scrapers.md), re-read every run): **Firecrawl, Bright Data, Exa, Airtop, ScrapingBee, Dumpling AI, Phantombuster**. Each gets a `⚠️ Conversion needed` tag that names the Apify Actor to swap in.
- **Yes, plus extra competitors (free-text).** Same as above, plus a user-supplied list (e.g. "Scrapfly, Decodo, Oxylabs"). Treat the extras exactly like the tracked ones for this run only — do not silently edit the reference file. If the extras look worth keeping, tell the user at the end of the report they can add them permanently to `references/competitor-scrapers.md`.
- **No, competitors stay in Replicas.** Pre-opt-in default behavior: a competitor scraper counts as "no scraper node" for bucket matching, so these templates land in Replica.

Phrase the question like this:

> Include Apify competitor scrapers (Firecrawl, Bright Data, Exa, Airtop, ScrapingBee, Dumpling AI, Phantombuster) as potential Power-up / MCP candidates in this scout? Opting in flags each with ⚠️ Conversion needed and names the Apify Actor to swap in. You can also add extras (one-off, not saved).

Record the choice and any extras as `competitorsIncluded` (bool), `competitorList` (array), and `userExtras` (array) — they feed the keyword step (adding competitor names as search terms when opted in) and the classification step (gating the competitor rules).

If the user doesn't answer or says "default", pick **Yes, include tracked competitors** — most scouts benefit from the extra signal, and the flag makes the trade-off visible in the report.

### 3. Extract 5–20 keywords from the readme

Read the readme and pull a de-duplicated list of **5 to 20 search keywords** that an n8n template author might realistically use to describe a workflow built around this Actor. Good keyword candidates:

- The Actor's slug and human title (always include both).
- The main domain / data source the Actor targets ("linkedin", "amazon", "google maps", "youtube", "shopify").
- The output type ("reviews", "contacts", "product data", "sentiment").
- Common verbs paired with the Actor ("scrape", "monitor", "enrich", "crawl").
- Any product / platform name the readme repeats three or more times.

Skip generic noise ("data", "api", "automation", "workflow"). Those return everything and nothing. Also skip generic LLM-shape terms (`chatbot`, `RAG`, `knowledge base`, `vector database`, `pinecone`, `qdrant`) **unless they appear in the Actor's own name** — they flood the pool with unrelated chatbot templates.

Store the list as `keywords`. Fewer, sharper keywords beat a long bland list — err toward 8–12.

**If `competitorsIncluded` is true, also append each name from `competitorList` + `userExtras` to `keywords`.** This is how the scraper finds competitor-driven templates in the first place — without those terms, the n8n search misses most of them. Keep the Actor-specific keywords first so view ranking still favors the Actor's own problem space.

### 4. Search the n8n template library

Run `advantageous_subcontra/n8n-template-scraper` with:

```json
{
  "keywords": [ "<from step 3>" ],
  "maxResultsPerKeyword": 20,
  "sort": "popularity",
  "includeWorkflowJson": true
}
```

**Why `includeWorkflowJson: true` is non-negotiable:** the classification in step 6 reads `nodes[].name` on every template. The scraper returns that even without the full workflow JSON, but having the workflow available means you can also inspect `workflow.nodes[].type` as a tiebreaker when a node's `displayName` is ambiguous.

**Why `sort: "popularity"`:** the question the user is answering is "what are n8n users actually building", not "what's new this week".

### 5. Rank and shortlist

From the merged, de-duplicated result pool:

- Discard templates whose `views` is below 100 — they're noise, not signal.
- Sort the rest by `views` descending.
- Keep the **top 20** for the full-detail report, and mark the **top 10** for deep analysis in step 6. If fewer than 10 pass the view threshold, use whatever you have and say so.

### 6. Classify each of the top 10

For every shortlisted template, inspect its `nodes` array (or `workflow.nodes` when present) and bucket it using the rules below. Count each node by its `name` field (the stable identifier n8n uses), not by its `displayName` (which authors can rename). Fall back to the template title and description for signals that live-in-code can't reveal — see the Apify / competitor note below.

**Node taxonomy:**

- **Apify node:** any node whose `name` starts with `n8n-nodes-base.apify` or whose `displayName` is literally "Apify". Also treat `n8n-nodes-base.httpRequest` as an Apify node when its `parameters.url` resolves to `api.apify.com` — **but note:** in exported n8n templates, `parameters.url` is almost always empty (URLs are bound via credential records). In practice, the reliable signals are (a) a native Apify node and (b) the template title / description naming Apify ("with Apify", "using Apify"). Treat the title/description match as sufficient — template authors routinely say "with Apify" and then call the API via `httpRequest`.
- **Competitor scraper node:** only used when the user opted in (step 2.5). A match is any node, title, or description signal for a service from [references/competitor-scrapers.md](references/competitor-scrapers.md) — currently Firecrawl, Bright Data, Exa, Airtop, ScrapingBee, Dumpling AI, Phantombuster — plus any `userExtras` the user supplied. Same caveat as Apify: `parameters.url` is usually empty, so title/description is the main signal in practice. Competitors are counted as a scraper node for bucket matching **but mark the template as needing conversion** (see below). When the user opted out, competitors are not a scraper node — the template falls to Replica like any other non-Apify scrape.
- **LLM node:** any node whose `name` matches one of these patterns (case-insensitive substring is fine):
  - `openAi`, `openai`
  - `anthropic`, `claude`
  - `googleGemini`, `gemini`, `lmChatGoogleGemini`
  - `ollama`
  - `mistral`
  - `cohere`
  - `deepseek`
  - `llama`
  - Any `@n8n/n8n-nodes-langchain.lmChat*` or `.agent` node
- **MCP-connector-supported node:** any node that matches a service listed in [references/apify-mcp-connectors.md](references/apify-mcp-connectors.md). As of 2026-10, that's Notion, Slack, GitHub, Sentry, Supabase. Re-read the reference each run — the list grows.
- **Infrastructure / trigger / utility nodes (ignore for classification):** `manualTrigger`, `scheduleTrigger`, `webhook`, `respondToWebhook`, `set`, `if`, `switch`, `merge`, `splitInBatches`, `code`, `function`, `stickyNote`, `noOp`, `wait`, `executeWorkflow`, `aggregate`, `filter`, `itemLists`. A workflow that is "only Apify + LLM + these" still counts as "only Apify + LLM" for bucket 2.

**"Scraper node"** in the rules below means an **Apify node** OR — only when the user opted in at step 2.5 — a **competitor scraper node**. Both qualify a template for buckets 1 and 2; competitor-driven matches get an extra conversion-needed flag. If the user opted out, a competitor-only template has no scraper node and falls to Replica by rule 3.

**Bucket rules (evaluate in order; first match wins):**

| # | Bucket | Rule |
|---|--------|------|
| 1 | **MCP-connector integration** | The template contains ≥1 scraper node **and** at least one node matches a service from the MCP connectors reference. |
| 2 | **Actor power-up** | The template contains ≥1 scraper node **and** every non-infrastructure non-scraper node is an LLM. (I.e. the LLM is the only thing standing between the scraper and the final output.) |
| 3 | **Marketing replica** | The template contains **zero** scraper nodes (no Apify, no competitor). Pure replica candidate. |
| 4 | **Other / mixed** | Everything else — e.g. scraper + Google Sheets + Gmail, where the extra services aren't on the MCP connector list yet. |

**Conversion-needed flag.** Any template that landed in bucket 1 or 2 via a competitor scraper (not an Apify node) carries `⚠️ Conversion needed`, which names the competitor and the Apify Actor to swap in. See [references/competitor-scrapers.md](references/competitor-scrapers.md) for how to pick the equivalent. These are still real power-up / MCP opportunities, but acting on them means the user has to rebuild the scrape step first — a bigger lift than a template that already uses Apify.

A template that lands in bucket 3 (replica) because its scraper is a competitor is **not** flagged as "conversion needed" — the whole point of a replica is to rewrite from scratch, so the extra flag would be redundant.

### 7. Write the report

Save a Markdown file at `<cwd>/<actor-slug>-n8n-scout.md` with this exact structure:

```markdown
# n8n scout: <Actor title>

**Actor:** [<username>/<name>](https://apify.com/<username>/<name>)
**Scouted:** <YYYY-MM-DD>
**Competitors included:** <"yes — tracked list" | "yes — tracked + <user extras>" | "no — competitors stay in Replicas">
**Keywords searched:** <comma-separated list from step 3>
**Templates considered:** <N returned> → <M after view cutoff> → top 10 classified

## Summary

- Marketing replicas: <count> templates — total views <sum>
- Actor power-ups: <count> templates — total views <sum> (of which <k> ⚠️ need competitor conversion)
- MCP-connector integrations: <count> templates — total views <sum> (of which <k> ⚠️ need competitor conversion)
- Other / mixed: <count> templates — total views <sum>

## 🎯 Marketing replicas

Templates that solve problems close to this Actor's but don't use Apify. Each is a candidate for a replica blog post / n8n template submission that swaps in `<username>/<name>`.

### [<Template title>](<template url>)
- **Views:** <views> (recent: <recentViews>)
- **Author:** <author.name> (@<author.username>)
- **What it does:** <one-sentence paraphrase of description>
- **Non-Apify data source it currently uses:** <node name(s)>
- **Replica angle:** <one sentence — why swapping in the Actor is better / cheaper / more reliable>

(repeat per template, highest views first)

## 🔌 Actor power-ups

Templates that are just a scraper node + an LLM. Signal that the LLM step belongs inside `<username>/<name>` itself. Items tagged `⚠️ Conversion needed` use a competitor scraper — still a valid power-up signal, but acting on it also means swapping the scraper for an Apify equivalent.

### [<Template title>](<template url>)
- **Views:** <views>
- **Scraper used:** <"Apify (via node)" | "Apify (via httpRequest to api.apify.com)" | "⚠️ Conversion needed — <competitor name>, swap in <apify/actor-slug>">
- **LLM used:** <node names, e.g. "OpenAI GPT-4o-mini" or "Anthropic Claude">
- **What the LLM does:** <one sentence inferred from node parameters or template description — summarization, extraction, classification, …>
- **Power-up suggestion:** <one sentence — concrete feature idea for the Actor>

## 🔗 MCP-connector integrations

Templates that chain a scraper with a service Apify's MCP connectors already support. Signal that wiring the Actor + MCP connector covers the same workflow with no n8n needed. Items tagged `⚠️ Conversion needed` use a competitor scraper.

### [<Template title>](<template url>)
- **Views:** <views>
- **Scraper used:** <same options as above>
- **Services involved:** <e.g. "Notion, Slack">
- **Integration angle:** <one sentence — what the MCP combo would do end-to-end>

## 🧩 Other / mixed

Full list for reference, no immediate action.

| Template | Views | Services | Why mixed |
|----------|------:|----------|-----------|
| [<title>](<url>) | <n> | <services> | <one phrase, e.g. "needs Gmail — not yet on MCP"> |

## Raw shortlist

| Rank | Template | Views | Bucket | Conversion |
|-----:|----------|------:|--------|-----------|
| 1 | [<title>](<url>) | <n> | <bucket> | <"—" or "⚠️ <competitor> → <apify/actor>"> |
| … | | | | |
```

Keep each per-template note to **one sentence per bullet** — the user is scanning dozens of these at a time. If you can't say the "replica angle" or "power-up suggestion" in one sentence, that's a sign the template probably doesn't belong in that bucket.

### 8. Report back in chat

End your reply with:

- The file path to the report.
- The competitor-inclusion choice from step 2.5 (one line: `competitors: on (tracked)` / `competitors: on (tracked + <extras>)` / `competitors: off`), so the user can re-run with the other setting if they want.
- The four bucket counts (and how many of the power-ups / MCP integrations are conversion-needed).
- The single highest-views template in each actionable bucket (replicas / power-ups / MCP integrations), as a one-line pitch each. If the top power-up or MCP template is conversion-needed, name the competitor and the Apify Actor to swap in in that one-liner — the user needs to see the conversion cost up front.
- If `userExtras` were supplied and any of them produced hits, suggest in one line that the user add those names to `references/competitor-scrapers.md` so future runs track them permanently.

Do **not** paste the full report into chat — the file is the deliverable.

## Edge cases

- **The scraper returns zero results.** Say so, re-check your keyword list (step 3 — were they too generic? too niche?), and ask the user whether to retry with a different set before giving up. Don't fabricate templates.
- **The Actor has no readme.** Fall back to the Actor's description, title, and categories for keywords. Flag in the report that keyword quality is lower than usual.
- **A template matches multiple Apify Actors.** Still classify it against the input Actor — the point of the report is "what's relevant to _this_ Actor", not "what's the global state of Apify-in-n8n".
- **The `nodes` array is empty but `workflow.nodes` is populated.** Use `workflow.nodes[].type` instead. The scraper sometimes drops the summary field when the template is unusually large.
- **The dataset response from `get-items` is very large.** Project with `fields=name,url,slug,views,recentViews,description,author,nodes,matchedKeywords,categories` (comma-separated) to shrink the payload. The classification only needs the `nodes` summary plus titles/descriptions.

## References

- [references/apify-mcp-connectors.md](references/apify-mcp-connectors.md) — current list of services Apify's MCP connectors support, with the matching n8n node names.
- [references/competitor-scrapers.md](references/competitor-scrapers.md) — Apify competitor scraping services (Firecrawl, Bright Data, Exa, …) and the Apify Actor to pitch as the swap-in. Re-read every run; the list grows.
- [references/node-taxonomy.md](references/node-taxonomy.md) — longer list of LLM / infra / utility node name patterns for the classification step.
