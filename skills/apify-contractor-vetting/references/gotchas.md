# Gotchas

Measured on a real vetting run (one contractor, all steps).

## Cost

- A full vet (licence, entity, complaints) cost a few cents in Actor events at small `maxResults`.
- Name searches cost more than number searches: a common name returns many licences, and each row is billed.
  Search by licence number when the user has one, and keep `maxResults` low (5 to 10) on name searches.
- Do not run the same search twice to "double check": read the first result.

## Failure modes and fixes

| What happens | Why | Fix |
|---|---|---|
| Entity search returns only lookalikes ("Delta Builders Co" vs "Delta Builders Group Inc") | The licence is held under a legal or trade name the user did not give | Re-search with the licence's business name, its DBA and listed officers; still none, mark a gap |
| Several licences match one name | Common names, family firms, branches | Match on business name AND city, or ask the user for the city or licence number |
| No complaints Actor for the state | Coverage varies by state | Say no complaint data was checked; the verdict cannot be CLEAR on complaints alone |
| Empty result | Spelling, suffixes (LLC, Inc), punctuation | Retry once with the shortest distinctive part of the name |
| Licence active but wrong classification | A general licence is not a speciality one (e.g. electrical) | CAUTION, and name the classification the job needs |
| Search returns an Actor for a neighbouring state | Store search is fuzzy | Check the state in the Actor's title before running it |

## Verdict discipline

- Missing data is a gap, never a clean record.
- An old sole proprietorship may have no entity record: that alone is not a red flag.
