---
name: apify-domain-name-finder
description: >
  Brainstorm brandable domain names for a business, check which ones are
  free to register with automation-lab/domain-availability-checker (Server
  Actor HTTP interface first, batch run as fallback), then check the
  available ones for leftover SEO authority, backlinks and spam history with
  steadyfetch/domain-authority-checker (dropped domains can carry link
  equity or a toxic past). Ends with a shortlist of available domains ranked
  by brand fit, with an availability matrix across TLDs. Use when the user
  asks to "find a domain name", "brainstorm domain ideas", "name my business
  / startup / product and check the domain", "is <name>.com available",
  "which TLDs are free for <name>", or describes a business and wants name
  and domain ideas. Do NOT use for brand-protection / typosquatting
  monitoring at scale or expired-domain investing. Requires the Apify MCP
  server (preferred) or the Apify CLI.
author: Fabian Maume
author_url: https://github.com/fmaume
metadata:
  category: marketing
  keywords: "domain-name, domain-availability, business-name, brand-name, naming, startup, brainstorm, rdap, whois, tld, domain-authority, backlinks, spam-score, expired-domains"
---

# Apify Domain Name Finder

Turn a business description into a shortlist of domains you can register today. It runs in four phases:

1. **Brainstorm** names with the user.
2. **Check availability** across TLDs with [`automation-lab/domain-availability-checker`](https://apify.com/automation-lab/domain-availability-checker).
3. **Check authority** of the available domains with [`steadyfetch/domain-authority-checker`](https://apify.com/steadyfetch/domain-authority-checker). This step flags domains that were registered before and still carry backlinks or a spammy past.
4. **Report** a ranked shortlist.

## Example prompts

Prompts this skill handles:

- "I'm launching a coffee subscription for remote teams. Help me find a name and a free domain."
- "Is brewnest available on .com, .ai or .co?"
- "Give me 20 short, techy domain ideas for an AI bookkeeping tool and check which are free."

Out of scope (the boundary):

- "Monitor all look-alike domains of our brand every week". That is brand-protection monitoring: run the availability Actor directly in batch on a schedule.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- One of:
  - the [Apify MCP server](https://mcp.apify.com) (preferred: it exposes the Server Actor interface used below)
  - the Apify CLI with `apify login` or an `APIFY_TOKEN` environment variable

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Is a domain registered? | `automation-lab/domain-availability-checker` | community | RDAP with DNS/WHOIS fallback, many TLDs, unknown answers free |
| Does an available domain have SEO history? | `steadyfetch/domain-authority-checker` | community | 0–1000 authority rank, backlinks, referring domains, spam score |

## Phase 1: Brainstorm

### 1a. Gather the brief (ask only what is missing, in one question round)

- What the business does and who it serves (one sentence is enough)
- Tone: serious / playful / premium / technical / local
- Words to include or avoid; languages and markets (these decide country TLDs like .de, .cz, .co.uk)
- Preferred TLDs (default: `com`, `ai`, `co`, `app`, plus a country TLD for a local business)
- Max length (default: 12 characters before the TLD)

If the user already gave a clear description, skip the questions.

### 1b. Generate 30–40 candidate names across these styles

Label each name with its style so the user can steer.

| Style | Pattern | Example (coffee subscription) |
|---|---|---|
| Descriptive | keyword + keyword | beanbox, roastdrop |
| Compound | two words fused | brewnest, cupcraft |
| Portmanteau | blended syllables | caffinity, roastopia |
| Invented | pronounceable coinage | lumaro, vexo |
| Prefix / suffix | get-, try-, use-, -ly, -ify, -hq, -labs | getbeanbox, roastly |
| Evocative | a related image or feeling | morningember, firstpour |
| Misspelling (sparingly) | drop a vowel, swap a letter | brewr, kofi |
| Local / founder | a place or a name | praguebrew |

### 1c. Filter before checking

Drop names that are longer than the max length, contain hyphens or digits (unless asked), are hard to spell after hearing them once, read badly across word boundaries (e.g. "therapistfinder"), or match a famous brand. Keep 20–30.

Show the filtered list grouped by style and ask: "Check all of these, or tweak first?" If the user said to just run it, go ahead without asking.

## Phase 2: Check availability

Cost: about $0.002 per definite answer, with no start fee on the server interface. Inconclusive answers are free. 30 names × 5 TLDs = 150 checks ≈ $0.30. Tell the user the estimate when it's over 200 domains.

### 2a. Preferred: Server Actor interface (MCP `send-server-actor-request`)

Expand names × TLDs into full domains and send **up to 10 domains per request**. Send several requests in parallel.

```
tool: send-server-actor-request
actor: automation-lab/domain-availability-checker
method: POST
path: /domains
body: {"domains": ["brewnest.com", "brewnest.ai", "..."]}   # ≤10 domains, ≤4096-byte body
```

For one domain: `GET /domain` with query `domain=brewnest.com`.

Response: `{"ok": true, "count": N, "results": [{domain, tld, status, available, registered, registrar, expiryDate, daysUntilExpiry, registryStatus, method, error}]}`

**`/domains` returns only definite answers.** Any domain you sent that is missing from `results` is **unknown**. `GET /domain` answers an unknown with HTTP 502 `UPSTREAM_ERROR`. Report these as "❔ unknown, check at a registrar" and never count them as available. Retry an unknown once with `GET /domain`. If a server request fails (non-2xx other than 502, timeout), use 2b for the remaining domains.

### 2b. Fallback: batch run

Use for more than ~100 domains, when the server interface fails, or when only the CLI is available. It adds a $0.035 start fee.

MCP: `call-actor` with `actor: automation-lab/domain-availability-checker`, `input: {"names": [...], "tlds": [...]}`, then `get-dataset-items`.

CLI:

```bash
apify actors call automation-lab/domain-availability-checker \
  -i '{"names": ["brewnest", "cupcraft"], "tlds": ["com", "ai", "co"]}' \
  --json \
  --user-agent apify-awesome-skills/apify-domain-name-finder \
  2>/dev/null
```

Take `defaultDatasetId` from the output, then:

```bash
apify datasets get-items DATASET_ID --format json \
  --user-agent apify-awesome-skills/apify-domain-name-finder 2>/dev/null
```

Use `{"domains": [...]}` instead of `names` + `tlds` for exact domains. Batch runs also save unknown domains as rows with `status: "unknown"` (free of charge).

### 2c. Interpret

- `available`: can be registered now. The Actor returns no price, and premium names may cost more at the registrar. Say so.
- `registered`: taken. If `daysUntilExpiry` < 30 or `registryStatus` contains `redemption period` / `pending delete`, flag it as "may drop soon".
- missing or `unknown`: not confirmed either way.

## Phase 3: Authority check of available domains

An available domain may have been registered before and dropped. It can still carry backlinks (a head start for SEO) or a spammy past (a liability). Check **only domains with `status: "available"`** from Phase 2.

### 3a. Preferred: Server Actor interface

```
tool: send-server-actor-request
actor: steadyfetch/domain-authority-checker
method: POST
path: /
body: {"domains": ["brewnest.com", "cupcraft.ai", "..."]}   # ≤50 per request (≤10 on the Apify free plan)
```

Cost: a $0.055 fee **per request**, whatever it holds, plus $0.0025–0.004 per domain that has a rank. Domains with no backlink history are free. **Put as many domains as allowed into each request.** Never send one domain at a time.

Response: `{"rows": [...], "receipt": {...}}`. Use the rows with `rowType: "domain"` and skip the `batch` row:

- `status: "no_data"`: no link to it has ever been found. A fresh domain with a clean slate (most invented names).
- `status: "delivered"`: it has history. Read `authorityRank` (0–1000 on the Actor's own scale, not Moz DA or Ahrefs DR), `referringDomains`, `backlinks`, `spamScore` (0–100) and `firstSeen`.

### 3b. Fallback: batch run

For more than 50 available domains, when the server request fails, or with the CLI. It handles up to 1,000 domains per run, with a $0.055 fee per 100.

```bash
apify actors call steadyfetch/domain-authority-checker \
  -i '{"domains": ["brewnest.com", "cupcraft.ai"]}' \
  --json \
  --user-agent apify-awesome-skills/apify-domain-name-finder \
  2>/dev/null
```

Then fetch the rows with `apify datasets get-items` as in 2b. With MCP `call-actor`, set `callOptions.maxTotalChargeUsd` to about 0.004 × domains + 0.06 per started 100.

### 3c. Interpret

| Signal | Label |
|---|---|
| `no_data` | 🆕 Fresh (no history) |
| rank > 0, `spamScore` < 30, `referringDomains` ≥ 10 | ⭐ Has authority (existing link equity) |
| rank > 0, few referring domains, `spamScore` < 30 | ▫️ Minor history |
| `spamScore` ≥ 30 | ⚠️ Spammy history (avoid, or audit its backlinks and check web.archive.org first) |

## Phase 4: Report

Output in chat (Markdown), in this order:

1. **Top picks (3–5)**: available names where the `.com` (or the user's priority TLD) is free and the label isn't ⚠️. One line each on why it fits the brief, plus the authority label. Brand fit outranks authority: authority breaks ties and counts as a bonus, and never pushes a weak name up.
2. **Availability matrix**: rows = names, columns = TLDs, cells ✅ available / ❌ taken / ❔ unknown. Add the authority label next to ✅ when it isn't 🆕 (e.g. `✅⭐ 212`). Sort rows by number of available TLDs, with `.com` available first.
3. **Available domains with history**: every available domain with `delivered` status: domain, authorityRank, referringDomains, spamScore, firstSeen, label.
4. **Taken but interesting**: registered names that expire soon, or whose name is free on other TLDs.
5. **Cost**: the total spent on availability and authority checks.
6. **Next step**: offer a second round of variations on the user's favourite names (prefix/suffix, synonyms), checked the same way.

Never call a domain available unless the Actor returned `status: "available"` for it in this session. Never register or buy domains on the user's behalf.

## Troubleshooting

- **`.io` always comes back unknown** (tested November 2026), even for unregistered names, on both the server interface and batch runs. `.com` and `.ai` resolve fine. Don't spend retries on `.io`: tell the user to check it at a registrar.
- **A domain is missing from the `/domains` response**: it's unknown, not an error. See 2a.
- **Authority checker returns `skipped.free_plan_allowance`**: the Apify free plan rates one batch of up to 100 domains a day. Report authority as "not checked" or wait for the daily reset.
- **Authority checker returns `rate-limit`, `try_again` or `retryable: true`**: resend those domains once, a few minutes later.
- **Authority checker returns `input_error`**: send a bare domain (`example.com`), not a phrase or an IP address.
