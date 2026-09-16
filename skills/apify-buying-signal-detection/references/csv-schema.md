# `leads.csv` column contract

The aggregate script appends new rows to this file. All columns are strings; empty
cells are `""`, never `null`. The file is a plain CSV with a header row.

| Column | Type | Notes |
|---|---|---|
| `detected_at` | ISO 8601 UTC timestamp | When `aggregate.py` wrote this row. Also the idempotency key — the aggregator checks the max `detected_at` and skips if within the current ISO week. |
| `company` | string | Company name as returned by the Actor. Lightly normalized (trailing `Inc`/`Ltd` kept, whitespace collapsed). |
| `domain` | string (lowercased) | Primary dedup key, and only ever the company's *own* domain. Sourced from Actor output; falls back to the company website URL if the Actor returns a URL instead of a bare domain. Job boards and social networks (`linkedin.com`, `indeed.com`, `stepstone.de`, `crunchbase.com`, …) are rejected rather than stored — see `NON_COMPANY_HOSTS` in `aggregate.py`. Empty is therefore common, not rare: the LinkedIn jobs Actors only return a `linkedin.com/company/<slug>` URL, so every row from that signal is domainless and dedupes on the company name instead. |
| `signal_type` | enum | One of `jobs`, `funding`, `linkedin_content`. |
| `signal_detail` | string | One-line human-readable signal summary. Examples: `"Hiring 3x Account Executive - EMEA"`, `"Raised $12M Series A led by Accel"`, `"Post: 'outbound is broken'"`. Free-form; the aggregator generates it per signal type. |
| `signal_source_actor` | string | Apify Actor ID that produced this row (e.g. `bebity/linkedin-jobs-scraper`). Lets you trace back to the source dataset. |
| `signal_date` | ISO 8601 date | Date the signal event happened (post publish date, funding announcement date, job posting date). May be empty if the Actor doesn't expose it — post-filters that depend on recency (`max_days_since_announcement`, `posted_within_days`) skip rows with empty dates so nothing false-positive gets through. |
| `evidence_url` | URL | Direct link to the source page (LinkedIn post URL, TechCrunch article, job listing). Non-empty when the Actor exposes a URL — required for the row to be considered valid. |
| `geo` | ISO 3166-1 alpha-2 or empty | Best-effort country tag. Empty when the Actor doesn't expose country. |
| `notes` | string | Aggregator scratch column — currently used for `"seniority mismatch (post-filtered)"` audit notes and blacklist near-miss warnings. |

## Dedup rules

Order of precedence when a new row collides with an existing row:

1. **Identical `domain`**: existing row wins (first-seen is preserved). The incoming
   row is dropped. The signal that first surfaced this lead stays authoritative — a
   later, weaker signal shouldn't overwrite it.
2. **Identical normalized `company`, different `domain`**: both rows kept. Different
   domains for the same brand name are almost always different entities (subsidiaries,
   regional offices, or unrelated companies that happen to share a name).
3. **Identical normalized `company`, both rows domainless**: existing row wins, and the
   incoming one is counted under `dropped.dup_company`. This is the working key for the
   jobs signal, where no Actor returns an employer domain — three postings from one
   company become one lead.
4. **Identical `evidence_url`**: dropped as a re-scrape of the same source. Guards
   against the same Actor run being aggregated twice.

Normalization for company-name comparison: lowercase, strip punctuation, collapse
whitespace, drop trailing corporate suffixes (`inc`, `ltd`, `gmbh`, `sa`, `sarl`, `bv`, `llc`).

## Blacklist matching

Blacklist rows check both `domain` and normalized `company`. Domain match is exact
(`sub.example.com` won't match a blacklist entry of `example.com` — add both if you
want subdomain coverage). Company match uses the same normalization as dedup.

## Weekly idempotency

Before pulling new data, `aggregate.py` reads the CSV's max `detected_at`. If it
falls in the current ISO week (Monday 00:00 UTC through Sunday 23:59 UTC), the
script exits with `"skipped: already run this week"` and no HTTP calls are made.
This lets you set the Claude-side schedule to fire more often than weekly (safety
net for missed runs) without cost impact.

## Full example

See [`examples/leads.example.csv`](../examples/leads.example.csv).
