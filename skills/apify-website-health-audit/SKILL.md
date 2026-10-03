---
name: apify-website-health-audit
description: >-
  Audit public websites for hacked SEO spam, broken links, SPF/DMARC and DNS posture, or visual regressions. Use when a user says "check my site health", "find broken links", "is this site hacked", "check SPF or DMARC", or "take responsive screenshots of this website".
author: Weio
author_url: https://apify.com/weio
metadata:
  category: web-scraping
  keywords: "website health, hacked site, SEO spam, broken links, 404 checker, SPF, DMARC, DNS, WHOIS, screenshots"
---

# Website health audit

Route a public website health question to a focused Apify Actor: compromise signals, crawlable broken links, domain email security, or screenshots. Results are diagnostics, not a security verdict.

Routed Actors are built by the author (Weio); no affiliate parameters.

This skill was prepared with AI assistance and reviewed by the author.

## Example prompts

Prompts this skill handles:

- "Check these domains for casino spam or signs they were hacked."
- "Crawl my site for broken links and show the 404s."
- "Check SPF, DMARC and MX for example.com."

Out of scope (the boundary):

- "Exploit or remove malware from this server." Route incident response and remediation to an authorized security professional; these Actors only read public web and DNS data.

## Prerequisites

- An Apify account and a token configured for the interface you use.
- A concrete list of public website URLs or domains from the user. Do not insert default targets.
- Permission to scan the supplied public targets. Keep scope and run limits proportional to the request.

## Workflow

1. Identify the question: compromise signals, link integrity, email/DNS posture, or visual capture. One question can use more than one Actor, but do not run an Actor merely because it is listed here.
2. Before constructing an input, fetch that Actor's current schema. Required fields are `websites` for all routes except DNS, which requires `domains`.
3. Start with a small user-approved batch. Estimate pay-per-result cost from [the actor index](references/actor-index.md), then return the dataset URL, number of rows, and any errors or skipped targets.
4. Treat results as evidence to investigate: do not label a site compromised, noncompliant, or accessible solely from one automated result.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Hacked-site or injected SEO-spam signals | `weio/hacked-website-seo-spam-checker` | community | Public-page compromise indicators |
| Broken internal or external links | `weio/broken-link-checker-bulk` | community | Bounded website link crawl |
| WHOIS/RDAP, DNS, SPF and DMARC | `weio/domain-whois-dns-email-security-checker` | community | Domain and email-security posture |
| Responsive visual evidence | `weio/website-screenshot-phone-desktop` | community | Phone, tablet, and desktop screenshots |

For the live pricing, exact input properties, and route boundaries, read [references/actor-index.md](references/actor-index.md).

## Calling Actors — Apify CLI

First obtain the authoritative input contract instead of guessing fields:

```bash
apify actors info "weio/hacked-website-seo-spam-checker" --input \
  --user-agent apify-awesome-skills/apify-website-health-audit \
  2>/dev/null
```

Then call only with user-supplied targets. For example, a small broken-link check (replace the placeholder with a supplied URL):

```bash
apify actors call "weio/broken-link-checker-bulk" \
  -i '{"websites":["USER_SUPPLIED_URL"],"maxPagesPerSite":50}' \
  --json \
  --user-agent apify-awesome-skills/apify-website-health-audit \
  2>/dev/null
```

To retrieve the resulting dataset:

```bash
apify datasets get-items "DATASET_ID" --format json \
  --user-agent apify-awesome-skills/apify-website-health-audit \
  2>/dev/null
```

The same Actors can also be called through the [Apify MCP connector](https://mcp.apify.com) or an API client; preserve the same input and cost checks.

## Output and interpretation

- Report the submitted target count, returned row count, and any error or skipped rows before summarizing findings.
- Hacked-site findings are leads for a human review, not proof of compromise.
- Broken-link output reflects what the Actor could load during that run; bot walls, redirects, and transient network failures matter.
- SPF/DMARC output describes published DNS records, not complete email deliverability or legal compliance.
- Screenshots are point-in-time renderings, not a full accessibility or cross-browser test.

## Troubleshooting

- A blank input is rejected: supply the required `websites` or `domains` array from the user.
- Unreachable, invalid, and other error targets are returned free; inspect their error fields rather than retrying blindly.
- For expanded pricing safeguards and route-specific limits, see [references/gotchas.md](references/gotchas.md).
