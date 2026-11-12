# Report templates

All reports are written to `~/apify-reports/` (create it if missing). Link every Actor to its Store page and every issue or template to its URL. Keep one sentence per bullet.

## Verdict report

`~/apify-reports/apify-actor-idea-<slug>-<YYYY-MM-DD>.md`, where `<slug>` = brand, lowercased, with non-alphanumerics replaced by `-`.

```markdown
# Actor idea check — <one-line idea>

**Generated:** <ISO date>   **Target:** <domain>   **Market:** <country>/<language>

## Verdict: <Build | Build with differentiation | Don't build>

<One paragraph: the deciding reasons.>

| Question | Answer |
|---|---|
| Is there demand? | <Yes / Weak / Yes for platform, thin for tool> — <total_volume> searches/mo, <visits> visits/mo |
| Official API? | <none / free-unlimited / free-rate-limited / paid / partner-only> — <one-line evidence> |
| Is there room against competition? | <Yes / Limited / No> — <n> Actors (<normal/halved> buckets), leader <name> at <share>% of MAU |
| How to differentiate? | <top 2 features in a few words> |

## 1. Demand

### Search volume (<country>, Google Ads data)

| Keyword | Monthly searches | CPC | Paid-search competition | Trend |
|---|---:|---:|---|---|
| ... |

**Total:** <n>/mo. Strongest intent: <bucket>. <Note on 0-volume keywords.>

### Site traffic (Similarweb, <month>)

<visits>/mo, global rank <rank>, top countries <...>, traffic sources <...>.

**Gate:** <Passed / Below threshold — user chose to continue/stop>

## 2. Competition

### Official API

<api_status> — <URL>. Price: <...>. Limits: <...>. Covers: <fields>. Effect: <normal buckets / halved / continued despite free API>.

### Actors on the Store

**<n> Actors** target <domain> (<segment split if any>). Apify-owned: <n>. Stale (>6 mo): <n>.

| Actor | Scope | MAU | Rating | Price / 1k | Fail % (30d) | Last update |
|---|---|---:|---:|---:|---:|---|
| ... |

<Leader share, price range, pain points and worst run health from the audit, coverage gaps from market research, n8n signal.>

## 3. What to build to stand out

1. **<Feature>** — <why>. *Evidence:* <source: uncovered powerup / N issues / n8n templates with X views / keyword with Y searches>.
2. ...
N. *(only if triggered)* **Undercut on price** — all competitors > USD 10 / 1k results. *Note:* less effective than value-added differentiation; easy for competitors to match.

**Risks to check before building:** <login walls, rate limits, legal / GDPR, cost per entity>.

## Methodology & cost

- Keyword volume: run <runId>, <n> keywords (<k> with data), about USD <x>
- Traffic: run <runId>, about USD <x>
- Official API check: <queries>, <pages read>
- Store search: <queries>; full listing via `/v2/store`: <yes/no>
- Sub-reports: [market research](<file>), [quality audit](<file>), [n8n scout](<file>)
- Thresholds: demand ≥ 500 searches/mo OR ≥ 10k visits/mo; buckets <2 / 2–5 / 6–10 / >10 (halved to <1 / 1–2 / 3–5 / >5 for paid, rate-limited or partner-only APIs); price differentiation when every competitor > USD 10 / 1k
```

## Market research

`~/apify-reports/apify-market-research-<slug>.md`

```markdown
# Apify Store market research — <keywords>

**Generated:** <date>   **Actors surveyed:** <n> (<MAU> MAU)   **Apify-owned:** <n>   **Community:** <n>
**Schemas read in full:** <n> · from search field lists: <n> · inferred: <n>

## Powerup coverage

| Powerup | Actors | Total MAU | Top 3 by MAU |
|---|---:|---:|---|
| ... |
| **<gap powerup>** | **0** | 0 | — |

## Actors

| Actor | MAU | Price / 1k | Rating | Powerups |
|---|---:|---:|---:|---|

## Pricing

<min / median / leader>. <"Price differentiation does not apply" or "triggered">.

## Unmapped toggles

- `<field>` — <actor>

## Methodology
```

## Quality audit

`~/apify-reports/apify-actor-quality-audit-<slug>-<YYYY-MM-DD>.md`

```markdown
# Apify Actor quality audit — <field>

**Generated:** <date>   **Actors audited:** <n>   **Issues (open + closed):** <n> (<open> open)   **Bugs:** <n>   **Feature requests:** <n>

## Executive summary

- **Market shape / leader:** ...
- **Top market pain point:** **<theme>** — <count> reports across <k> Actors.
- **Top powerup ask:** **<theme>** — <count> asks across <k> Actors (or the clearest singleton).
- **Lowest-quality Actor:** **<actor>** — <signal that decided it>.
- **Worst run health (≥ 50 runs):** **<actor>** — <fail>% of <runs> runs.

## Actor quality scorecard

| Actor | MAU | Rating | Issues (open/closed) | Bugs | Feat. req. | Runs 30d | Fail % | Abort % | Price / 1k | Status |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---|

Fail % = (FAILED + TIMED-OUT) / public runs in 30 days. ⚠ ≥ 10%, 🔴 ≥ 25%. "low sample" = < 50 runs.

## 🚀 Potential powerups (clustered feature requests)

### 1. <theme> — <count> asks across <k> Actors
**Pitch:** ... · **Examples:** <linked issue titles with dates>

## 🐛 Market pain points (clustered bugs)

### 1. <theme> — <count> reports across <k> Actors
<per-Actor counts, linked examples>

## Methodology & caveats
```

## n8n scout

`~/apify-reports/<reference-actor-slug>-n8n-scout.md`

```markdown
# n8n scout: <reference Actor or idea>

**Scouted:** <date>   **Competitors included:** <yes — tracked list | no>
**Keywords searched:** <list>
**Adjacent problem-space terms (relevance filter):** <list>
**Templates considered:** <N returned> → <R after relevance filter> → <M after view cutoff> → <K classified>

## Key finding        <!-- only when the platform has no templates -->

## Summary
- Marketing replicas: <n> — <views>
- Actor power-ups: <n> — <views> (<k> ⚠️ conversion needed)
- MCP-connector integrations: <n> — <views>
- Other / mixed: <n> — <views>

## 🎯 Marketing replicas
### [<title>](<url>)
- **Views:** · **Current data source:** · **Replica angle:**

## 🔌 Actor power-ups
### [<title>](<url>)
- **Views:** · **Scraper used:** · **LLM used:** · **What the LLM does:** · **Power-up suggestion:**

## 🔗 MCP-connector integrations

## 🧩 Other / mixed
| Template | Views | Services | Why mixed |

## Raw shortlist
| Rank | Template | Views | Bucket | Conversion |
```
