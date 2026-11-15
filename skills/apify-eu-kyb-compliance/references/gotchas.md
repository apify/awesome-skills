# Gotchas — apify-eu-kyb-compliance

Cost guardrails, error recovery, and the places where register data is easy to misread.

## Cost guardrails

All routed Actors are `PAY_PER_EVENT`. Check current prices with
`apify actors info "ACTOR_ID" --json --user-agent apify-awesome-skills/apify-eu-kyb-compliance 2>/dev/null`
(look at `pricingInfos`).

| Actor | Cost driver | Typical cost |
|-------|-------------|--------------|
| `itulo/eu-sanctions-screen` | $0.01 per run + $0.002 per row; one name can yield up to `maxMatchesPerQuery` rows | 100 names, mostly clear: about $0.25 |
| `itulo/eu-vies-vat-validator` | $0.0025 per VAT number; `includeMemberStateStatus:true` adds 28 rows | 100 numbers: about $0.25 |
| `itulo/france-sirene-company-search` | $0.0025 per company; search mode returns up to `maxResults` (default 100) | Always set `maxResults` in search mode |
| `itulo/uk-companies-house-kyb` | $0.0025 per company, $0.001 per filing/charge item, $0.002 per LEI, $0.003 per ownership chain | `filingHistoryItems: 50` on 1,000 companies adds up to $50; keep it 0 unless asked |
| `itulo/prh-company-events` | $0.01 per run + $0.002 per event; `maxPerEvent` defaults to 500 per event type | A wide window with all event types can return thousands of rows; set `maxPerEvent` |

Platform usage is included in the event prices (none of these Actors uses "pay per event +
usage"). New Apify accounts get free monthly platform credits.

### Confirmation thresholds (suggested)

- Estimated cost **>$5** → warn the user.
- Estimated cost **>$20** → require explicit user confirmation before running.
- Always present cost as a **rough estimate** ("around $X"), not a guarantee.

## Common errors and misreadings

| Symptom | Cause | Fix |
|---------|-------|-----|
| Sirene `lookup` returns 0 items for a real SIREN | Company opted out of commercial reuse (`excludeMarketingOptOut` defaults to `true`); `OUTPUT_SUMMARY` shows `excluded.marketing_opt_out` | For KYB, compliance or credit checks rerun with `excludeMarketingOptOut:false`. Never use those rows for prospecting. |
| Sirene `vatNumberComputed` is `valid:false` in VIES | The number is computed from the SIREN; VAT groups and some large companies use a different number | Ask the user for the VAT number on the invoice; report both results. |
| VIES `valid:false` | Number not registered for intra-EU trade, deregistered, or the national database is down | Run `mode=member_state_status`; if the country is unavailable, retry later and say so. |
| Sanctions `possible_match` | Fuzzy similarity, not identity (e.g. "Rosneft" matches "ROSNEFT AERO") | Human review against the Official Journal. Do not lower `fuzzyThreshold` to make hits disappear. |
| Sanctions `clear` | No entry above the threshold on the EU list of `listPublicationDate` | Report as "no EU FSF match on <date>"; it says nothing about UN, OFAC or UK lists. |
| GLEIF `gleif_search` by `gleifRegisteredAs` returns 0 | National numbers are stored in each registration authority's format | Retry by `gleifName` + `gleifCountry`. |
| GLEIF `registration.status` = `LAPSED` | The LEI was not renewed; the entity can still be active | Report both `entityStatus` and `registration.status`. |
| UK `lookup` without a key returns `lei-record` rows | No Companies House key, so the Actor fell back to GLEIF | Ask the user for their free key, or report GLEIF data as such. |
| PRH `watchBusinessIds` returns nothing on the first run | First run only stores the snapshot | Run again later with the same `alertStateKey`; only changes are emitted. |
| `apify actors call --json` shows no rows | It returns run metadata | Read `storage.defaultDatasetId`, then `apify datasets get-items ID --format json`. |

## Actor-specific notes

### `itulo/eu-sanctions-screen`

- Screens the EU FSF list only. The list date is in every row (`listPublicationDate`).
- Every row carries `disclaimer` and `attribution`; keep them in reports.

### `itulo/eu-vies-vat-validator`

- Input is the full number with country prefix; spaces, dots and hyphens are stripped. Greece is `EL`, Northern Ireland `XI`.
- `reverseChargeCandidate` is a flag for review, not tax advice.

### `itulo/uk-companies-house-kyb`

- Pass the Companies House key through an input file built from an environment variable; never paste it into a command, URL or chat.
- GLEIF requests are spaced at least 1.1 s apart (GLEIF allows 60/min), so large LEI batches take minutes.

### `itulo/prh-company-events`

- Default window is yesterday (back to Friday on Mondays). Set both `dateFrom` and `dateTo` for a custom window.
- Norway mode supports a subset of event types; unsupported ones are listed in `OUTPUT_SUMMARY`. Sole proprietorships are excluded.
