# Website health audit gotchas

## Cost guardrails

These are pay-per-event Actors. Estimate from the current live price and the user's exact target count before starting; re-read Actor information if a run would be material. Ask before an estimated cost above $5 and require explicit confirmation above $20.

| Route | Cost driver | Guardrail |
|-------|-------------|-----------|
| Hacked-site checker | checked sites | Start with a representative small list. |
| Broken links | sites crawled | Set a small `maxPagesPerSite` first; a link audit can expand quickly. |
| WHOIS/DNS | checked domains | Use domains, not URLs, and deduplicate first. |
| Screenshots | captures | Limit `devices` and use one site first when validating layout. |

## Input and recovery

- Blank input is rejected before a run starts. Do not send `{}` or invent a target; supply the required non-empty `websites` or `domains` field.
- Unreachable, invalid, and other error targets are free. Return their error information to the user and correct the target before retrying.
- Fetch schemas with `apify actors info "ACTOR_ID" --input` rather than guessing fields or retaining stale examples. Current schemas can change.
- A bot wall, robots restriction, redirect, timeout, or incomplete page is an observation about that run, not evidence of a broken or compromised site.
- Hacked-site output identifies public indicators only. Never use it to attempt exploitation, authentication, malware removal, or an accusation.

## Interpretation limits

- SPF/DMARC findings are DNS-record observations; they do not establish full mail deliverability, sender authorization, or compliance.
- Link findings vary with time, geography, and the remote site's response. Preserve URLs and timestamps when handing off a finding.
- Screenshot output is visual evidence for the selected device presets, not a substitute for accessibility, browser-compatibility, or manual QA.

Routed Actors are built by the author (Weio); no affiliate parameters.
