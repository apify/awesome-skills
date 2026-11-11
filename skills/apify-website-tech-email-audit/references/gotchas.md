# Gotchas - apify-website-tech-email-audit

## Cost guardrails

| Model | What to watch for |
|-------|-------------------|
| `PAY_PER_EVENT` | Both Actors charge per domain successfully processed. Estimate as domains × price. |

- Estimated cost **>$5** → warn the user.
- Estimated cost **>$20** → require explicit confirmation before running.
- Present cost as a rough estimate ("around $X"); blocked and unreachable domains are not charged.

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| Run fails with "No valid domains in input" | Every entry was malformed | Pass domains like `acme.com`; URLs and emails also work |
| Many `unreachable` rows | Dead domains, typos, or parked domains | Report them separately; they cost nothing |
| `emailProvider: null` | Domain has no MX records | It cannot receive mail; flag it, do not guess a provider |
| Wildcard DKIM (`dkim.status: wildcard`) | `_domainkey` answers every name | Ask for the real selector and re-run |

## Actor-specific notes

### `brightrun/website-intel`

- Detects about 90 technologies from homepage HTML and response headers using asset-level
  fingerprints (script and CDN hosts), so a page that merely mentions a vendor is not a detection.
- Set `includeEmailAuth: false` for faster runs when only the tech stack matters.
- Up to 2,000 domains per run; split larger lists.

### `brightrun/email-auth-audit`

- Reads public DNS only; sends no email and changes nothing.
- Probes 37 common DKIM selectors plus any in `dkimSelectors`.
- DNS changes can take up to 48 hours to show; re-run after a fix rather than trusting cached results.
