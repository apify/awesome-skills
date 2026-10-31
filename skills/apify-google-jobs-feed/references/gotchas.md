# Gotchas: Google Jobs feed

- **Cost guardrail:** pricing is per job row (see the Actor page for the current price). `maxJobs` caps both rows and spend; confirm with the user before runs above 200 jobs in total.
- **EU/EEA:** Google shows no jobs panel in the EU and EEA, so `country` values there return no jobs. This is a Google limitation, not a run failure.
- **Empty location:** some country editions return few or no jobs when `location` is empty for broad queries. If a status row says `empty`, retry with a city or with the country name as `location`.
- **Salary:** about half of postings carry a pay range; `salaryMin`/`salaryMax` stay null when the posting has none. Check `salaryPeriod` before comparing (hourly vs yearly).
- **Status rows:** rows with `_status` describe each query (`ok`, `partial` when the time budget ran out, `empty` with a reason). Filter them out before analysis; they are never charged.
- **Freshness:** use `datePosted` (`today`, `3days`, `week`, `month`) rather than filtering `ageDays` yourself, so you are not charged for rows you discard.
