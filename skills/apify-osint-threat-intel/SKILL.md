---
name: apify-osint-threat-intel
description: >
  Use this skill when the user asks to "find CVEs for", "check if my domain is breached",
  "threat intel on", "OSINT on", "security news about", "attack surface of",
  "is this IP malicious", "what vulnerabilities affect", "security advisory for",
  "monitor threats for", "threat actor research", "recent exploits for",
  "data breach check", "security posture of", "what's the threat landscape for",
  "investigate [domain/IP/software]", "is [company] exposed", or any request involving
  vulnerability research, breach detection, threat actor profiling, or security intelligence.
  Requires Apify CLI or Apify MCP server.

author: karthik-zoro-96
author_url: https://github.com/karthik-zoro-96
---

# OSINT Threat Intelligence

Real-time security intelligence powered by live threat data via Apify actors.
**Never answer security questions from training knowledge alone.** CVEs, breaches, and
threat actor activity change daily — always gather live data first, then analyze.

---

## Prerequisites

- Apify CLI v1.5.0+: `npm i -g apify-cli`
- Authenticated: `apify login` or `export APIFY_TOKEN=your_token`
- Token: https://console.apify.com/settings/integrations

### CLI rules (always follow)
```bash
apify actors call "ACTOR_ID" -i 'INPUT_JSON' --json 2>/dev/null
apify datasets get-items DATASET_ID --format json > /tmp/results.json 2>/dev/null
jq '.[] | "\(.field1) | \(.field2)"' /tmp/results.json
apify actors info "ACTOR_ID" --input --json 2>/dev/null   # check schema
```

---

## Actor Routing Table

| Data Need | Actor ID | Notes |
|---|---|---|
| CVE lookup | `apify/google-search-scraper` | Query: `site:nvd.nist.gov [product] [version]` |
| NVD full record | `apify/website-content-crawler` | URL: `nvd.nist.gov/vuln/detail/CVE-XXXX-XXXXX` |
| CISA known exploited | `apify/rag-web-browser` | URL: `cisa.gov/known-exploited-vulnerabilities-catalog` |
| GitHub advisories | `apify/rag-web-browser` | URL: `github.com/advisories?query=[product]` |
| Exploit-DB search | `apify/google-search-scraper` | Query: `site:exploit-db.com [product] [version]` |
| Security news | `data_xplorer/google-news-scraper-fast` | Keywords: `"[target]" vulnerability OR exploit OR breach` |
| Reddit threat discussion | `trudax/reddit-scraper` | `withinCommunity`: r/netsec OR r/cybersecurity |
| Threat intel Twitter/X | `apidojo/tweet-scraper` | Keywords: `#threatintel [target]`, search mode |
| Breach mention search | `apify/google-search-scraper` | Query: `"[domain]" site:pastebin.com OR intext:breach` |
| Vendor security advisory | `apify/website-content-crawler` | Direct vendor security page URL |
| Shodan exposure hints | `apify/google-search-scraper` | Query: `site:shodan.io "[domain OR org name]"` |
| Threat actor research | `apify/rag-web-browser` | MITRE ATT&CK: `attack.mitre.org/groups/` |

**Prefer** `apify/google-search-scraper` and `apify/rag-web-browser` over `website-content-crawler` for speed.  
**Use** `website-content-crawler` only when you need the full page body (e.g. NVD detail, vendor advisory).  
**Do NOT** use `website-content-crawler` on: reddit.com, twitter.com, pastebin.com, linkedin.com.

---

## Core Workflow

### Step 0 — Clarify scope before running anything

Ask the user:
- **Target type**: domain, IP, software/version, CVE ID, threat actor name, or keyword?
- **Goal**: one-time lookup vs. ongoing monitoring brief?
- **Autonomy**: full autopilot, or checkpoint before each actor call?

### Step 1 — Identify module

| User says | Module | Steps |
|---|---|---|
| "Find CVEs for [product]" | CVE Intelligence | 2a |
| "Is [domain] breached / exposed" | Domain Threat Profile | 2b |
| "Research [threat actor / malware]" | Threat Actor Profile | 2c |
| "Security news about [topic]" | Security News Brief | 2d |
| "Attack surface of [company]" | Attack Surface Discovery | 2b + 2d |
| "Full threat report on [target]" | Multi-Module | 2a + 2b + 2c + 2d |

### Step 2a — CVE Intelligence

Gather live CVE data for a product or version:

```bash
# 1. Search NVD via Google
apify actors call "apify/google-search-scraper" -i '{
  "queries": "site:nvd.nist.gov CVE [PRODUCT] [VERSION]",
  "maxResultsPerPage": 10,
  "resultsPerPage": 10
}' --json 2>/dev/null

# 2. Pull full NVD record for each CVE ID found
apify actors call "apify/website-content-crawler" -i '{
  "startUrls": [{"url": "https://nvd.nist.gov/vuln/detail/CVE-XXXX-XXXXX"}],
  "maxCrawlPages": 1
}' --json 2>/dev/null

# 3. Check if CVE is in CISA's Known Exploited Vulnerabilities list
apify actors call "apify/rag-web-browser" -i '{
  "query": "[CVE-ID] site:cisa.gov/known-exploited-vulnerabilities-catalog",
  "maxResults": 3
}' --json 2>/dev/null

# 4. Check Exploit-DB for public PoC
apify actors call "apify/google-search-scraper" -i '{
  "queries": "site:exploit-db.com [PRODUCT] [VERSION]",
  "maxResultsPerPage": 5
}' --json 2>/dev/null
```

Synthesize: severity (CVSS), exploitability (CISA KEV = active exploitation), public PoC exists (yes/no), patch available (yes/no).

### Step 2b — Domain Threat Profile

```bash
# 1. Search for breach mentions
apify actors call "apify/google-search-scraper" -i '{
  "queries": "\"[DOMAIN]\" breach OR leak OR hacked OR \"data exposed\"",
  "maxResultsPerPage": 10
}' --json 2>/dev/null

# 2. Check paste sites for credential leaks
apify actors call "apify/google-search-scraper" -i '{
  "queries": "\"[DOMAIN]\" site:pastebin.com OR site:ghostbin.com OR site:rentry.co",
  "maxResultsPerPage": 5
}' --json 2>/dev/null

# 3. Check Shodan exposure hints via Google
apify actors call "apify/google-search-scraper" -i '{
  "queries": "site:shodan.io \"[DOMAIN OR ORG]\"",
  "maxResultsPerPage": 5
}' --json 2>/dev/null

# 4. Scan r/netsec and r/cybersecurity for mentions
apify actors call "trudax/reddit-scraper" -i '{
  "searchTerms": ["[DOMAIN] breach", "[DOMAIN] hack", "[DOMAIN] vulnerability"],
  "withinCommunity": "r/netsec",
  "maxPostsCount": 10
}' --json 2>/dev/null
```

### Step 2c — Threat Actor Profile

```bash
# 1. MITRE ATT&CK lookup
apify actors call "apify/rag-web-browser" -i '{
  "query": "[THREAT ACTOR NAME] site:attack.mitre.org",
  "maxResults": 3
}' --json 2>/dev/null

# 2. Recent activity via news
apify actors call "data_xplorer/google-news-scraper-fast" -i '{
  "keyword": "[THREAT ACTOR NAME] attack OR campaign OR malware",
  "maxItems": 15
}' --json 2>/dev/null

# 3. Community threat intel on Twitter/X
apify actors call "apidojo/tweet-scraper" -i '{
  "searchTerms": ["#threatintel [THREAT ACTOR]", "[THREAT ACTOR] TTPs"],
  "maxItems": 20,
  "sort": "Latest"
}' --json 2>/dev/null

# 4. Reddit discussion
apify actors call "trudax/reddit-scraper" -i '{
  "searchTerms": ["[THREAT ACTOR NAME]"],
  "withinCommunity": "r/netsec",
  "maxPostsCount": 10
}' --json 2>/dev/null
```

### Step 2d — Security News Brief

```bash
# 1. Google News for topic
apify actors call "data_xplorer/google-news-scraper-fast" -i '{
  "keyword": "[TOPIC] vulnerability OR CVE OR breach OR exploit",
  "maxItems": 20
}' --json 2>/dev/null

# 2. Reddit r/netsec latest
apify actors call "trudax/reddit-scraper" -i '{
  "startUrls": [{"url": "https://www.reddit.com/r/netsec/"}],
  "maxPostsCount": 15,
  "sort": "new"
}' --json 2>/dev/null
```

### Step 3 — Triage and assess

For every finding, apply this classification:

| Severity | Criteria |
|---|---|
| **Critical** | CVSS ≥ 9.0 OR on CISA KEV list OR public PoC + unpatched |
| **High** | CVSS 7.0–8.9 OR active exploitation reported in news |
| **Medium** | CVSS 4.0–6.9 OR breach mention without active exploit |
| **Low** | CVSS < 4.0 OR historical, patched, no active exploitation |
| **Informational** | Exposure hints without confirmed vulnerability |

### Step 4 — Deliver structured report

Output format:
```
## Threat Intelligence Report — [TARGET]
Date: [today]

### Executive Summary
[2–3 sentence risk verdict]

### Critical Findings
- [CVE/Finding] — Severity: [X] — Status: [Patched/Unpatched/Active exploit]
  Source: [URL]

### Breach/Exposure Indicators
- [Finding] — Source: [URL]

### Threat Actor Activity (if applicable)
- [Actor] — TTPs: [list] — Last seen: [date]

### Recommended Actions
1. [Immediate action]
2. [Short-term action]
3. [Monitoring recommendation]

### Data Sources
[Bullet list of all URLs cited]
```

---

## Data Quality Rules

- **Every claim needs a source URL** — no ungrounded assertions
- **Empty results are intelligence** — report them explicitly ("no paste mentions found")
- **Date-stamp all findings** — CVE severity, patch status, and breach reports are time-sensitive
- **Confidence tiers**:
  - `[Confirmed]` — primary source (NVD, CISA, vendor advisory)
  - `[Reported]` — news + community corroboration
  - `[Unverified]` — single secondary source, flag clearly
- **Parallelize** independent actor calls (CVE search + news + Reddit can run simultaneously)
- **Budget**: warn user if >10 actor calls needed; get approval before proceeding

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `google-search-scraper` returns 0 results | Simplify query, remove `site:` filter, try broader terms |
| `website-content-crawler` times out on NVD | Use `rag-web-browser` as fallback with direct CVE URL |
| `trudax/reddit-scraper` returns empty | Try `harshmaur/reddit-scraper` as fallback |
| `tweet-scraper` returns sparse results | Broaden to `#cybersecurity [term]` or drop hashtag requirement |
| CISA KEV page too large to crawl | Use `rag-web-browser` with specific CVE ID as query |

See [gotchas.md](../../docs/gotchas.md) for cost guardrails and rate limit guidance.
