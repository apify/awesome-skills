# Cost guardrails and error recovery: government registries

## Confirm live prices before a batch

Prices change. Read them from the live Actor:

```bash
apify actors info "regdata/krz-debtor-scraper" --json \
  --user-agent apify-awesome-skills/apify-government-registries \
  2>/dev/null
```

If the metadata cannot be parsed, use `apify api` to GET `/v2/acts/regdata~krz-debtor-scraper` with the same skill user-agent. Keep authentication in the CLI or an `Authorization: Bearer` header, never in the URL.

## Cost model

- **Start fee + per record** (CRBR, Handelsregister and most profile Actors): the start fee is charged once per run, so put every company into one run instead of one run per company. One company per run costs about four times as much per record as a batch of 100.
- **Per search + per result** (KRZ): each identifier is a search. Narrow with `proceedingKinds` (for example `["bankruptcy","restructuring"]`) to skip enforcement rows you would not use; skipped rows are not charged.
- **Per check** (`poland-kyb-check`): the Actor calls the REGON, CRBR and KRZ Actors on your account, so their fees appear on your bill next to the orchestration fee. Each beneficial owner adds two insolvency searches. A company with many owners costs more.
- **Per name** (`adverse-media-screener`): one charge per entity screened.

Rule of thumb: mention cost under about $5, warn over about $5, get explicit sign-off over about $20.

## Guardrails

1. Run one identifier first and check the row shape before a batch.
2. De-duplicate identifiers before the run. Repeated IDs are searched and billed again.
3. Prefer identifiers over names. A name search in KRZ or Handelsregister can return many candidates, each billed.
4. Monitoring: the KRZ and Handelsregister Actors accept `onlyNew` with a `monitorKey` so a scheduled run returns only what changed since the last run. Use this for watchlists instead of re-pulling everything.

## Error recovery

- `verdict: "partial"` (KYB check): a source register was unreachable. Re-run later. The orchestration fee is not charged, but component lookups that did run are.
- `verdict: "not_found"` or `found: false`: no entity under that ID. Usually a typo; confirm the ID with the user.
- `sanctionsListStatus: "unknown"` or `screeningStatus: "unavailable"` (adverse-media screener): one half of the screen could not run. The row says which. Do not report the entity as clear; re-run.
- KRZ `proceedingsComplete: false`: not every proceeding could be listed. Search by NIP or KRS instead of by name.
- Empty dataset with a `SUCCEEDED` run: check the run log for a validation message about the input (wrong field name, unsupported value) and compare against the input schema.
- Before retrying a failed or timed-out call, check the original run's status so a lost response does not start a second paid run.
