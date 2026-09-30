# Security Policy

This repository distributes **agent skills** — instruction files that other people's
AI agents execute with their own Apify account and `APIFY_TOKEN`. A malicious or
careless skill can spend someone else's money or leak someone else's data. Every
contribution is reviewed with that in mind.

## Threat model

- **Skills are executed by other people's agents.** A `SKILL.md` is a set of
  instructions an AI agent follows with the user's `APIFY_TOKEN` and permissions.
- **Actor runs cost money.** Skills trigger paid Apify Actors; a skill can cause
  unintended spending of platform credits.
- **Skills handle scraped data.** Results may contain personal or business data;
  a skill could attempt to exfiltrate them to a third party.

## Hard rejects

A PR is rejected (and an existing skill removed) if it contains any of the following:

- Sending data to any endpoint, webhook, or inbox outside the user's control.
- Hardcoded tokens, API keys, or other secrets. CI enforces this via
  `scripts/lint_references.py`, which fails on any `apify_api_` token in a
  skill's files. A token must never be assembled into a URL either — use the
  `Authorization: Bearer` header, which the Apify API accepts everywhere;
  `?token=…` leaks the secret into every access log the request touches.
  That one no regex can catch, so reviewers read for it (see `REVIEWING.md`).
- Prompt-injection patterns — e.g. "ignore previous instructions", or instructions
  that disable approval gates or safety checks of the executing agent.
- Instructions that trigger unbounded spending without explicit user confirmation
  (cost gate) — see the cost guardrails in `skills/_template/references/gotchas.md`.
- Asking users to provide credentials in plaintext (chat, files, or command output).

## Reporting a vulnerability

If you find a malicious skill or a security issue in this repository:

1. Open a [private security advisory](https://github.com/apify/awesome-skills/security/advisories/new) (preferred), or
<!-- TODO(maintainers): confirm the reporting e-mail address -->
2. e-mail `security@apify.com`.

Please do not report security issues via public GitHub issues.
