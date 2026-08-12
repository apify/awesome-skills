# Fit Scoring — apify-jobs-data (Step 6)

How Step 6 turns de-noised postings into a ranked shortlist. The headline rule,
borrowed from `apify-link-prospecting-outreach` (which is explicit that "regex /
keyword scoring is not acceptable for the final draft"):

> **The final fit call is made by a sub-agent that reads the full job description
> against the user's profile — not by counting keyword overlaps.** Keyword scoring
> is the labeled fallback used only when no profile was supplied.

A posting can name "Python" once in a boilerplate list and be a terrible fit, or
never use the user's exact keyword yet be perfect. Only reading the JD in context
catches that. Always show the **per-component breakdown** so the user sees *why* a
job ranked where it did and can re-weight.

## Path A — profile supplied (default): per-posting sub-agents

After the skip pass, spawn one sub-agent per surviving posting, in parallel,
batched (cap concurrency to keep the round responsive — see the orchestration note
below). Each sub-agent gets the full JD text + the user's profile and returns this
exact contract:

```json
{
  "fit": 0-100,
  "band": "strong | worth-a-look | stretch | low",
  "matched_skills": ["..."],
  "gaps": ["..."],
  "seniority_match": "exact | one-off | mismatch",
  "comp_vs_floor": "above | overlaps | below | undisclosed",
  "ats_keywords_missing": [
    { "term": "Kubernetes", "honest_to_add": true,  "note": "résumé says 'container orchestration' — same thing, name it" },
    { "term": "Terraform",  "honest_to_add": false, "note": "candidate has no IaC experience — a real gap, don't add" }
  ],
  "hook": "one sentence linking the user's strongest relevant experience to the role's headline responsibility",
  "rationale": "2-3 sentences: why this score, grounded in JD + profile text",
  "verdict": "apply | maybe | skip"
}
```

### Sub-agent instructions (give verbatim)

> You are scoring one job posting for fit against a candidate's profile. Read the
> full job description and the profile. Score 0–100 using the rubric weights below.
> Ground every claim in text that is actually present — do not assume the candidate
> has experience they didn't list, and do not credit a skill the JD only mentions
> in passing. List concrete matched skills and concrete gaps. For
> `ats_keywords_missing`, extract the hard skills/tools the JD names as requirements
> that do NOT appear in the résumé (these are what an ATS keyword-filter screens on);
> for each, set `honest_to_add: true` ONLY if the candidate plausibly has the
> experience under a different name (note the synonym), and `false` if it's a genuine
> gap they'd be lying to claim. Write one tailored hook sentence the candidate could
> open a cover letter with, using only experience they actually claimed. If the role
> is a clear mismatch, return `verdict: skip` with a one-line reason. Return only the
> JSON contract.

The `ats_keywords_missing` field is the single highest-value output for a real job
seeker — an ATS often rejects on keyword match before a human reads anything — and it
is fully grounded in the scraped JD vs the résumé. **Never mark a genuine gap as
`honest_to_add: true`; coaching a candidate to lie gets them caught in the interview.**

### Rubric the sub-agent applies (weights sum to 100)

| Component | Weight | Scored from |
|---|---:|---|
| **Skill & responsibility match** | 40 | How well the candidate's actual experience covers the role's *core* responsibilities (not its keyword list). Must-haves the candidate lacks cost the most. This is the thing the user actually cares about and the only thing reading the JD uniquely buys you — so it carries the most weight. |
| **Seniority match** | 20 | Exact level → 20; one level off → 10; two+ off → 0. Inferred from scope/responsibilities, not just the title word. |
| **Compensation** | 10 | Disclosed band ≥ floor → 10; overlaps → 5; below → 0 (these were dropped in skip-pass rule 1 anyway). **Undisclosed → 5 (half-credit, neutral)**, flagged. Weight is deliberately low: comp is already enforced as a *hard filter*, and most real postings don't disclose, so it must not dominate or silently penalize the modal job (see note below). |
| **Location / remote** | 15 | Matches preference (or remote when remote requested) → 15; same country, diff city → 8; else → 0. **Exception the sub-agent should catch:** a posting whose listed location is a foreign HQ but whose JD is explicitly remote-eligible for the user's region scores as a location match, not 0 — read the JD, don't just compare the location string. |
| **Recency & realness** | 15 | Within the user's window and not flagged as ghost → 15; decays to 0 at 2× window; a flagged-ghost posting is capped at 7 here regardless of date. |

**Salary-disclosure note.** Disclosure rate is largely a *jurisdiction artifact* —
mandated and reliable in CA/CO/NY/WA and EU-transparency-covered roles, absent or
aspirational elsewhere. A blank salary is therefore not a company-quality signal,
which is exactly why comp carries low weight and undisclosed scores neutral rather
than penalizing. When comp genuinely matters to the user, cross-check against the
Glassdoor salary benchmark (analysis mode, analysis.md), don't lean on the posted band.

### Orchestration note

In an agent session that supports sub-agents (e.g. a Task/Agent tool), spawn one
sub-agent per posting, in parallel, batched ~8–10 at a time. If sub-agent spawning
isn't available in the runtime, the *same* rubric can be applied inline by the main
agent reading each JD sequentially — slower but identical contract. Do **not** silently downgrade
to keyword scoring when a profile exists; reading the JD is the point.

## Path B — no profile: mechanical fallback (labeled `Fit (partial)`)

When anchor #7 is empty you cannot judge skill or seniority fit. Score only what
the data supports and **label the column `Fit (partial)`**:

| Component | Weight |
|---|---:|
| Recency & realness (ghost-flagged capped) | 40 |
| Location / remote match | 30 |
| Compensation (vs. any stated floor, else relative rank of disclosed salaries; undisclosed neutral) | 30 |

Always invite the user to paste a résumé or skill list to unlock Path A. Never
present a partial score as a true match.

## Banding

The sub-agent contract returns `band` as text; the output renders it as an emoji.
Mapping (used by both the sub-agent and the renderer):

| Score | `band` text | Emoji | Meaning |
|---|---|---|---|
| 80–100 | `strong` | 🟢 | Apply first; tailor the application |
| 60–79 | `worth-a-look` | 🟡 | Apply if capacity; mind the gaps |
| 40–59 | `stretch` | 🟠 | Only if the company/mission is a real draw |
| 0–39 | `low` | 🔴 | Low fit. Stays in **Active** (not the Skipped section); the user decides |

A `verdict: skip` from the sub-agent maps to the 🔴 `low` band and stays in the ranked
output — it is never moved to the Step-5 Skipped section, which is reserved for
skip-pass drops with a `Skip Reason`.

Order the output by `fit` descending, then posting date.

## Tailoring output (always include for 🟢/🟡 rows)

From the sub-agent contract, surface per row: `Matched Skills`, `Gaps` (the
questions to prepare for, not necessarily disqualifiers), the `Hook`, and the
`ats_keywords_missing` terms (only the `honest_to_add: true` ones as "add these",
the rest as honest gaps). Keep all of it grounded in JD + profile text. **Never
invent experience the candidate didn't claim** — a fabricated hook or a dishonest
ATS keyword gets them caught in the interview.
