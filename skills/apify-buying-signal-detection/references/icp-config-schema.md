# ICP config schema (`icp.json`)

One JSON file per lead-gen campaign. Both `setup_apify_tasks.py` and `aggregate.py`
read this file — keep them consistent by never editing it by hand once tasks are
provisioned. Add a new campaign file if you need a materially different ICP.

## Top-level fields

| Field | Type | Required | Description |
|---|---|---|---|
| `campaign_name` | string | yes | Short slug (lowercase, dashes). Used as prefix for named Apify tasks (e.g. `<campaign_name>-linkedin-jobs`). |
| `leads_csv` | string (path) | yes | Where the deduplicated leads CSV lives. Relative to the campaign dir. |
| `blacklist_csv` | string (path) | no | Optional path to a CSV with `domain,company,reason` columns. Rows matching either `domain` or normalized `company` are dropped from the append. |
| `signals` | array of enum | yes | Subset of `["jobs", "funding", "linkedin_content"]`. Determines which Actors to provision. |
| `geo` | array of ISO-3166 alpha-2 | yes | Country codes (uppercase). Drives Actor routing — see [`actors.md`](./actors.md). |
| `industry_keywords` | array of string | yes | Keywords describing the target category. Passed to job scrapers as `keyword`, to LinkedIn scrapers as `keywords`, to funding trackers as `industry` when the Actor supports it. |
| `persona` | object | when `signals` includes `jobs` | See below. |
| `funding` | object | when `signals` includes `funding` | See below. |
| `linkedin_content` | object | when `signals` includes `linkedin_content` | See below. |
| `schedule` | object | no | Cron expressions for Apify-side and Claude-side triggers. If absent, defaults are `0 6 * * 1` and `0 8 * * 1` respectively. |

## `persona` (jobs signal)

| Field | Type | Notes |
|---|---|---|
| `titles` | array of string | Job titles the ICP hires for. Passed as `title` (bebity uses the first entry) / `queries` (google-jobs, indeed) / `searchTerms` (regional Actors). |
| `seniority` | array of string | Informational only — not enforced post-hoc. Job Actors don't uniformly expose seniority, so filtering here would drop most rows spuriously. Keep it in the ICP for future reference. |
| `company_size` | array of string | Informational only — same reason. Enrich with a follow-up Actor if you need this filter. |

## `funding` (funding signal)

| Field | Type | Notes |
|---|---|---|
| `stages` | array of enum | One or more of `pre_seed`, `seed`, `series_a`, `series_b`, `series_c`, `growth`. Post-filter in `aggregate.py`. |
| `max_days_since_announcement` | int | Drop rows older than N days. Default 90. |

## `linkedin_content` (linkedin_content signal)

| Field | Type | Notes |
|---|---|---|
| `search_terms` | array of string | Phrases to search LinkedIn posts for. Passed as the `keywords` / `search` field on the Actor. Prefer specific pain-point phrases over broad category names — see [`actors.md`](./actors.md#linkedin-content-signals). |
| `min_reactions` | int | Post-filter. Drop posts with fewer than N reactions. Default 5. |
| `posted_within_days` | int | Post-filter. Drop posts older than N days. Default 14. |

## `schedule`

| Field | Type | Notes |
|---|---|---|
| `apify_side_cron` | cron string | Optional. If present, `setup_apify_tasks.py` creates an Apify Schedule that fires the tasks on this cadence. Omit to run tasks manually / on-demand. |
| `claude_side_cron` | cron string | Informational — used only when registering the Claude scheduled task. |
| `note` | string | Free-form human note. |

## Non-obvious rules the aggregator applies

- `geo` acts as a **routing filter, not a hard gate**: rows where the Actor doesn't
  expose country get through if all other filters match. Better to have false-positive
  leads than to silently drop a Swiss company because the German Actor didn't tag
  country.
- The `linkedin_content` signal is intentionally noisier than the other two —
  pain-point posts are subjective. Expect ~30% of surviving rows to be low-signal
  even after `min_reactions` filtering. Treat this signal as *inspiration*, not
  *qualification*.
- All post-filters run in `aggregate.py`, not in the Actor input. This decoupling
  means you can tighten filters (e.g. raise `min_reactions` from 5 to 25) without
  reprovisioning Apify tasks.

## Full example

See [`examples/icp.example.json`](../examples/icp.example.json).
