---
name: apify-influencer-discovery
description: Find and evaluate influencers for brand partnerships, verify authenticity, and track collaboration performance across Instagram, Facebook, YouTube, and TikTok.
author: Dušan Vystrčil
author_url: https://github.com/vystrcild
---

# Influencer Discovery

Discover and analyze influencers across multiple platforms using Apify Actors via the `apify` CLI.

**CLI rules:** Always pass `--user-agent apify-agent-skills/apify-influencer-discovery`, `--json` (or the relevant `--format` flag on `datasets get-items`), and `2>/dev/null`. The `--user-agent` flag is critical for telemetry — never omit it.

## Prerequisites
(No need to check it upfront)

- Apify CLI v1.5.0+ (`npm install -g apify-cli`)
- `jq` (recommended for quick extraction and filtering; `brew install jq` on macOS, `apt install jq` on Linux)
- Authentication via one of:
  - `apify login` (OAuth, opens browser)
  - `APIFY_TOKEN` env variable (e.g. `export APIFY_TOKEN=...` or `.env` file)
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

Verify auth: `apify info --user-agent apify-agent-skills/apify-influencer-discovery` — should show username and userId.

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Step 1: Determine discovery source (select Actor)
- [ ] Step 2: Fetch Actor schema
- [ ] Step 3: Ask user preferences (format, filename)
- [ ] Step 4: Run the Actor and fetch results
- [ ] Step 5: Summarize results
```

### Step 1: Determine Discovery Source

Select the appropriate Actor based on user needs:

| User Need | Actor ID | Best For |
|-----------|----------|----------|
| Influencer profiles | `apify/instagram-profile-scraper` | Profile metrics, bio, follower counts |
| Find by hashtag | `apify/instagram-hashtag-scraper` | Discover influencers using specific hashtags |
| Reel engagement | `apify/instagram-reel-scraper` | Analyze reel performance and engagement |
| Discovery by niche | `apify/instagram-search-scraper` | Search for influencers by keyword/niche |
| Brand mentions | `apify/instagram-tagged-scraper` | Track who tags brands/products |
| Comprehensive data | `apify/instagram-scraper` | Full profile, posts, comments analysis |
| API-based discovery | `apify/instagram-api-scraper` | Fast API-based data extraction |
| Engagement analysis | `apify/export-instagram-comments-posts` | Export comments for sentiment analysis |
| Facebook content | `apify/facebook-posts-scraper` | Analyze Facebook post performance |
| Micro-influencers | `apify/facebook-groups-scraper` | Find influencers in niche groups |
| Influential pages | `apify/facebook-search-scraper` | Search for influential pages |
| YouTube creators | `streamers/youtube-channel-scraper` | Channel metrics and subscriber data |
| TikTok influencers | `clockworks/tiktok-scraper` | Comprehensive TikTok data extraction |
| TikTok (free) | `clockworks/free-tiktok-scraper` | Free TikTok data extractor |
| Live streamers | `clockworks/tiktok-live-scraper` | Discover live streaming influencers |

### Step 2: Fetch Actor Schema

Fetch the Actor summary, input schema, and README:

```bash
# Summary (title, description, pricing, stats)
apify actors info "ACTOR_ID" --user-agent apify-agent-skills/apify-influencer-discovery --json 2>/dev/null

# Input schema (required and optional parameters; schema lives in
# .taggedBuilds.latest.build.inputSchema as an escaped JSON string)
apify actors info "ACTOR_ID" --user-agent apify-agent-skills/apify-influencer-discovery --input --json 2>/dev/null

# README (capabilities, examples, gotchas)
apify actors info "ACTOR_ID" --user-agent apify-agent-skills/apify-influencer-discovery --readme 2>/dev/null
```

Replace `ACTOR_ID` with the selected Actor (e.g., `apify/instagram-profile-scraper`).

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
  --user-agent apify-agent-skills/apify-influencer-discovery --json 2>/dev/null
```

From the output use `.id` (run ID), `.status` (should be `SUCCEEDED`), and `.defaultDatasetId`.

**Fetch results** — pick the variant based on the user's preference:

```bash
# Quick answer: total count + fields + top 5 in chat (no file)
apify datasets info DATASET_ID --json \
  --user-agent apify-agent-skills/apify-influencer-discovery 2>/dev/null \
  | jq '{itemCount, fields, consoleUrl}'
apify datasets get-items DATASET_ID --limit 5 \
  --user-agent apify-agent-skills/apify-influencer-discovery --format json 2>/dev/null

# CSV file
apify datasets get-items DATASET_ID \
  --user-agent apify-agent-skills/apify-influencer-discovery --format csv 2>/dev/null > YYYY-MM-DD_OUTPUT_FILE.csv

# JSON file
apify datasets get-items DATASET_ID \
  --user-agent apify-agent-skills/apify-influencer-discovery --format json 2>/dev/null > YYYY-MM-DD_OUTPUT_FILE.json
```

Other `--format` options: `jsonl`, `xlsx`, `xml`, `rss`, `html`. Use `--offset N` to paginate large datasets.

**Tip:** for anything more than a quick peek, save the dataset to a local file first (with `> file.json` / `> file.csv`) and run further analysis from disk. `apify datasets get-items` always streams over the network, so piping it straight into `jq` re-downloads the whole thing every iteration.

**Combining with `jq` for quick extraction:**

Treat `jq` as a complement to `apify datasets get-items`, not a replacement: server-side `--limit` / `--offset` / `--format` keeps cost and bandwidth down. Use `jq` on a sample item or on a file you already saved.

```bash
# Discover real field names from one sample item (Actor outputs vary —
# use this before composing further jq queries)
apify datasets get-items DATASET_ID --limit 1 --format json \
  --user-agent apify-agent-skills/apify-influencer-discovery 2>/dev/null \
  | jq '.[0]'

# Quick aggregation from a JSON file you already saved with the commands above
jq '[.[] | select(.followersCount != null and .followersCount >= 10000)] | length' YYYY-MM-DD_OUTPUT_FILE.json
```

### Step 5: Summarize Results

After completion, report:
- Number of influencers found
- File location and name
- Key metrics available (followers, engagement rate, etc.)
- Suggested next steps (filtering, outreach, deeper analysis)


## Error Handling

- Auth error → run `apify login`, or set `APIFY_TOKEN` env var
- `Actor not found` → check Actor ID spelling
- Run status `FAILED` → open the console URL (`.consoleUrl` from run metadata) for logs
- Timeout / very long run → pass `--timeout <seconds>` to `apify actors call`
