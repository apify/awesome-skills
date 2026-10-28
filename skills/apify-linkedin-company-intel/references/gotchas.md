# Gotchas — apify-linkedin-company-intel

## Cost guardrails

All three Actors are pay per event (no monthly rental). Check live prices before a large run:

    apify actors info "saliga/linkedin-company-search" --json \
      --user-agent apify-awesome-skills/apify-linkedin-company-intel 2>/dev/null

Look at `pricingInfo` / `pricingInfos` in the output.

| Actor | Charged event | What is free |
|-------|---------------|--------------|
| `saliga/linkedin-company-search` | each **matching** company | companies that do not match the filters, pages that could not be read, the job searches used for discovery |
| `saliga/linkedin-company-scraper` | each company row (`companies` output) or each post row (`posts` output) | inputs not found, websites without a LinkedIn page, failures, posts already seen by the monitor |
| `saliga/linkedin-jobs-scraper` | each job row (`jobs` output) or each company row (`companies` output) | duplicates across searches, jobs removed by your filters, jobs already seen by the monitor |

Estimate = expected rows × event price. Suggested thresholds: warn above ~$5, require explicit confirmation above ~$20. All three Actors respect the per-run spending limit set in Apify and stop cleanly when it is reached.

## Known limits

- **No people.** Employee lists, profile photos and posts written by people are skipped on purpose. Do not promise names, titles or emails.
- **Search is discovery, not a full directory.** LinkedIn's own company search needs a login; `linkedin-company-search` finds active companies via hiring and "Similar pages". Narrow filters need a higher `maxPagesToCheck`.
- **Look-alikes follow size.** Similar pages of a large company are mostly large companies. For small targets, seed with small companies or use keywords. `lookAlikeDepth` 2-3 widens results but drifts from the topic.
- **Up to 10 posts per company** are visible to signed-out visitors. For a history, schedule the posts monitor.
- **External apply links are not available** for LinkedIn jobs to signed-out visitors; `easyApply: false` means the job is applied for on the company's own site.
- **Short page names can belong to someone else** — prefer full links or website domains.
- **`followers` may be missing** on some large pages; it is omitted, not zero.

## Common errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Run succeeded with 0 or few results | Filters too narrow, or every candidate rejected (see status message: "Not matching: 45 size, …") | Loosen the named filter, add keywords/locations, raise `maxPagesToCheck` |
| Rows with `error: "Page not found on LinkedIn"` | Wrong page name | Use the full LinkedIn link or the website |
| `error` mentions a sign-in wall | LinkedIn rate-limited the proxy addresses | Re-run with the RESIDENTIAL proxy group; failed rows are free |
| Website row with `No LinkedIn company page found` | The site does not link to LinkedIn and no page name matches the domain | Pass the LinkedIn link directly |
| Monitor returns nothing on the second run | Working as intended: no new posts/jobs | Use a different `monitorName` to start fresh |

## Actor-specific notes

### `saliga/linkedin-company-search`

- Default memory is 2 GB (page parsing is CPU-bound); a 60-company search took ~4 minutes in testing.
- `foundVia` explains each row; keep it when exporting, it helps users judge relevance.

### `saliga/linkedin-company-scraper`

- `websites[]` lookup: first the LinkedIn link on the site, then page names guessed from the domain, accepted only if that LinkedIn page lists the same website (`foundBy` says which).
- `jobsUrl` can be passed to `linkedin-jobs-scraper` as a `searchUrls` entry.

### `saliga/linkedin-jobs-scraper`

- `staffingAgency` flags recruiter reposts (agency names and ad wording like "our client is"); `excludeStaffingAgencies` drops them for free.
- LinkedIn returns about 1,000 jobs per search at most; split large searches by keyword or location.
