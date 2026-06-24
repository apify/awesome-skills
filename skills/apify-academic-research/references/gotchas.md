# Gotchas — cost, keys, and coverage

## Cost

- These Actors are pay-per-event: a small start fee plus a charge per paper/record fetched. Cost scales with `maxResults`, so set it to what the user actually needs (25-50 is plenty for most reviews) rather than the maximum.
- Multi-query modes (e.g. Semantic Scholar `compare-topics`) bill each query as a separate search. Confirm before running many at once.

## API keys

- Most sources are free, keyless public APIs. CORE is the exception: it requires a free API key (core.ac.uk) or it cannot run. OpenAlex and Semantic Scholar accept an optional free key that raises rate limits on large jobs; without it they share a small global pool and hit 429s faster.
- Keys are secret input fields. Ask the user for the CORE key whenever routing to CORE, and for the optional keys only on large jobs; never hard-code them.

## Coverage and honesty

- No single source is complete. OpenAlex is broadest; PubMed/Europe PMC are biomedical; arXiv is preprints (not peer-reviewed); DBLP is computer science. Pick the source that fits the field, and say which source the answer came from.
- These Actors return metadata, abstracts, and open-access full text. They do not return paywalled full text. Don't imply a complete full-text search of closed literature.
- arXiv results are preprints and may not be peer-reviewed; flag that when it matters to the user's decision.

## Recovery

- A failed run carries a `.consoleUrl` in its run metadata; open it for logs.
- Empty results usually mean too narrow a query or too high a citation floor, not that the literature doesn't exist. Broaden, or switch source.
