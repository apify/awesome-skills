# Output Schema

Three outputs per run:

1. **Named Apify Dataset rows** -- append-only, machine-readable history.
2. **Named Apify Key-Value Store records** -- one record per (run, prompt) with the full raw Apify dataset item. Long-term archive for "what did Perplexity actually say two months ago?" queries.
3. **Markdown report** at `reports/snapshot-<ISO-date>.md` -- human-readable, entity-major.

## Dataset row schema

One row per `(run, prompt, source, entity)`. For N prompts x 6 sources x (1 brand + M competitors), a run appends `N x 6 x (1 + M)` rows.

```json
{
  "run_timestamp": "2026-05-18T09:00:14Z",
  "run_id": "a1B2c3D4e5F6g7H8",
  "prompt": "best web scraping tool",
  "source": "ai_overviews",
  "entity": "brand",
  "entity_name": "Apify",
  "entity_domain": "apify.com",
  "cited": true,
  "mentioned": true,
  "matched_citation_urls": ["https://apify.com/store"],
  "citation_urls": ["https://apify.com/store", "https://en.wikipedia.org/wiki/Web_scraping"],
  "citations": [{"url": "https://apify.com/store", "title": "Apify Store", "description": "..."}],
  "answer_text": "Apify is a cloud platform for web scraping...",
  "share_of_voice_pct": 50.0
}
```

| Field | Notes |
|-------|-------|
| `run_timestamp` | ISO 8601 UTC; start of the Apify run. |
| `run_id` | Apify run ID. Click: `console.apify.com/actors/runs/<id>`. |
| `source` | One of `ai_overviews`, `ai_mode`, `chatgpt`, `perplexity`, `copilot`, `gemini`. |
| `cited` | True if any citation URL's registrable domain == `entity_domain`. |
| `mentioned` | True if `answer_text` contains any surface form (`\bform\b`, case-insensitive). |
| `matched_citation_urls` | Subset of `citation_urls` that drove the "cited" flag. Empty when `cited` is false. |
| `citation_urls` | All citations for this (prompt, source) cell. Same across every entity row of the cell. |
| `citations` | `[{url, title, description}]` -- preserves the metadata each AI surface returned. Same across every entity row. |
| `answer_text` | Full AI answer text. `"[no answer returned]"` if the source returned nothing. |
| `share_of_voice_pct` | `len(matched_citation_urls) / len(citation_urls) * 100`. `0.0` if no citations. |

**Why every entity gets a row even when not cited:** continuity. The history diff in run 2+ needs the prior row to compare against.

## Key-value store records

| Aspect | Value |
|--------|-------|
| Store name | `<dataset_name>-raw` by default (configurable via `apify.kv_store_name`). Created on first run. |
| Record key | `<run_timestamp with ':' -> '-'>__<prompt-slug>` -- e.g. `2026-05-18T09-00-14Z__how-to-get-data-from-booking-com`. |
| Record value | The full Apify dataset item: `searchQuery`, `organicResults[]`, `peopleAlsoAsk[]`, `aiOverview`, `aiModeResult`, `chatGptSearchResult`, `perplexitySearchResult`, `copilotSearchResult`, `geminiSearchResult`. Untouched. |
| Why named, not the run's default | Default KV stores follow the run's retention policy. A named store persists indefinitely. |

Read a historical snapshot:

```python
import requests, os
token = os.environ["APIFY_TOKEN"]
stores = requests.get(f"https://api.apify.com/v2/key-value-stores?token={token}&unnamed=false").json()["data"]["items"]
store_id = next(s["id"] for s in stores if s["name"] == "ai-visibility-apify-raw")
record = requests.get(
    f"https://api.apify.com/v2/key-value-stores/{store_id}/records/"
    f"2026-05-18T09-00-14Z__how-to-get-data-from-booking-com?token={token}"
).json()
```

## History (run 2+)

From the second run onwards the report compares today to **all** prior runs in the named dataset. Per (prompt, source, entity) the renderer computes:

- `total_prior_runs` / `cited_in_prior_runs` / `mentioned_in_prior_runs`
- `first_cited_at` / `last_cited_at` (or `None`)
- `newly_cited` -- cited today AND `cited_in_prior_runs == 0`
- `newly_mentioned` -- analogous for mentions
- `dropped` -- not cited today AND the latest prior run had `cited: true`

The report renders one entity-major table per tracked entity (`Source | Cited | Mentioned | SoV% | Matched URLs | History`), with a one-line interpretive note quoting the surface-form context where the entity was mentioned. When any entity in a (prompt, source) cell is mentioned and `include_full_answers == "always"`, the full LLM answer is embedded verbatim; otherwise short quoted snippets only.

If the user explicitly asks "compare to yesterday only", drop to single-run diff (`newly_cited` and `dropped` against the most recent prior run only). Default is history mode.
