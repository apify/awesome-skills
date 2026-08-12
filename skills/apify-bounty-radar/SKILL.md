---
name: apify-bounty-radar
description: Find, screen, and prioritize public GitHub bounty opportunities with Apify Actors. Use when a user asks to find paid GitHub issues, Algora or Polar bounties, bounty races, claimable open-source tasks, or recently posted contribution opportunities, and needs evidence on payout terms, competition, assignment rules, and claimability before starting work.
author: Peter7896
author_url: https://github.com/Peter7896
---

# Apify Bounty Radar

Find public open-source bounty opportunities, collect the evidence needed to decide whether to attempt them, and separate credible paid work from stale, crowded, assigned, or unsafe opportunities.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` if using the Apify CLI
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console > Settings > Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. Clarify the target lane: bounty platform, minimum reward, preferred stack, allowed regions, and whether credits or token payouts count.
2. Discover candidates with search Actors. Start narrow: recent GitHub issues, Algora wording, Polar funding text, or project-specific labels.
3. Crawl only the candidate pages that pass the first filter. Extract issue body, labels, comments, linked PRs, reward amount, assignment rules, and claim instructions.
4. Score each candidate before recommending work:
   - Reward credibility: platform, maintainer wording, currency, payout region, and deadline.
   - Claimability: open state, assignee, first-claim rule, required registration, and whether a claim comment is allowed.
   - Competition: number of attempts, merged or rewarded PRs, recent maintainer preference, and open high-quality PRs.
   - Delivery fit: stack, setup burden, tests, required demo video, and whether private data or paid services are needed.
5. Return a compact queue: claim now, inspect deeper, monitor, or skip. Include the exact evidence URL for each decision.

## Actor Routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Search broad web and GitHub pages for bounty wording | `apify/google-search-scraper` | apify | Fresh discovery by query, platform, amount, or repo |
| Extract readable issue text, comments, and linked pages | `apify/website-content-crawler` | apify | Evidence capture from GitHub issue, PR, Algora, Polar, and docs pages |
| Run custom page extraction when the generic crawler misses structured data | `apify/web-scraper` | apify | GitHub pages, bounty tables, label pages, and custom selectors |

Prefer Apify-maintained Actors first. Use third-party Actors only when the user accepts the extra trust and cost tradeoff.

## Discovery Queries

Use several narrow searches instead of one broad scrape:

```text
site:github.com "bounty" "$" "Steps to solve" "/attempt"
site:github.com "bounty" "$100" "is:issue" "open"
site:github.com "Polar" "Funding" "issue is completed"
site:github.com "Algora" "Low quality" "PRs will not receive review"
site:github.com "label:\"$50\"" "label:bounty"
```

For a specific ecosystem, add stack terms:

```text
FastAPI bounty "$100" site:github.com
Rust bounty Algora site:github.com
Kubernetes "bounty" "$250" site:github.com
```

## Calling Actors

### Search Candidates

```bash
apify actors call apify/google-search-scraper \
  --input '{"queries":"site:github.com \"bounty\" \"$\" \"Steps to solve\" \"/attempt\"","resultsPerPage":10,"maxPagesPerQuery":2,"countryCode":"US","languageCode":"en"}' \
  --json \
  --user-agent apify-awesome-skills/apify-bounty-radar \
  2>/dev/null
```

### Crawl Candidate Evidence

```bash
apify actors call apify/website-content-crawler \
  --input '{"startUrls":[{"url":"https://github.com/OWNER/REPO/issues/NUMBER"}],"maxCrawlPages":1,"crawlerType":"cheerio","removeElementsCssSelector":"nav,footer,script,style","saveMarkdown":true}' \
  --json \
  --user-agent apify-awesome-skills/apify-bounty-radar \
  2>/dev/null
```

### Fetch Results

```bash
apify datasets get-items DATASET_ID --format json \
  --user-agent apify-awesome-skills/apify-bounty-radar \
  2>/dev/null
```

## Decision Rules

Classify every candidate:

- `claim now`: clear payout, open issue, claim method available, no assignee or exclusive owner, low competition, and realistic scope.
- `inspect deeper`: possible payout but unclear rules, unclear status, or needs repo setup review.
- `monitor`: good project but already assigned, waiting on maintainer confirmation, or crowded with several strong PRs.
- `skip`: closed, archived, deadline passed, duplicate already rewarded, creator-only, private-registration-only, pay-to-bid, unsafe data handling, or requires publishing private config or identity metadata.

If a candidate says "first comment wins", "assigned only", "creator only", or "only one PR", treat that wording as a hard gate.

## Evidence Table

Return concise rows:

| Field | What to capture |
|-------|-----------------|
| URL | Issue or bounty page |
| Reward | Amount, currency, and whether cash, credits, or tokens |
| Platform | Algora, Polar, maintainer-direct, OpenCollective, or unknown |
| Claim rule | `/attempt`, `/claim`, assignment, registration, or none |
| Competition | Attempts, open PRs, rewarded PRs, comments, assignees |
| Risk | Deadline, demo video, private signup, public metadata, payment region |
| Decision | claim now, inspect deeper, monitor, or skip |
| Next action | Exact next safe step |

## Cost Guardrails

- Start with search results only. Do not crawl more than 10 candidate pages without user approval.
- For GitHub issue pages, crawl one page at a time; use GitHub APIs when available for comments and PR state.
- Stop crawling if a page is archived, closed, paid already, or clearly unavailable.
- Never crawl private repositories, account dashboards, payment settings, or pages requiring login unless the user explicitly authorizes that account workflow.

## Troubleshooting

- Too many stale hits: add `created:`, `updated:`, current year, platform name, and minimum amount to the search phrase.
- Search misses label-only bounties: search GitHub labels directly with the GitHub API or crawl repository label pages.
- GitHub HTML is noisy: use `website-content-crawler` for page text, then verify state and comments through GitHub APIs before any public action.
- Reward is not cash: label it clearly as credits, tokens, or unknown; do not mix it with confirmed cash payout.
- Existing PRs look weak: competing is only worth it when the new implementation can prove a stronger root cause, broader coverage, or lower review burden.
