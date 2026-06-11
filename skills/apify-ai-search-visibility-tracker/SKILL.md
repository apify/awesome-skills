---
name: apify-ai-search-visibility-tracker
description: Track whether a brand and its competitors get cited or mentioned across Google AI Overviews, Google AI Mode, ChatGPT Search, Perplexity, Microsoft Copilot, and Google Gemini for a defined set of prompts, on a recurring schedule. Use when user asks to track AI visibility, monitor brand mentions in AI search, track ChatGPT citations, do AI search SEO tracking, GEO tracking (Generative Engine Optimization), AEO tracking (Answer Engine Optimization), monitor Perplexity citations, track AI Overviews mentions, see if their brand shows up in AI search, discover which prompts competitors rank for in AI search, find citation opportunities, or audit a website for AI visibility readiness.
author: Daniela Ryplová
author_url: https://github.com/danielarypl
---

# AI Search Visibility Tracker

Four workflows covering the full AI visibility lifecycle: **discover** which prompts matter → **find** citation opportunities → **audit** your site → **track** over time.

All workflows use `apify/google-search-scraper` for AI search. Workflow C also uses `apify/website-content-crawler`.

**Recommended flow:** Run Workflow A to discover prompts → Workflow B to find citation opportunities → Workflow C to audit your site → Workflow D to track everything on a schedule.

---

## Workflow A — Competitor Prompt Discovery

**Goal:** Find which queries surface a competitor in AI search answers, so you know which prompts are worth monitoring.

### Inputs to collect

| # | Input | Notes |
|---|-------|-------|
| 1 | Competitor domain(s) | e.g. `brightdata.com`, `scraperapi.com` |
| 2 | Seed topic keywords | e.g. "web scraping", "data extraction API" |
| 3 | AI sources | Default: all six (AI Overviews, AI Mode, ChatGPT, Perplexity, Copilot, Gemini) |

### Workflow

1. Generate 15–30 candidate queries from seed keywords using these templates:
   - `best [topic]`, `[topic] tools`, `how to [topic]`, `[topic] for [use case]`
   - `[topic] vs [competitor brand]`, `[competitor brand] alternative`
   - `[topic] API`, `[topic] pricing`, `[topic] tutorial`

2. Run `apify/google-search-scraper` for each candidate query. For each result, extract:
   - `aiOverview.sources[]`, `aiMode.sources[]`, `chatGptAnswer.sources[]`, `perplexityAnswer.sources[]`, `copilotAnswer.sources[]`, `geminiAnswer.sources[]`
   - Also check `answer_text` / `aiOverview.text` for competitor brand name mentions (word-boundary match: `\bBrand\b`)

3. For each (query, source) pair where the competitor domain or brand appears: record a hit.

4. Output a prompt-major table sorted by total hit count descending:

```
| Query | ChatGPT | Perplexity | AI Overviews | AI Mode | Copilot | Gemini | Total |
|-------|---------|------------|--------------|---------|---------|--------|-------|
| "best web scraping API" | ✓ | ✓ | — | ✓ | — | ✓ | 4 |
| "how to scrape Google" | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 6 |
```

5. Deliver the top-N queries (default 10) as a ready-to-paste list for Workflow D's `config.json` prompts.

---

## Workflow B — Citation Opportunity Finder

**Goal:** For a target topic, identify which domains and content types AI engines most often cite — revealing where to publish or pitch content.

### Inputs to collect

| # | Input | Notes |
|---|-------|-------|
| 1 | Target topic / industry | e.g. "web scraping", "ecommerce automation" |
| 2 | Seed queries | 5–20 queries covering the topic space |
| 3 | AI sources | Default: all six |
| 4 | Deep-crawl top cited? | Optional: crawl top-3 cited pages with `website-content-crawler` for structure patterns |

### Workflow

1. Run `apify/google-search-scraper` for each seed query across selected AI sources.

2. Collect every URL from `sources[]` across all results. Normalise to registrable domain (`blog.example.com` → `example.com`).

3. Aggregate:
   - **By domain**: count citations, list which AI sources cite it, list which queries triggered it
   - **By content type**: infer from URL path patterns (docs → `/docs/`, `/reference/`; blog → `/blog/`; news → known news domains)

4. Rank by total citation count. Output:

```
Top-cited domains for "web scraping" (42 queries × 6 sources):
| Domain | Citations | AI Sources | Inferred type |
|--------|-----------|------------|--------------|
| docs.apify.com | 38 | ChatGPT, Perplexity, AI Mode | Documentation |
| scraperapi.com/blog | 21 | AI Overviews, Gemini | Long-form blog |
```

5. If deep-crawl enabled: run `apify/website-content-crawler` on the top-3 cited URLs per domain. From the markdown output, extract:
   - First heading that directly answers the query
   - Presence of code blocks in first 500 words
   - Word count
   - Whether an H2/H3 contains the exact query phrase

6. Summarise patterns: "AI engines in this topic prefer [long-form docs / short direct-answer posts]. Typical cited page: [word count range], [has/lacks direct-answer H2], [has/lacks code example above the fold]."

---

## Workflow C — GEO Website Audit

**Goal:** Check whether a specific website's content is structured for AI citation; compare it against what AI engines actually cite for your target prompts.

### Inputs to collect

| # | Input | Notes |
|---|-------|-------|
| 1 | Your website URL | e.g. `https://apify.com` |
| 2 | Target prompts | Use Workflow A output, or supply 5–10 directly |
| 3 | AI sources | Default: all six |

### Workflow

1. Run `apify/google-search-scraper` for each target prompt. For each (prompt × source) record whether your registrable domain appears in `sources[]`.

2. For prompts where your domain is **not** cited: identify the top-cited competitor URL for that prompt.

3. Run `apify/website-content-crawler` on:
   - Your most relevant page(s) for each un-cited prompt
   - The top-cited competitor page for each un-cited prompt

4. For each un-cited prompt, produce a gap card:

```
Prompt: "how to scrape Google search results"
Your page: apify.com/blog/scraping-google  →  NOT cited on ChatGPT, Perplexity, AI Mode
Top-cited: docs.brightdata.com/scraping/google (cited 5/6 sources)

Structural gaps:
  ✗ Your page: answer buried after 900 words, no direct-answer H2
  ✓ Competitor: H2 "How to scrape Google in 3 steps" at word 120 + code block at word 180

Recommended actions (priority order):
  1. Add H2 that mirrors the query phrase within first 300 words
  2. Move code example above the fold
  3. Add a "Quick answer" summary box at the top
```

5. Deliver: per-prompt gap cards + a consolidated action table ranked by expected impact.

---

## Workflow D — Recurring Visibility Tracker

**Goal:** Snapshot brand citations and mentions across all six AI surfaces on a recurring schedule and track changes over time.

### Prerequisites
(No need to check upfront)

- `APIFY_TOKEN` saved in a `.env` file next to `config.json` (the runner auto-loads it).
- Python 3.9+ on PATH. `pip3 install requests` (only third-party dependency); `pip3 install tldextract` recommended for accurate registrable-domain matching on multi-part TLDs.
- For automated daily runs: macOS / Linux with launchd or cron available (the installer handles both). Windows users get printed `schtasks` instructions.

### Steps

Copy this checklist and track progress:

```
Task Progress:
- [ ] Step 1: Load or collect the seven required inputs
- [ ] Step 2: Confirm AI sources and cadence
- [ ] Step 3: Write config.json + .env, then install the OS schedule
- [ ] Step 4: Run a snapshot now so the user sees the first report
- [ ] Step 5: Deliver the history report (diff vs. all prior runs)
```

### Step 1: Load or Collect the Seven Required Inputs

If `config.json` exists in the user's working directory, load it and skip to Step 4 unless the user asks to reconfigure. On first run, ask all seven anchors **before** any Actor call:

| # | Input | Why it matters |
|---|-------|----------------|
| 1 | **Brand URL** | Primary domain. Drives registrable-domain citation matching (`blog.apify.com` -> `apify.com`). |
| 2 | **Brand name(s)** | Surface forms for text-mention matching (e.g., `Apify`, `apify.com`, `@apify`). URL-only matching misses mentions without links. |
| 3 | **Competitor brands** | Ask explicitly: *"Which competitors do you want tracked alongside your brand?"* Accept `name + domain` pairs. Zero is allowed; the question must still be asked on first run. |
| 4 | **Prompts to monitor** | One or more search queries. Each runs through every enabled AI source. If you don't know which prompts to use yet, run Workflow A first — it discovers competitor-visible prompts you can paste here. |
| 5 | **Cadence** | `daily` / `weekly` / `monthly`. Drives the schedule entry that `install_cron.sh` writes. |
| 6 | **Which AI sources** | Present the six (AI Overviews, AI Mode, ChatGPT, Perplexity, Copilot, Gemini), all enabled by default. Each adds per-result cost -- current pricing on the Actor page (https://apify.com/apify/google-search-scraper). |
| 7 | **Apify Dataset name** | The named dataset to append to. If absent, created on first run; the name is recorded in `config.json`. |

After those seven, ask optional follow-ups: `countryCode`, `languageCode`, `location` (UULE), preferred run hour (default `09:00` local).

Then one verbosity question -- save as `config.json:include_full_answers`:

- **`on_demand`** (default): report shows short quoted snippets around each surface-form match. Full LLM answers live in the named KV store; user can ask later.
- **`always`**: report embeds the full LLM answer verbatim whenever any entity is mentioned. Useful for one prompt; gets unwieldy at 5+ prompts.

### Step 2: Confirm AI Sources and Cadence

Echo back the user's seven choices in a single paragraph for confirmation. If the user toggles sources, update the in-memory config before writing.

### Step 3: Write `config.json` + `.env`, Then Install the OS Schedule

Create the working directory layout next to where the user wants reports to land:

```
working-dir/
  config.json     # copied from the skill's config.example.json, edited with collected values
  .env            # APIFY_TOKEN=apify_api_xxx   (chmod 600)
```

```bash
cp ${CLAUDE_PLUGIN_ROOT}/reference/scripts/config.example.json ./config.json
# then edit with the collected values, save

echo 'APIFY_TOKEN=your_token_here' > ./.env
chmod 600 ./.env
```

Then install the OS schedule:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/reference/scripts/install_cron.sh --cadence daily --hour 9
```

Cron expression mapping:

| Cadence | Cron expression | When |
|---------|-----------------|------|
| daily   | `0 H * * *`     | every day at H:00 local |
| weekly  | `0 H * * 1`     | every Monday at H:00 |
| monthly | `0 H 1 * *`     | the 1st of every month at H:00 |

### Step 4: Run a Snapshot Now

**macOS:**

```bash
launchctl kickstart "gui/$(id -u)/com.apify.ai-visibility-tracker"
tail -f ~/Library/Logs/ai-visibility-tracker.log
```

**Linux / generic:**

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_snapshot.py --config ./config.json
```

Both paths:

1. Call `apify/google-search-scraper` with the configured prompts + AI-source toggles.
2. Parse each (prompt x source) cell for citations and brand/competitor mentions.
3. Append rows to the named Apify Dataset (schema in `reference/output-schema.md`).
4. Write the raw item to the named KV store (long-term archive).
5. Compute the history vs. all prior runs.
6. Write `reports/snapshot-<ISO-date>.md` next to `config.json`.

### Step 5: Deliver the History Report

Open `reports/snapshot-<ISO-date>.md` and surface the top findings in chat. Lead with:

- **First-ever citations / mentions today** -- entity x source combinations crossing the threshold for the first time.
- **Drops** -- entity was cited in the latest prior run but isn't today.
- For every cited entity, the **exact matched URL(s)**.

### Output format

Snapshot summaries are **entity-major**: one Markdown table per tracked entity (brand, then competitors), one row per AI source, columns `Source | Cited | Mentioned | SoV% | Matched URLs | History`.

---

## Actors

| Actor | Used in | Key input fields |
|-------|---------|-----------------|
| `apify/google-search-scraper` | A, B, C, D | `queries[]`, `aiOverview`, `chatGptSearch`, `perplexitySearch`, `googleAiMode`, `bingCopilotSearch`, `googleGeminiSearch` |
| `apify/website-content-crawler` | B (optional), C | `startUrls[]`, `maxCrawlPages`, `outputMarkdown: true` |

Pricing changes; check the [pricing tab](https://apify.com/apify/google-search-scraper) before quoting numbers. Disable unused AI sources to reduce cost.

**Telemetry.** Workflow D runs through `reference/scripts/run_snapshot.py`, which already sets `User-Agent: apify-awesome-skills/ai-search-visibility-tracker-...` on every Apify API call. When calling these Actors ad-hoc in Workflows A-C, pass the matching flags so usage is attributed: `--user-agent apify-awesome-skills/apify-ai-search-visibility-tracker` and `--json` (use `--format json` for `apify datasets get-items`), and append `2>/dev/null`. Example:

```bash
apify actors call apify/google-search-scraper \
  --user-agent apify-awesome-skills/apify-ai-search-visibility-tracker \
  --json 2>/dev/null
```

## Quality Rules

- **Non-interactive.** No stdin reads in `run_snapshot.py` -- launchd / cron has no stdin.
- **Word-boundary brand matching** (`\bbrand\b`, case-insensitive). See `reference/citation-matching.md`.
- **Registrable-domain citation matching** (`blog.apify.com` counts as `apify.com`). See `reference/citation-matching.md`.
- **Never skip a row.** If an AI source returns nothing, write a row with `cited: false, mentioned: false, answer_text: "[no answer returned]"`.
- **Every row carries the Apify run ID** so any finding can be reverified.

## Error Handling

`APIFY_TOKEN not found` -- Tell the user to put it in `.env` next to `config.json` (`echo 'APIFY_TOKEN=...' > .env && chmod 600 .env`). Token at https://console.apify.com/account/integrations.
`config.json not found` -- Run Step 3 first to create it from the template.
`Dataset name not set` -- Ask the user for a name; the runner will create the dataset on first append.
`Actor run FAILED` -- Print the console link from the runner output and ask the user to inspect it.
`AI source returned no answer` -- The row is still written with `[no answer returned]`. Not an error.
`website-content-crawler returns no markdown` -- Page may be JS-heavy; try with `useBrowserCrawler: true`.
`Schedule not firing` -- See `reference/scheduling.md` troubleshooting section.
`No previous run to diff against` -- First run only. The report renders the snapshot without a history section.
