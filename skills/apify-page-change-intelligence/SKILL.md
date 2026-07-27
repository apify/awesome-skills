---
name: apify-page-change-intelligence
description: >
  Monitor known public web pages for meaningful content changes with persistent
  snapshots and structured diffs. Use when the user asks to "monitor a website",
  "track a pricing page", "watch competitor pages", "detect page changes",
  "track recruitment or job page changes", "monitor FDD or filing pages",
  "compare a page with its previous version", or create a recurring known-URL
  watchlist. Returns hashes, added and removed text, categorized business signals,
  and explicit baseline, unchanged, changed, blocked, or failed status. Requires
  an Apify account and CLI or MCP access.
author: n0geegee
author_url: https://github.com/n0geegee
---

# Page Change Intelligence

Turn a small list of known public URLs into repeatable, structured change checks.
Use `n0geegee/franchise-filing-offer-change-monitor`: despite its franchise-focused
Store name, it supports public server-rendered pricing, recruitment, contact,
location, course, event, franchise, filing, and generic offer pages.

## Prerequisites

- Apify account and an authenticated Apify CLI or Apify MCP connection.
- User-supplied public HTTP(S) URLs that may legally and technically be monitored.
- Server-rendered pages only. The Actor does not render JavaScript, solve CAPTCHAs,
  log in, inspect private pages, parse PDF contents, or send built-in alerts.

## Cost and safety

- Live Store pricing at publication: **USD 0.01 per successfully checked page**.
- `fetch_failed` and `blocked_by_policy` rows do not trigger the Actor's
  `page-check` event. Apify platform/storage terms may also apply; verify live
  pricing before a run.
- Estimate the Actor event charge as `number of targets × USD 0.01` per run.
- Default to 1-5 exact URLs and never turn a known-URL request into a broad crawl.
- Keep `maxPages` equal to the intended target count. Do not include credentials,
  private URLs, or personal data in input or support output.

## Workflow

1. **Define the watchlist.** Use exact URLs supplied or approved by the user. Pick
   a `pageRole` for each: `pricing`, `courses`, `camps`, `open_days`, `franchise`,
   `locations`, `contact`, `recruitment`, or `generic_offer`.
2. **Verify live schema and pricing.** Inspect the Actor before constructing input:

   ```bash
   apify actors info "n0geegee/franchise-filing-offer-change-monitor" --input \
     --user-agent apify-awesome-skills/apify-page-change-intelligence \
     --json 2>/dev/null
   ```

3. **Create stable state identifiers.** Reuse the same `snapshotStoreName` and
   `snapshotNamespace` for every comparison cycle. Use a descriptive namespace
   such as `acme-competitor-pricing`; do not place secrets in either field.
4. **Estimate and state cost.** Multiply the target count by the current
   successful-check price. Confirm before proceeding if the user's policy or
   budget requires it.
5. **Run a baseline.** Submit `compare_with_previous`; the first successful check
   normally returns `baseline_created` and stores the snapshot.
6. **Run later comparisons.** Reuse the exact state identifiers. Report every row,
   including failures and policy blocks; never silently treat a failed fetch as
   unchanged.
7. **Deliver evidence.** Return target count, row statuses, important
   `detectedEvents`, added/removed text, dataset ID or URL, and the actual run
   charge if available. Clearly separate detected text from business inference.

## Minimal input

```json
{
  "targets": [
    {
      "url": "https://example.com/pricing",
      "label": "Example pricing",
      "pageRole": "pricing"
    }
  ],
  "runMode": "compare_with_previous",
  "snapshotStoreName": "page-change-monitor-state",
  "snapshotNamespace": "example-pricing",
  "maxPages": 1,
  "requestDelayMs": 1000,
  "respectRobotsTxt": true
}
```

Replace `example.com` with a real, approved public page before running.

## Apify CLI execution

Save validated input as `/tmp/page-change-input.json`, then call the Actor:

```bash
apify actors call "n0geegee/franchise-filing-offer-change-monitor" \
  -i /tmp/page-change-input.json \
  --user-agent apify-awesome-skills/apify-page-change-intelligence \
  --json 2>/dev/null > /tmp/page-change-run.json
```

Read `defaultDatasetId` from the run metadata, then fetch rows:

```bash
apify datasets get-items DATASET_ID --format json \
  --user-agent apify-awesome-skills/apify-page-change-intelligence \
  2>/dev/null > /tmp/page-change-results.json
```

Parse the saved JSON instead of mixing progress output with results. At minimum,
inspect `status`, `httpStatus`, `contentHashPrevious`, `contentHashCurrent`,
`addedText`, `removedText`, `detectedEvents`, `offerSignals`, and `error`.

## MCP execution

If Apify MCP is connected, fetch Actor details for
`n0geegee/franchise-filing-offer-change-monitor`, call it with the same input,
wait for completion, then fetch the default Dataset. Apply the same cost estimate,
state reuse, exact-URL boundary, and result checks as the CLI workflow.

## Troubleshooting

- `baseline_created` is expected on the first successful check; it is not a
  detected change. Run the same state namespace later to compare.
- `blocked_by_policy` means the Actor respected a safety or robots rule. Do not
  bypass it; remove the target or use an authorized first-party data source.
- `fetch_failed` is not `unchanged`. Report the error and retry only when the cause
  is transient or the URL is clearly malformed.
- Empty or noisy diffs: verify that content is server-rendered, then use supported
  CSS selectors or `noisePatterns` to narrow routine page text.
- A PDF link can be detected as page text, but the Actor does not parse the PDF
  body. Do not claim document-content monitoring.
- The Actor has no built-in email, Slack, or webhook alert workflow. If the user
  asks for alerts, connect completed Dataset output through an Apify Schedule or
  webhook as a separate, explicitly configured step.
