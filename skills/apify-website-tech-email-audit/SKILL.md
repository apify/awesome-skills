---
name: apify-website-tech-email-audit
description: Audit a list of company websites for their tech stack and email setup in one pass, then segment or qualify the list. Returns per domain the CMS or ecommerce platform, analytics, ad pixels, marketing automation, live chat, payments and CDN, plus the email provider (Google Workspace, Microsoft 365, Proofpoint...) and an SPF, DKIM and DMARC grade with the exact fix. Use when the user asks "what tech does this site use", "detect the tech stack of these domains", "which of these companies run Shopify / WordPress / HubSpot", "find stores without Klaviyo", "who is running Meta ads", "which email provider does this company use", "check SPF DKIM DMARC for a list of domains", "are these domains ready for the Gmail and Yahoo bulk-sender rules", "segment my lead list by CMS", or "qualify prospects for a deliverability / web agency offer". Routed Actors are built by the author (see Disclosure).
author: Brightrun Labs
author_url: https://github.com/davodavis66-beep
metadata:
  category: data-extraction
  keywords: "tech-stack, technology-detection, builtwith-alternative, wappalyzer-alternative, cms-detection, shopify-detection, ad-pixel-detection, email-provider, spf, dkim, dmarc, email-deliverability, bulk-sender-rules, lead-qualification, lead-segmentation, agency-prospecting, domain-audit"
---

# Website Tech Stack & Email Audit

Turn a list of domains into a qualified table: what each site is built with, what it
spends on (ad pixels, marketing tools), who hosts its email, and whether its email
authentication passes. Two Actors, one per job, chosen by what the user actually asked.

> **Disclosure:** both routed Actors (`brightrun/website-intel`, `brightrun/email-auth-audit`)
> are built and monetised by the author of this skill. No affiliate or referral parameters are used.

## Example prompts

Prompts this skill handles:

- "Here are 300 ecommerce domains. Which run Shopify, and which of those have no Klaviyo?"
- "Check SPF, DKIM and DMARC for these 50 client domains and tell me what to fix first."
- "Which of these companies use Google Workspace and run Meta ads?"

Out of scope (the boundary):

- "Find the marketing director's email at each of these companies" (contact finding). Use
  `apify-lead-scoring-enrichment` or `apify-verified-email-finder` instead.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via `apify login`, or the `APIFY_TOKEN` environment variable
  ([Console → Settings → Integrations](https://console.apify.com/settings/integrations))
- Apify CLI: `npm install -g apify-cli`

## Workflow

1. **Pick the Actor from the question.**
   - Tech stack, CMS, ad pixels, tools, segmentation, or "everything about these sites" → `brightrun/website-intel`
     (it also includes the email provider and an email-auth grade).
   - Only email authentication, or the user wants the full SPF/DKIM/DMARC detail and fix list → `brightrun/email-auth-audit`.
2. **Clean the input.** Both Actors accept bare domains, URLs (`https://www.acme.com/about`) or
   email addresses (`jane@acme.com`) and reduce them to the domain, so pass the user's list as is.
   Deduplicate first; the Actors also deduplicate.
3. **Confirm the schema** (fields can change between builds):

       apify actors info "brightrun/website-intel" --input --json \
         --user-agent apify-awesome-skills/apify-website-tech-email-audit 2>/dev/null

4. **Estimate cost and confirm** if large (see Costs). Then run.
5. **Answer the question, not the dump.** Filter and count on the returned fields (below), and
   report the rows with `status` other than `ok` separately so nothing silently disappears.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Tech stack + email provider + email-auth grade per domain | `brightrun/website-intel` | community | Segmenting and qualifying lead lists, competitor research |
| Full SPF / DKIM / DMARC / MX / BIMI / MTA-STS audit with fixes | `brightrun/email-auth-audit` | community | Deliverability checks, bulk-sender rule readiness, client onboarding |

## Running

Tech stack and email setup:

    apify actors call "brightrun/website-intel" \
      -i '{"domains": ["gymshark.com", "techcrunch.com", "zapier.com"], "includeEmailAuth": true}' \
      --json --user-agent apify-awesome-skills/apify-website-tech-email-audit 2>/dev/null

Deep email-authentication audit:

    apify actors call "brightrun/email-auth-audit" \
      -i '{"domains": ["acme.com", "jane@example.org"], "dkimSelectors": ["s1"]}' \
      --json --user-agent apify-awesome-skills/apify-website-tech-email-audit 2>/dev/null

`--json` returns the run summary; the rows live in the dataset at `.storage.defaultDatasetId`
(check `.run.status == "SUCCEEDED"` first). Fetch them:

    apify datasets get-items DATASET_ID --format json \
      --user-agent apify-awesome-skills/apify-website-tech-email-audit 2>/dev/null

## Output fields you will filter on

`brightrun/website-intel`, one row per domain:

| Field | Meaning |
|-------|---------|
| `status` | `ok`, `blocked` (bot wall: header data only), `unreachable`, `invalid_domain` |
| `technologies[]` | `{ name, category }`, e.g. `{ "name": "Shopify", "category": "Ecommerce" }` |
| `techByCategory` | Same data grouped: `{ "Advertising": ["Meta Pixel", "Google Ads"] }` |
| `cms` | First CMS / ecommerce / funnel platform found, or `null` |
| `hasAdPixels` | `true` if any advertising pixel loads on the homepage |
| `emailProvider` | `Google Workspace`, `Microsoft 365`, `Proofpoint`, `Mimecast`, ..., `Other / self-hosted`, or `null` (no MX) |
| `emailAuth` | `{ grade, score, spf, dkim, dmarcPolicy, bulkSenderReady, summary }` |
| `title`, `description`, `language`, `socials`, `hasCareersLink`, `hasPricingLink` | Homepage details |

`brightrun/email-auth-audit`, one row per domain: `grade` (A to F), `score` (0 to 100),
`summary`, `bulkSenderReady`, `spf.status` / `spf.lookups` / `spf.allQualifier`,
`dkim.status` / `dkim.selectors[]`, `dmarc.policy` / `dmarc.pct` / `dmarc.reportAddress`,
`mx.count`, `bimi.present`, `mtaSts.present`, and `issues[]` as `{ severity, message, fix }`
sorted most severe first. Invalid inputs come back as `{ domain, error: "invalid_domain" }`.

Example filter ("Shopify stores without Klaviyo"): keep rows where `cms == "Shopify"` and no
item in `technologies` has `name == "Klaviyo"`.

## Costs

Both are pay-per-event; check live pricing with `apify actors info "ACTOR_ID" --json --user-agent apify-awesome-skills/apify-website-tech-email-audit 2>/dev/null` (`pricingInfo`).

| Actor | Charged event | Price at time of writing | Free rows |
|-------|---------------|--------------------------|-----------|
| `brightrun/website-intel` | `domain-analysed` | $5 per 1,000 domains | `blocked`, `unreachable`, `invalid_domain` |
| `brightrun/email-auth-audit` | `domain-audited` | $10 per 1,000 domains | invalid domains, failed lookups |

1,000 domains through `website-intel` costs about $5. Warn above $5 and ask for confirmation
above $20. A run stops cleanly when the user's maximum-charge limit is reached.

## Troubleshooting

- **`status: blocked`** → the site sits behind bot protection; only CDN / hosting headers are
  reported and the row is free. Do not retry in a loop; report it as unknown.
- **`dkim.status: not_found` on a domain that does sign mail** → its selector is custom. Ask the
  user for it (shown in their sending platform) and re-run `email-auth-audit` with `dkimSelectors`.
- **A tool the user knows is installed is missing** → detection reads the homepage HTML only.
  Pixels injected later by a tag manager or after cookie consent (common on large brands) may
  not appear, so `hasAdPixels: false` means "none found in the page", not "no ad spend". Say so.
- **More detail:** [references/gotchas.md](references/gotchas.md).
