# Gotchas and cost guardrails

## Cost

- Billing is per delivered row, so always set `maxItems` while exploring. One list can hold more than 8,000 investors.
- Enrichment bills per unique firm, not per row, and a firm appearing on many rows is charged once.
- Unresolved firms are never charged, so a partial enrichment result costs less, not more.

## Speed

- Enrichment does company-name lookups in chunks, so a run covering 75 firms can take about 20 minutes. Without enrichment the same run finishes in seconds.
- `pageSize` controls how many investors are requested per page. The default of 50 is a good balance.

## Data

- Check-size fields are empty when the investor does not publish a range. They are never estimated.
- Geography is modeled as a list, not as a filter on investors. Use the geographic list slugs.
- Rows carry `result_type`: `investor`, `firm`, `list`, or `error`. Filter on it rather than assuming a shape.
- An `error` row means one list slug failed; the rest of the run still delivers.

## Recovery

- Empty output almost always means a wrong slug. Run `mode: "lists"` and copy the exact `slug`.
- If a run hits its charge limit it stops early and finishes cleanly, returning what it already delivered.
