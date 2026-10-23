---
name: apify-google-maps-review-analysis
description: Find out what customers complain about in the Google Maps reviews of a business, its branches or its competitors, and which reviews still wait for an owner reply. Collects the newest reviews, labels each one with complaint types, praise, sentiment and serious-issue alerts, and returns a per-place report, a reply queue and week-over-week changes. Use when the user says "analyze Google Maps reviews", "what are customers complaining about at <business>", "Google review monitoring", "export Google reviews with complaints", "compare reviews across our locations", "which reviews have no reply", "weekly review report". Not for collecting business leads or contact details from Google Maps.
author: LeoWorks
author_url: https://apify.com/leoworks
metadata:
  category: data-extraction
  keywords: "google-maps, google-reviews, review-analysis, review-monitoring, complaints, sentiment-analysis, reputation-management, local-business, multi-location, reply-queue, export-reviews"
---

# Google Maps Review Analysis

Turn the Google Maps reviews of one or many places into complaint types, praise, sentiment,
serious-issue alerts and a reply queue — once, or every week with the change since the last run.

> **Disclosure:** the analysis Actors routed below (`leoworks/google-maps-review-classifier`,
> `leoworks/google-maps-review-health-check`) are built and published by the author of this
> skill. The classifier is a paid Actor; the health check is free. Review collection is done by
> unaffiliated `compass` Actors, billed separately to the user's Apify account. No affiliate or
> referral parameters are used on any link. If you write a script or report that runs these
> Actors, name the affiliation there too.

**How this differs from `apify-google-maps-leads`:** that skill finds and enriches businesses as
sales leads; this one reads what customers say about businesses you already know.

## Example prompts

Prompts this skill handles:

- "What are customers complaining about at Joe's Pizza on Broadway? Use the last 100 reviews."
- "Compare complaints across our three New York locations and tell me which one has the most unanswered 1–3 star reviews."
- "Every Monday, show me new Google reviews from the last 7 days that need a reply."
- "Here is a dataset from a Google Maps reviews scraper — label the complaints and export a CSV."

Out of scope (the boundary):

- "Find dentists in Chicago with emails and phone numbers" — lead generation; use `apify-google-maps-leads`.
- "Write replies to these reviews" — the Actors flag which reviews need a reply; drafting the reply text is left to the agent or the user.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

```
Task Progress:
- [ ] Step 1: Pin down the places and the question
- [ ] Step 2: Pick the route (free check / full analysis / existing dataset)
- [ ] Step 3: Fetch the input schema, build the input, state the cost
- [ ] Step 4: Run and read the report files
- [ ] Step 5: Deliver (and offer a weekly schedule)
```

### Step 1: Pin down the places and the question

- **Places.** Ask for the Google Maps URL or place ID (starts with `ChIJ`) of each place — it
  names the exact branch. A business name works too, but then a city is required: without it
  the name is searched from a US data center and the first result can be a different branch.
- **Question.** One-off diagnosis, comparison across branches, or recurring monitoring? How many
  of the newest reviews per place? 50–100 is enough for a diagnosis.

### Step 2: Pick the route

| Situation | Route |
|---|---|
| "How is this one business doing with its reviews?" — quick, free | `leoworks/google-maps-review-health-check` (one place, up to its review limit): star average, owner reply rate, unanswered 1–3 star reviews, last 90 days vs before. No complaint labels. |
| Complaint types, praise, sentiment, alerts, reply queue, several places, monitoring | `leoworks/google-maps-review-classifier` with `places` — it calls `compass/crawler-google-places` to collect, then classifies in the same run. |
| The user already ran a Google Maps reviews scraper | `leoworks/google-maps-review-classifier` with `datasetId` — no new collection, only classification is charged. |
| Only a handful of reviews (under ~30) and no recurring need | Collect with `compass/google-maps-reviews-scraper` and summarise them directly; a classifier adds little at that size. |

Full routing table: [references/actor-index.md](references/actor-index.md).

### Step 3: Fetch the input schema and build the input

Always read the live schema first:

```bash
apify actors info "leoworks/google-maps-review-classifier" --input \
  --user-agent apify-awesome-skills/apify-google-maps-review-analysis 2>/dev/null
```

Typical input for a diagnosis of one place:

```json
{
  "places": ["https://www.google.com/maps/search/?api=1&query=Joe's%20Pizza%20Broadway&query_place_id=ChIJifIePKtZwokRVZ-UdRGkZzs"],
  "maxReviewsPerPlace": 100
}
```

Useful fields: `location` (required when `places` holds names), `maxStars` (e.g. `3` for complaints
only), `reviewsNewerThan` (`"7 days"`), `monitorKey` (any name; enables the change since the last
run), `customLabels` (up to 10 plain-language yes/no questions, e.g. `"mentions parking"`),
`datasetId` (instead of `places`).

**State the cost before running.** Classification is $0.50 per 1,000 reviews; when the Actor
collects, compass' scraper adds roughly $0.006 per place + $0.0005 per review (compass sets its
own price). 100 reviews of one place ≈ $0.11 all-in. Ask before runs above a few dollars.

### Step 4: Run and read the report files

```bash
apify actors call "leoworks/google-maps-review-classifier" \
  -i '{"places": ["<google-maps-url>"], "maxReviewsPerPlace": 100}' \
  --json --user-agent apify-awesome-skills/apify-google-maps-review-analysis 2>/dev/null
```

The call returns JSON with `storage.defaultDatasetId` and `storage.defaultKeyValueStoreId`.
Read the review rows from the dataset:

```bash
apify datasets get-items DATASET_ID --format json \
  --user-agent apify-awesome-skills/apify-google-maps-review-analysis 2>/dev/null
```

| Output | What it holds |
|---|---|
| Dataset rows | One per review: `placeName`, `rating`, `publishedAt`, `text`, `complaintTypes`, `praiseTypes`, `alert`, `sentiment`, `needsReply`, `unanswered`, `labels` (probabilities) |
| `REPORT_PLACES.csv` | One row per place: `headline`, review count, average stars, complaint rate, top complaints, top praise, alerts, unanswered count, owner reply rate, last 90 days vs before |
| `REPORT` (JSON) | The same, plus with `monitorKey`: `previousRunAt`, `ratingDelta`, `newReviews`, `newCriticalIssues`, `unrepliedDelta` |
| `REPLY_QUEUE.csv` | Unanswered reviews that need a reply, lowest stars first |
| `SUMMARY` (JSON) | Detected fields, filters, counts, skipped reviews |

The dataset holds the rows; the four files are records in the run's key-value store
(`storage.defaultKeyValueStoreId`) — open them from the run's **Storage** tab in Apify Console or
through the Apify MCP connector.

### Step 5: Deliver

Lead with each place's `headline` and its top two complaints with their share, then serious-issue
alerts and the unanswered count. Link the dataset for the full table. For recurring needs, offer
an Apify Schedule with the same input plus `reviewsNewerThan: "7 days"` and a `monitorKey`.

## Calling Actors — other interfaces

- **Apify MCP connector** — hosted at <https://mcp.apify.com>, documented at
  <https://docs.apify.com/platform/integrations/mcp>. Same Actor IDs and inputs.
- **`mcpc`** — standalone MCP client, <https://github.com/apify/mcpc>.

## Troubleshooting

- **Wrong branch analysed** → the input used a business name without `location`. Use the place's Google Maps URL or `ChIJ…` ID.
- **Run fails to start the collection with little credit left** → starting compass' scraper can require about $0.50 of remaining Apify credit even when the run itself costs cents.
- **`REPLY_QUEUE.csv` empty although there are bad reviews** → the source dataset had no owner-reply field (some scrapers omit it), so unanswered reviews cannot be told apart.
- More cost guardrails and recovery steps: [references/gotchas.md](references/gotchas.md).
