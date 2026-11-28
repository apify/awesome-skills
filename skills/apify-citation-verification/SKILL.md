---
name: apify-citation-verification
description: Check a reference list for fake, mismatched or retracted papers before anyone sees it, then format the verified ones. Routes "are these citations real", "check my references for hallucinated papers", "find retracted papers in this bibliography", "verify these DOIs", "format these references in APA / MLA / Chicago / Harvard / IEEE / Vancouver", "turn these DOIs into BibTeX" and "find real papers on <topic> instead of making them up" to Actors that look each reference up in Crossref, OpenAlex, PubMed and Retraction Watch data and return OK / CHECK / FIX per reference with the matched DOI and the differences. Use when an agent or a person has a list of citations (often AI-written) and needs proof they exist and are cited correctly, or needs a formatted bibliography from identifiers. Pay per reference; no API key besides Apify; no scraping of Google Scholar.
author: Panda Federation (pandadad0214) — routes to Actors built by the author; no affiliate or referral parameters
author_url: https://github.com/pandadad0214
metadata:
  category: data-extraction
  keywords: "citations, references, citation-checker, fake-citations, hallucinated-references, retractions, retraction-watch, doi, crossref, openalex, pubmed, bibliography, apa, mla, chicago, harvard, ieee, vancouver, bibtex, ris, literature-search, google-scholar-alternative, research, apify"
---

# Citation verification and formatting

Turn "are these references real?" into a per-reference verdict an agent can act on: each citation, DOI or title is matched against Crossref and OpenAlex (PubMed for biomedical IDs), checked for retractions, corrections and expressions of concern, and returned as OK (verified), CHECK (found, but details differ or a notice exists) or FIX (not found, miscited, a DOI that belongs to another paper, or retracted). Verified items can be formatted in six styles plus BibTeX and RIS in the same flow.

Disclosure: the author of this skill owns the Actors it routes to (`pandadad0214/*`). They are pay-per-result Actors on the Apify Store; no referral or tracking parameters are used anywhere in this skill.

## Example prompts

Prompts this skill handles:

- "Here are the 14 references from my draft. Which ones are fake, wrong or retracted?"
- "Verify these DOIs and give me the verified ones in APA 7 and BibTeX."
- "Find 10 real, recent papers on retrieval-augmented generation in clinical settings, with DOIs and open-access links."

Out of scope (the boundary):

- "Write my literature review / do my assignment for me." The skill verifies and formats sources; it does not write coursework. Plagiarism or AI-text detection is also out of scope.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. Decide the job: verify (Reference Checker), format only (Citation Formatter), or find real papers first (Literature Search). For biomedical evidence tables, use PubMed Evidence Table.
2. Build the input from the user's list: Reference Checker takes `dois`, `titles` or a pasted `bibliography`; Citation Formatter takes `references` (one per item) and `styles`. Fetch the input schema first if unsure.
3. Tell the user the cost ceiling before large runs (price per reference is on each Actor page) and set `maxTotalChargeUsd` on the run. Runs that find nothing for paid events cost nothing.
4. Report the counts (OK / CHECK / FIX), list every FIX with the reason, and link the dataset. Never present a FIX reference as verified.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Check references for fake, mismatched or retracted papers | `pandadad0214/reference-checker` | community | Reference lists, AI-written drafts, peer review |
| Format DOIs / ISBNs / PMIDs / arXiv IDs / messy references | `pandadad0214/citation-formatter` | community | APA, MLA, Chicago, Harvard, IEEE, Vancouver, BibTeX, RIS |
| Find real papers on a topic (Google Scholar alternative) | `pandadad0214/literature-search` | community | Ranked papers with DOIs, citation counts, free PDF links, retraction flags |
| PubMed search to evidence table with PRISMA counts | `pandadad0214/pubmed-evidence-table` | community | Systematic reviews, medical writing |
| Same tools as an MCP server for agents | `pandadad0214/panda-research-mcp` | community | Claude, Cursor or any MCP client |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling Actors

### Option A: Apify CLI

```bash
apify actors call "pandadad0214/reference-checker" \
  -i '{"dois": ["10.1038/nature14539"], "bibliography": "Smith J. A made-up paper title. Nature. 2021;600:1-2."}' \
  --json \
  --user-agent apify-awesome-skills/apify-citation-verification \
  2>/dev/null
```

### Option B: Apify MCP server

Add `https://mcp.apify.com?actors=pandadad0214/reference-checker,pandadad0214/citation-formatter,pandadad0214/literature-search` to the client, or call `call-actor` with the Actor IDs above.

## Gotchas

- A DOI that resolves to a different paper than the citation describes comes back as CHECK or FIX with the differences listed; show the user the mismatch instead of "fixing" it silently.
- Retracted papers are FIX even though they exist. Say so plainly.
- "Not found" means not found in Crossref or OpenAlex, not proof of fabrication: books, grey literature, very new papers and some non-English works can be missing. Tell the user to review not-found items rather than calling them fake.
- Titles with no DOI match on similarity; lower `minMatchScore` (Actor) or `min_match_score` (MCP) only if the user accepts looser matches.
- Reference Checker charges per reference checked, including not-found ones (that verdict is the product). Citation Formatter and Literature Search charge only for resolved items.
