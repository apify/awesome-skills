---
name: apify-jev-classifier
description: >
  Classify, score, label, triage or sentiment-tag a list of texts or any Apify dataset
  (Google Maps reviews, LinkedIn profiles, social posts and comments, product reviews, job
  postings, support tickets, company records) with TypeSafe AI's Jev decision model through
  the sameh.jarour/jev-classifier Actor: one run, every question answered per item, a
  calibrated confidence per answer, $0.50 per 1,000 items, no Jev or OpenRouter key needed.
  Use when the user says "classify these reviews", "score these leads", "which tickets are
  urgent", "tag sentiment on this dataset", "flag spam or toxic comments", "label my scraped
  data", "is this profile a decision maker", or asks how to run the Actor, what input it
  takes, what the output rows contain, or whether they need an API key. Out of scope:
  generating text, summarizing, or extracting new fields.
author: Sameh Jarour
author_url: https://github.com/samehjarour
metadata:
  category: data-extraction
  keywords: "classification, text-classification, sentiment-analysis, lead-scoring, data-labeling, triage, jev, typesafe, google-maps-reviews, linkedin-profiles, social-media-comments, product-reviews, job-postings, support-tickets, dataset-enrichment"
---

# Jev Bulk Classifier

Turn scraped text into labels, scores and yes/no flags with TypeSafe AI's Jev through the
`sameh.jarour/jev-classifier` Actor. One run sends every item to Jev once, asks all
questions in that single call, and writes one dataset row per item with a flat answer, a
confidence and the raw probabilities. No TypeSafe or OpenRouter key is needed: the default
provider routes through Apify's OpenRouter Actor and bills the run's own Apify account.

Disclosure: the routed Actor `sameh.jarour/jev-classifier` is built and monetized
(pay-per-event, $0.0005 per classified item) by the author of this skill.

## Example prompts

Prompts this skill handles:

- "Classify the Google Maps reviews in dataset Sn7qAbnhkKIzqlJRa by sentiment and topic, and flag complaints."
- "Here are 200 support tickets. Which department should handle each one and which are urgent?"
- "Score these LinkedIn profiles: seniority, department, and whether they look like decision makers."

Out of scope (the boundary):

- "Summarize these reviews" or "extract the phone number from each listing". Jev only picks
  between options you define; it does not generate or extract text. Use a scraper with
  built-in extraction or an LLM Actor for that.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)
- Nothing else. Do not ask the user for a Jev, TypeSafe or OpenRouter key; the default
  `provider` uses the run's Apify token.

## Workflow

1. **Pick the source.** Inline `items` (strings or objects) or `datasetIds` from an earlier
   scraper run. Never re-upload a dataset; pass its ID.
2. **Pick the questions.** A `preset` when the data comes from a common scraper, otherwise
   `preset: custom` with your own `questions`. Read one item of the dataset first and set
   `datasetFields` to the text-bearing fields; field names differ between scrapers.
3. **Test, then run.** Run once with `maxItems: 50`, check the labels and confidences, then
   run the full dataset. Warn the user when the estimate exceeds about $5 (10,000 items).
4. **Deliver.** Report the row count, the dataset link
   (`https://console.apify.com/storage/datasets/DATASET_ID`), the share of rows below 0.9
   confidence, and the `SUMMARY` totals from the run's key-value store.

## Run it

Pick ONE source (`items` or `datasetIds`) and ONE question source (`preset` or `questions`).

Minimal `input.json` for a Google Maps Reviews Scraper dataset:

```json
{
  "datasetIds": ["Sn7qAbnhkKIzqlJRa"],
  "datasetFields": ["text", "stars", "title"],
  "preset": "google-maps-reviews"
}
```

### Option A: Apify CLI (recommended for portability)

```bash
# Blocking run (fine for up to a few thousand items)
apify actors call sameh.jarour/jev-classifier --input-file input.json \
  --user-agent apify-awesome-skills/apify-jev-classifier --json 2>/dev/null
# From the output: .id (run ID), .status, .defaultDatasetId

# Large runs: start, then poll until .status is SUCCEEDED or FAILED
apify actors start sameh.jarour/jev-classifier --input-file input.json \
  --user-agent apify-awesome-skills/apify-jev-classifier --json 2>/dev/null
apify runs info RUN_ID --user-agent apify-awesome-skills/apify-jev-classifier --json 2>/dev/null

# Fetch the rows
apify datasets get-items DATASET_ID --format json \
  --user-agent apify-awesome-skills/apify-jev-classifier 2>/dev/null

# Input schema and README
apify actors info sameh.jarour/jev-classifier --input \
  --user-agent apify-awesome-skills/apify-jev-classifier 2>/dev/null
apify actors info sameh.jarour/jev-classifier --readme \
  --user-agent apify-awesome-skills/apify-jev-classifier
```

### Option B: Apify MCP connector

With the hosted MCP server at <https://mcp.apify.com>, use `call-actor` with actor
`sameh.jarour/jev-classifier` and the same JSON as input, then `get-dataset-items` on the
returned `defaultDatasetId`.

### Option C: REST API

```bash
# The response is wrapped in `data` (.data.id, .data.status, .data.defaultDatasetId).
# waitForFinish accepts up to 300 s, but the POST can still return READY or RUNNING for a
# queued run, so poll GET /v2/actor-runs/RUN_ID?waitForFinish=60 until SUCCEEDED or FAILED.
curl -X POST "https://api.apify.com/v2/acts/sameh.jarour~jev-classifier/runs?waitForFinish=120" \
  -H "Authorization: Bearer $APIFY_TOKEN" -H "Content-Type: application/json" -d @input.json
# Rows: GET https://api.apify.com/v2/datasets/DATASET_ID/items?clean=true (same Bearer header)
```

Never put the token in the URL; use the `Authorization` header.

## Input reference

| Field | Type | Notes |
|---|---|---|
| `items` | array of strings or objects | Inline texts or records. Omit when using datasets. |
| `datasetIds` | array of strings | Dataset IDs or names. Processed after `items`. |
| `datasetFields` | array of strings | Only these fields are sent to Jev. Dot paths like `authorMeta.name` work. Always set it for large records; whole Google Maps place records cost thousands of tokens. Items with none of the fields are skipped. |
| `maxItems` | integer | Cap on dataset items, 0 = all. Use 50 to test questions first. |
| `preset` | string | One of the ids below, or `custom` (default) to use `questions`. A preset wins over `questions`. |
| `questions` | object | Raw Jev questions map, used only with `preset: custom`. See Custom questions. |
| `provider` | string | `apify-openrouter` (default, no key) or `typesafe` (needs `apiKey`). |
| `apiKey` | string, secret | TypeSafe key, only for `provider: typesafe`. |
| `model` | string | `jev-latest` (default, = jev-1.13), `jev-preview` (= jev-1.14), `jev-1.13.0`, or the OpenRouter ids typesafe/jev-1.13 and typesafe/jev-1.14. Names translate automatically. |
| `concurrency` | integer | Parallel items, default 10, max 50. |
| `failOnError` | boolean | Default false: failed items get an `error` field and the run continues. |
| `includeRawResponse` | boolean | Adds the full Jev response per row. |

## Presets

Choice labels for every preset are in [references/presets.json](references/presets.json)
(each `criteria` key is a label). Key types: `sentiment`, `frustration`, `business_size`,
`online_presence`, `company_size` are scores (0 = first level, e.g. very negative, up to
levels-1); `department`, `main_topic`, `seniority`, `customer_type`, `sells_to`,
`business_model`, `content_type`, `intent`, `work_arrangement`, `employment_type` are
choices (label); every `is_*`, `has_*`, `would_*`, `needs_*`, `open_to_*`, `mentions_*`,
`actionable_feedback`, `salary_disclosed`, `requires_degree` is a noul (probability of yes).

| `preset` | Questions (result keys) | `datasetFields` to send |
|---|---|---|
| `support-tickets` | department, frustration, is_urgent | subject, body |
| `google-maps-reviews` | sentiment, main_topic, is_complaint, actionable_feedback, would_return | text, stars, title |
| `google-maps-leads` | business_size, customer_type, is_independent, has_website, online_presence | title, categoryName, description, website, reviewsCount, totalScore |
| `linkedin-profiles` | seniority, department, is_decision_maker, is_technical, open_to_opportunities | headline, summary, jobTitle, companyName, experience |
| `company-enrichment` | company_size, business_model, sells_to, is_startup, is_tech_company | name, description, industry, employeeCount, website |
| `social-media-posts` | sentiment, content_type, is_sponsored, has_call_to_action, is_brand_safe | caption, text, hashtags |
| `social-media-comments` | sentiment, intent, needs_reply, is_spam, is_toxic | text |
| `product-reviews` | sentiment, main_topic, mentions_defect, would_recommend, is_suspicious | reviewTitle, reviewDescription, ratingScore |
| `job-postings` | seniority, work_arrangement, employment_type, requires_degree, salary_disclosed, is_technical_role | title, description, location, employmentType |

Field names differ between scrapers. Read one item of the dataset first and adjust
`datasetFields`.

**To add a question to a preset:** copy that preset's `questions` object from
`references/presets.json`, add your question, and send it with `preset: custom`. Labels and
wording then match the preset exactly.

## Custom questions

Three types. Describe every option in a phrase; Jev reads literally.

```json
{
  "preset": "custom",
  "questions": {
    "department": { "type": "choice", "instructions": "Which team handles this?",
      "criteria": { "billing": "Payments, refunds", "technical": "Bugs, outages", "sales": "Pricing, plans" } },
    "frustration": { "type": "score", "instructions": "How frustrated is the sender?",
      "criteria": ["Calm", "Frustrated but civil", "Very angry"] },
    "is_urgent": { "type": "noul", "instructions": "Is this time-sensitive?" }
  }
}
```

`choice` returns a label (up to 255 options). `score` returns a number from 0 to levels-1
(2 to 10 levels). `noul` returns the probability of yes.

## Output rows

One row per item in the run's default dataset:

```json
{
  "index": 0,
  "source": { "type": "dataset", "datasetId": "Sn7qAbnhkKIzqlJRa", "offset": 0 },
  "state": { "text": "Waited 45 minutes...", "stars": 1, "title": "Bella Pasta" },
  "results": { "sentiment": 0.03, "main_topic": "wait_time_speed", "is_complaint": 0.99, "actionable_feedback": 0.85, "would_return": 0.02 },
  "confidence": { "sentiment": 0.97, "main_topic": 0.76, "is_complaint": 0.99, "actionable_feedback": 0.85, "would_return": 0.98 },
  "answers": { "main_topic": { "type": "choice", "choice": "wait_time_speed", "probabilities": { "...": 0.1 }, "confidence": 0.76 } },
  "model": "typesafe/jev-1.13-20260917",
  "inputTokens": 596, "estimatedCostUsd": 0.000025, "charged": true, "error": null
}
```

- `results` is the flat answer per question key: label, score, or yes-probability.
- `confidence` is 0 to 1 per key. Route rows below 0.9 to a human.
- `source.offset` joins a row back to the original dataset item.
- `state` is exactly what was sent: the raw string for inline string items, or the selected
  fields for dataset items. Other original fields are not copied.
- A `SUMMARY` record in the run's key-value store has totals: processed, failed, tokens, cost.

## Cost

Pay-per-event: $0.0005 per classified item ($0.50 per 1,000) plus about $0.02 per 1,000
items in Jev tokens when `datasetFields` is set. Failed items are not charged. The run
stops cleanly when the user's max cost per run is reached and keeps the rows produced so
far. Present cost as a rough estimate; confirm with the user above about $20
(40,000 items).

## Troubleshooting

| Problem | Fix |
|---|---|
| Guessing `datasetId`, `textField`, `tasks` | Use `datasetIds` (array), `datasetFields`, `preset`. |
| Asking for a Jev or OpenRouter key | Not needed. Default provider uses the run's Apify token. Only an Apify login or `APIFY_TOKEN` is required. |
| Sending whole scraper records | Set `datasetFields`; cost and accuracy both improve. |
| Expecting generated text or extracted fields | Jev only picks between the options you define. |
| `questions` ignored | A non-custom `preset` overrides it. Set `preset: custom`. |
| Run fails with "Model ... does not exist" | Use a listed `model` id; typesafe/jev-latest is not served by OpenRouter. |
| Run stops early with "max charge" | The user's max cost per run was hit. Raise it; rows produced so far are kept. |
| Rows with `error` set and `charged: false` | Per-item Jev failure (timeout, malformed item). Re-run those offsets with `failOnError: false` left as is; nothing was billed for them. |
