# Gotchas

Non-obvious failure modes and cost guardrails. Read this before your first
weekly run so it doesn't cost more than expected.

## Cost guardrails

- **LinkedIn Actors are the biggest cost lever.** `harvestapi/linkedin-post-search`
  is $2 per 1000 posts. Broad search terms (`sales`, `hiring`) can return 10k+
  matches per week; a 3-term campaign at that breadth is $60/week. Narrow terms
  first, then broaden if the surviving qualified rows are too few. Cap via the
  Actor's `maxItems` input — set to 500 per term as a default.
- **Job Actors compound with geo fan-out.** Adding France Travail + Stepstone +
  Indeed + LinkedIn Jobs to the same campaign multiplies weekly cost roughly
  4×. Only include regional Actors when the ICP `geo` actually covers those
  countries.
- **Funding Actors are cheap** ($1–3/run typical). Include the full pick list.
- **Enrichment Actor** (`tech_gear/company-funding-details`) charges per company
  looked up. Don't call it on every row — only when the user asks for
  round-detail enrichment on a specific lead.
- **LinkedIn domain resolution is a two-hop enrichment chain.**
  `aggregate.py` calls `harvestapi/linkedin-profile-scraper` ($4 per 1k
  profiles in `"Profile details no email ($4 per 1k)"` mode) to resolve
  author → `currentPosition[0].companyLinkedinUrl`, then
  `harvestapi/linkedin-company` on the deduped set of company URLs to pull
  `website`. Without both hops, the aggregator has no domain for
  `linkedin_content` rows and cannot blacklist or dedup them. Cost is bounded
  by three knobs: (a) canonical author-URL dedup at hop 1 (`?miniProfileUrn=…`
  stripped so N samples of the same author = 1 lookup), (b) company-URL dedup
  at hop 2 (N authors at the same company = 1 company lookup), (c) the whole
  chain is skipped when every LinkedIn row already has a domain. If enrichment
  dominates your bill, narrow the LinkedIn search terms first — a broader post
  search means more distinct authors, which is where the cost lives.

## Signal-quality traps

- **LinkedIn posts by consultants / agencies** appear in every buying-intent
  search. They complain about the same tools their clients complain about but
  aren't buyers themselves. Filter post-hoc: if the author's `headline`
  contains `founder`, `consultant`, `agency`, `advisor` AND the author's
  `followers` > 5000, downgrade the row (drop in aggregator, or flag in
  `notes`).
- **LinkedIn post scraper rarely returns a company domain.** The primary
  scraper returns the author's *label* current company but not its website.
  Consequence: without a domain, blacklist and dedup can't act on the row.
  `aggregate.py::enrich_linkedin_domains` closes this with a second call to
  `harvestapi/linkedin-profile-scraper` (see [`actors.md#linkedin-content-signals`](./actors.md#linkedin-content-signals)).
  When neither scraper resolves a domain, the row is dropped with the
  `linkedin_no_domain` audit bucket — the alternative (letting them through)
  would silently bypass the blacklist.
- **Profiles with no current employer** (freelancers between gigs,
  retired founders posting for fun) return an empty
  `currentCompanyWebsite` from the profile scraper — they land in the
  `linkedin_no_domain` bucket even after enrichment. This is correct; there
  is no company to blacklist or dedup against.
- **Reposts inflate reaction counts.** LinkedIn's API doesn't cleanly separate
  original posts from reposts of the same text. `harvestapi` returns one row
  per repost URL — dedup on the post's *canonical* URL (strip
  `?trackingId=...` query params).
- **Funding announcements are re-published**: a Series A shows up on TechCrunch,
  Crunchbase, the company's blog, and the local press. The CSV dedup on
  `domain` collapses these correctly, but during a single Actor run you'll see
  duplicates in the raw dataset. Normal.
- **Job postings are often reposted 30 days later** with a new posting date.
  The dedup rule (first-seen wins) keeps the original signal intact — a job
  reposted is not a new signal.

## Idempotency edge cases

- **Manual runs mid-week**: the week-guard reads the CSV's max `detected_at`.
  If you manually run `aggregate.py` on Wednesday, the Monday-scheduled run
  will skip. To force a re-pull, pass `--force` (bypasses the week check but
  still dedupes against existing rows).
- **First run** on an empty CSV: no timestamp exists → guard is bypassed → all
  configured Actors are pulled. This is the intended bootstrap behavior.
- **Multi-machine writes to the same CSV** will corrupt the file. Single-writer
  assumption. If two agents share a lead file, put it in a location that
  serializes writes (e.g. behind a `flock` on Linux, or one shared Google
  Sheet exported nightly).

## Apify Task and Schedule ownership

- `setup_apify_tasks.py` creates tasks with names prefixed by
  `<campaign_name>-`. If you rename the campaign, the script creates fresh
  tasks and orphans the old ones — no automatic cleanup. Delete the old
  tasks manually via the Apify Console or the CLI:
  `apify tasks list --json 2>/dev/null | jq '.[] | select(.name | startswith("old-name-")) | .id'`.
- Apify Schedules are separate resources from tasks. The setup script creates
  one schedule per campaign; renaming or reassigning tasks requires updating
  the schedule too. The script does this idempotently — safe to re-run.

## Recovery from failed weekly runs

- **Actor run failed** — no data lands in the dataset for that Actor. The next
  run picks up when its schedule fires. If you want to fill the gap manually:
  ```bash
  apify tasks run <task-id> --wait 300 --json \
    --user-agent apify-awesome-skills/apify-buying-signal-detection 2>/dev/null
  ```
  Then invoke `aggregate.py --force` to pull the new data.
- **`aggregate.py` failed mid-write** — the CSV is written atomically (write to
  temp, rename over target) so a mid-write crash leaves the previous CSV
  intact. Rerun the script.
- **APIFY_TOKEN rotation** — export the new token and re-run
  `setup_apify_tasks.py --config icp.json`. Task and Schedule upserts are
  keyed by name and idempotent, so no data is duplicated. Existing tasks
  continue to work with the new token as long as it's on the same Apify
  account.
