# Cost guardrails and error recovery

## Live prices, not remembered ones

```bash
apify actors info "johnvc/ashby-job-board-scraper" --json \
  --user-agent apify-awesome-skills/apify-ashby-jobs-scraper \
  2>/dev/null
```

Read `pricingInfos` from the output. Events are per delivered row; filtered rows are never charged, and there is no start fee.

## Guardrails

- Cap every exploratory run: `maxJobs: 25` (jobs) or `maxCompanies: 25` (discovery) until the row shape is confirmed.
- Filters run before billing. Push `titleKeywords`, `employmentTypes`, `remoteOnly`, `publishedAfter`, and `discoveryQuery` into the input rather than filtering downstream.
- Description formats are per-row add-on events. Metadata-only rows (all description toggles off) are the cheapest job rows.
- `includeCompanyData` adds one page request per job and its own event; keep it off for bulk crawls unless the enrichment is the point.
- The whole-run `report` is one flat event; skip it in pipelines.

## Error recovery

- `board_not_found`: check `didYouMean` if present on the error row; paste the board URL when a name will not resolve.
- `job_not_found`: the single-job URL points at a closed posting; fetch the board instead.
- `http_error`: transient upstream answer; retry once, then check the board in a browser.
- `invalid_url`: the entry is not an Ashby slug, name, or jobs.ashbyhq.com URL.
- Errors are in-band dataset rows with `resultType: "error"`; pipelines should branch on `resultType`, not on run status.

## Freshness facts worth knowing

- Ashby publishes no per-job update timestamp anywhere public. `publishedAfter` is a new-postings cutoff, not a changed-jobs cutoff.
- The bundled company directory is refreshed with releases; runtime probes keep counts live between refreshes.
