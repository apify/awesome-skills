---
name: apify-sitemap-health-check
description: Check every URL listed in a website's XML sitemap for broken links, 404s, server errors, redirects, redirect chains, https-to-http downgrades and X-Robots-Tag noindex headers, then summarize what to fix. Use when the user asks to audit a sitemap, find broken URLs or 404s in a sitemap, check sitemap URLs before or after a site migration or CMS update, find redirect chains listed in a sitemap, check whether sitemap URLs return 200, find noindex pages that should not be in the sitemap, or set up a recurring sitemap health check. Works from a site address (sitemap found via robots.txt or /sitemap.xml) or a direct sitemap / sitemap-index / .xml.gz URL. The routed Actor, lineagersiui/sitemap-url-health-checker, is built by this skill's author (see Disclosure).
author: lineagersiui-boop
author_url: https://github.com/lineagersiui-boop
metadata:
  category: data-extraction
  keywords: "sitemap, sitemap-checker, broken-links, 404, http-status, redirects, redirect-chain, noindex, x-robots-tag, technical-seo, site-migration, seo-audit, robots-txt, sitemap-index"
---

# Sitemap Health Check

Find the URLs in a sitemap that are broken, redirected or marked `noindex`, and turn the results into a short fix list.

**Disclosure:** the routed Actor is built and maintained by this skill's author, who earns its pay-per-event fees. There are no affiliate or referral parameters.

## Example prompts

Prompts this skill handles:

- "Check the sitemap of example.com for broken links and redirects"
- "We migrated our blog last week. Which URLs in https://example.com/sitemap_index.xml now 404 or redirect?"
- "Which pages in our sitemap send a noindex header?"

Out of scope (the boundary):

- "Crawl my whole site and find every broken link inside the page content." This skill checks only the URLs listed in the sitemap and does not follow links inside pages. Use a full-site crawler Actor for that, for example by searching the Apify Store with `apify actors search` as shown below.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)
- The user must own the site or have permission to check it. The Actor refuses non-demo runs unless `confirmPermission` is `true`.

## Workflow

1. **Get the target.** Ask for a site address (e.g. `example.com`) or a direct sitemap URL. Confirm that the user owns the site or has permission to check it. Do not set `confirmPermission` on their behalf without asking.
2. **Estimate the cost.** Each URL that returns an HTTP status is one billed event at $0.0005, so 1,000 URLs cost $0.50, plus Apify platform usage. URLs skipped by robots.txt, timeouts and network errors are not billed. Default cap: 500 URLs. Hard cap: 5,000. Confirm with the user before going above 1,000 URLs.
3. **Run the Actor.** Pass `onlyProblems: true` when the user only wants the fix list.
4. **Report.** Read the `SUMMARY` record for counts. Group the problem rows by flag (see the table below) and give the user a short fix list. Link the dataset in Apify Console for the full output.

To see the output format first at no cost, run the Actor with empty input. It checks 20 URLs of apify.com and isn't billed.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Check every URL listed in a sitemap: status, redirects, noindex | `lineagersiui/sitemap-url-health-checker` | community | Sitemap audits, pre/post-migration checks, scheduled checks. Pay-per-event, $0.0005 per URL checked |

## Input

| Field | Type | Notes |
|-------|------|-------|
| `siteUrls` | array of strings | Site addresses. The sitemap is found from robots.txt or `/sitemap.xml`. Up to 10 |
| `sitemapUrls` | array of strings | Direct sitemap, sitemap-index, `.xml.gz` or plain-text list URLs. Up to 10 |
| `confirmPermission` | boolean | Must be `true` for non-demo runs |
| `maxUrls` | integer | Default 500, max 5,000. This is the hard cap per run |
| `onlyProblems` | boolean | Leave out URLs that returned 2xx with no redirect (they are still billed) |
| `timeLimitSecs` | integer | Default 1,500. The run stops starting new checks after this |

## Output

One dataset item per URL with these fields: `url`, `status`, `flags`, `redirects`, `redirectStatuses`, `finalUrl`, `lastmod`, `sitemap`. The key-value store record `SUMMARY` holds the counts (`urlsFound`, `checked`, `billed`, `problems`, `blockedByRobots`, `errors`).

| Flag | Meaning | Suggested fix |
|------|---------|---------------|
| `not_found`, `client_error`, `server_error` | 404/410, another 4xx, or 5xx | Fix the page or remove it from the sitemap |
| `redirected`, `redirect_chain`, `too_many_redirects` | Redirects once, more than once, or more than 5 times | List the final URL in the sitemap instead |
| `https_downgrade` | An https URL redirects to http | Fix the redirect rule |
| `noindex_header` | Sends `X-Robots-Tag: noindex` | Remove the URL from the sitemap, or remove the header |
| `blocked_by_robots` | robots.txt disallows the URL for this checker; skipped and not billed | Usually nothing to do |
| `timeout`, `network_error`, `blocked_private_address` | Couldn't be checked; not billed | Re-run later or check by hand |
| `ok` | 2xx, no redirect | — |

## Calling the Actor

### Option A: Apify CLI

    apify actors call "lineagersiui/sitemap-url-health-checker" \
      -i '{"siteUrls": ["example.com"], "confirmPermission": true, "maxUrls": 500, "onlyProblems": true}' \
      --json \
      --user-agent apify-awesome-skills/apify-sitemap-health-check \
      2>/dev/null

Fetch the input schema:

    apify actors info "lineagersiui/sitemap-url-health-checker" --input \
      --user-agent apify-awesome-skills/apify-sitemap-health-check 2>/dev/null

Fetch the results (the dataset ID is `storage.defaultDatasetId` in the call's JSON output):

    apify datasets get-items DATASET_ID --format json \
      --user-agent apify-awesome-skills/apify-sitemap-health-check 2>/dev/null

Search for a full-site crawler (for out-of-scope requests):

    apify actors search "broken link crawler" --json --limit 10 \
      --user-agent apify-awesome-skills/apify-sitemap-health-check 2>/dev/null

### Option B: Apify MCP connector

Hosted MCP server at <https://mcp.apify.com>. Documented at
<https://docs.apify.com/platform/integrations/mcp>.

## Troubleshooting

- **Run refused (the call exits non-zero and the run status is FAILED), or only the demo ran:** `confirmPermission` is missing or `false`, or no site/sitemap was given. Nothing is checked or charged. Ask the user to confirm permission, then set it to `true`.
- **0 URLs found:** the site has no sitemap in robots.txt or at `/sitemap.xml`. Ask for the direct sitemap URL and pass it in `sitemapUrls`.
- **Many `blocked_by_robots` rows:** the site's robots.txt disallows these URLs for this checker. The Actor respects that, and they aren't billed.
- **Run stopped early:** `maxUrls` or `timeLimitSecs` was reached. Unchecked URLs aren't billed. Raise the limits or split the sitemap.

---

Disclosure: `lineagersiui/sitemap-url-health-checker` is built by this skill's author (pay-per-event). Drafted with AI tools under the author's direction. Not affiliated with or endorsed by Apify beyond publishing on the Apify Store.
