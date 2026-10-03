# Website health audit Actor index

Live routing table re-read from the public Apify API on 2026-10-03. Each Actor is public. Fetch its current schema with `apify actors info "ACTOR_ID" --input` before building an input; the tables below describe the live contract observed at that read, not a substitute for it.

| User intent | Actor ID | Required input | Price | Use it for |
|-------------|----------|----------------|-------|------------|
| Hacked website / casino or pharma SEO spam | [`weio/hacked-website-seo-spam-checker`](https://apify.com/weio/hacked-website-seo-spam-checker) | `websites` | $0.005 per checked site | Public-page spam, cloaking, sitemap, and WordPress-post signals |
| Broken links / 404 audit | [`weio/broken-link-checker-bulk`](https://apify.com/weio/broken-link-checker-bulk) | `websites` | $0.01 per site | Bounded crawl for internal and optional external link failures |
| SPF, DMARC, WHOIS/RDAP, MX and DNS | [`weio/domain-whois-dns-email-security-checker`](https://apify.com/weio/domain-whois-dns-email-security-checker) | `domains` | $0.003 per checked domain | Published DNS and email-security posture |
| Responsive screenshots | [`weio/website-screenshot-phone-desktop`](https://apify.com/weio/website-screenshot-phone-desktop) | `websites` | $0.003 per screenshot | Point-in-time phone, tablet, or desktop image evidence |

## Live schema notes

- Hacked-site checker also exposes `checkSitemaps`, `checkWordPress`, `onlyLikelyHacked`, and `concurrency`.
- Broken-link checker also exposes `maxPagesPerSite`, `checkExternal`, and `checkImages`; bound page count before a large crawl.
- Domain checker also exposes `concurrency`.
- Screenshot also exposes `devices`, `fullPage`, `format`, `waitMs`, and `hideCookieBanners`; price scales with screenshots requested.

All four are Weio community Actors. Routed Actors are built by the author (Weio); no affiliate parameters.
