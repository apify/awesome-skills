# Gotchas: new-license leads

## Cost guardrails

- **Always set the cap.** `maxItems` (contractors) and `maxResults` (carriers)
  both default to 500. At $0.08 per contractor lead that is about $40, so an
  uncapped "all new contractors in CA, FL and TX" request is a real bill.
- **Estimate before running:** `start fee + cap × per-lead price`. Confirm with
  the user above a few dollars, and say the number back to them.
- **Narrow before you cap.** A classification filter (`C-10`, `Electrical
  Contractor`), a state list or a fleet-size band returns the leads the user can
  actually use; a bare cap only returns the first N of everything.
- **Quiet runs are cheap.** A scheduled only-new run that finds nothing pays the
  start fee only ($0.01 contractors, $0.005 carriers). The first Texas delta run
  is not billed for its baseline.
- **Webhook digests cost $0.03 each** on the carrier Actor, and only when one is
  actually sent (new carriers found and a `webhookUrl` set).

## Only-new modes (deltaMode / monitorMode)

- Each Actor keeps one memory per filter set (states and classifications for
  contractors; states, for-hire, email and fleet size for carriers). Changing
  any of those starts a new watch that reports its whole window again; changing
  only the date window (`issuedWithinDays`, `sinceDays`) keeps the same watch.
- Contractors: CA and FL first delta runs report the recent window normally;
  TX's first run is a silent baseline.
- Carriers: the first monitor run records the `sinceDays` window as a baseline
  and returns nothing (not charged); later runs return only unseen USDOT numbers.
- Keep the schedule tighter than the window (daily schedule, window of a few
  days) so nothing falls between two runs.

## Freshness

- FMCSA's census file lags a real registration by about 2 to 3 days.
- State registries refresh daily; a license issued today can appear tomorrow.

## Compliance

- These are public business license and carrier registrations, published for
  verification. Many new licensees are sole proprietors, so a row can name a
  person. The user is responsible for using the data in line with the laws that
  apply to their outreach (TCPA for calls and texts, CAN-SPAM for email in the
  US). Mention this once when handing over a call or email list.

## Error recovery

| Symptom | Cause | Fix |
|---------|-------|-----|
| Input rejected | Field name or enum guessed | Re-fetch the input schema (SKILL.md, Option A) and rebuild |
| 0 contractor rows on a dated (CA/FL) run | No licenses issued in that class and window | Widen `issuedWithinDays` or drop the classification filter |
| 0 TX rows on first run | Delta baseline | Expected; rerun on the schedule |
| 0 carriers on the first monitor run | Monitor baseline | Expected; run once without `monitorMode` for today's list |
| Partial contractor run | Time limit hit on a large registry file | Raise the run timeout or run one state per run |
| Carrier rows without email | Not every registration files one | Set `requireEmail: true` |
