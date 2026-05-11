# Multi-Module Playbook

For comprehensive analysis (battlecard, deep dive, board prep). Uses subagent architecture — each module runs as independent agent.

## Module Sequence

Each step builds on prior findings (read definitions in modules/):

1. **Market Landscape** → competitor list + URLs + positioning signals
2. **Competitor Snapshots** → profiles using URLs from step 1
3. **Pricing Intelligence** → gathered alongside snapshots (pricing pages)
4. **Review Intelligence** → uses company names from step 1 for SERP queries
5. **Hiring Signals** → uses company names + career URLs from steps 1-2
6. **Content & SEO** → uses category keywords + domains from step 1

## Data Carry-Forward

- **URLs** from Market Landscape → reuse everywhere (avoid re-searching)
- **Company names** → Review SERP queries + Hiring LinkedIn URLs
- **Positioning insights** from Snapshots → inform SEO keywords
- **Review complaints** → validate/contradict Snapshot claims

## Subagent Architecture

Run discovery SERP directly (small, fast), then spawn parallel subagents:

- **Competitor Profiler** (Snapshots + Pricing) — URLs, pricing pages
- **Review Analyst** — company names, main rivals
- **Hiring & Culture Analyst** — company names, career URLs
- **SEO & Content Analyst** — domains, category keywords

Each subagent brief must include: user context (Step 0), competitor list + URLs, module reference path, output format (summary under 500 words: headline finding, key data table, 3 insights with source URLs).

## Synthesis

1. Executive narrative — 1 paragraph connecting biggest cross-module finding
2. Top 5 cross-module insights (e.g., "G2 reviews confirm pricing vulnerability from snapshot")
3. Competitive comparison matrix
4. Strategic recommendations — prioritized, framed for user's role
5. Data gaps and confidence levels
