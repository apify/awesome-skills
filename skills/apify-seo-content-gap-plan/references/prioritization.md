# Prioritization — apify-seo-content-gap-plan

The score ranks clusters by how much search demand a competitor already captures there, how
hard it is to compete, whether the searcher is close to buying, and how close the topic sits
to what the user sells. Every factor is visible, so the user can change a weight and re-rank.

## Formula

For each cluster, using only keywords that came from the gap run (not the keywords the
clustering Actor added on its own):

```
gap_volume     = sum(search_volume of "missing" keywords) + 0.5 x sum(search_volume of "weaker" keywords)
avg_difficulty = mean keyword_difficulty weighted by the same volumes (weaker x 0.5);
                 rows with keyword_difficulty 0 are left out of both sums (0 = unknown)
ease           = 1 - avg_difficulty / 100
priority       = gap_volume x ease x intent_weight x fit_weight
```

| Factor | Source | Default weights |
|---|---|---|
| `gap_volume` | gap Actor `search_volume`, `gap_type` | `weaker` counts half: the user already has a page, the upside is a better rank, not a new one |
| `avg_difficulty` | gap Actor `keyword_difficulty` | all rows 0 or missing → use 50 and mark the cluster "difficulty unknown" |
| `intent_weight` | clustering Actor `clusters[].intent` | transactional 1.0 · commercial 1.0 · informational 0.6 · navigational 0 |
| `fit_weight` | clustering Actor `clusters[].classification` | CORE 1.0 · OUTER 0.5 |

Adjust the weights when the user says so (a content-led brand may weight informational 1.0).
Say which weights were used in the Markdown file.

Then:
- Sort by `priority` descending; ties → lower `avg_difficulty` first.
- Tier: P1 = top 20% of clusters with a non-zero score, P2 = next 30%, P3 = the rest.
- Action per cluster: `new page` when most gap volume is `missing`; `improve <your_url>`
  when most is `weaker` (use the `your_url` with the highest volume).
- Clusters with no gap keywords score 0; list them under "supporting ideas", not in the backlog.
- Keywords left without a cluster (`cluster_id` -1, or not returned) go to an "unclustered"
  list with their own volume, so nothing silently disappears.

## Worked example

Invented numbers for illustration only (a bike-parts shop vs a cycling magazine):

| Cluster (canonical_query) | Class / intent | Gap keywords (volume, KD, type) | gap_volume | avg KD | priority |
|---|---|---|---:|---:|---:|
| tubeless tyre setup | CORE / informational | tubeless tyre setup (8,100, 34, missing), how to seal tubeless tyres (2,400, 0, missing), tubeless sealant (6,600, 41, weaker) | 13,800 | 36.0 | 5,297 |
| gravel bike wheels | CORE / commercial | best gravel wheels (3,600, 22, missing), gravel wheelset (2,900, 18, missing) | 6,500 | 20.2 | 5,186 |
| bike commuting tips | OUTER / informational | bike commuting tips (12,100, 15, missing) | 12,100 | 15.0 | 3,086 |

Check of the first row: gap_volume = 8,100 + 2,400 + 0.5 x 6,600 = 13,800. The KD-0 row is
left out of the average: (8,100 x 34 + 3,300 x 41) / 11,400 = 36.0. Priority = 13,800 x 0.640
x 0.6 x 1.0 = 5,297. A keyword the clustering Actor added to that cluster (say "tubeless valve
core") is listed as supporting and adds nothing to the score. The commuting cluster has the
most single-keyword volume but is OUTER, so it ranks last.

Rounding: keep full precision until the end; round `priority` to an integer and
`avg_difficulty` to one decimal only in the output.
