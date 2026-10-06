# Actor routing table: backlinks and domain authority

All four `crawlplant/*` Actors read the same Common Crawl web graph index. The single-purpose ones fix one mode and
expose only the inputs that mode needs. Fetch the live input schema with
`apify actors info "<actor-id>" --input --user-agent apify-awesome-skills/apify-backlinks-domain-authority 2>/dev/null`.

## By job

| Job | Actor | Mode | Key inputs | Row `type` |
|-----|-------|------|------------|------------|
| Score a list of domains | `crawlplant/commoncrawl-domain-metrics` | `profiles` (default) | `domains`, `minAuthority`, `sortBy`, `sources` | `profile` |
| Who links to a domain | `crawlplant/referring-domains-checker` | fixed | `domains`, `maxReferrersPerDomain`, `minAuthority`, `maxItems` | `referrer` |
| Link gap vs competitors | `crawlplant/link-gap-finder` | fixed | `yourDomain`, `domains` (up to 20 competitors), `maxReferrersPerDomain`, `minAuthority`, `excludeHubs`, `maxItems` | `linkGap` |
| Sites like a domain | `crawlplant/similar-sites-finder` | fixed | `domains`, `maxReferrersPerDomain` (up to 1,000), `minAuthority`, `maxItems` | `similar` |
| Authority over time | `crawlplant/commoncrawl-domain-metrics` | `history` | `domains`, `historyReleases` (1-60, default 6), `graphRelease` | `history` |
| Referring domains gained and lost since last month | `crawlplant/commoncrawl-domain-metrics` | `changes` | `domains`, `maxReferrersPerDomain` (per list), `minAuthority` | `change` |
| Domains a site links to | `crawlplant/commoncrawl-domain-metrics` | `outlinks` | `domains`, `maxReferrersPerDomain`, `minAuthority` | `outlink` |

The full Actor also runs `referrers`, `linkGap` and `similar` modes with the same inputs as the single-purpose
Actors; use it when one run should mix several jobs' settings, otherwise prefer the single-purpose Actor.

## Input cheat sheet (`crawlplant/commoncrawl-domain-metrics`)

| Input | Default | Notes |
|-------|---------|-------|
| `mode` | `profiles` | `profiles`, `history`, `referrers`, `linkGap`, `similar`, `outlinks`, `changes` |
| `domains` | 3 examples | Domains, URLs or e-mails; reduced to the registrable domain, duplicates merged. In `linkGap`: competitors, up to 20 |
| `yourDomain` | none | `linkGap` only: your site, whose referring domains are left out |
| `excludeHubs` | `true` | `linkGap`: drops CDNs, user-content hosts, link shorteners and sites linking to more than 30,000 domains |
| `sources` | `commoncrawl`, `majestic`, `crux` | Add `tranco` for the Tranco rank (and its daily history in `history` mode) |
| `minAuthority` | `0` | 0-100. Profiles: keep domains at or above it (`1` drops unscored ones). Link modes: keep listed domains at or above it. Filtered rows are free |
| `sortBy` | `input` | Profiles: `input` or `authority` |
| `maxReferrersPerDomain` | `100` | Rows per domain in link modes, strongest first. `linkGap`: strongest referring domains compared per competitor (up to 100,000) |
| `historyReleases` | `6` | `history`: releases to read, newest first; the archive reaches early 2018 |
| `graphRelease` | newest | A release id such as `cc-main-2026-jun-jul-aug` |
| `graphScanDepth` | `10000000` | Only for `history` and older `graphRelease` values; leave the default |
| `maxItems` | `10000` | Hard cap on rows returned and paid for |

## Unaffiliated alternatives

| Need | Actor | Why |
|------|-------|-----|
| Ahrefs DR, URL-level backlinks, anchor text | `radeance/ahrefs-scraper` | Ahrefs' own metrics when the user asks for them by name |
| Website traffic estimates | `tri_angle/similarweb-scraper` | Visits and traffic sources; the crawlplant Actors give only a Chrome popularity bucket |
| Keyword search volume and CPC | `aitorsm/keyword-volume` | Keyword research; the crawlplant Actors have no keyword data |

## Store and MCP

- https://apify.com/crawlplant/commoncrawl-domain-metrics
- https://apify.com/crawlplant/referring-domains-checker
- https://apify.com/crawlplant/link-gap-finder
- https://apify.com/crawlplant/similar-sites-finder
- Hosted MCP server: `https://mcp.apify.com/?tools=actors,docs,crawlplant/commoncrawl-domain-metrics`
- MCP docs: https://docs.apify.com/platform/integrations/mcp
