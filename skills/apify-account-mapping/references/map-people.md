# Map the people at each account

Input: the resolved company URLs from [resolve-accounts.md](resolve-accounts.md). Output: per account, people in role buckets with employer evidence, plus a coverage line.

## Turn roles into title phrases

- For sales, ask which function the user sells into, then cover four slots. Economic buyer: chief, VP or head of that function. Champion: director, head of, or manager in the function. Evaluator: the hands-on lead who will use the product. Procurement or vendor management, when the deal size calls for it.
- Pair a seniority word with the function ("head of finance", "vp engineering", "procurement manager"). A bare function word that is also the account's product category matches almost everyone there, and a title the account's own customers hold can return only staff in other roles (decision rule 3).
- Keep the phrase list short and in priority order. On a first pass of 3 people per account, the people step searches about 12 slices per company: one per phrase, then phrase and city pairs. A 13th phrase is never searched ([gotchas.md](gotchas.md)). The first pass only needs enough rows to judge precision.
- Add the city as a location only when the user asked for one; it narrows the map to people whose profile shows that place.

## First pass small, then widen

- Run 3 people per account first. Classify the rows (below) and widen only the accounts where most rows landed in a real role bucket.
- If most first-pass rows at an account land in "role unconfirmed", change the phrases before raising the cap. A bigger cap on a noisy phrase only returns more noise.
- Batch accounts that share the same phrases and city into one run. An account that needs a different city or different phrases gets its own run, because every phrase and place in an input applies to every account in it.

## Classify every row

- Role bucket. Read `currentTitle`, else `headline`, and match it to the slots above. A headline cut off with "...", a missing title, or a title outside the asked-for roles goes to "role unconfirmed", even when `verified` is true.
- Excluded, with the reason. Board members, advisors and investors hold a current role but are not staff. Placeholder or test profiles (no followers, no About, a name like "Test User") do not belong to a person.
- Employer evidence. Keep `matchReason` on every card. Rows with `verified` null had their employer taken from search, without a profile check; label them "employer not checked" and keep them out of the committee unless the profile step confirms them (decision rule 6).

## Coverage check before reporting

- Every requested account must appear in `RUN_SUMMARY` or as an error row. An account missing from both points to a failed step; rerun it on its own before calling it empty.
- Compare each account's employee rows in the dataset with its found count in `RUN_SUMMARY`. A first read right after the run can be short, so re-read before you report a gap.
- Put found, verified and LinkedIn's employee count on every account, and call a large account's list a slice. Never present a map as the whole committee or the whole team.

## Talent mapping

- The accounts are the competitors, the title phrases are the roles you hire for, and the city is usually required.
- Deliver team composition: people per role and city, the seniority mix, and prior employers where `positions` is public. State the share of rows with public history. Most profiles hide it, so a missing history tells you nothing about the person (decision rule 5).
- Use the map for sourcing only. Never use a row to accept, reject or vet a candidate, and do not schedule repeat maps of a team to watch individuals: diffs between runs are noisy, and tracking people is out of scope.
