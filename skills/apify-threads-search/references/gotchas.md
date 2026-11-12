# Gotchas — cost, limits, stop reasons and recovery

## Cost

| Event | Price | How many |
|---|---|---|
| Actor start | $0.02 free plan / $0.005 paid, **per GB of memory** | 4 per run (4 GB) — $0.08 free, $0.02 paid |
| Stored row | $0.0025 | One per row in the dataset |

| What you ask for | Rows at most | Free plan | Paid plan |
|---|---|---|---|
| 1 keyword, `max_posts: 10` | 10 | $0.105 | $0.045 |
| 1 keyword, `max_posts: 100` | 100 | $0.33 | $0.27 |
| 5 keywords, `max_posts: 200` | 1,000 | $2.58 | $2.52 |
| 3 accounts, `max_posts: 500` | 1,500 | $3.83 | $3.77 |

You pay for rows stored, and public availability often stops a run below the ceiling. The start
is charged on every run that starts — measured on one that stored 0 rows and on one the Actor
failed for a 101-plus-character keyword. Input that breaks the schema (for example
`max_posts: 5`) is rejected before a run exists and costs nothing.

**The cap.** `apify actors call` has no charge-cap flag; the Run API's `maxTotalChargeUsd` does,
reached through `apify api` (CLI 1.5.0 and later). Size the cap from the free-plan estimate: on a
paid plan it is then generous, and on the free plan a cap below $0.08 stores nothing. At the cap
the run ends `SUCCEEDED`, `partial`, `budget_reached`, with every row already saved and a status
message saying to raise the limit. Measured: $0.06 → 16 rows and $0.03 → 4 rows on a paid plan,
each exactly the start plus the rows.

**Settled cost.** `chargedEventCounts` (`apify-actor-start`, `apify-default-dataset-item`) can read
0 row events right after a run ends and the real count seconds later; Step 4 re-reads until the
row events match the rows. Filter `apify runs info --json` through `jq` as Step 4 does —
unfiltered, it prints the whole Actor and build record, several MB for an Actor you own.

## Limits

| Limit | Value |
|---|---|
| `keywords` / `usernames` per run | 1–20 |
| Characters per keyword | 100 — a longer one fails the run (`Keyword is too long (maximum 100 characters).`), 0 rows, start charged |
| `max_posts` | 10–10000, per keyword or per username |
| Profile discovery | 10 rows per keyword, whatever `max_posts` says |
| Date window | `search` only; `start_date` from 00:00 UTC, `end_date` inclusive to 23:59:59 UTC |
| Per run | One `mode`, one `search_filter` — a comparison is two runs |

## Stop reasons and per-input counts

`collection_stop_reason` describes this run only. `requested_limit_reached` means at least one
input reached `max_posts`, not each; `budget_reached` means the cap was hit. The Actor README lists
every value under "How to read account stopping reasons" and "How to read Search stopping
reasons" (for example `no_more_public_posts`, `no_more_public_accounts`, `mixed_item_results`):

```bash
apify actors info "futurizerush/meta-threads-scraper" --readme \
  --user-agent apify-awesome-skills/apify-threads-search </dev/null
```

Before saying each input got its quota, count per input (`$THREADS_WORK` from SKILL.md Step 2):

- search — `jq '.search_items[] | {keyword, results_saved, stop_reason}' "$THREADS_WORK/output.json"`
- account modes — `jq 'group_by(.requested_username) | map({(.[0].requested_username): length}) | add' "$THREADS_WORK/rows.json"`
- profiles — `jq 'group_by(.search_keyword) | map({(.[0].search_keyword): length}) | add' "$THREADS_WORK/rows.json"` (first matching keyword only)

## Recovery

| Symptom | What it means | What to do |
|---|---|---|
| A command never returns | It ran without `</dev/null` in a shell whose stdin stays open; or `key-value-stores get-value` asked for a key that does not exist | Add `</dev/null`; read records with `apify api GET`, which answers `record-not-found` instead of hanging |
| `Not started: …` | The Run API rejected the request | Read the message: input, login, or a CLI older than 1.5.0 |
| `rows: 0` | This run's logged-out search found nothing for this exact input — not proof no matching public post exists | Confirm spelling, then offer **one** shorter query or a wider window and ask first |
| `Run FAILED` | The Actor's message says why | Fix the input; the start was charged |
| `partial` | The run ended with requested rows still missing | Report partial with the stop reason; do not retry silently |
| Rows outside the window | No window was sent, or `recent` was taken for a range | Send absolute `start_date` / `end_date` |
| Rows cover a fraction of the window | Rows are a sample; `max_posts` too small | Raise `max_posts` and report the span covered |
| Fewer rows than `max_posts` | It is a ceiling, and thread continuations use it up in `user` mode | Say so; raise `max_posts` only with a yes |
| Cost above the estimate | `max_posts` was read as a run total | It is per keyword or per username |
| A profile does not fit the niche | A keyword match on a name or bio is not a relevance check | Read the bio before recommending the account |

## What the data does not prove

Logged-out Threads search is ranked, not exhaustive. `collection_status: complete` means this
run finished what it planned — never that every matching post on Threads was seen. No answer
built on these rows can claim complete coverage, a total count of mentions, or an author's
location: a place word in a query is query text, not a verified attribute.
