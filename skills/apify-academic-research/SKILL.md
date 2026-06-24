---
name: apify-academic-research
description: Find and analyze scholarly research across the major open academic databases — search and rank papers by field-normalized impact, run a literature review, trace citation graphs, find similar / foundational / breakout papers, map a field's institutions and funders, compare institutions, build a citation-safe RAG corpus, check whether a preprint is safe to cite, mine biomedical entities and datasets, grade clinical evidence, and look up or disambiguate researchers. Covers all fields via OpenAlex, Semantic Scholar, arXiv, Crossref, PubMed, Europe PMC, CORE, DBLP, and ORCID. Use when the user wants academic papers, peer-reviewed studies, a literature or systematic review, an evidence summary, the most-cited or seminal papers, research trends, a research-funding or institution landscape, or a researcher profile — e.g. "find papers on...", "what does the research say about...", "summarize the literature on...", "who's winning this field".
author: apifyforge
author_url: https://github.com/apifyforge
license: MIT
metadata:
  version: "1.0"
---

# Academic Research — search, review and map scholarly literature

Route a research question to the right academic database, run it, and deliver a synthesized answer (ranked papers, a literature map, a citation trail) rather than a raw result dump. The Actors cover open scholarly sources across every field, with deeper synthesis (literature review, citation graphs, influential-citation ranking, evidence triage) where the source supports it.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)
- Most of these Actors call free, keyless scholarly APIs (OpenAlex, arXiv, Europe PMC, Crossref, PubMed, DBLP, ORCID). Two exceptions: CORE requires a free API key (core.ac.uk), and OpenAlex / Semantic Scholar accept an optional free key to raise rate limits on large jobs. Ask the user for the CORE key when routing there; pass any key as a secret input field, never hard-code it.

## Workflow

1. Classify the intent (keyword search, literature review, citation graph, similar/foundational papers, author lookup, ID lookup, biomedical evidence) and pick the Actor from the routing table.
2. Fetch the Actor's input schema so you build a valid input (field names and modes differ per Actor):
   `apify actors info "ACTOR_ID" --input --json --user-agent apify-awesome-skills/apify-academic-research 2>/dev/null`
3. Confirm scope with the user: field, year range, citation floor, open-access-only, and result count (results are billed per record fetched, so cap `maxResults`).
4. Run the Actor, fetch the dataset, and deliver a synthesized answer — top papers with why they matter, the shape of the literature, key authors — not a raw list. Cite titles, publication years, authors when available, and DOIs. Note that a high citation count signals influence, not necessarily quality or current consensus, and recent work can matter before citations accumulate.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Field intelligence: impact, funders, competitors | `ryanclinton/openalex-research-search` | community | Field-normalized impact (FWCI), institution/funder/author graph, head-to-head institution comparison, topic landscape + opportunity signals, RAG-safe corpus, monitoring; query or identifier (DOI/ORCID/ROR) input |
| Single-answer research intelligence + citation graph | `ryanclinton/semantic-scholar-search` | community | One decision/answer, literature-review clusters, similar + foundational papers, citation-graph walk, author papers, influential-citation ranking |
| Preprint intelligence: read/cite plan, code, RAG | `ryanclinton/arxiv-paper-search` | community | Is a preprint safe to cite (published/accepted/preprint + citationRisk), does it ship code, maturity, reading plan, RAG-ready corpus, monitoring (CS/physics/maths/bio/econ) |
| Bulk metadata + BibTeX/RIS from DOIs | `ryanclinton/crossref-paper-search` | community | Cross-publisher metadata, DOI resolution, BibTeX / RIS / open-access / retraction flags, bulk from a DOI list |
| Biomedical knowledge graph + entity/dataset mining | `ryanclinton/europe-pmc-search` | community | Mines genes / proteins / diseases / chemicals + dataset accessions (GEO/ENA/PDB/UniProt), co-occurrence knowledge graph, emerging entities, bioRxiv/medRxiv preprints, clinical trials |
| Clinical evidence triage + grading | `ryanclinton/pubmed-research-search` | community | PubMed evidence triage: evidence units, evidence level/hierarchy, dedup, RAG-safe flag, decision-oriented summary |
| Usable open-access corpus (verified PDFs) | `ryanclinton/core-academic-search` | community | Verifies full-text PDFs download now, dedups across repositories, research-readiness score, corpus health, RAG corpus (needs a free CORE key) |
| Computer-science publications | `ryanclinton/dblp-publication-search` | community | DBLP CS publications and author bibliographies |
| Researcher intelligence + institution map | `ryanclinton/orcid-researcher-search` | community | Find / verify / rank researchers, same-name identity confidence, Researcher Health score, expert/reviewer shortlists, institution map + comparison, field monitoring |

`Tier` = `apify` (Apify-maintained) or `community` (third-party developer). Every Actor in this table is a `community` Actor.

## Picking the source

- General topic, field impact, who's winning, funders, or competitors → OpenAlex.
- "Just give me the answer", summarize the literature, papers similar to X, trace citations → Semantic Scholar.
- Preprints, is-it-safe-to-cite, does-it-ship-code, cutting edge → arXiv.
- Clinical evidence, what to read first in medicine, evidence grading → PubMed.
- Biomedical entities (genes / diseases / datasets) or a biomedical knowledge graph → Europe PMC.
- Need the actual downloadable PDF or a usable open-access corpus → CORE.
- Computer science specifically → DBLP.
- A researcher, or an institution's people → ORCID.
- Bulk metadata / BibTeX / RIS from a list of DOIs → Crossref.
- When several sources return the same paper, prefer OpenAlex for impact + discovery, Semantic Scholar for citation context, PubMed or Europe PMC for biomedical evidence, and Crossref for DOI/metadata resolution.

## Tracking new research over time

Several of these Actors support scheduled monitoring, which turns a one-off review into a "what's new in this field" feed. Semantic Scholar uses `monitoringStateKey` + `continuousMode`; OpenAlex, arXiv, and CORE use `monitorMode` + `watchlistName`; ORCID monitors a field or watchlist. Each flags new, rising, or retracted work since the last run. Tell the user the first run is the baseline.

## Calling Actors — choose your interface

### Option A: Apify CLI (recommended for portability)

Three flags on every call: `--json` (stable output), `--user-agent apify-awesome-skills/apify-academic-research` (attribution), `2>/dev/null` (suppress progress noise that breaks JSON).

The example inputs below are illustrative. Field names and modes vary by Actor and can change between versions, so always inspect the Actor's input schema (workflow step 2) before building input rather than copying these verbatim.

Worked example — highest field-impact papers on a topic via OpenAlex:

```
apify actors call "ryanclinton/openalex-research-search" \
  -i '{"searchQuery":"retrieval augmented generation","analysisMode":"impact-ranking","minImpactClass":"influential","maxResults":25}' \
  --json \
  --user-agent apify-awesome-skills/apify-academic-research \
  2>/dev/null
```

Worked example — a literature review via Semantic Scholar:

```
apify actors call "ryanclinton/semantic-scholar-search" \
  -i '{"mode":"literature-review","query":"microplastics human health","yearFrom":2020}' \
  --json \
  --user-agent apify-awesome-skills/apify-academic-research \
  2>/dev/null
```

Worked example — which preprints on a topic are safe to cite, via arXiv:

```
apify actors call "ryanclinton/arxiv-paper-search" \
  -i '{"searchQuery":"all:diffusion models"}' \
  --json \
  --user-agent apify-awesome-skills/apify-academic-research \
  2>/dev/null
```

For every other Actor in the table, fetch its schema first (step 2 of the workflow), then build the input the same way.

Other useful commands:

```
# Fetch an Actor's input schema before building input
apify actors info "ACTOR_ID" --input --json --user-agent apify-awesome-skills/apify-academic-research 2>/dev/null

# Fetch results
apify datasets get-items DATASET_ID --format json --user-agent apify-awesome-skills/apify-academic-research 2>/dev/null
```

### Option B: Apify MCP connector

Hosted MCP server at <https://mcp.apify.com>. Documented at <https://docs.apify.com/platform/integrations/mcp>.

### Option C: MCP client of your choice

Standalone CLI client. See <https://github.com/apify/mcpc>.

## Do not use this skill when

- The question is general knowledge the model can answer directly, with no need for primary literature.
- The user wants news articles, blog posts, or general web content rather than scholarly papers — use a web-search or content skill.
- The user needs the full PDF of a paywalled paper — these Actors return metadata, abstracts, and open-access full text only.

## Troubleshooting

- Auth failure → run `apify login` or set `APIFY_TOKEN`.
- 429 / rate-limit errors on a large job → pass the source's free API key in the input to raise the limit, or lower `maxResults`.
- Few or no results → broaden the query, drop the citation floor, or switch source (e.g. OpenAlex for breadth, PubMed/Europe PMC for biomedicine).
- For cost notes (papers billed per fetch) and the free-data caveat, see [references/gotchas.md](references/gotchas.md).
