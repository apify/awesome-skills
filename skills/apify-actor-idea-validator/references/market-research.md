# Module: Market research (powerup coverage + pricing)

Run from Step 7 of [SKILL.md](../SKILL.md). It answers two questions about the competitors found in Step 6:

1. **Who is in this market?** One row per Actor with MAU, pricing, rating and the feature toggles ("powerups") its input schema exposes.
2. **How is the market covered?** One row per powerup, with how many Actors expose it and how much MAU sits behind it. Powerups with 0–1 Actors are gaps.

Output: `~/apify-reports/apify-market-research-<slug>.md`. Use the template in [report-templates.md](report-templates.md#market-research).

## M1 — Scope the Actor set

Start from the relevant Actors kept in Step 6 of SKILL.md. For a crowded niche, also run `apify actors search` for 1–3 brand-level keywords that returned search volume in Step 3, and add any relevant hits. Dedupe on `username/name`.

## M2 — Read input schemas

Use these sources in order of preference:

1. **Full schema** for every Actor shown in the report (the top 15–20 by MAU when there are many):
   ```bash
   apify actors info "OWNER/ACTOR" --input --json \
     --user-agent apify-awesome-skills/apify-actor-idea-validator 2>/dev/null
   ```
   With the MCP server, use `fetch-actor-details` with `output: { inputSchema: true }`.
2. **Field lists from search.** `apify actors search` / MCP `search-actors` results include each Actor's input field names and types. That's enough to detect powerups by field name. Use it for the long tail and as the fallback.
3. **Don't** read `GET /v2/actor-builds/<buildId>` for other developers' Actors. Without owner access it returns no `inputSchema` for most of them, and the coverage table silently undercounts.

For Actors with neither source, infer powerups from the title, description and pricing event names (an "Answer + Comment" event implies comments) and mark them "(inferred)". In Methodology, say how many schemas were read in full and how many came from search field lists.

MAU, pricing and last-modified come from the public Actor endpoint:

```bash
curl -s "https://api.apify.com/v2/acts/OWNER~ACTOR"
```

(`data.stats.totalUsers30Days`, `data.pricingInfos[-1]`, `data.modifiedAt`)

## M3 — Extract powerup candidates

Walk the schema's `properties`.

1. **Keep** a field if it's `boolean`, a `string`/`array` with a feature-mode enum, or its name starts with `include|extract|scrape|enable|fetch|use|get|with|return|download|capture|only`.
2. **Drop** plumbing (proxies, concurrency, timeouts, retries, logging, plain limits, primary input). The full stop-list is in [powerup-taxonomy.md](powerup-taxonomy.md).
3. **Label** each survivor from its `title` + `description` as a short noun phrase of 2–4 words.

Filters that open a new use case also count as powerups, not plumbing. Examples: "min MRR", "asking price", "AI-answer filter", "date range".

## M4 — Normalise across Actors

Map each label to the canonical taxonomy in [powerup-taxonomy.md](powerup-taxonomy.md), **matching on meaning**. Add domain-specific canonical labels when the niche needs them (e.g. "Revenue time series", "Company employee lists"). Keep unmatched labels and mark them `(unmapped)`. An `(unmapped)` label seen in 3+ Actors is worth calling out.

## M5 — Aggregate coverage

For each canonical powerup, compute:
- `actor_count`
- `total_mau` (skip Actors with missing MAU and note how many)
- Apify-owned vs community split
- top 3 Actors by MAU

Sort by `total_mau` descending. List explicitly, in **bold**, the powerups that **0 Actors** cover but that the idea, keyword intent or n8n evidence suggests users want.

## M6 — Pricing

Normalise each Actor to **USD per 1,000 results**:
- Use its per-result event (Bronze tier when tiered), with the start fee left out unless it's material.
- Mark pay-per-usage and rental Actors as "n/a".
- For multi-event pricing (question + answer), report the range.

Report the min, median and leader price. **Price differentiation applies only if every priced competitor is above USD 10 per 1k.** Otherwise write "Price differentiation does not apply". If the value is in aggregation (ranking, deduplicated leads), suggest a per-entity pricing unit instead.
