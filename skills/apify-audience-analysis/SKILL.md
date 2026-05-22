---
name: apify-audience-analysis
description: Understand audience demographics, preferences, behavior patterns, and engagement quality across Facebook, Instagram, YouTube, and TikTok.
author: Dušan Vystrčil
author_url: https://github.com/vystrcild
---

# Audience Analysis

Analyze and understand your audience using Apify Actors via the `apify` CLI to extract follower demographics, engagement patterns, and behavior data from multiple platforms.

**CLI rules:** Always pass `--user-agent apify-agent-skills/apify-audience-analysis`, `--json` (or the relevant `--format` flag on `datasets get-items`), and `2>/dev/null`. The `--user-agent` flag is critical for telemetry — never omit it.

## Prerequisites
(No need to check it upfront)

- Apify CLI v1.5.0+ (`npm install -g apify-cli`)
- `jq` (recommended for quick extraction and filtering; `brew install jq` on macOS, `apt install jq` on Linux)
- Authentication via one of:
  - `apify login` (OAuth, opens browser)
  - `APIFY_TOKEN` env variable (e.g. `export APIFY_TOKEN=...` or `.env` file)
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

Verify auth: `apify info --user-agent apify-agent-skills/apify-audience-analysis` — should show username and userId.

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Step 1: Identify audience analysis type (select Actor)
- [ ] Step 2: Fetch Actor schema
- [ ] Step 3: Ask user preferences (format, filename)
- [ ] Step 4: Run the Actor and fetch results
- [ ] Step 5: Summarize findings
```

### Step 1: Identify Audience Analysis Type

Select the appropriate Actor based on analysis needs:

| User Need | Actor ID | Best For |
|-----------|----------|----------|
| Facebook follower demographics | `apify/facebook-followers-following-scraper` | FB followers/following lists |
| Facebook engagement behavior | `apify/facebook-likes-scraper` | FB post likes analysis |
| Facebook video audience | `apify/facebook-reels-scraper` | FB Reels viewers |
| Facebook comment analysis | `apify/facebook-comments-scraper` | FB post/video comments |
| Facebook content engagement | `apify/facebook-posts-scraper` | FB post engagement metrics |
| Instagram audience sizing | `apify/instagram-profile-scraper` | IG profile demographics |
| Instagram location-based | `apify/instagram-search-scraper` | IG geo-tagged audience |
| Instagram tagged network | `apify/instagram-tagged-scraper` | IG tag network analysis |
| Instagram comprehensive | `apify/instagram-scraper` | Full IG audience data |
| Instagram API-based | `apify/instagram-api-scraper` | IG API access |
| Instagram follower counts | `apify/instagram-followers-count-scraper` | IG follower tracking |
| Instagram comment export | `apify/export-instagram-comments-posts` | IG comment bulk export |
| Instagram comment analysis | `apify/instagram-comment-scraper` | IG comment sentiment |
| YouTube viewer feedback | `streamers/youtube-comments-scraper` | YT comment analysis |
| YouTube channel audience | `streamers/youtube-channel-scraper` | YT channel subscribers |
| TikTok follower demographics | `clockworks/tiktok-followers-scraper` | TT follower lists |
| TikTok profile analysis | `clockworks/tiktok-profile-scraper` | TT profile demographics |
| TikTok comment analysis | `clockworks/tiktok-comments-scraper` | TT comment engagement |

### Step 2: Fetch Actor Schema

Fetch the Actor summary, input schema, and README:

```bash
# Summary (title, description, pricing, stats)
apify actors info "ACTOR_ID" --user-agent apify-agent-skills/apify-audience-analysis --json 2>/dev/null

# Input schema (required and optional parameters; schema lives in
# .taggedBuilds.latest.build.inputSchema as an escaped JSON string)
apify actors info "ACTOR_ID" --user-agent apify-agent-skills/apify-audience-analysis --input --json 2>/dev/null

# README (capabilities, examples, gotchas)
apify actors info "ACTOR_ID" --user-agent apify-agent-skills/apify-audience-analysis --readme 2>/dev/null
```

Replace `ACTOR_ID` with the selected Actor (e.g., `apify/facebook-followers-following-scraper`).

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
  --user-agent apify-agent-skills/apify-audience-analysis --json 2>/dev/null
```

From the output use `.id` (run ID), `.status` (should be `SUCCEEDED`), and `.defaultDatasetId`.

**Fetch results** — pick the variant based on the user's preference:

```bash
# Quick answer: total count + fields + top 5 in chat (no file)
apify datasets info DATASET_ID --json \
  --user-agent apify-agent-skills/apify-audience-analysis 2>/dev/null \
  | jq '{itemCount, fields, consoleUrl}'
apify datasets get-items DATASET_ID --limit 5 \
  --user-agent apify-agent-skills/apify-audience-analysis --format json 2>/dev/null

# CSV file
apify datasets get-items DATASET_ID \
  --user-agent apify-agent-skills/apify-audience-analysis --format csv 2>/dev/null > YYYY-MM-DD_OUTPUT_FILE.csv

# JSON file
apify datasets get-items DATASET_ID \
  --user-agent apify-agent-skills/apify-audience-analysis --format json 2>/dev/null > YYYY-MM-DD_OUTPUT_FILE.json
```

Other `--format` options: `jsonl`, `xlsx`, `xml`, `rss`, `html`. Use `--offset N` to paginate large datasets.

**Tip:** for anything more than a quick peek, save the dataset to a local file first (with `> file.json` / `> file.csv`) and run further analysis from disk. `apify datasets get-items` always streams over the network, so piping it straight into `jq` re-downloads the whole thing every iteration.

**Combining with `jq` for quick extraction:**

Treat `jq` as a complement to `apify datasets get-items`, not a replacement: server-side `--limit` / `--offset` / `--format` keeps cost and bandwidth down. Use `jq` on a sample item or on a file you already saved.

```bash
# Discover real field names from one sample item (Actor outputs vary —
# use this before composing further jq queries)
apify datasets get-items DATASET_ID --limit 1 --format json \
  --user-agent apify-agent-skills/apify-audience-analysis 2>/dev/null \
  | jq '.[0]'

# Quick aggregation from a JSON file you already saved with the commands above
jq '[.[] | select(.verified == true)] | length' YYYY-MM-DD_OUTPUT_FILE.json
```

### Step 5: Summarize Findings

After completion, report:
- Number of audience members/profiles analyzed
- File location and name
- Key demographic insights
- Suggested next steps (deeper analysis, segmentation)


## Error Handling

- Auth error → run `apify login`, or set `APIFY_TOKEN` env var
- `Actor not found` → check Actor ID spelling
- Run status `FAILED` → open the console URL (`.consoleUrl` from run metadata) for logs
- Timeout / very long run → pass `--timeout <seconds>` to `apify actors call`
