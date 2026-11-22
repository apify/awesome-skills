# Gotchas: research papers

## Picking the sources

| Need | Sources | Why |
|---|---|---|
| Citation counts, most-cited lists | `openalex` | OpenAlex has counts for most works; Crossref only for DOIs it knows; arXiv and PubMed have none |
| Evidence grading in medicine, health, biology | `pubmed` alone | PubMed's publication-type tags (`systematic review[pt]`, `meta-analysis[pt]`, `randomized controlled trial[pt]`) select the study design |
| Preprints | `arxiv` | Newest versions first with `sort: newest`; arXiv allows one request every three seconds, so a call with arXiv takes about three seconds longer |
| Everything on a topic | leave `sources` empty | Each source is asked for up to `maxResults` papers, then merged by DOI, arXiv id or PubMed id |

## Evidence levels for a consensus answer

Read the evidence call's rows in this order and say which level the answer rests on:

1. Systematic reviews and meta-analyses (the PubMed `[pt]` query).
2. Randomized controlled trials: rerun with `randomized controlled trial[pt]` when no review exists.
3. Highly cited single studies from the impact call: context only, never a consensus on their own.

Say so when the newest review is more than five years old.

## Cost guardrails

- $0.0005 per paper; `maxResults` caps a call at $0.10.
- For a scheduled "what's new" check, use `sort: newest` with `fromYear` set to the current year and a small `maxResults`; a daily run of 20 papers costs $0.01.
- `status` rows are never charged.

## Matching

- Records merge only on a shared DOI, arXiv id or PubMed id. A preprint and its journal version with different DOIs can appear twice.
- `author` uses each source's own name matching. A common surname can match other people; add a `query`.
- PubMed matches loosely: check that the titles fit the topic before you answer, and put phrases in quotes (`"human health"`) when they drift.
- `openAccessOnly` trusts what each source says. Crossref counts only records with an open (Creative Commons) licence.

## Status rows

| `status` | Meaning | What to do |
|---|---|---|
| `no_results` | No paper in the chosen sources matches | For an evidence call this is an answer: no review found. Otherwise widen the query or drop filters |
| `not_found` | A listed DOI or arXiv id is unknown to the sources that answered | Check the id; the other papers are returned |
| `partial` | One source did not answer | The papers come from the others; run again later |
| `unavailable` | OpenAlex cannot be read at the moment | Counts are missing; Crossref still has counts for DOIs it knows |
| `invalid_input` | No query and no DOIs, a bad DOI, `fromYear` after `toYear`, more than 50 DOIs | The message says what to change |
| `limit_reached` | The run's spending limit was reached | Raise the limit or lower `maxResults` |
