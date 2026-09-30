# Gotchas — apify-jobs-data

Cost guardrails, error recovery, and platform quirks. Read on demand when building
an input (Step 3) or when a run misbehaves.

## Cost guardrails

Check the pricing model before running:

```bash
apify actors info "ACTOR_ID" --json \
  --user-agent apify-awesome-skills/apify-jobs-data 2>/dev/null
# inspect pricingInfo
```

| Model | Actors here | What to watch |
|---|---|---|
| `PAY_PER_RESULT` / `PAY_PER_EVENT` (all of them) | `agentx/all-jobs-scraper` (default), `misceres/indeed-scraper` (community), `memo23/glassdoor-scraper-ppr` | Cost scales with `max_results × platforms`. No subscriptions — a capped run costs cents. Estimate first. |

**ToS / account risk.** Every board Actor scrapes a third-party site against its
Terms of Service (SKILL.md Prerequisites). All routes run on Apify's infrastructure
(no user login), so they never put the user's own board accounts at risk.

### Estimate the WHOLE pipeline

```
total ≈ board_pull + (optional Glassdoor salary benchmark × companies)
board_pull ≈ start_fee + (max_results × boards_hit × per_result)
```
For `agentx/all-jobs-scraper`, `max_results` is **per platform** and, with `platforms`
empty, it hits every platform it supports for the country (up to 42), so the row count
(and cost) is ≈ `max_results × platforms_hit` — a request for 50 returns hundreds of
jobs, not 50. Pin `platforms` to make the estimate exact.

Reference rates as of 2026-09-16, free tier (confirm live in console — they change, and
paid plans get lower per-result rates):
- `agentx/all-jobs-scraper`: ≈ $0.01 start (per GB of run memory) + $0.0035 / job (≈ $3.50 / 1,000).
- `misceres/indeed-scraper`: ≈ $0.006 / job (≈ $6 / 1,000 listings), no start fee.
- `memo23/glassdoor-scraper-ppr`: ≈ $0.005 start + $0.00475 / row; **always set `maxItems`
  (≤ 50 for a benchmark)** — the Actor's default is 20,000 per URL (≈ $95). Only when
  the salary benchmark is used.

### Confirmation thresholds

- Estimated cost **> $5** → warn with a rough number ("around $X").
- Estimated cost **> $20** → require explicit confirmation before running.
- Biggest silent trap: a high `max_results` × several boards. Estimate the board pull
  (plus the optional Glassdoor salary benchmark) before running.

## Common errors

| Symptom | Cause | Fix |
|---|---|---|
| Zero results, all boards | Over-narrow query / unparseable location | Widen `posted_since`, drop one filter, try `City, Country` form, lower specificity |
| Zero in-area rows on one board only | That board blocked the run, or the Actor ignored the location | If the user named that board and it has a standalone Actor, run the fallback once (SKILL.md Step 2); otherwise note it in the header as a coverage gap. Not a fatal error. |
| Run `RUNNING` for minutes | Large `max_results` / multi-board fan-out | Poll `get-actor-run` (waitSecs ≤ 45); raise `timeout` to 900–1800. The Actors' own default timeouts are huge (aggregator 12 h, Indeed 7 days — live `defaultRunOptions`, 2026-09-16), so a longer timeout is always paired with `maxTotalChargeUsd`, the only cap on spend (SKILL.md Step 4) |
| Anti-bot / partial pages | Board rate-limited the Actor | Lower concurrency and `max_results` in the *first* run's design — don't rerun the aggregator for the same board (SKILL.md Step 2); if a named board came back with 0 in-area rows, take its per-board fallback instead |
| LinkedIn returns little/nothing | LinkedIn blocks hardest | No standalone LinkedIn Actor here and no second aggregator retry — note the thin LinkedIn coverage in the header as a gap; the aggregator's other boards carry the run |
| Duplicate-heavy dataset | Same role syndicated across boards | Expected — skip-pass rule 2 dedupes; set `saveOnlyUniqueItems: true` on Indeed |
| Salary always blank | Many postings don't disclose | Real — never infer. Leave blank; in analysis, report the disclosed share as coverage |
| "Posted today" on a known-old role | Board re-stamped a repost | Ghost tell (skip-pass rule 3). Flag `⚠ re-stamped`; don't trust the date |
| No Glassdoor data | Small / private company | Report "no Glassdoor data found"; don't fabricate figures |

## Platform quirks

### `agentx/all-jobs-scraper`
- `country` is a **full country name** from the actor's enum (`Germany`, `United
  States`) — **not** an ISO-2 code; it is required with no default (omitting it fails
  validation). A wrong country silently narrows or mis-targets results.
- **`max_results` is per platform.** With `platforms` empty the actor fans out to
  every platform it supports for the country, so a request for 10 can return far
  more than 60 rows. Budget and expectations should use `max_results × platforms`,
  not `max_results` — pin `platforms` to bound it.
- `job_type` enum values have **no hyphen** (`fulltime`, not `full-time`).
- Field coverage varies sharply by board/region; `salary` especially is often blank
  (a live Berlin run disclosed salary on 1 of 58 rows) and currency/period can be
  inconsistent. Treat blanks as missing, normalize before aggregating (analysis.md).

### `misceres/indeed-scraper`
- `country` is required and must match `location`. `saveOnlyUniqueItems: true` cuts
  Indeed-side dupes before Step 5.

### `memo23/glassdoor-scraper-ppr`
- Input is `startUrls` (Glassdoor **company-page URLs**) plus a `command`/section
  selector — there is **no `companyName` field**. Find the URL via a SERP for
  "<company> glassdoor".
- The section selector's exact name/values vary by version — fetch the live schema first.
  Set `command: "salaries"` explicitly (the default is `reviews`) and **always set
  `maxItems`** (default 20,000 per URL). Leave the separately billed add-ons
  (`painPointAnalysis`, `reviewInsights`, `enrichEmails`) at their `false` default.
- Verify the returned company is the right entity (generic names mis-match) before
  trusting the salary figures; surface the matched Glassdoor URL in the output.

## Data-quality reminders

- **Empty results are signal**, not failure — 0 niche roles in a small market is
  real information. Report it; suggest a concrete loosening. Never fabricate filler.
- **Recency is signal.** A 45-day-old "urgent" req is often filled — flag, don't hide.
- **Disclosed ≠ accurate.** Posted bands can be aspirational; cross-check against the
  Glassdoor salary benchmark (analysis mode) when comp matters.
- **One board's silence isn't the market.** Zero in-area rows on one board usually
  means a block, not no jobs — run that board's standalone fallback Actor where one
  exists (Indeed), and where none does (LinkedIn), say so in the header.
