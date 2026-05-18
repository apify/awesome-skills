---
name: apify-trend-analysis
description: Discover and track emerging trends across Google Trends, Instagram, Facebook, YouTube, and TikTok to inform content strategy.
author: Dušan Vystrčil
author_url: https://github.com/vystrcild
---

# Trend Analysis

Discover and track emerging trends using Apify Actors to extract data from multiple platforms via the `apify` CLI.

**CLI rules:** Always pass `--user-agent apify-agent-skills/apify-trend-analysis`, `--json` (or the relevant `--format` flag on `datasets get-items`), and `2>/dev/null`. The `--user-agent` flag is critical for telemetry — never omit it.

## Prerequisites
(No need to check it upfront)

- Apify CLI v1.5.0+ (`npm install -g apify-cli`)
- `jq` (recommended for quick extraction and filtering; `brew install jq` on macOS, `apt install jq` on Linux)
- Authentication via one of:
  - `apify login` (OAuth, opens browser)
  - `APIFY_TOKEN` env variable (e.g. `export APIFY_TOKEN=...` or `.env` file)
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

Verify auth: `apify info --user-agent apify-agent-skills/apify-trend-analysis` — should show username and userId.

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Step 1: Identify trend type (select Actor)
- [ ] Step 2: Fetch Actor schema
- [ ] Step 3: Ask user preferences (format, filename)
- [ ] Step 4: Run the Actor and fetch results
- [ ] Step 5: Summarize findings
```

### Step 1: Identify Trend Type

Select the appropriate Actor based on research needs:

| User Need | Actor ID | Best For |
|-----------|----------|----------|
| Search trends | `apify/google-trends-scraper` | Google Trends data |
| Hashtag tracking | `apify/instagram-hashtag-scraper` | Hashtag content |
| Hashtag metrics | `apify/instagram-hashtag-stats` | Performance stats |
| Visual trends | `apify/instagram-post-scraper` | Post analysis |
| Trending discovery | `apify/instagram-search-scraper` | Search trends |
| Comprehensive tracking | `apify/instagram-scraper` | Full data |
| API-based trends | `apify/instagram-api-scraper` | API access |
| Engagement trends | `apify/export-instagram-comments-posts` | Comment tracking |
| Product trends | `apify/facebook-marketplace-scraper` | Marketplace data |
| Visual analysis | `apify/facebook-photos-scraper` | Photo trends |
| Community trends | `apify/facebook-groups-scraper` | Group monitoring |
| YouTube Shorts | `streamers/youtube-shorts-scraper` | Short-form trends |
| YouTube hashtags | `streamers/youtube-video-scraper-by-hashtag` | Hashtag videos |
| TikTok hashtags | `clockworks/tiktok-hashtag-scraper` | Hashtag content |
| Trending sounds | `clockworks/tiktok-sound-scraper` | Audio trends |
| TikTok ads | `clockworks/tiktok-ads-scraper` | Ad trends |
| Discover page | `clockworks/tiktok-discover-scraper` | Discover trends |
| Explore trends | `clockworks/tiktok-explore-scraper` | Explore content |
| Trending content | `clockworks/tiktok-trends-scraper` | Viral content |

### Step 2: Fetch Actor Schema

Fetch the Actor summary, input schema, and README:

```bash
# Summary (title, description, pricing, stats)
apify actors info "ACTOR_ID" --user-agent apify-agent-skills/apify-trend-analysis --json 2>/dev/null

# Input schema (required and optional parameters; schema lives in
# .taggedBuilds.latest.build.inputSchema as an escaped JSON string)
apify actors info "ACTOR_ID" --user-agent apify-agent-skills/apify-trend-analysis --input --json 2>/dev/null

# README (capabilities, examples, gotchas)
apify actors info "ACTOR_ID" --user-agent apify-agent-skills/apify-trend-analysis --readme 2>/dev/null
```

Replace `ACTOR_ID` with the selected Actor (e.g., `apify/google-trends-scraper`).

### Step 3: Ask User Preferences

**Skip this step** for simple lookups (e.g., "what's Nike's follower count?", "find me 5 coffee shops in Prague") — just use quick answer mode and move to Step 4.

For larger scraping tasks, ask:
1. **Output format**:
   - **Quick answer** - Display top few results in chat (no file saved)
   - **CSV** - Full export with all fields
   - **JSON** - Full export in JSON format
2. **Number of results**: Based on character of use case

**Cost safety**: Always set a sensible result limit in the Actor input (e.g., `maxResults`, `resultsLimit`, `maxCrawledPages`, or equivalent field from the input schema). Default to 100 results unless the user explicitly asks for more. Warn the user before running large scrapes (1000+ results) as they consume more Apify credits.

### Step 4: Run the Actor and Fetch Results

Two steps: run the Actor (blocks until done), then fetch dataset items in the requested format.

**Run the Actor** — returns run metadata as JSON; extract `defaultDatasetId` for the next step:

```bash
apify actors call "ACTOR_ID" -i 'JSON_INPUT' \
  --user-agent apify-agent-skills/apify-trend-analysis --json 2>/dev/null
```

From the output use `.id` (run ID), `.status` (should be `SUCCEEDED`), and `.defaultDatasetId`.

**Fetch results** — pick the variant based on the user's preference:

```bash
# Quick answer: total count + fields + top 5 in chat (no file)
apify datasets info DATASET_ID --json \
  --user-agent apify-agent-skills/apify-trend-analysis 2>/dev/null \
  | jq '{itemCount, fields, consoleUrl}'
apify datasets get-items DATASET_ID --limit 5 \
  --user-agent apify-agent-skills/apify-trend-analysis --format json 2>/dev/null

# CSV file
apify datasets get-items DATASET_ID \
  --user-agent apify-agent-skills/apify-trend-analysis --format csv 2>/dev/null > YYYY-MM-DD_OUTPUT_FILE.csv

# JSON file
apify datasets get-items DATASET_ID \
  --user-agent apify-agent-skills/apify-trend-analysis --format json 2>/dev/null > YYYY-MM-DD_OUTPUT_FILE.json
```

Other `--format` options: `jsonl`, `xlsx`, `xml`, `rss`, `html`. Use `--offset N` to paginate large datasets.

**Tip:** for anything more than a quick peek, save the dataset to a local file first (with `> file.json` / `> file.csv`) and run further analysis from disk. `apify datasets get-items` always streams over the network, so piping it straight into `jq` re-downloads the whole thing every iteration.

**Combining with `jq` for quick extraction:**

Treat `jq` as a complement to `apify datasets get-items`, not a replacement: server-side `--limit` / `--offset` / `--format` keeps cost and bandwidth down. Use `jq` on a sample item or on a file you already saved.

```bash
# Discover real field names from one sample item (Actor outputs vary —
# use this before composing further jq queries)
apify datasets get-items DATASET_ID --limit 1 --format json \
  --user-agent apify-agent-skills/apify-trend-analysis 2>/dev/null \
  | jq '.[0]'

# Quick aggregation from a JSON file you already saved with the commands above
jq '[.[] | select(.searchVolume != null)] | sort_by(-.searchVolume) | .[0:10]' YYYY-MM-DD_OUTPUT_FILE.json
```

### Step 5: Summarize Findings

After completion, report:
- Number of results found
- File location and name
- Key trend insights
- Suggested next steps (deeper analysis, content opportunities)


## Error Handling

- Auth error → run `apify login`, or set `APIFY_TOKEN` env var
- `Actor not found` → check Actor ID spelling
- Run status `FAILED` → open the console URL (`.consoleUrl` from run metadata) for logs
- Timeout / very long run → pass `--timeout <seconds>` to `apify actors call`
