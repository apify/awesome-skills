# Cost and safety

## Cost controls

The Apify Store currently advertises this Actor from $3.50 per 1,000 results. Pricing can vary by account tier and can change, so check the current Store page when cost precision matters.

- Start exploratory discovery with 10–25 items.
- Tell the user before increasing scope substantially.
- Avoid repeated runs when one dataset can answer multiple questions.
- Use exact channel slugs when the target list is already known.
- Never describe `maxItems` as a guaranteed result count.

Repository release validation is separate from normal skill usage. Its runner uses `maxItems: 1` plus Apify's server-enforced `maxTotalChargeUsd=1` ceiling.

## Credential safety

- Authenticate through `apify login` or a locally configured `APIFY_TOKEN`.
- Never request a token in chat or place it in a command argument, committed file, fixture, or generated artifact.
- Never print environment variables, authentication files, full account objects, or proxy configuration.
- Do not save or display an unfiltered authenticated `apify actors info ... --json` response.
- Keep structured output on stdout and diagnostics on stderr; use `2>/dev/null` only when parsing JSON.
- Scan canonical and generated artifacts for token-like strings before release.

If sensitive material appears in tool output, stop using it, do not copy it into files or chat, and advise the owner to rotate the exposed credential.

## External actions

Running the Actor is a paid external action. Confirm the user's requested scope before the first run. Scheduling, webhooks, recurring monitoring, publication, and account changes require separate approval.
