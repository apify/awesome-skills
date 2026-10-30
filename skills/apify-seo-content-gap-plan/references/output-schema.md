# Output schema — apify-seo-content-gap-plan

Two files in the working directory, named with today's date.

## `YYYY-MM-DD_content-gap-plan.csv`

One row per cluster with a non-zero score, sorted by `priority` descending. UTF-8, comma
separated, header row, lists joined with ` | `. Wrap every field that contains a comma or a quote
in double quotes (Python's `csv` module does this for you); a row must have exactly 19 fields.

| Column | Meaning |
|---|---|
| `rank` | 1 = write first |
| `tier` | P1 / P2 / P3 |
| `cluster_id` | `clusters[].id` from the clustering run |
| `topic` | `cluster_label` |
| `target_keyword` | `canonical_query` |
| `gap_keywords` | gap keywords in the cluster |
| `supporting_keywords` | other members (added by the clustering Actor) |
| `gap_volume` | see prioritization |
| `avg_difficulty` | volume-weighted, or `unknown` |
| `intent` | cluster intent |
| `fit` | CORE / OUTER |
| `priority` | score, rounded to an integer |
| `action` | `new page` or `improve <your_url>` |
| `competitor_url` | best-ranking competitor page for the cluster |
| `competitor_rank` | its rank |
| `competitors` | every competitor domain ranking in the cluster |
| `recommended_format` | from the clustering Actor |
| `gap_run_ids` | gap run IDs (` \| ` separated) |
| `cluster_run_id` | clustering run ID |

Example row:

```csv
rank,tier,cluster_id,topic,target_keyword,gap_keywords,supporting_keywords,gap_volume,avg_difficulty,intent,fit,priority,action,competitor_url,competitor_rank,competitors,recommended_format,gap_run_ids,cluster_run_id
1,P1,4,Tubeless Tyre Setup and Sealing,tubeless tyre setup,"tubeless tyre setup | how to seal tubeless tyres | tubeless sealant","tubeless valve core",13800,36.0,informational,CORE,5297,new page,https://cyclingmag.example/tubeless-setup,3,cyclingmag.example,how-to guide,RUN_ID_1,RUN_ID_2
```

## `YYYY-MM-DD_content-gap-plan.md`

1. **Summary**: domains, market, date, rows fetched → rows kept (with the filter counts),
   clusters, total gap volume, total Apify cost reported by the runs.
2. **Backlog table**: rank, tier, topic, target keyword, gap volume, avg KD, intent, fit,
   priority, action.
3. **Briefs** for the top N clusters, each with: working title; target keyword; supporting
   keywords; search intent and format; action (new page / improve URL); competitor page to
   beat and its rank; 4-6 H2 ideas from member keywords; internal links to the pillar from
   `topical_map` when the cluster is a supporting page.
4. **Supporting ideas**: clusters with no gap keywords.
5. **Unclustered and dropped keywords**: counts per filter rule, top 10 dropped by volume.
6. **Method**: the formula, the weights used, Actor IDs, run IDs with Console links
   (`https://console.apify.com/actors/runs/RUN_ID`) and dataset IDs.
