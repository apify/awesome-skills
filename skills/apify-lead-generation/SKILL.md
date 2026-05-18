---
name: apify-lead-generation
description: Generates B2B/B2C leads by scraping Google Maps, websites, Instagram, TikTok, Facebook, LinkedIn, YouTube, and Google Search. Use when user asks to find leads, prospects, businesses, build lead lists, enrich contacts, or scrape profiles for sales outreach.
author: Dušan Vystrčil
author_url: https://github.com/vystrcild
---

# Lead Generation

Scrape leads from multiple platforms using Apify Actors via the `apify` CLI.

**CLI rules:** Always pass `--user-agent apify-agent-skills/apify-lead-generation`, `--json` (or the relevant `--format` flag on `datasets get-items`), and `2>/dev/null`. The `--user-agent` flag is critical for telemetry — never omit it.

## Prerequisites
(No need to check it upfront)

- Apify CLI v1.5.0+ (`npm install -g apify-cli`)
- `jq` (recommended for quick extraction and filtering; `brew install jq` on macOS, `apt install jq` on Linux)
- Authentication via one of:
  - `apify login` (OAuth, opens browser)
  - `APIFY_TOKEN` env variable (e.g. `export APIFY_TOKEN=...` or `.env` file)
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

Verify auth: `apify info --user-agent apify-agent-skills/apify-lead-generation` — should show username and userId.

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Step 1: Determine lead source (select Actor)
- [ ] Step 2: Fetch Actor schema
- [ ] Step 3: Ask user preferences (format, filename)
- [ ] Step 4: Run the Actor and fetch results
- [ ] Step 5: Summarize results
```

### Step 1: Determine Lead Source

Select the appropriate Actor based on user needs:

| User Need | Actor ID | Best For |
|-----------|----------|----------|
| Local businesses | `compass/crawler-google-places` | Restaurants, gyms, shops |
| Contact enrichment | `vdrmota/contact-info-scraper` | Emails, phones from URLs |
| Instagram profiles | `apify/instagram-profile-scraper` | Influencer discovery |
| Instagram posts/comments | `apify/instagram-scraper` | Posts, comments, hashtags, places |
| Instagram search | `apify/instagram-search-scraper` | Places, users, hashtags discovery |
| TikTok videos/hashtags | `clockworks/tiktok-scraper` | Comprehensive TikTok data extraction |
| TikTok hashtags/profiles | `clockworks/free-tiktok-scraper` | Free TikTok data extractor |
| TikTok user search | `clockworks/tiktok-user-search-scraper` | Find users by keywords |
| TikTok profiles | `clockworks/tiktok-profile-scraper` | Creator outreach |
| TikTok followers/following | `clockworks/tiktok-followers-scraper` | Audience analysis, segmentation |
| Facebook pages | `apify/facebook-pages-scraper` | Business contacts |
| Facebook page contacts | `apify/facebook-page-contact-information` | Extract emails, phones, addresses |
| Facebook groups | `apify/facebook-groups-scraper` | Buying intent signals |
| Facebook events | `apify/facebook-events-scraper` | Event networking, partnerships |
| Google Search | `apify/google-search-scraper` | Broad lead discovery |
| YouTube channels | `streamers/youtube-scraper` | Creator partnerships |
| Google Maps emails | `poidata/google-maps-email-extractor` | Direct email extraction |

### Step 2: Fetch Actor Schema

Fetch the Actor summary, input schema, and README:

```bash
# Summary (title, description, pricing, stats)
apify actors info "ACTOR_ID" --user-agent apify-agent-skills/apify-lead-generation --json 2>/dev/null

# Input schema (required and optional parameters; schema lives in
# .taggedBuilds.latest.build.inputSchema as an escaped JSON string)
apify actors info "ACTOR_ID" --user-agent apify-agent-skills/apify-lead-generation --input --json 2>/dev/null

# README (capabilities, examples, gotchas)
apify actors info "ACTOR_ID" --user-agent apify-agent-skills/apify-lead-generation --readme 2>/dev/null
```

Replace `ACTOR_ID` with the selected Actor (e.g., `compass/crawler-google-places`).

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
  --user-agent apify-agent-skills/apify-lead-generation --json 2>/dev/null
```

From the output use `.id` (run ID), `.status` (should be `SUCCEEDED`), and `.defaultDatasetId`.

**Fetch results** — pick the variant based on the user's preference:

```bash
# Quick answer: total count + fields + top 5 in chat (no file)
apify datasets info DATASET_ID --json \
  --user-agent apify-agent-skills/apify-lead-generation 2>/dev/null \
  | jq '{itemCount, fields, consoleUrl}'
apify datasets get-items DATASET_ID --limit 5 \
  --user-agent apify-agent-skills/apify-lead-generation --format json 2>/dev/null

# CSV file
apify datasets get-items DATASET_ID \
  --user-agent apify-agent-skills/apify-lead-generation --format csv 2>/dev/null > YYYY-MM-DD_OUTPUT_FILE.csv

# JSON file
apify datasets get-items DATASET_ID \
  --user-agent apify-agent-skills/apify-lead-generation --format json 2>/dev/null > YYYY-MM-DD_OUTPUT_FILE.json
```

Other `--format` options: `jsonl`, `xlsx`, `xml`, `rss`, `html`. Use `--offset N` to paginate large datasets.

**Tip:** for anything more than a quick peek, save the dataset to a local file first (with `> file.json` / `> file.csv`) and run further analysis from disk. `apify datasets get-items` always streams over the network, so piping it straight into `jq` re-downloads the whole thing every iteration.

**Combining with `jq` for quick extraction:**

Treat `jq` as a complement to `apify datasets get-items`, not a replacement: server-side `--limit` / `--offset` / `--format` keeps cost and bandwidth down. Use `jq` on a sample item or on a file you already saved.

```bash
# Discover real field names from one sample item (Actor outputs vary —
# use this before composing further jq queries)
apify datasets get-items DATASET_ID --limit 1 --format json \
  --user-agent apify-agent-skills/apify-lead-generation 2>/dev/null \
  | jq '.[0]'

# Filter + count from a JSON file you already saved with the commands above
jq '[.[] | select(.emails != null and (.emails | length) > 0)] | length' YYYY-MM-DD_OUTPUT_FILE.json
```

### Step 5: Summarize Results

After completion, report:
- Number of leads found
- File location and name
- Key fields available
- Suggested next steps (filtering, enrichment)


## Error Handling

- Auth error → run `apify login`, or set `APIFY_TOKEN` env var
- `Actor not found` → check Actor ID spelling
- Run status `FAILED` → open the console URL (`.consoleUrl` from run metadata) for logs
- Timeout / very long run → pass `--timeout <seconds>` to `apify actors call`
