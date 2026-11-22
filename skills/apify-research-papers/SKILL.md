---
name: apify-research-papers
description: "Answer research-literature questions from OpenAlex, Crossref, arXiv and PubMed with the Apify Actor extractlyspace/academic-papers-search, and pick the search for the question: topic search, most-cited papers, preprints, DOI lookup, or impact plus evidence when the user asks whether there is consensus. For a consensus or evidence question in medicine, health or biology it runs two calls automatically: OpenAlex sorted by citations for the papers that shaped the field, and PubMed restricted to systematic reviews and meta-analyses for what the evidence says. Returns one row per paper: title, authors, year, venue, type, DOI, link, free PDF link, open-access flag, citation count and abstract, merged across sources by DOI. Use for: literature search, most cited papers on a topic, is there scientific consensus, what does the evidence say, systematic reviews on a topic, recent papers, papers by an author, resolve DOIs or arXiv ids. Not for full texts, Google Scholar or patents. Pay per paper returned, no start fee."
author: extractlyspace
author_url: https://apify.com/extractlyspace
license: MIT
metadata:
  version: "1.0"
  category: research
  keywords: "research-papers, academic-search, literature-review, openalex, pubmed, arxiv, crossref, systematic-review, meta-analysis, citations, scientific-consensus"
---

# Research papers: impact and evidence

Turn a question about the research literature into the right search over OpenAlex, Crossref, arXiv and PubMed, and answer from the rows.

Disclosure: this skill routes to a paid Actor built by the author (extractlyspace).

## Example prompts

Prompts this skill handles:

- "Microplastics and human health: what are the most cited papers, and is there a consensus?"
- "Find 20 recent open-access papers on malaria vaccines."
- "Give me title, authors, abstract and a PDF link for 10.1038/nature14539 and arXiv:1706.03762."

Out of scope (the boundary):

- "Summarize the full text of this paper." The rows carry abstracts and links, not full texts.
- Patents, grants or Google Scholar profiles. None of the four sources covers them.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable

## Workflow

1. **Classify the question** before the first call. This decides the sources and the sort:

| The user asks | Call | Input |
|---|---|---|
| Papers on a topic, recent work | one | all sources (leave `sources` empty), `sort: relevance` or `newest` |
| Most cited, landmark or foundational papers | one | `sources: ["openalex"]`, `sort: most_cited` |
| **Is there consensus, what does the evidence say, does X cause or treat Y** (medicine, health, biology, environment and health) | **two** | impact call: `sources: ["openalex"]`, `sort: most_cited`, `includeAbstract: false`; evidence call: `sources: ["pubmed"]`, PubMed query below, `sort: newest`, `fromYear` about ten years back |
| The same consensus question outside the life sciences | one | `sources: ["openalex"]`, `sort: most_cited`; then read the rows with `type: review` first |
| Preprints, machine learning, physics | one | `sources: ["arxiv"]`, `sort: newest` |
| Known DOIs or arXiv ids | one | `dois: [...]`, no `query` |
| Papers by one person | one | `author` with the full name, plus a `query` |

2. **Build the evidence query for PubMed** by wrapping the topic: `(microplastics) AND (human health) AND (systematic review[pt] OR meta-analysis[pt])`. The `[pt]` tags only work when `sources` is `["pubmed"]` alone; sent to the other sources they are searched as plain words.
3. Fetch the input schema once if anything is unclear. Do not guess field names.
4. Run the call or calls. Each costs at most `maxResults x $0.0005`; the two-call consensus check with 15 + 10 papers costs about $0.0125.
5. **Answer from the evidence rows first.** Say how many reviews were found, the newest year, and what their abstracts conclude, and quote the titles. Use the impact rows for context ("the most cited work on the topic is ..."). If the evidence call returns `no_results`, say that no systematic review or meta-analysis was found, which is itself an answer; do not report a consensus from citation counts alone.
6. Separate the rows by `recordType`: `paper` rows are the result; `status` rows are free and explain what is missing. Tell the user about every `partial` and `not_found` row.

**Avoid unauthenticated Semantic Scholar for this.** Its shared public pool answers most requests with status 429, so a Semantic Scholar step often returns nothing at all. This Actor does not use Semantic Scholar; OpenAlex gives the citation counts.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Papers from OpenAlex, Crossref, arXiv and PubMed in one call, merged by DOI | `extractlyspace/academic-papers-search` | community | Topic searches, most-cited lists, PubMed reviews, DOI lookups |

## Run it with the Apify CLI

Fetch the input schema:

```bash
apify actors info "extractlyspace/academic-papers-search" --input --json \
  --user-agent apify-awesome-skills/apify-research-papers \
  2>/dev/null
```

Consensus check, impact call:

```bash
apify actors call "extractlyspace/academic-papers-search" \
  -i '{"query":"microplastics human health","sources":["openalex"],"sort":"most_cited","maxResults":15,"includeAbstract":false}' \
  --json \
  --user-agent apify-awesome-skills/apify-research-papers \
  2>/dev/null
```

Consensus check, evidence call:

```bash
apify actors call "extractlyspace/academic-papers-search" \
  -i '{"query":"(microplastics) AND (human health) AND (systematic review[pt] OR meta-analysis[pt])","sources":["pubmed"],"sort":"newest","fromYear":2016,"maxResults":10}' \
  --json \
  --user-agent apify-awesome-skills/apify-research-papers \
  2>/dev/null
```

Recent open-access papers on a topic:

```bash
apify actors call "extractlyspace/academic-papers-search" \
  -i '{"query":"malaria vaccine","sort":"newest","openAccessOnly":true,"maxResults":20}' \
  --json \
  --user-agent apify-awesome-skills/apify-research-papers \
  2>/dev/null
```

Look up known papers:

```bash
apify actors call "extractlyspace/academic-papers-search" \
  -i '{"dois":["10.1038/nature14539","arXiv:1706.03762"]}' \
  --json \
  --user-agent apify-awesome-skills/apify-research-papers \
  2>/dev/null
```

The call prints the run as JSON. Read the rows from its `defaultDatasetId`:

```bash
apify datasets get-items <DATASET_ID> --format json \
  --user-agent apify-awesome-skills/apify-research-papers \
  2>/dev/null
```

## What you get

One row per paper, always with the same fields:

- `recordType` (`paper`), `title`, `authors`, `firstAuthor`, `year`, `publicationDate`, `venue`, `type`
- `doi`, `url`, `pdfUrl`, `isOpenAccess`, `citationCount`, `abstract`
- `sources` (where it was found: `openalex`, `crossref`, `arxiv`, `pubmed`), `openalexId`, `arxivId`, `pmid`, `scrapedAt`

A value no source provides is `null`. `citationCount` comes from OpenAlex, otherwise Crossref, so PubMed-only and arXiv-only rows have `null` there. `type` is `review` for reviews; PubMed lists a meta-analysis as `article` or `review`, so read the title too.

Rows with `recordType: "status"` carry `status`, `message` and `subject`. The `status` is one of `no_results`, `not_found`, `partial`, `invalid_input`, `limit_reached`, `unavailable`.

## Cost

- $0.0005 for each paper returned. `status` rows are free. No start fee.
- `maxResults` is 1 to 200 (default 20), so one call costs at most $0.10.
- `includeAbstract: false` makes the rows smaller but does not change the price.

## Troubleshooting

- PubMed tags such as `[pt]` or `[tiab]` are PubMed's own syntax and the other sources do not understand them. Send a tagged query with `sources: ["pubmed"]` alone.
- `most_cited` returns old papers that drift off topic: it sorts what the sources found for the words, it does not rank a whole field. Narrow the `query` or add `fromYear`.
- A `partial` row: one source did not answer; the papers come from the others. Run again later for the missing one.
- An `unavailable` row for OpenAlex: citation counts are missing for this run; Crossref still gives counts for DOIs it knows.
- The run fails only when no source could be read. Retry once; if it fails again, report the run ID on the Actor's issue page on Apify.
- More in [references/gotchas.md](references/gotchas.md).
