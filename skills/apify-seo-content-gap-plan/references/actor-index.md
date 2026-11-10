# Actor index — apify-seo-content-gap-plan

Both Actors are public in the Apify Store, pay-per-event, and built by the skill author.
The live input schema (step 2 of the workflow in SKILL.md) wins over anything below.

| Step | User intent | Actor ID | Tier | Notes |
|---|---|---|---|---|
| Gap | Keywords a competitor ranks for where I rank worse or not at all | `doesaiknow/doesaiknow-competitor-keywords-apify` | community | Event `keyword`, billed per delivered row, success only |
| Cluster | Group the gap keywords into topics with intent and CORE/OUTER fit | `doesaiknow/ai-keyword-clustering-tool-topical-clustering-bulk-serp` | community | Event `batch_1k_keywords`, one per run of up to 1,000 input keywords, success only |

## Competitor Keywords (gap mode) — input

| Field | Type | Use in this skill |
|---|---|---|
| `targets` | string[] (max 20) | Competitor domains. Scheme and path are stripped |
| `target` | string | Legacy single domain; merged into `targets`. Do not use |
| `mode` | `"ranked"` \| `"gap"` | Always `"gap"` |
| `compareToDomain` | string | The user's domain. Required in gap mode; without it the run ends with 0 rows |
| `maxKeywords` | int 1-5000 (default 1000) | Rows per competitor; the main cost lever |
| `location` | enum of full names | `"United States"`, `"United Kingdom"`, `"Germany"`, `"Poland"` … |
| `language` | enum of full names | `"English"`, `"German"`, `"Polish"` … |
| `minVolume` | int (default 0) | Filters before billing. 50-100 is a sane floor |
| `maxKeywordDifficulty` | int 0-100 (default 100) | Filters before billing |
| `intentFilter` | string[] | `informational`, `commercial`, `transactional`, `navigational`; empty = all |
| `positionFrom` / `positionTo` | int (1 / 100) | Competitor rank window; `positionTo: 20` keeps rankings that earn traffic |

### Output (one row per keyword per competitor)

`keyword`, `search_volume`, `cpc`, `competition_level`, `keyword_difficulty` (0-100),
`search_intent`, `competitor_domain`, `competitor_rank`, `competitor_url`,
`estimated_traffic_value`, `is_featured_snippet`, `location`, `language`, `content_hash`;
gap mode adds `your_domain`, `your_rank` (null = not ranking), `your_url`, `gap_type`
(`missing` | `weaker` | `stronger` | `tied`).

```json
{"keyword": "best gravel wheels", "search_volume": 3600, "keyword_difficulty": 22,
 "search_intent": "commercial", "competitor_domain": "cyclingmag.example", "competitor_rank": 4,
 "competitor_url": "https://cyclingmag.example/best-gravel-wheels", "your_domain": "bikeparts.example",
 "your_rank": null, "your_url": null, "gap_type": "missing"}
```

## AI Keyword Clustering — input

| Field | Type | Use in this skill |
|---|---|---|
| `keywords` | string[] (1-1000, required) | Filtered gap keywords. Case-insensitive duplicates are removed by the Actor |
| `businessContext` | string (required) | 1-3 sentences; drives the CORE/OUTER classification |
| `country` | ISO-3166 lowercase | `us`, `gb`, `de`, `pl` … Unknown codes fall back to US |
| `language` | ISO-639 lowercase | Optional; defaults to the country's language |
| `enableSerpValidation` | bool (default false) | MERGE advice from live SERP overlap; longer run |
| `enableSplitCheck` | bool (default false) | SPLIT advice for clusters over 10 members |
| `minClusterSize` | int 1-10 (default 2) | Below it a keyword becomes an outlier (`cluster_id` -1) |
| `maxClusters` | int 5-200 | Optional hard cap |

### Output (one dataset item per run)

- `summary`: `input_keywords`, `expanded_keywords`, `total_clusters`, `outliers`,
  `core_topics`, `outer_topics`, `expansion_skipped`.
- `keywords[]`: `keyword`, `cluster_id`, `google_search_volume`, `google_cpc_usd`,
  `google_competition`, `monthly_history[]`, `trend_mom_pct`.
- `clusters[]`: `id`, `canonical_query`, `central_entity`, `cluster_label`, `intent`,
  `recommended_format`, `classification` (`CORE` | `OUTER`), `members[]`, `members_count`,
  `total_volume`, `avg_cpc_usd`, `serp_top10[]` (when SERP validation ran).
- `validation`: `splits[]`, `merges[]`. `topical_map`: `core[]`, `outer[]` with
  `pillar_page` and `supporting_pages` (cluster ids).

## Plan limits

| Actor | Free Apify plan | Paid plans |
|---|---|---|
| Competitor Keywords | 1 domain and 100 keywords per run; extra domains and rows are cut without an error | up to 20 domains x 5,000 keywords per run |
| AI Keyword Clustering | up to 200 input keywords per run; more → run ends with 0 items, nothing charged | up to 1,000 keywords per run |
