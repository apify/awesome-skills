# Cost and data-truth guardrails

- Check the live Store pricing before each new workflow. The documented price can change.
- The Actor accepts one domain and writes at most one validated result per run.
- A failed run can still incur a small platform start charge even when no result event is charged.
- Do not loop over a list without showing the user the count and maximum expected spend first.
- Do not retry automatically. A second run can duplicate cost without improving evidence.
- Treat every returned business field as a website-derived candidate. Preserve `provenance.sourceUrl`, `provenance.method`, `provenance.caveat`, and `observedAt`.
- Never claim account ownership, registry identity, creditworthiness, compliance status, buyer identity, or outreach eligibility from this result.
