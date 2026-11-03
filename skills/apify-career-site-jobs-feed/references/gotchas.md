# Gotchas — apify-career-site-jobs-feed

## Cost guardrails

All three Actors are `PAY_PER_EVENT` at $0.002 per returned row plus a negligible Actor-start event. Platform compute is included.

- 20 Greenhouse/Lever/Ashby boards: usually 500 to 3,000 rows, under $6.
- One large Workday tenant (CVS, NVIDIA) can exceed 2,000 rows alone; set `maxJobsPerBoard` or expect up to $4 per such tenant.
- Estimated cost **>$5** → warn the user; **>$20** → require explicit confirmation. Use the Console "max total charge" to hard-cap a run; the Actor stops at the limit.

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| row with `error: 404 ...` | wrong slug or company changed ATS | open the careers page, read the host, resubmit that board |
| `unrecognized careers URL` | host is not Greenhouse/Lever/Ashby/Workday/SmartRecruiters/Recruitee | pass `source:slug` explicitly or route to `apify-job-boards` |
| Workday returns fewer rows than the site shows | `maxJobsPerBoard` cap or a tenant site slug for a different region | raise the cap; use the exact `<site>` from the URL (e.g. `external_experienced`) |
| HN thread has 0 rows | `thread` id is not a "Who is hiring?" post | use `"latest"` or the id of the monthly Ask HN post |
| RemoteOK rows missing in your output | attribution requirement | keep `source_url` and name RemoteOK when republishing their rows |
