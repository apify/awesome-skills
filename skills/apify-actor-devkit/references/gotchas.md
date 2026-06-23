# Gotchas — cost and decision discipline

## Branch on the decision field, never the prose

- Every Actor here returns a stable enum: `decision` (`act_now` / `monitor` / `ignore`) or A/B Tester's `decisionPosture` (`switch_now` / `canary_recommended` / `monitor_only` / `no_call`).
- Branch automation on that field only. `verdictHuman`, `summary`, `explanation`, `oneLine` are for display — their wording is not contract-stable and will break parsers.
- Read `warnings[]` first. Any warning with `severity: blocking` forbids an actionable verdict regardless of how good the numbers look.

## Cost

- A/B Tester runs each Actor N times: `runs: N` = 2N sub-Actor runs, each billed at its own rate on your account, plus the per-test orchestration fee. Budget before high-stakes (10-run) modes.
- Fleet-wide Actors (Quality Monitor, Fleet Health Report) scan every Actor on the account in one run. Cost scales with fleet size.
- Start with a smoke / single-target run to confirm the output shape before a full pass.

## Honest abstention is a feature

- `no_call` / `insufficient-data` is a valid outcome, not a failure. It means the evidence does not support a decision — re-run with more samples rather than forcing a verdict.
- A first scheduled run of a delta-tracking comparison returns `{found: false}`. That is the baseline, not an error.

## Recovery

- A failed run carries a `.consoleUrl` in its run metadata; open it for logs.
- A/B Tester needs two distinct Actors that accept the same `testInput` shape. Incompatible input shapes produce a `RESULT_SHAPE_DIVERGENCE` warning and a `no_call`.
