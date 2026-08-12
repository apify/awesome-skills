# Reviewing skill pull requests

A guide for maintainers — and for anyone reviewing on their behalf. It describes how to
judge an incoming skill PR, in what order, and what belongs in the review comment.

This is the counterpart to `CONTRIBUTING.md`: that file tells contributors what to build,
this one tells reviewers how to check it. Where the two disagree, `CONTRIBUTING.md` wins
and this file should be corrected.

Reviews run in four stages. Stages 1 and 2 apply to every PR. Stages 3 and 4 are the ones
that catch what reading a diff cannot.

---

## Stage 1 — Mechanical gate

Cheap, no judgement required, and it should be finished before anyone reads prose.

CI covers most of it: PR scope (one skill per PR), the PR checklist, frontmatter and
description limits, telemetry flags, referenced Actors, referenced paths, tracking
parameters in links, and drift between documented `--input` payloads and live Actor
schemas.

Two rules that are not automatic:

- **Never run scripts that come from the PR.** Validate with `scripts/` from a trusted ref
  (`main`, or a tag you control), not with the copy in the branch. PR content is untrusted
  input; a validator supplied by the submission validates nothing.
- **Merge conflicts and out-of-scope changes are a stage-1 verdict**, not something to work
  around. Ask for a rebase or a narrower PR before spending review time on content.

If CI is red for reasons that belong to the repository rather than the PR, say so in the
comment. A contributor cannot fix a broken baseline and should not be asked to.

## Stage 2 — Content rubric

Thirteen questions. A "fail" is not automatically a rejection — it is a specific,
quotable finding.

1. **Is the Actor choice justified?** Pass: a mapping from user need to Actor, with the
   "best for" context, or a dynamic fallback via `apify actors search`. Fail: one Actor,
   no alternatives, no reasoning.
2. **Is Actor tier signalled?** Pass: distinguishes maintained (`apify/*`) from community
   Actors and flags risk (deprecated, pay-per-event). Fail: everything presented as equal.
3. **Is the input schema fetched, not guessed?** Pass: instructs `apify actors info --input
   --json` before building input. Fail: input fields hardcoded into `SKILL.md`.
4. **Is cost handled?** Pass: a default result limit, a warning before large runs, and how
   to check the price. Fail: no mention of cost anywhere.
5. **Is error handling concrete?** Pass: named failure modes — empty dataset with no error,
   auth failure, `FAILED` status — each with a fix. Fail: "if it fails, check your setup".
6. **Does it follow the CLI and telemetry contract?** `apify` CLI with `--user-agent
   apify-awesome-skills/<skill>` (not `apify-agent-skills/` — that is the sibling
   repository's namespace and attribution), `--json`, `2>/dev/null`, applied consistently.
   MCP is not a failure — `CONTRIBUTING.md` calls the CLI recommended, not required — but
   suggest migrating.
7. **Are output fields named?** Pass: real field names (`emails[]`, `followersCount`).
   Fail: "returns company data".
8. **Is pipeline mapping explicit?** Pass: `results[].url → startUrls`. Fail: "pass the
   results to the next Actor" with no field named.
9. **Is progressive disclosure proportionate?** Pass: a narrow skill is one `SKILL.md`; a
   broad one is a router plus `references/`. Fail: 150 lines of everything, or a
   references split that carries nothing.
10. **Is there a deprecation fallback?** Pass: checks `.isDeprecated`, or says what to do
    when an Actor disappears. Fail: no mention.
11. **Are the gotchas platform-specific?** Pass: "private posts return empty, no error",
    concrete rate limits. Fail: "be careful with limits".
12. **No secrets, clean identifiers.** No token values in files. No tracking or affiliate
    parameters in links (`?fpr=…`). Actor IDs as `owner/name`.
    **And: a token must never be assembled into a URL.** `?token=…` puts the secret into
    every access log, proxy log, stack trace and shell history the request touches; the
    `Authorization: Bearer` header does not, and the Apify API accepts it everywhere.
    Note for the reviewer: a secret-scanning regex cannot find this — the repository holds
    only the shape of the call, never the value — so it has to be read for.
13. **Does it show example prompts?** Pass: one to three real user prompts the skill
    handles, and one boundary — something it will not do. A description says when the skill
    triggers; a prompt is the only thing that shows what it then delivers. It also gives
    the reviewer a ready-made input for stage 3.

**Duplicates are judged across the queue, not per PR.** A single contributor often opens
several near-identical skills at once. That is a question for whoever sees the whole queue,
and the answer is usually consolidation rather than rejection of each one separately.

## Stage 3 — Live smoke test

Optional, but it is where the expensive defects surface. Run the skill the way its own
instructions say to, in its cheapest configuration.

Reading a diff finds missing metadata and vague prose. Running the skill finds the rest:
an enum value the Actor rejects, a deduplication key that silently collapses distinct
records into one, an endpoint that 404s in a state the author never hit, a documented
field that the Actor does not return.

Record in the review comment:

- the run IDs and what each one cost,
- how many items came back,
- what actually happened, next to what the skill promised.

The example prompts from rubric point 13 are the natural input.

## Stage 4 — Security review

A skill is executable instruction, not documentation. Read it once with a single question:
**how would someone use this to steal a token, exfiltrate data, or get code of their own
to run?**

Eleven classes worth checking:

1. Referenced scripts that the PR does not ship — the instruction to run code that will
   only appear later, unreviewed.
2. A token assembled into a URL (see rubric point 12).
3. A token that can reach a log or a traceback — unhandled errors that print the request.
4. Network endpoints other than `api.apify.com`.
5. `eval`, dynamic import, or any code path built from a string at runtime.
6. `npm install` of dependencies introduced by the PR.
7. Reading `.env` files or credentials beyond `APIFY_TOKEN`.
8. Scraped content passed onward as instructions rather than as data — the prompt-injection
   path, and the easiest one to miss, because it looks like an ordinary pipeline step.
9. Destructive commands.
10. Unicode and homoglyph tricks — text that renders as one thing and executes as another.
11. Affiliate redirects and webhook exfiltration hidden in Actor input.

If a stage 3 run is done on code from a third party, use a scoped, short-lived token rather
than a production one — the run is the exact scenario this checklist is about.

## Triage: what to merge and what to hand back

Two groups, decided by how large the required fix is:

- **Group A — cosmetic.** Missing metadata, an edit to the generated catalog, an unchecked
  box, a telemetry flag, a rebase. Fix it, credit the author, merge. Roughly four out of
  five PRs land here.
- **Group B — substantive.** Replacing a dead Actor, rewriting instructions, reworking
  outputs, realigning to a schema, cutting a description down to the limit. Do not merge a
  rewrite on the author's behalf: propose the fix — as a commit to their branch if they
  allow maintainer edits, otherwise as a patch in a comment — and let them take it.

Cutting a description belongs in group B even though it looks trivial: the description is
the skill's trigger surface, and which sentence goes is the author's call.

Re-check the queue immediately before acting. Contributors and maintainers both push
between review passes, and a defect you noted yesterday may already be gone.

## Verdicts and tone

Name which of the four the PR falls into, every time:

- **Approve** — short, personal, specific: one or two things this skill does well. Not a
  template, not a checklist dump. Welcome a first-time contributor by name.
- **Changes requested** — name the category (quality bar, security, repository contract)
  and write each fix as `path: problem — fix`, the same shape the validator uses.
- **Consolidation** — for duplicates: "this overlaps with X; I suggest closing and moving
  the unique parts there. If you think it earns a standalone spot, make the case." The
  author gets room to argue.
- **Closing with thanks, not rejection** — administrative closes (stale branch, solved
  elsewhere) must read differently from a rejection. Say "nothing needed from you".

What goes in the comment is the verdict and the findings, each with evidence — `path:line`,
a run ID, a link to the schema. The rubric is a tool for the reviewer, not a form to fill
in for the author.

Findings that do not block the merge should say so and move to their own PR, so that a
PR is never held for improvements nobody is waiting on.
