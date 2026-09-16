# De-noise / Skip Pass — apify-jobs-data (Step 5)

De-noise the raw dataset so every output mode (analysis, export, résumé-fit) runs on
clean data — ghost-job and repost pollution corrupts demand counts and salary stats
just as much as it wastes a job seeker's time. Adapted from the skip-pass discipline
in `apify-link-prospecting-outreach`.

**Golden rule: skip ≠ delete.** Every skipped row stays in the output in a separate
`Skipped` section with a one-line `skip_reason`. The user must be able to audit what
was filtered and loosen a rule. Never silently drop a row.

Apply the rules in order. A row that hard-drops (rules 1, 2, 5) leaves the clean set;
a row that's only *flagged* (rules 3, 4) stays in the set but carries a warning.

## Rule 1 — Hard-filter violation (DROP)

A hard filter (anchor #6) is a non-negotiable, not a score penalty. Drop the row,
record which filter it failed.

| Filter | Drop when |
|---|---|
| `salary_floor` | Disclosed max < floor. **Undisclosed salary never drops here** — it can't violate a floor it doesn't state. Flag it `salary: undisclosed` and let it score neutral in Step 6. |
| `remote_only` | Posting is on-site / hybrid-required and the user required remote. |
| `job_type` | Posting type ≠ requested (e.g. contract when user wants full-time). |
| Work authorization | JD states a citizenship / clearance / visa-sponsorship-excluded constraint the user can't meet. Only drop on an explicit, unambiguous statement — don't infer. |
| Location | Posting location is a different city/region than anchor #2 **and** the JD does not state remote eligibility for the user's region. Record `location mismatch: <posting city>`. A JD that explicitly states remote for the user's region is in-area. Bare `Remote` (no region) is **never dropped and never counted as in-area** — keep it, flag it `remote: unverified` (the flag must reach the output table and the CSV `flags` column), and report the count separately in the Step 7 header ("N remote postings without a stated region"). |

Filters from anchor #6 apply only when the user supplied them — an analysis-mode run
usually wants the *whole* market, no hard filters. The **Location check always runs**
when anchor #2 is set — Actors return out-of-area rows even with an explicit location
input (aggregator/Indeed: ~99 % in one measured run); treat their location filter as
unverified. Strip ZIP codes before comparing (`Austin, TX 78759` = `Austin, TX`), for
this rule and for the Rule 2 dedupe key.

## Rule 2 — Duplicate / repost (DROP, merge up)

The same role is syndicated across boards and reposted over time. Group by
`(normalized company, normalized title, location)` **as candidates only**:

- Normalize company: lowercase, strip `Inc/GmbH/Ltd/LLC/AG`, collapse whitespace.
- Normalize title: lowercase, strip seniority punctuation and `(m/f/d)`-style tags.

Merge a group only when a stable vacancy identity also matches: the same job id /
apply URL, or a near-identical JD body. Same company + title + location with different
JD bodies stays as separate rows, each flagged `possible duplicate` — losing a real
vacancy costs more than one extra row.

Within a merged group keep the row with the **most complete fields and the freshest
genuine post date**; merge the duplicates' apply links into `Other Sources` so nothing
is lost. Set `saveOnlyUniqueItems: true` on Indeed to cut board-side dupes early.

## Rule 3 — Ghost / stale job (FLAG)

A "ghost job" is a posting that isn't a real, fillable opening right now. These
waste the user's time. Flag (don't hard-drop unless the user asked to exclude
ghosts) with `Skip Reason: possible ghost — <tell>`. Tells:

- **Re-stamped recency.** Within one run, the same `(company, title, location)`
  appearing on multiple boards with conflicting "posted" dates (one shows weeks ago,
  another "today") is a re-stamp tell. A single board's date alone can't be
  cross-checked, so single-run ghost detection leans on the language and specificity
  tells below.
- **Evergreen age.** Continuously open 60+ days with no edits. This tell is only as
  trustworthy as the board's original-post-date field — several boards re-stamp or
  omit it, so treat a missing/unreliable date as "can't compute", not "fresh".
- **Pipeline language.** JD contains "always accepting applications", "building a
  pipeline", "future opportunities", "talent community", no specific team/start.
- **No specifics.** No named team, manager, level band, or start window in a
  senior-titled req.
A single weak tell → note it. Two+ tells → label `likely ghost`. Be honest that
this is heuristic, not certain — never hard-drop a posting on ghost suspicion alone.

## Rule 4 — Staffing-agency repost (FLAG)

When the user wants **direct-employer** roles, flag postings that come from a
third-party recruiting agency rather than the hiring company. Detect empirically
(pattern from `apify-influencer-brand-collabs` — don't trust a single unreliable
field). **A name pattern alone is not enough** — many real employers contain
"Solutions", "Consulting", or "Talent". Flag only when the name pattern is
**corroborated** by at least one of the stronger signals:

- **Name pattern** (necessary, not sufficient): `Recruit*`, `Staffing`, `Talent`,
  `Consulting`, `Solutions`, `Robert Half`, `Hays`, `Michael Page`, `TEKsystems`,
  `Randstad`, etc. — a candidate signal, never a flag on its own.
- **Corroboration (require ≥1):** the **same JD body** appears under multiple
  different "company" names (strong — the real employer is hidden), **or** the JD
  says "our client" / "a leading company" / "confidential client".

Flag with `Skip Reason: staffing agency — employer hidden` only when name pattern +
corroboration both hold. Never drop: some users are fine applying through agencies.
If the user wants agency roles included, skip this rule entirely.

## Rule 5 — Off-target role (DROP)

The query string matched but the role family is wrong (e.g. a query of `engineer`
returning `sales engineer`, `engineering manager` when the user wants an IC SWE
role). Make this call from the title + JD, conservatively — when unsure, keep the
row rather than dropping a real match. Only apply this rule when the user's intent is
a specific role family; an open market scan keeps everything.

## Empty results are signal

If de-noise empties the clean set (everything was noise) or the board returned
nothing, **say so plainly and explain why** — niche role, tiny market, over-tight
recency, a board block. Suggest a concrete loosening (wider `posted_since`, broader
location, drop a filter, try the fallback Actor). Never fabricate filler rows. (From
`apify-easy-competitive-intelligence`: "Empty results ARE intelligence.")

## Report the cuts

In the Step 7 header, state the funnel in application order:
`raw → after location check → after hard filters → after dedupe → clean (+ N flagged
ghosts, M flagged agency, K remote postings without a stated region)`. Transparency
lets the user trust the data and re-run with a looser rule.
